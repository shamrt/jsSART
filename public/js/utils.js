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
  timing_stim: jsSART.TIMING_STIM_DISPLAY[1],
  timing_response: jsSART.TIMING_STIM_DISPLAY[1],
  timing_post_trial: 0
};


// Functions
// ------------------------

// sum a list of values
function sum(list) {
  return _.reduce(list, function(memo, num){ return memo + num; });
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

  // next, get PID via window prompt
  pid = pid || window.prompt("Please enter a participant ID.");

  // as a last resort, use 99999 with 5-digit random integer appended
  pid = pid || "99999" + _.random(10000, 99999);

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


// add results data to the last trial
function addTrialResults(trial_data, extra_data) {
  extra_data = extra_data || {};
  var expected, response, correct;

  var trial_stimulus = JSON.parse(trial_data.stimulus);
  var stimulus_text = $(trial_stimulus[0]).text();
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
    correct: correct
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
    }, 350);
  }
}


// create a formatted list of trial stimuli for a block
function formatBlockStimuli(trials, font_sizes_px) {
  // make smallest font size by default
  font_sizes_px = (typeof font_sizes_px !== "undefined") ?
    font_sizes_px : jsSART.STIMULI.FONT_SIZES;

  var block_stimuli = [];
  for (var i = 0; i < trials.length; i++) {
    // create formatted stimulus with randomly sampled font size
    var trial_stimuli = {
      stimuli: [
        "<div style='font-size:" + _.sample(font_sizes_px) + "'>" +
        trials[i] +
        "</div>",
        "<img src='" + fixation_cross_path + "'/>"
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

    timing_stim: jsSART.TIMING_STIM_DISPLAY,
    timing_response: sum(jsSART.TIMING_STIM_DISPLAY),
    timing_post_trial: 0,
    response_ends_trial: false,

    data: {block_stimuli: stimuli},
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
    block.timing_post_trial = 350;
  }

  return block;
}


// generate a complete experiment chunk, complete with survey
function generateExperimentChunk(stimuli, options) {
  var notice = createTextBlock("When you're ready to continue, a trial block will begin.");

  var block = createSartBlock(stimuli, options),
      survey_questions = jsSART.POST_BLOCK_QUESTIONS,
      // make all questions required
      required = _.map(survey_questions, function(){ return true; });

  var survey = {
      type: 'survey-multi-choice',
      questions: [survey_questions],
      options: [[jsSART.LIKERT_SCALE_1, jsSART.LIKERT_SCALE_1]],
      required: [required],
      horizontal: true
  };

  var chunk = {
    chunk_type: 'linear',
    timeline: [notice, fixation_trial, block, survey]
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
// Note: return an object with block stimuli lists and formatted stimuli
function generateSartBlockStimuli(block_types) {
  // get random stimuli for each block
  var block_stimuli = _.map(block_types, function(difficulty) {
    return generateStimuli(difficulty);
  });

  // generate jsPsych block objects
  var stimuli_types = _.zip(block_stimuli, block_types);
  var formatted_stimuli = _.map(stimuli_types, function(stimuli_type) {
    var added_data = {block_type: stimuli_type[1]};

    return generateExperimentChunk(stimuli_type[0], {
      added_data: added_data
    });
  });

  return {
    block_stimuli: block_stimuli,
    formatted_stimuli: formatted_stimuli
  };
}


// generate quasi-random stimuli for SART blocks
// return list of trial values
function generateStimuli(num_trials) {
  var stimuli = [];
  var quasi_random_counter = -1;
  var last_trial;

  while (stimuli.length < num_trials) {
    // prohibit 3s unless quasi-random counter equals zero
    if (last_trial === 3 && quasi_random_counter < 0) {
      // select a random countdown number from list
      quasi_random_counter = _.sample(jsSART.STIMULI.QUASI_RANDOM_RANGE);
    }

    // select random stimuli
    var trial = _.sample(jsSART.STIMULI.VALUES);

    // add trial to stimuli if allowable
    if (quasi_random_counter < 0 ||
        (quasi_random_counter >= 0 && trial !== 3)) {
      stimuli.push(trial);
      last_trial = trial;
      if (quasi_random_counter > -1) quasi_random_counter--;
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


// post data to the server using an AJAX call
function postDataToDb(data, filename, redirect) {
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
