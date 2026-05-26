"""
Skills schema validator tests.
"""

from agent_doctor.skills import check_skills


VALID_SKILL = """---
name: my-skill
description: Does something useful
version: "1.0"
author: team@example.com
tags:
  - automation
  - helper
---

# My Skill

Some description here.
"""

MISSING_NAME_SKILL = """---
description: Missing name field
---

# SKill
"""

MISSING_FRONTMATTER = """# No frontmatter

Just a description.
"""

BAD_YAML_SKILL = """---
name: bad-skill
description: [this is broken yaml: {bad
---

# SKill
"""


class TestSkills:
    def test_valid_skill_passes(self, tmp_path):
        skills_dir = tmp_path / "skills"
        skills_dir.mkdir()
        skill_file = skills_dir / "SKILL.md"
        skill_file.write_text(VALID_SKILL)

        report = check_skills(skills_dir)
        # No errors
        errors = [f for f in report.files if f.severity == "error"]
        assert len(errors) == 0
        assert report.skills_valid == 1

    def test_missing_frontmatter_flagged(self, tmp_path):
        skills_dir = tmp_path / "skills"
        skills_dir.mkdir()
        skill_file = skills_dir / "SKILL.md"
        skill_file.write_text(MISSING_FRONTMATTER)

        report = check_skills(skills_dir)
        errors = [f for f in report.files if f.severity == "error"]
        assert len(errors) == 1
        assert "frontmatter" in errors[0].message.lower()

    def test_missing_name_field_flagged(self, tmp_path):
        skills_dir = tmp_path / "skills"
        skills_dir.mkdir()
        skill_file = skills_dir / "SKILL.md"
        skill_file.write_text(MISSING_NAME_SKILL)

        report = check_skills(skills_dir)
        errors = [f for f in report.files if f.severity == "error"]
        assert len(errors) >= 1
        assert any("name" in e.message.lower() for e in errors)

    def test_bad_yaml_flagged(self, tmp_path):
        skills_dir = tmp_path / "skills"
        skills_dir.mkdir()
        skill_file = skills_dir / "SKILL.md"
        skill_file.write_text(BAD_YAML_SKILL)

        report = check_skills(skills_dir)
        errors = [f for f in report.files if f.severity == "error"]
        assert len(errors) >= 1

    def test_json_output_valid(self, tmp_path):
        import json

        skills_dir = tmp_path / "skills"
        skills_dir.mkdir()
        skill_file = skills_dir / "SKILL.md"
        skill_file.write_text(VALID_SKILL)
        report = check_skills(skills_dir)
        json.dumps([f.__dict__ for f in report.files])