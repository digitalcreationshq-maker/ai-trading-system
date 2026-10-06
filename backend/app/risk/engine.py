from .models import AccountSnapshot, RiskDecision, TradeRequest


class RiskEngine:
    """Independent safety gate. It may reject a trade, but never loosen a hard limit."""

    def __init__(
        self,
        *,
        risk_per_trade_pct: float = 0.5,
        absolute_risk_ceiling_pct: float = 1.0,
        daily_loss_limit_pct: float = 2.0,
        weekly_loss_limit_pct: float = 5.0,
        max_total_open_risk_pct: float = 2.0,
        max_correlated_exposure_pct: float = 1.0,
        consecutive_loss_pause: int = 3,
        max_trades_per_day: int = 5,
        max_trades_per_week: int = 20,
        min_setup_score: int = 70,
        min_autonomous_score: int = 80,
        absolute_min_rr: float = 1.5,
        max_staleness_seconds: int = 60,
        orders_enabled: bool = False,
        kill_switch: bool = True,
    ) -> None:
        self.risk_per_trade_pct = risk_per_trade_pct
        self.absolute_risk_ceiling_pct = absolute_risk_ceiling_pct
        self.daily_loss_limit_pct = daily_loss_limit_pct
        self.weekly_loss_limit_pct = weekly_loss_limit_pct
        self.max_total_open_risk_pct = max_total_open_risk_pct
        self.max_correlated_exposure_pct = max_correlated_exposure_pct
        self.consecutive_loss_pause = consecutive_loss_pause
        self.max_trades_per_day = max_trades_per_day
        self.max_trades_per_week = max_trades_per_week
        self.min_setup_score = min_setup_score
        self.min_autonomous_score = min_autonomous_score
        self.absolute_min_rr = absolute_min_rr
        self.max_staleness_seconds = max_staleness_seconds
        self.orders_enabled = orders_enabled
        self.kill_switch = kill_switch

    def evaluate(self, account: AccountSnapshot, trade: TradeRequest) -> RiskDecision:
        reasons: list[str] = []

        if self.kill_switch:
            reasons.append("KILL_SWITCH_ACTIVE")
        if not self.orders_enabled:
            reasons.append("ORDERS_DISABLED")

        if trade.risk_pct <= 0:
            reasons.append("INVALID_RISK")
        if trade.risk_pct > self.risk_per_trade_pct:
            reasons.append("RISK_ABOVE_CONFIGURED_DEFAULT")
        if trade.risk_pct > self.absolute_risk_ceiling_pct:
            reasons.append("RISK_ABOVE_ABSOLUTE_CEILING")

        if account.open_risk_pct + trade.risk_pct > self.max_total_open_risk_pct:
            reasons.append("TOTAL_OPEN_RISK_LIMIT")
        if account.correlated_exposure_pct + trade.correlated_risk_pct > self.max_correlated_exposure_pct:
            reasons.append("CORRELATED_EXPOSURE_LIMIT")

        if account.trades_today >= self.max_trades_per_day:
            reasons.append("DAILY_TRADE_LIMIT")
        if account.trades_this_week >= self.max_trades_per_week:
            reasons.append("WEEKLY_TRADE_LIMIT")
        if account.consecutive_losses >= self.consecutive_loss_pause:
            reasons.append("CONSECUTIVE_LOSS_PAUSE")

        daily_loss_pct = max(0.0, (account.daily_start_equity - account.equity) / account.daily_start_equity * 100)
        weekly_loss_pct = max(0.0, (account.weekly_start_equity - account.equity) / account.weekly_start_equity * 100)
        drawdown_pct = max(0.0, (account.high_water_mark - account.equity) / account.high_water_mark * 100)

        if daily_loss_pct >= self.daily_loss_limit_pct:
            reasons.append("DAILY_LOSS_LIMIT")
        if weekly_loss_pct >= self.weekly_loss_limit_pct:
            reasons.append("WEEKLY_LOSS_LIMIT")
        if drawdown_pct >= 10.0:
            reasons.append("HIGH_WATER_MARK_DRAWDOWN_SUSPENSION")

        if trade.setup_score < self.min_setup_score:
            reasons.append("SETUP_SCORE_BELOW_THRESHOLD")
        if trade.autonomous and trade.setup_score < self.min_autonomous_score:
            reasons.append("AUTONOMOUS_SCORE_BELOW_THRESHOLD")

        risk_reward = self._risk_reward(trade)
        if risk_reward < self.absolute_min_rr:
            reasons.append("RISK_REWARD_BELOW_ABSOLUTE_FLOOR")

        age = (trade.now - trade.data_timestamp).total_seconds()
        if age < 0 or age > self.max_staleness_seconds:
            reasons.append("STALE_OR_FUTURE_DATA")

        if not trade.contract_verified:
            reasons.append("CONTRACT_UNVERIFIED")
        if not trade.position_size_valid:
            reasons.append("INVALID_POSITION_SIZE")
        if trade.estimated_margin > trade.available_margin:
            reasons.append("INSUFFICIENT_MARGIN")
        if not trade.idempotency_key:
            reasons.append("MISSING_IDEMPOTENCY_KEY")

        return RiskDecision(allowed=not reasons, reasons=tuple(reasons))

    @staticmethod
    def _risk_reward(trade: TradeRequest) -> float:
        risk = abs(trade.entry_price - trade.stop_loss)
        reward = abs(trade.take_profit - trade.entry_price)
        return reward / risk if risk > 0 else 0.0
