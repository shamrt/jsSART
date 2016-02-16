QUnit.test("getParticipantId", function(assert) {
  var url_params = getUrlParams();
  var expected_pid = 9999910000;
  if (_.contains(_.keys(url_params), "pid")) {
    expected_pid = url_params.pid;
  }
  assert.ok(getParticipantId() >= expected_pid);
});


QUnit.test("createTextBlock", function(assert) {
  var arg = "<p>Foo bar</p>";
  var expected = {
    "type": "text",
    "text": arg + continue_html,
    "cont_key": [32, 13]
  };
  assert.deepEqual(createTextBlock(arg), expected);
});


QUnit.test("formatBlockStimuli, several with font size given", function(assert) {
  var font_sizes = ["100px"];
  var trials = [3, 4, 9];
  var expected = [
    {
      "stimuli": [
        "<div style='font-size:100px'>3</div>",
        "<img src='../img/fixation-cross.png'/>"
      ]
    },
    {
      "stimuli": [
        "<div style='font-size:100px'>4</div>",
        "<img src='../img/fixation-cross.png'/>"
      ]
    },
    {
      "stimuli": [
        "<div style='font-size:100px'>9</div>",
        "<img src='../img/fixation-cross.png'/>"
      ]
    }
  ];

  assert.deepEqual(formatBlockStimuli(trials, font_sizes), expected);
});


// check that randomly formatted block matches set of possible objects
function checkSingleFormattedBlockStimulus(trial, font_sizes) {
  var block_stimuli = formatBlockStimuli(trial);

  var has_expected_block = false;
  for (var i=0; i < font_sizes.length; i++) {
    var possible_expected = [{
      "stimuli": [
        "<div style='font-size:" + font_sizes[i] + "'>2</div>",
        "<img src='../img/fixation-cross.png'/>"
      ]
    }];

    if (_.isEqual(possible_expected, block_stimuli)) {
      has_expected_block = true;
      break;
    }
  }

  return has_expected_block;
}

QUnit.test("formatBlockStimuli, single stimulus without font sizes given", function(assert) {
  var trial = [2];
  var font_sizes = jsSART.STIMULI.FONT_SIZES;
  var has_expected_block = checkSingleFormattedBlockStimulus(
      trial, font_sizes);
  assert.ok(has_expected_block);
});

QUnit.test("formatBlockStimuli, single stimulus with incorrect possible font sizes given", function(assert) {
  var trial = [2];
  var font_sizes = ["foo", "bar", "baz"];
  var has_expected_block = checkSingleFormattedBlockStimulus(
      trial, font_sizes);
  assert.notOk(has_expected_block);
});


QUnit.test("generateStimuli length", function(assert) {
  var num_stimuli = 25;
  var stimuli = generateStimuli(num_stimuli);
  assert.deepEqual(stimuli.length, num_stimuli);
});

QUnit.test("generateStimuli stimuli values", function(assert) {
  // check that all stimuli are expected possible value set
  var num_stimuli = 25;
  var stimuli = generateStimuli(num_stimuli);
  for (var i=0; i < stimuli.length; i++) {
    var is_expected_value = _.contains(jsSART.STIMULI.VALUES, stimuli[i]);
    assert.ok(is_expected_value);
  }
});


QUnit.test("generateConditions", function(assert) {
  var conditions = generateConditions();
  assert.ok(_.contains(jsSART.CONDITIONS.NUM_TRIALS, conditions.num_trials));
  assert.ok(_.contains(
    jsSART.CONDITIONS.TRIALS_PER_BLOCK, conditions.trials_per_block
  ));
});


QUnit.test("divideStimuliIntoBlocks with 10 stimuli and 2 trials per block", function(assert) {
  // there should be five blocks
  assert.expect(5);

  var stimuli = [8, 3, 7, 5, 6, 3, 1, 5, 1, 4];
  var trials_per_block = 2;
  var blocks = divideStimuliIntoBlocks(stimuli, trials_per_block);

  // check that blocks match
  var expected_blocks = [[8, 3], [7, 5], [6, 3], [1, 5], [1, 4]];
  for (var i=0; i < expected_blocks.length; i++) {
    assert.deepEqual(expected_blocks[i], blocks[i]);
  }
});


