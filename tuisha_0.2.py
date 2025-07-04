# tuisha_0.2.py

import hashlib
import os

from textual import events
from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.message import Message
from textual.screen import Screen
from textual.widgets import Button, Input, Label, Static, Tree


class FileSelected(Message):
    """Custom event for file selection in the file browser."""

    def __init__(self, file_path: str):
        super().__init__()
        self.path = file_path


class ModeSelected(Message):
    """Custom event for mode selection in the menu."""

    def __init__(self, mode: str):
        super().__init__()
        self.mode = mode


class FileBrowser(Tree):
    """Enhanced File Browser with navigation support."""

    def __init__(self, path: str, **kwargs):
        super().__init__("📂  Select a File", **kwargs)
        self.current_path = path  # Track the current directory
        self.show_root = False  # Hide the root folder name
        self.populate_tree(path)  # Ensure this method is defined!

    def populate_tree(self, path: str, node=None):
        """Populate the tree with directories and files, including navigation support."""
        self.current_path = path  # Update the current path
        node = node or self.root
        node.remove_children()  # Clear existing contents

        try:
            parent_dir = os.path.abspath(os.path.join(path, os.pardir))
            if parent_dir != path:  # Prevent navigating above the filesystem root
                up_node = node.add("⬆  .. (Parent Directory)", data=parent_dir)
                up_node.allow_expand = False  # Special case: Up navigation

            for entry in sorted(
                os.scandir(path), key=lambda e: (not e.is_dir(), e.name.lower())
            ):
                if entry.name.startswith("."):  # Skip hidden files
                    continue

                if entry.is_dir():
                    branch = node.add(f"📁  {entry.name}", expand=False)
                    branch.data = entry.path
                    branch.allow_expand = True  # Allow expanding folders
                else:
                    leaf = node.add(f"📄  {entry.name}", data=entry.path)
                    leaf.allow_expand = False  # Files are leaf nodes

        except PermissionError:
            pass  # Skip folders that can't be accessed

    def on_tree_node_selected(self, event):
        """Handle file selection and directory navigation."""
        node = event.node

        if node.data == self.current_path:
            return

        label_text = str(node.label)  # Convert label to string for comparison

        if label_text.startswith("⬆  .."):
            self.populate_tree(node.data)
        elif node.allow_expand:
            self.populate_tree(node.data)
        else:
            self.post_message(FileSelected(node.data))

    def on_focus(self, event: events.Focus) -> None:
        """Automatically select the first item in the file browser on focus."""
        # The first node is directly accessible from the tree's nodes collection
        if self.root.children:
            first_child = self.root.children[0]
            self.select_node(first_child)
            self.scroll_to_node(first_child)


