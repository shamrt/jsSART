# -*- coding: utf-8 -*-
import os

import pytest

from scripts import compile_data


TESTS_DIR = os.path.abspath(os.path.join(__file__, '..'))
MOCK_DATA_DIR = os.path.join(TESTS_DIR, 'mock_data')
PID_FAIL = '401'
PID_SUCCESS = '1'
PID_SUCCESS_2 = '2'


def _csv_path(stage, pid):
    return os.path.join(MOCK_DATA_DIR, stage, '{}.csv'.format(pid))


def test_get_data_file_paths_returns_list_of_paths():
    mock_practice_csvs = compile_data.get_csv_paths(MOCK_DATA_DIR, 'practice')
    assert len(mock_practice_csvs) == 3
    assert _csv_path('practice', PID_SUCCESS) in mock_practice_csvs


def test_extract_sart_blocks_with_2_practice():
    # NOTE: tests out get_csv_as_dataframe() from compile_data
    csv_path = _csv_path('practice', PID_SUCCESS)
    df = compile_data.get_csv_as_dataframe(csv_path)
    blocks = compile_data.extract_sart_blocks(df)
    assert len(blocks) == 2
    for b in blocks:
        assert isinstance(b, compile_data.pd.DataFrame)
    # number of trials
    assert len(blocks[0].index.values) == 18
    assert len(blocks[1].index.values) == 27


def get_csv_as_df(stage, pid):
    """Take an experiment stage and participant ID and return a pandas
    data frame.
    """
    csv_path = os.path.join(MOCK_DATA_DIR, stage, '{}.csv'.format(pid))
    df = compile_data.get_csv_as_dataframe(csv_path)
    return df


def test_extract_sart_blocks_with_4_practices():
    """Examine blocks performed by participant who failed practice
    """
    df = get_csv_as_df('practice', PID_FAIL)
    blocks = compile_data.extract_sart_blocks(df)
    assert len(blocks) == 4

    # number of trials
    assert len(blocks[0].index.values) == 18
    assert len(blocks[1].index.values) == 27
    assert len(blocks[2].index.values) == 27
    assert len(blocks[3].index.values) == 27

    for b in blocks:
        # class
        assert isinstance(b, compile_data.pd.DataFrame)

        # trials
        for idx, series in b.iterrows():
            series['trial_type'] == 'multi-stim-multi-response'


def test_extract_sart_blocks_with_experiment_trials_plus_survey():
    df = get_csv_as_df('experiment', PID_SUCCESS)
    blocks = compile_data.extract_sart_blocks(df, with_survey=True)
    # basic structure
    assert len(blocks) == 5
    for b in blocks:
        assert isinstance(b, compile_data.pd.DataFrame)

    # number of trials + multi-choice survey responses
    EXPECTED_BLOCK_LENGTH = 228
    assert len(blocks[0].index.values) == EXPECTED_BLOCK_LENGTH
    assert len(blocks[1].index.values) == EXPECTED_BLOCK_LENGTH
    assert len(blocks[2].index.values) == EXPECTED_BLOCK_LENGTH
    assert len(blocks[3].index.values) == EXPECTED_BLOCK_LENGTH
    assert len(blocks[4].index.values) == EXPECTED_BLOCK_LENGTH

    # trial structure
    trial_type_mc = 'survey-multi-choice'
    trial_type_msmr = 'multi-stim-multi-response'

    b4 = blocks[4]
    b4_last_idx = b4.last_valid_index()
    b4_first_idx = b4.first_valid_index()
    assert b4.ix[b4_first_idx]['trial_type'] == trial_type_msmr
    assert b4.ix[b4_last_idx-3]['trial_type'] == trial_type_msmr
    # last three trials should be multiple choice
    assert b4.ix[b4_last_idx-2]['trial_type'] == trial_type_mc
    assert b4.ix[b4_last_idx-1]['trial_type'] == trial_type_mc
    assert b4.ix[b4_last_idx]['trial_type'] == trial_type_mc


def test_compile_practice_with_passing_data():
    df = get_csv_as_df('practice', PID_SUCCESS)
    data = compile_data.compile_practice_data(df)
    assert data['id'] == PID_SUCCESS
    assert data['num_practice_blk2s'] == 1
    assert data['passed_practice'] is True
    assert data['time_practice_blk1_ms'] == 25851
    assert data['time_practice_blk2_1_ms'] == 29900
    assert data['time_practice_ms'] == 134626


