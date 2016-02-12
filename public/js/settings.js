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
    'TRIALS_PER_BLOCK': [225, 82]
  },

  // Stimuli
  // --------------------------------
  'STIMULI': {
    // Possible stimuli values
    'VALUES': _.range(1, 10),  // 1--9
    // No-go value
    'NO_GO_VALUE': 3,
    // Font sizes
    'FONT_SIZES': ["48px", "72px", "94px", "100px", "120px"],
    // Second level quasi-random counter range
    'QUASI_RANDOM_RANGE': _.range(4)  // 0-3
  },

  // Pace of PASAT trial presentation
  // --------------------------------
  'TIMING_STIM_DISPLAY': 1000,
  'TIMING_POST_STIM': 4000,

  // Practice block stimuli
  // --------------------------------
  'PRACTICE_BLOCK_1_STIMULI': [9, 1, 3, 5, 2, 6],
  'PRACTICE_BLOCK_2_STIMULI': [6, 4, 5, 7, 2, 8, 4, 5, 9, 3, 6, 9, 2, 7, 3, 8],
  'PRACTICE_BLOCK_2_MAX_ATTEMPTS': 3,

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
