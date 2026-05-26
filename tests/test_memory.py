"""
Memory budget checker tests.
"""

from agent_doctor.memory import check_memory


class TestMemory:
    def test_detects_over_95_percent(self, tmp_path):
        # Create a file with 9600 chars (96% of 10000)
        filler = "x" * 9600
        mem_file = tmp_path / "memory.md"
        mem_file.write_text(filler)

        report, stats = check_memory(mem_file, limits=(10000, 5000))
        assert len(report.files) == 1
        assert report.files[0].severity == "error"
        assert "96.0%" in report.files[0].message

    def test_ok_under_80_percent(self, tmp_path):
        filler = "y" * 7000  # 70%
        mem_file = tmp_path / "memory.md"
        mem_file.write_text(filler)

        report, stats = check_memory(mem_file, limits=(10000, 5000))
        # no error/warning, only info at most
        assert not any(f.severity == "error" for f in report.files)
        assert not any(f.severity == "warning" for f in report.files)

    def test_user_file_over_95_percent(self, tmp_path):
        mem_file = tmp_path / "memory.md"
        user_file = tmp_path / "user.md"
        mem_file.write_text("a" * 1000)
        user_file.write_text("b" * 4900)  # 98% of 5000

        report, stats = check_memory(mem_file, user_file, limits=(10000, 5000))
        assert len(report.files) == 1
        assert "user" in report.files[0].file_path.lower()
        assert report.files[0].severity == "error"

    def test_stats_returned(self, tmp_path):
        mem_file = tmp_path / "memory.md"
        mem_file.write_text("z" * 5000)
        report, stats = check_memory(mem_file, limits=(10000, 5000))
        assert len(stats) == 1
        assert stats[0].char_count == 5000
        assert stats[0].pct == 50.0

    def test_json_output_valid(self, tmp_path):
        import json

        mem_file = tmp_path / "memory.md"
        mem_file.write_text("x" * 9600)
        report, stats = check_memory(mem_file, limits=(10000, 5000))
        json.dumps({"report": [f.__dict__ for f in report.files], "stats": [s.__dict__ for s in stats]})