QUnit.test("millisecondsToMinutes", function(assert) {
  // 1 second rounds to one minute
  assert.equal(millisecondsToMinutes(1000), 1);
  // 65 seconds rounds to 2 minutes
  assert.equal(millisecondsToMinutes(65000), 2);
  // 600 seconds rounds to 10 minutes
  assert.equal(millisecondsToMinutes(600000), 10);
});

QUnit.test("approxExperimentDuration", function(assert) {
  // 40 trials
  assert.equal(approxExperimentDuration(50), "1-2 minutes");
  // 150 trials
  assert.equal(approxExperimentDuration(150), "3-4 minutes");
  // 800 trials
  assert.equal(approxExperimentDuration(800), "16-20 minutes");
});


QUnit.test("getParticipantId", function(assert) {
  // NOTE: does not test for getting PID via window prompt
  var pid = getParticipantId();

  var url_params = getUrlParams();
  if (_.contains(_.keys(url_params), "pid")) {
    // just get the PID from URL
    expected_pid = url_params.pid;
    assert.ok(pid === expected_pid);
  } else {
    // should be an 32-char alphanumeric string
    var re = new RegEx('[a-z0-9]{32}');
    assert.ok(re.match(pid));
  }
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
        "<img src='../img/fixation-cross.png' style='width:29mm;height:29mm'/>"
      ]
    },
    {
      "stimuli": [
        "<div style='font-size:100px'>4</div>",
        "<img src='../img/fixation-cross.png' style='width:29mm;height:29mm'/>"
      ]
    },
    {
      "stimuli": [
        "<div style='font-size:100px'>9</div>",
        "<img src='../img/fixation-cross.png' style='width:29mm;height:29mm'/>"
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
        "<img src='../img/fixation-cross.png' style='width:29mm;height:29mm'/>"
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

      timing_stim: jsSART.STIMULI.DISPLAY_TIMING,
      timing_response: sum(jsSART.STIMULI.DISPLAY_TIMING),
      response_ends_trial: false,
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
  var block_stimuli = [9, 1, 3, 5, 2, 6];
  return {
    block_stimuli: block_stimuli,
    internal_node_id: "0.0-2.0-4.0",
    key_press: "[" + key_press + "]",
    participant_id: "123456",
    rt: "350",
    stimulus: "[" +
      "\"<div style='font-size:120px'>" +
        block_stimuli[trial_index - 1] +
      "</div>\",\"<img src='../img/fixation-cross.png'/>\"" +
    "]",
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
    response: true,
    stimulus: 6
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
    response: false,
    stimulus: 3
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
    response: false,
    stimulus: 9
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
    response: true,
    stimulus: 3
  };
  assert.deepEqual(trial_results, expected);
});


QUnit.test("generatePracticeCondition", function(assert) {
  var condition = generatePracticeCondition();
  assert.ok(_.contains(jsSART.CONDITIONS.PRACTICE, condition));
});


QUnit.test("generatePracticeTrials, with num_trials condition", function(assert) {
  function numberOfThreesInList(list) {
    var counts = _.countBy(list, function(num) { return num === 3; });
    return counts["true"];
  }

  var trials = generatePracticeTrials('num_trials');

  assert.ok(trials.BLOCK_1_STIMULI.length === 5);
  assert.equal(numberOfThreesInList(trials.BLOCK_1_STIMULI), 1);

  assert.ok(trials.BLOCK_2_STIMULI.length === 15);
  assert.equal(numberOfThreesInList(trials.BLOCK_2_STIMULI), 2);
});


QUnit.test("generatePracticeTrials, with time_duration condition", function(assert) {
  var trials = generatePracticeTrials('time_duration');
  assert.ok(trials.BLOCK_1_STIMULI.length === 29);
  assert.ok(trials.BLOCK_2_STIMULI.length === 72);
});


QUnit.test("getPracticeMinCorrect", function(assert) {
  var min_correct = getPracticeMinCorrect(15, 0.10);
  assert.equal(min_correct, 13);

  var min_correct = getPracticeMinCorrect(72, 0.15);
  assert.equal(min_correct, 61);
});
