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
    assert data['id'] == "003"
    assert data['practice_condition'] == 'num_trials'
    assert data['num_practice_blk2s'] == 1
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
    assert data['num_practice_blk2s'] == 3
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


def test__format_rts():
    rts = ['[667]']
    rts_strf = compile_data._format_rts(rts)
    assert isinstance(rts_strf, list)
    assert len(rts_strf) == 1
    for rt in rts_strf:
        assert isinstance(rt, int)


def get_sart_trial_block(pid, block_index=0):
    df = get_csv_as_df('experiment', pid)
    blocks = compile_data.extract_sart_blocks(df, with_survey=True)
    b1 = blocks[block_index]
    trial_block = b1.loc[b1['trial_type'] == 'multi-stim-multi-response']
    return trial_block


def test__format_rts_with_data():
    pid = "011"
    sart_block = get_sart_trial_block(pid)
    rt_strf = compile_data._format_rts(sart_block['rt'])
    assert isinstance(rt_strf, list)
    assert len(rt_strf) == 59
    for rt in rt_strf:
        assert isinstance(rt, int)


def test__is_anticipation_error():
    assert not compile_data._is_anticipation_error('[667]')
    assert not compile_data._is_anticipation_error('[100]')
    assert compile_data._is_anticipation_error('[99]')
    assert compile_data._is_anticipation_error('[15]')
    assert not compile_data._is_anticipation_error('[-1]')


def test__add_anticipation_errors_to_df():
    pid = "104"
    df = get_sart_trial_block(pid)
    df_anticip = compile_data._add_anticipation_errors(df)
    assert 'anticipate_error' in df_anticip
    anticipated = list(df_anticip.anticipate_error)
    assert anticipated.count(True) == 6


def test___calculate_go_errors():
    pid = "104"
    df = get_sart_trial_block(pid)

    # check known values
    assert list(df.correct.values).count(False) == 5

    df = compile_data._add_anticipation_errors(df)

    # check known values
    assert list(df.anticipate_error.values).count(True) == 6
    assert list(df.correct.values).count(False) == 11

    go_errors = compile_data._calculate_go_errors(df, 'go')
    assert isinstance(go_errors, compile_data.pd.Series)
    assert list(go_errors).count(True) == 1
    nogo_errors = compile_data._calculate_go_errors(df, 'no_go')
    assert isinstance(nogo_errors, compile_data.pd.Series)
    assert list(nogo_errors).count(True) == 4


def test__calculate_nogo_error_rt_avgs_104():
    pid = "104"
    df = get_sart_trial_block(pid)
    df = compile_data._add_anticipation_errors(df)
    df['nogo_error'] = compile_data._calculate_go_errors(df, 'no_go')
    assert list(df['nogo_error']).count(True) == 4

    adjacent_rts = compile_data._calculate_nogo_error_rt_avgs(df)
    assert adjacent_rts['prev4_avg'] == 254.4375
    assert adjacent_rts['num_prev4_rts'] == 16
    assert adjacent_rts['next4_avg'] == 224.1875
    assert adjacent_rts['num_next4_rts'] == 16


def test__calculate_nogo_error_rt_avgs_011():
    pid = "011"
    df = get_sart_trial_block(pid)
    df = compile_data._add_anticipation_errors(df)
    df['nogo_error'] = compile_data._calculate_go_errors(df, 'no_go')
    assert list(df['nogo_error']).count(True) == 4

    adjacent_rts = compile_data._calculate_nogo_error_rt_avgs(df)
    assert adjacent_rts['prev4_avg'] == 347.142857143
    assert adjacent_rts['num_prev4_rts'] == 7
    assert adjacent_rts['next4_avg'] == 391.875
    assert adjacent_rts['num_next4_rts'] == 8


