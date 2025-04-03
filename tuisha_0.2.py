# tuisha_0.2.py

import hashlib
import os

from textual.app import App, ComposeResult
from textual.containers import Horizontal
from textual.message import Message
from textual.widgets import Button, Input, Label, Static, Tree


class FileSelected(Message):
    """Custom event for file selection in the file browser."""

    def __init__(self, file_path: str):
        super().__init__()
        self.path = file_path


class FileBrowser(Tree):
    """Enhanced File Browser with navigation support."""

    def __init__(self, path: str, **kwargs):
        super().__init__("📂 Select a File", **kwargs)
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
                up_node = node.add("⬆ .. (Parent Directory)", data=parent_dir)
                up_node.allow_expand = False  # Special case: Up navigation

            for entry in sorted(
                os.scandir(path), key=lambda e: (not e.is_dir(), e.name.lower())
            ):
                if entry.name.startswith("."):  # Skip hidden files
                    continue

                if entry.is_dir():
                    branch = node.add(f"📁 {entry.name}", expand=False)
                    branch.data = entry.path
                    branch.allow_expand = True  # Allow expanding folders
                else:
                    leaf = node.add(f"📄 {entry.name}", data=entry.path)
                    leaf.allow_expand = False  # Files are leaf nodes

        except PermissionError:
            pass  # Skip folders that can't be accessed

    def on_tree_node_selected(self, event):
        """Handle file selection and directory navigation."""
        node = event.node

        if node.data == self.current_path:
            return

        label_text = str(node.label)  # Convert label to string for comparison

        if label_text.startswith("⬆ .."):
            self.populate_tree(node.data)
        elif node.allow_expand:
            self.populate_tree(node.data)
        else:
            self.post_message(FileSelected(node.data))


class SHA256Verifier(App):
    """A Textual-based TUI for verifying SHA-256 file hashes with a file browser."""

    CSS = """
    Screen {
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
        """Define the UI layout."""
        yield Label("🔍 SHA-256 File Checksum Verifier", id="title")
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
            Button("Quit", id="quit_button"),
            id="button_row",
            classes="button-row",  # Optional class for future styling
        )

        self.result_label = Label("")
        yield self.result_label

    def on_file_selected(self, message: FileSelected) -> None:
        self.file_input.value = message.path
        self.file_input.focus()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button clicks for verification and clearing fields."""
        button_id = event.button.id

        if button_id == "verify_button":
            self.verify_hash()
        elif button_id == "clear_button":
            self.clear_fields()
        elif button_id == "quit_button":
            self.exit()

    def hashfile(self, file_path: str) -> str | None:
        """Computes the SHA-256 hash of the given file."""
        BUF_SIZE = 65536  # Read file in 64KB chunks
        sha256 = hashlib.sha256()

        try:
            with open(file_path, "rb") as f:
                while chunk := f.read(BUF_SIZE):
                    sha256.update(chunk)
            return sha256.hexdigest()
        except FileNotFoundError:
            self.result_label.update("❌ Error: File not found.")
        except PermissionError:
            self.result_label.update("❌ Error: Permission denied.")
        except Exception as e:
            self.result_label.update(f"⚠️ Unexpected error: {e}")

        return None

    def verify_hash(self) -> None:
        """Verifies the SHA-256 hash of a file against the expected hash."""
        expected_hash = self.hash_input.value.strip()
        file_path = self.file_input.value.strip()

        if not expected_hash:
            self.result_label.update("⚠️ Error: Expected hash cannot be empty.")
            return

        if not file_path or not os.path.isfile(file_path):
            self.result_label.update("⚠️ Error: Please enter a valid file path.")
            return

        self.result_label.update("🔄 Verifying checksum...")

        computed_hash = self.hashfile(file_path)

        if computed_hash:
            if expected_hash.lower() == computed_hash.lower():
                self.result_label.update("✅ Hashes match, file is legit.")
            else:
                self.result_label.update("❌ Hashes are different, beware!")

    def clear_fields(self) -> None:
        """Clears the input fields and result label."""
        self.hash_input.value = ""
        self.file_input.value = ""
        self.result_label.update("")


if __name__ == "__main__":
    SHA256Verifier().run()
