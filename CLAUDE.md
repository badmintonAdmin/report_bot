# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

Install deps and apply migrations to the local SQLite DB:

```bash
pip install -r requirements.txt
alembic upgrade head
```

Run the long-running Telegram bot (polling):

```bash
python tg/run_bot.py
```

Run the one-shot report jobs (intended to be triggered by an external Airflow DAG, **after** the upstream metadata DB has been refreshed):

```bash
python update_report.py   # builds the remote report, stores it in local DB, posts to the allowed group
python update_topup.py    # builds the top-up message from gsheets+contracts, stores it, posts it
```

Create a new Alembic migration:

```bash
alembic revision --autogenerate -m "message"
```

Format code (Black is pinned in `requirements.txt`):

```bash
black .
```

There is no test suite in this repo.

## Configuration

All configuration is read from a `.env` file at the project root by `general_config.Config`, which simply turns every `dotenv_values()` key into an attribute on `config`. Required keys are documented in `README.md` and include the remote Postgres connection (`DB_NAME`/`DB_USER`/`PASSWORD`/`HOST`/`PORT`), the local SQLite URL (`DATABASE_URL`, used by both `local_db/ldb.py` and `alembic/env.py`), Telegram (`TOKEN`, `ALLOWED_GROUP_ID`, `OWNER_ID`), an Infura-style `URL` for web3, and `SELL_CONTRACT`. `gsheets/google.json` (service-account credentials, gitignored) must also be present.

## Architecture

The system has **three data sources** that get fused into two Telegram messages (a daily report and a top-up reminder):

1. **Remote Postgres** (`db/`) — read-only analytics warehouse populated by an upstream pipeline. `db.database` is a module-level singleton wrapping `psycopg2`; `database.execute_query("foo.sql")` loads `db/sql/foo.sql`, executes it, and returns a pandas `DataFrame`. The set of SQL files driving the daily report is hardcoded in `report/get_data.py::get_all_data`.
2. **On-chain via web3** (`contracts/`) — `contracts.contract_data` holds singletons for the Arbitrum and Ethereum RPCs plus the LCG/AAVE/xToken/cToken/USDC contracts; ABIs live under `contracts/abi/`. `contracts/get_data.py` and `report/data/request_contract.py` are the call sites that compose web3 reads into rows.
3. **Google Sheets** (`gsheets/`) — `gspread`-based; `gsheets/template.py::all_format` is the entry point for the top-up message and stitches policies/pools/loans (from sheets) together with epoch info (from `contracts/get_data.py`).

The **local SQLite DB** (`local_db/`) is a separate, write-side store with its own SQLAlchemy async engine (`local_db/ldb.py`, singleton `ldb`). Models (`CommandModel`, `ReportModel`, `TopupModel`) inherit from `local_db/models/base.py::BaseModel`, and **`alembic/env.py` targets `BaseModel.metadata`** — when adding a new model, also import it in `local_db/models/__init__.py` so autogenerate sees it. This DB exists primarily so `/get_report` can return the most recent stored report without re-running the heavy SQL+web3 fan-out.

The **Telegram layer** (`tg/`) is built on `aiogram` v3:

- `tg/run_bot.py` → `LndxBot` (`tg/core/lndx_bot.py`) wraps a `BaseBot` and a `Dispatcher`, includes the top-level `router` from `tg/core/routers/__init__.py`, which fans out into `commands/` (slash commands) and `messages/` (free-text). New commands are added as new files under `tg/core/routers/commands/` and re-exported from that package's `__init__.py`.
- Every command handler is gated with the `IsAllowed` filter from `tg/core/access.py`, which only admits DMs from `OWNER_ID` or messages in `ALLOWED_GROUP_ID`.
- `tg/core/menu.py` registers the visible command list with BotFather at startup.

**One-shot scripts vs. the bot**: `update_report.py` / `update_topup.py` instantiate their own `LndxBot` instance purely to reuse `bot.send_message`, then explicitly close `bot.bot.session`. They are **not** invoked from inside the polling bot — they're external jobs that push into the chat. The bot itself only reads previously-stored data via `local_db.requests.get_report`.

**Report assembly** (`report/`): `report/run.py::get_remote_report` is the single entry point. It calls `report/get_data.py::get_all_data` to collect a list of pre-formatted row groups (SQL DataFrames + contract reads + AAVE/LCG composites), then `report/template.py::generate_report` joins them into the final string. To add a section to the daily report, add a SQL file under `db/sql/` (and include its stem in the `sql_queries` list in `report/get_data.py`) or a contract reader, write a transformer in `report/data/response.py`, append the result to `big_arr` in `get_all_data`, and render it in `report/template.py`.