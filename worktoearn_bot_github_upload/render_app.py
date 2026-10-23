import os
import sys
import threading
import logging
from flask import Flask

# Configure root logger
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR)

import tg_bot
import proof_manager_bot

app = Flask(__name__)

@app.route('/')
def home():
    return {
        "status": "online",
        "service": "WorkToEarn 24/7 Telegram Bots Hub",
        "bots": ["@trxmaabot", "@trxmangrbot"]
    }

@app.route('/healthz')
def health():
    return "OK", 200

def run_tg_bot():
    try:
        logging.info("[RENDER] Starting @trxmaabot...")
        tg_bot.main()
    except Exception as e:
        logging.error(f"[RENDER] Error in tg_bot: {e}")

def run_proof_bot():
    try:
        logging.info("[RENDER] Starting @trxmangrbot...")
        proof_manager_bot.main()
    except Exception as e:
        logging.error(f"[RENDER] Error in proof_manager_bot: {e}")

if __name__ == '__main__':
    # Start bot 1 in background thread
    t1 = threading.Thread(target=run_tg_bot, daemon=True)
    t1.start()

    # Start bot 2 in background thread
    t2 = threading.Thread(target=run_proof_bot, daemon=True)
    t2.start()

    # Start Flask Web Service on Render's assigned PORT
    port = int(os.environ.get("PORT", 10000))
    logging.info(f"[RENDER] Web health check server listening on port {port}...")
    app.run(host='0.0.0.0', port=port, debug=False)
