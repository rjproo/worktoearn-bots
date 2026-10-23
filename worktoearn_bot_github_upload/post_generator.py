import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR)

from database import get_ref_link

# ==============================================================
# POST 1: OFFICIAL TEMPLATE (TRIMMED TO FIT FREE TWITTER 280 LIMIT)
# Strict text only - no photo!
# ==============================================================
POST1_TEMPLATE = """🔥 The Work To Earn Referral System is LIVE!
💰 1 Point = 1 TRX 💸
🚀 Withdraw with just 2 Points!
Earn TRX every time you complete tasks.
👇Join Work To Earn Now:
{ref_link}

#WorkToEarn #TRX #Web3 #Airdrop"""

# ==============================================================
# POST 2: DAILY SOCIAL MEDIA GRAPHIC (DSPAY / DIGITAL SHIELD APP)
# Must reach 20+ Views / Impressions
# ==============================================================
POST2_DSPAY_CAPTIONS = [
    """Digital payments are evolving with DSpay! 💳⚡
Accept instant USDT & crypto settlements with zero friction. Decentralized Web3 merchant payments are here.

Explore: https://ds.pro
#DSpay #USDT #CryptoPayment #Web3Payment""",

    """Fast & secure crypto payments powered by DSpay 🌐
Instant stablecoin checkout for merchants with sub-second TRC20 finality.

More info: https://ds.pro
#DSpay #CryptoPayment #Web3 #USDT #Fintech""",

    """Empowering businesses worldwide with DSpay Web3 payments! 🚀
Settle multi-chain payments & USDT with high speed & zero chargebacks.

Check: https://ds.pro
#DSpay #Web3Payment #CryptoPayment #USDT"""
]

POST2_APP_CAPTIONS = [
    """Take full control of your wealth with Digital Shield APP! 🛡️
Non-custodial, multi-chain security & biometric key protection.

Download & secure assets: https://ds.pro
#DigitalShield #DigitalShieldWallet #Crypto #Web3""",

    """Security meets simplicity with Digital Shield APP 🔐
Manage TRX, ETH & USDT in one decentralized wallet with 100% self-custody.

Learn more: https://ds.pro
#DigitalShield #CryptoWallet #Web3Security #Crypto""",

    """Experience next-level Web3 security with Digital Shield APP ⚡
Explore dApps safely, track portfolios & earn ecosystem rewards.

Get started: https://ds.pro
#DigitalShield #CryptoWallet #Web3 #Decentralized"""
]

# ==============================================================
# POST 3: WORK TO EARN REFERRAL GRAPHIC POST
# STRICTLY COMPACT (Under 230 chars) SO TWITTER NEVER SHOWS
# "Upgrade to Plus to write longer posts"!
# ==============================================================
POST3_CAPTIONS = [
    """Earn daily TRX on Work To Earn! 💎
1 Pt = 1 TRX (Min 2 TRX cashout).
Simple daily social tasks = Real crypto in wallet!

🔗 Join: {ref_link}
💬 Official TG: https://t.me/worktoearn_official

#WorkToEarn #TRX #Web3 #Airdrop""",

    """Daily TRX bounty is LIVE on Work To Earn 🚀
Complete quick missions & claim TRX straight to your Tron wallet!
Min cashout: Just 2 TRX.

👉 Join: {ref_link}
📢 Official TG: https://t.me/worktoearn_official

#WorkToEarn #TRX #Crypto #Web3""",

    """Claim free TRX daily with Work To Earn ⚡
1 Point = 1 TRX instant payout.
Complete easy daily tasks & earn real crypto!

Register here 👇
🔗 {ref_link}
📌 TG Community: https://t.me/worktoearn_official

#TRX #WorkToEarn #Web3Airdrop #Crypto"""
]

def generate_daily_pack(acc_id: int, custom_ref: str = None):
    ref_link = custom_ref if custom_ref else get_ref_link(acc_id)
    if not ref_link:
        ref_link = "https://worktoearnoecm.icanfly.cyou/"

    # Post 1
    p1_text = POST1_TEMPLATE.format(ref_link=ref_link)

    # Post 2
    is_dspay = (acc_id % 2 == 1)
    if is_dspay:
        topic = "DSpay"
        p2_text = POST2_DSPAY_CAPTIONS[acc_id % len(POST2_DSPAY_CAPTIONS)]
    else:
        topic = "Digital Shield APP"
        p2_text = POST2_APP_CAPTIONS[acc_id % len(POST2_APP_CAPTIONS)]

    # Post 3 (Short & safe for Twitter free tier)
    p3_text = POST3_CAPTIONS[acc_id % len(POST3_CAPTIONS)].format(ref_link=ref_link)

    return {
        "acc_id": acc_id,
        "ref_link": ref_link,
        "is_custom_link": bool(get_ref_link(acc_id)),
        "post1": {
            "title": "POST 1: X (Twitter) Referral Promotion",
            "needs_photo": False,
            "text": p1_text
        },
        "post2": {
            "title": "POST 2: Daily Social Media Graphic Task",
            "topic": topic,
            "needs_photo": True,
            "needs_20_views": True,
            "text": p2_text
        },
        "post3": {
            "title": "POST 3: Referral Graphic Post (Work To Earn)",
            "topic": "Work To Earn Referral",
            "needs_photo": True,
            "needs_20_views": False,
            "text": p3_text
        }
    }
