# Imports
from dataclasses import dataclass
from enum import Enum

# Raven Framework Imports
from raven_framework import (
    Button,
    RavenApp,
    RunApp,
)
from raven_framework.components.media_viewer import MediaViewer
from raven_framework.components.cards import ScrollableListCard


# Data Classes
@dataclass
class Painting:
    """Data class for painting information."""

    # Name of the painting
    title: str
    # File path to the image
    path: str
    # Width and height of the image
    resolution: tuple[int, int]


# Constants
# Dictionary containing all available paintings
PAINTINGS = {
    "Apple": Painting(title="Apple", path="paintings/apple.png", resolution=(400, 600)),
    "Pear": Painting(title="Pear", path="paintings/pear.png", resolution=(400, 600)),
    "Candle": Painting(
        title="Candle", path="paintings/candle.png", resolution=(400, 600)
    ),
    "Mug": Painting(title="Mug", path="paintings/mug.png", resolution=(400, 600)),
    "Sky": Painting(title="Sky", path="paintings/sky.png", resolution=(400, 600)),
    "Sunset": Painting(
        title="Sunset", path="paintings/sunset.png", resolution=(400, 600)
    ),
}


# Enums
class AppState(Enum):
    """Application state enumeration."""

    # Showing the list of paintings
    PAINTING_LIST = "painting_list"
    # Showing a single painting
    PAINTING_VIEW = "painting_view"


# Application
class ArtStudio(RavenApp):
    """Oil painting reference viewer for learning basic objects."""

    def __init__(self, parent=None) -> None:
        """Initialize the ArtStudio application."""
        # Call parent constructor to set up the app
        super().__init__(parent)
        # Store all paintings
        self.paintings = PAINTINGS
        # Start in list view
        self.app_state = AppState.PAINTING_LIST
        # No painting selected initially
        self.selected_painting = None
        # Initialize the UI
        self.init_ui()

    def init_ui(self) -> None:
        """Initialize the UI based on the current application state."""
        # Clear the app to remove any existing widgets
        self.app.clear()

        if self.app_state == AppState.PAINTING_LIST:
            # Create list of painting titles for display
            info_strings = [painting.title for painting in self.paintings.values()]
            # Create "View" button for each painting
            button_strings = ["View"] * len(info_strings)
            # Create click handlers for each item - each calls view_painting with the painting name
            on_item_click = [
                (self.view_painting, painting.title)
                for painting in self.paintings.values()
            ]
            # Create a scrollable list card with all paintings
            card = ScrollableListCard(
                title_text="Learn oil painting",
                info_strings=info_strings,
                button_strings=button_strings,
                on_item_click=on_item_click,
            )
            # Add the card to the app
            self.app.add(card)
        elif self.app_state == AppState.PAINTING_VIEW:
            # Validate that the selected painting exists
            if self.selected_painting not in self.paintings:
                # If not found, go back to list view
                self.app_state = AppState.PAINTING_LIST
                print(
                    f"Selected painting {self.selected_painting} not found in paintings"
                )
                self.go_back()
                return

            # Get the painting data
            painting = self.paintings[self.selected_painting]

            # Create a media viewer to display the painting image
            painting_viewer = MediaViewer(
                media_path=painting.path,
                width=painting.resolution[0],
                height=painting.resolution[1],
            )

            # Create a back button to return to the list
            back_button = Button(
                center_text="Back",
            )
            # Set the click handler to go back to list
            back_button.on_clicked(self.go_back)

            # Add the painting viewer, positioned at the right edge
            self.app.add(
                painting_viewer, x=self.app.width() - painting.resolution[0], y=0
            )
            # Add the back button, positioned at bottom right
            self.app.add(
                back_button,
                x=self.app.width() - back_button.width(),
                y=painting.resolution[1] - 30,
            )

    def switch_state(self, new_state: AppState) -> None:
        """Switch the application to a new state and update the UI accordingly."""
        # Change the app state
        self.app_state = new_state
        # Reinitialize UI to reflect the new state
        self.init_ui()

    def view_painting(self, painting_name: str) -> None:
        """Navigate to painting view."""
        # Store the selected painting name
        self.selected_painting = painting_name
        # Switch to painting view state
        self.switch_state(AppState.PAINTING_VIEW)

    def go_back(self) -> None:
        """Return to painting list view."""
        # Clear the selected painting
        self.selected_painting = None
        # Switch back to list view state
        self.switch_state(AppState.PAINTING_LIST)


if __name__ == "__main__":
    RunApp.run(lambda: ArtStudio(), app_id="", app_key="")
