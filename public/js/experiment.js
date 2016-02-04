/**
 * Experiment view blocks for jsPASAT
 */
var
  experiment = [],
  participant_id = getParticipantId();

// prospective survey notice and questions
var prospective_survey_text = "<p>Before we begin, we would like to know what you <strong>expect to experience</strong> on this <strong>working memory task</strong>. The <strong>working memory task</strong> that will follow is identical to the practice trial you have just completed, although it will be longer, approximately 5-10 minutes.</p>";
var prospective_survey_notice = createTextBlock(prospective_survey_text);
experiment.push(prospective_survey_notice);

var prospective_survey = {
    type: 'survey-multi-choice',
    questions: [
      ["In light of your experience so far, how much do you anticipate <strong><u>enjoying</u></strong> the <strong>working memory task</strong>?"],
      ["In light of your experience so far, how well do you <strong><u>anticipate performing</strong></u> during the <strong>working memory task</strong>?"],
      ["In light of your experience so far, how much <strong><u>mental effort</strong></u> do you expect will be required to complete the <strong>working memory task</strong>?"],
      ["In light of your experience so far, how much <strong><u>discomfort or distress</strong></u> do you expect to experience during the <strong>working memory task</strong>?"],
      ["In light of your experience so far, how much <strong><u>mental fatigue</strong></u> do you expect to have while completing the <strong>working memory task</strong>?"],
    ],
    options: [
      [jsPASAT.LIKERT_SCALE_1],
      [jsPASAT.LIKERT_SCALE_2],
      [jsPASAT.LIKERT_SCALE_1],
      [jsPASAT.LIKERT_SCALE_1],
      [jsPASAT.LIKERT_SCALE_1]
    ],
    required: [
      [true],
      [true],
      [true],
      [true],
      [true],
    ],
    horizontal: true
};
experiment.push(prospective_survey);


// pre-experiment notice
var experiment_notice_text = "<p>This was an overview of the task, and you have completed the practice trials.</p> <p>The <strong>working memory</strong> task that will follow is identical to the practice trial you have just completed, altogether it will be 5-10 minutes long.</p> <p>Remember, if you get lost, just jump back in because we can’t stop the experiment once it has started. At several points in the task you will pause briefly to report your experience and then continue with the task.</p> <p>The <strong>working memory</strong> task will now follow.";
var experiment_notice = createTextBlock(experiment_notice_text);
experiment.push(experiment_notice);


// generate the experiment blocks
var condition = generateCondition();
var block_types = (jsPASAT.BLOCK_TYPE_ORDER === null) ? generateRandomBlockTypes(condition) : jsPASAT.BLOCK_TYPE_ORDER;
var pasat_blocks = generatePasatBlockStimuli(block_types);
experiment = experiment.concat(pasat_blocks.formatted_stimuli);


// end notice
var experiment_end_notice = createTextBlock(
  "<p><strong>You have completed the working memory task.</strong></p>"
);
experiment.push(experiment_end_notice);


// add generated experiment settings to saved data
jsPsych.data.addProperties({
  condition: condition,
  block_order: block_types,
  participant_id: participant_id,
});


jsPsych.init({
  display_element: $('#jspsych-target'),
  timeline: experiment,
  on_finish: function() {
    var url = 'follow_up?pid=' + participant_id;
    postDataToDb(jsPsych.data.getData(), participant_id, url);
  }
});
