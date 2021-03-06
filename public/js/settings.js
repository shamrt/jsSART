/**
 * Settings configuration for jsSART
 */

var jsSART = {

  // Conditions
  // --------------------------------
  'CONDITIONS': {
    // Total number of trials a participant will see during experiment
    'NUM_TRIALS': [1125],
    // Number of trials before being shown real-time post-block questions
    'TRIALS_PER_BLOCK': [225],
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
    // No-go values per block
    'NO_GOS_PER_BLOCK': 25,
    // Font sizes
    // NOTE: approx. 48px, 72px, 94px, 100px and 120px
    'FONT_SIZES': ["12mm", "17.4mm", "22.717mm", "24.17mm", "29mm"],
    // Allow keys 1--9 and numpad 1--9
    'ALLOW_KEYCODES': [32, 13],
    // Pace of PASAT trial presentation
    // NOTE: first number for stimlus (in milliseconds), second for fixation
    'DISPLAY_TIMINGS': [250, 900]
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
    // Baseline and post-experiment evaluation of valence and arousal
    'AROUSAL': [
      {
        question: "Right now, I am feeling:",
        likert_scale: 'EMOTIONS'
      },
      {
        question: "Right now, my mind and body are:",
        likert_scale: "ENERGY"
      },
    ],
    // Real-time evaluation during the experiment (between blocks)
    'REAL_TIME': [
      {
        question: "How much mental effort is this task currently requiring?",
        likert_scale: 'NONE_ALOT'
      },
      {
        question: "How much discomfort or distress is this task currently causing?",
        likert_scale: "NONE_ALOT"
      },
      {
        question: "How much boredom are you currently experiencing?",
        likert_scale: "NONE_ALOT"
      },
    ],
    // Self-report anticipated effort, discomfort, etc
    'ANTICIPATION': [
      {
        question: "In light of your experience so far, how much do you anticipate <strong><u>enjoying</u></strong> this task?",
         likert_scale: "NONE_ALOT"
      },
      {
        question: "In light of your experience so far, how well do you <strong><u>anticipate performing</strong></u> during this task?",
        likert_scale: "BELOW_ABOVE_AVG"
      },
      {
        question: "In light of your experience so far, how much <strong><u>mental effort</strong></u> do you expect will be required to complete this task?",
        likert_scale: "NONE_ALOT"
      },
      {
        question: "In light of your experience so far, how much <strong><u>discomfort or distress</strong></u> do you expect to experience during this task?",
        likert_scale: "NONE_ALOT"
      },
      {
        question: "In light of your experience so far, how much <strong><u>mental fatigue</strong></u> do you expect to have while completing this task?",
        likert_scale: "NONE_ALOT"
      },
      {
        question: "In light of your experience so far, how <strong><u>motivated</strong></u> are you to perform to the best of your ability on this task?",
        likert_scale: "NOT_EXTREMELY"
      },
      {
        question: "How much boredom are you currently experiencing?",
        likert_scale: "NONE_ALOT"
      },
    ],
    // Post-experiment retrospective evaluation
    'RETROSPECTIVE': [
      {
        question: "How mentally demanding was the task?",
        likert_scale: "LOW_HIGH"
      },
      {
        question: "How physically demanding was the task?",
        likert_scale: "LOW_HIGH"
      },
      {
        question: "How hurried or rushed was the pace of the task?",
        likert_scale: "LOW_HIGH"
      },
      {
        question: "How successful were you in accomplishing what you were asked to do?",
        likert_scale: "PERFORMANCE"
      },
      {
        question: "How hard did you have to work to accomplish your level of performance?",
        likert_scale: "LOW_HIGH"
      },
      {
        question: "How insecure, discouraged, irritated, stressed, and annoyed were you?",
        likert_scale: "LOW_HIGH"
      },
      {
        question: "How distressed or uncomfortable were you?",
        likert_scale: "LOW_HIGH"
      },
      {
        question: "How bored were you?",
        likert_scale: "LOW_HIGH"
      },
      {
        question: "How mentally fatigued were you?",
        likert_scale: "LOW_HIGH"
      },
      {
        question: "How much did you enjoy the task?",
        likert_scale: "LOW_HIGH"
      },
      {
        question: "How much did you enjoy the task?",
        likert_scale: "NONE_ALOT"
      },
      {
        question: "How hard did you try to do you best?",
        likert_scale: "NOT_EXTREMELY"
      },
      {
        question: "How satisfied are you with your performance?",
        likert_scale: "SATISFACTION"
      },
    ]
  },

  // Re-useable Likert scale labels
  // --------------------------------
  'LIKERT': {
    'NONE_ALOT': ["1<br>None", "2", "3", "4", "5", "6", "7<br>A Lot"],
    'LOW_HIGH': ["1<br>Very Low", "2", "3", "4", "5", "6", "7<br>Very High"],
    'PERFORMANCE': ["1<br>Perfect", "2", "3", "4", "5", "6", "7<br>Failure"],
    'BELOW_ABOVE_AVG': [
      "1<br>Significantly<br>Below Average", "2", "3", "4<br>Average",
      "5", "6", "7<br>Significantly<br>Above Average"
    ],
    'EMOTIONS': [
      "1<br>Very Negative/<br>Unpleasant<br>Emotions", "2", "3", "4",
      "5", "6", "7<br>Very Positive/<br>Pleasant<br>Emotions"
    ],
    'ENERGY': [
      "1<br>Deactivated<br>and Have Very<br>Little Energy", "2", "3", "4",
      "5", "6", "7<br>Activated and<br>Have a Great<br>Deal of Energy"
    ],
    'NOT_EXTREMELY': [
      "1<br>Not<br>at all", "2", "3", "4", "5", "6", "7<br>Extremely"
    ],
    'NOT_WELL': [
      "1<br>Not at all", "2<br>A little", "3<br>Somewhat", "4<br>Well", "5<br>Very well"
    ],
    'SATISFACTION': [
      "1<br>Not at all<br>satisfied", "2", "3", "4", "5", "6",
      "7<br>Completely<br>satisfied"
    ],
    'WILLINGNESS': [
      "1<br>Not at all<br>willing", "2", "3", "4", "5", "6",
      "7<br>Definitely<br>willing"
    ],
    'TRUTH': [
      "1<br>Not at all<br>true", "2", "3", "4", "5", "6",
      "7<br>Very true"
    ],
    'AGREE_DISAGREE': [
      "1<br>Strongly<br>disagree", "2<br>Disagree",
      "3<br>Somewhat<br>disagree", "4<br>Neutral", "5<br>Somewhat<br>agree",
      "6<br>Agree", "7<br>Strongly<br>agree"
    ],
  }
};
