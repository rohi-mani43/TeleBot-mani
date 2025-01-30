import logging
import os
import google.generativeai as genai
from dotenv import load_dotenv
from pymongo import MongoClient
from telegram import (
    Update, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, 
    InlineKeyboardButton, ReplyKeyboardRemove
)
from telegram.ext import (
    Application, CommandHandler, MessageHandler, CallbackQueryHandler, 
    CallbackContext, filters
)
from telegram.helpers import escape_markdown
from datetime import datetime
import pytesseract
from PIL import Image
import io
import base64
from serpapi.google_search import GoogleSearch
from googlesearch import search  # Use this instead of SerpAPI for simplicity
import asyncio
import html

# Load environment variables
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
MONGO_URI = os.getenv("MONGO_URI")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
SERPAPI_API_KEY = os.getenv("SERPAPI_API_KEY")

# Create downloads directory
os.makedirs("downloads", exist_ok=True)

# Connect to MongoDB
client = MongoClient(MONGO_URI, tls=True, tlsAllowInvalidCertificates=True)
db = client["telegram_bot"]
users_collection = db["users"]
history_collection = db["chat_history"]

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Configure Gemini
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-pro')
vision_model = genai.GenerativeModel('gemini-pro-vision')

# Generation config
generation_config = {
    "temperature": 0.7,
    "top_p": 0.8,
    "top_k": 32,
    "max_output_tokens": 4096,
    "candidate_count": 1,
}

# Safety settings
safety_settings = [
    {
        "category": "HARM_CATEGORY_HARASSMENT",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
    },
    {
        "category": "HARM_CATEGORY_HATE_SPEECH",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
    },
    {
        "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
    },
    {
        "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
    }
]

# Temporary state storage
USER_STATE = {}

# Tesseract OCR setup
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

async def perform_web_search(query: str) -> str:
    try:
        logger.info(f"Starting web search for query: {query}")
        
        # Perform Google search
        search_results = []
        for result in search(query, num_results=5, lang="en"):
            search_results.append(result)
            
        if not search_results:
            return "No results found. Please try a different search query."

        # Format results
        formatted_results = f"🔍 Search Results for: '{html.escape(query)}'\n\n"
        
        for i, url in enumerate(search_results, 1):
            formatted_results += f"{i}. 🔗 {url}\n\n"

        # Generate AI summary
        summary_prompt = f"Provide a brief summary of search results about: {query}"
        try:
            ai_summary = await generate_gemini_response(summary_prompt)
            formatted_results += f"\n📝 AI Summary:\n{ai_summary}"
        except Exception as e:
            logger.error(f"AI summary generation error: {e}")
            formatted_results += "\n⚠️ AI summary generation failed."

        return formatted_results

    except Exception as e:
        logger.error(f"Search error: {e}")
        return "❌ Search failed. Please try again later."

"""""
Please try:
• Checking your internet connection
• Waiting a few moments
• Trying a different search query

If the problem persists, contact support."""

async def generate_gemini_response(prompt: str) -> str:
    try:
        response = model.generate_content(
            prompt,
            generation_config=generation_config,
            safety_settings=safety_settings
        )
        return response.text
    except Exception as e:
        logger.error(f"Gemini API error: {str(e)}")
        return "Sorry, I encountered an error processing your request. Please try again."

async def analyze_image_with_gemini(image_path: str) -> str:
    try:
        with open(image_path, 'rb') as image_file:
            image_bytes = image_file.read()

        contents = {
            "contents": [
                {
                    "parts": [
                        {
                            "text": """Please analyze this image in detail and provide:
                            1. Main subject or focus
                            2. Visual elements and composition
                            3. Text content (if any)
                            4. Notable features or patterns
                            5. Context and purpose
                            
                            Keep the analysis clear and concise."""
                        },
                        {
                            "inline_data": {
                                "mime_type": "image/jpeg",
                                "data": base64.b64encode(image_bytes).decode('utf-8')
                            }
                        }
                    ]
                }
            ]
        }

        response = vision_model.generate_content(
            contents=contents,
            generation_config=generation_config,
            safety_settings=safety_settings
        )

        if response.prompt_feedback.block_reason:
            return "⚠️ The image analysis was blocked due to content safety policies."

        return response.text

    except Exception as e:
        logger.error(f"Vision analysis error: {str(e)}")
        return f"Sorry, I encountered an error analyzing the image. Please try again later."
async def extract_text_from_image(image_path):
    try:
        image = Image.open(image_path)
        text = pytesseract.image_to_string(image)
        return text.strip() or "No text detected in the image."
    except Exception as e:
        logger.error(f"OCR Error: {str(e)}")
        return "Error processing image text."

