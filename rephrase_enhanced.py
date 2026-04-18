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
import queue

# Load environment variables
load_dotenv()

# Preset modes with their prompts - Specialized for professional workplace communication
PRESET_MODES = {
    "Default": "Rephrase the provided text to be professional, concise, and diplomatic. Strictly remove all filler words (e.g., 'just,' 'actually,' 'I think,' 'kind of') and weak language. The goal is to sound authoritative yet respectful. Ensure the output is brief and suitable for high-level corporate communication. Maintain the original intent but polish the delivery for maximum clarity. IMPORTANT: If the input has multiple paragraphs or line breaks, preserve the paragraph structure in your output. Provide only ONE rephrased version, no options or alternatives:",
    
    "Work Update": "Transform this text into a clear, action-oriented status update. Remove all technical jargon and replace it with plain English that any stakeholder can understand. Focus on active verbs (e.g., 'Completed,' 'Launched,' 'Resolved'). Strip away all weak phrasing and filler words. The final text should clearly communicate progress, impact, and next steps without any fluff. IMPORTANT: If the input has multiple paragraphs or line breaks, preserve the paragraph structure in your output. Provide only ONE rephrased version, no options or alternatives:",
    
    "Pitch": "Rephrase this into a persuasive proposal or pitch. Use collaborative language (focus on 'we' and 'our') to invite the reader into the idea. Maintain a tone of 'humble confidence'—be convincing and optimistic about the potential of the idea without sounding arrogant or demanding. Frame suggestions as exciting opportunities for the team to explore together. IMPORTANT: If the input has multiple paragraphs or line breaks, preserve the paragraph structure in your output. Provide only ONE rephrased version, no options or alternatives:",
    
    "Feedback": "Rephrase this response to be strictly neutral, objective, and constructive. Remove personal pronouns where possible to focus on the work or the system rather than the individual. Eliminate all defensive tone and filler words. The goal is to provide a logic-based explanation or piece of feedback that is helpful and growth-oriented. Ensure the tone remains professional and detached from emotion. IMPORTANT: If the input has multiple paragraphs or line breaks, preserve the paragraph structure in your output. Provide only ONE rephrased version, no options or alternatives:",
}

