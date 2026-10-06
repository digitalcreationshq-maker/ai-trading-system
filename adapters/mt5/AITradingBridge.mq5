#property version   "0.1.0"
#property description "AI Trading System MT5 bridge - safe/research mode only."

input bool EnableExecution = false;

int OnInit()
{
   Print("AI Trading System MT5 bridge initialized. Execution=", EnableExecution);
   Print("SAFE MODE: this build does not submit broker orders.");
   return(INIT_SUCCEEDED);
}

void OnTick()
{
   // Initial phase: heartbeat/read-only boundary only.
   // No CTrade/order-send execution is permitted in this build.
   static datetime last_heartbeat = 0;
   datetime now = TimeCurrent();

   if(now - last_heartbeat >= 60)
   {
      last_heartbeat = now;
      Print("AI Trading System MT5 heartbeat | login=", AccountInfoInteger(ACCOUNT_LOGIN),
            " | server=", AccountInfoString(ACCOUNT_SERVER),
            " | trade_allowed=", (bool)AccountInfoInteger(ACCOUNT_TRADE_ALLOWED));
   }
}

void OnDeinit(const int reason)
{
   Print("AI Trading System MT5 bridge stopped. reason=", reason);
}
