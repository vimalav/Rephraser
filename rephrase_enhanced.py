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
from groq import Groq
from huggingface_hub import InferenceClient
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
        self.current_provider = "Gemini"  # Default provider
        self.failed_providers = set()  # Track failed providers for this session
        
        # Initialize API clients
        self.gemini_key = os.getenv('GEMINI_API_KEY')
        self.groq_key = os.getenv('GROQ_API_KEY')
        self.hf_token = os.getenv('HF_TOKEN')
        
        # Check if at least one provider is configured
        if not any([self.gemini_key, self.groq_key, self.hf_token]):
            rumps.alert("Error", "No API keys found in .env file. Please add at least one provider key.")
            rumps.quit_application()
        
        # Initialize clients
        self.gemini_client = genai.Client(api_key=self.gemini_key) if self.gemini_key else None
        self.groq_client = Groq(api_key=self.groq_key) if self.groq_key else None
        self.hf_client = InferenceClient(token=self.hf_token) if self.hf_token else None
        
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
        
        # Provider status submenu
        provider_items = []
        providers = [
            ("Gemini", self.gemini_client),
            ("Groq", self.groq_client),
            ("HuggingFace", self.hf_client)
        ]
        
        for provider_name, client in providers:
            if client:
                status = "❌ Failed" if provider_name in self.failed_providers else "✅ Available"
                item = rumps.MenuItem(f"{provider_name}: {status}")
                provider_items.append(item)
        
        # Main menu
        self.menu = [
            rumps.MenuItem("Rephrase Clipboard", callback=self.rephrase_clipboard),
            None,
            [rumps.MenuItem("Preset Modes"), preset_items],
            rumps.MenuItem("Custom Prompt...", callback=self.set_custom_prompt),
            None,
            [rumps.MenuItem("Provider Status"), provider_items],
            rumps.MenuItem("Reset Failed Providers", callback=self.reset_providers),
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
    def reset_providers(self, _):
        """Reset failed providers to allow retry"""
        self.failed_providers.clear()
        self.build_menu()  # Rebuild menu to update status
        
        rumps.notification(
            title="Providers Reset",
            subtitle="All providers available again",
            message="Failed providers have been reset and can be retried"
        )
    
    
    def show_about(self, _):
        """Show about dialog"""
        rumps.alert(
            title="Text Rephraser",
            message="A lightweight menu bar app for rephrasing text using Google Gemini AI.\n\n"
                   "Hotkeys:\n"
                   "• Cmd+Shift+P - Quick rephrase\n"
                   "• Cmd+Shift+Option+P - Mode selection\n\n"
                   "Features:\n"
                   "• Multiple preset modes\n"
                   "• Custom prompts\n"
                   "• Clipboard integration\n\n"
                   "Made with ❤️"
        )
    
    def show_mode_selection_modal(self):
        """Show modal for selecting rephrasing mode"""
        # Get clipboard text first
        try:
            text = pyperclip.paste()
            if not text or not text.strip():
                rumps.alert("Error", "No text found in clipboard")
                return
        except Exception as e:
            rumps.alert("Error", f"Could not read clipboard: {str(e)}")
            return
        
        # Create mode selection window
        mode_options = list(PRESET_MODES.keys())
        current_index = mode_options.index(self.current_mode) if self.current_mode in mode_options else 0
        
        # Build message with mode options
        message = "Select a rephrasing mode:\n\n"
        for i, mode in enumerate(mode_options, 1):
            marker = "●" if mode == self.current_mode else "○"
            message += f"{marker} {i}. {mode}\n"
        message += "\nOr enter a custom prompt below:"
        
        window = rumps.Window(
            title="Select Rephrasing Mode",
            message=message,
            default_text=self.custom_prompt if self.custom_prompt else "",
            ok="Rephrase",
            cancel="Cancel",
            dimensions=(400, 200)
        )
        
        response = window.run()
        
        if response.clicked:
            custom_text = response.text.strip()
            
            if custom_text:
                # User entered custom prompt
                self.custom_prompt = custom_text
                self.current_mode = "Custom"
                
                # Uncheck all preset modes
                for item in self.menu["Preset Modes"].values():
                    item.state = False
            
            # Now rephrase with selected/current mode
            thread = threading.Thread(target=self._process_rephrase, args=(text,))
            thread.daemon = True
            thread.start()
    
    
    def start_hotkey_listener(self):
        """Start listening for global hotkeys"""
        # Track currently pressed keys
        current_keys = set()
        
        def on_quick_rephrase():
            print("Quick rephrase triggered")
            self.rephrase_clipboard(None)
        
        def on_modal_rephrase():
            print("Modal rephrase triggered")
            self.show_mode_selection_modal()
        
        def on_press(key):
            # Add key to current set
            try:
                current_keys.add(key)
            except:
                pass
            
            # Check for Cmd+Shift+Option+P (modal) - check this FIRST
            if (keyboard.Key.cmd in current_keys and
                keyboard.Key.shift in current_keys and
                keyboard.Key.alt in current_keys and
                (hasattr(key, 'char') and key.char == 'p')):
                on_modal_rephrase()
                current_keys.clear()
                return
            
            # Check for Cmd+Shift+P (quick rephrase) - check this SECOND
            if (keyboard.Key.cmd in current_keys and
                keyboard.Key.shift in current_keys and
                keyboard.Key.alt not in current_keys and  # Make sure Option is NOT pressed
                (hasattr(key, 'char') and key.char == 'p')):
                on_quick_rephrase()
                current_keys.clear()
                return
        
        def on_release(key):
            # Remove key from current set
            try:
                current_keys.discard(key)
            except:
                pass
        
        listener = keyboard.Listener(
            on_press=on_press,
            on_release=on_release
        )
        
        listener.start()
        print("Hotkey listener started")
        print("  Cmd+Shift+P - Quick rephrase")
        print("  Cmd+Shift+Option+P - Mode selection modal")
    
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
    
    def _rephrase_with_gemini(self, prompt):
        """Try to rephrase using Gemini"""
        if not self.gemini_client or "Gemini" in self.failed_providers:
            return None
        
        try:
            response = self.gemini_client.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt
            )
            return response.text if response.text else None
        except Exception as e:
            error_str = str(e)
            if "429" in error_str or "RESOURCE_EXHAUSTED" in error_str:
                self.failed_providers.add("Gemini")
            raise
    
    def _rephrase_with_groq(self, prompt):
        """Try to rephrase using Groq"""
        if not self.groq_client or "Groq" in self.failed_providers:
            return None
        
        try:
            response = self.groq_client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=1024
            )
            return response.choices[0].message.content if response.choices else None
        except Exception as e:
            error_str = str(e)
            if "429" in error_str or "rate_limit" in error_str.lower():
                self.failed_providers.add("Groq")
            raise
    
    def _rephrase_with_hf(self, prompt):
        """Try to rephrase using Hugging Face"""
        if not self.hf_client or "HuggingFace" in self.failed_providers:
            return None
        
        try:
            response = self.hf_client.text_generation(
                prompt,
                model="meta-llama/Llama-3.2-3B-Instruct",
                max_new_tokens=512,
                temperature=0.7
            )
            return response if response else None
        except Exception as e:
            error_str = str(e)
            if "429" in error_str or "rate" in error_str.lower():
                self.failed_providers.add("HuggingFace")
            raise
    
    def _process_rephrase(self, text):
        """Process the rephrasing in background with fallback"""
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
            
            rephrased_text = None
            provider_used = None
            
            # Try providers in order: Gemini -> Groq -> HuggingFace
            providers = [
                ("Gemini", self._rephrase_with_gemini),
                ("Groq", self._rephrase_with_groq),
                ("HuggingFace", self._rephrase_with_hf)
            ]
            
            for provider_name, rephrase_func in providers:
                if provider_name in self.failed_providers:
                    continue
                
                try:
                    rephrased_text = rephrase_func(prompt)
                    if rephrased_text:
                        provider_used = provider_name
                        break
                except Exception as e:
                    print(f"{provider_name} failed: {e}")
                    continue
            
            if not rephrased_text:
                raise Exception("All providers failed or returned empty response")
            
            # Copy to clipboard
            pyperclip.copy(rephrased_text)
            
            # Change icon to success
            self.title = "✅"
            
            # Show success notification
            rumps.notification(
                title="✅ Done!",
                subtitle=f"Rephrased using: {provider_used}",
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