async def show_main_menu(update: Update, context: CallbackContext):
    keyboard = [
        [InlineKeyboardButton("📋 View Profile", callback_data="view_profile")],
        [InlineKeyboardButton("🔄 Update Info", callback_data="update_info")],
        [InlineKeyboardButton("🔍 Web Search", callback_data="web_search")],
        [InlineKeyboardButton("🚀 Start Chat", callback_data="next_action")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    menu_text = """🌟 Main Menu

Choose an option:
• View your profile
• Update your information
• Perform web searches
• Start chatting with AI

You can also:
• Send images for analysis
• Share PDFs for review
• Use /websearch for web queries
• Ask any questions"""

    try:
        if isinstance(update, Update):
            if update.message:
                await update.message.reply_text(menu_text, reply_markup=reply_markup)
            elif update.callback_query:
                await update.callback_query.message.edit_text(
                    menu_text,
                    reply_markup=reply_markup
                )
        else:
            await update.edit_message_text(menu_text, reply_markup=reply_markup)
    except Exception as e:
        logger.error(f"Error showing main menu: {str(e)}")
        try:
            if isinstance(update, Update):
                await update.message.reply_text("❌ Error showing menu. Please try /start again.")
            else:
                await update.edit_message_text("❌ Error showing menu. Please try /start again.")
        except Exception:
            pass

async def start(update: Update, context: CallbackContext):
    user = update.effective_user
    chat_id = user.id

    try:
        existing_user = users_collection.find_one({"chat_id": chat_id})
        if existing_user and existing_user.get("phone_number"):
            await update.message.reply_text(
                f"""👋 Welcome back, {user.first_name}!
                
🤖 I'm your Gemini AI assistant, ready to help you with:
• Image analysis
• Document processing
• Web searches
• Question answering
• And more!"""
            )
            await show_main_menu(update, context)
            return

        if not existing_user:
            user_data = {
                "chat_id": chat_id,
                "first_name": user.first_name,
                "username": user.username if user.username else None,
                "phone_number": None,
                "registration_date": datetime.utcnow()
            }
            users_collection.insert_one(user_data)
            logger.info(f"New user registered: {user.first_name} ({chat_id})")

        keyboard = [[KeyboardButton("📞 Send Phone Number", request_contact=True)]]
        reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
        await update.message.reply_text(
            """👋 Welcome to Gemini AI Bot!

To get started, please:
1️⃣ Share your phone number
2️⃣ Set up your username
3️⃣ Start exploring features

🔒 Your information is secure and private.""",
            reply_markup=reply_markup
        )
    except Exception as e:
        logger.error(f"Error in start command: {str(e)}")
        await update.message.reply_text("❌ An error occurred. Please try again later.")

async def save_contact(update: Update, context: CallbackContext):
    user = update.effective_user
    contact = update.message.contact

    if not contact or contact.user_id != user.id:
        await update.message.reply_text(
            """⚠️ Please use the provided button to share your phone number.

🔒 This is required for registration and security purposes.""",
            reply_markup=ReplyKeyboardMarkup(
                [[KeyboardButton("📞 Send Phone Number", request_contact=True)]],
                resize_keyboard=True,
                one_time_keyboard=True
            )
        )
        return

    try:
        users_collection.update_one(
            {"chat_id": user.id},
            {
                "$set": {
                    "phone_number": contact.phone_number,
                    "phone_verified": True,
                    "last_updated": datetime.utcnow()
                }
            }
        )

        await update.message.reply_text(
            """✅ Phone number verified successfully!

📝 Please enter your username (without @):
• Minimum 3 characters
• No special characters
• No spaces

Example: johndoe""",
            reply_markup=ReplyKeyboardRemove()
        )
        
        USER_STATE[user.id] = "waiting_for_username"
        
    except Exception as e:
        logger.error(f"Error saving contact: {str(e)}")
        await update.message.reply_text(
            "❌ Error saving your contact information. Please try again or contact support."
        )

async def handle_username(update: Update, context: CallbackContext):
    user = update.effective_user
    if USER_STATE.get(user.id) == "waiting_for_username":
        username = update.message.text.strip()
        
        try:
            if not username or len(username) < 3:
                await update.message.reply_text(
                    "⚠️ Username must be at least 3 characters long. Please try again:"
                )
                return
                
            if '@' in username:
                await update.message.reply_text(
                    "⚠️ Please enter username without '@'. Try again:"
                )
                return

            users_collection.update_one(
                {"chat_id": user.id},
                {"$set": {
                    "username": username,
                    "last_updated": datetime.utcnow()
                }}
            )

            await update.message.reply_text(
                f"""✅ Registration Complete!

📝 Your Details:
• Username: @{username}
• ID: {user.id}
• Registration Time: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}

Welcome to Gemini AI Bot! 🎉""",
                reply_markup=ReplyKeyboardRemove()
            )

            del USER_STATE[user.id]
            await show_main_menu(update, context)

        except Exception as e:
            logger.error(f"Error handling username: {str(e)}")
            await update.message.reply_text(
                "❌ Error saving username. Please try again or contact support."
            )

async def handle_message(update: Update, context: CallbackContext):
    user = update.effective_user
    state = USER_STATE.get(user.id, {}).get("step")
    message_text = update.message.text.strip()

    # Handle web search command
    if message_text.startswith('/websearch'):
        query = message_text[10:].strip()
        if not query:
            await update.message.reply_text(
                """⚠️ Please provide a search query after /websearch

Example: 
/websearch python programming tutorial

Tips:
• Be specific with your query
• Use relevant keywords
• Keep queries concise"""
            )
            return
        
        status_message = await update.message.reply_text(
            "🔍 Searching... Please wait..."
        )
        
        try:
            search_results = await perform_web_search(query)
            await status_message.delete()
            
            # Split long messages if needed
            if len(search_results) > 4096:
                chunks = [search_results[i:i+4000] for i in range(0, len(search_results), 4000)]
                for chunk in chunks:
                    await update.message.reply_text(
                        chunk,
                        disable_web_page_preview=True,
                        parse_mode='HTML'
                    )
            else:
                await update.message.reply_text(
                    search_results,
                    disable_web_page_preview=True,
                    parse_mode='HTML'
                )
        except Exception as e:
            logger.error(f"Search handling error: {e}")
            await status_message.edit_text(
                "❌ Search failed. Please try again later."
            )
        return
    # Regular message handling
    if state == "query_bot":
        try:
            thinking_msg = await update.message.reply_text("🤔 Thinking...")
            bot_response = await generate_gemini_response(message_text)
            
            chat_entry = {
                "chat_id": user.id,
                "username": user.username,
                "user_input": message_text,
                "bot_response": bot_response,
                "timestamp": datetime.utcnow()
            }
            history_collection.insert_one(chat_entry)

            await thinking_msg.delete()

            if len(bot_response) > 4096:
                chunks = [bot_response[i:i+4000] for i in range(0, len(bot_response), 4000)]
                for chunk in chunks:
                    await update.message.reply_text(chunk)
            else:
                await update.message.reply_text(bot_response)

        except Exception as e:
            logger.error(f"Error in message handling: {str(e)}")
            await update.message.reply_text("❌ Sorry, I encountered an error. Please try again.")
    
    elif state == "update_name":
        users_collection.update_one(
            {"chat_id": user.id},
            {"$set": {"first_name": message_text}}
        )
        USER_STATE[user.id]["step"] = "update_username"
        await update.message.reply_text("✅ Name updated! Now enter your new username (without @):")
    
    elif state == "update_username":
        users_collection.update_one(
            {"chat_id": user.id},
            {"$set": {"username": message_text}}
        )
        del USER_STATE[user.id]
        await update.message.reply_text("✅ Profile updated successfully!")
        await show_main_menu(update, context)
    
    elif state == "waiting_for_username":
        await handle_username(update, context)
    else:
        await update.message.reply_text(
            """Please use the menu options or:
• Send me an image/file to analyze
• Use /websearch followed by your query to search the web
• Ask me any question directly"""
        )

async def menu_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()

    if query.data == "view_profile":
        user = users_collection.find_one({"chat_id": query.from_user.id})
        if user:
            name = escape_markdown(user.get("first_name", "N/A"), version=2)
            username = escape_markdown(user.get("username", "N/A"), version=2)
            phone = escape_markdown(user.get("phone_number", "N/A"), version=2)

            profile_text = f"""👤 *Your Profile:*

📛 Name: {name}
🔹 Username: @{username}
📞 Phone: {phone}"""

            await query.message.reply_text(profile_text, parse_mode="MarkdownV2")
        else:
            await query.message.reply_text("❌ No profile found.")

    elif query.data == "update_info":
        USER_STATE[query.from_user.id] = {"step": "update_name"}
        await query.message.reply_text("📝 Enter your new name:")

    elif query.data == "web_search":
        await query.message.reply_text(
            """🔍 Web Search Mode

To search the web, use the command:
/websearch followed by your query

Example:
/websearch latest AI developments

The results will include:
• Top search results
• Brief descriptions
• Direct links
• AI-generated summary"""
        )

    elif query.data == "next_action":
        USER_STATE[query.from_user.id] = {"step": "query_bot"}
        await query.message.reply_text(
            """🤖 Welcome to Gemini AI Assistant!

I can help you with:
1. 💬 Answer your questions
2. 📷 Analyze images (JPG, PNG)
3. 📑 Handle PDF documents
4. 📝 Extract text from images
5. 🔍 Search the web

To get started:
• Ask any question
• Send an image or PDF
• Share documents for analysis
• Use /websearch for web queries

Tips for best results:
• Use clear images
• Ensure good lighting
• Share readable content
• Ask specific questions

I'm ready to assist you! What would you like to do?"""
        )
async def handle_file(update: Update, context: CallbackContext):
    user = update.effective_user
    
    try:
        processing_message = await update.message.reply_text("🔄 Processing your file... Please wait.")
        
        if update.message.photo:
            file = await update.message.photo[-1].get_file()
            file_name = f"image_{file.file_id}.jpg"
            file_type = "photo"
        else:
            file = await update.message.document.get_file()
            file_name = update.message.document.file_name
            file_type = "document"

        download_path = os.path.join("downloads", f"{user.id}_{file_name}")
        await file.download_to_drive(download_path)

        if file_name.lower().endswith(('.jpg', '.jpeg', '.png')):
            try:
                # Get Gemini's analysis
                gemini_analysis = await analyze_image_with_gemini(download_path)
                
                # Get OCR text as backup
                ocr_text = await extract_text_from_image(download_path)
                
                description = f"""📷 Image Analysis Report

🔍 Gemini AI Analysis:
{gemini_analysis}

📝 OCR Text Detection:
{ocr_text}

---
Generated by Gemini AI Bot"""

            except Exception as e:
                logger.error(f"Error in image analysis: {str(e)}")
                description = "❌ Sorry, there was an error analyzing the image. Please try again."

        elif file_name.lower().endswith('.pdf'):
            description = f"""📑 PDF File Received: {file_name}

⚠️ Note: Direct PDF content analysis is currently limited. 
Please share specific pages as images for detailed analysis.

🔍 File Information:
- Name: {file_name}
- Type: PDF Document
- Received: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}

💡 Tip: For better analysis, you can:
1. Convert specific pages to images
2. Share screenshots of important sections
3. Type out any specific questions about the content"""

        else:
            description = """⚠️ Unsupported file format

Please share:
✅ Images (.jpg, .jpeg, .png)
✅ PDF documents
✅ Clear, readable content

For best results, ensure:
- Good image quality
- Clear text if present
- Proper file format"""

        # Save to MongoDB
        try:
            file_metadata = {
                "chat_id": user.id,
                "file_name": file_name,
                "file_type": file_type,
                "analysis": description,
                "timestamp": datetime.utcnow()
            }
            history_collection.insert_one(file_metadata)
        except Exception as e:
            logger.error(f"MongoDB Error: {str(e)}")

        await processing_message.delete()

        # Split long responses if needed
        if len(description) > 4096:
            chunks = [description[i:i+4000] for i in range(0, len(description), 4000)]
            for i, chunk in enumerate(chunks):
                header = "📄 Analysis (continued):\n\n" if i > 0 else ""
                await update.message.reply_text(f"{header}{chunk}")
        else:
            await update.message.reply_text(description)

    except Exception as e:
        logger.error(f"Error processing file: {str(e)}")
        await update.message.reply_text(
            "❌ Sorry, there was an error processing your file. Please try again."
        )
    finally:
        # Clean up downloaded file
        if 'download_path' in locals() and os.path.exists(download_path):
            try:
                os.remove(download_path)
            except Exception as e:
                logger.error(f"Error removing file: {str(e)}")


async def error_handler(update: object, context: CallbackContext):
    logger.error(f"Update {update} caused error {context.error}")
    try:
        if isinstance(update, Update) and update.message:
            await update.message.reply_text(
                "❌ An error occurred. Please try again or contact support."
            )
    except Exception:
        pass

def main():
    app = Application.builder().token(BOT_TOKEN).build()

    # Add handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.CONTACT, save_contact))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(MessageHandler(filters.PHOTO | filters.Document.ALL, handle_file))
    app.add_handler(CallbackQueryHandler(menu_handler))
    app.add_error_handler(error_handler)

    logger.info("✨ Bot started successfully!")
    app.run_polling()

if __name__ == "__main__":
    main()
