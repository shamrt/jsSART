/**
 * Follow-up question blocks for jsSART
 */
var
  follow_up = [],
  participant_id = getParticipantId();

// post-survey notice
var task_complete_text = "<p>Now you will be asked a series of questions about yourself.</p>";
var task_complete_notice = createTextBlock(task_complete_text);
follow_up.push(task_complete_notice);


// post-survey demographics questions
// ---------------------------------

// age questions
var demographics_age = {
  type: 'survey-text',
  timeline: [
    {questions: ["How old are you?"]},
    {questions: [
      "What is your date of birth? (MM/YYYY; e.g., <code>01/1995</code>)"
    ]}
  ]
};

// part 1
var demographics_1_questions = [
  {
    questions: ["Please indicate your sex:"],
    options: [["Male", "Female"]]
  },
  {
    questions: ["Which year of university are you currently in?"],
    options: [[
      "1st year undergrad", "2nd year undergrad", "3rd year undergrad",
      "4th year undergrad", "Graduated", "Post-BA/BSc continuing"
    ]]
  },
  {
    questions: ["What is the highest level of education that you intend to complete?"],
    options: [[
      "Bachelor's degree", "Master's degree", "PhD",
      "Professional degree (e.g., law)"
    ]]
  },
  {
    questions: ["Is English your first language?"],
    options: [["Yes", "No"]]
  },
  {
    questions: ["For how many years have you been speaking English?"],
    options: [[
      "Less than 1 year", "1–2 years", "3–5 years", "6–10 years",
      "10+ years", "All my life"
    ]]
  },
  {
    questions: ["What is your mother’s highest level of education?"],
    options: [[
      "Less than high school", "High school", "Some college", "BA/BSc degree",
      "MA/MSc degree", "PhD", "Professional degree (e.g., law)",
      "Not applicable"
    ]]
  }
];
var demographics_1 = {
  type: 'survey-multi-choice',
  timeline: demographics_1_questions,
  required: _.map(demographics_1_questions, function() { return true; })
};

// part 2
var demographics_2 = {
  type: 'survey-text',
  questions: [
    ["What is your mother's occupation?"]
  ]
};

// part 3
var demographics_3_questions = [
  {
    questions: ["What is your father’s highest level of education?"],
    options: [
      ["Less than high school", "High school", "Some college", "BA/BSc degree", "MA/MSc degree", "PhD", "Professional degree (e.g., law)", "Not applicable"]
    ]
  },
];
var demographics_3 = {
  type: 'survey-multi-choice',
  timeline: demographics_3_questions,
  required: _.map(demographics_3_questions, function() { return true; })
};

// part 4
var demographics_4_questions = [
  ["What is your father's occupation?"],
  ["What was your final average at the end of high school?<br><em>(percentage; e.g., <code>75%</code>)</em>"],
  ["Estimate your current university average<br><em>(estimate percentage; e.g., <code>75%</code>)</em>:"],
];
var demographics_4 = {
  type: 'survey-text',
  timeline: _.map(demographics_4_questions, function(q) {
    return {questions: q};
  })
};

// part 5
var demographics_5_questions = [
  {
    questions: ["How many <u>statistics</u> courses <strong>in university</strong> have you taken (or are currently taking)?"],
    options: ["None", "1", "2", "3", "4", "5", "More than 5"],
  },
  {
    questions: ["How many <u>statistics</u> courses did you take <strong>in high school</strong>?"],
    options: ["None", "1", "2", "3", "4", "5", "More than 5"],
  },
  {
    questions: ["How many years of <strong>mathematics</strong> (algebra, geometry, calculus, etc.) did you take <strong>in high school</strong>?"],
    options: ["None", "1", "2", "3", "4", "More than 4"],
  },
  {
    questions: ["How many <u>mathematics</u> courses <strong>in university</strong> have you taken (or are currently taking)?"],
    options: ["None", "1", "2", "3", "4", "5", "More than 5"],
  },
  {
    questions: ["On a scale of 1–7, how much do you like math?"],
    options: jsSART.LIKERT.SCALE_1,
  },
  {
    questions: ["Have you been previously diagnosed with ADD or AD/HD?"],
    options: ["Yes", "No"],
  },
];
var demographics_5 = {
  type: 'survey-multi-choice',
  timeline: demographics_5_questions,
  required: _.map(demographics_5_questions, function() { return true; }),
  horizontal: true
};

// part 6
var demographics_6 = {
  type: 'survey-text',
  questions: [
    ["Please indicate what your current (or intended) university major is:"]
  ]
};

// extended questions
var lead_in_question = "When using <strong>computers and/or electronic media</strong>, do you ";
var extended_questions = [
      lead_in_question + "open attachments in emails that are sent by someone you don’t know?",
      lead_in_question + "backup important work and documents on your computer?",
      lead_in_question + "have time limits on how much recreational time you spend using those electronic media at home?",
      lead_in_question + "use the privacy settings on social networking sites, such as Facebook and Twitter, to protect your personal information and privacy?",
      "Do you have anti-virus software on your home computer(s)?",
      "Have you ever had a computer virus?",
    ];
