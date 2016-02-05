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
