from app.broker.discovery import AccountHealth, BrokerSymbolSpec, DiscoveryService


class FakeGateway:
    def account_health(self):
        return AccountHealth("TEST", "TOKENIZED-001", "USD", 10000, 10000, 0, 10000, True)

    def symbol_spec(self, symbol):
        return BrokerSymbolSpec(symbol, 5, 0.00001, 0.00001, 1.0, 0.01, 100, 0.01, 10, True)


def test_discovery_is_read_only():
    service = DiscoveryService(FakeGateway())
    assert service.discover_account().terminal_connected
    assert service.discover_symbol("EURUSD").trade_allowed


def test_invalid_contract_is_blocked():
    class BadGateway(FakeGateway):
        def symbol_spec(self, symbol):
            return BrokerSymbolSpec(symbol, 5, 0.00001, 0, 1.0, 0.01, 100, 0.01, 10, True)

    service = DiscoveryService(BadGateway())
    try:
        service.discover_symbol("EURUSD")
    except ValueError as exc:
        assert "INVALID_CONTRACT_SPEC" in str(exc)
    else:
        raise AssertionError("invalid contract was accepted")
