# Auto-Start Setup Instructions

## ✅ Setup Complete!

Your Text Rephraser app is now configured to start automatically when you log in to your Mac.

## What Was Done

1. **Created Launch Agent**: `com.textrephraser.plist`
2. **Installed**: Copied to `~/Library/LaunchAgents/`
3. **Activated**: Loaded with `launchctl`
4. **Verified**: App is currently running (PID: 33420)

## How It Works

The launch agent will:

- Start the app automatically when you log in
- Run in the background
- Show the 🐧 icon in your menu bar
- Keep logs in the app directory

## Managing the Auto-Start

### Check if it's running:

```bash
launchctl list | grep textrephraser
ps aux | grep rephrase_enhanced.py | grep -v grep
```

### Stop the app:

```bash
launchctl unload ~/Library/LaunchAgents/com.textrephraser.plist
```

### Start the app manually:

```bash
launchctl load ~/Library/LaunchAgents/com.textrephraser.plist
```

### Disable auto-start (remove from login):

```bash
launchctl unload ~/Library/LaunchAgents/com.textrephraser.plist
rm ~/Library/LaunchAgents/com.textrephraser.plist
```

### Re-enable auto-start:

```bash
cp com.textrephraser.plist ~/Library/LaunchAgents/
launchctl load ~/Library/LaunchAgents/com.textrephraser.plist
```

## Log Files

If you need to troubleshoot, check these log files in the app directory:

- `rephraser.log` - Standard output
- `rephraser.error.log` - Error messages

## Testing

1. **Current Status**: The app is running now! Look for the 🐧 icon in your menu bar.
2. **Test the hotkey**: Copy some text and press `Cmd+Shift+R`
3. **Test on next login**: Log out and log back in - the app should start automatically

## Notes

- The app will start automatically on every login
- No terminal window will appear (runs in background)
- The 🐧 icon will appear in your menu bar when running
- If you move the app folder, you'll need to update the plist file paths

## Troubleshooting

If the app doesn't start on login:

1. Check the log files for errors
2. Verify the paths in `com.textrephraser.plist` are correct
3. Make sure you have Accessibility permissions granted
4. Try unloading and reloading the launch agent

---

**Made with ❤️ by Bob**
