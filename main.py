import smtplib
import os
import json
import asyncio
import random
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
import re

# Bot Token
BOT_TOKEN = ""

# Gmail Accounts
ACCOUNTS = [
    {"email": "tk7827k@gmail.com", "password": "vhnb uy dfhi gfcj"},
    {"email": "you0411@gmail.com", "password": "dpvd f ttfo byod"},
    {"email": "Gogobober7824@gmail.com", "password": "p bmiz ncrl itvy"}
]

# Simple Message (Not aggressive)
SIMPLE_MESSAGE = """Dear Customer,

This is a follow-up regarding your pending account settlement. 

Please review your account at your earliest convenience.

Clear Full Amount Loan Your father doesn't have any money, son.

Thank you for your cooperation.

Best Regards,
Customer Service
"""

SETTINGS_FILE = "bot_settings.json"

class EmailBot:
    def __init__(self):
        self.recipients = []
        self.send_count = 5
        self.current_account_index = 0
        self.sending = False
        self.should_stop = False
        self.selected_recipients = []
        self.load_settings()
    
    def load_settings(self):
        if os.path.exists(SETTINGS_FILE):
            with open(SETTINGS_FILE, 'r') as f:
                data = json.load(f)
                self.recipients = data.get('recipients', [])
                self.send_count = data.get('send_count', 5)
    
    def save_settings(self):
        with open(SETTINGS_FILE, 'w') as f:
            json.dump({'recipients': self.recipients, 'send_count': self.send_count}, f)
    
    def get_next_account(self):
        account = ACCOUNTS[self.current_account_index]
        self.current_account_index = (self.current_account_index + 1) % len(ACCOUNTS)
        return account
    
    def send_email(self, receiver, message_num, total_messages):
        try:
            account = self.get_next_account()
            msg = MIMEMultipart()
            msg['From'] = account['email']
            msg['To'] = receiver
            # Simple subject line as requested
            msg['Subject'] = f"📧 Message #{message_num} - Notifier"
            
            body = f"""
📧 Message #{message_num} of {total_messages}
⏰ Time: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
📧 To: {receiver}

{SIMPLE_MESSAGE}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Please Clear Loan Otherwise Spoil Your Life
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
            
            msg.attach(MIMEText(body, 'plain'))
            
            clean_password = account['password'].replace(" ", "")
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(account['email'], clean_password)
            server.send_message(msg)
            server.quit()
            
            return True, account['email']
        except Exception as e:
            return False, str(e)[:50]

bot = EmailBot()

# ============= KEYBOARDS =============

def main_keyboard():
    keyboard = [
        [InlineKeyboardButton("📧 ADD RECIPIENT", callback_data="add")],
        [InlineKeyboardButton("👥 VIEW & SELECT", callback_data="view_select")],
        [InlineKeyboardButton("🔢 SET SEND COUNT", callback_data="count")],
        [InlineKeyboardButton("🗑️ CLEAR ALL", callback_data="clear")],
        [InlineKeyboardButton("🚀 START SENDING", callback_data="start")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_recipients_keyboard(selected=None):
    if selected is None:
        selected = bot.selected_recipients
    
    keyboard = []
    for i, email in enumerate(bot.recipients):
        is_selected = email in selected
        status = "✅" if is_selected else "⬜"
        keyboard.append([InlineKeyboardButton(f"{status} {email}", callback_data=f"toggle_{i}")])
    
    keyboard.append([InlineKeyboardButton("✅ SELECT ALL", callback_data="select_all")])
    keyboard.append([InlineKeyboardButton("❌ DESELECT ALL", callback_data="deselect_all")])
    keyboard.append([InlineKeyboardButton("🗑️ DELETE SELECTED", callback_data="delete_selected")])
    keyboard.append([InlineKeyboardButton("🔙 BACK", callback_data="menu")])
    
    return InlineKeyboardMarkup(keyboard)

def count_keyboard():
    keyboard = [
        [InlineKeyboardButton("5", callback_data="cnt_5"), InlineKeyboardButton("10", callback_data="cnt_10")],
        [InlineKeyboardButton("20", callback_data="cnt_20"), InlineKeyboardButton("50", callback_data="cnt_50")],
        [InlineKeyboardButton("100", callback_data="cnt_100"), InlineKeyboardButton("✏️ CUSTOM", callback_data="cnt_custom")],
        [InlineKeyboardButton("🔙 BACK", callback_data="menu")]
    ]
    return InlineKeyboardMarkup(keyboard)

def confirm_keyboard():
    keyboard = [
        [InlineKeyboardButton("✅ YES, START", callback_data="confirm_yes")],
        [InlineKeyboardButton("❌ NO", callback_data="confirm_no")]
    ]
    return InlineKeyboardMarkup(keyboard)

def stop_keyboard():
    keyboard = [[InlineKeyboardButton("🛑 STOP SENDING", callback_data="stop")]]
    return InlineKeyboardMarkup(keyboard)

def back_keyboard():
    keyboard = [[InlineKeyboardButton("🔙 BACK", callback_data="menu")]]
    return InlineKeyboardMarkup(keyboard)

# ============= HANDLERS =============

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = f"""
🔥 *PD NOTIFIER BOT* 🔥