QUnit.test("divideStimuliIntoBlocks with 12 stimuli and 5 trials per block", function(assert) {
  // expect three blocks
  assert.expect(3);

  var stimuli = [9, 4, 7, 7, 3, 5, 6, 2, 5, 4, 3, 2];
  var trials_per_block = 5;
  var blocks = divideStimuliIntoBlocks(stimuli, trials_per_block);

  // check that blocks match
  // NOTE: last block should be shortened
  var expected_blocks = [[9, 4, 7, 7, 3], [5, 6, 2, 5, 4], [3, 2]];
  for (var i=0; i < expected_blocks.length; i++) {
    assert.deepEqual(expected_blocks[i], blocks[i]);
  }
});


QUnit.test("createSartBlock with 1 stimulus", function(assert) {
  var stimulus = [9];
  var sart_block = createSartBlock([9]);
  var font_sizes = jsSART.STIMULI.FONT_SIZES;

  var check_block_obj_equality = function(obj1, obj2) {
    var obj_equality = {};
    _.map(_.keys(obj1), function(k){
      obj_equality[k] = _.isEqual(obj1[k], obj2[k]);
    });
    return obj_equality;
  };

  var has_expected_block = false;
  for (var i=0; i < font_sizes.length; i++) {
    var possible_expected = {
      type: "multi-stim-multi-response",

      timeline: formatBlockStimuli(stimulus, [font_sizes[i]]),
      is_html: true,
      choices: [jsSART.STIMULI.ALLOW_KEYCODES],

      timing_stim: jsSART.TIMING_STIM_DISPLAY,
      timing_response: sum(jsSART.TIMING_STIM_DISPLAY),
      response_ends_trial: false,

      data: {block_stimuli: stimulus}
    };

    var block_objs_are_equal = check_block_obj_equality(
      possible_expected, sart_block
    );

    if (_.all(block_objs_are_equal)) {
      has_expected_block = true;
      break;
    }
  }

  assert.ok(has_expected_block);
});


// mock trial data generator (of block with 6 trials)
// NOTE: no-go trial is 3rd in index
function generateMockTrialData(key_press, trial_index) {
  return {
    block_stimuli: [9, 1, 3, 5, 2, 6],
    internal_node_id: "0.0-2.0-4.0",
    key_press: [key_press],
    participant_id: "123456",
    rt: "350",
    stimulus: [
      "<div style='font-size:120px'>2</div>",
      "<img src='../img/fixation-cross.png'/>"
    ],
    time_elapsed: 9596,
    trial_index: trial_index,
    trial_type: "multi-stim-multi-response",
  };
}

QUnit.test("addTrialResults, correct response on go trial", function(assert) {
  // should expect response on 6th trial
  var mock_trial_data = generateMockTrialData(32, 6);
  var trial_results = addTrialResults(mock_trial_data);
  var expected = {
    correct: true,
    expected: true,
    response: true
  };
  assert.deepEqual(trial_results, expected);
});

QUnit.test("addTrialResults, correct response on no-go trial", function(assert) {
  // should NOT expect response on 3rd trial
  var mock_trial_data = generateMockTrialData(-1, 3);
  var trial_results = addTrialResults(mock_trial_data);
  var expected = {
    correct: true,
    expected: false,
    response: false
  };
  assert.deepEqual(trial_results, expected);
});

QUnit.test("addTrialResults, incorrect response on go trial", function(assert) {
  // should expect response on 1st trial
  var mock_trial_data = generateMockTrialData(-1, 1);
  var trial_results = addTrialResults(mock_trial_data);
  var expected = {
    correct: false,
    expected: true,
    response: false
  };
  assert.deepEqual(trial_results, expected);
});

QUnit.test("addTrialResults, incorrect response on no-go trial", function(assert) {
  // should expect response on 1st trial
  var mock_trial_data = generateMockTrialData(32, 3);
  var trial_results = addTrialResults(mock_trial_data);
  var expected = {
    correct: false,
    expected: false,
    response: true
  };
  assert.deepEqual(trial_results, expected);
});
