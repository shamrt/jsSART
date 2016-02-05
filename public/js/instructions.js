/**
 * Instructions view block for jsSART
 */
var
  instructions = [],
  participant_id = getParticipantId();

var instructions_block = {
  type: "instructions",
  pages: [
    "<p>Welcome!</p> " +
    "<p>In this study you will be presented with a single digit (1-9) in varying sizes in the middle of the screen for a short duration. The digit is then followed by a crossed circle.</p>",

    "<p>Your task is to either:</p> " +
    "<ol>" +
      "<li>press the " + spacebar_html + " when you see any digit other than <code>3</code>; or,</li>" +
      "<li>don’t do anything (press no key) when you see the digit <code>3</code>, and just wait for the next digit to be shown.</li>" +
    "<ol>",

    "<p>It’s important to be accurate and fast in this study.</p>" +
    "<p>Use the index finger of your dominant hand when responding (e.g. if you are left-handed, use your left index finger to press the " + spacebar_html + ").</p>",

    "<p>We will now continue to some practice trials.</p>"
  ],
  show_clickable_nav: true
};
instructions.push(instructions_block);

jsPsych.init({
  display_element: $('#jspsych-target'),
  timeline: instructions,
  on_finish: function() {
    var url = 'practice?pid=' + participant_id;
    window.location = url;
  }
});