def test_compile_practice_with_failing_data():
    df = get_csv_as_df('practice', PID_FAIL)
    data = compile_data.compile_practice_data(df)
    assert data['id'] == PID_FAIL
    assert data['num_practice_blk2s'] == 3
    assert data['passed_practice'] is False
    assert data['time_practice_blk1_ms'] == 25572
    assert data['time_practice_blk2_1_ms'] == 29968
    assert data['time_practice_blk2_2_ms'] == 29962
    assert data['time_practice_blk2_3_ms'] == 29964

    # baseline evaluation of valence and arousal
    assert data['arousal_baseline_feeling'] == '1'
    assert data['arousal_baseline_mind_body'] == '2'

    assert data['time_practice_ms'] == 152517


def test_get_response_from_json():
    json = '{"Q0":"3"}'
    resp1 = compile_data.get_response_from_json(json)
    assert resp1 == "3"

    json = '{"Q0":"2<br>Often or<br>very much"}'
    resp1 = compile_data.get_response_from_json(json)
    assert resp1 == "2<br>Often or<br>very much"


def test_get_response_via_node_id():
    df = get_csv_as_df('follow_up', PID_SUCCESS)
    resp1 = compile_data.get_response_via_node_id(df, '0.0-1.0-0.0')
    assert resp1 == '28'
    resp2 = compile_data.get_response_via_node_id(df, '0.0-2.0-0.0')
    assert resp2 == 'Female'


def test__format_rts():
    rts = ['[667]']
    rts_strf = compile_data._format_rts(rts)
    assert isinstance(rts_strf, list)
    assert len(rts_strf) == 1
    for rt in rts_strf:
        assert isinstance(rt, int)


def _get_sart_experiment_block(pid, block_index=0):
    df = get_csv_as_df('experiment', pid)
    blocks = compile_data.extract_sart_blocks(df, with_survey=True)
    b = blocks[block_index]
    trial_block = b.loc[b['trial_type'] == 'multi-stim-multi-response']
    return trial_block


def test__format_rts_with_data():
    pid = PID_SUCCESS
    sart_block = _get_sart_experiment_block(pid)
    rt_strf = compile_data._format_rts(sart_block['rt'])
    assert isinstance(rt_strf, list)
    assert len(rt_strf) == 222
    for rt in rt_strf:
        assert isinstance(rt, int)


def test__is_anticipation_error():
    assert not compile_data._is_anticipation_error('[667]')
    assert not compile_data._is_anticipation_error('[100]')
    assert compile_data._is_anticipation_error('[99]')
    assert compile_data._is_anticipation_error('[15]')
    assert not compile_data._is_anticipation_error('[-1]')


def test__add_anticipation_errors_to_df():
    pid = PID_SUCCESS
    df = _get_sart_experiment_block(pid, 2)
    df_anticip = compile_data._add_anticipation_errors(df)
    assert 'anticipate_error' in df_anticip
    anticipated = list(df_anticip.anticipate_error)
    assert anticipated.count(True) == 2


def test___calculate_go_errors():
    pid = PID_SUCCESS
    df = _get_sart_experiment_block(pid, 2)

    # check known values
    assert list(df.correct.values).count(False) == 4

    # add anticipation errors
    dfa = compile_data._add_anticipation_errors(df)

    # check known values
    assert list(dfa.anticipate_error.values).count(True) == 2
    # anticipation errors are added to error count
    assert list(dfa.correct.values).count(False) == 6

    go_errors = compile_data._calculate_go_errors(dfa, 'go')
    assert isinstance(go_errors, compile_data.pd.Series)
    assert list(go_errors).count(True) == 1
    nogo_errors = compile_data._calculate_go_errors(dfa, 'no_go')
    assert isinstance(nogo_errors, compile_data.pd.Series)
    assert list(nogo_errors).count(True) == 3


def test__calculate_nogo_error_rt_avgs_blk3():
    pid = PID_SUCCESS
    df = _get_sart_experiment_block(pid, 2)
    df = compile_data._add_anticipation_errors(df)
    df['nogo_error'] = compile_data._calculate_go_errors(df, 'no_go')
    assert list(df['nogo_error']).count(True) == 3

    adjacent_rts = compile_data._calculate_nogo_error_rt_avgs(df)
    assert adjacent_rts['prev4_avg'] == 371.0
    assert adjacent_rts['num_prev4_rts'] == 12
    assert adjacent_rts['next4_avg'] == 435.75
    assert adjacent_rts['num_next4_rts'] == 12


