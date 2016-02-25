# -*- coding: utf-8 -*-
import os

import pytest

from scripts import compile_data


TESTS_DIR = os.path.abspath(os.path.join(__file__, '..'))
MOCK_DATA_DIR = os.path.join(TESTS_DIR, 'mock_data')


def _csv_path(stage, pid):
    return os.path.join(MOCK_DATA_DIR, stage, '{}.csv'.format(pid))


def test_get_data_file_paths_returns_list_of_paths():
    mock_practice_csvs = compile_data.get_csv_paths(MOCK_DATA_DIR, 'practice')
    assert len(mock_practice_csvs) == 5
    assert _csv_path('practice', '003') in mock_practice_csvs


def test_extract_sart_blocks_with_2_practice():
    # NOTE: tests out get_csv_as_dataframe() from compile_data
    csv_path = _csv_path('practice', '003')
    df = compile_data.get_csv_as_dataframe(csv_path)
    blocks = compile_data.extract_sart_blocks(df)
    assert len(blocks) == 2
    for b in blocks:
        assert isinstance(b, compile_data.pd.DataFrame)
    # number of trials
    assert len(blocks[0].index.values) == 5
    assert len(blocks[1].index.values) == 15


def get_csv_as_df(stage, pid):
    """Take an experiment stage and participant ID and return a pandas
    data frame.
    """
    csv_path = os.path.join(MOCK_DATA_DIR, stage, '{}.csv'.format(pid))
    df = compile_data.get_csv_as_dataframe(csv_path)
    return df


def test_extract_sart_blocks_with_4_practice():
    df = get_csv_as_df('practice', 'fail1')
    blocks = compile_data.extract_sart_blocks(df)
    assert len(blocks) == 4

    # number of trials
    assert len(blocks[0].index.values) == 29
    assert len(blocks[1].index.values) == 72
    assert len(blocks[2].index.values) == 72
    assert len(blocks[3].index.values) == 72

    for b in blocks:
        # class
        assert isinstance(b, compile_data.pd.DataFrame)

        # trials
        for idx, series in b.iterrows():
            series['trial_type'] == 'multi-stim-multi-response'


def test_extract_sart_blocks_with_4_practice_and_survey():
    df = get_csv_as_df('experiment', '104')
    blocks = compile_data.extract_sart_blocks(df, with_survey=True)
    # basic structure
    assert len(blocks) == 8
    for b in blocks:
        assert isinstance(b, compile_data.pd.DataFrame)

    # number of trials
    assert len(blocks[0].index.values) == 84
    assert len(blocks[1].index.values) == 84
    assert len(blocks[2].index.values) == 84
    assert len(blocks[3].index.values) == 84
    assert len(blocks[4].index.values) == 84
    assert len(blocks[5].index.values) == 84
    assert len(blocks[6].index.values) == 84
    assert len(blocks[7].index.values) == 74

    # trial structure
    trial_type_mc = 'survey-multi-choice'
    trial_type_msmr = 'multi-stim-multi-response'

    b7 = blocks[7]
    b7_last_idx = b7.last_valid_index()
    b7_first_idx = b7.first_valid_index()
    assert b7.ix[b7_first_idx]['trial_type'] == trial_type_msmr
    assert b7.ix[b7_last_idx-1]['trial_type'] == trial_type_mc
    assert b7.ix[b7_last_idx]['trial_type'] == trial_type_mc


def test_passing_compile_practice_data():
    df = get_csv_as_df('practice', '003')
    data = compile_data.compile_practice_data(df)
    assert data['id'] == 3
    assert data['practice_condition'] == 'num_trials'
    assert data['passed_practice'] == True
    assert data['time_practice_blk1_ms'] == 6030
    assert data['time_practice_blk2_1_ms'] == 16165
    assert data['time_practice_ms'] == 67198


def test_failing_compile_practice_data():
    pid = "fail1"
    df = get_csv_as_df('practice', pid)
    data = compile_data.compile_practice_data(df)
    assert data['id'] == pid
    assert data['practice_condition'] == 'time_duration'
    assert data['passed_practice'] == False
    assert data['time_practice_blk1_ms'] == 42198
    assert data['time_practice_blk2_1_ms'] == 120397
    assert data['time_practice_blk2_2_ms'] == 140798
    assert data['time_practice_blk2_3_ms'] == 125869
    assert data['time_practice_ms'] == 469892


