import os
import sys
import logging
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

if sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR)

from proof_manager_db import (
    init_proof_db, save_topic_link, save_topic_screenshot,
    get_account_proofs, get_all_proofs_summary,
    reset_proofs_for_account, reset_all_proofs
)

BOT_TOKEN = "8912273447:AAFC-uYvvotFd6HPd2M0Z8g5aXqndABbrAg"

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

PROOFS_STORAGE_DIR = os.path.join(BASE_DIR, "proofs_storage")
os.makedirs(PROOFS_STORAGE_DIR, exist_ok=True)

TOPIC_NAMES = {
    1: "X Referral Promotion",
    2: "Social Media Graphic (20 Views)",
    3: "Referral Graphic Post"
}

def get_main_keyboard():
    keyboard = [
        [KeyboardButton("📤 Upload Proof (Link/SS)")],
        [KeyboardButton("📁 View Account Proofs"), KeyboardButton("📊 Today's Progress")],
        [KeyboardButton("🌐 Web Proof Hub Link"), KeyboardButton("🗑️ Reset Account Proofs")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    msg = (
        "🛡️ *Work To Earn - Proof & Link Manager Bot*\n\n"
        "Bhai, ye bot aapke sabhi 50 accounts ke **Post Links** aur **Screenshots** ko "
        "topic-wise organize karke rakhta hai taaki:\n"
        "1. Mobile gallery me 500+ screenshots download na karne padein.\n"
        "2. Kisi bhi account ka link aur photo kabhi mix na ho.\n\n"
        "👉 *Niche diye gaye buttons se shuru karein:*"
    )
    await update.message.reply_text(msg, parse_mode="Markdown", reply_markup=get_main_keyboard())

def make_topic_select_keyboard(acc_id):
    keyboard = [
        [InlineKeyboardButton("1️⃣ Topic 1: X Promo", callback_data=f"seltop_{acc_id}_1")],
        [InlineKeyboardButton("2️⃣ Topic 2: 20 Views Graphic", callback_data=f"seltop_{acc_id}_2")],
        [InlineKeyboardButton("3️⃣ Topic 3: Referral Graphic", callback_data=f"seltop_{acc_id}_3")],
        [InlineKeyboardButton("📋 View Status of Acc " + str(acc_id), callback_data=f"viewacc_{acc_id}")]
    ]
    return InlineKeyboardMarkup(keyboard)

async def send_account_summary_card(chat_id, acc_id, context: ContextTypes.DEFAULT_TYPE):
    proofs = get_account_proofs(acc_id)
    
    text = f"══════════════════════\n📁 *ACCOUNT {acc_id:02d} - PROOFS SUMMARY*\n══════════════════════\n\n"
    
    for row in proofs:
        top_id = row["topic_id"]
        top_name = TOPIC_NAMES.get(top_id, f"Topic {top_id}")
        
        link_icon = "✅" if row["post_link"] else "❌"
        link_str = f"`{row['post_link']}`" if row["post_link"] else "_No Link_"
        
        p_ss = "✅" if row["ss_post_path"] else "❌"
        pr_ss = "✅" if row["ss_profile_path"] else "❌"
        
        text += f"*{top_id}. {top_name}:*\n"
        text += f"• Link: {link_icon} {link_str}\n"
        text += f"• Post SS: {p_ss} | Profile SS: {pr_ss}"
        
        if top_id == 2:
            v_ss = "✅" if row["ss_views_path"] else "❌"
            text += f" | 20+ Views SS: {v_ss}\n\n"
        else:
            text += "\n\n"
            
    # Navigation & Action buttons
    prev_id = 50 if acc_id == 1 else acc_id - 1
    next_id = 1 if acc_id == 50 else acc_id + 1
    kb = [
        [
            InlineKeyboardButton("📤 Upload to Topic 1", callback_data=f"seltop_{acc_id}_1"),
            InlineKeyboardButton("📤 Upload to Topic 2", callback_data=f"seltop_{acc_id}_2")
        ],
        [
            InlineKeyboardButton("📤 Upload to Topic 3", callback_data=f"seltop_{acc_id}_3"),
            InlineKeyboardButton("📸 Send All SS Here", callback_data=f"sendall_{acc_id}")
        ],
        [
            InlineKeyboardButton(f"⬅️ Acc {prev_id:02d}", callback_data=f"viewacc_{prev_id}"),
            InlineKeyboardButton(f"Acc {next_id:02d} ➡️", callback_data=f"viewacc_{next_id}")
        ]
    ]
    await context.bot.send_message(chat_id=chat_id, text=text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(kb))

async def message_router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip() if update.message.text else ""
    chat_id = update.message.chat_id
    state = context.user_data.get("state")

    # 1. Main Button: Upload Proof
    if text == "📤 Upload Proof (Link/SS)":
        context.user_data["state"] = "AWAITING_UPLOAD_ACC"
        await update.message.reply_text(
            "👉 *Kis account ke proofs upload karne hain?*\n\n"
            "1 se 50 ke beech koi bhi number bhejo (jaise: `1`, `7`, ya `25`):",
            parse_mode="Markdown"
        )
        return

    # 2. Main Button: View Account Proofs
    elif text == "📁 View Account Proofs":
        context.user_data["state"] = "AWAITING_VIEW_ACC"
        await update.message.reply_text(
            "👉 *Kis account ke proofs dekhne hain?*\n\n"
            "1 se 50 ke beech koi bhi number bhejo (jaise: `1` ya `10`):",
            parse_mode="Markdown"
        )
        return

    # 3. Main Button: Today's Progress
    elif text == "📊 Today's Progress":
        all_data = get_all_proofs_summary()
        completed = 0
        partial = 0
        
        for acc_id, topics in all_data.items():
            t1 = bool(topics[1].get("post_link") and topics[1].get("ss_post_path"))
            t2 = bool(topics[2].get("post_link") and topics[2].get("ss_views_path"))
            t3 = bool(topics[3].get("post_link") and topics[3].get("ss_post_path"))
            if t1 and t2 and t3:
                completed += 1
            elif t1 or t2 or t3:
                partial += 1

        prog_msg = (
            f"📊 *50 Accounts Work To Earn Progress:*\n\n"
            f"✅ *Fully Completed Accounts:* {completed} / 50\n"
            f"⏳ *Partially Done Accounts:* {partial} / 50\n"
            f"❌ *Pending Accounts:* {50 - completed - partial}\n\n"
            f"💡 Kisi bhi account ka detail dekhne ke liye '📁 View Account Proofs' dabayein."
        )
        await update.message.reply_text(prog_msg, parse_mode="Markdown")
        return

    # 4. Main Button: Web Proof Hub Link
    elif text == "🌐 Web Proof Hub Link":
        msg = (
            "🌐 *Web Proof & Link Hub:* [http://127.0.0.1:5001](http://127.0.0.1:5001)\n\n"
            "Is link ko apne browser me open karo. Wahan aap Account 1 se 50 ke sabhi links "
            "1-click me copy kar sakte ho aur screenshots directly drag/drop kar sakte ho!"
        )
        await update.message.reply_text(msg, parse_mode="Markdown")
        return

    # 5. Main Button: Reset Account Proofs
    elif text == "🗑️ Reset Account Proofs":
        context.user_data["state"] = "AWAITING_RESET_ACC"
        await update.message.reply_text(
            "⚠️ *Kis account ke proofs reset karne hain?*\n"
            "Account number bhejo (1-50), ya sabhi 50 accounts reset karne ke liye 'ALL' likho:",
            parse_mode="Markdown"
        )
        return

    # State: AWAITING_RESET_ACC
    if state == "AWAITING_RESET_ACC":
        context.user_data["state"] = None
        if text.upper() == "ALL":
            reset_all_proofs()
            await update.message.reply_text("🗑️ *Sabhi 50 accounts ke proofs successfully reset kar diye gaye!*", parse_mode="Markdown")
        elif text.isdigit() and 1 <= int(text) <= 50:
            reset_proofs_for_account(int(text))
            await update.message.reply_text(f"🗑️ *Account {int(text):02d} ke proofs reset ho gaye!*", parse_mode="Markdown")
        else:
            await update.message.reply_text("Action cancel ho gaya.")
        return

    # State: AWAITING_VIEW_ACC
    if state == "AWAITING_VIEW_ACC":
        if text.isdigit() and 1 <= int(text) <= 50:
            context.user_data["state"] = None
            await send_account_summary_card(chat_id, int(text), context)
        else:
            await update.message.reply_text("1 se 50 ke beech valid number bhejo bhai.")
        return

    # State: AWAITING_UPLOAD_ACC
    if state == "AWAITING_UPLOAD_ACC":
        if text.isdigit() and 1 <= int(text) <= 50:
            acc_id = int(text)
            context.user_data["active_acc_id"] = acc_id
            context.user_data["state"] = None
            await update.message.reply_text(
                f"📱 *Account {acc_id:02d} Selected!*\nKaunse topic ka proof upload karna hai? Niche choose karo 👇",
                parse_mode="Markdown",
                reply_markup=make_topic_select_keyboard(acc_id)
            )
        else:
            await update.message.reply_text("1 se 50 ke beech valid number bhejo bhai.")
        return

    # Active Upload Mode: User sends text (Link)
    active_acc = context.user_data.get("active_acc_id")
    active_top = context.user_data.get("active_topic_id")

    if active_acc and active_top:
        if "http" in text:
            # It's a post link!
            save_topic_link(active_acc, active_top, text.strip())
            await update.message.reply_text(
                f"✅ *Account {active_acc:02d} - Topic {active_top} Post Link Saved!*\n`{text.strip()}`\n\n"
                f"👉 Ab is topic ke screenshots (Photos) bhej do ya doosra topic select karo.",
                parse_mode="Markdown",
                reply_markup=make_topic_select_keyboard(active_acc)
            )
            return

    # Direct account number typed (e.g. user just types '5')
    if text.isdigit() and 1 <= int(text) <= 50:
        await send_account_summary_card(chat_id, int(text), context)
        return

    await update.message.reply_text(
        "Niche diye gaye buttons se choose karein ya account number bhejo bhai 👇",
        reply_markup=get_main_keyboard()
    )

async def photo_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    active_acc = context.user_data.get("active_acc_id")
    active_top = context.user_data.get("active_topic_id")

    if not active_acc or not active_top:
        await update.message.reply_text(
            "⚠️ Bhai pehle '📤 Upload Proof' button se account aur topic select karo, fir photo bhejo!",
            reply_markup=get_main_keyboard()
        )
        return

    photo = update.message.photo[-1]
    file_id = photo.file_id

    # Check which screenshot is missing
    proofs = get_account_proofs(active_acc)
    row = next((r for r in proofs if r["topic_id"] == active_top), {})

    ss_type = "post"
    ss_label = "Post Screenshot"

    if not row.get("ss_post_path"):
        ss_type = "post"
        ss_label = "1. Post Screenshot"
    elif not row.get("ss_profile_path"):
        ss_type = "profile"
        ss_label = "2. Profile Screenshot"
    elif active_top == 2 and not row.get("ss_views_path"):
        ss_type = "views"
        ss_label = "3. 20+ Views Screenshot"
    else:
        # Overwrite post SS
        ss_type = "post"
        ss_label = "1. Post Screenshot (Updated)"

    # Download photo to local storage
    acc_dir = os.path.join(PROOFS_STORAGE_DIR, f"Account_{active_acc:02d}", f"Topic_{active_top}")
    os.makedirs(acc_dir, exist_ok=True)
    local_path = os.path.join(acc_dir, f"{ss_type}.jpg")

    new_file = await context.bot.get_file(file_id)
    await new_file.download_to_drive(local_path)

    save_topic_screenshot(active_acc, active_top, ss_type, file_id, local_path)

    # Next missing check
    proofs_updated = get_account_proofs(active_acc)
    row_up = next((r for r in proofs_updated if r["topic_id"] == active_top), {})
    
    status_msg = f"📸 *{ss_label} Successfully Saved!*\nAccount: *{active_acc:02d}* | Topic: *{active_top} ({TOPIC_NAMES[active_top]})*\n\n"
    
    # Check if this topic is fully complete
    is_topic_complete = False
    if active_top == 2:
        is_topic_complete = bool(row_up.get("ss_post_path") and row_up.get("ss_profile_path") and row_up.get("ss_views_path"))
    else:
        is_topic_complete = bool(row_up.get("ss_post_path") and row_up.get("ss_profile_path"))

    if is_topic_complete:
        if active_top == 1:
            # Auto switch to Topic 2!
            context.user_data["active_topic_id"] = 2
            next_kb = InlineKeyboardMarkup([
                [InlineKeyboardButton("📸 Topic 2 (20 Views) Active - Bhejo Abhi", callback_data=f"seltop_{active_acc}_2")],
                [InlineKeyboardButton("📋 View Account " + str(active_acc), callback_data=f"viewacc_{active_acc}")]
            ])
            status_msg = (
                f"🎉 *Topic 1 Complete!*\n\n"
                f"👉 *Ab direct Topic 2 (Social Media Graphic - 20 Views) ke Screenshots aur Link bhej do!*"
            )
            await update.message.reply_text(status_msg, parse_mode="Markdown", reply_markup=next_kb)
            return

        elif active_top == 2:
            # Auto switch to Topic 3!
            context.user_data["active_topic_id"] = 3
            next_kb = InlineKeyboardMarkup([
                [InlineKeyboardButton("📸 Topic 3 (Referral Graphic) Active - Bhejo Abhi", callback_data=f"seltop_{active_acc}_3")],
                [InlineKeyboardButton("📋 View Account " + str(active_acc), callback_data=f"viewacc_{active_acc}")]
            ])
            status_msg = (
                f"🎉 *Topic 2 Complete!*\n\n"
                f"👉 *Ab direct Topic 3 (Referral Graphic Post) ke Screenshots aur Link bhej do!*"
            )
            await update.message.reply_text(status_msg, parse_mode="Markdown", reply_markup=next_kb)
            return

        elif active_top == 3:
            next_acc = 1 if active_acc == 50 else active_acc + 1
            finish_kb = InlineKeyboardMarkup([
                [InlineKeyboardButton(f"🚀 Start Account {next_acc:02d} ➡️", callback_data=f"seltop_{next_acc}_1")],
                [InlineKeyboardButton(f"📁 View Account {active_acc:02d} Proofs", callback_data=f"viewacc_{active_acc}")]
            ])
            status_msg = (
                f"🏆 *ACCOUNT {active_acc:02d} COMPLETED! (All 3 Topics Done)*\n\n"
                f"👉 Agle Account {next_acc:02d} ke proofs upload karne ke liye niche button dabao:"
            )
            await update.message.reply_text(status_msg, parse_mode="Markdown", reply_markup=finish_kb)
            return

    else:
        # Prompt for next missing screenshot in current topic
        if not row_up.get("ss_profile_path"):
            status_msg += "👉 *Ab 'Profile Screenshot' bhej do:*"
        elif active_top == 2 and not row_up.get("ss_views_path"):
            status_msg += "👉 *Ab '20+ Views/Impressions Screenshot' bhej do:*"

        await update.message.reply_text(
            status_msg,
            parse_mode="Markdown",
            reply_markup=make_topic_select_keyboard(active_acc)
        )

async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    chat_id = query.message.chat_id

    if data.startswith("seltop_"):
        parts = data.split("_")
        acc_id = int(parts[1])
        top_id = int(parts[2])
        context.user_data["active_acc_id"] = acc_id
        context.user_data["active_topic_id"] = top_id
        
        await query.message.reply_text(
            f"📥 *Uploading Mode: Account {acc_id:02d} - Topic {top_id} ({TOPIC_NAMES[top_id]})*\n\n"
            f"1️⃣ Post ka Link text me paste karke send karo.\n"
            f"2️⃣ Screenshots (Photos) direct send karo.\n\n"
            f"_(Bot automatically Post SS, Profile SS aur Views SS me save kar lega)_",
            parse_mode="Markdown"
        )

    elif data.startswith("viewacc_"):
        acc_id = int(data.split("_")[1])
        await send_account_summary_card(chat_id, acc_id, context)

    elif data.startswith("sendall_"):
        acc_id = int(data.split("_")[1])
        proofs = get_account_proofs(acc_id)
        
        sent_any = False
        for row in proofs:
            top_id = row["topic_id"]
            media = []
            if row["ss_post_file_id"]:
                media.append(InputMediaPhoto(row["ss_post_file_id"], caption=f"Acc {acc_id:02d} - Topic {top_id} Post SS\nLink: {row['post_link']}"))
            elif row["ss_post_path"] and os.path.exists(row["ss_post_path"]):
                media.append(InputMediaPhoto(open(row["ss_post_path"], "rb"), caption=f"Acc {acc_id:02d} - Topic {top_id} Post SS\nLink: {row['post_link']}"))
                
            if row["ss_profile_file_id"]:
                media.append(InputMediaPhoto(row["ss_profile_file_id"], caption=f"Acc {acc_id:02d} - Topic {top_id} Profile SS"))
            elif row["ss_profile_path"] and os.path.exists(row["ss_profile_path"]):
                media.append(InputMediaPhoto(open(row["ss_profile_path"], "rb"), caption=f"Acc {acc_id:02d} - Topic {top_id} Profile SS"))
                
            if top_id == 2:
                if row["ss_views_file_id"]:
                    media.append(InputMediaPhoto(row["ss_views_file_id"], caption=f"Acc {acc_id:02d} - Topic 2 20+ Views SS"))
                elif row["ss_views_path"] and os.path.exists(row["ss_views_path"]):
                    media.append(InputMediaPhoto(open(row["ss_views_path"], "rb"), caption=f"Acc {acc_id:02d} - Topic 2 20+ Views SS"))
                    
            if media:
                sent_any = True
                await context.bot.send_media_group(chat_id=chat_id, media=media)

        if not sent_any:
            await query.message.reply_text(f"⚠️ Account {acc_id:02d} ke liye abhi koi screenshot uploaded nahi hai.")

def main():
    print("[+] Initializing Proof DB...")
    init_proof_db()
    print("[+] Starting Proof Manager Bot @trxmangrbot ...")
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("menu", start_command))
    app.add_handler(CallbackQueryHandler(callback_handler))
    app.add_handler(MessageHandler(filters.PHOTO, photo_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_router))

    app.run_polling()

if __name__ == '__main__':
    main()