var extended_questions_1 = {
  type: 'survey-multi-choice',
  timeline: _.map(extended_questions, function(q) {
    return {
      questions: [q],
      options: [["Yes", "No"]],
      required: [true]
    };
  }),
};
var extended_questions_2 = {
  type: 'survey-text',
  questions: [
    ["How many times have you had a computer virus?"]
  ]
};

// behavioural survey preamble
var behav_survey_preamble = "For these next items, please indicate how the emotional or behavioural problems listed might have affected you <strong><u>in the last month</u></strong>.";
var behav_survey_notice = createTextBlock(behav_survey_preamble);

// behavioural survey
var lead_in_school = "<strong>At school</strong>, have you had ";
var lead_in_life = "<strong>In general</strong>, have you ";
var behav_survey_questions = [
  lead_in_school + "problems taking notes?",
  lead_in_school + "problems completing assignments?",
  lead_in_school + "problems getting your work done efficiently ?",
  lead_in_school + "problems with instructors?",
  lead_in_school + "problems meeting minimum requirements to stay in school?",
  lead_in_school + "problems with attendance?",
  lead_in_school + "problems with being late?",
  lead_in_school + "problems with working to your potential?",
  lead_in_school + "problems with inconsistent grades?",
  lead_in_life + "made excessive or inappropriate use of internet, video games or TV?",
  lead_in_life + "had problems getting ready to leave the house?",
  lead_in_life + "had problems getting to bed?",
  lead_in_life + "had problems with eating junk food?",
  lead_in_life + "gotten hurt or injured?",
  lead_in_life + "been avoiding exercise?",
  lead_in_life + "had problems attending regular appointments, such as doctor/dentist?",
  lead_in_life + "had problems managing chores at home?",
  lead_in_life + "had problems managing money?"
];
var behav_survey_likert = [
  "0<br>Never or<br>not at all",
  "1<br>Sometimes<br>or somewhat",
  "2<br>Often or<br>very much",
  "3<br>Very often<br>or very much",
  "N/A"
];
var behavioural_survey = {
  type: 'survey-multi-choice',
  timeline: _.map(behav_survey_questions, function(q) {
    return {
      questions: [q],
      options: [behav_survey_likert],
      required: [true]
    };
  }),
  horizontal: true,
  randomize_order: true
};

follow_up.push(
  // demographics_age,
  // demographics_1,
  // demographics_2,
  // demographics_3,
  // demographics_4,
  // demographics_5,
  // demographics_6,
  // extended_questions_1,
  // extended_questions_2,
  // behav_survey_notice,
  // behavioural_survey
);


// retrospective questions notice
var retrospective_survey_text = "<p>Now we are going to ask you some questions about <strong>the sustained attention task</strong> you completed previously – that is, the task where numbers were presented to you on a computer screen one at a time and you had to add them up.</p>";
var retrospective_survey_notice = createTextBlock(retrospective_survey_text);

// retrospective questions
var retrospective_survey_timeline = [
  {
    questions: ["On this <strong>sustained attention task</strong>, what was " +
                "your <u><strong>total amount of mental effort</strong></u>?"],
    options: [jsSART.LIKERT.SCALE_1]
  },
  {
    questions: ["On this <strong>sustained attention task</strong>, what was " +
                "your total amount of <u><strong>discomfort or " +
                "distress</strong></u>?"],
    options: [jsSART.LIKERT.SCALE_1]
  },
  {
    questions: ["How much did you <u><strong>enjoy</u></strong> doing this " +
                "<strong>sustained attention task</strong>?"],
    options: [jsSART.LIKERT.SCALE_1]
  },
  {
    questions: ["How well did you <u><strong>perform</u></strong> on the " +
                "<strong>sustained attention task</strong>?"],
    options: [jsSART.LIKERT.SCALE_2]
  },
  {
    questions: ["How much <u><strong>mental fatigue</u></strong> did you " +
                "have during the <strong>sustained attention task</strong>?"],
    options: [jsSART.LIKERT.SCALE_1]
  },
  {
    questions: ["How <u><strong>satisfied</u></strong> are you with your " +
                "performance on the <strong>sustained attention " +
                "task</strong>?"],
    options: [[
      "1<br>Not at all<br>satisfied", "2", "3", "4", "5", "6",
      "7<br>Completely<br>satisfied"
    ]]
  },
  {
    questions: ["How willing would you be to do <strong><u>another</u> sustained attention task</strong> right now?"],
    options: [[
      "1<br>Not at all<br>willing", "2", "3", "4", "5", "6",
      "7<br>Definitely<br>willing"
    ]]
  }
];
var retrospective_survey = {
  type: 'survey-multi-choice',
  timeline: retrospective_survey_timeline,
  required: _.map(retrospective_survey_timeline, function() {
    return true;
  }),
  horizontal: true
};

// don't include retrospective questions if the experiment was skipped
var url_params = getUrlParams();
if (!_.has(url_params, 'skip_experiment')) {
  follow_up.push(retrospective_survey_notice);
  follow_up.push(retrospective_survey);
}


// add generated experiment settings to saved data
jsPsych.data.addProperties({
  participant_id: participant_id,
});


jsPsych.init({
  display_element: $('#jspsych-target'),
  timeline: follow_up,
  on_finish: function() {
    postDataToDb(jsPsych.data.getData(), participant_id, 'finish');
  }
});
