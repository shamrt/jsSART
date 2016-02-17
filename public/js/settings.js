/**
 * Settings configuration for jsSART
 */

var jsSART = {

  // Conditions
  // --------------------------------
  'CONDITIONS': {
    // Total number of trials a participant will see during experiment
    'NUM_TRIALS': [484, 560, 646, 731, 810],
    // Number of trials before being shown real-time post-block questions
    'TRIALS_PER_BLOCK': [225, 82],
    // Practice blocks conditions
    'PRACTICE': ['num_trials', 'time_duration']
  },

  // Stimuli
  // --------------------------------
  'STIMULI': {
    // Possible stimuli values
    'VALUES': _.range(1, 10),  // 1--9
    // No-go value
    'NO_GO_VALUE': 3,
    // Font sizes
    'FONT_SIZES': ["12mm", "17.4mm", "22.717mm", "24.17mm", "29mm"],
    // Second level quasi-random counter range
    'QUASI_RANDOM_RANGE': _.range(4),  // 0-3
    // Allow keys 1--9 and numpad 1--9
    'ALLOW_KEYCODES': [32, 13]
    // Pace of PASAT trial presentation
    // NOTE: first number for stimlus (in milliseconds), second for fixation
    'DISPLAY_TIMING': [250, 900],
  },

  // Practice block stimuli
  // --------------------------------
  'PRACTICE': {
    // Duration of time to show trial feedback for block 1
    'FEEDBACK_DELAY_MS': 350,
    // Maximum proportion of trials a participant can get wrong in block 2
    'MAX_ERROR_RATE': 0.10,
    // Maximum number of times a participant can attempt block 2
    // (before skipping experiment)
    'MAX_ATTEMPTS': 3
  },

  // Experiment blocks
  // --------------------------------
  // Can be a flat array of strings
  'POST_BLOCK_QUESTIONS': [
    "Rate your current level of <strong>mental effort</strong>.",
    "Rate your current level of <strong>discomfort or distress</strong>."
  ],

  // Re-useable Likert scale labels
  // --------------------------------
  'LIKERT_SCALE_1': ["1<br>None", "2", "3", "4", "5", "6", "7<br>A Lot"],
  'LIKERT_SCALE_2': [
    "1<br>Significantly<br>Below Average",
    "2",
    "3",
    "4<br>Average",
    "5",
    "6",
    "7<br>Significantly<br>Above Average"
  ],

};
