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
DECODER = json.JSONDecoder()
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


def extract_sart_blocks(df, with_survey=False):
    """Take pandas data frame and find SART trial blocks.
    Return list of pandas data frames.
    """
    blocks = []

    # the type of trial(s) to target
    mc_trial_type = "survey-multi-choice"
    block_trial_types = ["multi-stim-multi-response"]
    if with_survey:
        block_trial_types.append(mc_trial_type)

    # find and extract block rows
    first_trial_idx = None
    last_trial_idx = None
    num_mc_trials = 0
    for index, series in df.iterrows():
        if not first_trial_idx and series['trial_type'] == mc_trial_type:
            # skip if first trial type is a survey
            continue
        elif series['trial_type'] in block_trial_types and \
                num_mc_trials < 2:
            if not first_trial_idx:
                first_trial_idx = index
            last_trial_idx = index

            # NOTE: limit to 2 survey trials, as per experiment specs
            if series['trial_type'] == mc_trial_type:
                num_mc_trials += 1
        else:
            if first_trial_idx and last_trial_idx:
                block = df.loc[first_trial_idx:last_trial_idx]
                blocks.append(block)
                first_trial_idx = None
                last_trial_idx = None
                num_mc_trials = 0

    return blocks


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
    num_practice_blk2s = 0
    practice_blocks = extract_sart_blocks(df)
    for i, blk in enumerate(practice_blocks):
        blk_start_ms = int(blk.ix[blk.first_valid_index()]['time_elapsed'])
        blk_end_ms = int(blk.ix[blk.last_valid_index()]['time_elapsed'])
        time_practice_blk_ms = blk_end_ms - blk_start_ms
        if i > 0:
            # record as practice block #2 trials
            time_blk_key = 'time_practice_blk2_{}_ms'.format(i)
            compiled_data[time_blk_key] = time_practice_blk_ms
            num_practice_blk2s += 1
        else:
            # record as practice block #1
            compiled_data['time_practice_blk1_ms'] = time_practice_blk_ms

    # number of practice 2 blocks required to reach criterion
    compiled_data['num_practice_blk2s'] = num_practice_blk2s

    # time taken to complete entire practice
    time_practice_ms = int(df.ix[df.last_valid_index()]['time_elapsed'])
    compiled_data['time_practice_ms'] = time_practice_ms

    return compiled_data


def get_response_from_json(string, question_number=0):
    """Take JSON string representing a survey response and decode.
    Return target question answer string.
    """
    resp_json = DECODER.decode(string)
    target_question = "Q{}".format(question_number)
    resp = resp_json[target_question] if target_question in resp_json else None
    return resp


def get_response_from_node_id(df, inid, is_likert=False):
    """Take a data frame and internal node ID (inid).
    Return a jsPsych survey response string.
    """
    response = None

    # get row and then response text
    response_str = df[df['internal_node_id'] == inid]['responses'].values
    if response_str:
        response = get_response_from_json(response_str[0]).strip()

    if is_likert and response and response[0].isdigit():
        # we only want the numeric response
        response = response[0]

    return response


def _format_rts(rts):
    """Take a pandas series of reaction times and return formatted array.
    """
    rt_arrays = map(lambda x: DECODER.decode(x), rts)
    all_rts_strf = np.ndarray.flatten(np.array(rt_arrays))
    # exclude non-response RTs
    rts_strf = [rt for rt in all_rts_strf if rt >= 0]

    return list(rts_strf)


def _is_anticipation_error(rt):
    """Take reaction time JSON string and determine whether it represents an
    anticipation error (<100ms response).
    """
    is_error = False
    rt_ms = _format_rts([rt])
    if rt_ms and rt_ms[0] < 100 and rt_ms[0] > -1:
        is_error = True
    return is_error


def _add_anticipation_errors(df):
    """Add anticipation errors to pandas data frame and re-calculate
    `correct` column.
    """
    df['anticipate_error'] = pd.Series(
        df['rt'].apply(_is_anticipation_error), index=df.index)
    df.ix[df.anticipate_error, 'correct'] = False
    return df


def _calculate_go_errors(df, err_type):
    """Take pandas data frame and return boolean list (true if go error).
    """
    errors = []
    for idx, series in df.iterrows():
        error = False
        if series['stimulus'].isdigit() and not series['correct'] and \
                not series['anticipate_error']:
            if err_type == 'go' and series['stimulus'] != '3':
                error = True
            elif err_type == 'no_go' and series['stimulus'] == '3':
                error = True
        errors.append(error)
    return errors


def summarize_block_performance(df):
    """Take pandas dataframe representing raw SART trails data and
    summarize performance. Return dict.
    """
    performance = {}

    # number of trials
    num_trials = len(df.index.values)
    performance['num_trials'] = num_trials

    # average reaction time
    rts = _format_rts(df['rt'].values)
    performance['rt_avg'] = round(np.mean(rts), ROUND_NDIGITS)

    # add anticipation errors and re-calculate `correct` column
    df = _add_anticipation_errors(df)

    # number of anticipation errors
    antipations = list(df['anticipate_error'].values)
    anticipated = float(antipations.count(True)) / num_trials
    performance['anticipated'] = round(anticipated, ROUND_NDIGITS)

    # overall accuracy
    corrects = list(df['correct'].values)
    accuracy = float(corrects.count(True)) / num_trials
    performance['accuracy'] = round(accuracy, ROUND_NDIGITS)

    # number of go errors
    go_errors = _calculate_go_errors(df, 'go')
    go_errors_prop = float(go_errors.count(True)) / num_trials
    performance['go_errors'] = round(go_errors_prop, ROUND_NDIGITS)

    # number of no-go errors
    no_go_errors = _calculate_go_errors(df, 'no_go')
    no_go_errors_prop = float(no_go_errors.count(True)) / num_trials
    performance['no_go_errors'] = round(no_go_errors_prop, ROUND_NDIGITS)

    return performance


