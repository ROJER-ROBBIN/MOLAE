// frontend/js/chat.js

const UI = {
    messagesWrapper: document.getElementById('messages-wrapper'),
    emptyState: document.getElementById('empty-state'),
    typingIndicator: document.getElementById('typing-indicator'),
    errorBanner: document.getElementById('error-banner'),
    chatContainer: document.getElementById('chat-container')
};

function scrollToBottom() {
    UI.chatContainer.scrollTop = UI.chatContainer.scrollHeight;
}

function escapeHTML(str) {
    const p = document.createElement("p");
    p.appendChild(document.createTextNode(str));
    return p.innerHTML;
}

function formatText(text) {
    return escapeHTML(text);
}

function appendUserMessage(text) {
    UI.emptyState.style.display = 'none';
    const msgDiv = document.createElement('div');
    msgDiv.className = 'message user-message';
    
    const now = new Date();
    const timeString = now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    
    msgDiv.innerHTML = formatText(text) + `<div class="message-meta"><span>${timeString}</span><span class="ticks">✓✓</span></div>`;
    UI.messagesWrapper.insertBefore(msgDiv, UI.typingIndicator);
    scrollToBottom();
}

function appendAIMessage(text, sourceLabel = "AI RECONSTRUCTION", memories = null) {
    UI.emptyState.style.display = 'none';
    const msgDiv = document.createElement('div');
    msgDiv.className = 'message ai-message';
    
    const labelDiv = document.createElement('div');
    labelDiv.className = 'message-label';
    labelDiv.textContent = sourceLabel;
    msgDiv.appendChild(labelDiv);
    
    const textNode = document.createElement('span');
    textNode.innerHTML = formatText(text);
    msgDiv.appendChild(textNode);

    const now = new Date();
    const timeString = now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    
    const metaDiv = document.createElement('div');
    metaDiv.className = 'message-meta';
    metaDiv.innerHTML = `<span>${timeString}</span>`;
    msgDiv.appendChild(metaDiv);

    // If memories were used, add the debug expander
    if (memories && memories.length > 0) {
        const memoryBtn = document.createElement('button');
        memoryBtn.className = 'memories-used-btn';
        memoryBtn.innerHTML = `
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <circle cx="12" cy="12" r="10"></circle>
                <line x1="12" y1="16" x2="12" y2="12"></line>
                <line x1="12" y1="8" x2="12.01" y2="8"></line>
            </svg>
            Memories used
        `;
        
        const memoryPanel = document.createElement('div');
        memoryPanel.className = 'memories-panel';
        
        let memoryHTML = '<strong>Historical Sources:</strong><br/>';
        memories.forEach(m => {
            memoryHTML += `&bull; ${escapeHTML(m.date || 'Unknown')} - <i>${escapeHTML(m.document.substring(0, 100))}...</i><br/>`;
        });
        memoryPanel.innerHTML = memoryHTML;
        
        memoryBtn.onclick = () => {
            memoryPanel.classList.toggle('open');
        };
        
        msgDiv.appendChild(document.createElement('br'));
        msgDiv.appendChild(memoryBtn);
        msgDiv.appendChild(memoryPanel);
    }
    
    UI.messagesWrapper.insertBefore(msgDiv, UI.typingIndicator);
    scrollToBottom();
}

function showTypingIndicator() {
    UI.typingIndicator.style.display = 'flex';
    scrollToBottom();
}

function hideTypingIndicator() {
    UI.typingIndicator.style.display = 'none';
}

function showError(msg) {
    UI.errorBanner.textContent = msg;
    UI.errorBanner.style.display = 'block';
    setTimeout(() => {
        UI.errorBanner.style.display = 'none';
    }, 5000);
}

function clearChat() {
    const messages = UI.messagesWrapper.querySelectorAll('.message:not(.typing)');
    messages.forEach(msg => msg.remove());
    UI.emptyState.style.display = 'flex';
    hideTypingIndicator();
    UI.errorBanner.style.display = 'none';
}

function renderHistory(messages) {
    if (!messages || messages.length === 0) {
        clearChat();
        return;
    }
    
    UI.emptyState.style.display = 'none';
    const msgs = UI.messagesWrapper.querySelectorAll('.message:not(.typing)');
    msgs.forEach(msg => msg.remove());
    
    messages.forEach(msg => {
        if (msg.role === 'user') {
            appendUserMessage(msg.content);
        } else if (msg.role === 'assistant') {
            // we don't store memories locally yet, but could be added if needed
            appendAIMessage(msg.content, msg.source === 'ai_reconstruction' ? 'AI RECONSTRUCTION' : 'AI RECONSTRUCTION', msg.memories);
        }
    });
}

window.ChatUI = {
    appendUserMessage,
    appendAIMessage,
    showTypingIndicator,
    hideTypingIndicator,
    showError,
    clearChat,
    renderHistory
};
