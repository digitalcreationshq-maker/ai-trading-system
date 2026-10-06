from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class BrokerSymbolSpec:
    symbol: str
    digits: int
    point: float
    tick_size: float
    tick_value: float
    volume_min: float
    volume_max: float
    volume_step: float
    stops_level_points: int
    trade_allowed: bool


@dataclass(frozen=True)
class AccountHealth:
    broker: str
    account_reference: str
    currency: str
    balance: float
    equity: float
    margin: float
    free_margin: float
    terminal_connected: bool


class ReadOnlyBrokerGateway(Protocol):
    def account_health(self) -> AccountHealth: ...
    def symbol_spec(self, symbol: str) -> BrokerSymbolSpec: ...


class DiscoveryService:
    """Read-only broker discovery boundary. No order methods exist here by design."""

    def __init__(self, gateway: ReadOnlyBrokerGateway) -> None:
        self.gateway = gateway

    def discover_account(self) -> AccountHealth:
        return self.gateway.account_health()

    def discover_symbol(self, symbol: str) -> BrokerSymbolSpec:
        spec = self.gateway.symbol_spec(symbol)
        if not spec.trade_allowed:
            raise ValueError(f"SYMBOL_NOT_TRADEABLE: {symbol}")
        if spec.tick_size <= 0 or spec.tick_value <= 0:
            raise ValueError(f"INVALID_CONTRACT_SPEC: {symbol}")
        if spec.volume_min <= 0 or spec.volume_step <= 0 or spec.volume_max < spec.volume_min:
            raise ValueError(f"INVALID_VOLUME_CONSTRAINTS: {symbol}")
        return spec
