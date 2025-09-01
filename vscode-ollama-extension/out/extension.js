"use strict";
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __importStar = (this && this.__importStar) || function (mod) {
    if (mod && mod.__esModule) return mod;
    var result = {};
    if (mod != null) for (var k in mod) if (k !== "default" && Object.prototype.hasOwnProperty.call(mod, k)) __createBinding(result, mod, k);
    __setModuleDefault(result, mod);
    return result;
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.deactivate = exports.activate = void 0;
const vscode = __importStar(require("vscode"));
const child_process_1 = require("child_process");
const util_1 = require("util");
const execAsync = (0, util_1.promisify)(child_process_1.exec);
function activate(context) {
    console.log('PyOllama extension is now active!');
    // Register commands
    const chatCommand = vscode.commands.registerCommand('pyollama.chat', async () => {
        await startChat();
    });
    const generateCommand = vscode.commands.registerCommand('pyollama.generate', async () => {
        await generateText();
    });
    const listModelsCommand = vscode.commands.registerCommand('pyollama.listModels', async () => {
        await listModels();
    });
    context.subscriptions.push(chatCommand, generateCommand, listModelsCommand);
}
exports.activate = activate;
async function getPythonPath() {
    const config = vscode.workspace.getConfiguration('pyollama');
    return config.get('pythonPath', 'python');
}
async function getModelDir() {
    const config = vscode.workspace.getConfiguration('pyollama');
    return config.get('modelDir', '~/.ollama/models');
}
async function runPyOllamaCommand(args) {
    const pythonPath = await getPythonPath();
    const modelDir = await getModelDir();
    const command = `${pythonPath} -m pyollama --model-dir ${modelDir} ${args.join(' ')}`;
    try {
        const { stdout, stderr } = await execAsync(command);
        if (stderr) {
            console.warn('PyOllama stderr:', stderr);
        }
        return stdout;
    }
    catch (error) {
        throw new Error(`PyOllama command failed: ${error.message}`);
    }
}
async function listModels() {
    try {
        const output = await runPyOllamaCommand(['list']);
        vscode.window.showInformationMessage('Models:\n' + output);
    }
    catch (error) {
        vscode.window.showErrorMessage(`Failed to list models: ${error.message}`);
    }
}
async function startChat() {
    const modelName = await vscode.window.showInputBox({
        prompt: 'Enter the model name to chat with',
        placeHolder: 'e.g., llama3.2'
    });
    if (!modelName) {
        return;
    }
    const chatPanel = vscode.window.createWebviewPanel('pyollamaChat', `PyOllama Chat - ${modelName}`, vscode.ViewColumn.One, {
        enableScripts: true,
        retainContextWhenHidden: true
    });
    chatPanel.webview.html = getChatHtml(modelName);
    // Handle messages from the webview
    chatPanel.webview.onDidReceiveMessage(async (message) => {
        if (message.type === 'sendMessage') {
            try {
                // For simplicity, we'll use the generate command
                // In a real implementation, you'd want to maintain conversation state
                const output = await runPyOllamaCommand(['generate', modelName, message.text]);
                chatPanel.webview.postMessage({
                    type: 'response',
                    text: output.trim()
                });
            }
            catch (error) {
                chatPanel.webview.postMessage({
                    type: 'error',
                    text: error.message
                });
            }
        }
    });
}
async function generateText() {
    const editor = vscode.window.activeTextEditor;
    if (!editor) {
        vscode.window.showErrorMessage('No active editor found');
        return;
    }
    const selection = editor.selection;
    const selectedText = editor.document.getText(selection);
    if (!selectedText) {
        vscode.window.showErrorMessage('Please select some text to use as a prompt');
        return;
    }
    const modelName = await vscode.window.showInputBox({
        prompt: 'Enter the model name',
        placeHolder: 'e.g., llama3.2'
    });
    if (!modelName) {
        return;
    }
    try {
        const output = await runPyOllamaCommand(['generate', modelName, `"${selectedText}"`]);
        editor.edit(editBuilder => {
            editBuilder.insert(selection.end, '\n\n' + output.trim());
        });
    }
    catch (error) {
        vscode.window.showErrorMessage(`Generation failed: ${error.message}`);
    }
}
function getChatHtml(modelName) {
    return `
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PyOllama Chat</title>
    <style>
        body {
            font-family: var(--vscode-font-family);
            font-size: var(--vscode-font-size);
            background-color: var(--vscode-editor-background);
            color: var(--vscode-editor-foreground);
            margin: 0;
            padding: 20px;
            height: 100vh;
            display: flex;
            flex-direction: column;
        }
        #chat-container {
            flex: 1;
            overflow-y: auto;
            margin-bottom: 20px;
            border: 1px solid var(--vscode-panel-border);
            padding: 10px;
            border-radius: 4px;
        }
        #input-container {
            display: flex;
            gap: 10px;
        }
        #message-input {
            flex: 1;
            padding: 8px;
            background-color: var(--vscode-input-background);
            color: var(--vscode-input-foreground);
            border: 1px solid var(--vscode-input-border);
            border-radius: 4px;
        }
        #send-button {
            padding: 8px 16px;
            background-color: var(--vscode-button-background);
            color: var(--vscode-button-foreground);
            border: none;
            border-radius: 4px;
            cursor: pointer;
        }
        #send-button:hover {
            background-color: var(--vscode-button-hoverBackground);
        }
        .message {
            margin-bottom: 10px;
            padding: 8px;
            border-radius: 4px;
        }
        .user-message {
            background-color: var(--vscode-textBlockQuote-background);
            margin-left: 20%;
        }
        .assistant-message {
            background-color: var(--vscode-textPreformat-background);
            margin-right: 20%;
        }
    </style>
</head>
<body>
    <h2>Chat with ${modelName}</h2>
    <div id="chat-container"></div>
    <div id="input-container">
        <input type="text" id="message-input" placeholder="Type your message...">
        <button id="send-button">Send</button>
    </div>

    <script>
        const vscode = acquireVsCodeApi();
        const chatContainer = document.getElementById('chat-container');
        const messageInput = document.getElementById('message-input');
        const sendButton = document.getElementById('send-button');

        function addMessage(text, isUser = false) {
            const messageDiv = document.createElement('div');
            messageDiv.className = 'message ' + (isUser ? 'user-message' : 'assistant-message');
            messageDiv.textContent = text;
            chatContainer.appendChild(messageDiv);
            chatContainer.scrollTop = chatContainer.scrollHeight;
        }

        function sendMessage() {
            const text = messageInput.value.trim();
            if (text) {
                addMessage(text, true);
                vscode.postMessage({ type: 'sendMessage', text: text });
                messageInput.value = '';
            }
        }

        sendButton.addEventListener('click', sendMessage);
        messageInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                sendMessage();
            }
        });

        window.addEventListener('message', event => {
            const message = event.data;
            if (message.type === 'response') {
                addMessage(message.text, false);
            } else if (message.type === 'error') {
                addMessage('Error: ' + message.text, false);
            }
        });
    </script>
</body>
</html>`;
}
function deactivate() { }
exports.deactivate = deactivate;
//# sourceMappingURL=extension.js.map