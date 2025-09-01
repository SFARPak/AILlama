#!/usr/bin/env python3

import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'ollama-python-app', 'src'))

try:
    from ollama_client.client import OllamaClient
    from ollama_client.cli import main
    print("✅ PyOllama modules imported successfully!")

    # Test the client initialization
    client = OllamaClient()
    print("✅ OllamaClient initialized successfully!")

    # Test listing models (should show no models)
    models = client.list_models()
    print(f"✅ List models works! Found {len(models)} models")

    # Test GUI import (optional)
    try:
        from ollama_client.gui import PyOllamaGUI
        print("✅ GUI module imported successfully!")
        print("   GUI can be launched with: pyollama gui")
    except ImportError as e:
        print(f"⚠️  GUI module not available: {e}")
        print("   This is normal if tkinter is not installed")

    print("\n🎉 PyOllama is working correctly!")
    print("\nAvailable commands:")
    print("  - pyollama list")
    print("  - pyollama pull <model>")
    print("  - pyollama generate <model> <prompt>")
    print("  - pyollama chat <model>")
    print("  - pyollama embed <model> <text>")
    print("  - pyollama show <model>")
    print("  - pyollama delete <model>")
    print("  - pyollama gui (if tkinter available)")

    print("\nTo launch GUI:")
    print("  pyollama gui")
    print("  # or")
    print("  python3 launch_gui.py")

except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)
except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1)