def test__calculate_nogo_error_rt_avgs_blk4():
    pid = PID_SUCCESS
    df = _get_sart_experiment_block(pid, 3)
    df = compile_data._add_anticipation_errors(df)
    df['nogo_error'] = compile_data._calculate_go_errors(df, 'no_go')
    assert list(df['nogo_error']).count(True) == 5

    adjacent_rts = compile_data._calculate_nogo_error_rt_avgs(df)
    assert adjacent_rts['prev4_avg'] == 318.833333333
    assert adjacent_rts['num_prev4_rts'] == 18
    assert adjacent_rts['next4_avg'] == 407.105263158
    assert adjacent_rts['num_next4_rts'] == 19


def test__get_correct_rts_blk1():
    pid = PID_SUCCESS
    sart_block = _get_sart_experiment_block(pid)
    df = compile_data._add_anticipation_errors(sart_block)
    rts = compile_data._get_correct_rts(df)
    assert len(rts) == 218
    assert round(compile_data.np.mean(rts), 2) == 364.58


def test__get_correct_rts_blk4():
    pid = PID_SUCCESS
    sart_block = _get_sart_experiment_block(pid, 3)
    df = compile_data._add_anticipation_errors(sart_block)
    rts = compile_data._get_correct_rts(df)
    assert len(rts) == 198
    assert round(compile_data.np.mean(rts), 2) == 351.56


def test_summarize_block_performance_blk4():
    pid = PID_SUCCESS
    sart_block = _get_sart_experiment_block(pid, 4)
    p = compile_data.summarize_block_performance(sart_block)
    assert p['num_trials'] == 225
    assert p['rt_avg'] == 404.205263158
    assert p['anticipated_num_errors'] == 25
    assert p['anticipated'] == 0.111111111
    assert p['go_num_errors'] == 6
    assert p['go_errors'] == 0.026666667
    assert p['nogo_num_errors'] == 0
    assert p['nogo_errors'] == 0.0
    assert p['accuracy'] == 0.862222222  # 194/225
    total_error_prop = (p['anticipated'] + p['go_errors'] + p['nogo_errors'])

    # average RTs before and after no-go errors
    assert p['nogo_prev4_avg'] == None  # no no-go errors
    assert p['nogo_next4_avg'] == None  # no no-go errors

    # ensure that calculations match up
    rnd = compile_data.ROUND_NDIGITS
    assert round(total_error_prop, rnd-1) == round(1 - p['accuracy'], rnd-1)


def test_summarize_sart_chunk():
    pid = PID_SUCCESS
    df = get_csv_as_df('experiment', pid)
    blocks = compile_data.extract_sart_blocks(df, with_survey=True)

    # fourth block
    b4 = blocks[3]
    b4s = compile_data.summarize_sart_chunk(b4)
    assert b4s['anticipated'] == 0.062222222
    assert b4s['accuracy'] == 0.88
    assert b4s['effort'] == 7
    assert b4s['discomfort'] == 7
    assert b4s['boredom'] == 6

    assert b4s['ratings_time_min'] == 19.616666667
    assert b4s['num_trials'] == 225

    assert b4s['nogo_prev4_avg'] == 318.833333333
    assert b4s['nogo_next4_avg'] == 407.105263158

    # last (fifth) block
    b5 = blocks[-1]
    b5s = compile_data.summarize_sart_chunk(b5)
    assert b5s['anticipated'] == 0.111111111
    assert b5s['accuracy'] == 0.862222222
    assert b5s['effort'] == 7
    assert b5s['discomfort'] == 7
    assert b5s['boredom'] == 6
    assert b5s['ratings_time_min'] == 24.183333333

    assert b5s['num_trials'] == 225

    assert b4s['nogo_prev4_avg'] == 318.833333333
    assert b4s['nogo_next4_avg'] == 407.105263158


