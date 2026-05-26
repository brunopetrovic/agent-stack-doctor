"""
Cron checker tests.
"""

from agent_doctor.cron import check_cron


JOBS_STALE_OUTPUT = """
[
  {
    "id": "job-1",
    "enabled": true,
    "script": "/scripts/notify.py",
    "last_run": "2020-01-01T00:00:00Z",
    "outputs": ["output/report.json"]
  },
  {
    "id": "job-2",
    "enabled": true,
    "script": "/scripts/sync.py"
  },
  {
    "id": "job-3",
    "enabled": false,
    "script": "/scripts/disabled.py",
    "last_run": "2020-01-01T00:00:00Z"
  }
]
"""

JOBS_MISSING_SCRIPT = """
[
  {
    "id": "job-no-script",
    "enabled": true,
    "last_run": "2025-01-01T00:00:00Z"
  }
]
"""


class TestCron:
    def test_detects_stale_output(self, tmp_path):
        jobs_file = tmp_path / "jobs.json"
        output_dir = tmp_path / "output"
        output_dir.mkdir()
        jobs_file.write_text(JOBS_STALE_OUTPUT)

        report = check_cron(jobs_file, output_dir)
        messages = [f.message for f in report.findings]
        assert any("stale" in m or "2020" in m for m in messages), f"Expected stale output finding, got: {messages}"

    def test_missing_script_flagged(self, tmp_path):
        jobs_file = tmp_path / "jobs.json"
        jobs_file.write_text(JOBS_MISSING_SCRIPT)

        report = check_cron(jobs_file)
        messages = [f.message for f in report.findings]
        assert any("script" in m.lower() for m in messages), f"Expected missing-script finding, got: {messages}"

    def test_disabled_jobs_not_flagged(self, tmp_path):
        jobs_file = tmp_path / "jobs.json"
        output_dir = tmp_path / "output"
        output_dir.mkdir()
        jobs_file.write_text(JOBS_STALE_OUTPUT)

        report = check_cron(jobs_file, output_dir)
        disabled_finding = [f for f in report.findings if "job-3" in f.message]
        assert len(disabled_finding) == 0, "Disabled job should not be flagged"

    def test_json_output_valid(self, tmp_path):
        import json

        jobs_file = tmp_path / "jobs.json"
        jobs_file.write_text(JOBS_MISSING_SCRIPT)
        report = check_cron(jobs_file)
        json.dumps([f.__dict__ for f in report.findings])  # must not raise