import pytest

from app.risk.position_sizing import ContractSpec, calculate_position_size


def test_position_size_respects_risk():
    spec = ContractSpec(0.0001, 10.0, 0.01, 100.0, 0.01)
    volume = calculate_position_size(10000, 0.5, 1.1000, 1.0950, spec)
    assert volume > 0
    risk = (abs(1.1000 - 1.0950) / spec.tick_size) * spec.tick_value * volume
    assert risk <= 50.0


def test_invalid_contract_is_rejected():
    with pytest.raises(ValueError):
        calculate_position_size(
            10000, 0.5, 1.1, 1.09,
            ContractSpec(0, 10, 0.01, 100, 0.01),
        )
