# Import the necessary components from the Raven Framework
from raven_framework import RavenApp, RunApp, TextBox, VerticalContainer


# Define your app class, inheriting from RavenApp (required for all Raven apps)
class HelloWorld(RavenApp):
    # Initialize the app
    def __init__(self, parent=None) -> None:
        # Call the parent class constructor to set up the app
        super().__init__(parent)
        # Create a vertical container with a width of 640 pixels
        # VerticalContainer automatically stacks widgets vertically
        vbox = VerticalContainer(width=640)
        # Create a text box with "Hello, World!" text
        # width=640 makes it span the container width
        # alignment="center" centers the text horizontally
        text_box = TextBox("Hello, World!", width=640, alignment="center")
        # Add the text box to the vertical container
        vbox.add(text_box)
        # Add the container to the main app window (self.app is a 640x640 container)
        self.app.add(vbox)


# Entry point - run the app when this script is executed
if __name__ == "__main__":
    # Launch the app using RunApp.run()
    # lambda: HelloWorld() creates a new instance of the app
    # app_id="" and app_key="" are empty for simulator mode
    RunApp.run(lambda: HelloWorld(), app_id="", app_key="")
