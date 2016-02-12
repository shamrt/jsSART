QUnit.test("getParticipantId", function(assert) {
  var url_params = getUrlParams();
  var expected_pid = 9999910000;
  if (_.contains(_.keys(url_params), "pid")) {
    expected_pid = url_params.pid;
  }
  assert.ok(getParticipantId() >= expected_pid);
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


QUnit.test("formatBlockStimuli, several with font size given", function(assert) {
  var font_sizes = ["100px"];
  var trials = [3, 4, 9];
  var expected = [
    {
      "stimuli": [
        "<div style='font-size:100px'>3</div>"
      ]
    },
    {
      "stimuli": [
        "<div style='font-size:100px'>4</div>"
      ]
    },
    {
      "stimuli": [
        "<div style='font-size:100px'>9</div>"
      ]
    }
  ];

  assert.deepEqual(formatBlockStimuli(trials, font_sizes), expected);
});


// check that randomly formatted block matches set of possible objects
function checkSingleFormattedBlockStimulus(trial, font_sizes) {
  var block_stimuli = formatBlockStimuli(trial);

  var has_expected_block = false;
  for (var i=0; i < font_sizes.length; i++) {
    var possible_expected = [{
      "stimuli": [
        "<div style='font-size:" + font_sizes[i] + "'>2</div>"
      ]
    }];

    if (_.isEqual(possible_expected, block_stimuli)) {
      has_expected_block = true;
      break;
    }
  }

  return has_expected_block;
}


QUnit.test("formatBlockStimuli, single stimulus without font sizes given", function(assert) {
  var trial = [2];
  var font_sizes = jsSART.STIMULI.FONT_SIZES;
  var has_expected_block = checkSingleFormattedBlockStimulus(
      trial, font_sizes);
  assert.ok(has_expected_block);
});


QUnit.test("formatBlockStimuli, single stimulus with incorrect possible font sizes given", function(assert) {
  var trial = [2];
  var font_sizes = ["foo", "bar", "baz"];
  var has_expected_block = checkSingleFormattedBlockStimulus(
      trial, font_sizes);
  assert.notOk(has_expected_block);
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
