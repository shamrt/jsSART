/**
 * Practice view blocks for jsSART
 */
var
 practice = [],
 participant_id = getParticipantId();

// practice block 1 notice
var practice_block_1_notice_text = "<p>For the first practice block, you will be given feedback after each item so that you know how you performed the task.</p>";
var practice_block_1_notice = createTextBlock(practice_block_1_notice_text);
practice.push(practice_block_1_notice);


// practice block 1
var practice_block_1 = createSartBlock(jsSART.PRACTICE_BLOCK_1_STIMULI, {
  give_feedback: true
});
practice.push(fixation_trial);
practice.push(practice_block_1);


// practice block 2 instructions
var practice_num_items = jsSART.PRACTICE_BLOCK_2_STIMULI.length,
    practice_min_correct = Math.ceil((practice_num_items - 1) / 4);

var practice_block_2_instructions = {
  type: "instructions",
  pages: [
    "<p>OK, you should be getting the hang of it.</p> <p>Before continuing, let the experimenter know if you have any questions.</p>",

    "<p>Now we are going to try some more practice but this time the numbers will be presented at a rate of <code>1</code> every <code>" + (jsSART.TIMING_POST_STIM / 1000) + "</code> seconds. You will be shown <code>" + practice_num_items + "</code> numbers; try your best to get as many problems right as possible.</p> <p>If you get fewer than <code>" + practice_min_correct + "</code> right, don't worry, the practice will repeat and you can try again! We want to be sure that you understand the task that is ahead of you.</p>"
  ],
  show_clickable_nav: true,
  allow_backward: false
};
practice.push(practice_block_2_instructions);


// practice block 2
// note: repeats until 1/4 of problems are correctly answered, or 3 failed
// trials
var practice_block_2_attempts = 0,
    skip_experiment = false;
var practice_block_2_notice_text = "<p>OK, let's practice the task once more, just as it will be in the experiment...</p>",
    practice_block_2_notice = createTextBlock(practice_block_2_notice_text),
    practice_block_2 = createSartBlock(jsSART.PRACTICE_BLOCK_2_STIMULI);

var practice_2_chunk = {
  chunk_type: 'while',
  timeline: [practice_block_2_notice, fixation_trial, practice_block_2],
  continue_function: function(data) {
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
    } else if (practice_block_2_attempts >=
        jsSART.PRACTICE_BLOCK_2_MAX_ATTEMPTS) {
      // skip the experiment in order to go straight to demographics
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
  "<p><strong>OK, looks like you've got it!</strong></p> <p>Do you have any questions at all? Remember, this is a challenging task. If you lose your place, just jump right back in. Watch for two numbers in a row, then add them up and keep going.</p> <p>Also note that, at several points during the task, you will pause briefly and be asked to report your experience before continuing on.</p>"
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
});


jsPsych.init({
  display_element: $('#jspsych-target'),
  timeline: practice,
  on_finish: function() {
    var url_params = {pid: participant_id},
        url_path = 'experiment';
    if (skip_experiment) {
      url_params = _.extend(url_params, {skip_experiment: skip_experiment});
      url_path = 'follow_up';
    }
    var url = url_path + '?' + $.param(url_params);
    postDataToDb(jsPsych.data.getData(), participant_id, url);
  }
});