def test_get_response_from_json():
    json = '{"Q0":"3"}'
    resp1 = compile_data.get_response_from_json(json)
    assert resp1 == "3"

    json = '{"Q0":"2<br>Often or<br>very much"}'
    resp1 = compile_data.get_response_from_json(json)
    assert resp1 == "2<br>Often or<br>very much"


def test_get_response_from_node_id():
    df = get_csv_as_df('follow_up', '003')
    resp1 = compile_data.get_response_from_node_id(df, '0.0-1.0-0.0')
    assert resp1 == '22'
    resp2 = compile_data.get_response_from_node_id(df, '0.0-2.0-0.0')
    assert resp2 == 'Female'


def test_summarize_sart_chunk():
    pid = "011"
    df = get_csv_as_df('experiment', pid)
    blocks = compile_data.extract_sart_blocks(df, with_survey=True)


    # first block
    b1 = blocks[0]
    b1_summary = compile_data.summarize_sart_chunk(b1)
    assert b1_summary['num_trials'] == 82
    assert b1_summary['accuracy'] == 0.731707317
    assert b1_summary['effort'] == 4
    assert b1_summary['discomfort'] == 5

    # last block
    lb = blocks[-1]
    lb_summary = compile_data.summarize_sart_chunk(lb)
    assert lb_summary['num_trials'] == 68
    assert lb_summary['accuracy'] == 0.926470588
    assert lb_summary['effort'] == 3
    assert lb_summary['discomfort'] == 5


# def test_complete_compile_experiment_data():
#     pid = "011"
#     df = get_csv_as_df('experiment', pid)
#     data = compile_data.compile_experiment_data(df)
#     assert data['condition'] == 5
#
#     assert data['block_order'] == ('medium,medium,hard,medium,easy,'
#                                    'medium,medium,medium,medium')
#     assert data['num_blocks'] == 9

#     assert data['anticipated_enjoyment'] == 3
#     assert data['anticipated_performance'] == 4
#     assert data['anticipated_effort'] == 4
#     assert data['anticipated_discomfort'] == 4
#     assert data['anticipated_fatigue'] == 4
#
#     # real-time data for each block
#     assert data['accuracy_1'] == 0.571428571
#     assert data['accuracy_2'] == 0.428571429
#     assert data['accuracy_3'] == 0.357142857
#     assert data['accuracy_4'] == 0.5
#     assert data['accuracy_5'] == 0.571428571
#     assert data['accuracy_6'] == 0.285714286
#     assert data['accuracy_7'] == 0.357142857
#     assert data['accuracy_8'] == 0.428571429
#     assert data['accuracy_9'] == 0.357142857
#     assert 'accuracy_10' not in data.keys()
#
#     assert data['effort_1'] == 5
#     assert data['effort_2'] == 4
#     assert data['effort_3'] == 4
#     assert data['effort_4'] == 4
#     assert data['effort_5'] == 4
#     assert data['effort_6'] == 7
#     assert data['effort_7'] == 1
#     assert data['effort_8'] == 2
#     assert data['effort_9'] == 7
#     assert 'effort_10' not in data.keys()
#
#     assert data['discomfort_1'] == 5
#     assert data['discomfort_2'] == 4
#     assert data['discomfort_3'] == 4
#     assert data['discomfort_4'] == 4
#     assert data['discomfort_5'] == 4
#     assert data['discomfort_6'] == 7
#     assert data['discomfort_7'] == 1
#     assert data['discomfort_8'] == 2
#     assert data['discomfort_9'] == 7
#     assert 'discomfort_10' not in data.keys()
#
#     # real-time data by block type
#     assert data['medium_accuracy'] == 0.418367347
#     assert data['medium_effort'] == 4.285714286
#     assert data['medium_discomfort'] == 4.285714286
#
#     assert data['medium_accuracy_slope'] == -0.021539028
#     assert data['medium_accuracy_intercept'] == 0.532216495
#     assert data['medium_effort_slope'] == -0.028350515
#     assert data['medium_effort_intercept'] == 4.43556701
#     assert data['medium_discomfort_slope'] == -0.028350515
#     assert data['medium_discomfort_intercept'] == 4.43556701
#
#     assert data['hard_accuracy'] == 0.357142857
#     assert data['hard_effort'] == 4
#     assert data['hard_discomfort'] == 4
#     assert data['easy_accuracy'] == 0.571428571
#     assert data['easy_effort'] == 4
#     assert data['easy_discomfort'] == 4
#
#     assert data['start_discomfort'] == 5
#     assert data['peak_discomfort'] == 7
#     assert data['end_discomfort'] == 7
#     assert data['avg_discomfort'] == 4.222222222
#
#     assert data['start_effort'] == 5
#     assert data['peak_effort'] == 7
#     assert data['end_effort'] == 7
#     assert data['avg_effort'] == 4.222222222
#
#     assert data['avg_accuracy'] == 0.428571429
#     assert data['max_accuracy'] == 0.571428571
#     assert data['min_accuracy'] == 0.285714286
#     assert data['start_accuracy'] == 0.571428571
#     assert data['end_accuracy'] == 0.357142857
#
#     assert data['auc_accuracy'] == 3.392857143
#     assert data['auc_effort'] == 32.0
#     assert data['auc_discomfort'] == 32.0
#
#     assert data['time_experiment_ms'] == 831136