class RephraserApp(rumps.App):
    def __init__(self):
        super(RephraserApp, self).__init__(
            "✏️",
            icon=None,
            quit_button=None
        )
        self.is_processing = False
        self.current_mode = "Default"  # Default mode
        self.custom_prompt = ""
        self.current_provider = "Gemini"  # Default provider
        self.failed_providers = set()  # Track failed providers for this session
        
        # Queue for hotkey actions to be executed on main thread
        self.action_queue = queue.Queue()
        
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
        
        # Start action queue processor
        self.start_action_processor()
    
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
            rumps.MenuItem("Restart App", callback=self.restart_app),
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
        """Reset failed providers to allow retry
        
        When an AI provider (Gemini, Groq, or HuggingFace) hits a rate limit,
        it's marked as 'failed' to avoid repeated failed attempts. This option
        clears that list so you can try those providers again.
        """
        self.failed_providers.clear()
        self.build_menu()  # Rebuild menu to update status
        
        rumps.notification(
            title="Providers Reset",
            subtitle="All providers available again",
            message="Failed providers have been reset and can be retried"
        )
    
    def restart_app(self, _):
        """Restart the application"""
        import sys
        import subprocess
        
        rumps.notification(
            title="Restarting...",
            subtitle="Application will restart now",
            message=""
        )
        
        # Get the path to the current script
        script_path = os.path.abspath(__file__)
        
        # Kill any existing instances first to prevent duplicates
        try:
            subprocess.run([
                'pkill', '-f', 'rephrase_enhanced.py'
            ], check=False)
            time.sleep(0.5)  # Wait for processes to terminate
        except Exception as e:
            print(f"Error killing existing instances: {e}")
        
        # Start new instance
        subprocess.Popen([sys.executable, script_path])
        
        # Quit current instance
        rumps.quit_application()
    
    
    def show_about(self, _):
        """Show about dialog"""
        rumps.alert(
            title="Text Rephraser",
            message="A lightweight menu bar app for rephrasing text using AI.\n\n"
                   "Hotkeys:\n"
                   "• Cmd+Shift+P - Quick rephrase\n"
                   "• Cmd+Shift+M - Mode selection\n\n"
                   "Features:\n"
                   "• Multi-provider AI (Gemini, Groq, HuggingFace)\n"
                   "• Automatic fallback\n"
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
    
    
    def start_action_processor(self):
        """Process queued actions on the main thread"""
        @rumps.timer(0.1)
        def process_actions(_):
            try:
                while not self.action_queue.empty():
                    action = self.action_queue.get_nowait()
                    action()
            except queue.Empty:
                pass
    
    def start_hotkey_listener(self):
        """Start listening for global hotkeys"""
        # Track currently pressed keys
        current_keys = set()
        last_trigger_time = {'quick': 0.0, 'modal': 0.0}
        triggered = {'quick': False, 'modal': False}
        modal_is_open = {'value': False}  # Track if modal is currently open
        
        def on_quick_rephrase():
            # Debounce - prevent multiple triggers within 0.5 seconds
            current_time = time.time()
            if current_time - last_trigger_time['quick'] < 0.5:
                return
            last_trigger_time['quick'] = current_time
            
            print("Quick rephrase triggered (Cmd+Shift+P)")
            # Queue action to be executed on main thread
            self.action_queue.put(lambda: self.rephrase_clipboard(None))
        
        def on_modal_rephrase():
            # Prevent opening modal if already open
            if modal_is_open['value']:
                print("Modal already open, ignoring trigger")
                return
            
            # Debounce - prevent multiple triggers within 0.5 seconds
            current_time = time.time()
            if current_time - last_trigger_time['modal'] < 0.5:
                return
            last_trigger_time['modal'] = current_time
            
            print("Modal rephrase triggered (Cmd+Shift+M)")
            modal_is_open['value'] = True
            
            # Queue action to be executed on main thread
            def show_modal_and_reset():
                try:
                    self.show_mode_selection_modal()
                finally:
                    modal_is_open['value'] = False
            
            self.action_queue.put(show_modal_and_reset)
        
        def check_hotkey_combination():
            """Check if a valid hotkey combination is pressed"""
            # Check for Cmd (either left or right)
            cmd_pressed = (keyboard.Key.cmd in current_keys or
                          keyboard.Key.cmd_r in current_keys)
            
            # Check for Shift (either left or right)
            shift_pressed = (keyboard.Key.shift in current_keys or
                           keyboard.Key.shift_r in current_keys)
            
            if not (cmd_pressed and shift_pressed):
                return None
            
            # MUST have exactly 3 keys: Cmd + Shift + (P or M)
            # This prevents triggering on just Cmd+Shift
            if len(current_keys) < 3:
                return None
            
            # Check for specific character keys - look for P or M
            has_p = False
            has_m = False
            
            for key in current_keys:
                try:
                    if hasattr(key, 'char') and key.char:
                        char = key.char.lower()
                        if char == 'p':
                            has_p = True
                        elif char == 'm':
                            has_m = True
                except (AttributeError, TypeError):
                    continue
            
            # Only return a hotkey if we have the letter key
            # Prioritize 'p' over 'm' if both are somehow pressed
            if has_p:
                return 'quick'
            elif has_m:
                return 'modal'
            
            return None
        
        def on_press(key):
            # Add key to current set
            try:
                current_keys.add(key)
            except:
                pass
            
            # Check for hotkey combinations
            hotkey = check_hotkey_combination()
            
            # Only trigger once per key combination press
            if hotkey == 'quick' and not triggered['quick']:
                triggered['quick'] = True
                on_quick_rephrase()
            elif hotkey == 'modal' and not triggered['modal']:
                triggered['modal'] = True
                on_modal_rephrase()
        
        def on_release(key):
            # Remove key from current set
            try:
                current_keys.discard(key)
                
                # Reset trigger flags when ANY key in the combination is released
                if key in [keyboard.Key.cmd, keyboard.Key.cmd_r,
                          keyboard.Key.shift, keyboard.Key.shift_r]:
                    triggered['quick'] = False
                    triggered['modal'] = False
                
                # Also reset when character keys are released
                if hasattr(key, 'char') and key.char:
                    char = key.char.lower()
                    if char == 'p':
                        triggered['quick'] = False
                    elif char == 'm':
                        triggered['modal'] = False
            except:
                pass
        
        # Start the listener
        listener = keyboard.Listener(
            on_press=on_press,
            on_release=on_release
        )
        
        listener.start()
        print("Hotkey listener started successfully")
        print("  Cmd+Shift+P - Quick rephrase (current mode)")
        print("  Cmd+Shift+M - Mode selection modal")
    
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
                contents=prompt,
                config={
                    'temperature': 0.7,
                    'max_output_tokens': 1024
                }
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
            self.title = "✏️"
            
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            print(f"Error during rephrasing: {error_details}")
            # Change icon back to normal
            self.title = "✏️"
            
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
