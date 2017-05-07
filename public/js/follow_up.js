/**
 * Follow-up question blocks for jsSART
 */

(function(){
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
  var demographics_1 = {
    type: 'survey-multi-choice',
    timeline: [
      {
        questions: ["Please indicate your gender:"],
        options: [["Male", "Female", "Other"]]
      },
    ],
    required: [true]
  };

  follow_up.push(
    demographics_age,
    demographics_1
  );


  // Behavioural survey questions
  // -------------

  // SMS scale
  var sms_scale_notice = createTextBlock("Next you will be presented with a list of statements.</p><p>Please use the accompanying rating scale to indicate how well each statement describes your experiences in the past 15 minutes.")
  var sms_questions = [
    "I was aware of different emotions that arose in me",
    "I tried to pay attention to pleasant and unpleasant sensations",
    "I found some of my experiences interesting",
    "I noticed many small details of my experience",
    "I felt aware of what was happening inside of me",
    "I noticed pleasant and unpleasant emotions",
    "I actively explored my experience in the moment",
    "I clearly physically felt what was going on in my body",
    "I changed my body posture and paid attention to the physical process of moving",
    "I felt that I was experiencing the present moment fully",
    "I noticed pleasant and unpleasant thoughts",
    "I noticed emotions come and go",
    "I noticed various sensations caused by my surroundings (e.g., heat, coolness, the wind on my face)",
    "I noticed physical sensations come and go",
    "I had moments when I felt alert and aware",
    "I felt closely connected to the present moment",
    "I noticed thoughts come and go",
    "I felt in contact with my body",
    "I was aware of what was going on in my mind",
    "It was interesting to see the patterns of my thinking",
    "I noticed some pleasant and unpleasant physical sensations",
  ];
  var sms_question_set = createScaleQuestionSet(sms_questions, "NOT_WELL");
  var sms_scale = generateMultiChoiceSurvey(sms_question_set, true);

  // state boredom scale
  var state_boredom_notice = createTextBlock("<p>For the next series of statements, please indicate how you feel <strong>right now</strong> about yourself and your life, even if it is different from how you usually feel.</p>");
  var state_boredom_questions = [
    "I seem to be forced to do thing that have no value to me.",
    "I feel bored.",
    "I am wasting time that would be better spent on something else.",
    "I want something to happen but I am not sure what.",
    "I feel like I’m sitting around waiting for something to happen.",
    "I am easily distracted.",
    "My mind is wandering.",
    "Time is passing by slower than usual.",
  ];
  var state_boredom_question_set = createScaleQuestionSet(state_boredom_questions, "AGREE_DISAGREE");
  var state_boredom_scale = generateMultiChoiceSurvey(state_boredom_question_set, true);

  follow_up.push(
    sms_scale_notice,
    sms_scale,
    state_boredom_notice,
    state_boredom_scale
  );


  // retrospective questions notice
  var retrospective_survey_text = "<p>Now we are going to ask you some questions about <strong>the attention task</strong> you completed previously – that is, the task where numbers were presented to you on a computer screen one at a time and you had to press the " + spacebar_html + " for every number except <code>" + jsSART.STIMULI.NO_GO_VALUE + "</code>.</p>";
  var retrospective_survey_notice = createTextBlock(retrospective_survey_text);

  // retrospective questions
  var retrospective_survey = generateMultiChoiceSurvey(
    jsSART.QUESTIONS.RETROSPECTIVE, true);  // randomize order

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
})();
