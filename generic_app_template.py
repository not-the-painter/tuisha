from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Button
from textual.containers import Horizontal
from textual import on


class MyApp(App):
    """A basic template for a Textual app."""

    BINDINGS = [
        ("q", "quit", "Quit"),
        ("r", "refresh", "Refresh"),
    ]

    def compose(self) -> ComposeResult:
        """Define the layout of the application."""
        yield Header()  # Provides a top navigation bar
        yield Horizontal(
            Button("Submit", id="submit"),
            Button("Quit", id="quit")
        )
        yield Footer()  # Provides a status bar at the bottom

    @on(Button.Pressed, "#submit")
    def handle_submit(self) -> None:
        self.notify("Submit button pressed!")

    @on(Button.Pressed, "#quit")
    def handle_quit(self) -> None:
        self.exit()


if __name__ == "__main__":
    MyApp().run()
