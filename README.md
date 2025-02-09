# TeleBot-mani: Telegram Bot with Gemini AI Integration

## Description
A powerful **Telegram bot** that integrates **Google's Gemini AI** for intelligent interactions, image analysis, and web search capabilities.

---

## 🔑 Key Features

### 💼 User Registration
- Saves `first_name`, `username`, and `chat_id` in **MongoDB**
- Phone number verification via **Telegram's contact button**
- Secure user data storage

### 📚 Gemini-Powered Chat
- Integrates with **Google's Gemini AI API**
- Stores complete chat history with timestamps
- **Context-aware** conversations

### 🖼️ Image/File Analysis
- Processes images (**JPG, PNG**) and **PDFs**
- Uses **Gemini AI** for content description
- **OCR text extraction**
- Stores file metadata in **MongoDB**

### 🌐 Web Search
- Custom **web search** functionality
- **AI-powered** search result summaries
- Returns relevant web links
- Integrated with chat interface

---

## ⚙️ Requirements
To install dependencies, run:
```bash
pip install python-telegram-bot google-generativeai pymongo python-dotenv Pillow pytesseract serpapi
```

### Required Libraries
- `python-telegram-bot`
- `google-generativeai`
- `pymongo`
- `python-dotenv`
- `Pillow`
- `pytesseract`
- `serpapi`

---

## 🔒 Environment Variables
Create a **.env** file with the following:
```env
BOT_TOKEN=your_telegram_bot_token
MONGO_URI=your_mongodb_connection_string
GEMINI_API_KEY=your_gemini_api_key
SERPAPI_API_KEY=your_serpapi_api_key
```

---

## 🚀 Setup Instructions
1. **Clone the repository:**
   ```bash
   git clone https://github.com/your-username/TeleBot-mani.git
   cd TeleBot-mani
   ```
2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
3. **Configure environment variables:**
   Ensure your **.env** file is properly set up.
4. **Install Tesseract OCR:**
   - **Windows:** Download and install from [Tesseract OCR](https://github.com/UB-Mannheim/tesseract/wiki)
   - **Linux (Ubuntu/Debian):**
     ```bash
     sudo apt install tesseract-ocr
     ```
5. **Run the bot:**
   ```bash
   python bot.py
   ```

---

## 📝 Note
- **MongoDB instance with TLS support** is required.
- **Tesseract OCR** must be installed for text extraction.
- **Rate limiting** implemented for all API calls.
- **Comprehensive error handling and logging** included.

---

## 📝 Pictorial Representation
### System Architecture:
```
+------------------+        +------------------+
| Telegram User   | --->   | TeleBot          |
+------------------+        +------------------+
       |                           |
       v                           v
+------------------+        +------------------+
| Gemini AI API   |        | MongoDB Database |
+------------------+        +------------------+
       |                           |
       v                           v
+------------------+        +------------------+
| Web Search API  |        | OCR & File Store |
+------------------+        +------------------+
```

---

## 🌐 Deployment
Consider hosting on:
- **Heroku**
- **AWS Lambda**
- **Google Cloud Functions**

Ensure **environment variables** are set securely.

---

## 👥 Author
- **Peruri Rohith Manikanta**
- **Email:** rohithmanikantaperuri@gmail.com
- **LinkedIn:** [rohith-manikanta-peruri](https://www.linkedin.com/in/rohith-manikanta-peruri-a3323b2b8/)

---
Feel free to **fork, modify, and use** as needed! 🚀
