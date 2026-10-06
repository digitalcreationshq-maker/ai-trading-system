import json
from pathlib import Path


def test_default_config_has_research_safety_state():
    config = json.loads(Path(__file__).parents[2].joinpath("config/default.json").read_text())
    assert config["system"]["mode"] == "research"
    assert config["execution"]["orders_enabled"] is False
    assert config["execution"]["kill_switch"] is True
    assert config["authorization"]["explicit_live_authorization"] is False
    assert config["risk"]["risk_per_trade_pct"] == 0.5
    assert config["risk"]["absolute_risk_ceiling_pct"] == 1.0
