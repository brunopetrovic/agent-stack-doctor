"""
Credentials checker tests.
"""

from agent_doctor.credentials import check_file


PLACEHOLDER_CASES = [
    """STRIPE_KEY='Fake'
OPENAI_API_KEY=sk-real-key-here
TWILIO_TOKEN=<INSERT_TOKEN>
SENTRY_DSN=${SENTRY_DSN}
SMTP_PASSWORD=CHANGE_ME
INTERNAL_SECRET=
ANTHROPIC_API_KEY=NULL
""",
]


class TestCredentials:
    def test_redacts_values(self, tmp_path):
        env = tmp_path / ".env"
        env.write_text("SECRET_KEY=super-secret-123\n")
        report = check_file(env)
        for key in report.keys:
            assert key.key != "super-secret-123"
            assert "super-secret" not in str(key)

    def test_placeholder_keys_flagged(self, tmp_path):
        env = tmp_path / ".env"
        env.write_text(PLACEHOLDER_CASES[0].lstrip())
        report = check_file(env)
        placeholders = report.placeholders
        assert len(placeholders) > 0, "Expected placeholders, got none"
        for pk in placeholders:
            assert pk.status == "placeholder", f"key {pk.key} expected placeholder, got {pk.status}"

    def test_no_false_positives_on_real_values(self, tmp_path):
        """Keys with real (non-placeholder) values should not be flagged."""
        env = tmp_path / ".env"
        env.write_text("OPENAI_API_KEY=sk-abc123\nMY_KEY=real_value\n")
        report = check_file(env)
        statuses = {k.key: k.status for k in report.keys}
        assert statuses.get("OPENAI_API_KEY") == "set"
        assert statuses.get("MY_KEY") == "set"

    def test_missing_required_keys(self, tmp_path):
        env = tmp_path / ".env"
        env.write_text("OPENAI_API_KEY=sk-abc\n")
        report = check_file(env, required_keys=["ANTHROPIC_API_KEY", "MISSING_KEY"])
        missing = report.missing
        assert len(missing) == 2
        missing_names = {k.key for k in missing}
        assert "ANTHROPIC_API_KEY" in missing_names
        assert "MISSING_KEY" in missing_names

    def test_json_output_valid(self, tmp_path):
        import json

        env = tmp_path / ".env"
        env.write_text("FOO=BAR\n")
        report = check_file(env)
        json.dumps([k.key for k in report.keys])