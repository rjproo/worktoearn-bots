import os
import random
import time
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FONT_DIR = os.path.join(BASE_DIR, "fonts")

def get_font(name="calibrib.ttf", size=32):
    # Check local fonts directory first (Render / Linux compatible)
    local_path = os.path.join(FONT_DIR, name)
    if os.path.exists(local_path):
        try:
            return ImageFont.truetype(local_path, size)
        except Exception:
            pass
            
    # Check Windows Fonts
    win_path = os.path.join("C:/Windows/Fonts", name)
    if os.path.exists(win_path):
        try:
            return ImageFont.truetype(win_path, size)
        except Exception:
            pass

    # Fallback to any local font
    for f in ["arialbd.ttf", "arial.ttf", "calibri.ttf"]:
        p = os.path.join(FONT_DIR, f)
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, size)
            except Exception:
                pass

    return ImageFont.load_default()

# Varied color schemes for different accounts
THEMES = [
    # (Background, Card, Border, Accent Green/Color, Text Main, Text Dim)
    ((17, 20, 28), (27, 32, 44), (43, 50, 68), (14, 203, 129), (245, 247, 250), (140, 149, 168)), # Binance Pro Dark
    ((13, 17, 23), (22, 27, 34), (48, 54, 61), (46, 160, 67), (240, 246, 252), (139, 148, 158)),  # Tron Midnight
    ((18, 18, 20), (28, 28, 32), (48, 48, 56), (34, 197, 94), (255, 255, 255), (160, 160, 175)),  # TrustWallet Minimal
    ((15, 23, 42), (30, 41, 59), (51, 65, 85), (56, 189, 248), (248, 250, 252), (148, 163, 184)), # Cyber Slate
    ((20, 21, 26), (30, 32, 40), (50, 54, 68), (234, 88, 12), (245, 245, 245), (150, 155, 170)),  # Dark Orange
    ((24, 18, 36), (36, 28, 54), (58, 45, 85), (192, 132, 252), (250, 250, 255), (170, 160, 190)),# Deep Violet
]

def draw_status_bar(draw, width, text_color, accent_color):
    cur_time = datetime.now().strftime("%H:%M")
    draw.text((65, 36), cur_time, fill=text_color, font=get_font("arialbd.ttf", 26))

    sx = width - 180
    for i in range(4):
        h = 8 + (i * 5)
        bar_col = text_color if i < 3 else (100, 100, 100)
        draw.rectangle([sx + (i * 8), 58 - h, sx + (i * 8) + 5, 58], fill=bar_col)
    draw.text((width - 145, 38), "5G", fill=text_color, font=get_font("arialbd.ttf", 20))

    battery_pct = random.randint(62, 98)
    draw.rounded_rectangle([width - 105, 42, width - 60, 60], radius=4, outline=text_color, width=2)
    fill_w = int(37 * (battery_pct / 100))
    draw.rectangle([width - 102, 45, width - 102 + fill_w, 57], fill=accent_color)
    draw.rectangle([width - 58, 47, width - 56, 55], fill=text_color)

