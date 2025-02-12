# LandX Report Bot

## 🚀 Installation and Setup

### Installation

1. Клонируйте репозиторий:
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
ADMIN_GROUP="your-admin-group-id"
MY_DEV="your-developer-id"
```

### Start bot
```bash
python tg/run_bot.py
```

### Add to dag
You need to add a script to the DAG python update_report.py that will run after all the data has been written to the metadata database.
```bash
python update_report.py
```
