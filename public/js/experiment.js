/**
 * Experiment view blocks for jsSART
 */

(function(){
  var experiment = [];
  var participant_id = getParticipantId();
  var conditions = generateConditions();

  // prospective survey notice and questions
  var prospective_survey_text = "<p>Before we begin, we would like to know what you <strong>expect to experience</strong> on this <strong>attention task</strong>. The <strong>attention task</strong> that will follow is identical to the practice trial you have just completed, although it will be longer.</p>";
  var prospective_survey_notice = createTextBlock(prospective_survey_text);

  var prospective_survey = generateMultiChoiceSurvey(
    jsSART.QUESTIONS.ANTICIPATION, true);  // randomize order

  var realtime_notice = createTextBlock("<p>Throughout the attention task, you will be asked at various time points to report how you feel <strong>at that exact moment</strong>.</p><p>Please report how you feel as accurately as possible, even if your rating is the same as (or higher or lower than) your last rating — we are interested in the accurate reporting of how you feel during the attention task moment by moment.</p>");

  experiment.push(
    prospective_survey_notice,
    prospective_survey,
    realtime_notice
  );


  // pre-experiment notice
  var experiment_notice_text = "<p>This was an overview of the task, and you have completed the practice trials.</p> <p>The <strong>attention task</strong> that will follow is identical to the practice trial you have just completed.</p> <p>Remember, if you get lost, just jump back in because we can’t stop the experiment once it has started. At several points in the task you will pause briefly to report your experience and then continue with the task.</p> <p>The <strong>attention task</strong> will now follow.";
  var experiment_notice = createTextBlock(experiment_notice_text);
  experiment.push(experiment_notice);


  // generate the experiment blocks
  var formatted_block_stimuli = generateSartBlockStimuli(conditions);
  experiment = experiment.concat(formatted_block_stimuli);


  // post-experiment valance and arousal questions (randomized order)
  var valence_and_arousal = generateMultiChoiceSurvey(
    jsSART.QUESTIONS.AROUSAL, true
  );
  experiment.push(valence_and_arousal);


  // end notice
  var experiment_end_notice = createTextBlock(
    "<p><strong>You have completed the attention task.</strong></p>"
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
    }
  });
})();