👑 *Owner:* PD Papa

📌 *Setup:*
1️⃣ Add Recipient Email
2️⃣ Select recipients
3️⃣ Set Send Count
4️⃣ Click START SENDING

✅ *Status:*
👥 Total: {len(bot.recipients)}
🎯 Selected: {len(bot.selected_recipients)}
🔢 Send Count: {bot.send_count}
⏱️ Delay: 1.5 seconds

👇 *Choose option:*
"""
    await update.message.reply_text(text, reply_markup=main_keyboard(), parse_mode='Markdown')

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    
    if data == "menu":
        text = f"📋 *MAIN MENU*\n\n👥 Total: {len(bot.recipients)}\n🎯 Selected: {len(bot.selected_recipients)}\n🔢 Send: {bot.send_count}"
        await query.edit_message_text(text, reply_markup=main_keyboard(), parse_mode='Markdown')
    
    elif data == "add":
        await query.edit_message_text("📧 *Send email address*\n\nExample: `user@gmail.com`", reply_markup=back_keyboard(), parse_mode='Markdown')
        context.user_data['waiting'] = 'email'
    
    elif data == "view_select":
        if not bot.recipients:
            await query.edit_message_text("❌ No recipients!", reply_markup=back_keyboard(), parse_mode='Markdown')
        else:
            await query.edit_message_text(f"👥 *SELECT RECIPIENTS*\n\nSelected: {len(bot.selected_recipients)}/{len(bot.recipients)}", reply_markup=get_recipients_keyboard(), parse_mode='Markdown')
    
    elif data.startswith("toggle_"):
        index = int(data.split("_")[1])
        email = bot.recipients[index]
        
        if email in bot.selected_recipients:
            bot.selected_recipients.remove(email)
        else:
            bot.selected_recipients.append(email)
        
        await query.edit_message_text(f"👥 *SELECT RECIPIENTS*\n\nSelected: {len(bot.selected_recipients)}/{len(bot.recipients)}", reply_markup=get_recipients_keyboard(), parse_mode='Markdown')
    
    elif data == "select_all":
        bot.selected_recipients = bot.recipients.copy()
        await query.edit_message_text(f"👥 *SELECT RECIPIENTS*\n\n✅ All selected! ({len(bot.selected_recipients)})", reply_markup=get_recipients_keyboard(), parse_mode='Markdown')
    
    elif data == "deselect_all":
        bot.selected_recipients = []
        await query.edit_message_text(f"👥 *SELECT RECIPIENTS*\n\n❌ All deselected!", reply_markup=get_recipients_keyboard(), parse_mode='Markdown')
    
    elif data == "delete_selected":
        if bot.selected_recipients:
            bot.recipients = [e for e in bot.recipients if e not in bot.selected_recipients]
            bot.selected_recipients = []
            bot.save_settings()
            await query.edit_message_text(f"🗑️ *Deleted!*\n\nRemaining: {len(bot.recipients)}", reply_markup=main_keyboard(), parse_mode='Markdown')
        else:
            await query.edit_message_text("❌ No recipients selected!", reply_markup=back_keyboard(), parse_mode='Markdown')
    
    elif data == "count":
        await query.edit_message_text("🔢 *How many times to send?*", reply_markup=count_keyboard(), parse_mode='Markdown')
    
    elif data.startswith("cnt_"):
        if data == "cnt_custom":
            await query.edit_message_text("✏️ *Enter number (1-500):*", reply_markup=back_keyboard(), parse_mode='Markdown')
            context.user_data['waiting'] = 'custom_count'
        else:
            bot.send_count = int(data.split("_")[1])
            bot.save_settings()
            await query.edit_message_text(f"✅ Set to {bot.send_count} times!", reply_markup=back_keyboard(), parse_mode='Markdown')
    
    elif data == "clear":
        bot.recipients = []
        bot.selected_recipients = []
        bot.send_count = 5
        bot.save_settings()
        await query.edit_message_text("🗑️ *All cleared!*", reply_markup=main_keyboard(), parse_mode='Markdown')
    
    elif data == "start":
        if not bot.selected_recipients:
            await query.edit_message_text("❌ *No recipients selected!*", reply_markup=main_keyboard(), parse_mode='Markdown')
            return
        
        total = len(bot.selected_recipients) * bot.send_count
        recipients_list = "\n".join([f"• {e}" for e in bot.selected_recipients[:5]])
        if len(bot.selected_recipients) > 5:
            recipients_list += f"\n• ... and {len(bot.selected_recipients)-5} more"
        
        msg = f"""