# ==============================================================
# POST 2 GRAPHICS (DSpay or Digital Shield APP)
# ==============================================================
def draw_post2_graphic(acc_id, topic, output_path):
    """
    POST 2: Daily Social Media Graphic (DSpay or Digital Shield APP)
    Human touch, realistic UI.
    """
    width, height = 1080, 1380
    theme = THEMES[(acc_id * 2) % len(THEMES)]
    bg_color, card_bg, card_border, accent, text_white, text_dim = theme

    img = Image.new('RGB', (width, height), bg_color)
    draw = ImageDraw.Draw(img)
    draw_status_bar(draw, width, text_white, accent)

    if topic == "DSpay":
        # Realistic POS / Merchant Checkout Screen
        draw.text((width//2, 120), "DSpay Merchant Checkout", fill=accent, font=get_font("arialbd.ttf", 36), anchor="mm")
        draw.text((width//2, 165), "Decentralized USDT Web3 Payment Terminal", fill=text_dim, font=get_font("calibri.ttf", 24), anchor="mm")

        # Amount card
        draw.rounded_rectangle([60, 220, width - 60, 470], radius=24, fill=card_bg, outline=card_border, width=1)
        draw.text((width//2, 275), "PAYMENT RECEIVED", fill=(16, 185, 129), font=get_font("arialbd.ttf", 26), anchor="mm")

        amounts = [15.00, 25.50, 40.00, 50.00, 75.00, 95.00, 120.00]
        usdt_amt = amounts[acc_id % len(amounts)]
        draw.text((width//2, 355), f"{usdt_amt:.2f} USDT", fill=text_white, font=get_font("arialbd.ttf", 66), anchor="mm")
        draw.text((width//2, 420), "Instant TRC-20 Blockchain Settlement", fill=accent, font=get_font("calibri.ttf", 24), anchor="mm")

        # Details
        draw.rounded_rectangle([60, 500, width - 60, 980], radius=20, fill=card_bg, outline=card_border, width=1)
        now_str = datetime.now().strftime("%d %b %Y, %H:%M UTC")
        items = [
            ("Payment Protocol", "DSpay Smart Contract v3"),
            ("Merchant ID", f"Web3 Merchant #{400 + acc_id}"),
            ("Order Reference", f"DSP-2026-{1200 + acc_id*11}"),
            ("Settlement Time", "0.8 seconds (Sub-second)"),
            ("Chargeback Risk", "0.00% (Decentralized)"),
            ("Timestamp", now_str),
            ("Payment Status", "COMPLETED")
        ]
        iy = 545
        for label, val in items:
            draw.text((95, iy), label, fill=text_dim, font=get_font("calibri.ttf", 26))
            val_col = (16, 185, 129) if val == "COMPLETED" else text_white
            draw.text((width - 95, iy), val, fill=val_col, font=get_font("arialbd.ttf", 26), anchor="ra")
            iy += 60

        # Footer
        draw.rounded_rectangle([60, 1010, width - 60, 1260], radius=20, fill=(20, 36, 48), outline=accent, width=1)
        draw.text((width//2, 1060), "ACCEPT USDT ANYWHERE WITH DSPAY", fill=accent, font=get_font("arialbd.ttf", 30), anchor="mm")
        draw.text((width//2, 1115), "Zero setup fees • Instant Tron finality • ds.pro", fill=text_white, font=get_font("calibri.ttf", 26), anchor="mm")
        draw.text((width//2, 1190), "#DSpay #USDT #CryptoPayment #Web3Payment", fill=text_dim, font=get_font("calibri.ttf", 24), anchor="mm")

    else:
        # Realistic Digital Shield APP Mobile Screen
        draw.text((95, 120), "Digital Shield", fill=text_white, font=get_font("arialbd.ttf", 38))
        draw.rounded_rectangle([width - 240, 100, width - 60, 145], radius=15, fill=(30, 41, 75), outline=accent, width=1)
        draw.text((width - 150, 122), "Vault: Active", fill=accent, font=get_font("calibri.ttf", 22), anchor="mm")

        # Balance Card
        draw.rounded_rectangle([60, 180, width - 60, 440], radius=24, fill=card_bg, outline=card_border, width=1)
        draw.text((95, 225), "Total Protected Balance", fill=text_dim, font=get_font("calibri.ttf", 26))
        bal = 1050.50 + (acc_id * 23.40)
        draw.text((95, 295), f"${bal:,.2f}", fill=text_white, font=get_font("arialbd.ttf", 58))
        draw.text((95, 370), "+5.62% past 24h (All Assets Safe)", fill=(16, 185, 129), font=get_font("arialbd.ttf", 26))

        # Assets
        draw.text((65, 480), "Assets Portfolio", fill=text_white, font=get_font("arialbd.ttf", 30))
        assets = [
            ("TRON (TRX)", f"{2100 + acc_id*35:,.2f} TRX", f"${(2100 + acc_id*35)*0.165:,.2f}", "+3.2%"),
            ("Tether (USDT)", "650.00 USDT", "$650.00", "0.0%"),
            ("Bitcoin (BTC)", "0.015 BTC", "$985.40", "+2.8%"),
            ("Ethereum (ETH)", "0.12 ETH", "$312.00", "+4.1%")
        ]
        ay = 530
        for coin, qty, val, change in assets:
            draw.rounded_rectangle([60, ay, width - 60, ay + 85], radius=16, fill=card_bg, outline=card_border, width=1)
            draw.text((95, ay + 20), coin, fill=text_white, font=get_font("arialbd.ttf", 26))
            draw.text((95, ay + 50), qty, fill=text_dim, font=get_font("calibri.ttf", 22))
            draw.text((width - 95, ay + 20), val, fill=text_white, font=get_font("arialbd.ttf", 26), anchor="ra")
            draw.text((width - 95, ay + 50), change, fill=(16, 185, 129), font=get_font("calibri.ttf", 22), anchor="ra")
            ay += 100

        # Features
        draw.rounded_rectangle([60, 960, width - 60, 1260], radius=20, fill=(20, 28, 48), outline=accent, width=1)
        draw.text((width//2, 1010), "DIGITAL SHIELD APP - SECURITY SUITE", fill=accent, font=get_font("arialbd.ttf", 28), anchor="mm")
        feats = [
            "✓ Biometric Local Private Key Encryption",
            "✓ Non-Custodial Multi-Chain Wallet",
            "✓ Web3 dApp Browser & Daily Task Portal",
            "✓ Official website: ds.pro"
        ]
        fy = 1055
        for f in feats:
            draw.text((100, fy), f, fill=text_white, font=get_font("calibri.ttf", 25))
            fy += 42

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    img.save(output_path, "JPEG", quality=95)
    return output_path

# ==============================================================
# POST 3 GRAPHICS (Work To Earn Referral Graphic)
# ==============================================================
def draw_post3_graphic(acc_id, ref_link, output_path):
    """
    POST 3: Work To Earn Referral Graphic
    Looks like an authentic Tron Wallet Payout Receipt or Routine Card.
    """
    width, height = 1080, 1380
    theme = THEMES[(acc_id * 3 + 1) % len(THEMES)]
    bg_color, card_bg, card_border, accent_green, text_white, text_dim = theme

    img = Image.new('RGB', (width, height), bg_color)
    draw = ImageDraw.Draw(img)
    draw_status_bar(draw, width, text_white, accent_green)

    # Top Bar
    draw.text((65, 105), "←", fill=text_white, font=get_font("arialbd.ttf", 36))
    draw.text((width//2, 115), "Work To Earn Payout", fill=text_white, font=get_font("arialbd.ttf", 32), anchor="mm")
    draw.text((width - 75, 105), "⋮", fill=text_white, font=get_font("arialbd.ttf", 36))
    draw.line([(50, 155), (width - 50, 155)], fill=card_border, width=1)

    # Payout Amount
    payout_seed = (acc_id * 13) % 7
    base_amounts = [2.40, 4.60, 6.80, 9.20, 12.00, 16.40, 22.00]
    trx_amt = base_amounts[payout_seed]

    center_y = 265
    draw.ellipse([width//2 - 46, center_y - 46, width//2 + 46, center_y + 46], fill=(22, 54, 40), outline=(16, 185, 129), width=3)
    cx = width // 2
    draw.line([(cx - 16, center_y), (cx - 4, center_y + 14)], fill=(16, 185, 129), width=5)
    draw.line([(cx - 4, center_y + 14), (cx + 20, center_y - 12)], fill=(16, 185, 129), width=5)

    draw.text((width//2, 345), "Reward Claim Confirmed", fill=(16, 185, 129), font=get_font("arialbd.ttf", 32), anchor="mm")
    draw.text((width//2, 420), f"+{trx_amt:.2f} TRX", fill=text_white, font=get_font("arialbd.ttf", 64), anchor="mm")
    usd_val = trx_amt * 0.165
    draw.text((width//2, 480), f"≈ ${usd_val:.2f} USD", fill=text_dim, font=get_font("calibri.ttf", 28), anchor="mm")

    # Info Box
    box_top = 540
    box_bottom = 980
    draw.rounded_rectangle([60, box_top, width - 60, box_bottom], radius=20, fill=card_bg, outline=card_border, width=1)

    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    tx_hash = f"c{acc_id*6:02x}9f{payout_seed*5:02x}2...82a{acc_id*4:02x}3"

    details = [
        ("Network", "TRON (TRC-20)"),
        ("Source Contract", "WorkToEarn Bounty Pool"),
        ("Confirmation Time", now_str),
        ("Transaction Hash", tx_hash),
        ("Status", f"Block #{693100 + acc_id*18} (Success)"),
        ("Gas Fee", "0.00 TRX (Sponsored)")
    ]

    ry = box_top + 45
    for label, val in details:
        draw.text((95, ry), label, fill=text_dim, font=get_font("calibri.ttf", 26))
        val_color = (16, 185, 129) if "Success" in val else text_white
        draw.text((width - 95, ry), val, fill=val_color, font=get_font("arialbd.ttf", 26), anchor="ra")
        ry += 65

    # Referral & TG Box
    ref_display = ref_link if ref_link else "https://worktoearnoecm.icanfly.cyou/"
    if "invite=" in ref_display:
        ref_code = ref_display.split("invite=")[-1]
    elif "ref=" in ref_display:
        ref_code = ref_display.split("ref=")[-1]
    else:
        ref_code = f"ACC_{acc_id:02d}"

    draw.rounded_rectangle([60, 1015, width - 60, 1260], radius=20, fill=(24, 36, 52), outline=(56, 189, 248), width=1)
    draw.text((width//2, 1060), "⚡ WORK TO EARN REFERRAL PROGRAM", fill=(56, 189, 248), font=get_font("arialbd.ttf", 28), anchor="mm")
    draw.text((width//2, 1105), f"Invite Code: {ref_code} | Min 2 TRX Cashout", fill=(255, 215, 0), font=get_font("arialbd.ttf", 26), anchor="mm")
    draw.text((width//2, 1155), f"{ref_display}", fill=text_white, font=get_font("calibri.ttf", 24), anchor="mm")
    draw.text((width//2, 1210), "Official Telegram: t.me/worktoearn_official", fill=text_dim, font=get_font("calibri.ttf", 22), anchor="mm")

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    img.save(output_path, "JPEG", quality=95)
    return output_path
