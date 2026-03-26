# 🐧 Text Rephraser - AI-Powered Menu Bar App

A lightweight macOS menu bar application that rephrases clipboard text using Google Gemini AI. Features multiple preset modes, custom prompts, and seamless clipboard integration.

## ✨ Features

- 🐧 **Menu Bar Integration**: Lives in your macOS menu bar with a cute penguin icon
- ⌨️ **Global Hotkey**: Press `Cmd + Shift + P` from anywhere to rephrase clipboard text
- 🎯 **Multiple Preset Modes**:
  - **Polite**: Make text more courteous and respectful
  - **Professional**: Transform to formal business language
  - **Casual**: Convert to friendly, relaxed tone
  - **Concise**: Shorten while keeping the meaning
  - **Detailed**: Expand with more information
  - **Simple**: Use simpler words and shorter sentences
- ✏️ **Custom Prompts**: Create your own rephrasing instructions
- 📋 **Clipboard Integration**: Automatically works with copied text
- 🔄 **Visual Feedback**: Icon changes during processing (🐧 → ⏳ → ✅)
- 🤖 **AI-Powered**: Uses Google Gemini 2.0 Flash for intelligent rephrasing

## 📋 Prerequisites

- macOS 10.13 or later
- Python 3.8 or later
- Google Gemini API Key ([Get one free here](https://makersuite.google.com/app/apikey))

## 🚀 Installation

### 1. Clone or Download the Project

```bash
cd ~/Documents
git clone <your-repo-url>
cd rephrase-python-app
```

Or download and extract the ZIP file.

### 2. Install Python Dependencies

```bash
pip3 install -r requirements.txt
```

This will install:

- `rumps` - macOS menu bar framework
- `pynput` - Global keyboard listener
- `pyperclip` - Clipboard operations
- `python-dotenv` - Environment variable management
- `google-genai` - Google Gemini API client

### 3. Set Up Your API Key

1. Get your free Gemini API key from [Google AI Studio](https://makersuite.google.com/app/apikey)

2. Create a `.env` file from the template:

   ```bash
   cp .env.example .env
   ```

3. Edit `.env` and add your API key:

   ```bash
   nano .env
   ```

   Replace `your-gemini-api-key-here` with your actual API key:

   ```
   GEMINI_API_KEY=your-actual-api-key-here
   ```

### 4. Make the Script Executable

```bash
chmod +x rephrase_enhanced.py
```

## 🎮 Usage

### Starting the App

```bash
python3 rephrase_enhanced.py
```

Or run it directly:

```bash
./rephrase_enhanced.py
```

You'll see a 🐧 penguin icon appear in your menu bar!

### How to Use

#### Method 1: Using the Hotkey (Recommended)

1. Copy any text to your clipboard
2. Press `Cmd + Shift + P` from anywhere
3. Watch the icon change: 🐧 → ⏳ → ✅
4. The rephrased text is automatically copied to your clipboard
5. Paste it wherever you need!

#### Method 2: Using the Menu

1. Click the 🐧 icon in your menu bar
2. Select "Rephrase Clipboard"
3. The rephrased text will be copied to your clipboard

### Selecting a Mode

1. Click the 🐧 icon
2. Hover over "Preset Modes"
3. Select your desired mode:
   - **Polite** - For courteous communication
   - **Professional** - For business emails and documents
   - **Casual** - For friendly messages
   - **Concise** - To shorten lengthy text
   - **Detailed** - To expand brief text
   - **Simple** - To simplify complex language

### Using Custom Prompts

1. Click the 🐧 icon
2. Select "Custom Prompt..."
3. Enter your custom instruction (e.g., "Rephrase this as a haiku")
4. Click "Set"
5. Now use the hotkey or menu to rephrase with your custom prompt

## 🔧 macOS Permissions

On first run, macOS will ask for permissions:

### Accessibility Access (Required for Hotkey)

1. Go to **System Preferences** → **Security & Privacy** → **Privacy** → **Accessibility**
2. Click the lock icon to make changes
3. Add **Terminal** or **Python** (depending on how you run it)
4. Enable the checkbox
5. Restart the app

### Input Monitoring (May be Required)

1. Go to **System Preferences** → **Security & Privacy** → **Privacy** → **Input Monitoring**
2. Add **Terminal** or **Python**
3. Enable the checkbox
4. Restart the app

## 🔄 Running on Startup (Optional)

To make the app start automatically when you log in:

### Using Automator

1. Open **Automator** (Applications → Automator)
2. Create a new **Application**
3. Add "Run Shell Script" action
4. Paste this script (update the path to match your installation):
   ```bash
   cd /Users/YOUR_USERNAME/Documents/rephrase-python-app
   /usr/bin/python3 rephrase_enhanced.py
   ```
5. Save as "Text Rephraser" in Applications
6. Go to **System Preferences** → **Users & Groups** → **Login Items**
7. Click the "+" button and add the "Text Rephraser" app

## 🐛 Troubleshooting

### "GEMINI_API_KEY not found" error

- Make sure `.env` file exists in the app directory
- Verify the API key is correctly set in `.env`
- Check there are no extra spaces or quotes around the key

### Global hotkey doesn't work

- Grant Accessibility permissions (see above)
- Restart the app after granting permissions
- Make sure no other app is using `Cmd+Shift+P`

### "Import rumps could not be resolved"

- Install dependencies: `pip3 install -r requirements.txt`
- Make sure you're using Python 3: `python3 --version`

### API errors

- Verify your Gemini API key is valid
- Check you have internet connection
- Ensure you haven't exceeded API rate limits

### Icon doesn't appear in menu bar

- Check if the app is running: `ps aux | grep rephrase`
- Try running from Terminal to see error messages
- Check Console.app for error logs

## 💰 Cost Considerations

Google Gemini API offers a generous free tier:

- **Free tier**: 15 requests per minute, 1,500 requests per day
- A typical rephrasing request uses ~50-200 tokens
- Most users will stay within the free tier limits

## 📁 Project Structure

```
rephrase-python-app/
├── rephrase_enhanced.py    # Main application
├── requirements.txt        # Python dependencies
├── .env                    # Your API key (not in git)
├── .env.example           # Template for .env
├── .gitignore            # Git ignore rules
└── README.md             # This file
```

## 🔒 Security Notes

- Never commit your `.env` file to git (it's already in `.gitignore`)
- Keep your Gemini API key secure and private
- The app runs locally; no data is sent anywhere except Google's Gemini API
- Each team member should use their own API key

## 🤝 Sharing with Team Members

### For Git Users

1. Push to your repository (the `.env` file is automatically excluded)
2. Team members clone the repo
3. Each person creates their own `.env` file with their API key

### For Non-Git Users

1. Create a ZIP file (excluding `.env`):
   ```bash
   zip -r rephrase-app.zip . -x "*.env" -x "*__pycache__*" -x "*.pyc"
   ```
2. Share the ZIP file
3. Each person follows the installation steps and adds their own API key

## 🗑️ Uninstalling

1. Stop the app (click 🐧 icon → Quit)
2. Remove from Login Items (if added)
3. Delete the app directory:
   ```bash
   rm -rf ~/Documents/rephrase-python-app
   ```

## 📝 License

MIT License - Feel free to use and modify!

## 🙏 Credits

- Built with [rumps](https://github.com/jaredks/rumps) for macOS menu bar integration
- Powered by [Google Gemini AI](https://ai.google.dev/)
- Made with ❤️ for productivity

---

**Enjoy rephrasing! 🐧✨**

For issues or questions, check the Troubleshooting section above or refer to:

- [Google Gemini API Documentation](https://ai.google.dev/docs)
- [Python Documentation](https://www.python.org/doc/)
