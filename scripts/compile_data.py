#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""A script that parses raw data output by jsSART (jsPsych), compiles each
participant's data and creates/updates a file in jsSART's ``data``
directory.
"""
import os
import glob
import json
import re

import pandas as pd
import numpy as np
from scipy import stats
from tqdm import tqdm


PROJECT_DIR = os.path.abspath(os.path.join(__file__, '..', '..'))
DATA_DIR = os.path.join(PROJECT_DIR, 'data')
DECODER = json.JSONDecoder()
ROUND_NDIGITS = 9

# pandas options
pd.options.mode.chained_assignment = None  # no false-positive warnings


def get_csv_paths(basedir, exp_stage):
    """Take base data directory and experiment stage. Return list of file paths.
    """
    glob_path = os.path.join(basedir, exp_stage, '*.csv')
    return glob.glob(glob_path)


def get_csv_as_dataframe(path):
    """Take CSV path. Return pandas dataframe.
    """
    return pd.read_csv(path,
                       index_col='trial_index',
                       converters={'participant_id': lambda x: str(x)}
                       )


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


def _get_arousal_ratings(df):
    """Take 2-row pandas data frame and return mind-and-body and feeling
    ratings for evaluation of valence and arousal questions.
    """
    mind_body = None
    feeling = None

    re_prefix = r'\d+\.\d+\-\d+\.\d+\-'
    mind_body_inid_pattern = r'{}0\.0'.format(re_prefix)
    feeling_inid_pattern = r'{}1\.0'.format(re_prefix)

    for i, d in df.iterrows():
        inid = d['internal_node_id']
        if re.match(mind_body_inid_pattern, inid):
            mind_body = get_response_from_node_id(df, inid, is_likert=True)
        elif re.match(feeling_inid_pattern, inid):
            feeling = get_response_from_node_id(df, inid, is_likert=True)

    return mind_body, feeling


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

    # baseline evaluation of valence and arousal
    arousal_df = df.ix[1:2]
    mind_body, feeling = _get_arousal_ratings(arousal_df)
    compiled_data['arousal_baseline_mind_body'] = mind_body
    compiled_data['arousal_baseline_feeling'] = feeling

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
    return pd.Series(errors, index=df.index)


def _calculate_nogo_error_rt_avgs(df):
    """Take pandas dataframe representing raw SART trails data,
    calculate reaction time average before and after no-go errors and
    return before and after RT averages.
    """
    MAX_ADJACENT_ROWS = 4

    def get_adjacent_row_rts(idx, direction):
        row_idx = idx
        next_num_rows = 0

        if direction == 'next':
            break_row_idx = df.last_valid_index()
        if direction == 'prev':
            break_row_idx = df.first_valid_index()

        row_rts = []
        while next_num_rows < MAX_ADJACENT_ROWS and row_idx != break_row_idx:
            # adjacent row index
            if direction == 'next':
                row_idx += 1
            if direction == 'prev':
                row_idx -= 1

            row = df[df.index == row_idx]
            rts = row['rt'].values

            # stop collecting rows if no trial response (rt = [-1])
            if not rts == ['[-1]']:
                row_rt = _format_rts(rts)
                if row_rt:
                    row_rts.append(row_rt[0])

            next_num_rows += 1
        return row_rts

    # find all no-go errors
    nogo_error_rows = []
    for row in df.iterrows():
        if row[1]['nogo_error'] == True:
            nogo_error_rows.append(row)

    # find all row (trial) RTs before and after no-go error rows
    prev_row_rts = []
    next_row_rts = []
    for nogo_row in nogo_error_rows:
        idx = nogo_row[0]
        prev_nogo_row_rts = get_adjacent_row_rts(idx, 'prev')
        prev_row_rts.append(prev_nogo_row_rts)
        next_nogo_row_rts = get_adjacent_row_rts(idx, 'next')
        next_row_rts.append(next_nogo_row_rts)

    prev4_rts = [rt for sublist in prev_row_rts for rt in sublist]
    prev4_avg = round(np.mean(prev4_rts), ROUND_NDIGITS)
    next4_rts = [rt for sublist in next_row_rts for rt in sublist]
    next4_avg = round(np.mean(next4_rts), ROUND_NDIGITS)

    return {
        "prev4_avg": prev4_avg,
        "num_prev4_rts": len(prev4_rts),
        "next4_avg": next4_avg,
        "num_next4_rts": len(next4_rts)
    }


def _get_correct_rts(df):
    """Take pandas dataframe representing raw SART trails data and
    return array of RTs for correct trials.
    """
    rts = []
    for idx, series in df.iterrows():
        if series['correct']:
            rt = _format_rts([series['rt']])
            if rt:
                rts.append(rt[0])
    return rts


def summarize_block_performance(df):
    """Take pandas dataframe representing raw SART trails data and
    summarize performance. Return dict.
    """
    performance = {}

    # number of trials
    num_trials = len(df.index.values)
    performance['num_trials'] = num_trials

    # add anticipation errors and re-calculate `correct` column
    df = _add_anticipation_errors(df)

    # number of anticipation errors
    antipations = list(df['anticipate_error'].values)
    anticipated = (float(antipations.count(True)) / num_trials)
    performance['anticipated'] = round(anticipated, ROUND_NDIGITS)

    # overall accuracy
    corrects = list(df['correct'].values)
    accuracy = (float(corrects.count(True)) / num_trials)
    performance['accuracy'] = round(accuracy, ROUND_NDIGITS)

    # number of go errors
    df['go_error'] = _calculate_go_errors(df, 'go')
    go_errors = list(df['go_error'].values)
    go_errors_prop = (float(go_errors.count(True)) / num_trials)
    performance['go_errors'] = round(go_errors_prop, ROUND_NDIGITS)

    # number of no-go errors
    df['nogo_error'] = _calculate_go_errors(df, 'no_go')
    nogo_errors = list(df['nogo_error'].values)
    performance['nogo_num_errors'] = nogo_errors.count(True)
    nogo_errors_prop = (float(nogo_errors.count(True)) / num_trials)
    performance['nogo_errors'] = round(nogo_errors_prop, ROUND_NDIGITS)

    # average reaction time (RT)
    correct_rts = _get_correct_rts(df)
    performance['rt_avg'] = round(np.mean(correct_rts), ROUND_NDIGITS)

    # average RTs before and after no-go errors
    nogo_adjacent_rts = _calculate_nogo_error_rt_avgs(df)
    performance['nogo_prev4_avg'] = nogo_adjacent_rts['prev4_avg']
    performance['nogo_num_prev4_rts'] = nogo_adjacent_rts['num_prev4_rts']
    performance['nogo_next4_avg'] = nogo_adjacent_rts['next4_avg']
    performance['nogo_num_next4_rts'] = nogo_adjacent_rts['num_next4_rts']

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


def _calculate_ratings_proportions(ratings):
    """Given a list of ratings integers, calcuate the number of changes.
    Return dict indicating proportion of increases, decreases, and no-changes.
    """
    def changes_prop(changes):
        """Calculate changes as a proportion of possible changes in main list.
        """
        possible_changes = (len(ratings) - 1)
        return round(float(len(changes)) / possible_changes, ROUND_NDIGITS)

    ups = []
    downs = []
    sames = []
    last_rating = None
    for rating in ratings:
        if last_rating:
            if rating > last_rating:
                ups.append(rating)
            elif rating < last_rating:
                downs.append(rating)
            else:
                sames.append(rating)
        last_rating = rating

    return {
        'ups': changes_prop(ups),
        'downs': changes_prop(downs),
        'sames': changes_prop(sames)
    }


def compile_experiment_data(df):
    """Take pandas dataframe and compile key variables. Return dict.
    """
    compiled_data = {}

    # conditions
    compiled_data['num_trials'] = df['num_trials'].values[0]
    compiled_data['trials_per_block'] = df['trials_per_block'].values[0]

    # blocks and block order
    blocks = extract_sart_blocks(df, with_survey=True)
    compiled_data['num_blocks'] = len(blocks)

    # anticipated questions
    anticipated_questions_index = [
        ('forecasted_enjoyment', 1),
        ('forecasted_performance', 2),
        ('forecasted_effort', 3),
        ('forecasted_discomfort', 4),
        ('forecasted_fatigue', 5),
        ('forecasted_motivation', 6)
    ]
    for label, i in anticipated_questions_index:
        response = get_response_from_json(df.ix[i]['responses'])
        compiled_data[label] = int(response[0])

    # SART accuracy and affective reports
    effort_ratings = []
    discomfort_ratings = []
    accuracies = []
    num_block_trials = []

    # for calculating no-go error averages
    nogo_num_errors = 0
    nogo_prev4_avgs = []
    nogo_next4_avgs = []
    nogo_num_next4_rts = []
    nogo_num_prev4_rts = []

    # collect and organize experiment data from experimental blocks
    for i, block in enumerate(blocks, start=1):
        blk_summary = summarize_sart_chunk(block)
        blk_name = "blk{}".format(i)

        # add block summaries to compiled data
        for key in blk_summary.keys():
            blk_key = "{}_{}".format(blk_name, key)
            compiled_data[blk_key] = blk_summary[key]

        # collect data for later averaging
        effort_ratings.append(blk_summary['effort'])
        discomfort_ratings.append(blk_summary['discomfort'])
        accuracies.append(blk_summary['accuracy'])
        num_block_trials.append(blk_summary['num_trials'])

        nogo_num_errors += blk_summary['nogo_num_errors']
        nogo_prev4_avgs.append(blk_summary['nogo_prev4_avg'])
        nogo_num_prev4_rts.append(blk_summary['nogo_num_prev4_rts'])
        nogo_next4_avgs.append(blk_summary['nogo_next4_avg'])
        nogo_num_next4_rts.append(blk_summary['nogo_num_next4_rts'])

    # weighted averages for RTs before and after no-go errors
    compiled_data['nogo_num_errors'] = nogo_num_errors
    compiled_data['nogo_error_prev_rt_avg'] = np.average(
        nogo_prev4_avgs, weights=nogo_num_prev4_rts)
    compiled_data['nogo_error_next_rt_avg'] = np.average(
        nogo_next4_avgs, weights=nogo_num_next4_rts)

    # assign other variables
    compiled_data['start_effort'] = effort_ratings[0]
    compiled_data['peak_effort'] = max(effort_ratings)
    compiled_data['min_effort'] = min(effort_ratings)
    compiled_data['end_effort'] = effort_ratings[-1]
    avg_effort = np.mean(effort_ratings)
    compiled_data['avg_effort'] = round(avg_effort, ROUND_NDIGITS)

    compiled_data['start_discomfort'] = discomfort_ratings[0]
    compiled_data['peak_discomfort'] = max(discomfort_ratings)
    compiled_data['min_discomfort'] = min(discomfort_ratings)
    compiled_data['end_discomfort'] = discomfort_ratings[-1]
    avg_discomfort = np.mean(discomfort_ratings)
    compiled_data['avg_discomfort'] = round(avg_discomfort, ROUND_NDIGITS)

    average_accuracy = np.average(accuracies, weights=num_block_trials)
    compiled_data['avg_accuracy'] = round(average_accuracy, ROUND_NDIGITS)
    compiled_data['max_accuracy'] = max(accuracies)
    compiled_data['min_accuracy'] = min(accuracies)
    compiled_data['start_accuracy'] = accuracies[0]
    compiled_data['end_accuracy'] = accuracies[-1]

    # proportion of effort and discomfort ratings that increase or decrease
    discomfort_props = _calculate_ratings_proportions(discomfort_ratings)
    compiled_data['prop_discomfort_ups'] = discomfort_props['ups']
    compiled_data['prop_discomfort_downs'] = discomfort_props['downs']
    compiled_data['prop_discomfort_sames'] = discomfort_props['sames']

    effort_props = _calculate_ratings_proportions(effort_ratings)
    compiled_data['prop_effort_ups'] = effort_props['ups']
    compiled_data['prop_effort_downs'] = effort_props['downs']
    compiled_data['prop_effort_sames'] = effort_props['sames']

    # area under the curve calculations
    compiled_data['auc_accuracy'] = round(
        np.trapz(accuracies), ROUND_NDIGITS)
    compiled_data['auc_effort'] = round(
        np.trapz(effort_ratings), ROUND_NDIGITS)
    compiled_data['auc_discomfort'] = round(
        np.trapz(discomfort_ratings), ROUND_NDIGITS)

    # post-experiment evaluation of valence and arousal
    arousal_df = df.ix[df.last_valid_index()-2:df.last_valid_index()-1]
    mind_body, feeling = _get_arousal_ratings(arousal_df)
    compiled_data['arousal_post_mind_body'] = mind_body
    compiled_data['arousal_post_feeling'] = feeling

    # time taken to complete working memory task
    time_experiment_ms = int(df.ix[df.last_valid_index()]['time_elapsed'])
    compiled_data['time_experiment_ms'] = time_experiment_ms

    return compiled_data


DEMOGRAPHICS_INDEX = [
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

BEHAVIOURAL_SURVEY_INDEX = [
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


def compile_demographic_data(df):
    """Take pandas dataframe and compile key variables. Return dict.
    """
    compiled_data = {}
    responses = list(df['responses'].dropna().values)

    # demographics
    for label, inid in DEMOGRAPHICS_INDEX:
        compiled_data[label] = get_response_from_node_id(df, inid)

    # behavioursal surveys
    for label, inid in BEHAVIOURAL_SURVEY_INDEX:
        compiled_data[label] = get_response_from_node_id(
            df, inid, is_likert=True)

    # post-working memory task delay
    if 46 in df.index.values:
        delay_b4_retrospect_ms = int(df.ix[46]['time_elapsed'])
        compiled_data['time_delay_b4_retrospect_ms'] = delay_b4_retrospect_ms

    # time taken for post-working memory task follow-up
    time_follow_up_ms = int(df.ix[df.last_valid_index()]['time_elapsed'])
    compiled_data['time_follow_up_ms'] = time_follow_up_ms

    return compiled_data


RETROSPECTIVE_INDEX = [
    ('retrospective_effort', '0.0-13.0-0.0'),
    ('retrospective_discomfort', '0.0-13.0-1.0'),
    ('retrospective_performance', '0.0-13.0-2.0'),
    ('retrospective_willingtodowmt', '0.0-13.0-3.0'),
    ('retrospective_fatigue', '0.0-13.0-4.0'),
    ('retrospective_satisfaction', '0.0-13.0-5.0'),
    ('retrospective_didmybest', '0.0-13.0-6.0'),
    ('retrospective_enjoyment', '0.0-13.0-7.0'),
]


def compile_retrospective_data(df):
    """Take pandas dataframe and compile key variables. Return dict.
    """
    compiled_data = {}
    responses = list(df['responses'].dropna().values)

    # retrospective questions
    for label, inid in RETROSPECTIVE_INDEX:
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
    for practice_csv in tqdm(raw_data_csvs['practice']):
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

    # create unordered data frame
    compiled_df = pd.DataFrame.from_dict(compiled_participants)

    # organize variable names
    compiled_var_names = list(compiled_df.columns.values)
    ordered_columns = []

    first_columns = [
        'id',
        'passed_practice',
        'num_practice_blk2s',
        'missing_data',
        'practice_condition',
        'num_trials',
        'trials_per_block',
        'num_blocks',
    ]
    for var_name in first_columns:
        if var_name in compiled_var_names:
            var_index = compiled_var_names.index(var_name)
            ordered_columns.append(compiled_var_names.pop(var_index))

    demographic_columns = []
    indices = [DEMOGRAPHICS_INDEX, BEHAVIOURAL_SURVEY_INDEX,
               RETROSPECTIVE_INDEX]
    for index in indices:
        for var_name, idx in index:
            if var_name in compiled_var_names:
                var_index = compiled_var_names.index(var_name)
                demographic_columns.append(compiled_var_names.pop(var_index))

    ordered_columns += compiled_var_names + demographic_columns
    ordered_compiled_df = compiled_df.reindex_axis(ordered_columns, axis=1)

    # export complete data set to CSV
    compiled_csv_path = os.path.join(DATA_DIR, 'compiled.csv')
    ordered_compiled_df.to_csv(compiled_csv_path, encoding='utf-8')


if __name__ == '__main__':
    main()
