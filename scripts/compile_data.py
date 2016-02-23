#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""A script that parses raw data output by jsSART (jsPsych), compiles each
participant's data and creates/updates a file in jsSART's ``data``
directory.
"""
import os
import glob
import json

import pandas as pd
import numpy as np
from scipy import stats


PROJECT_DIR = os.path.abspath(os.path.join(__file__, '..', '..'))
DATA_DIR = os.path.join(PROJECT_DIR, 'data')
ROUND_NDIGITS = 9


def get_csv_paths(basedir, exp_stage):
    """Take base data directory and experiment stage. Return list of file paths.
    """
    glob_path = os.path.join(basedir, exp_stage, '*.csv')
    return glob.glob(glob_path)


def get_csv_as_dataframe(path):
    """Take CSV path. Return pandas dataframe.
    """
    return pd.DataFrame.from_csv(path, index_col='trial_index')


def compile_practice_data(df):
    """Take pandas dataframe and compile key variables. Return dict.
    """
    compiled_data = {}

    # participant ID
    participant_id_col = df['participant_id'].values
    compiled_data['id'] = participant_id_col[0]

    # participant ID
    condition_col = df['practice_condition'].values
    compiled_data['practice_condition'] = condition_col[0]

    # was practice block #2 completed successfully?
    passed_practice = ('0.0-7.0-0.0' in df['internal_node_id'].values)
    compiled_data['passed_practice'] = passed_practice

    # time taken to complete practice blocks
    time_block_1_start_ms = int(df.ix[1]['time_elapsed'])
    time_block_1_end_ms = int(df.ix[7]['time_elapsed'])
    time_practice_blk1_ms = time_block_1_end_ms - time_block_1_start_ms
    compiled_data['time_practice_blk1_ms'] = time_practice_blk1_ms

    time_block_2_start_ms = int(df.ix[10]['time_elapsed'])
    time_block_2_end_ms = int(df.ix[26]['time_elapsed'])
    time_practice_blk2_ms = time_block_2_end_ms - time_block_2_start_ms
    compiled_data['time_practice_blk2_ms'] = time_practice_blk2_ms

    # time taken to complete entire practice
    time_practice_ms = int(df.ix[df.last_valid_index()]['time_elapsed'])
    compiled_data['time_practice_ms'] = time_practice_ms

    return compiled_data


def get_response_from_json(string, question_number=0):
    """Take JSON string representing a survey response and decode.
    Return target question answer string.
    """
    decoder = json.JSONDecoder()
    resp_json = decoder.decode(string)
    target_question = "Q{}".format(question_number)
    resp = resp_json[target_question] if target_question in resp_json else None
    return resp


def summarize_sart_chunk(df):
    """Take pandas dataframe representing raw SART chunk data and summarize.
    Return dict.
    """
    summary = {}

    block_type_col = df['block_type'].dropna().values
    summary['block_type'] = block_type_col[0]

    # summarize performance
    raw_trials = df.loc[df['trial_type'] == 'multi-stim-multi-response']
    trials = list(raw_trials['correct'].values)
    trials.pop(0)  # remove fixation data
    accuracy = float(trials.count(True)) / len(trials)
    summary['accuracy'] = round(accuracy, ROUND_NDIGITS)

    # affective ratings
    ratings_json = df.ix[df.last_valid_index()]['responses']
    raw_effort_rating = get_response_from_json(ratings_json)
    summary['effort'] = int(raw_effort_rating[0])
    raw_discomfort_rating = get_response_from_json(ratings_json, 1)
    summary['discomfort'] = int(raw_discomfort_rating[0])

    return summary


def compile_experiment_data(df):
    """Take pandas dataframe and compile key variables. Return dict.
    """
    compiled_data = {}

    # condition
    condition_col = df['condition'].values
    compiled_data['condition'] = condition_col[0]

    # blocks and block order
    block_order_col = df['block_order'].values
    block_order = block_order_col[0]
    blocks = block_order.split(',')
    compiled_data['block_order'] = block_order
    compiled_data['num_blocks'] = len(blocks)

    # anticipated questions
    anticipated_questions_index = [
        ('anticipated_enjoyment', 1),
        ('anticipated_performance', 2),
        ('anticipated_effort', 3),
        ('anticipated_discomfort', 4),
        ('anticipated_fatigue', 5)
    ]
    for label, i in anticipated_questions_index:
        response = get_response_from_json(df.ix[i]['responses'])
        compiled_data[label] = int(response[0])

    # SART accuracy and affective reports
    hard_accuracy = None
    medium_accuracy = None
    easy_accuracy = None
    hard_effort = None
    medium_effort = None
    easy_effort = None
    hard_discomfort = None
    medium_discomfort = None
    easy_discomfort = None

    effort_ratings = []
    discomfort_ratings = []
    accuracies = []
    medium_effort_ratings = []
    medium_discomfort_ratings = []
    medium_accuracies = []
    medium_blocks_order = []

    # collect and organize experiment data from experimental blocks
    for i, block in enumerate(blocks, start=1):
        # note: SART chunks start at chunk_id 0-0.3-0
        block_chunk_id = '0-0.{}-0'.format(i + 2)
        block = df.loc[df['internal_node_id'] == block_chunk_id]
        block_summary = summarize_sart_chunk(block)

        # add block summaries to compiled data
        compiled_data['effort_{}'.format(i)] = block_summary['effort']
        discomfort_key = 'discomfort_{}'.format(i)
        compiled_data[discomfort_key] = block_summary['discomfort']
        accuracy_key = 'accuracy_{}'.format(i)
        compiled_data[accuracy_key] = block_summary['accuracy']

        # identify and organize data by block type
        effort_ratings.append(block_summary['effort'])
        discomfort_ratings.append(block_summary['discomfort'])
        accuracies.append(block_summary['accuracy'])

        if block_summary['block_type'] == 'medium':
            medium_blocks_order.append(i)
            medium_accuracies.append(block_summary['accuracy'])
            medium_effort_ratings.append(block_summary['effort'])
            medium_discomfort_ratings.append(
                block_summary['discomfort'])
        elif block_summary['block_type'] == 'hard':
            hard_accuracy = block_summary['accuracy']
            hard_effort = block_summary['effort']
            hard_discomfort = block_summary['discomfort']
        elif block_summary['block_type'] == 'easy':
            easy_accuracy = block_summary['accuracy']
            easy_effort = block_summary['effort']
            easy_discomfort = block_summary['discomfort']

    # compute medium block averages
    medium_accuracy = np.mean(medium_accuracies)
    compiled_data['medium_accuracy'] = round(medium_accuracy, ROUND_NDIGITS)
    medium_effort = np.mean(medium_effort_ratings)
    compiled_data['medium_effort'] = round(medium_effort, ROUND_NDIGITS)
    medium_discomfort = np.mean(medium_discomfort_ratings)
    compiled_data['medium_discomfort'] = round(
        medium_discomfort, ROUND_NDIGITS)

    # compute regression variables for medium blocks
    medium_block_measures = [
        ('medium_accuracy', medium_accuracies),
        ('medium_effort', medium_effort_ratings),
        ('medium_discomfort', medium_discomfort_ratings)
    ]
    for measure_name, measure_values in medium_block_measures:
        measure_regress = stats.linregress(medium_blocks_order, measure_values)
        compiled_data['{}_slope'.format(measure_name)] = round(
            measure_regress.slope, ROUND_NDIGITS)
        compiled_data['{}_intercept'.format(measure_name)] = round(
            measure_regress.intercept, ROUND_NDIGITS)

    # assign other variables
    compiled_data['hard_accuracy'] = hard_accuracy
    compiled_data['hard_effort'] = hard_effort
    compiled_data['hard_discomfort'] = hard_discomfort
    compiled_data['easy_accuracy'] = easy_accuracy
    compiled_data['easy_effort'] = easy_effort
    compiled_data['easy_discomfort'] = easy_discomfort

    compiled_data['start_effort'] = effort_ratings[0]
    compiled_data['peak_effort'] = max(effort_ratings)
    compiled_data['end_effort'] = effort_ratings[-1]
    avg_effort = np.mean(effort_ratings)
    compiled_data['avg_effort'] = round(avg_effort, ROUND_NDIGITS)

    compiled_data['start_discomfort'] = discomfort_ratings[0]
    compiled_data['peak_discomfort'] = max(discomfort_ratings)
    compiled_data['end_discomfort'] = discomfort_ratings[-1]
    avg_discomfort = np.mean(discomfort_ratings)
    compiled_data['avg_discomfort'] = round(avg_discomfort, ROUND_NDIGITS)

    average_accuracy = np.mean(accuracies)
    compiled_data['avg_accuracy'] = round(average_accuracy, ROUND_NDIGITS)
    compiled_data['max_accuracy'] = max(accuracies)
    compiled_data['min_accuracy'] = min(accuracies)
    compiled_data['start_accuracy'] = accuracies[0]
    compiled_data['end_accuracy'] = accuracies[-1]

    # area under the curve calculations
    compiled_data['auc_accuracy'] = round(
        np.trapz(accuracies), ROUND_NDIGITS)
    compiled_data['auc_effort'] = round(
        np.trapz(effort_ratings), ROUND_NDIGITS)
    compiled_data['auc_discomfort'] = round(
        np.trapz(discomfort_ratings), ROUND_NDIGITS)

    # time taken to complete working memory task
    time_experiment_ms = int(df.ix[df.last_valid_index()]['time_elapsed'])
    compiled_data['time_experiment_ms'] = time_experiment_ms

    return compiled_data


def compile_demographic_data(df):
    """Take pandas dataframe and compile key variables. Return dict.
    """
    compiled_data = {}
    responses = list(df['responses'].dropna().values)

    demographics_index = [
        # demographics questions
        ('age', 1),
        ('dob', 2),
        ('sex', 3),
        ('edu_year', 4),
        ('edu_plan', 5),
        ('first_lang', 6),
        ('years_eng', 7),
        ('mother_edu', 8),
        ('mother_job', 9),
        ('father_edu', 10),
        ('father_job', 11),
        ('high_school_avg', 12),
        ('uni_avg', 13),
        ('num_uni_stats', 14),
        ('num_hs_stats', 15),
        ('num_hs_math', 16),
        ('num_uni_math', 17),
        ('math_enjoy', 18),
        ('adhd_diag', 19),
        ('uni_major', 20),

        # electronics and Internet survey
        ('elect_survey_1', 21),
        ('elect_survey_2', 22),
        ('elect_survey_3', 23),
        ('elect_survey_4', 24),
        ('elect_survey_5', 25),
        ('elect_survey_6', 26),
        ('elect_survey_7', 27),
    ]
    for label, i in demographics_index:
        response = get_response_from_json(df.ix[i]['responses'])
        compiled_data[label] = response.strip()

    behavioural_survey = [
        # behavioural survey
        ('behav_survey_1', 29),
        ('behav_survey_2', 30),
        ('behav_survey_3', 31),
        ('behav_survey_4', 32),
        ('behav_survey_5', 33),
        ('behav_survey_6', 34),
        ('behav_survey_7', 35),
        ('behav_survey_8', 36),
        ('behav_survey_9', 37),
        ('behav_survey_10', 38),
        ('behav_survey_11', 39),
        ('behav_survey_12', 40),
        ('behav_survey_13', 41),
        ('behav_survey_14', 42),
        ('behav_survey_15', 43),
        ('behav_survey_16', 44),
        ('behav_survey_17', 45),
        ('behav_survey_18', 46),

    ]
    for label, i in behavioural_survey:
        response = get_response_from_json(df.ix[i]['responses'])
        if response[0].isdigit():
            response = response[0]
        compiled_data[label] = response

    # post-working memory task delay
    if 47 in df.index.values:
        compiled_data['time_pwmt_delay_ms'] = int(df.ix[47]['time_elapsed'])

    # time taken for post-working memory task follow-up
    time_follow_up_ms = int(df.ix[df.last_valid_index()]['time_elapsed'])
    compiled_data['time_follow_up_ms'] = time_follow_up_ms

    return compiled_data


def compile_retrospective_data(df):
    """Take pandas dataframe and compile key variables. Return dict.
    """
    compiled_data = {}
    responses = list(df['responses'].dropna().values)

    # retrospective questions
    retrospective_index = [
        ('pwmt_effort', 48),
        ('pwmt_discomfort', 49),
        ('pwmt_enjoyment', 50),
        ('pwmt_performance', 51),
        ('pwmt_fatigue', 52),
        ('pwmt_satisfaction', 53),
        ('pwmt_willingtodowmt', 54),
    ]
    for label, i in retrospective_index:
        response = get_response_from_json(df.ix[i]['responses'])
        compiled_data[label] = int(response[0])

    return compiled_data


def main():
    # collect lists of raw data CSVs
    raw_data_csvs = {}
    for exp_stage in ['practice', 'experiment', 'follow_up']:
        raw_data_csvs[exp_stage] = get_csv_paths(DATA_DIR, exp_stage)

    # create list of compiled participant data
    compiled_participants = []
    for practice_csv in raw_data_csvs['practice']:
        participant = {
            'missing_data': False
        }

        # compile practice data
        practice_df = get_csv_as_dataframe(practice_csv)
        compiled_practice_data = compile_practice_data(practice_df)
        participant.update(compiled_practice_data)

        # compile experimental and follow up data
        # note: checks to ensure that assumed CSV files exist
        for exp_stage in ['experiment', 'follow_up']:
            assumed_csv_path = os.path.join(
                DATA_DIR, exp_stage, '{}.csv'.format(participant['id']))

            if assumed_csv_path in raw_data_csvs[exp_stage] and \
                    os.path.exists(assumed_csv_path):
                stage_df = get_csv_as_dataframe(assumed_csv_path)

                if exp_stage == 'experiment':
                    experiment_data = compile_experiment_data(stage_df)
                    participant.update(experiment_data)
                elif exp_stage == 'follow_up':
                    demographics = compile_demographic_data(stage_df)
                    participant.update(demographics)
                    if participant['passed_practice']:
                        retrospective = compile_retrospective_data(stage_df)
                        participant.update(retrospective)

            elif (exp_stage == 'experiment' and
                    participant['passed_practice']) or \
                    exp_stage == 'follow_up':
                participant['missing_data'] = True

        # append compiled participant data to master list
        compiled_participants.append(participant)

    # export complete data set to CSV
    participants_df = pd.DataFrame.from_dict(compiled_participants)
    compiled_csv_path = os.path.join(DATA_DIR, 'compiled.csv')
    participants_df.to_csv(compiled_csv_path, encoding='utf-8')

    # create list of columns for alternative analysis
    first_columns = ['id', 'num_blocks']
    block_columns = []
    for i in range(1, 10):
        block_columns.append('accuracy_{}'.format(i))
        block_columns.append('discomfort_{}'.format(i))
        block_columns.append('effort_{}'.format(i))
    columns = (first_columns + sorted(block_columns))

    # export data for alternative analysis to CSV
    alt_analysis_df = participants_df[columns].copy()
    alt_analysis_df.sort(columns=['num_blocks'], inplace=True)
    alt_analysis_csv_path = os.path.join(DATA_DIR, 'alt_compiled.csv')
    alt_analysis_df.to_csv(alt_analysis_csv_path, encoding='utf-8')


if __name__ == '__main__':
    main()
