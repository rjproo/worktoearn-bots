import os
import sys
import logging
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

if sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR)

from database import init_db, save_ref_link, get_ref_link, get_all_accounts, bulk_save_links
from realistic_graphics import draw_post2_graphic, draw_post3_graphic
from post_generator import generate_daily_pack

BOT_TOKEN = "8843768830:AAHEcbDHPtMtoa5n4pWKEKKJZOi9H4pWMuM"

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

OUTPUT_DIR = os.path.join(BASE_DIR, "output_daily_posts")
os.makedirs(OUTPUT_DIR, exist_ok=True)

def get_main_keyboard():
    keyboard = [
        [KeyboardButton("⚡ Generate Post")],
        [KeyboardButton("📥 Bulk Add Refer Links"), KeyboardButton("📋 My Saved Accounts")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    msg = (
        "👑 *Work To Earn - 50 Accounts Mission Bot*\n\n"
        "Bhai, ye bot teeno posts bilkul sahi sequence (1, 2, 3) aur 100% human-touch real crypto mockups ke saath deta hai.\n\n"
        "👉 *Niche diye gaye buttons se shuru karo:*"
    )
    await update.message.reply_text(msg, parse_mode="Markdown", reply_markup=get_main_keyboard())

async def deliver_account_posts(chat_id, acc_id, context: ContextTypes.DEFAULT_TYPE, custom_ref=None):
    pack = generate_daily_pack(acc_id, custom_ref=custom_ref)
    ref_link = pack["ref_link"]

    acc_dir = os.path.join(OUTPUT_DIR, f"Account_{acc_id:02d}")
    os.makedirs(acc_dir, exist_ok=True)

    # Images
    p2_img = os.path.join(acc_dir, f"Post2_{pack['post2']['topic'].replace(' ', '_')}_Acc{acc_id:02d}.jpg")
    draw_post2_graphic(acc_id, pack['post2']['topic'], p2_img)

    p3_img = os.path.join(acc_dir, f"Post3_Referral_Acc{acc_id:02d}.jpg")
    draw_post3_graphic(acc_id, ref_link, p3_img)

    # Navigation buttons
    prev_id = 50 if acc_id == 1 else acc_id - 1
    next_id = 1 if acc_id == 50 else acc_id + 1
    nav_kb = InlineKeyboardMarkup([
        [
            InlineKeyboardButton(f"⬅️ Acc {prev_id:02d}", callback_data=f"gen_{prev_id}"),
            InlineKeyboardButton(f"Acc {next_id:02d} ➡️", callback_data=f"gen_{next_id}")
        ],
        [
            InlineKeyboardButton(f"✏️ Edit Link for Acc {acc_id}", callback_data=f"editlink_{acc_id}")
        ]
    ])

    # Header
    link_info = f"`{ref_link}`" if pack["is_custom_link"] else "⚠️ `Default Link`"
    await context.bot.send_message(
        chat_id=chat_id,
        text=f"══════════════════════\n📱 *ACCOUNT {acc_id:02d} / 50 DAILY POSTS*\n🔗 Ref Link: {link_info}\n══════════════════════",
        parse_mode="Markdown"
    )

    # ==============================================================
    # 1. POST 1: X REFERRAL PROMOTION (STRICT TEXT ONLY - NO PHOTO)
    # ==============================================================
    p1_msg = (
        f"1️⃣ *[POST 1: X Referral Promotion]* (+0.20 TRX)\n"
        f"🚫 *STRICT RULE: PHOTO NAHI LAGANI! (TEXT ONLY)*\n"
        f"❌ *Views:* Views ki koi limit nahi hai!\n\n"
        f"👇 *Niche diye text par 1-Tap karke direct Copy karo:*\n"
        f"```\n{pack['post1']['text']}\n```\n\n"
        f"📋 *Proof:* Post Screenshot + Post Link + Profile Screenshot"
    )
    await context.bot.send_message(chat_id=chat_id, text=p1_msg, parse_mode="Markdown")

    # ==============================================================
    # 2. POST 2: DAILY SOCIAL MEDIA GRAPHIC (DSPAY / APP - 20 VIEWS)
    # ==============================================================
    p2_caption = (
        f"2️⃣ *[POST 2: Daily Social Media Graphic - {pack['post2']['topic']}]* (+0.20 TRX)\n"
        f"⚠️ *CRITICAL: 20+ VIEWS / IMPRESSIONS COMPULSORY!*\n"
        f"👉 Post karne ke baad jab 20 views ho jayein, tabhi views data ka screenshot lena!\n\n"
        f"👇 *Niche diye Caption par 1-Tap karke direct Copy karo:*\n"
        f"```\n{pack['post2']['text']}\n```\n\n"
        f"📋 *Proof:* Post Screenshot + Post Link + Profile Screenshot + 20+ Views Screenshot"
    )
    with open(p2_img, "rb") as photo:
        await context.bot.send_photo(chat_id=chat_id, photo=photo, caption=p2_caption, parse_mode="Markdown")

    # ==============================================================
    # 3. POST 3: REFERRAL GRAPHIC POST (WORK TO EARN)
    # ==============================================================
    p3_caption = (
        f"3️⃣ *[POST 3: Referral Graphic Post - Work To Earn]* (+0.20 TRX)\n"
        f"🟢 *Rule:* Ye Photo upload karo + Niche ka caption copy karo.\n"
        f"❌ *Views:* Views ki koi limit nahi hai!\n\n"
        f"👇 *Niche diye Caption par 1-Tap karke direct Copy karo:*\n"
        f"```\n{pack['post3']['text']}\n```\n\n"
        f"📋 *Proof:* Post Screenshot + Post Link + Profile Screenshot"
    )
    with open(p3_img, "rb") as photo:
        await context.bot.send_photo(chat_id=chat_id, photo=photo, caption=p3_caption, parse_mode="Markdown", reply_markup=nav_kb)

async def message_router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip() if update.message.text else ""
    chat_id = update.message.chat_id
    state = context.user_data.get("state")
    logging.info(f"[MSG RECEIVED] Chat: {chat_id} | Text: '{text}' | State: {state}")

    # Button: ⚡ Generate Post
    if text == "⚡ Generate Post":
        context.user_data["state"] = "AWAITING_ACCOUNT_NUM"
        await update.message.reply_text(
            "👉 *Kis account number ke liye post chahiye?*\n\n"
            "1 se 50 ke beech koi bhi number bhejo (jaise: `1`, `5`, ya `23`):",
            parse_mode="Markdown"
        )
        return

    # Button: 📥 Bulk Add Refer Links
    elif text == "📥 Bulk Add Refer Links":
        context.user_data["state"] = "AWAITING_BULK_LINKS"
        instructions = (
            "📥 *Bulk Referral Links Add Karne Ka Tarika:*\n\n"
            "Aap ek saath 50 accounts ke links yahan paste kar sakte hain.\n\n"
            "*Format 1:*\n"
            "`1 = https://worktoearnoecm.icanfly.cyou/?ref=LINK1`\n"
            "`2 = https://worktoearnoecm.icanfly.cyou/?ref=LINK2`\n\n"
            "*Format 2 (Direct List):*\n"
            "Line-by-line bas links paste kar do (Line 1 = Acc 1, Line 2 = Acc 2...)\n\n"
            "👉 *Abhi apne links paste karke send karo:*"
        )
        await update.message.reply_text(instructions, parse_mode="Markdown")
        return

    # Button: 📋 My Saved Accounts
    elif text == "📋 My Saved Accounts":
        accounts = get_all_accounts()
        saved = [a for a in accounts if a["ref_link"]]
        summary = (
            f"📊 *Saved Accounts Status*\n\n"
            f"• Total Saved: *{len(saved)} / 50*\n"
            f"• Pending: *{50 - len(saved)}*\n\n"
        )
        if saved:
            summary += "*Saved Links Sample:*\n"
            for a in saved[:8]:
                summary += f"• Acc {a['account_id']:02d}: `{a['ref_link']}`\n"
            if len(saved) > 8:
                summary += f"_...aur {len(saved) - 8} accounts configured hain._\n"
        else:
            summary += "Abhi koi link save nahi hai. '📥 Bulk Add Refer Links' se ek baar me add kar sakte ho!"

        await update.message.reply_text(summary, parse_mode="Markdown")
        return

    # State: AWAITING_ACCOUNT_NUM
    if state == "AWAITING_ACCOUNT_NUM":
        if text.isdigit() and 1 <= int(text) <= 50:
            acc_id = int(text)
            context.user_data["target_acc_id"] = acc_id
            saved_link = get_ref_link(acc_id)

            if saved_link:
                context.user_data["state"] = None
                await update.message.reply_text(
                    f"⚡ *Account {acc_id:02d}* ka saved referral link mil gaya: `{saved_link}`\nGenerating posts...",
                    parse_mode="Markdown"
                )
                await deliver_account_posts(chat_id, acc_id, context, custom_ref=saved_link)
            else:
                context.user_data["state"] = "AWAITING_SINGLE_LINK"
                skip_kb = InlineKeyboardMarkup([
                    [InlineKeyboardButton("⏩ Bina Link Ke Banao (Skip)", callback_data=f"skip_{acc_id}")]
                ])
                await update.message.reply_text(
                    f"⚠️ *Account {acc_id:02d}* ka referral link database me save nahi hai!\n\n"
                    f"1️⃣ Apna referral link yahan bhejo (save ho jayega aur post ban jayegi), ya\n"
                    f"2️⃣ Agar abhi bina referral link ke chahiye toh **'skip'** likho ya niche button dabao 👇",
                    parse_mode="Markdown",
                    reply_markup=skip_kb
                )
            return
        else:
            await update.message.reply_text("Bhai 1 se 50 ke beech valid number bhejo (jaise: `1` ya `15`).")
            return

    # State: AWAITING_SINGLE_LINK
    if state == "AWAITING_SINGLE_LINK":
        acc_id = context.user_data.get("target_acc_id", 1)
        if text.lower() == "skip":
            context.user_data["state"] = None
            await update.message.reply_text(f"Generating posts for *Account {acc_id:02d}* (without saved link)...", parse_mode="Markdown")
            await deliver_account_posts(chat_id, acc_id, context, custom_ref=None)
            return

        if "http" in text:
            link = text.strip()
            save_ref_link(acc_id, link)
            context.user_data["state"] = None
            await update.message.reply_text(
                f"✅ *Account {acc_id:02d}* ka referral link database me save ho gaya!\nAb daily isi link se posts banengi. Generating posts now...",
                parse_mode="Markdown"
            )
            await deliver_account_posts(chat_id, acc_id, context, custom_ref=link)
            return
        else:
            await update.message.reply_text("Kripya valid link bhejo (jo https se shuru ho) ya 'skip' likho.")
            return

    # State: AWAITING_BULK_LINKS
    if state == "AWAITING_BULK_LINKS":
        count, results = bulk_save_links(text)
        context.user_data["state"] = None
        if count > 0:
            await update.message.reply_text(
                f"🎉 *Success! Total {count} Accounts ke Referral Links database me save ho gaye!*\n\n"
                f"Ab jab bhi aap kisi bhi account ki post generate karoge, uska link automatic post me lag kar aayega.",
                parse_mode="Markdown",
                reply_markup=get_main_keyboard()
            )
        else:
            await update.message.reply_text(
                "❌ Links format samajh nahi aaya bhai. Dubara try karo ya `/start` dabao.",
                reply_markup=get_main_keyboard()
            )
        return

    # Fallback: user typed number directly
    if text.isdigit() and 1 <= int(text) <= 50:
        acc_id = int(text)
        saved_link = get_ref_link(acc_id)
        if saved_link:
            await deliver_account_posts(chat_id, acc_id, context, custom_ref=saved_link)
        else:
            context.user_data["target_acc_id"] = acc_id
            context.user_data["state"] = "AWAITING_SINGLE_LINK"
            skip_kb = InlineKeyboardMarkup([
                [InlineKeyboardButton("⏩ Bina Link Ke Banao (Skip)", callback_data=f"skip_{acc_id}")]
            ])
            await update.message.reply_text(
                f"⚠️ *Account {acc_id:02d}* ka referral link database me save nahi hai!\n\n"
                f"1️⃣ Apna referral link yahan bhejo (save ho jayega aur post ban jayegi), ya\n"
                f"2️⃣ Agar abhi bina link ke chahiye toh **'skip'** likho ya niche button dabao 👇",
                parse_mode="Markdown",
                reply_markup=skip_kb
            )
        return

    await update.message.reply_text(
        "Niche diye gaye buttons se select karein ya account number bhejo bhai 👇",
        reply_markup=get_main_keyboard()
    )

async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    chat_id = query.message.chat_id

    if data.startswith("gen_"):
        acc_id = int(data.split("_")[1])
        saved_link = get_ref_link(acc_id)
        await deliver_account_posts(chat_id, acc_id, context, custom_ref=saved_link)

    elif data.startswith("skip_"):
        acc_id = int(data.split("_")[1])
        context.user_data["state"] = None
        await deliver_account_posts(chat_id, acc_id, context, custom_ref=None)

    elif data.startswith("editlink_"):
        acc_id = int(data.split("_")[1])
        context.user_data["target_acc_id"] = acc_id
        context.user_data["state"] = "AWAITING_SINGLE_LINK"
        await query.message.reply_text(
            f"✏️ *Account {acc_id:02d}* ke liye naya referral link bhejo:\n(Ya purana rakhne ke liye 'skip' likho)",
            parse_mode="Markdown"
        )

def main():
    print("[+] Initializing database...")
    init_db()
    print("[+] Starting Telegram Bot @trxmaabot ...")
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("menu", start_command))
    app.add_handler(CallbackQueryHandler(callback_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_router))

    app.run_polling()

if __name__ == '__main__':
    main()
