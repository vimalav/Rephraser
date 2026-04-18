# ✏️ Text Rephraser - AI-Powered Menu Bar App

A lightweight macOS menu bar application that rephrases clipboard text using multiple AI providers with automatic fallback. Features multiple preset modes, custom prompts, and seamless clipboard integration.

## ✨ Features

- ✏️ **Menu Bar Integration**: Lives in your macOS menu bar with a pencil icon
- ⌨️ **Global Hotkeys**:
  - `Cmd + Shift + P` - Quick rephrase with current mode
  - `Cmd + Shift + M` - Show mode selection modal
- 🎯 **Specialized Preset Modes**:
  - **Default**: Professional, concise, diplomatic communication (removes filler words)
  - **Work Update**: Clear, action-oriented status updates with active verbs
  - **Pitch**: Persuasive proposals with collaborative language and humble confidence
  - **Feedback**: Neutral, objective, constructive feedback focused on growth
- ✏️ **Custom Prompts**: Create your own rephrasing instructions
- 📋 **Clipboard Integration**: Automatically works with copied text
- 🔄 **Visual Feedback**: Icon changes during processing (✏️ → ⏳ → ✅)
- 🤖 **Multi-Provider AI Support**:
  - **Google Gemini** (Primary) - Fast and reliable
  - **Groq** (Fallback) - High-speed inference
  - **Hugging Face** (Fallback) - Open-source models
- 🔁 **Automatic Fallback**: Seamlessly switches providers if one fails or hits quota limits
- 📊 **Provider Status**: View which providers are available in the menu

## 📋 Prerequisites