def summarize_sart_chunk(df):
    """Take pandas dataframe representing raw SART chunk data and create a
    complete summary. Return dict.
    """
    summary = {}

    # summarize performance
    sart_trials = df.loc[df['trial_type'] == 'multi-stim-multi-response']
    performance = summarize_block_performance(sart_trials)
    summary.update(performance)

    # affective ratings
    survey_trials = df.loc[df['trial_type'] == 'survey-multi-choice'].\
        copy().reset_index()

    effort_rating_json = survey_trials.ix[0]['responses']
    raw_effort_rating = get_response_from_json(effort_rating_json)
    summary['effort'] = int(raw_effort_rating[0])

    discomfort_rating_json = survey_trials.ix[1]['responses']
    raw_discomfort_rating = get_response_from_json(discomfort_rating_json)
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
        ('age', '0.0-1.0-0.0'),
        ('dob', '0.0-1.0-1.0'),

        ('sex', '0.0-2.0-0.0'),
        ('edu_year', '0.0-2.0-1.0'),
        ('edu_plan', '0.0-2.0-2.0'),
        ('eng_first_lang', '0.0-2.0-3.0'),
        ('eng_years', '0.0-2.0-4.0'),
        ('mother_edu', '0.0-2.0-5.0'),

        ('mother_job', '0.0-3.0'),

        ('father_edu', '0.0-4.0-0.0'),

        ('father_job', '0.0-5.0-0.0'),
        ('high_school_avg', '0.0-5.0-1.0'),
        ('uni_avg', '0.0-5.0-2.0'),

        ('num_uni_stats', '0.0-6.0-0.0'),
        ('num_hs_stats', '0.0-6.0-1.0'),
        ('num_hs_math', '0.0-6.0-2.0'),
        ('num_uni_math', '0.0-6.0-3.0'),
        ('math_enjoy', '0.0-6.0-4.0'),
        ('adhd_diag', '0.0-6.0-5.0'),

        ('uni_major', '0.0-7.0'),

        # electronics and Internet survey
        ('elect_survey_1', '0.0-8.0-0.0'),
        ('elect_survey_2', '0.0-8.0-1.0'),
        ('elect_survey_3', '0.0-8.0-2.0'),
        ('elect_survey_4', '0.0-8.0-3.0'),
        ('elect_survey_5', '0.0-8.0-4.0'),
        ('elect_survey_6', '0.0-8.0-5.0'),
        ('elect_survey_7', '0.0-9.0')
    ]
    for label, inid in demographics_index:
        compiled_data[label] = get_response_from_node_id(df, inid)

    behavioural_survey = [
        # behavioural survey
        ('behav_survey_1', '0.0-11.0-0.0'),
        ('behav_survey_2', '0.0-11.0-1.0'),
        ('behav_survey_3', '0.0-11.0-2.0'),
        ('behav_survey_4', '0.0-11.0-3.0'),
        ('behav_survey_5', '0.0-11.0-4.0'),
        ('behav_survey_6', '0.0-11.0-5.0'),
        ('behav_survey_7', '0.0-11.0-6.0'),
        ('behav_survey_8', '0.0-11.0-7.0'),
        ('behav_survey_9', '0.0-11.0-8.0'),
        ('behav_survey_10', '0.0-11.0-9.0'),
        ('behav_survey_11', '0.0-11.0-10.0'),
        ('behav_survey_12', '0.0-11.0-11.0'),
        ('behav_survey_13', '0.0-11.0-12.0'),
        ('behav_survey_14', '0.0-11.0-13.0'),
        ('behav_survey_15', '0.0-11.0-14.0'),
        ('behav_survey_16', '0.0-11.0-15.0'),
        ('behav_survey_17', '0.0-11.0-16.0'),
        ('behav_survey_18', '0.0-11.0-17.0'),

    ]
    for label, inid in behavioural_survey:
        compiled_data[label] = get_response_from_node_id(
            df, inid, is_likert=True)

    # post-working memory task delay
    if 46 in df.index.values:
        compiled_data['time_pwmt_delay_ms'] = int(df.ix[46]['time_elapsed'])

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
        ('pwmt_effort', '0.0-13.0-0.0'),
        ('pwmt_discomfort', '0.0-13.0-1.0'),
        ('pwmt_performance', '0.0-13.0-2.0'),
        ('pwmt_willingtodowmt', '0.0-13.0-3.0'),
        ('pwmt_fatigue', '0.0-13.0-4.0'),
        ('pwmt_satisfaction', '0.0-13.0-5.0'),
        ('pwmt_didmybest', '0.0-13.0-6.0'),
        ('pwmt_enjoyment', '0.0-13.0-7.0'),
    ]
    for label, inid in retrospective_index:
        compiled_data[label] = get_response_from_node_id(
            df, inid, is_likert=True)

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
