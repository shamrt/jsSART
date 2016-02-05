QUnit.test("getParticipantId, with window prompt", function(assert) {
  assert.ok(getParticipantId() >= 9999910000 );
});
