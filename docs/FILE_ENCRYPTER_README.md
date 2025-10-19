# 🔐 Hybrid File Encrypter

A modern, dark-themed file encryption application with a sleek GUI built using Python Tkinter and C++ backend integration.

## ✨ Features

### 🎨 Visual Design
- **Dark Theme**: Modern dark UI with GitHub-inspired color scheme
- **Orbitron Font**: Futuristic font styling with fallback to Consolas
- **Animated Effects**: 
  - Flowing progress bar animations
  - Button hover effects with smooth transitions
  - Subtle glow animations
  - Color gradient transitions

### 🔒 Security Features
- **File Encryption/Decryption**: Secure file processing with password protection
- **C++ Backend**: High-performance encryption via pybind11 integration
- **Python Fallback**: XOR-based encryption when C++ backend unavailable
- **Password Protection**: SHA-256 hashed password keys

### 🖥️ User Interface
- **File Browser**: Easy file selection with common file type filters
- **Password Entry**: Secure password input with masked characters
- **Progress Indicators**: Animated progress bars during processing
- **Status Updates**: Real-time status messages with emoji indicators
- **Error Handling**: Detailed error popups with copy functionality

## 🚀 Usage

1. **Run the Application**:
   ```bash
   python gui.py
   ```

2. **Select a File**:
   - Click "Browse" to select any file for encryption/decryption
   - Supports all file types (text, images, documents, archives, etc.)

3. **Enter Password**:
   - Enter a secure password in the password field
   - Password is used to generate encryption key

4. **Encrypt/Decrypt**:
   - Click "🔒 ENCRYPT" to encrypt the selected file
   - Click "🔓 DECRYPT" to decrypt an encrypted file
   - Progress animation shows during processing

## 🎨 Visual Effects

### Color Scheme
- **Background**: `#0d1117` (Deep dark)
- **Panels**: `#161b22` (Dark gray)
- **Cards**: `#21262d` (Medium gray)
- **Accent**: `#58a6ff` (GitHub blue)
- **Success**: `#3fb950` (Green)
- **Warning**: `#f85149` (Orange-red)
- **Error**: `#ff7b72` (Light red)

### Animations
- **Progress Bar**: Flowing gradient animation during file processing
- **Button Hover**: Smooth color transitions on mouse hover
- **Glow Effects**: Subtle pulsing animations on UI elements

### Typography
- **Primary Font**: Orbitron (futuristic, clean)
- **Fallback Font**: Consolas (monospace)
- **Title**: 18pt bold
- **Buttons**: 12pt
- **Text**: 10pt

## 🔧 Technical Details

### Architecture
- **Frontend**: Python Tkinter with custom styling
- **Backend**: C++ encryption module via pybind11
- **Fallback**: Pure Python XOR encryption
- **Threading**: Background processing for non-blocking UI

### File Processing
- **Input**: Any file type
- **Output**: `.encrypted` extension for encrypted files
- **Decryption**: Removes `.encrypted` extension or adds `.decrypted`

### Error Handling
- **Validation**: Input validation before processing
- **Exceptions**: Comprehensive error catching and reporting
- **User Feedback**: Clear error messages and status updates

## 📁 Files

- `gui.py` - Main application file with complete GUI implementation
- `test_file.txt` - Sample file for testing encryption/decryption
- `calc_backend.*` - C++ extension module (when built)

## 🔮 Future Enhancements

- **Multiple Encryption Algorithms**: AES, RSA support
- **Batch Processing**: Encrypt multiple files at once
- **Key Management**: Secure key storage and recovery
- **File Shredding**: Secure deletion of original files
- **Themes**: Multiple color schemes and font options
- **Drag & Drop**: File selection via drag and drop

---

*Transformed from a scientific calculator to a modern file encrypter with enhanced visual appeal and security features.*
