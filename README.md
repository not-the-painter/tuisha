# Tuisha

A SHA-256 checksum tool with a beautiful Terminal User Interface (TUI) built using Python's Textual library.

## 🔍  Features

- **Hash Verification**: Verify file integrity by comparing against expected SHA-256 hashes
- **Hash Generation**: Generate SHA-256 hashes for any file
- **Interactive File Browser**: Navigate your filesystem with an intuitive tree view
- **Dual Input Methods**: Enter file paths manually or use the visual file browser
- **Clipboard Integration**: Copy generated hashes to clipboard with a single click
- **Keyboard Shortcuts**: Full keyboard navigation support
- **Clean Interface**: Modern TUI with emoji icons and clear status messages

## 🚀  Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Dependencies

The app requires the following Python packages:
- `textual` - For the terminal user interface
- `hashlib` - For SHA-256 hash computation (built-in)
- `os` - For file system operations (built-in)

## 🎮  Usage

### Running the Application

```bash
python tuisha.py
```

### Main Menu

When you start the app, you'll see a menu with three options:

1. **Verify Hash** - Check if a file matches an expected SHA-256 hash
2. **Generate Hash** - Create a SHA-256 hash for a file
3. **Quit** - Exit the application

### Hash Verification Mode

1. Enter the expected SHA-256 hash in the first field
2. Select a file using either:
   - The file browser (click on files to select)
   - Manual path entry in the file path field
3. Click "Verify" or press Enter in the file path field
4. The app will display whether the hashes match

### Hash Generation Mode

1. Select a file using either:
   - The file browser (automatic hash generation on selection)
   - Manual path entry and click "Generate"
2. The generated hash appears in the output field
3. Copy the hash to clipboard by:
   - Clicking on the hash field
   - Focusing the hash field and pressing Enter

### Navigation

**File Browser:**
- Click on folders to navigate into them
- Click on "⬆  .. (Parent Directory)" to go up one level
- Click on files to select them

**Keyboard Shortcuts:**
- `1` - Switch to Verify Hash mode
- `2` - Switch to Generate Hash mode
- `q` - Quit the application
- `Ctrl+C` - Force quit
- `Escape` - Go back to main menu (from any screen)
- `Enter` - Submit forms or copy hash to clipboard

## 📁  File Structure

```
tuisha/
├── tuisha.py              # Main application file
├── requirements.txt       # Python dependencies
├── README.md             # This file
├── LICENSE               # License information
└── generic_app_template.py # Template for new Textual apps
```

## 🛠  Technical Details

### Architecture

The application is built using the Textual framework and consists of several key components:

- **MenuScreen**: Main menu interface for mode selection
- **VerifyHashScreen**: Interface for hash verification
- **GenerateHashScreen**: Interface for hash generation
- **FileBrowser**: Enhanced file browser with navigation support
- **SHA256Verifier**: Main application class coordinating all screens

### Hash Computation

- Uses Python's built-in `hashlib` library for SHA-256 computation
- Processes files in 64KB chunks for memory efficiency
- Handles large files without loading them entirely into memory

### Error Handling

The app gracefully handles various error conditions:
- File not found errors
- Permission denied errors
- Invalid file paths
- Empty input validation

## 🎨  Interface Design

The application features a clean, modern interface with:
- Emoji icons for visual clarity
- Consistent color scheme
- Clear status messages
- Responsive layout
- Proper spacing optimized for monospace fonts

## 🔧  Development

### Requirements

Development requires the same dependencies as running the application. The code is structured to be easily extensible with new features.

### Adding New Features

The modular design makes it easy to add new functionality:
1. Create new Screen classes for additional interfaces
2. Add message types for communication between screens
3. Extend the main application class with new screen handling

## 📄  License

This project is licensed under the terms specified in the LICENSE file.

## 🤝  Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues for bug reports and feature requests.

## 🐛  Known Issues

- None currently reported

## 📞  Support

For support, please open an issue on the project repository.

---

*Built with ❤️  using Python and Textual*