# PyOllama VSCode Extension

A VSCode extension that integrates PyOllama (Python-based LLM runner) into your development environment.

## Features

- **Chat Interface**: Interactive chat with AI models directly in VSCode
- **Text Generation**: Generate text based on selected code or text
- **Model Management**: List and manage your AI models
- **Cross-Platform**: Works on Windows, macOS, and Linux

## Prerequisites

1. **Python 3.8+** installed on your system
2. **PyOllama** installed:
   ```bash
   pip install pyollama
   ```
3. **AI Models**: Download GGUF models or use models from Hugging Face

## Installation

1. Download the `.vsix` file from the releases
2. In VSCode, go to Extensions → Install from VSIX...
3. Select the downloaded `.vsix` file

## Configuration

Configure the extension in VSCode settings:

- `pyollama.pythonPath`: Path to Python executable (default: "python")
- `pyollama.modelDir`: Directory where models are stored (default: "~/.ollama/models")

## Usage

### Chat with AI Models

1. Open Command Palette (`Ctrl+Shift+P` / `Cmd+Shift+P`)
2. Run `PyOllama: Start Chat`
3. Enter the model name (e.g., "llama3.2")
4. Start chatting in the chat panel

### Generate Text

1. Select some text in your editor
2. Open Command Palette
3. Run `PyOllama: Generate Text`
4. Enter the model name
5. The generated text will be inserted after your selection

### List Models

1. Open Command Palette
2. Run `PyOllama: List Models`
3. View available models in a notification

## Model Setup

### Using Local GGUF Files

1. Download a GGUF model file (e.g., from Hugging Face)
2. Place it in `~/.ollama/models/`
3. Use the filename (without .gguf) as the model name

### Using Hugging Face Models

The extension can automatically download models from Hugging Face repositories.

## Building from Source

1. Clone this repository
2. Run `npm install`
3. Run `npm run compile`
4. Package the extension: `npx vsce package`

## Requirements

- VSCode 1.74.0 or later
- Python 3.8+
- PyOllama package
- Sufficient RAM for model loading (4GB+ recommended)

## Troubleshooting

### Extension not working

1. Check that Python is installed and accessible
2. Verify PyOllama is installed: `pip show pyollama`
3. Check VSCode settings for correct paths
4. Look at VSCode's developer console for error messages

### Model loading issues

1. Ensure you have enough RAM
2. Check that the model file exists and is not corrupted
3. Try using a smaller model for testing

## Contributing

Contributions are welcome! Please feel free to submit issues and pull requests.

## License

MIT License
