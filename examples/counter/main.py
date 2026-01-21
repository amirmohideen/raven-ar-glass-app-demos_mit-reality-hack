# Imports
from enum import Enum

# Raven Framework Imports
from raven_framework import RavenApp, Routine, RunApp, fade_in
from raven_framework.components.cards import TextCardWithButton, TextCardWithTwoButtons

# Constants - maximum time to display, container width, and font size
MAX_TIME = 3600
CONTAINER_WIDTH = 450
DISPLAY_FONT_SIZE = 38


# Helper function to convert seconds to MM:SS format
def seconds_to_time_string(seconds: int) -> str:
    # Check if time exceeds maximum
    if seconds > MAX_TIME:
        return "Max time reached"
    # Calculate minutes by integer division
    minutes = seconds // 60
    # Calculate remaining seconds using modulo
    seconds = seconds % 60
    # Format as MM:SS with zero-padding
    return f"{minutes:02d}:{seconds:02d}"


# Enum to represent the different states of the stopwatch
class AppState(Enum):
    """Application state enumeration."""

    # Stopwatch is actively counting
    RUNNING = "running"
    # Stopwatch is paused (time preserved)
    PAUSED = "paused"
    # Stopwatch is stopped
    STOPPED = "stopped"


# Application
class Stopwatch(RavenApp):
    """Stopwatch application with start, pause, resume, and reset functionality."""

    def __init__(self, parent=None) -> None:
        """Initialize the Stopwatch application."""
        # Call parent constructor to set up the app
        super().__init__(parent)
        # Initialize app state to stopped
        self.app_state = AppState.STOPPED
        # Initialize elapsed time to 0 seconds
        self.elapsed_time = 0
        # Routine will be created when stopwatch starts
        self.stopwatch_routine = None
        # Initialize the UI
        self.init_ui()
        # Fade in animation for smooth appearance
        fade_in(self.app)

    def init_ui(self):
        """Initialize the UI based on the current application state."""
        # Clear the app to remove any existing widgets
        self.app.clear()
        self.main_container = None

        # Create different UI based on current state
        if self.app_state == AppState.STOPPED:
            if self.elapsed_time > 0:
                # If time exists, show Resume and Reset buttons
                self.main_container = TextCardWithTwoButtons(
                    text=seconds_to_time_string(self.elapsed_time),
                    button_text_1="Resume",
                    button_text_2="Reset",
                    on_button_1_click=self.start_stopwatch,
                    on_button_2_click=self.reset_stopwatch,
                    text_alignment="center",
                    text_font_size=DISPLAY_FONT_SIZE,
                    container_width=CONTAINER_WIDTH,
                )
            else:
                # If no time, show Start button only
                self.main_container = TextCardWithButton(
                    text="00:00",
                    button_text="Start",
                    on_button_click=self.start_stopwatch,
                    text_alignment="center",
                    text_font_size=DISPLAY_FONT_SIZE,
                    container_width=CONTAINER_WIDTH,
                )
        elif self.app_state == AppState.RUNNING:
            # When running, show Pause and Stop buttons
            self.main_container = TextCardWithTwoButtons(
                text=seconds_to_time_string(self.elapsed_time),
                button_text_1="Pause",
                button_text_2="Stop",
                on_button_1_click=self.pause_stopwatch,
                on_button_2_click=self.stop_stopwatch,
                text_alignment="center",
                text_font_size=DISPLAY_FONT_SIZE,
                container_width=CONTAINER_WIDTH,
            )
        elif self.app_state == AppState.PAUSED:
            # When paused, show Resume and Stop buttons
            self.main_container = TextCardWithTwoButtons(
                text=seconds_to_time_string(self.elapsed_time),
                button_text_1="Resume",
                button_text_2="Stop",
                on_button_1_click=self.resume_stopwatch,
                on_button_2_click=self.stop_stopwatch,
                text_alignment="center",
                text_font_size=DISPLAY_FONT_SIZE,
                container_width=CONTAINER_WIDTH,
            )
        else:
            print("Error: Invalid app state")
            self.main_container = None

        # Add the container to the app, positioned at the right edge
        self.app.add(
            self.main_container, x=self.app.width() - self.main_container.width(), y=0
        )

    def start_stopwatch(self):
        """Start the stopwatch from stopped state."""
        # Change state to running
        self.app_state = AppState.RUNNING
        # Create a routine that calls update_stopwatch every 1000ms (1 second)
        self.stopwatch_routine = Routine(
            interval_ms=1000,
            invoke=self.update_stopwatch,
        )
        # Update UI to show running state
        self.init_ui()

    def pause_stopwatch(self):
        """Pause the stopwatch while preserving elapsed time."""
        # Change state to paused
        self.app_state = AppState.PAUSED
        # Stop the routine if it exists
        if self.stopwatch_routine:
            self.stopwatch_routine.stop()
            self.stopwatch_routine = None
        # Update UI to show paused state
        self.init_ui()

    def resume_stopwatch(self):
        """Resume the stopwatch from paused state."""
        # Change state to running
        self.app_state = AppState.RUNNING
        # Create a new routine to continue counting
        self.stopwatch_routine = Routine(
            interval_ms=1000,
            invoke=self.update_stopwatch,
        )
        # Update UI to show running state
        self.init_ui()

    def stop_stopwatch(self):
        """Stop the stopwatch and return to stopped state without resetting time."""
        # Change state to stopped (but keep the time)
        self.app_state = AppState.STOPPED
        # Stop the routine if it exists
        if self.stopwatch_routine:
            self.stopwatch_routine.stop()
            self.stopwatch_routine = None
        # Update UI to show stopped state
        self.init_ui()

    def reset_stopwatch(self):
        """Reset the stopwatch to 00:00 and stop if running."""
        # Reset elapsed time to 0
        self.elapsed_time = 0
        # Stop the routine if it exists
        if self.stopwatch_routine:
            self.stopwatch_routine.stop()
            self.stopwatch_routine = None
        # Change state to stopped
        self.app_state = AppState.STOPPED
        # Update UI to show reset state
        self.init_ui()

    def update_stopwatch(self):
        """Update the stopwatch display (called by routine every second)."""
        # Increment elapsed time by 1 second
        self.elapsed_time += 1
        # Convert to formatted string
        updated_string = seconds_to_time_string(self.elapsed_time)
        # Update the text in the UI
        self.main_container.text_box.set_text(updated_string)


if __name__ == "__main__":
    RunApp.run(lambda: Stopwatch(), app_id="", app_key="")
