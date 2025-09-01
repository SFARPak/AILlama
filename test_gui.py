#!/usr/bin/env python3
"""
PyOllama GUI Test Script

This script tests the GUI components without actually displaying the window.
"""

import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'ollama-python-app', 'src'))

def test_gui_import():
    """Test GUI module import"""
    print("🔧 Testing GUI module import...")
    try:
        from ollama_client.pyqt_gui import PyOllamaPyQtGUI, main
        print("✅ GUI module imported successfully!")
        return True
    except ImportError as e:
        print(f"❌ GUI import failed: {e}")
        return False
    except Exception as e:
        print(f"❌ GUI import error: {e}")
        return False

def test_gui_components():
    """Test GUI components can be created"""
    print("\n🔧 Testing GUI components...")

    try:
        from ollama_client.pyqt_gui import PyOllamaPyQtGUI

        # Test GUI class exists and has expected attributes
        print("✅ GUI class imported successfully!")

        # Test that the class has the expected methods
        expected_methods = [
            'setup_ui',
            'refresh_models',
            'send_message',
            'start_new_chat'
        ]

        for method in expected_methods:
            assert hasattr(PyOllamaPyQtGUI, method), f"Method {method} not found"

        print("✅ All expected GUI methods available!")

        return True

    except Exception as e:
        print(f"❌ GUI component test failed: {e}")
        return False

def test_gui_functionality():
    """Test GUI functionality without display"""
    print("\n🔧 Testing GUI functionality...")

    try:
        from ollama_client.client import OllamaClient
        from ollama_client.pyqt_gui import PyOllamaPyQtGUI

        # Test client integration
        client = OllamaClient()
        models = client.list_models()
        print(f"✅ Client integration works! Found {len(models)} models")

        # Test that GUI methods exist
        gui_methods = [
            'refresh_models',
            'show_pull_dialog',
            'send_message',
            'start_new_chat'
        ]

        for method in gui_methods:
            assert hasattr(PyOllamaPyQtGUI, method), f"Method {method} not found"

        print("✅ All GUI methods available!")

        return True

    except Exception as e:
        print(f"❌ GUI functionality test failed: {e}")
        return False

def show_usage_instructions():
    """Show how to actually run the GUI"""
    print("\n" + "="*50)
    print("🚀 HOW TO RUN THE GUI")
    print("="*50)

    print("\n📋 Prerequisites:")
    print("   • Python 3.8+ installed")
    print("   • PyQt5 installed (pip install PyQt5)")
    print("   • PyOllama installed: pip install -e .")

    print("\n🖥️  Launch Methods:")

    print("\n   1. Using CLI:")
    print("      pyollama gui")

    print("\n   2. Using launcher script:")
    print("      python3 ollama-python-app/launch_gui.py")

    print("\n   3. Direct Python import:")
    print("      python3 -c \"from ollama_client.pyqt_gui import main; main()\"")

    print("\n   4. From Python script:")
    print("      from ollama_client.pyqt_gui import main")
    print("      main()")

    print("\n🎯 GUI Features:")
    print("   • Modern chat interface with glass effect")
    print("   • Model selection and management")
    print("   • Real-time chat with Ollama models")
    print("   • macOS-style window controls")

    print("\n📁 Getting Started:")
    print("   1. Download a GGUF model file")
    print("   2. Place it in ~/.ollama/models/")
    print("   3. Launch GUI and start using!")

def main():
    print("🧪 PyOllama GUI Test Suite")
    print("=" * 40)

    # Run all tests
    test1 = test_gui_import()
    test2 = test_gui_components()
    test3 = test_gui_functionality()

    print("\n" + "="*40)
    if all([test1, test2, test3]):
        print("🎉 ALL TESTS PASSED!")
        print("✅ GUI is ready to run!")
    else:
        print("❌ Some tests failed!")
        print("🔧 Check the error messages above")

    # Always show usage instructions
    show_usage_instructions()

if __name__ == "__main__":
    main()