class MenuScreen(Screen):
    """Welcome screen with mode selection."""

    CSS = """
    MenuScreen {
        align: center middle;
    }
    #menu_container {
        width: 50%;
        height: auto;
        align: center middle;
        padding: 2;
        border: solid $primary;
        background: $surface;
    }
    #menu_title {
        text-align: center;
        margin-bottom: 2;
    }
    #menu_buttons {
        align: center middle;
        padding: 1;
    }
    #menu_buttons Button {
        width: 100%;
        margin: 1;
    }
    """

    def compose(self) -> ComposeResult:
        """Define the menu UI layout."""
        with Vertical(id="menu_container"):
            yield Label("🔍  SHA-256 File Checksum Tool", id="menu_title")
            yield Static("Choose an option:")
            with Vertical(id="menu_buttons"):
                yield Button("1. Verify Hash", id="verify_mode", variant="primary")
                yield Button("2. Generate Hash", id="generate_mode")
                yield Button("Q. Quit", id="quit_button", variant="error")

    def on_mount(self) -> None:
        """Set focus to the verify button on mount."""
        self.query_one("#verify_mode").focus()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle mode selection."""
        if event.button.id == "verify_mode":
            self.post_message(ModeSelected("verify"))
        elif event.button.id == "generate_mode":
            self.post_message(ModeSelected("generate"))
        elif event.button.id == "quit_button":
            self.app.exit()

    def on_key(self, event: events.Key) -> None:
        """Handle keyboard navigation."""
        if event.key == "1":
            self.post_message(ModeSelected("verify"))
        elif event.key == "2":
            self.post_message(ModeSelected("generate"))
        elif event.key == "q":
            self.app.exit()


class VerifyHashScreen(Screen):
    """Screen for hash verification mode."""

    CSS = """
    VerifyHashScreen {
        align: center middle;
    }
    Input {
        width: 80%;
    }
    Button {
        width: 30%;
    }
    Label {
        text-align: center;
    }
    #button_row {
        width: 80%;
        align-horizontal: center;
        padding: 1;
    }
    """

    def compose(self) -> ComposeResult:
        """Define the verification UI layout."""
        yield Label("🔍  SHA-256 Hash Verification", id="title")
        yield Static("Enter Expected SHA-256 Hash:")
        self.hash_input = Input(placeholder="Paste the expected SHA-256 hash here")
        yield self.hash_input

        yield Static("Select File:")
        self.file_input = Input(
            placeholder="Enter file path manually or use the file browser", type="text"
        )
        yield self.file_input

        self.file_browser = FileBrowser(path=os.getcwd(), id="file_browser")
        yield self.file_browser

        yield Horizontal(
            Button("Verify", id="verify_button"),
            Button("Clear", id="clear_button"),
            Button("Back to Menu", id="back_button"),
            id="button_row",
        )

        self.result_label = Label("")
        yield self.result_label

    def on_file_selected(self, message: FileSelected) -> None:
        self.file_input.value = message.path
        self.file_input.focus()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle Enter key press in input fields."""
        if event.input == self.file_input:
            self.verify_hash()
            self.query_one("#back_button").focus()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button clicks."""
        button_id = event.button.id

        if button_id == "verify_button":
            self.verify_hash()
        elif button_id == "clear_button":
            self.clear_fields()
        elif button_id == "back_button":
            self.app.pop_screen()

    def on_key(self, event: events.Key) -> None:
        """Handle Esc key to return to menu."""
        if event.key == "escape":
            self.app.pop_screen()

    def hashfile(self, file_path: str) -> str | None:
        """Computes the SHA-256 hash of the given file."""
        BUF_SIZE = 65536
        sha256 = hashlib.sha256()

        try:
            with open(file_path, "rb") as f:
                while chunk := f.read(BUF_SIZE):
                    sha256.update(chunk)
            return sha256.hexdigest()
        except FileNotFoundError:
            self.result_label.update("❌  Error: File not found.")
        except PermissionError:
            self.result_label.update("❌  Error: Permission denied.")
        except Exception as e:
            self.result_label.update(f"⚠️  Unexpected error: {e}")

        return None

    def verify_hash(self) -> None:
        """Verifies the SHA-256 hash of a file against the expected hash."""
        expected_hash = self.hash_input.value.strip()
        file_path = self.file_input.value.strip()

        if not expected_hash:
            self.result_label.update("⚠️  Error: Expected hash cannot be empty.")
            return

        if not file_path or not os.path.isfile(file_path):
            self.result_label.update("⚠️  Error: Please enter a valid file path.")
            return

        self.result_label.update("🔄  Verifying checksum...")

        computed_hash = self.hashfile(file_path)

        if computed_hash:
            if expected_hash.lower() == computed_hash.lower():
                self.result_label.update("✅  Hashes match, file is legit.")
            else:
                self.result_label.update("❌  Hashes are different, beware!")

    def clear_fields(self) -> None:
        """Clears the input fields and result label."""
        self.hash_input.value = ""
        self.file_input.value = ""
        self.result_label.update("")


class GenerateHashScreen(Screen):
    """Screen for hash generation mode."""

    CSS = """
    GenerateHashScreen {
        align: center middle;
    }
    Input {
        width: 80%;
    }
    Button {
        width: 30%;
    }
    Label {
        text-align: center;
    }
    #button_row {
        width: 80%;
        align-horizontal: center;
        padding: 1;
    }
    #hash_output {
        width: 80%;
        margin: 1;
    }
    """

    def compose(self) -> ComposeResult:
        """Define the hash generation UI layout."""
        yield Label("🔐  SHA-256 Hash Generation", id="title")
        yield Static("Select File:")
        self.file_input = Input(
            placeholder="Enter file path manually or use the file browser", type="text"
        )
        yield self.file_input

        self.file_browser = FileBrowser(path=os.getcwd(), id="file_browser")
        yield self.file_browser

        yield Static("Generated Hash (click field or press Enter to copy):")
        self.hash_output = Input(placeholder="Hash will appear here...", id="hash_output")
        self.hash_output.disabled = False
        yield self.hash_output

        yield Horizontal(
            Button("Generate", id="generate_button"),
            Button("Clear", id="clear_button"),
            Button("Back to Menu", id="back_button"),
            id="button_row",
        )

        self.result_label = Label("")
        yield self.result_label

    def on_file_selected(self, message: FileSelected) -> None:
        self.file_input.value = message.path
        self.generate_hash()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle Enter key press in file input."""
        if event.input == self.file_input:
            self.generate_hash()
        elif event.input == self.hash_output:
            # Copy hash to clipboard when user presses Enter in the hash field
            if self.hash_output.value:
                self.app.copy_to_clipboard(self.hash_output.value)
                self.result_label.update("✅  Hash copied to clipboard!")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button clicks."""
        button_id = event.button.id

        if button_id == "generate_button":
            self.generate_hash()
        elif button_id == "clear_button":
            self.clear_fields()
        elif button_id == "back_button":
            self.app.pop_screen()

    def on_key(self, event: events.Key) -> None:
        """Handle Esc key to return to menu."""
        if event.key == "escape":
            self.app.pop_screen()

    def on_mouse_down(self, event: events.MouseDown) -> None:
        """Handle mouse clicks on the hash output field."""
        # Check if the click is on the hash output field
        widget = self.get_widget_at(event.x, event.y)[0]
        if widget == self.hash_output and self.hash_output.value:
            self.app.copy_to_clipboard(self.hash_output.value)
            self.result_label.update("✅  Hash copied to clipboard!")

    def hashfile(self, file_path: str) -> str | None:
        """Computes the SHA-256 hash of the given file."""
        BUF_SIZE = 65536
        sha256 = hashlib.sha256()

        try:
            with open(file_path, "rb") as f:
                while chunk := f.read(BUF_SIZE):
                    sha256.update(chunk)
            return sha256.hexdigest()
        except FileNotFoundError:
            self.result_label.update("❌  Error: File not found.")
        except PermissionError:
            self.result_label.update("❌  Error: Permission denied.")
        except Exception as e:
            self.result_label.update(f"⚠️  Unexpected error: {e}")

        return None

    def generate_hash(self) -> None:
        """Generates the SHA-256 hash of the selected file."""
        file_path = self.file_input.value.strip()

        if not file_path or not os.path.isfile(file_path):
            self.result_label.update("⚠️  Error: Please enter a valid file path.")
            self.hash_output.value = ""
            return

        self.result_label.update("🔄  Generating hash...")

        computed_hash = self.hashfile(file_path)

        if computed_hash:
            self.hash_output.value = computed_hash
            self.result_label.update("✅  Hash generated successfully. Click the hash field or press Enter to copy.")
        else:
            self.hash_output.value = ""

    def clear_fields(self) -> None:
        """Clears the input fields and result label."""
        self.file_input.value = ""
        self.hash_output.value = ""
        self.result_label.update("")


class SHA256Verifier(App):
    """A Textual-based TUI for SHA-256 file operations with menu navigation."""

    def on_mount(self) -> None:
        """Show the menu screen on startup."""
        self.push_screen(MenuScreen())

    def on_mode_selected(self, message: ModeSelected) -> None:
        """Handle mode selection from the menu."""
        if message.mode == "verify":
            self.push_screen(VerifyHashScreen())
        elif message.mode == "generate":
            self.push_screen(GenerateHashScreen())

    def on_key(self, event: events.Key) -> None:
        """Handle global key events."""
        if event.key == "q" or event.key == "ctrl+c":
            self.exit()


if __name__ == "__main__":
    SHA256Verifier().run()
