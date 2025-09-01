# PyOllama GUI Usage Guide

## 🎨 GUI Overview

PyOllama now includes a modern graphical user interface built with PyQt5, featuring a sleek chat-focused design with glass effects and native macOS-style controls.

## ✅ Testing Results

### All Tests Passed! 🎉

```
🧪 PyOllama GUI Test Suite
========================================
🔧 Testing GUI module import... ✅
🔧 Testing GUI components... ✅
🔧 Testing GUI functionality... ✅
========================================
🎉 ALL TESTS PASSED!
✅ GUI is ready to run!
```

## 🚀 How to Launch the GUI

### Method 1: CLI Command (Recommended)
```bash
pyollama gui
```

### Method 2: Launcher Script
```bash
python3 ollama-python-app/launch_gui.py
```

### Method 3: Direct Python Import
```bash
python3 -c "from ollama_client.pyqt_gui import main; main()"
```

### Method 4: From Python Script
```python
from ollama_client.pyqt_gui import main
main()
```

## 📋 Prerequisites

- ✅ Python 3.8+ installed
- ✅ PyQt5 installed (`pip install PyQt5`)
- ✅ PyOllama installed: `pip install -e .`
- ✅ Internet connection (for downloading models)

## 🖥️ GUI Features

### Modern Chat Interface
**Purpose**: Clean, focused chat experience with AI models
**Features**:
- 💬 Real-time chat with conversation history
- 🤖 Model selection dropdown
- 🎨 Glass effect background (macOS)
- 🍎 macOS-style window controls (traffic lights)
- 📱 Responsive, minimalist design
- ⌨️ Multi-line message input
- ⏎ Send with Enter key

**How to use**:
1. Select a model from the dropdown
2. Type your message in the input area
3. Press Enter or click the send button
4. View responses in the chat history
5. Continue the conversation seamlessly

### Model Management
**Features**:
- 📥 Pull new models via dialog
- � Auto-refresh model list on startup
- 📋 View available models in dropdown
- �️ Model deletion (via dialog)

**How to use**:
1. Use the pull dialog to download models
2. Models automatically appear in the dropdown
3. Switch between models during chat
4. Models persist between sessions

### Window Controls
**Features**:
- � Close button (red traffic light)
- 🟡 Minimize button (yellow traffic light)
- 🟢 Maximize button (green traffic light)
- �️ Drag to move window
- � Frameless window design

**How to use**:
1. Click traffic lights for window control
2. Drag title bar to move window
3. Double-click title bar to maximize

## 🎯 Getting Started Workflow

### Step 1: Get a Model
```bash
# Option A: Pull from Hugging Face
pyollama pull microsoft/DialoGPT-medium

# Option B: Download GGUF manually
# 1. Find a GGUF model on Hugging Face
# 2. Download the .gguf file
# 3. Place it in ~/.ollama/models/
```

### Step 2: Launch GUI
```bash
pyollama gui
```

### Step 3: Start Using
1. **Select Model**: Choose from dropdown
2. **Start Chatting**: Type your first message
3. **View Responses**: Read AI replies in chat history
4. **Continue Conversation**: Keep chatting naturally

## 🔧 Advanced Features

### Menu Options
- **File → Settings**: Configure model directory
- **Models → Refresh Models**: Update model list
- **Models → Pull Model**: Download new models
- **Models → Import Local Model**: Add local files
- **Help → About**: Application information

### Keyboard Shortcuts
- **Ctrl+Enter**: Send message in chat
- **Ctrl+Q**: Quit application (File menu)

### Status Bar
- Shows current operation progress
- Displays error messages
- Indicates when operations complete

## 🐛 Troubleshooting

### GUI Won't Start
```bash
# Check PyQt5 installation
python3 -c "import PyQt5; print('PyQt5 available')"

# Install PyQt5 if missing
pip install PyQt5

# Reinstall PyOllama
pip uninstall pyollama
pip install -e .
```

### No Models Found
```bash
# Check model directory
ls ~/.ollama/models/

# Pull a model
pyollama pull microsoft/DialoGPT-medium
```

### Import Errors
```bash
# Ensure proper Python path
cd ollama-python-app
python3 -c "import sys; sys.path.insert(0, 'src'); import ollama_client"
```

## 📊 Performance Tips

### Memory Usage
- Small models (7B): 4-8GB RAM
- Medium models (13B): 8-16GB RAM
- Large models (30B+): 16GB+ RAM

### Model Selection
- **DialoGPT-medium**: Good for chat, fast
- **Llama-2-7B**: Versatile, good balance
- **CodeLlama**: Specialized for coding

### Optimization
- Use smaller models for faster response
- Lower temperature for more consistent output
- Reduce max tokens for quicker generation

## 🔌 Integration

### Use in Your Own Scripts
```python
from ollama_client.pyqt_gui import PyOllamaPyQtGUI
from PyQt5.QtWidgets import QApplication
import sys

# Create and run GUI
app = QApplication(sys.argv)
gui = PyOllamaPyQtGUI()
gui.show()
sys.exit(app.exec_())
```

### API Integration
```python
from ollama_client.client import OllamaClient

client = OllamaClient()
models = client.list_models()
# Use models in your application
```

## 📦 Distribution

### Create Standalone Executable
```bash
pip install pyinstaller
pyinstaller --onefile --windowed ollama-python-app/src/ollama_client/pyqt_gui.py
```

### Package for Distribution
```bash
# Create wheel
python3 -m build

# Upload to PyPI
twine upload dist/*
```

## 🎉 Success!

Your PyOllama GUI is now ready to use! The interface provides an intuitive way to interact with local language models, combining the power of llama.cpp with a user-friendly graphical interface.

**Happy chatting with your AI models! 🤖✨**
