from dataclasses import dataclass


@dataclass(frozen=True)
class ContractSpec:
    tick_size: float
    tick_value: float
    volume_min: float
    volume_max: float
    volume_step: float


def calculate_position_size(
    equity: float,
    permitted_risk_pct: float,
    entry_price: float,
    stop_price: float,
    contract: ContractSpec,
) -> float:
    if equity <= 0:
        raise ValueError("equity must be positive")
    if not 0 < permitted_risk_pct <= 100:
        raise ValueError("permitted_risk_pct must be between 0 and 100")
    if entry_price <= 0 or stop_price <= 0:
        raise ValueError("prices must be positive")
    if stop_price == entry_price:
        raise ValueError("stop distance must be non-zero")
    if contract.tick_size <= 0 or contract.tick_value <= 0:
        raise ValueError("invalid contract tick specification")
    if contract.volume_min <= 0 or contract.volume_step <= 0 or contract.volume_max < contract.volume_min:
        raise ValueError("invalid broker volume constraints")

    risk_cash = equity * permitted_risk_pct / 100.0
    stop_ticks = abs(entry_price - stop_price) / contract.tick_size
    risk_per_lot = stop_ticks * contract.tick_value
    if risk_per_lot <= 0:
        raise ValueError("invalid risk-per-lot calculation")

    raw_volume = risk_cash / risk_per_lot
    steps = int(raw_volume / contract.volume_step)
    volume = steps * contract.volume_step
    if volume < contract.volume_min:
        return 0.0
    return min(volume, contract.volume_max)