🚀 *READY TO SEND?*

📧 Selected: {len(bot.selected_recipients)}
🔢 Per recipient: {bot.send_count} times
📊 Total emails: {total}
⏱️ Delay: 1.5 seconds

📋 *Recipients:*
{recipients_list}

⚠️ *Confirm?*
"""
        await query.edit_message_text(msg, reply_markup=confirm_keyboard(), parse_mode='Markdown')
    
    elif data == "confirm_yes":
        await query.edit_message_text("🚀 *STARTING...*\n\n🛑 Use STOP to cancel", reply_markup=stop_keyboard(), parse_mode='Markdown')
        
        bot.sending = True
        bot.should_stop = False
        
        total = len(bot.selected_recipients) * bot.send_count
        sent = 0
        failed = 0
        
        for recipient in bot.selected_recipients:
            if bot.should_stop:
                break
            
            for i in range(bot.send_count):
                if bot.should_stop:
                    break
                
                message_num = (i + 1)
                total_messages = bot.send_count
                
                success, _ = bot.send_email(recipient, message_num, total_messages)
                
                if success:
                    sent += 1
                else:
                    failed += 1
                
                progress = ((sent + failed) / total) * 100
                
                try:
                    await query.edit_message_text(f"📊 *SENDING...*\n\n✅ Sent: {sent}\n❌ Failed: {failed}\n📈 Progress: {progress:.1f}%\n📧 To: {recipient}\n🔢 Msg: {message_num}/{total_messages}\n\n🛑 Click STOP", reply_markup=stop_keyboard(), parse_mode='Markdown')
                except:
                    pass
                
                if i < bot.send_count - 1 and not bot.should_stop:
                    await asyncio.sleep(1.5)
            
            if not bot.should_stop and len(bot.selected_recipients) > 1:
                await asyncio.sleep(1.5)
        
        bot.sending = False
        
        if bot.should_stop:
            await query.edit_message_text(f"🛑 *STOPPED!*\n\n✅ Sent: {sent}\n❌ Failed: {failed}\n📊 Progress: {((sent+failed)/total)*100:.1f}%", reply_markup=main_keyboard(), parse_mode='Markdown')
        else:
            await query.edit_message_text(f"🎉 *COMPLETE!*\n\n✅ Sent: {sent}\n❌ Failed: {failed}\n📊 Rate: {(sent/total)*100:.1f}%\n\n👑 @krishna7824", reply_markup=main_keyboard(), parse_mode='Markdown')
        
        with open("email_logs.txt", "a") as f:
            f.write(f"\n[{datetime.now()}] Sent: {sent} | Failed: {failed} | Total: {total}\n")
    
    elif data == "confirm_no":
        await query.edit_message_text("❌ *Cancelled!*", reply_markup=main_keyboard(), parse_mode='Markdown')
    
    elif data == "stop":
        bot.should_stop = True
        bot.sending = False
        await query.edit_message_text("🛑 *STOPPING...*", reply_markup=main_keyboard(), parse_mode='Markdown')

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    waiting = context.user_data.get('waiting')
    
    if waiting == 'email':
        if re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', text):
            bot.recipients.append(text)
            if text not in bot.selected_recipients:
                bot.selected_recipients.append(text)
            bot.save_settings()
            await update.message.reply_text(f"✅ Added: {text}\nTotal: {len(bot.recipients)} | Selected: {len(bot.selected_recipients)}", reply_markup=back_keyboard(), parse_mode='Markdown')
        else:
            await update.message.reply_text("❌ Invalid email!", reply_markup=back_keyboard(), parse_mode='Markdown')
        context.user_data['waiting'] = None
    
    elif waiting == 'custom_count':
        try:
            count = int(text)
            if 1 <= count <= 500:
                bot.send_count = count
                bot.save_settings()
                await update.message.reply_text(f"✅ Set to {count} times!", reply_markup=back_keyboard(), parse_mode='Markdown')
            else:
                await update.message.reply_text("❌ Enter 1-500!", reply_markup=back_keyboard(), parse_mode='Markdown')
        except:
            await update.message.reply_text("❌ Invalid number!", reply_markup=back_keyboard(), parse_mode='Markdown')
        context.user_data['waiting'] = None
    
    else:
        await update.message.reply_text("❓ Use /start", parse_mode='Markdown')

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("="*50)
    print("🤖 PD NOTIFIER BOT RUNNING...")
    print(f"📧 Accounts: {len(ACCOUNTS)}")
    print("📧 Subject: 📧 Message #X - Notifier")
    print("✅ Inbox delivery expected!")
    print("🔥 Press Ctrl+C to stop")
    print("="*50)
    
    app.run_polling()

if __name__ == "__main__":
    main()
