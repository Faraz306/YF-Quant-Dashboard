import streamlit as st
import pandas as pd
import yfinance as yf  # Free, open cloud data loader

st.set_page_config(layout='wide')

symbol = st.text_input("Enter the symbol to backtest (e.g., EURUSD=X, BTC-USD, AAPL).")
name = st.text_input("Enter your name.")

if name and symbol:
    with st.spinner("Downloading historical market data from open web servers..."):
        try:
            # Downloads identical 1-minute high-resolution interval bars
            ticker = yf.Ticker(symbol)
            df_raw = ticker.history(period="5d", interval="1m")

            if not df_raw.empty:
                # Structure columns to match your original script layout perfectly
                real_data = df_raw.reset_index()
                real_data.rename(columns={
                    'Datetime': 'time',
                    'Open': 'open',
                    'High': 'high',
                    'Low': 'low',
                    'Close': 'close'
                }, inplace=True)


                # --- YOUR EXACT STRATEGY MATH RUNS UNTOUCHED BENEATH THIS LINE ---
                def deduplicate_events(events):
                    return {e['candle_index']: e for e in events}.values()


                # Let's write the FVG func!
                def bullFVG(df):
                    events = []
                    for i in range(1, len(df) - 1):
                        prev_high = df['high'].iloc[i - 1]
                        middle_candle = df.iloc[i]
                        next_low = df['low'].iloc[i + 1]
                        gap = next_low - prev_high

                        # NOTE: If testing standard FX pairs (like EURUSD), change 10.0 to 0.0001
                        if gap > 10.0:
                            events.append({'candle_index': i})
                    return deduplicate_events(events)


                def test_any_strategy(df, strategy_func):
                    """
                    YF App Universal Strategy Tester Engine v4.1 (With Live UI Validation)
                    Pass ANY historical asset DataFrame and ANY SMC/ICT strategy function.
                    Calculates authentic wins and losses based on realistic Stop Loss and Take Profit levels.
                    """
                    # --- TRANSMISSION & COMMISSION CONFIGURATION ---
                    lot_size = 0.10
                    comm_per_lot_rt = 0.65
                    trade_cost = lot_size * comm_per_lot_rt

                    # 1. Execute strategy function to locate potential structural setups
                    found_events = strategy_func(df)
                    wins, losses = 0, 0
                    total_profit = 0.0
                    total_loss = 0.0
                    total_commission = 0.0

                    # Capital Structure Parameters
                    starting_balance = 10000
                    risk_per_trade = 0.01  # Risk 1% of the account balance ($100) per trade
                    risk_reward_ratio = 2.0  # Standard 1:2 Risk-to-Reward ratio

                    # Automatically detect short/bear strategy from function name
                    strategy_name_lower = strategy_func.__name__.lower()
                    is_short_strategy = "sell" in strategy_name_lower or "bear" in strategy_name_lower or "low" in strategy_name_lower

                    # List to track individual trade details for spot-checking
                    trade_records = []

                    # 2. Process Trades across realistic market bars
                    for item in found_events:
                        idx = item['candle_index']

                        # Max hold time of 24 candles to prevent infinite loops, bounded by dataframe edge
                        max_hold_candles = min(24, len(df) - 1 - idx)
                        if max_hold_candles <= 0:
                            continue

                        total_commission += trade_cost
                        entry_price = df['close'].iloc[idx]

                        # Extract trade execution timestamp if available in your DataFrame index
                        if hasattr(df, 'index') and isinstance(df.index, pd.DatetimeIndex):
                            trade_time = df.index[idx].strftime('%Y-%m-%d %H:%M:%S')
                        else:
                            raw_ts = df['time'].iloc[idx] if 'time' in df.columns else idx
                            trade_time = pd.to_datetime(raw_ts, unit='s').strftime('%Y-%m-%d %H:%M:%S')

                        # --- DYNAMIC RISK BOUNDARIES ---
                        atr_fallback = entry_price * 0.002  # 0.2% price buffer
                        if is_short_strategy:
                            stop_loss = item.get('sl_price', entry_price + atr_fallback)
                            risk_pips = max(stop_loss - entry_price, 0.0001)
                            take_profit = entry_price - (risk_pips * risk_reward_ratio)
                        else:
                            stop_loss = item.get('sl_price', entry_price - atr_fallback)
                            risk_pips = max(entry_price - stop_loss, 0.0001)
                            take_profit = entry_price + (risk_pips * risk_reward_ratio)

                        trade_resolved = False
                        outcome = "Unknown"

                        # Scan forward bar-by-bar to see if SL or TP is struck first
                        for future_offset in range(1, max_hold_candles + 1):
                            current_idx = idx + future_offset
                            high_p = df['high'].iloc[current_idx]
                            low_p = df['low'].iloc[current_idx]

                            if is_short_strategy:
                                if high_p >= stop_loss:
                                    losses += 1
                                    total_loss += starting_balance * risk_per_trade
                                    trade_resolved = True
                                    outcome = "Loss (SL)"
                                    break
                                elif low_p <= take_profit:
                                    wins += 1
                                    total_profit += starting_balance * risk_per_trade * risk_reward_ratio
                                    trade_resolved = True
                                    outcome = "Win (TP)"
                                    break
                            else:
                                if low_p <= stop_loss:
                                    losses += 1
                                    total_loss += starting_balance * risk_per_trade
                                    trade_resolved = True
                                    outcome = "Loss (SL)"
                                    break
                                elif high_p >= take_profit:
                                    wins += 1
                                    total_profit += starting_balance * risk_per_trade * risk_reward_ratio
                                    trade_resolved = True
                                    outcome = "Win (TP)"
                                    break

                        # Time-horizon exit fallback if neither target nor stop is hit within the window
                        if not trade_resolved:
                            exit_price = df['close'].iloc[idx + max_hold_candles]
                            if is_short_strategy:
                                is_win = exit_price < entry_price
                            else:
                                is_win = exit_price > entry_price

                            if is_win:
                                wins += 1
                                total_profit += starting_balance * (abs(entry_price - exit_price) / risk_pips) * risk_per_trade
                                outcome = "Win (Time-out)"
                            else:
                                losses += 1
                                total_loss += starting_balance * (abs(entry_price - exit_price) / risk_pips) * risk_per_trade
                                outcome = "Loss (Time-out)"

                        # Save this trade's data into our logging array
                        trade_records.append({
                            "Time/Index": trade_time,
                            "Entry Price": round(entry_price, 5),
                            "Stop Loss": round(stop_loss, 5),
                            "Take Profit": round(take_profit, 5),
                            "Outcome": outcome
                        })

                    # 3. Calculate Portfolio Analytical Aggregates
                    total_trades = wins + losses
                    win_rate = (wins / total_trades * 100) if total_trades > 0 else 0
                    net_profit = (total_profit - total_loss) - total_commission

                    # 4. Streamlit Dashboard Live UI Rendering
                    st.write(f"### 📈 Results for Strategy: {strategy_func.__name__}")
                    if is_short_strategy:
                        st.info("ℹ️ System detected a **Short / Bearish** directional profile. Evaluation logic flipped.")
                    else:
                        st.success("ℹ️ System detected a **Long / Bullish** directional profile. Standard logic active.")

                    st.write(f"**Total Trades** : {total_trades} | "
                             f"**Win Rate**: {win_rate:.2f}% | "
                             f"**Net Profit**: ${net_profit:.2f}")

                    # FIXED: Writes entries using safe .write text lines inside the scope
                    with open("FILE.txt", "a") as f:
                        f.write(f"{total_trades}, {win_rate:.2f}, {net_profit:.2f}, {strategy_func.__name__},{name}\n")

                    # Display Last 10 Backtest Trades for Quick Validation
                    if trade_records:
                        st.write("#### 🔍 Recent Backtest Log (Use this to match your Demo account)")
                        recent_trades_df = pd.DataFrame(trade_records[-10:])
                        st.dataframe(recent_trades_df, use_container_width=True)


                # FIXED: The duplicate lines that were crashing out the script here have been deleted!
                test_any_strategy(real_data, bullFVG)

        except Exception as e:
            st.error(e)
