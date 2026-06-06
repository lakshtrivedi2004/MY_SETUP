# Alpha Trading Ecosystem v2.1

A collection of independent Python scripts for testing a 9-period EMA crossover
strategy, fetching market data, checking Dhan API credentials, and placing
orders through Dhan.

> **Risk warning:** Some scripts in this repository place real orders. Review
> the instrument, quantity, price, product type, and API credentials before
> running any live-trading script. Use `paper_trading_bot.py` first.

## Project Files

| File | Purpose | Places real orders? |
| --- | --- | --- |
| `paper_trading_bot.py` | Runs the strategy with BTC-USD data and simulated orders | No |
| `bot.py` | Tests Dhan authentication and displays the available margin | No |
| `fetch_data.py` | Fetches the current day's 1-minute HDFC Bank data from Dhan | No |
| `alpha_bot.py` | Trades HDFC Bank using the EMA crossover strategy | **Yes** |
| `place_order.py` | Interactively submits a Tata Motors bracket order | **Yes** |
| `place_amo.py` | Submits a hardcoded Tata Motors after-market limit order | **Yes** |

Each script runs independently. Running one script does not automatically start
the others.

## Requirements

- Python 3
- Internet access
- A Dhan account and API credentials for scripts that use Dhan

## Installation

1. Create and activate a virtual environment:

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

2. Install the dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Create a `.env` file in the project directory:

   ```env
   DHAN_CLIENT_ID=your_client_id
   DHAN_ACCESS_TOKEN=your_access_token
   ```

4. Keep `.env` private. Do not commit or share API credentials.

The paper-trading script uses Yahoo Finance and does not require Dhan
credentials.

## Recommended First Run

Start with paper trading:

```bash
python3 paper_trading_bot.py
```

The script:

- Reads 1-minute BTC-USD market data from Yahoo Finance.
- Detects a 9-period EMA bullish crossover.
- Simulates entries and exits without sending orders.
- Uses a fixed `$50` risk distance per trade.
- Moves the simulated stop to breakeven at `1R`.
- Exits at a `2R` target or the active stop.
- Stops after three entries in the current process.

Press `Ctrl+C` to stop it.

## Dhan Connection Test

Verify the credentials before using any live-order script:

```bash
python3 bot.py
```

This calls the Dhan fund-limits endpoint and prints the available margin when
authentication succeeds.

## Fetch Intraday Data

```bash
python3 fetch_data.py
```

This requests the current day's 1-minute intraday data for HDFC Bank
(`security_id: 1333`) and prints the latest rows as a pandas DataFrame. It may
return no data when Dhan has no intraday records for the current date, such as
on a market holiday.

## Live Trading Bot

```bash
python3 alpha_bot.py
```

Current configuration:

- Instrument: HDFC Bank (`HDFCBANK.NS`, Dhan security ID `1333`)
- Exchange segment: NSE equity
- Product type: intraday
- Order type: market
- Quantity: 1
- Signal: bullish 9-period EMA crossover
- Risk distance: INR 5 per share
- Target: `2R`
- Breakeven adjustment: `1R`
- Entry limit: three entries per process
- Scan interval: approximately 30 seconds

The market signal comes from Yahoo Finance, while orders are sent to Dhan.
Stops and targets are monitored by the Python process and are not submitted as
broker-side protective orders. The script and network connection must remain
active for those exits to be sent.

## Manual Bracket Order

```bash
python3 place_order.py
```

The script prompts for quantity, entry price, target input, and stop-loss input,
then submits a Tata Motors order (`security_id: 3456`) using Dhan's bracket
order product. Confirm the expected bracket-order parameter format with the
installed Dhan SDK before placing a live order.

## After-Market Order

```bash
python3 place_amo.py
```

This script immediately attempts to submit the following hardcoded live order:

- Tata Motors (`security_id: 3456`)
- Buy quantity: 1
- Limit price: INR 900
- Product type: intraday
- After-market timing: open

Edit and review the payload in `place_amo.py` before running it. A successful
run creates a real pending order that must be managed in Dhan.

## Strategy Summary

The automated bots calculate a 9-period exponential moving average. A buy
signal occurs when:

1. The earlier closed candle is at or below its 9 EMA.
2. The latest closed candle finishes above its 9 EMA.

After entry, the bots use a fixed price-distance risk model. At `1R`, the
tracked stop moves to the entry price. At `2R`, the bot attempts to exit for a
profit.

## Important Limitations

- The scripts use hardcoded instruments, quantities, and risk values.
- Runtime state is stored only in memory and is lost when a script stops.
- The trade counter does not persist or automatically reset while a process is
  running.
- The live bot does not reconcile its local position state with Dhan after a
  restart, rejection, partial fill, or manual order change.
- No strategy guarantees a profit. Test thoroughly before using real funds.
