class ChatbotUI {
    constructor(config) {
        this.config = config;
        this.isOpen = false;
        this.messages = [];
        this.ws = null;
        this.defaultTheme = {
            border_radius: "8px",
            header_text: "Chatbot",
            height: "500px",
            input_placeholder: "Type your message...",
            launcher: true,
            position: "bottom-right",
            primary_color: "#3B82F6",
            secondary_color: "#3B82F6",
            show_header: true,
            text_color: "#000000",
            theme: "light",
            width: "350px"
        };
        this.theme = { ...this.defaultTheme };
        this.initUI();
        this.connectWebSocket();
    }

    connectWebSocket() {
        // Create WebSocket connection
        const wsUrl = this.config.wsEndpoint || `ws://localhost:8000/api/v1/playground/chat`;
        this.ws = new WebSocket(wsUrl);

        // Connection opened
        this.ws.onopen = () => {
            console.log('WebSocket connection established');
            this.addMessage({
                text: "Hello! How can I help you today?",
                isUser: false,
                timestamp: new Date()
            });
        };

        // Listen for messages
        this.ws.onmessage = (event) => {
            this.addMessage({
                text: event.data,
                isUser: false,
                timestamp: new Date()
            });
        };

        // Handle connection errors
        this.ws.onerror = (error) => {
            console.error('WebSocket error:', error);
            this.addMessage({
                text: "Connection error. Please try again later.",
                isUser: false,
                timestamp: new Date()
            });
        };

        // Handle connection close
        this.ws.onclose = () => {
            console.log('WebSocket connection closed');
            this.addMessage({
                text: "Connection closed. Reconnecting...",
                isUser: false,
                timestamp: new Date()
            });
            // Attempt to reconnect after 5 seconds
            setTimeout(() => this.connectWebSocket(), 5000);
        };
    }

    async fetchTheme() {
        try {
            const response = await fetch(`http://localhost:8000/api/v1/theme?workspace_id=${this.config.workspaceId}`);
            if (!response.ok) throw new Error('Failed to fetch theme');
            const data = await response.json();
            this.theme = { ...this.defaultTheme, ...data };
        } catch (error) {
            console.error("Error fetching theme:", error);
            // Keep using default theme
        }
    }

    async initUI() {
        await this.fetchTheme();

        // Create chat container
        this.container = document.createElement('div');
        this.container.id = 'chatbot-container';
        this.container.className = 'h-full flex flex-col';
        
        // Create card structure
        const card = document.createElement('div');
        card.className = 'flex-1 flex flex-col';
        
        // Card header with close button
        const cardHeader = document.createElement('div');
        cardHeader.className = 'p-4 border-b flex justify-between items-center';
        cardHeader.style.display = this.theme.show_header ? 'flex' : 'none';
        cardHeader.innerHTML = `
            <h1 class="text-xl font-semibold" style="color: ${this.theme.text_color}">${this.theme.header_text}</h1>
            <button class="chatbot-close-btn">&times;</button>
        `;
        
        // Add close button functionality
        cardHeader.querySelector('.chatbot-close-btn').addEventListener('click', () => {
            this.toggleChatbot(false);
        });
        
        // Card content
        const cardContent = document.createElement('div');
        cardContent.className = 'flex-1 flex flex-col p-0';
        
        // Message area
        this.messageArea = document.createElement('div');
        this.messageArea.className = 'flex-1 p-4 min-h-[300px] max-h-[400px] overflow-y-auto';
        
        // Input form
        const form = document.createElement('form');
        form.className = 'p-4 border-t';
        form.onsubmit = this.handleSubmit.bind(this);
        
        const inputContainer = document.createElement('div');
        inputContainer.className = 'flex gap-2';
        
        this.input = document.createElement('input');
        this.input.className = 'flex-1 p-2 border rounded';
        this.input.placeholder = this.theme.input_placeholder;
        
        const submitButton = document.createElement('button');
        submitButton.className = 'p-2 text-white rounded flex items-center justify-center';
        submitButton.style.backgroundColor = this.theme.primary_color;
        submitButton.innerHTML = `
            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M22 2L11 13"></path>
                <path d="M22 2L15 22L11 13L2 9L22 2Z"></path>
            </svg>
        `;
        
        // Assemble components
        inputContainer.appendChild(this.input);
        inputContainer.appendChild(submitButton);
        form.appendChild(inputContainer);
        cardContent.appendChild(this.messageArea);
        cardContent.appendChild(form);
        card.appendChild(cardHeader);
        card.appendChild(cardContent);
        this.container.appendChild(card);
        
        // Position container
        this.container.style.position = 'fixed';
        this.container.style.bottom = '20px';
        this.container.style.right = '20px';
        this.container.style.width = this.theme.width;
        this.container.style.height = this.theme.height;
        this.container.style.backgroundColor = this.theme.theme === 'dark' ? '#1a1a1a' : 'white';
        this.container.style.boxShadow = '0 0 10px rgba(0,0,0,0.1)';
        this.container.style.borderRadius = this.theme.border_radius;
        this.container.style.zIndex = '1000';
        this.container.style.display = 'none';
        
        // Create bot launcher icon
        if (this.theme.launcher) {
            this.launcher = document.createElement('div');
            this.launcher.className = 'chatbot-launcher';
            this.launcher.innerHTML = `
                <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
                    <line x1="9" y1="9" x2="15" y2="9"></line>
                    <line x1="9" y1="13" x2="15" y2="13"></line>
                </svg>
            `;
            this.launcher.style.position = 'fixed';
            this.launcher.style.bottom = '20px';
            this.launcher.style.right = '20px';
            this.launcher.style.width = '50px';
            this.launcher.style.height = '50px';
            this.launcher.style.backgroundColor = this.theme.primary_color;
            this.launcher.style.borderRadius = '50%';
            this.launcher.style.display = 'flex';
            this.launcher.style.alignItems = 'center';
            this.launcher.style.justifyContent = 'center';
            this.launcher.style.cursor = 'pointer';
            this.launcher.style.boxShadow = '0 2px 8px rgba(0,0,0,0.2)';
            this.launcher.style.zIndex = '999';
            this.launcher.style.color = 'white';
            
            this.launcher.addEventListener('click', () => {
                this.toggleChatbot(true);
            });
            
            document.body.appendChild(this.launcher);
        }
        
        // Add CSS for styling
        const style = document.createElement('style');
        style.textContent = `
            .chatbot-close-btn {
                background: none;
                border: none;
                font-size: 20px;
                cursor: pointer;
                color: ${this.theme.text_color};
            }
            .chatbot-close-btn:hover {
                opacity: 0.8;
            }
            #chatbot-container {
                transition: all 0.3s ease;
                overflow: hidden;
            }
            .chatbot-launcher {
                transition: all 0.3s ease;
            }
            .chatbot-launcher:hover {
                transform: scale(1.05);
            }
        `;
        
        document.head.appendChild(style);
        document.body.appendChild(this.container);
    }

