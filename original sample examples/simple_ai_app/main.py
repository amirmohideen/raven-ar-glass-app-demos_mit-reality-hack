# Import Raven Framework components
from raven_framework import AsyncRunner, RavenApp, RunApp
from raven_framework.components.cards import TextCardWithButton
from raven_framework.helpers.open_ai_helper import OpenAiHelper
from raven_framework.peripherals.camera import Camera
from raven_framework.peripherals.microphone import Microphone
from raven_framework.peripherals.speaker import Speaker

# OpenAI API key - set this or load from environment variable
OPEN_AI_KEY = ""  # Enter open ai key here or load from env


class SimpleAiApp(RavenApp):
    def __init__(self, parent=None) -> None:
        # Call parent constructor to set up the app
        super().__init__(parent)
        # Create a card with a button for user interaction
        self.card_container = TextCardWithButton(
            text="Ask me anything about what you're looking at!",
            on_button_click=self.on_button_click,
        )
        # Add the card to the app, positioned at the right edge
        self.app.add(
            self.card_container, x=(self.app.width() - self.card_container.width()), y=0
        )
        # Set initial button text
        self.card_container.button.set_text("Start")
        # Initialize sensor and helper objects as None (lazy initialization)
        self.camera = None
        self.agent = None
        self.mic = None
        self.speaker = None
        self.async_runner = None
        # Track recording state
        self.is_recording = False

    def on_button_click(self):
        """Toggle recording and process with AI when button is clicked."""
        if self.is_recording:
            # If currently recording, stop and process
            self.stop_recording_and_process()
        else:
            # If not recording, start recording
            self.start_recording()

    def start_recording(self):
        """Start recording audio from microphone."""
        # Initialize microphone if not already done
        if not self.mic:
            self.mic = Microphone()

        # Start recording audio
        self.mic.start_recording()
        # Update state
        self.is_recording = True
        # Update UI to show recording state
        self.card_container.button.set_text("Stop")
        self.card_container.button.set_enabled(True)
        self.card_container.text_box.set_text("Recording... Click again to stop!")
        print("Recording started")

    def stop_recording_and_process(self):
        """Stop recording, transcribe, process with image, and play response."""
        # Check if microphone is initialized
        if not self.mic:
            self.card_container.text_box.set_text("Error: Microphone not initialized")
            self.card_container.button.set_enabled(True)
            return

        # Stop recording and get audio bytes
        wav_bytes = self.mic.stop_recording()
        # Update state
        self.is_recording = False
        # Update button text
        self.card_container.button.set_text("Start")

        # Check if audio was actually recorded
        if not wav_bytes:
            self.card_container.text_box.set_text("No audio recorded. Try again.")
            self.card_container.button.set_enabled(True)
            print("No audio recorded")
            return

        print(f"Audio recorded, {len(wav_bytes)} bytes")
        # Update UI to show processing state
        self.card_container.text_box.set_text("Processing...")
        self.card_container.button.set_text("...")
        self.card_container.button.set_disabled(True)

        # Initialize OpenAI helper if not already done
        if not self.agent:
            if OPEN_AI_KEY == "":
                print("Open AI Key missing")
                return
            self.agent = OpenAiHelper(OPEN_AI_KEY)

        # Initialize camera if not already done
        if not self.camera:
            self.camera = Camera()

        # Initialize speaker if not already done
        if not self.speaker:
            self.speaker = Speaker()

        # Initialize async runner if not already done
        if not self.async_runner:
            self.async_runner = AsyncRunner()

        # Define async function to process AI (runs in background thread)
        def run_ai():
            try:
                # Step 1: Transcribe the audio to text using Whisper
                text = self.agent.transcribe_audio(wav_bytes)
                print(f"Transcribed text: {text}")

                # Step 2: Capture image from camera
                frame = self.camera.capture_camera_image_and_close()

                if frame is None:
                    # If no image available, use text-only response
                    response = self.agent.get_text_response(
                        f"{text} (Reply as short as possible)"
                    )
                    print("No camera image, using text-only response")
                else:
                    # Step 3: Process image with transcribed text using multimodal model
                    prompt = f"{text} (Reply as short as possible)"
                    response = self.agent.process_multimodal_with_image(
                        prompt=prompt, image=frame
                    )
                    print(f"AI response: {response}")

                # Step 4: Store the response and generate text-to-speech audio
                self.ai_response = response
                self.ai_audio_bytes = self.agent.generate_tts(response)

            except Exception as e:
                # Handle any errors during processing
                print(f"Failed to process: {e}")
                self.ai_response = f"Error: {str(e)}"
                self.ai_audio_bytes = None

        # Define callback to update UI and play audio (runs on main thread)
        def on_complete():
            # Update UI with the AI response
            if hasattr(self, "ai_response"):
                self.card_container.text_box.set_text(self.ai_response)
                # Play the audio response if available
                if hasattr(self, "ai_audio_bytes") and self.ai_audio_bytes:
                    self.speaker.play_audio(self.ai_audio_bytes)
            # Reset button state
            self.card_container.button.set_text("Start")
            self.card_container.button.set_enabled(True)

        # Run AI processing asynchronously (won't block the UI)
        self.async_runner.run(run_ai, on_complete=on_complete)


if __name__ == "__main__":
    RunApp.run(lambda: SimpleAiApp(), app_id="", app_key="")
