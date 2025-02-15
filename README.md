# Report Bot

## 🚀 Installation and Setup

### Installation

1. Clone the repository:
```bash
https://github.com/badmintonAdmin/report_bot.git
cd report_bot
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## ⚙️ Config

Create a .env file in the project root directory with the following parameters:

```env
# API and URL 
URL="your-api-url"
SELL_CONTRACT="your-contract-address"

# BD
DB_NAME="your-database-name"
DB_USER="your-database-user"
PASSWORD="your-database-password"
HOST="your-database-host"
PORT="your-database-port"

# Telegram params
TOKEN="your-telegram-bot-token"
ALLOWED_GROUP_ID="your-admin-group-id"
OWNER_ID="your-developer-id"
```
### Add credentials
add json to folder gsheets/google.json
This is a special file with access to a Google spreadsheet.

### Start bot
The bot should simply start and run in the background, listening for events and executing commands, without being added to Apache Airflow or creating a DAG. On successful startup, the terminal should display the message Bot running.....
```bash
python tg/run_bot.py
```

### Add to dag
You need to add a script to the DAG python update_report.py that will run after all the data has been written to the metadata database.
```bash
python update_report.py
```
```bash
python update_topup.py
```
