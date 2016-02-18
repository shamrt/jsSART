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
    'ALLOW_KEYCODES': [32, 13],
    // Pace of PASAT trial presentation
    // NOTE: first number for stimlus (in milliseconds), second for fixation
    'DISPLAY_TIMING': [250, 900]
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

  // Evaluation questions
  // --------------------------------
  'QUESTIONS': {
    // Baseline evaluation of valence and arousal
    'BASELINE': [
      {
        question: "Right now, I am feeling:",
        likert_scale: 'SCALE_3'
      },
      {
        question: "Right now, my mind and body are:",
        likert_scale: "SCALE_4"
      },
    ],
    'REAL_TIME': [
      {
        question: "How much mental effort is this task currently requiring?",
        likert_scale: 'SCALE_1'
      },
      {
        question: "How much discomfort or distress is this task currently causing?",
        likert_scale: "SCALE_1"
      },
    ],
  },

  // Re-useable Likert scale labels
  // --------------------------------
  'LIKERT': {
    'SCALE_1': ["1<br>None", "2", "3", "4", "5", "6", "7<br>A Lot"],
    'SCALE_2': [
      "1<br>Significantly<br>Below Average", "2", "3", "4<br>Average",
      "5", "6", "7<br>Significantly<br>Above Average"],
    'SCALE_3': [
      "1<br>Very Negative/<br>Unpleasant<br>Emotions ", "2", "3", "4",
      "5", "6", "7<br>Very Positive/<br>Pleasant<br>Emotions"],
    'SCALE_4': [
      "1<br>Deactivated<br>and Have Very<br>Little Energy ", "2", "3", "4",
      "5", "6", "7<br>Activated and<br>Have a Great<br>Deal of Energy"]
  }
};
