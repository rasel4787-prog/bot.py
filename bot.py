import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
import json
import os
import asyncio

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Replace with your actual bot token
BOT_TOKEN = "8425270617:AAHrs9qx1m664wTycEbp28EUFzseBk9xrNY"

# Replace with your web app URL (will be your cloud hosting URL)
WEB_APP_URL = "https://your-domain.com/webapp.html"

# File to store user data
USER_DATA_FILE = "user_data.json"

def load_user_data():
    """Load user data from JSON file"""
    try:
        if os.path.exists(USER_DATA_FILE):
            with open(USER_DATA_FILE, 'r') as f:
                return json.load(f)
    except Exception as e:
        logger.error(f"Error loading user data: {e}")
    return {}

def save_user_data(data):
    """Save user data to JSON file"""
    try:
        with open(USER_DATA_FILE, 'w') as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        logger.error(f"Error saving user data: {e}")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    try:
        user = update.effective_user
        user_id = str(user.id)
        username = user.username or user.first_name
        
        # Load existing user data
        user_data = load_user_data()
        
        # Initialize user if not exists
        if user_id not in user_data:
            user_data[user_id] = {
                "username": username,
                "ads_watched_today": 0,
                "total_ads_watched": 0,
                "history": []
            }
            save_user_data(user_data)
        
        # Create inline keyboard with Web App button
        keyboard = [
            [InlineKeyboardButton(
                "🎯 Click Here To Earn", 
                web_app=WebAppInfo(url=WEB_APP_URL)
            )],
            [InlineKeyboardButton("📊 View Stats", callback_data="stats")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        welcome_text = f"""
🎉 Welcome to EarnTerra Bot, {username}!

💰 Earn rewards by watching ads and completing tasks!
📱 Click the button below to start earning.

Stats:
• Today's ads watched: {user_data[user_id]['ads_watched_today']}
• Total ads watched: {user_data[user_id]['total_ads_watched']}
        """
        
        await update.message.reply_text(welcome_text, reply_markup=reply_markup)
        
    except Exception as e:
        logger.error(f"Error in start command: {e}")
        await update.message.reply_text("Sorry, there was an error. Please try again.")

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle button callbacks"""
    try:
        query = update.callback_query
        await query.answer()
        
        user_id = str(query.from_user.id)
        user_data = load_user_data()
        
        if query.data == "stats":
            if user_id in user_data:
                stats_text = f"""
📊 Your EarnTerra Stats:

👤 Username: @{user_data[user_id]['username']}
📅 Ads watched today: {user_data[user_id]['ads_watched_today']}
🎯 Total ads watched: {user_data[user_id]['total_ads_watched']}

📜 Recent History:
"""
                # Show last 5 entries from history
                history = user_data[user_id]['history'][-5:]
                for entry in history:
                    stats_text += f"• {entry}\n"
                
                if not history:
                    stats_text += "No history yet. Start earning!"
            else:
                stats_text = "No data found. Please start the bot first!"
            
            await query.edit_message_text(stats_text)
            
    except Exception as e:
        logger.error(f"Error in button callback: {e}")

async def main() -> None:
    """Start the bot."""
    try:
        # Create the Application
        application = Application.builder().token(BOT_TOKEN).build()
        
        # Add handlers
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CallbackQueryHandler(button_callback))
        
        # Run the bot until the user presses Ctrl-C
        logger.info("Bot is starting...")
        await application.initialize()
        await application.start()
        await application.updater.start_polling()
        
        # Keep the bot running
        try:
            await asyncio.Event().wait()
        except KeyboardInterrupt:
            logger.info("Bot stopped by user")
        finally:
            await application.updater.stop()
            await application.stop()
            await application.shutdown()
            
    except Exception as e:
        logger.error(f"Error starting bot: {e}")
        print(f"Error: {e}")
        print("\nTroubleshooting steps:")
        print("1. Make sure you replaced YOUR_BOT_TOKEN_HERE with your actual bot token")
        print("2. Check your internet connection")
        print("3. Verify your bot token is correct")

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nBot stopped.")