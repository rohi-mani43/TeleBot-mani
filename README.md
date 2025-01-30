# TeleBot-mani
Telegram Bot with Gemini AI Integration

A powerful Telegram bot that integrates Google's Gemini AI for intelligent interactions, image analysis, and web search capabilities.


🔑 Key Features

User Registration

Saves first_name, username, and chat_id in MongoDB
Phone number verification via Telegram's contact button
Secure user data storage
Gemini-Powered Chat

Integrates with Google's Gemini AI API
Stores complete chat history with timestamps
Context-aware conversations
Image/File Analysis

Processes images (JPG, PNG) and PDFs
Uses Gemini AI for content description
OCR text extraction
Stores file metadata in MongoDB
Web Search

Custom web search functionality
AI-powered search result summaries
Returns relevant web links
Integrated with chat interface

⚙️ Requirements

plaintext
python-telegram-bot
google-generativeai
pymongo
python-dotenv
Pillow
pytesseract
serpapi

🔒 Environment Variables

plaintext
BOT_TOKEN=your_telegram_bot_token
MONGO_URI=your_mongodb_connection_string
GEMINI_API_KEY=your_gemini_api_key
SERPAPI_API_KEY=your_serpapi_api_key

🚀 Setup

Clone the repository
Install dependencies: pip install -r requirements.txt
Configure environment variables
Install Tesseract OCR
Run the bot: python bot.py

📝 Note

Requires MongoDB instance with TLS support
Tesseract OCR must be installed for text extraction
Rate limiting implemented for all API calls
Comprehensive error handling and logging
