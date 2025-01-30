# TeleBot-mani
Telegram Bot with Gemini AI Integration

A powerful Telegram bot that integrates Google's Gemini AI for intelligent interactions, image analysis, and web search capabilities.


🔑 Key Features

User Registration

  1.Saves first_name, username, and chat_id in MongoDB
  
  2.Phone number verification via Telegram's contact button
  
  3.Secure user data storage

Gemini-Powered Chat

  1.Integrates with Google's Gemini AI API
  
  2.Stores complete chat history with timestamps
  
  3.Context-aware conversations

Image/File Analysis

  1.Processes images (JPG, PNG) and PDFs
  
  2.Uses Gemini AI for content description
  
  3.OCR text extraction
  
  4.Stores file metadata in MongoDB

Web Search
  
  1.Custom web search functionality
  
  2.AI-powered search result summaries
  
  3.Returns relevant web links
  
  4.Integrated with chat interface

⚙️ Requirements

python-telegram-bot

google-generativeai

pymongo

python-dotenv

Pillow

pytesseract

serpapi

🔒 Environment Variables

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
