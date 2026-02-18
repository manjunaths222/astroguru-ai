// Chat functionality for query orders

let currentChatOrderId = null;

// Show chat interface
function showChat(orderId) {
    // Use global hideAllSections if available
    if (window.hideAllSections) {
        window.hideAllSections();
    } else {
        // Fallback
        const sections = ['welcomePage', 'authRequired', 'dashboardContainer', 'formContainer', 
                         'paymentSuccess', 'paymentFailure', 'resultsContainer', 'chatContainer'];
        sections.forEach(id => {
            const el = document.getElementById(id);
            if (el) el.style.display = 'none';
        });
    }
    
    const chatContainer = document.getElementById('chatContainer');
    const navbar = document.getElementById('navbar');
    const header = document.getElementById('header');
    
    if (chatContainer) {
        chatContainer.style.display = 'block';
    }
    if (navbar) {
        navbar.style.display = 'block';
    }
    if (header) {
        header.style.display = 'none';
    }
    
    currentChatOrderId = orderId;
    loadChatHistory(orderId);
    
    // Scroll to top
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

// Make showChat globally accessible
window.showChat = showChat;

// Load chat history
async function loadChatHistory(orderId) {
    const chatMessages = document.getElementById('chatMessages');
    chatMessages.innerHTML = '<div class="loading">Loading conversation history...</div>';
    
    try {
        const response = await fetch(`${window.API_BASE_URL}/api/v1/orders/${orderId}/chat/history`, {
            headers: authManager.getAuthHeaders()
        });
        
        if (!response.ok) {
            if (response.status === 401) {
                authManager.clearAuth();
                showAuthRequired();
                return;
            }
            throw new Error('Failed to load chat history');
        }
        
        const data = await response.json();
        
        // Log conversation history info
        console.log(`Loaded conversation history: ${data.messages.length} messages (${data.user_message_count || 0} user messages, ${data.messages_remaining || 0} remaining)`);
        
        displayChatMessages(data.messages);
        updateMessageLimitInfo(data.user_message_count || 0, data.messages_remaining || 0, data.can_continue !== false);
        
        // Show conversation history indicator if there are messages
        if (data.messages && data.messages.length > 0) {
            showConversationHistoryIndicator(data.messages.length);
        }
        
    } catch (error) {
        console.error('Error loading chat history:', error);
        chatMessages.innerHTML = '<div class="error-state">Failed to load conversation history</div>';
    }
}

// Show conversation history indicator
function showConversationHistoryIndicator(messageCount) {
    // This function can be used to show a badge or indicator that conversation history is loaded
    // For now, we'll just log it - can be enhanced with UI element if needed
    console.log(`Conversation history loaded: ${messageCount} messages in history`);
}

// Display chat messages
function displayChatMessages(messages) {
    const chatMessages = document.getElementById('chatMessages');
    
    if (messages.length === 0) {
        chatMessages.innerHTML = '<div class="empty-state">No conversation history yet. Start by sending a message!</div>';
        return;
    }
    
    // Group messages by date for better organization
    const messagesByDate = {};
    messages.forEach(msg => {
        const date = new Date(msg.created_at).toLocaleDateString();
        if (!messagesByDate[date]) {
            messagesByDate[date] = [];
        }
        messagesByDate[date].push(msg);
    });
    
    // Build HTML with date separators
    let html = '';
    const dates = Object.keys(messagesByDate);
    
    dates.forEach((date, dateIndex) => {
        // Add date separator (except for first date)
        if (dateIndex > 0 || messages.length > 0) {
            html += `<div class="chat-date-separator">
                <span>${date}</span>
            </div>`;
        }
        
        // Add messages for this date
        messagesByDate[date].forEach((msg, msgIndex) => {
            const isUser = msg.role === 'user';
            const timestamp = new Date(msg.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
            // Use formatMarkdown for assistant messages, escapeHtml for user messages (user messages are plain text)
            const content = isUser ? escapeHtml(msg.content) : formatMarkdown(msg.content);
            
            // Show message number for context (first message is initial query)
            const isInitialQuery = msg.message_number === 1 && msg.role === 'user';
            const messageLabel = isInitialQuery ? 'Initial Query' : (msg.message_number > 1 ? `Message ${msg.message_number}` : '');
            
            html += `
                <div class="chat-message ${isUser ? 'user-message' : 'assistant-message'} message-new">
                    ${messageLabel ? `<div class="message-label">${messageLabel}</div>` : ''}
                    <div class="message-content ${isUser ? '' : 'markdown-content'}">
                        ${content}
                    </div>
                    <div class="message-meta">
                        <span class="message-role">${isUser ? 'You' : 'AstroGuru AI'}</span>
                        <span class="message-time">${timestamp}</span>
                    </div>
                </div>
            `;
        });
    });
    
    chatMessages.innerHTML = html;
    
    // Scroll to bottom with smooth animation
    setTimeout(() => {
        chatMessages.scrollTo({
            top: chatMessages.scrollHeight,
            behavior: 'smooth'
        });
    }, 100);
}

// Update message limit info
function updateMessageLimitInfo(userMessageCount, messagesRemaining, canContinue) {
    const messageLimitInfo = document.getElementById('messageLimitInfo');
    const chatInput = document.getElementById('chatInput');
    const sendChatBtn = document.getElementById('sendChatBtn');
    
    if (canContinue) {
        messageLimitInfo.innerHTML = `<span class="message-limit-text">${messagesRemaining} message${messagesRemaining !== 1 ? 's' : ''} remaining (${userMessageCount}/3 sent)</span>`;
        messageLimitInfo.className = 'message-limit-info';
        chatInput.disabled = false;
        sendChatBtn.disabled = false;
    } else {
            messageLimitInfo.innerHTML = `
            <span class="message-limit-text limit-reached">Message limit reached (3/3 messages sent). Please create a new query to continue.</span>
            <button class="btn-primary btn-small" id="createNewQueryBtn" style="margin-top: 8px;">Create New Query</button>
        `;
            
            // Add event listener for the button
            const createBtn = document.getElementById('createNewQueryBtn');
            if (createBtn) {
                createBtn.addEventListener('click', () => {
                    if (window.showForm) {
                        window.showForm();
                    } else {
                        // Fallback: navigate to form
                        hideAllSections();
                        const formContainer = document.getElementById('formContainer');
                        if (formContainer) {
                            formContainer.style.display = 'block';
                            document.getElementById('navbar').style.display = 'block';
                            document.getElementById('header').style.display = 'none';
                            window.scrollTo({ top: 0, behavior: 'smooth' });
                        }
                    }
                });
            }
        messageLimitInfo.className = 'message-limit-info limit-reached';
        chatInput.disabled = true;
        sendChatBtn.disabled = true;
    }
}

// Send chat message
async function sendChatMessage() {
    const chatInput = document.getElementById('chatInput');
    const sendChatBtn = document.getElementById('sendChatBtn');
    const chatMessages = document.getElementById('chatMessages');
    const message = chatInput.value.trim();
    
    if (!message || !currentChatOrderId) {
        return;
    }
    
    if (sendChatBtn.disabled) {
        return;
    }
    
    // Get current message count for numbering
    const currentMessages = Array.from(chatMessages.querySelectorAll('.chat-message'));
    const nextMessageNumber = currentMessages.length + 1;
    
    // Add user message immediately to chat
    const userMessageHtml = `
        <div class="chat-message user-message message-new">
            <div class="message-content">
                ${escapeHtml(message)}
            </div>
            <div class="message-meta">
                <span class="message-role">You</span>
                <span class="message-time">${new Date().toLocaleString()}</span>
            </div>
        </div>
    `;
    chatMessages.insertAdjacentHTML('beforeend', userMessageHtml);
    
    // Add loading indicator for assistant response
    const loadingHtml = `
        <div class="chat-message assistant-message message-loading">
            <div class="message-content">
                <div class="typing-indicator">
                    <span></span>
                    <span></span>
                    <span></span>
                </div>
            </div>
            <div class="message-meta">
                <span class="message-role">AstroGuru AI</span>
                <span class="message-time">Thinking...</span>
            </div>
        </div>
    `;
    chatMessages.insertAdjacentHTML('beforeend', loadingHtml);
    
    // Scroll to bottom
    chatMessages.scrollTop = chatMessages.scrollHeight;
    
    // Clear input and disable
    chatInput.value = '';
    chatInput.disabled = true;
    sendChatBtn.disabled = true;
    sendChatBtn.textContent = 'Sending...';
    
    try {
        const response = await fetch(`${window.API_BASE_URL}/api/v1/orders/${currentChatOrderId}/chat`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                ...authManager.getAuthHeaders()
            },
            body: JSON.stringify({ message })
        });
        
        if (!response.ok) {
            if (response.status === 401) {
                authManager.clearAuth();
                showAuthRequired();
                return;
            }
            const error = await response.json();
            throw new Error(error.detail || 'Failed to send message');
        }
        
        const data = await response.json();
        
        // Remove loading indicator
        const loadingEl = chatMessages.querySelector('.message-loading');
        if (loadingEl) {
            loadingEl.remove();
        }
        
        // Add assistant response
        const assistantMessageHtml = `
            <div class="chat-message assistant-message message-new">
                <div class="message-content markdown-content">
                    ${formatMarkdown(data.message)}
                </div>
                <div class="message-meta">
                    <span class="message-role">AstroGuru AI</span>
                    <span class="message-time">${new Date().toLocaleString()}</span>
                </div>
            </div>
        `;
        chatMessages.insertAdjacentHTML('beforeend', assistantMessageHtml);
        
        // Scroll to bottom
        chatMessages.scrollTop = chatMessages.scrollHeight;
        
        // Reload chat history to show new messages and updated counts
        // This ensures the full conversation history is displayed including the new message
        await loadChatHistory(currentChatOrderId);
        
        // Re-enable input
        chatInput.disabled = false;
        sendChatBtn.disabled = false;
        sendChatBtn.textContent = 'Send';
        chatInput.focus();
        
    } catch (error) {
        console.error('Error sending chat message:', error);
        
        // Remove loading indicator
        const loadingEl = chatMessages.querySelector('.message-loading');
        if (loadingEl) {
            loadingEl.remove();
        }
        
        // Show error message
        showNotification(error.message || 'Failed to send message', 'error');
        
        // Re-enable input
        chatInput.disabled = false;
        sendChatBtn.disabled = false;
        sendChatBtn.textContent = 'Send';
        chatInput.focus();
    }
}

