/**
 * Common utility values and functions for jsSART
 */

// Reuseable stimuli
// ------------------------

// HTML for text plugin
var spacebar_html = "<code>&lt;SPACEBAR&gt;</code>";
var continue_html = "<p>Press the " + spacebar_html + " to continue.</p>";

// fixation stimulus
var fixation_cross_path = "../img/fixation_cross.png";
var fixation_trial = {
  type: 'single-stim',
  stimuli: [],
  timing_response: jsSART.TIMING_STIM_DISPLAY,
  timing_post_trial: jsSART.TIMING_POST_STIM
};


// Functions
// ------------------------

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
function addTrialResults(added_data) {
  added_data = added_data || {};
  var expected, response, correct;
  var current_trial = jsPsych.data.getLastTrialData();
  var current_index = current_trial.trial_index - 1;

  // nothing expected on first trial
  if (current_index !== 0) {
    var current_value = current_trial.block_stimuli[current_index];
    var previous_value = current_trial.block_stimuli[current_index - 1];

    // expected (correct) response for the last trial
    expected = current_value + previous_value;

    // response given in the last trial
    var key_presses = JSON.parse(current_trial.key_press);
    var digit_presses = [];
    for (var i = 0; i < key_presses.length; i++) {
      var key_press = key_presses[i];
      if (key_press !== -1) {
        // normalize keycode from numpad to numrow
        if (key_press >= 96 && key_press <= 105) {
          key_press = key_press - 48;
        }

        var digit = String.fromCharCode(key_press);
        digit_presses.push(digit);
      }
    }
    response = parseInt(digit_presses.join(''));

    // was the response given as expected (correct)?
    correct = (expected === response) ? true : false;
  }

  var trial_results = $.extend({
    expected: expected,
    response: response,
    correct: correct
  }, added_data);  // merge with given data

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
    }, 800);
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
        "<div style='font-size:" + _.sample(font_sizes_px) + "'>" + trials[i] + "</div>"
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
  var added_data = options.added_data || {};

  var digit_keycodes = (_.range(48, 58)).concat(_.range(96, 106));
  var block = {
    type: "multi-stim-multi-response",

    timeline: formatBlockStimuli(stimuli),
    is_html: true,
    choices: [digit_keycodes, digit_keycodes],

    timing_stim: [jsSART.TIMING_STIM_DISPLAY],
    timing_response: jsSART.TIMING_POST_STIM,
    response_ends_trial: false,

    data: {block_stimuli: stimuli},
    on_finish: function() {
      jsPsych.data.addDataToLastTrial(addTrialResults(added_data));
      if (give_feedback) {
        var trial_data = jsPsych.data.getLastTrialData();
        displayTrialFeedback(trial_data);
      }
    }
  };
  if (give_feedback) {
    // add post-trial time for feedback display
    block.timing_post_trial = 1000;
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


// generate random condition
function generateCondition() {
  return _.random(1, jsSART.BLOCKS_PER_CONDITION.length);
}


// generate a set of randomized block difficulty types
// return list of block difficulty and block stimuli
function generateRandomBlockTypes(condition, outer_block_type) {
  outer_block_type = (typeof outer_block_type === "undefined") ? 'medium' : outer_block_type;
  var blocks_in_condition = jsSART.BLOCKS_PER_CONDITION[condition - 1];

  // calculate number of middle medium blocks
  // Note: is equal to number of blocks in a given condition, minus 2 'medium'
  // blocks at beginning and end of the list, minus 1 'easy' and 1 'hard' block
  var num_middle_medium_blocks = blocks_in_condition - 2 - 2;

  // add unshuffled middle 'medium', 'easy' and 'hard' blocks
  var unshuffled_middle_blocks = Array.apply(
    null, Array(num_middle_medium_blocks)).map(function() { return 'medium'; });
  unshuffled_middle_blocks.push('easy', 'hard');

  // randomize blocks
  random_middle_blocks = _.shuffle(unshuffled_middle_blocks);

  // complete block difficulty order generation
  var block_types = [outer_block_type];
  block_types = block_types.concat(random_middle_blocks);
  block_types = block_types.concat([outer_block_type]);

  return block_types;
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
