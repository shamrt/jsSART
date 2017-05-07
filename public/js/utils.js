/**
 * Common utility values and functions for jsSART
 */

// Reuseable stimuli
// ------------------------

// HTML for text plugin
var spacebar_html = "<code>&lt;SPACEBAR&gt;</code>";
var continue_html = "<p>Press the " + spacebar_html + " to continue.</p>";

// fixation stimulus
var fixation_cross_path = "../img/fixation-cross.png";
var fixation_trial = {
  type: 'single-stim',
  stimulus: [fixation_cross_path],
  timing_stim: jsSART.STIMULI.DISPLAY_TIMINGS[1],
  timing_response: jsSART.STIMULI.DISPLAY_TIMINGS[1],
  timing_post_trial: 0
};


// Functions
// ------------------------

// sum a list of values
function sum(list) {
  return _.reduce(list, function(memo, num){ return memo + num; });
}

// convert milliseconds to minutes, rounding up
function millisecondsToMinutes(ms) {
  return Math.ceil(ms / 1000 / 60);
}

// get url parameters
function getUrlParams() {
  var url_params = window.location.search.slice(1);
  return $.deparam(url_params);
}

// try to get a participant ID
function getParticipantId() {
  var pid;

  // first attempt to get PID via URL params
  params = getUrlParams();
  pid = params.pid;

  // if PID was in URL params, initialize page reload alert
  if (pid) {
    $(window).bind('beforeunload', function(){
      return 'If you leave this page, your progress will be lost. Are you sure you want to leave?';
    });
  }

  // next, get PID via window prompt
  pid = pid || window.prompt("Please enter a participant ID.");

  // as a last resort, generate a jsPsych random ID
  pid = pid || jsPsych.randomization.randomID();

  return pid;
}


// create a 'text' plugin block with some defaults
function createTextBlock(text_html) {
  return {
    type: "text",
    text: text_html + continue_html,
    cont_key: [32, 13]
  };
}


// calculate approximate length of time to complete SART experiment blocks
// returns a string
function approxExperimentDuration(num_trials) {
  var trial_duration_ms = sum(jsSART.STIMULI.DISPLAY_TIMINGS);
  var min_duration_ms = trial_duration_ms * num_trials;
  var max_duration_ms = trial_duration_ms * num_trials * 1.3;
  var min_duration_in_min = millisecondsToMinutes(min_duration_ms);
  var max_duration_in_min = millisecondsToMinutes(max_duration_ms);
  return min_duration_in_min + "-" + max_duration_in_min + " minutes";
}


// calculate the minimum number of errors a participant can make in
// practice block 2
function getPracticeMinCorrect(num_items, max_error_rate) {
  return Math.floor(num_items * (1 - max_error_rate));
}


// add results data to the last trial
function addTrialResults(trial_data, extra_data) {
  extra_data = extra_data || {};
  var expected, response, correct;

  var trial_stimuli = JSON.parse(trial_data.stimulus);
  var $stimulus = $(trial_stimuli[0]);
  var stimulus_font_size = $stimulus.css('font-size');
  var stimulus_text = $stimulus.text();
  var stimulus = parseInt(stimulus_text);

  // expected (correct) response for the last trial
  if (stimulus === jsSART.STIMULI.NO_GO_VALUE) {
    expected = false;
  } else {
    expected = true;
  }

  // check whether an expected key was pressed
  var key_press = JSON.parse(trial_data.key_press);
  response = _.contains(jsSART.STIMULI.ALLOW_KEYCODES, key_press[0]);

  // was the response given as expected (correct)?
  correct = (expected === response) ? true : false;

  var trial_results = $.extend({
    expected: expected,
    response: response,
    correct: correct,
    font_size: stimulus_font_size,
    stimulus: stimulus
  }, extra_data);  // merge with given data

  return trial_results;
}


// display trial feedback, based on response judgement
function displayTrialFeedback(data) {
  if (typeof data.correct !== "undefined") {
    var feedback_text = data.correct ? "Correct!" : "Incorrect";
    var feedback_class = data.correct ? "correct" : "incorrect";
    var feedback_html = '<h3 class="'+feedback_class+'">'+feedback_text+'</h3>';

    // show feedback
    $('#jspsych-feedback').html(feedback_html);
    // hide feedback
    window.setTimeout(function() {
      $('#jspsych-feedback').empty();
    }, jsSART.PRACTICE.FEEDBACK_DELAY_MS);
  }
}