def test__calculate_ratings_proportions():
    ratings = [5, 2, 3, 7, 6, 4, 3, 3]  # 8 ratings, 7 possible changes
    # ratings proportions
    rp = compile_data._calculate_ratings_proportions(ratings)
    assert rp['ups'] == 0.285714286  # 2 of 7
    assert rp['downs'] == 0.571428571  # 4 of 7
    assert rp['sames'] == 0.142857143  # 1 of 7


def test_complete_compile_experiment_data():
    pid = PID_SUCCESS
    df = get_csv_as_df('experiment', pid)
    ed = compile_data.compile_experiment_data(df)

    assert ed['num_trials'] == 1125
    assert ed['trials_per_block'] == 225
    assert ed['num_blocks'] == 5

    assert ed['forecasted_enjoyment'] == 4
    assert ed['forecasted_performance'] == 5
    assert ed['forecasted_effort'] == 4
    assert ed['forecasted_discomfort'] == 3
    assert ed['forecasted_fatigue'] == 5
    assert ed['forecasted_motivation'] == 6
    assert ed['antecedent_boredom'] == 3

    # check keys for each block's real-time data
    blk_summary_keys = [
        'anticipated', 'nogo_next4_avg', 'nogo_prev4_avg', 'go_errors',
        'effort', 'num_trials', 'discomfort', 'rt_avg', 'nogo_errors',
        'accuracy'
        ]
    for i in range(1, (ed['num_blocks'] + 1)):
        blk_key_prefix = "blk{}".format(i)
        blk_keys = [k for k in ed.keys() if k.startswith(blk_key_prefix)]
        assert len(blk_keys) == 16
        for k in blk_summary_keys:
            expected_blk_key = "{}_{}".format(blk_key_prefix, k)
            assert expected_blk_key in blk_keys

    # affective ratings
    assert ed['prop_effort_ups'] == 0.25  # 1/4
    assert ed['prop_effort_downs'] == 0.0  # 0/4
    assert ed['prop_effort_sames'] == 0.75  # 3/4

    assert ed['prop_discomfort_ups'] == 0.5  # 2/4
    assert ed['prop_discomfort_downs'] == 0.0  # 0/4
    assert ed['prop_discomfort_sames'] == 0.5  # 2/4

    assert ed['prop_boredom_ups'] == 0.5  # 2/4
    assert ed['prop_boredom_downs'] == 0.0  # 0/4
    assert ed['prop_boredom_sames'] == 0.5  # 2/4

    # go, no-go, and anticipated error variable weighted averages
    assert ed['nogo_num_errors'] == 18
    assert ed['nogo_error_prev_rt_avg'] == 352.12857142837146
    assert ed['nogo_error_next_rt_avg'] == 395.67605633805636

    # proportion of go, no-go, and anticipated errors across all trials
    # also proportion of trials that were completed accurately
    assert ed['avg_go_errors'] == 0.013333333
    assert ed['avg_nogo_errors'] == 0.016
    assert ed['avg_anticipation_errors'] == 0.036444444
    assert ed['avg_accuracy'] == 0.934222222

    # regression variables for blocks
    assert ed['accuracy_slope'] == -0.007162023
    assert ed['accuracy_intercept'] == 1.040912496
    assert ed['effort_slope'] == 0.04296334
    assert ed['effort_intercept'] == 6.15998945
    assert ed['discomfort_slope'] == 0.107323927
    assert ed['discomfort_intercept'] == 4.801231237
    assert ed['boredom_slope'] == 0.107323927
    assert ed['boredom_intercept'] == 3.801231237

    # peak-end calculations
    assert ed['start_effort'] == 6
    assert ed['peak_effort'] == 7
    assert ed['min_effort'] == 6
    assert ed['end_effort'] == 7
    assert ed['avg_effort'] == 6.8

    assert ed['start_discomfort'] == 5
    assert ed['peak_discomfort'] == 7
    assert ed['min_discomfort'] == 5
    assert ed['end_discomfort'] == 7
    assert ed['avg_discomfort'] == 6.4

    assert ed['start_boredom'] == 4
    assert ed['peak_boredom'] == 6
    assert ed['min_boredom'] == 4
    assert ed['end_boredom'] == 6
    assert ed['avg_boredom'] == 5.4

    assert ed['avg_blk_accuracy'] == 0.934222222
    assert ed['max_blk_accuracy'] == 0.982222222
    assert ed['min_blk_accuracy'] == 0.862222222
    assert ed['start_blk_accuracy'] == 0.982222222
    assert ed['end_blk_accuracy'] == 0.862222222

    assert ed['auc_accuracy'] == 3.748888888
    assert ed['auc_effort'] == 27.5
    assert ed['auc_discomfort'] == 26.0

    # post-experiment evaluation of valence and arousal
    assert ed['arousal_post_mind_body'] == '3'
    assert ed['arousal_post_feeling'] == '1'

    assert ed['time_experiment_ms'] == 1475020


