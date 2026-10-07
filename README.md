# AI Betting Intelligence v3

This version turns the tracker into a real local database application.

## Included
- SQLite database (`betting.db`)
- NBA, NFL, NHL, MLB, NCAAB, NCAAF, AFL, Soccer, Tennis, Horses, Greyhounds
- Sport-specific bet types and factor prompts
- Bet logging with reasoning, odds, closing odds, stake and CLV
- Post-game/post-race result entry
- Automatic OpenAI post-event process review when `OPENAI_API_KEY` is configured
- Performance by bet type, ROI, P&L and CLV
- Odds snapshot table
- CSV import for external odds feeds
- Source layer ready for authorized odds/stat APIs

## Important Sportsbet note
Sportsbet does not provide a generic public API that this package can safely assume access to. This app therefore does NOT scrape or fake Sportsbet live data. It supports:
1. an authorized Sportsbet feed via `SPORTSBET_API_URL`/`SPORTSBET_API_KEY`, if you have one;
2. an odds provider that carries Sportsbet prices via `ODDS_API_KEY`;
3. CSV imports of Sportsbet snapshots.

The database stores the bookmaker as Sportsbet and preserves the exact odds/closing price you enter/import.

## Run
pip install -r requirements.txt
streamlit run app.py

## Streamlit Cloud
Deploy `app.py` and `requirements.txt`. Add secrets:
OPENAI_API_KEY = "..."
ODDS_API_KEY = "..."
SPORTSBET_API_URL = "..."
SPORTSBET_API_KEY = "..."

An API endpoint must actually be authorized/available before the app can fetch it.

## Next production step
Add sport-specific API adapters that normalize:
- events
- players/runners
- statistics
- injuries/lineups
- racing form/sectionals
- bookmaker markets
- opening/current/closing prices

into the SQLite schema.
