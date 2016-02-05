/**
 * Settings configuration for jsSART
 */

var jsSART = {

  // Condition
  // --------------------------------
  // Sets the number of blocks in
  'BLOCKS_PER_CONDITION': [5, 6, 7, 8, 9],

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
  'TRIALS_PER_BLOCK': 15,
  // The order of blocks presented to a participant, e.g.:
  //   'BLOCK_TYPE_ORDER': ["medium", "hard", "medium", "medium", "easy", "medium", "medium"],
  // Note: If set to ``null``, block type order will be randomly generated
  'BLOCK_TYPE_ORDER': null,
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