// create a formatted list of trial stimuli for a block
function formatBlockStimuli(trials, font_sizes) {
  // make smallest font size by default
  font_sizes = (typeof font_sizes !== "undefined") ?
    font_sizes : jsSART.STIMULI.FONT_SIZES;

  var block_stimuli = [];
  for (var i = 0; i < trials.length; i++) {
    // create formatted stimulus with randomly sampled font size
    var trial_stimuli = {
      stimuli: [
        "<div style='font-size:" + _.sample(font_sizes) + "'>" +
        trials[i] +
        "</div>",
        "<img src='" + fixation_cross_path + "' style='width:29mm;height:29mm'/>"
      ]
    };
    block_stimuli.push(trial_stimuli);
  }
  return block_stimuli;
}


// create a block of trials
function createSartBlock(stimuli, options) {
  options = options || {};
  var give_feedback = options.give_feedback || false;
  var extra_data = options.extra_data || {};

  var block = {
    type: "multi-stim-multi-response",

    timeline: formatBlockStimuli(stimuli),
    is_html: true,
    choices: [jsSART.STIMULI.ALLOW_KEYCODES],

    timing_stim: jsSART.STIMULI.DISPLAY_TIMINGS,
    timing_response: sum(jsSART.STIMULI.DISPLAY_TIMINGS),
    timing_post_trial: 0,
    response_ends_trial: false,

    on_finish: function() {
      // add results to trial data
      var trial_data = jsPsych.data.getLastTrialData();
      var added_data = addTrialResults(trial_data, extra_data);
      jsPsych.data.addDataToLastTrial(added_data);

      if (give_feedback) {
        displayTrialFeedback(added_data);
      }
    }
  };
  if (give_feedback) {
    // add post-trial time for feedback display
    block.timing_post_trial = jsSART.PRACTICE.FEEDBACK_DELAY_MS;
  }

  return block;
}


// generate a multiple choice survey trials object
function generateMultiChoiceSurvey(questions, randomize_order) {
  // by default, do not randomize order
  randomize_order = (typeof randomize_order !== "undefined") ?
      randomize_order : false;

  return {
      type: 'survey-multi-choice',
      timeline: _.map(questions, function(q) {
        return {
          questions: [q.question],
          options: [jsSART.LIKERT[q.likert_scale]],
          required: [true]
        };
      }),
      randomize_order: randomize_order,
      horizontal: true
  };
}


// generate a complete experiment chunk, complete with survey
function generateExperimentChunk(stimuli) {
  var notice = createTextBlock("When you're ready to continue, a trial block will begin.");
  var sart_block = createSartBlock(stimuli);
  var survey = generateMultiChoiceSurvey(jsSART.QUESTIONS.REAL_TIME);

  var chunk = {
    chunk_type: 'linear',
    timeline: [notice, fixation_trial, sart_block, survey]
  };
  return chunk;
}


// generate random conditions
function generateConditions() {
  var conditions = {
    num_trials: _.sample(jsSART.CONDITIONS.NUM_TRIALS),
    trials_per_block: _.sample(jsSART.CONDITIONS.TRIALS_PER_BLOCK)
  };
  return conditions;
}


// generate a formatted and complete set of jsPsych blocks
// NOTE: return an object with block stimuli lists and formatted stimuli
function generateSartBlockStimuli(conditions) {
  // generate all random stimuli for the experiment
  var all_stimuli = generateStimuli(conditions.num_trials);

  // generate all experiment block objects
  var trials_per_block = conditions.trials_per_block;
  var stimuli_blocks = divideStimuliIntoBlocks(all_stimuli, trials_per_block);
  var formatted_stimuli = _.map(stimuli_blocks, function(stimuli) {
    return generateExperimentChunk(stimuli);
  });

  return formatted_stimuli;
}


// generate n-length array of no-go items
function generateNoGoItems(n) {
  return Array.apply(null, Array(n))
    .map(function() { return jsSART.STIMULI.NO_GO_VALUE; })
}


