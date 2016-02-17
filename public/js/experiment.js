/**
 * Experiment view blocks for jsSART
 */
var experiment = [];
var participant_id = getParticipantId();
var conditions = generateConditions();

// prospective survey notice and questions
var prospective_survey_text = "<p>Before we begin, we would like to know what you <strong>expect to experience</strong> on this <strong>sustained attention task</strong>. The <strong>sustained attention task</strong> that will follow is identical to the practice trial you have just completed, although it will be longer.</p>";
var prospective_survey_notice = createTextBlock(prospective_survey_text);
experiment.push(prospective_survey_notice);

var prospective_survey = {
    type: 'survey-multi-choice',
    timeline: [
      {
        questions:
         ["In light of your experience so far, how much do you anticipate <strong><u>enjoying</u></strong> the <strong>sustained attention task</strong>?"],
         options:
         [jsSART.LIKERT.SCALE_1],
      },
      {
        questions:
        ["In light of your experience so far, how well do you <strong><u>anticipate performing</strong></u> during the <strong>sustained attention task</strong>?"],
        options:
        [jsSART.LIKERT.SCALE_2],
      },
      {
        questions:
        ["In light of your experience so far, how much <strong><u>mental effort</strong></u> do you expect will be required to complete the <strong>sustained attention task</strong>?"],
        options:
        [jsSART.LIKERT.SCALE_1],
      },
      {
        questions:
        ["In light of your experience so far, how much <strong><u>discomfort or distress</strong></u> do you expect to experience during the <strong>sustained attention task</strong>?"],
        options:
        [jsSART.LIKERT.SCALE_1],
      },
      {
        questions:
        ["In light of your experience so far, how much <strong><u>mental fatigue</strong></u> do you expect to have while completing the <strong>sustained attention task</strong>?"],
        options:
        [jsSART.LIKERT.SCALE_1]
      },
    ],
    required: [true, true, true, true, true],
    horizontal: true
};
experiment.push(prospective_survey);


// pre-experiment notice
var experiment_notice_text = "<p>This was an overview of the task, and you have completed the practice trials.</p> <p>The <strong>sustained attention</strong> task that will follow is identical to the practice trial you have just completed, altogether it will be 5-10 minutes long.</p> <p>Remember, if you get lost, just jump back in because we can’t stop the experiment once it has started. At several points in the task you will pause briefly to report your experience and then continue with the task.</p> <p>The <strong>sustained attention</strong> task will now follow.";
var experiment_notice = createTextBlock(experiment_notice_text);
experiment.push(experiment_notice);


// generate the experiment blocks
var formatted_block_stimuli = generateSartBlockStimuli(conditions);
experiment = experiment.concat(formatted_block_stimuli);


// end notice
var experiment_end_notice = createTextBlock(
  "<p><strong>You have completed the sustained attention task.</strong></p>"
);
experiment.push(experiment_end_notice);


// add generated experiment settings to saved data
jsPsych.data.addProperties({
  num_trials: conditions.num_trials,
  trials_per_block: conditions.trials_per_block,
  participant_id: participant_id,
});


jsPsych.init({
  display_element: $('#jspsych-target'),
  timeline: experiment,
  on_finish: function() {
    var redirect_url = 'follow_up?pid=' + participant_id;
    postDataToDb(jsPsych.data.getData(), participant_id, redirect_url);
  },
  // fullscreen: true
});
