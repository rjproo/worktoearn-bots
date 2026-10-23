import os
import sys
import subprocess
import logging
from flask import Flask

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

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

if __name__ == '__main__':
    logging.info("[RENDER] Launching @trxmaabot independent process...")
    p1 = subprocess.Popen([sys.executable, os.path.join(BASE_DIR, "tg_bot.py")])

    logging.info("[RENDER] Launching @trxmangrbot independent process...")
    p2 = subprocess.Popen([sys.executable, os.path.join(BASE_DIR, "proof_manager_bot.py")])

    port = int(os.environ.get("PORT", 10000))
    logging.info(f"[RENDER] Web health check server listening on port {port}...")
    app.run(host='0.0.0.0', port=port, debug=False)
