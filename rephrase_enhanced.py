#!/usr/bin/env python3
"""
Text Rephraser - Enhanced Menu Bar App
A lightweight menu bar application that rephrases clipboard text using Google Gemini API
with multiple preset modes and custom prompts
"""

import rumps
import os
from dotenv import load_dotenv
from google import genai
import pyperclip
from pynput import keyboard
import threading
import time

# Load environment variables
load_dotenv()

# Preset modes with their prompts
PRESET_MODES = {
    "Polite": "Rephrase the following text to be more polite and courteous while maintaining the original meaning. Provide only ONE rephrased version, no options or alternatives:",
    "Professional": "Rephrase the following text to be more professional and formal while maintaining the original meaning. Provide only ONE rephrased version, no options or alternatives:",
    "Casual": "Rephrase the following text to be more casual and friendly while maintaining the original meaning. Provide only ONE rephrased version, no options or alternatives:",
    "Concise": "Rephrase the following text to be more concise and brief while maintaining the original meaning. Provide only ONE rephrased version, no options or alternatives:",
    "Detailed": "Rephrase the following text to be more detailed and elaborate while maintaining the original meaning. Provide only ONE rephrased version, no options or alternatives:",
    "Simple": "Rephrase the following text using simpler words and shorter sentences while maintaining the original meaning. Provide only ONE rephrased version, no options or alternatives:",
}

class RephraserApp(rumps.App):
    def __init__(self):
        super(RephraserApp, self).__init__(
            "🐧",
            icon=None,
            quit_button=None
        )
        self.is_processing = False
        self.current_mode = "Professional"  # Default mode
        self.custom_prompt = ""
        
        # Initialize Gemini API
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            rumps.alert("Error", "GEMINI_API_KEY not found in .env file")
            rumps.quit_application()
        
        self.client = genai.Client(api_key=api_key)
        
        # Build menu
        self.build_menu()
        
        # Start global hotkey listener
        self.start_hotkey_listener()
    
    def build_menu(self):
        """Build the menu structure"""
        # Preset modes submenu
        preset_items = []
        for mode in PRESET_MODES.keys():
            item = rumps.MenuItem(
                mode,
                callback=self.select_mode
            )
            if mode == self.current_mode:
                item.state = True
            preset_items.append(item)
        
        # Main menu
        self.menu = [
            rumps.MenuItem("Rephrase Clipboard", callback=self.rephrase_clipboard),
            None,
            [rumps.MenuItem("Preset Modes"), preset_items],
            rumps.MenuItem("Custom Prompt...", callback=self.set_custom_prompt),
            None,
            rumps.MenuItem("About", callback=self.show_about),
            rumps.MenuItem("Quit", callback=self.quit_app)
        ]
    
    def select_mode(self, sender):
        """Handle preset mode selection"""
        # Uncheck all modes
        for item in self.menu["Preset Modes"].values():
            item.state = False
        
        # Check selected mode
        sender.state = True
        self.current_mode = sender.title
        self.custom_prompt = ""  # Clear custom prompt when selecting preset
        
        rumps.notification(
            title="Mode Changed",
            subtitle=f"Now using: {self.current_mode}",
            message="Copy text and press Cmd+Shift+P to rephrase"
        )
    
    def set_custom_prompt(self, _):
        """Set a custom prompt"""
        window = rumps.Window(
            title="Custom Prompt",
            message="Enter your custom rephrasing instruction:",
            default_text=self.custom_prompt or "Rephrase the following text to...",
            ok="Set",
            cancel="Cancel",
            dimensions=(320, 100)
        )
        
        response = window.run()
        
        if response.clicked:
            self.custom_prompt = response.text.strip()
            if self.custom_prompt:
                # Uncheck all preset modes
                for item in self.menu["Preset Modes"].values():
                    item.state = False
                
                self.current_mode = "Custom"
                
                rumps.notification(
                    title="Custom Prompt Set",
                    subtitle="Using custom prompt",
                    message="Copy text and press Cmd+Shift+P to rephrase"
                )
    
    def show_about(self, _):
        """Show about dialog"""
        rumps.alert(
            title="Text Rephraser",
            message="A lightweight menu bar app for rephrasing text using Google Gemini AI.\n\n"
                   "Hotkey: Cmd+Shift+P\n\n"
                   "Features:\n"
                   "• Multiple preset modes\n"
                   "• Custom prompts\n"
                   "• Clipboard integration\n\n"
                   "Made with ❤️"
        )
    
    def start_hotkey_listener(self):
        """Start listening for global hotkey Cmd+Shift+P"""
        def on_activate():
            self.rephrase_clipboard(None)
        
        def for_canonical(f):
            return lambda k: f(listener.canonical(k))
        
        hotkey = keyboard.HotKey(
            keyboard.HotKey.parse('<cmd>+<shift>+p'),
            on_activate
        )
        
        listener = keyboard.Listener(
            on_press=for_canonical(hotkey.press),
            on_release=for_canonical(hotkey.release)
        )
        
        listener.start()
    
    @rumps.clicked("Rephrase Clipboard")
    def rephrase_clipboard(self, _):
        """Rephrase text from clipboard"""
        if self.is_processing:
            rumps.alert("Processing", "Already processing a request. Please wait.")
            return
        
        # Get text from clipboard
        try:
            text = pyperclip.paste()
            if not text or not text.strip():
                rumps.alert("Error", "No text found in clipboard")
                return
        except Exception as e:
            rumps.alert("Error", f"Could not read clipboard: {str(e)}")
            return
        
        # Process in background thread
        thread = threading.Thread(target=self._process_rephrase, args=(text,))
        thread.daemon = True
        thread.start()
    
    def _process_rephrase(self, text):
        """Process the rephrasing in background"""
        self.is_processing = True
        
        # Change icon to processing
        self.title = "⏳"
        
        try:
            # Get the prompt based on current mode
            if self.current_mode == "Custom" and self.custom_prompt:
                prompt = f"{self.custom_prompt}\n\n{text}"
            else:
                base_prompt = PRESET_MODES.get(self.current_mode, PRESET_MODES["Professional"])
                prompt = f"{base_prompt}\n\n{text}"
            
            # Call Gemini API
            response = self.client.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt
            )
            
            rephrased_text = response.text
            
            # Handle None response
            if not rephrased_text:
                raise Exception("No response from Gemini API")
            
            # Copy to clipboard
            pyperclip.copy(rephrased_text)
            
            # Change icon to success
            self.title = "✅"
            
            # Show success notification
            rumps.notification(
                title="✅ Done!",
                subtitle=f"Rephrased using: {self.current_mode}",
                message=rephrased_text[:100] + ("..." if len(rephrased_text) > 100 else "")
            )
            
            # Reset icon after 2 seconds
            time.sleep(2)
            self.title = "🐧"
            
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            print(f"Error during rephrasing: {error_details}")
            # Change icon back to normal
            self.title = "🐧"
            
            rumps.notification(
                title="❌ Error",
                subtitle="Failed to rephrase",
                message=str(e)
            )
        
        finally:
            self.is_processing = False
    
    @rumps.clicked("Quit")
    def quit_app(self, _):
        """Quit the application"""
        rumps.quit_application()

if __name__ == "__main__":
    app = RephraserApp()
    app.run()

# Made with Bob
