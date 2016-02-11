QUnit.test("getParticipantId, with window prompt", function(assert) {
  assert.ok(getParticipantId() >= 9999910000 );
});


QUnit.test("createTextBlock", function(assert) {
  var arg = "<p>Foo bar</p>";
  var expected = {
    "type": "text",
    "text": arg + continue_html,
    "cont_key": [32, 13]
  };
  assert.deepEqual(createTextBlock(arg), expected);
});


QUnit.test("formatBlockStimuli", function(assert) {
  assert.expect(2);

  // without font size given
  var without_trials = [2, 4];
  var without_expected = [
    {
      "stimuli": [
        "<div style='font-size:" + jsSART.STIMULI.FONT_SIZES[0] + "'>2</div>"
      ]
    },
    {
      "stimuli": [
        "<div style='font-size:" + jsSART.STIMULI.FONT_SIZES[0] + "'>4</div>"
      ]
    }
  ];
  assert.deepEqual(formatBlockStimuli(without_trials), without_expected);

  // with font size of 100 given
  var font_size = 100;
  var with_trials = [3];
  var with_expected = [
    {
      "stimuli": [
        "<div style='font-size:100'>3</div>"
      ]
    },
  ];
  assert.deepEqual(formatBlockStimuli(with_trials, font_size), with_expected);
});


QUnit.test("generateStimuli length", function(assert) {
  var num_stimuli = 25;
  var stimuli = generateStimuli(num_stimuli);
  assert.deepEqual(stimuli.length, num_stimuli);
});

QUnit.test("generateStimuli stimuli values", function(assert) {
  // check that all stimuli are expected possible value set
  var num_stimuli = 25;
  var stimuli = generateStimuli(num_stimuli);
  for (var i=0; i < stimuli.length; i++) {
    var is_expected_value = _.contains(jsSART.STIMULI.VALUES, stimuli[i]);
    assert.ok(is_expected_value);
  }
});
