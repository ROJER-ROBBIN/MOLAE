// frontend/js/app.js

document.addEventListener('DOMContentLoaded', () => {
    // UI Elements
    const messageInput = document.getElementById('message-input');
    const sendBtn = document.getElementById('send-btn');
    const newConversationBtn = document.getElementById('new-conversation-btn');
    const mobileMenuBtn = document.getElementById('mobile-menu-btn');
    const sidebar = document.getElementById('sidebar');
    const drawerOverlay = document.getElementById('drawer-overlay');
    const promptBtns = document.querySelectorAll('.prompt-btn');

    // Initialize state from storage
    const messages = Storage.getMessages();
    ChatUI.renderHistory(messages);

    // Auto-resize textarea
    messageInput.addEventListener('input', function() {
        this.style.height = 'auto';
        this.style.height = (this.scrollHeight) + 'px';
        
        // Toggle send button
        if (this.value.trim().length > 0) {
            sendBtn.removeAttribute('disabled');
        } else {
            sendBtn.setAttribute('disabled', 'true');
        }
    });

    // Handle form submission (Send Message)
    async function handleSend() {
        const text = messageInput.value.trim();
        if (!text) return;

        // Reset input
        messageInput.value = '';
        messageInput.style.height = 'auto';
        sendBtn.setAttribute('disabled', 'true');
        messageInput.focus();

        // Update UI
        ChatUI.appendUserMessage(text);
        ChatUI.showTypingIndicator();
        
        // Save user message to storage
        Storage.saveMessage('user', text);

        try {
            const sessionId = Storage.getSessionId();
            const response = await window.API.sendMessage(text, sessionId);
            
            ChatUI.hideTypingIndicator();
            
            // Save session id if provided
            if (response.session_id) {
                Storage.setSessionId(response.session_id);
            }

            // Append and save AI response
            ChatUI.appendAIMessage(
                response.response, 
                "AI RECONSTRUCTION", 
                response.memories_used // if the backend provides it for dev
            );
            Storage.saveMessage('assistant', response.response, response.source || 'ai_reconstruction', response.memories_used);

        } catch (error) {
            ChatUI.hideTypingIndicator();
            ChatUI.showError(error.message);
        }
    }

    sendBtn.addEventListener('click', handleSend);

    messageInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault(); // Prevent new line
            handleSend();
        }
    });

    // Handle New Conversation
    newConversationBtn.addEventListener('click', () => {
        Storage.clearSession();
        ChatUI.clearChat();
        
        // Mobile drawer close
        sidebar.classList.remove('open');
        drawerOverlay.classList.remove('active');
    });

    // Handle Suggested Prompts
    promptBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const promptText = btn.getAttribute('data-prompt');
            messageInput.value = promptText;
            messageInput.style.height = 'auto';
            sendBtn.removeAttribute('disabled');
            messageInput.focus();
        });
    });

    // Mobile Navigation
    mobileMenuBtn.addEventListener('click', () => {
        sidebar.classList.add('open');
        drawerOverlay.classList.add('active');
    });

    drawerOverlay.addEventListener('click', () => {
        sidebar.classList.remove('open');
        drawerOverlay.classList.remove('active');
    });
});