// generate n-length array of go (non-no-go) items
function generateGoItems(n) {
  var go_items = [];

  while (go_items.length < n) {
    var stimulus = _.sample(jsSART.STIMULI.VALUES);
    if (stimulus === jsSART.STIMULI.NO_GO_VALUE) continue;
    go_items.push(stimulus);
  }

  return go_items;
}


// generate quasi-random stimuli for SART blocks
// return list of trial values
function generateStimuli(num_trials, _num_no_gos) {
  var num_no_gos = _num_no_gos || jsSART.STIMULI.NO_GOS_PER_BLOCK;

  var no_go_val = jsSART.STIMULI.NO_GO_VALUE;

  var goStimuli = generateGoItems((num_trials - num_no_gos));
  var noGoStimuli = generateNoGoItems(num_no_gos);
  var unshuffledStimuli = goStimuli.concat(noGoStimuli);
  var stimuliIndexes = _.range(num_trials);
  var stimuli = Array.apply(null, Array(num_trials)).map(function() { return 0; });  // an array of `num_trials` 0s

  while (stimuliIndexes.length) {
    var random_index = _.sample(stimuliIndexes);
    var trial = unshuffledStimuli.pop();

    // add trial to stimuli if not a no-go value...
    if (trial !== no_go_val ||
        // ...or if the surrounding trials are not no-go values
        (stimuli[random_index + 1] !== no_go_val && stimuli[random_index - 1] !== no_go_val)
        ) {
      // replace zeroed stimulus
      stimuli[random_index] = trial;
      // remove index
      stimuliIndexes.splice(stimuliIndexes.indexOf(random_index), 1);
    } else {
      // put trial value back
      unshuffledStimuli.push(trial);
    }

  }

  return stimuli;
}


// divide all experiment stimuli into specified block lengths
// return list of lists
function divideStimuliIntoBlocks(stimuli, trials_per_block) {
  var blocks = [];

  while (stimuli.length) {
    // create blocks
    var block = [];
    for (var i=0; i < trials_per_block; i++) {
      var stimulus = stimuli.shift();
      block.push(stimulus);

      if (!stimuli.length) {
        // stop looping when run out of stimuli
        // NOTE: for last block
        break;
      }
    }
    blocks.push(block);
  }
  return blocks;
}


// generate random practice condition
function generatePracticeCondition() {
  return _.sample(jsSART.CONDITIONS.PRACTICE);
}


// generate practice trials from a random condition
function generatePracticeTrials(condition) {
  var trials;
  switch (condition) {
    case 'num_trials':
      // NOTE: Pre-set practice block trials for mirrored number of trials
      // condition
      trials = {
        'BLOCK_1_STIMULI': _.shuffle([9, 1, 3, 5, 6]),
        'BLOCK_2_STIMULI': _.shuffle(
          [4, 5, 7, 2, 8, 4, 5, 9, 3, 6, 9, 2, 7, 3, 8]
        )
      };
      break;
    default:
      trials = {
        'BLOCK_1_STIMULI': generateStimuli(29),
        'BLOCK_2_STIMULI': generateStimuli(72)
      };
  }
  return trials;
}


// generate a multi-choice timeline object based on a set of item strings
// @param {array} questions - Array of item/question strings
// @param {array} likert_scale - Array of Likert scale anchors
function createTimelineSet(questions, likert_scale) {
return questions.map(function(question) {
  return {
    questions: [question],
    options: [likert_scale],
  };
});
}


// post data to the server using an AJAX call
function postDataToDb(data, filename, redirect) {
  // remove page reload alert binding
  $(window).unbind('beforeunload');

  // save data
  var pathname = window.location.pathname.slice(1);
  $.ajax({
    type: "POST",
    url: "/experiment-data",
    data: JSON.stringify({filename: filename, pathname: pathname, data: data}),
    contentType: "application/json"
  })
  .done(function() {
    if (typeof redirect === "string") {
      window.location.href = redirect;
    }
  })
  .fail(function() {
    alert("A problem occurred while writing to the database. We cannot continue. Please contact the researcher for more information.");
  });
}
