"""
Routing policy checker tests.
"""

import pytest

from agent_doctor.routing import _normalize_provider, check_routing, load_config

YAML_CONFIG = """
routes:
  - id: primary-chat
    type: standard
    provider: openai/gpt-4o
  - id: auxiliary-search
    type: auxiliary
    provider: openai/gpt-4o-mini
  - id: code-assistant
    type: standard
    provider: anthropic/claude-3-5-sonnet
"""
YAML_POLICY = """
routes:
  - id: primary-chat
    type: standard
    allowed_providers:
      - openai
      - anthropic
  - id: auxiliary-search
    type: auxiliary
    blocked_providers:
      - openai
      - anthropic
      - cohere
      - google
      - azure
  - id: code-assistant
    type: standard
    allowed_providers:
      - anthropic
"""


class TestRouting:
    def test_premium_auxiliary_route_flagged(self, tmp_path):
        config_file = tmp_path / "config.yaml"
        policy_file = tmp_path / "policy.yaml"
        config_file.write_text(YAML_CONFIG)
        policy_file.write_text(YAML_POLICY)

        report = check_routing(config_file, policy_file)
        messages = [f.message for f in report.findings]

        # auxiliary-search uses openai which should be blocked in auxiliary routes
        assert any("auxiliary" in m and "openai" in m.lower() for m in messages), (
            f"Expected premium-in-auxiliary warning, got: {messages}"
        )

    def test_load_yaml_config(self, tmp_path):
        f = tmp_path / "cfg.yaml"
        f.write_text("key: value\nlist:\n  - a\n  - b\n")
        cfg = load_config(f)
        assert cfg["key"] == "value"
        assert cfg["list"] == ["a", "b"]

    def test_load_json_config(self, tmp_path):
        f = tmp_path / "cfg.json"
        f.write_text('{"key": "value"}\n')
        cfg = load_config(f)
        assert cfg["key"] == "value"

    def test_normalize_provider(self):
        assert _normalize_provider("openai/gpt-4o") == "openai"
        assert _normalize_provider("anthropic/claude-3") == "anthropic"
        assert _normalize_provider("OPENAI") == "openai"
        assert _normalize_provider("azure-gpt-35") == "azure"

    def test_json_output_valid(self, tmp_path):
        import json

        config_file = tmp_path / "config.yaml"
        policy_file = tmp_path / "policy.yaml"
        config_file.write_text(YAML_CONFIG)
        policy_file.write_text(YAML_POLICY)

        report = check_routing(config_file, policy_file)
        json.dumps([f.to_dict() for f in report.findings])  # must not raise