def test_compile_demographics_data_after_practice_failure():
    pid = PID_FAIL
    df = get_csv_as_df('follow_up', pid)
    data = compile_data.compile_demographic_data(df)
    expected_answers = [
        ('age', '23'),
        ('dob', '05/1994'),
        ('sex', 'Female'),

        ('sms_1', '1'),
        ('sms_2', '4'),
        ('sms_3', '3'),
        ('sms_4', '4'),
        ('sms_5', '2'),
        ('sms_6', '2'),
        ('sms_7', '4'),
        ('sms_8', '4'),
        ('sms_9', '1'),
        ('sms_10', '4'),
        ('sms_11', '2'),
        ('sms_12', '2'),
        ('sms_13', '5'),
        ('sms_14', '2'),
        ('sms_15', '2'),
        ('sms_16', '4'),
        ('sms_17', '3'),
        ('sms_18', '3'),
        ('sms_19', '3'),
        ('sms_20', '4'),
        ('sms_21', '3'),

        ('state_boredom_1', '3'),
        ('state_boredom_2', '4'),
        ('state_boredom_3', '3'),
        ('state_boredom_4', '2'),
        ('state_boredom_5', '4'),
        ('state_boredom_6', '3'),
        ('state_boredom_7', '6'),
        ('state_boredom_8', '5'),

        ('time_delay_b4_retrospect_ms', None),
        ('time_follow_up_ms', 122441),
    ]
    for label, answer in expected_answers:
        print label
        assert data[label] == answer


def test_compile_demographics_data_after_practice_success():
    pid = PID_SUCCESS
    df = get_csv_as_df('follow_up', pid)
    data = compile_data.compile_demographic_data(df)
    print data
    expected_answers = [
        ('age', '28'),
        ('dob', '03/1989'),
        ('sex', 'Female'),

        ('sms_1', '3'),
        ('sms_2', '3'),
        ('sms_3', '1'),
        ('sms_4', '3'),
        ('sms_5', '3'),
        ('sms_6', '3'),
        ('sms_7', '1'),
        ('sms_8', '2'),
        ('sms_9', '5'),
        ('sms_10', '2'),
        ('sms_11', '3'),
        ('sms_12', '3'),
        ('sms_13', '3'),
        ('sms_14', '4'),
        ('sms_15', '3'),
        ('sms_16', '1'),
        ('sms_17', '3'),
        ('sms_18', '1'),
        ('sms_19', '3'),
        ('sms_20', '3'),
        ('sms_21', '4'),

        ('state_boredom_1', '2'),
        ('state_boredom_2', '5'),
        ('state_boredom_3', '3'),
        ('state_boredom_4', '2'),
        ('state_boredom_5', '2'),
        ('state_boredom_6', '5'),
        ('state_boredom_7', '6'),
        ('state_boredom_8', '6'),

        ('time_delay_b4_retrospect_ms', 191192),
        ('time_follow_up_ms', 252719),
    ]
    for label, answer in expected_answers:
        assert data[label] == answer


def test_compile_retrospective_data_after_practice_success():
    pid = PID_SUCCESS
    df = get_csv_as_df('follow_up', pid)
    data = compile_data.compile_retrospective_data(df)
    print data
    expected_answers = [
        ('tlx_scale_1', '7'),
        ('tlx_scale_2', '2'),
        ('tlx_scale_3', '4'),
        ('tlx_scale_4', '6'),
        ('tlx_scale_5', '7'),
        ('tlx_scale_6', '6'),
        ('tlx_scale_7', '6'),
        ('tlx_scale_8', '5'),
        ('tlx_scale_9', '7'),
        ('tlx_scale_10', '2'),
        ('tlx_scale_11', '2'),
        ('tlx_scale_12', '6'),
        ('tlx_scale_13', '2'),
    ]
    for label, answer in expected_answers:
        assert data[label] == answer