    toggleChatbot(show) {
        this.isOpen = show !== undefined ? show : !this.isOpen;
        this.container.style.display = this.isOpen ? 'flex' : 'none';
        if (this.isOpen) {
            this.input.focus();
            // Scroll to bottom of message area
            this.messageArea.scrollTop = this.messageArea.scrollHeight;
        }
    }

    handleSubmit(e) {
        e.preventDefault();
        const message = this.input.value.trim();
        if (!message) return;
        
        // Add user message
        this.addMessage({
            text: message,
            isUser: true,
            timestamp: new Date()
        });
        
        // Clear input
        this.input.value = '';
        
        // Send message through WebSocket
        if (this.ws && this.ws.readyState === WebSocket.OPEN) {
            this.ws.send(message);
        } else {
            this.addMessage({
                text: "Not connected. Please wait...",
                isUser: false,
                timestamp: new Date()
            });
        }
    }

    addMessage(message) {
        const messageElement = document.createElement('div');
        messageElement.className = `flex ${message.isUser ? 'justify-end' : 'justify-start'} mb-4`;
        
        const bubble = document.createElement('div');
        bubble.className = `max-w-[80%] rounded-lg p-3`;
        bubble.style.backgroundColor = message.isUser ? this.theme.primary_color : (this.theme.theme === 'dark' ? '#2d2d2d' : '#f3f4f6');
        bubble.style.color = message.isUser ? 'white' : this.theme.text_color;
        
        const text = document.createElement('p');
        text.className = 'text-sm';
        text.textContent = message.text;
        
        const timestamp = document.createElement('p');
        timestamp.className = 'text-xs mt-1 opacity-80';
        timestamp.textContent = message.timestamp.toLocaleTimeString();
        
        bubble.appendChild(text);
        bubble.appendChild(timestamp);
        messageElement.appendChild(bubble);

        if (this.messageArea) {
            this.messageArea.appendChild(messageElement);
            this.messageArea.scrollTop = this.messageArea?.scrollHeight;
        }        
    }
}

window.initChatbot = function() {
    const script = document.querySelector('script[workspaceId-attr]');
    console.log("workspaceId-attr", script.getAttribute('workspaceId-attr'));
    console.log("userId-attr", script.getAttribute('userId-attr'));

    const config = {
        workspaceId: script.getAttribute('workspaceId-attr'),
        wsEndpoint: `ws://localhost:8000/api/v1/playground/chat`,
        userId: script.getAttribute('userId-attr'),
        theme: "light",
        position: "bottom-right",
        launcher: true
    }
    
    window.chatbotInstance = new ChatbotUI(config);
};

document.addEventListener('DOMContentLoaded', function() {
    window.initChatbot();
});

if (document.readyState === 'complete' || document.readyState === 'interactive') {
    setTimeout(window.initChatbot, 1);
}
