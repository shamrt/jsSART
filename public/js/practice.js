/**
 * Practice view blocks for jsSART
 */

(function() {
  var practice = [];
  var participant_id = getParticipantId();
  var practice_condition = generatePracticeCondition();
  var practice_trials = generatePracticeTrials(practice_condition);


  // baseline evaluation questions
  var baseline_notice = createTextBlock("<p>Before we get started, we would like to ask you a couple of questions about how you're feeling right now.</p>");
  var baseline_questions = generateMultiChoiceSurvey(
      jsSART.QUESTIONS.AROUSAL, true  // randomized order
  );
  practice.push(
    baseline_notice,
    baseline_questions
  );

  // practice block 1
  // ----------------------------
  // notice
  var practice_block_1_notice_text = "<p>Thank you!</p> <p>Now, for the first practice block, you will be given feedback after each item so that you know how you performed the task.</p> <p>When you're ready to continue, the practice block will begin.</p>";
  var practice_block_1_notice = createTextBlock(practice_block_1_notice_text);
  // practice block 1
  var practice_block_1 = createSartBlock(practice_trials.BLOCK_1_STIMULI, {
    give_feedback: true
  });
  practice.push(
    practice_block_1_notice,
    fixation_trial,
    practice_block_1
  );


  // practice block 2
  // ----------------------------
  // instructions
  var practice_num_items = practice_trials.BLOCK_2_STIMULI.length;
  // NOTE: participants must get a minimum number of items correct
  var practice_min_correct = getPracticeMinCorrect(
    practice_num_items, jsSART.PRACTICE.MAX_ERROR_RATE);

  var practice_block_2_instructions = {
    type: "instructions",
    pages: [
      "<p>OK, you should be getting the hang of it.</p> <p>Before continuing, let the experimenter know if you have any questions.</p> <p>You will now continue with a second block of practice trials; however, you will no longer receive any feedback on how you are doing.</p>",

      "<p><strong>Remember:</strong> Whenever there is a digit other than <code>" + jsSART.STIMULI.NO_GO_VALUE + "</code> (e.g. <code>1, 2, 4, 5, 6, 7, 8, 9</code>), press the " + spacebar_html + " as fast as you can. However, if digit <code>" + jsSART.STIMULI.NO_GO_VALUE + "</code> is presented, don’t do anything. Just wait for the next digit.</p> <p>Use the index finger of your dominant hand when responding (e.g. if you are left-handed, use your left index finger to press the " + spacebar_html + ".</p> <p>It’s important to be accurate and fast in this study.</p>",

      "<p>Now we are going to try some more practice but this time the numbers will be presented at a rate of <code>1</code> every <code>~" + (sum(jsSART.STIMULI.DISPLAY_TIMINGS) / 1000) + "</code> seconds. You will be shown <code>" + practice_num_items + "</code> numbers.</p> <p>We want to be sure that you understand the task that is ahead of you, so if you get fewer than <code>" + practice_min_correct + "</code> right, don't worry, the practice will repeat and you can try again!</p>"
    ],
    show_clickable_nav: true,
    allow_backward: false
  };
  practice.push(practice_block_2_instructions);


  // practice block 2
  // NOTE: repeats if error rate threshold is eclipsed, or 3 failed trials
  var practice_block_2_attempts = 0;
  var skip_experiment = false;
  var practice_block_2_notice_text = "<p>OK, let's practice the task once more, just as it will be in the experiment...</p>";
  var practice_block_2_notice = createTextBlock(practice_block_2_notice_text);
  var practice_block_2 = createSartBlock(practice_trials.BLOCK_2_STIMULI);

  var practice_2_chunk = {
    chunk_type: 'while',
    timeline: [practice_block_2_notice, fixation_trial, practice_block_2],
    loop_function: function(data) {
      practice_block_2_attempts++;
      // total number of correct problems
      var num_correct = 0;
      for (var i in data) {
        if (data[i].correct) {
          num_correct++;
        }
      }

      if (num_correct >= practice_min_correct) {
        // end the practice loop
        return false;
      } else if (practice_block_2_attempts >= jsSART.PRACTICE.MAX_ATTEMPTS) {
        // end the practice loop
        // also skip the experiment in order to go straight to demographics
        skip_experiment = true;
        return false;
      } else {
        // keep going until enough problems are correctly answered
        return true;
      }
    }
  };
  practice.push(practice_2_chunk);


  // post-practice notice
  // note: skipped if practice block 2 not understood
  var post_practice_notice_block = createTextBlock(
    "<p><strong>OK, looks like you've got it!</strong></p> <p>Do you have any questions at all? Remember, this is a challenging task. If you make a mistake, just jump right back in.</p> <p>Also note that, at several points during the task, you will pause briefly and be asked to report your experience before continuing on.</p>"
  );
  var post_practice_notice = {
    chunk_type: 'if',
    timeline: [post_practice_notice_block],
    conditional_function: function() { return !skip_experiment; }
  };
  practice.push(post_practice_notice);


  // end practice notice
  var end_practice_notice = createTextBlock(
    "<strong>You have now completed the practice blocks.</strong>"
  );
  practice.push(end_practice_notice);


  // add generated experiment settings to saved data
  jsPsych.data.addProperties({
    participant_id: participant_id,
    practice_condition: practice_condition
  });


  jsPsych.init({
    display_element: $('#jspsych-target'),
    timeline: practice,
    on_finish: function() {
      var url_params = {pid: participant_id};
      var url_path = 'experiment';
      // NOTE: different params and URL if practice block 2 not understood
      if (skip_experiment) {
        url_params = _.extend(url_params, {skip_experiment: skip_experiment});
        url_path = 'follow_up';
      }

      var redirect_url = url_path + '?' + $.param(url_params);
      postDataToDb(jsPsych.data.getData(), participant_id, redirect_url);
    }
  });
})();