def test_complete_demographics_data():
    pid = "003"
    df = get_csv_as_df('follow_up', pid)
    data = compile_data.compile_demographic_data(df)
    expected_answers = [
        ('age', '22'),
        ('dob', '03/1993'),
        ('sex', 'Female'),
        ('edu_year', 'Graduated'),
        ('edu_plan', 'PhD'),
        ('eng_first_lang', 'Yes'),
        ('eng_years', 'All my life'),
        ('mother_edu', 'Professional degree (e.g., law)'),
        ('mother_job', 'lawyer'),
        ('father_edu', 'MA/MSc degree'),
        ('father_job', 'computer scientist'),
        ('high_school_avg', '90'),
        ('uni_avg', 'n/a'),
        ('num_uni_stats', '1'),
        ('num_hs_stats', 'None'),
        ('num_hs_math', '4'),
        ('num_uni_math', 'None'),
        ('math_enjoy', '5'),
        ('adhd_diag', 'Yes'),
        ('uni_major', 'n/a'),

        ('elect_survey_1', 'No'),
        ('elect_survey_2', 'Yes'),
        ('elect_survey_3', 'Yes'),
        ('elect_survey_4', 'Yes'),
        ('elect_survey_5', 'Yes'),
        ('elect_survey_6', 'Yes'),
        ('elect_survey_7', '1'),

        ('behav_survey_1', 'N/A'),
        ('behav_survey_2', 'N/A'),
        ('behav_survey_3', '2'),
        ('behav_survey_4', 'N/A'),
        ('behav_survey_5', '2'),
        ('behav_survey_6', 'N/A'),
        ('behav_survey_7', 'N/A'),
        ('behav_survey_8', 'N/A'),
        ('behav_survey_9', 'N/A'),
        ('behav_survey_10', 'N/A'),
        ('behav_survey_11', 'N/A'),
        ('behav_survey_12', 'N/A'),
        ('behav_survey_13', 'N/A'),
        ('behav_survey_14', 'N/A'),
        ('behav_survey_15', 'N/A'),
        ('behav_survey_16', 'N/A'),
        ('behav_survey_17', 'N/A'),
        ('behav_survey_18', 'N/A'),

        ('time_pwmt_delay_ms', 196373),
        ('time_follow_up_ms', 220848),
    ]
    for label, answer in expected_answers:
        assert data[label] == answer


def test_complete_retrospective_data():
    pid = "003"
    df = get_csv_as_df('follow_up', pid)
    data = compile_data.compile_retrospective_data(df)
    expected_answers = [
        ('pwmt_effort', '4'),
        ('pwmt_discomfort', '4'),
        ('pwmt_performance', '4'),
        ('pwmt_willingtodowmt', '4'),
        ('pwmt_fatigue', '4'),
        ('pwmt_satisfaction', '4'),
        ('pwmt_didmybest', '4'),
        ('pwmt_enjoyment', '7'),
    ]
    for label, answer in expected_answers:
        assert data[label] == answer