// Handle Enter key in chat input
document.addEventListener('DOMContentLoaded', () => {
    const chatInput = document.getElementById('chatInput');
    if (chatInput) {
        chatInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                sendChatMessage();
            }
        });
    }
});

// Escape HTML to prevent XSS (for user messages)
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Format markdown (reuse from app.js)
function formatMarkdown(text) {
    if (!text) return '';
    
    const lines = text.split('\n');
    let html = '';
    let inList = false;
    let inParagraph = false;
    
    for (let i = 0; i < lines.length; i++) {
        const line = lines[i].trim();
        
        if (!line) {
            if (inList) {
                html += '</ul>';
                inList = false;
            }
            if (inParagraph) {
                html += '</p>';
                inParagraph = false;
            }
            continue;
        }
        
        if (line.startsWith('#### ')) {
            if (inList) { html += '</ul>'; inList = false; }
            if (inParagraph) { html += '</p>'; inParagraph = false; }
            html += `<h4>${line.substring(5)}</h4>`;
        } else if (line.startsWith('### ')) {
            if (inList) { html += '</ul>'; inList = false; }
            if (inParagraph) { html += '</p>'; inParagraph = false; }
            html += `<h3>${line.substring(4)}</h3>`;
        } else if (line.startsWith('## ')) {
            if (inList) { html += '</ul>'; inList = false; }
            if (inParagraph) { html += '</p>'; inParagraph = false; }
            html += `<h2>${line.substring(3)}</h2>`;
        } else if (line.startsWith('# ')) {
            if (inList) { html += '</ul>'; inList = false; }
            if (inParagraph) { html += '</p>'; inParagraph = false; }
            html += `<h1>${line.substring(2)}</h1>`;
        } else if (line.startsWith('---')) {
            if (inList) { html += '</ul>'; inList = false; }
            if (inParagraph) { html += '</p>'; inParagraph = false; }
            html += '<hr>';
        } else if (line.match(/^[\-\*] /) || line.match(/^\d+\. /)) {
            if (!inList) {
                if (inParagraph) { html += '</p>'; inParagraph = false; }
                html += '<ul>';
                inList = true;
            }
            const listContent = line.replace(/^[\-\*] /, '').replace(/^\d+\. /, '');
            html += `<li>${processInlineMarkdown(listContent)}</li>`;
        } else {
            if (inList) {
                html += '</ul>';
                inList = false;
            }
            if (!inParagraph) {
                html += '<p>';
                inParagraph = true;
            } else {
                html += '<br>';
            }
            html += processInlineMarkdown(line);
        }
    }
    
    if (inList) html += '</ul>';
    if (inParagraph) html += '</p>';
    
    return html;
}

// Process inline markdown
function processInlineMarkdown(text) {
    return text
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(/__(.*?)__/g, '<strong>$1</strong>')
        .replace(/\*(.*?)\*/g, '<em>$1</em>')
        .replace(/_(.*?)_/g, '<em>$1</em>')
        .replace(/`(.*?)`/g, '<code>$1</code>');
}