def test_summarize_block_performance():
    pid = "104"
    sart_block = get_sart_trial_block(pid)
    p = compile_data.summarize_block_performance(sart_block)
    assert p['num_trials'] == 82
    assert p['rt_avg'] == 272.790123457
    assert p['anticipated'] == 0.073170732  # 6 anticipation errors
    assert p['go_errors'] == 0.012195122  # 1 go error
    assert p['nogo_errors'] == 0.048780488  # 4 no-go errors
    assert p['accuracy'] == 0.865853659  # 71/82
    total_error_prop = (p['anticipated'] + p['go_errors'] + p['nogo_errors'])

    # average RTs before and after no-go errors
    assert p['nogo_prev4_avg'] == 254.4375
    assert p['nogo_next4_avg'] == 224.1875

    # ensure that calculations match up
    rnd = compile_data.ROUND_NDIGITS
    assert round(total_error_prop, rnd-1) == round(1 - p['accuracy'], rnd-1)


def test_summarize_sart_chunk():
    pid = "011"
    df = get_csv_as_df('experiment', pid)
    blocks = compile_data.extract_sart_blocks(df, with_survey=True)

    # first block
    b1 = blocks[0]
    b1s = compile_data.summarize_sart_chunk(b1)
    assert b1s['anticipated'] == 0.0
    assert b1s['accuracy'] == 0.731707317
    assert b1s['effort'] == 4
    assert b1s['discomfort'] == 5

    assert b1s['num_trials'] == 82

    assert b1s['nogo_prev4_avg'] == 347.142857143
    assert b1s['nogo_next4_avg'] == 391.875

    # last block
    lb = blocks[-1]
    lbs = compile_data.summarize_sart_chunk(lb)
    assert lbs['num_trials'] == 68
    assert lbs['anticipated'] == 0.014705882
    assert lbs['accuracy'] == 0.911764706
    assert lbs['effort'] == 3
    assert lbs['discomfort'] == 5


def test_complete_compile_experiment_data():
    pid = "104"
    df = get_csv_as_df('experiment', pid)
    ed = compile_data.compile_experiment_data(df)

    assert ed['num_trials'] == 646
    assert ed['trials_per_block'] == 82
    assert ed['num_blocks'] == 8

    assert ed['anticipated_enjoyment'] == 5
    assert ed['anticipated_performance'] == 4
    assert ed['anticipated_effort'] == 6
    assert ed['anticipated_discomfort'] == 5
    assert ed['anticipated_fatigue'] == 2
    assert ed['anticipated_motivation'] == 4

    # check keys for each block's real-time data
    blk_summary_keys = [
        'anticipated', 'nogo_next4_avg', 'nogo_prev4_avg', 'go_errors',
        'effort', 'num_trials', 'discomfort', 'rt_avg', 'nogo_errors',
        'accuracy'
        ]
    for i in range(1, 9):
        blk_key_prefix = "blk{}".format(i)
        blk_keys = [k for k in ed.keys() if k.startswith(blk_key_prefix)]
        assert len(blk_keys) == 12
        for k in blk_summary_keys:
            expected_blk_key = "{}_{}".format(blk_key_prefix, k)
            assert expected_blk_key in blk_keys

    # no-go error variable weighted averages
    assert ed['nogo_error_prev_rt_avg'] == 340.17721518987344
    assert ed['nogo_error_next_rt_avg'] == 336.77181208063763

    # peak-end calculations
    assert ed['start_effort'] == 2
    assert ed['peak_effort'] == 7
    assert ed['end_effort'] == 3
    assert ed['avg_effort'] == 4.125

    assert ed['start_discomfort'] == 4
    assert ed['peak_discomfort'] == 7
    assert ed['end_discomfort'] == 6
    assert ed['avg_discomfort'] == 5

    assert ed['avg_accuracy'] == 0.851753049
    assert ed['max_accuracy'] == 0.951219512
    assert ed['min_accuracy'] == 0.62195122
    assert ed['start_accuracy'] == 0.865853659
    assert ed['end_accuracy'] == 0.875

    assert ed['auc_accuracy'] == 5.943597561
    assert ed['auc_effort'] == 30.5
    assert ed['auc_discomfort'] == 35.0

    assert ed['time_experiment_ms'] == 940644


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