- macOS 10.13 or later
- Python 3.8 or later
- At least one API key from:
  - Google Gemini API Key ([Get one free here](https://makersuite.google.com/app/apikey))
  - Groq API Key ([Get one free here](https://console.groq.com/keys))
  - Hugging Face Token ([Get one free here](https://huggingface.co/settings/tokens))

## 🚀 Installation

### 1. Clone or Download the Project

```bash
cd ~/Documents
git clone https://github.com/vimalav/Rephraser.git
cd Rephraser
```

Or download and extract the ZIP file from the repository.

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
- `groq` - Groq API client
- `huggingface-hub` - Hugging Face API client

### 3. Set Up Your API Keys

1. Get API keys from one or more providers:
   - [Google Gemini API](https://makersuite.google.com/app/apikey) (Recommended)
   - [Groq API](https://console.groq.com/keys) (Fast fallback)
   - [Hugging Face Token](https://huggingface.co/settings/tokens) (Open-source fallback)

2. Create a `.env` file from the template:

   ```bash
   cp .env.example .env
   ```

3. Edit `.env` and add your API keys:

   ```bash
   nano .env
   ```

   Add at least one API key (all three recommended for best reliability):

   ```
   GEMINI_API_KEY=your-gemini-api-key-here
   GROQ_API_KEY=your-groq-api-key-here
   HF_TOKEN=your-huggingface-token-here
   ```

   **Note**: The app will automatically use available providers and fall back to others if one fails or hits quota limits.

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

You'll see a ✏️ pencil icon appear in your menu bar!

### How to Use

#### Method 1: Quick Rephrase (Fastest)

1. Copy any text to your clipboard
2. Press `Cmd + Shift + P` from anywhere
3. Watch the icon change: ✏️ → ⏳ → ✅
4. The rephrased text is automatically copied to your clipboard
5. Paste it wherever you need!

#### Method 2: Rephrase with Mode Selection

1. Copy any text to your clipboard
2. Press `Cmd + Shift + M` from anywhere
3. A modal appears showing:
   - All preset modes (Polite, Professional, Casual, etc.)
   - Custom prompt field
4. Select a mode or enter a custom prompt
5. Click "Rephrase" or press Enter
6. The rephrased text is copied to your clipboard

#### Method 3: Using the Menu

1. Click the ✏️ icon in your menu bar
2. Select "Rephrase Clipboard"
3. The rephrased text will be copied to your clipboard

### Selecting a Mode

1. Click the ✏️ icon
2. Hover over "Preset Modes"
3. Select your desired mode:
   - **Default** - Professional, concise communication (removes filler words and weak language)
   - **Work Update** - Clear status updates with active verbs (Completed, Launched, Resolved)
   - **Pitch** - Persuasive proposals with collaborative "we/our" language
   - **Feedback** - Neutral, objective feedback focused on work/system, not individuals

### Using Custom Prompts

1. Click the ✏️ icon
2. Select "Custom Prompt..."
3. Enter your custom instruction (e.g., "Rephrase this as a haiku")
4. Click "Set"
5. Now use the hotkey or menu to rephrase with your custom prompt

### Checking Provider Status

1. Click the ✏️ icon
2. Hover over "Provider Status" to see:
   - ✅ Available - Provider is working
   - ❌ Failed - Provider hit quota or failed
3. Use "Reset Failed Providers" to retry failed providers

## � macOS Permissions

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

## 🔄 Running on Startup (Recommended)

The app includes a launch agent for automatic startup. To enable it:

### Using Launch Agent (Recommended)

1. Copy the launch agent file:

   ```bash
   cp com.textrephraser.plist ~/Library/LaunchAgents/
   ```

2. Load the launch agent:

   ```bash
   launchctl load ~/Library/LaunchAgents/com.textrephraser.plist
   ```

3. The app will now start automatically on every login!

**Managing Auto-Start:**

- **Check status**: `launchctl list | grep textrephraser`
- **Disable**: `launchctl unload ~/Library/LaunchAgents/com.textrephraser.plist`
- **Re-enable**: `launchctl load ~/Library/LaunchAgents/com.textrephraser.plist`
- **Remove**: `launchctl unload ~/Library/LaunchAgents/com.textrephraser.plist && rm ~/Library/LaunchAgents/com.textrephraser.plist`

### Alternative: Using Automator

If you prefer Automator:

1. Open **Automator** (Applications → Automator)
2. Create a new **Application**
3. Add "Run Shell Script" action
4. Paste this script (update the path to match your installation):
   ```bash
   cd /Users/YOUR_USERNAME/Documents/Rephraser
   /usr/bin/python3 rephrase_enhanced.py
   ```
5. Save as "Text Rephraser" in Applications
6. Go to **System Preferences** → **Users & Groups** → **Login Items**
7. Click the "+" button and add the "Text Rephraser" app

## 🐛 Troubleshooting

### "API_KEY not found" error

- Make sure `.env` file exists in the app directory
- Verify at least one API key is correctly set in `.env`
- Check there are no extra spaces or quotes around the keys

### Global hotkey doesn't work

- Grant Accessibility permissions (see above)
- Restart the app after granting permissions
- Make sure no other app is using `Cmd+Shift+P` or `Cmd+Shift+M`

### "Import rumps could not be resolved"

- Install dependencies: `pip3 install -r requirements.txt`
- Make sure you're using Python 3: `python3 --version`

### API errors or "All providers failed"

- Verify at least one API key is valid
- Check you have internet connection
- If one provider fails, the app will automatically try others
- Use "Reset Failed Providers" menu option to retry failed providers
- Check provider status in the menu

### Icon doesn't appear in menu bar

- Check if the app is running: `ps aux | grep rephrase`
- Try running from Terminal to see error messages
- Check Console.app for error logs

## 💰 Cost Considerations

All three providers offer generous free tiers:

### Google Gemini (Primary)

- **Free tier**: 15 requests per minute, 1,500 requests per day
- Fast and reliable for most use cases

### Groq (Fallback)

- **Free tier**: High-speed inference with generous limits
- Excellent for when Gemini quota is exhausted

### Hugging Face (Fallback)

- **Free tier**: Access to open-source models
- Good backup option with reasonable limits

**Recommendation**: Configure all three providers for maximum reliability. The app will automatically use the best available provider and fall back to others when needed.

## 📁 Project Structure

```
Rephraser/
├── rephrase_enhanced.py       # Main application
├── requirements.txt           # Python dependencies
├── com.textrephraser.plist   # Launch agent for auto-start
├── .env                       # Your API keys (not in git)
├── .env.example              # Template for .env
├── .gitignore                # Git ignore rules
├── STARTUP_INSTRUCTIONS.md   # Auto-start setup guide
├── LICENSE                   # MIT License
└── README.md                 # This file
```

## 🔒 Security Notes

- Never commit your `.env` file to git (it's already in `.gitignore`)
- Keep all your API keys secure and private
- The app runs locally; no data is sent anywhere except the AI provider APIs
- Each team member should use their own API keys
- Rotate API keys periodically for security

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

1. Stop the app (click ✏️ icon → Quit)
2. Remove the launch agent (if installed):
   ```bash
   launchctl unload ~/Library/LaunchAgents/com.textrephraser.plist
   rm ~/Library/LaunchAgents/com.textrephraser.plist
   ```
3. Delete the app directory:
   ```bash
   rm -rf ~/Documents/Rephraser
   ```

## 📝 License

MIT License - Feel free to use and modify!

## 🙏 Credits

- Built with [rumps](https://github.com/jaredks/rumps) for macOS menu bar integration
- Powered by multiple AI providers:
  - [Google Gemini AI](https://ai.google.dev/)
  - [Groq](https://groq.com/)
  - [Hugging Face](https://huggingface.co/)
- Developed with assistance from **Bob (Cline AI Assistant)**
- Made with ❤️ for productivity

---

## 🚀 Quick Start Summary

```bash
# 1. Clone the repo
git clone https://github.com/vimalav/Rephraser.git
cd Rephraser

# 2. Install dependencies
pip3 install -r requirements.txt

# 3. Set up API keys
cp .env.example .env
nano .env  # Add your API keys

# 4. Run the app
python3 rephrase_enhanced.py

# 5. (Optional) Enable auto-start
cp com.textrephraser.plist ~/Library/LaunchAgents/
launchctl load ~/Library/LaunchAgents/com.textrephraser.plist
```

**Enjoy rephrasing! ✏️✨**

For issues or questions, check the Troubleshooting section above or refer to:

- [Google Gemini API Documentation](https://ai.google.dev/docs)
- [Groq API Documentation](https://console.groq.com/docs)
- [Hugging Face Documentation](https://huggingface.co/docs)
- [Python Documentation](https://www.python.org/doc/)
