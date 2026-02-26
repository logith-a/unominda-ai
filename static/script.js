// Debug mode - see what's happening
console.log("🚀 Script loaded!");
console.log("Window location:", window.location.hostname);

// Use localhost explicitly
const API_BASE = 'http://localhost:5000';

// DOM Elements
const messagesContainer = document.getElementById('messages');
const userInput = document.getElementById('user-input');
const sendBtn = document.getElementById('send-btn');
const typingIndicator = document.getElementById('typing-indicator');
const sourcesPanel = document.getElementById('sources-panel');
const sourcesList = document.getElementById('sources-list');

let isProcessing = false;

// Auto-resize textarea
if (userInput) {
    userInput.addEventListener('input', function() {
        this.style.height = 'auto';
        this.style.height = (this.scrollHeight) + 'px';
        if (sendBtn) sendBtn.disabled = !this.value.trim();
    });
}

// Send message on Enter
if (userInput) {
    userInput.addEventListener('keydown', function(e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            if (this.value.trim() && !isProcessing) {
                sendMessage();
            }
        }
    });
}

// Send button click
if (sendBtn) {
    sendBtn.addEventListener('click', sendMessage);
}

// Suggestion chips
document.querySelectorAll('.suggestion-chip').forEach(chip => {
    chip.addEventListener('click', function() {
        if (userInput) {
            userInput.value = this.textContent;
            if (sendBtn) sendBtn.disabled = false;
            sendMessage();
        }
    });
});

// Load PDF list on startup
console.log("📚 Loading PDF list...");
loadPDFList();

function loadPDFList() {
    const pdfList = document.getElementById('pdf-files');
    const pdfCountSpan = document.getElementById('pdf-count');
    const pageCountSpan = document.getElementById('page-count');
    
    console.log(`Fetching PDFs from ${API_BASE}/api/pdfs...`);
    
    fetch(`${API_BASE}/api/pdfs`)
        .then(response => {
            console.log("Response status:", response.status);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            console.log("PDF data received:", data);
            
            if (pdfCountSpan) pdfCountSpan.textContent = data.total_pdfs || 0;
            if (pageCountSpan) pageCountSpan.textContent = data.total_pages || 0;
            
            if (!pdfList) {
                console.error("PDF list element not found!");
                return;
            }
            
            if (data.total_pdfs === 0) {
                pdfList.innerHTML = '<p class="loading">No PDFs found. Add some to the "pdfs" folder!</p>';
                return;
            }
            
            pdfList.innerHTML = '';
            data.pdfs.forEach(pdf => {
                const pdfItem = document.createElement('div');
                pdfItem.className = 'pdf-item';
                pdfItem.innerHTML = `
                    <i class="fas fa-file-pdf"></i>
                    <span class="pdf-name">${pdf}</span>
                `;
                pdfList.appendChild(pdfItem);
            });
            
            console.log(`✅ Loaded ${data.pdfs.length} PDFs`);
        })
        .catch(error => {
            console.error('❌ Error loading PDFs:', error);
            if (pdfList) {
                pdfList.innerHTML = `<p class="loading">❌ Cannot connect to server: ${error.message}<br>Make sure Flask is running at ${API_BASE}</p>`;
            }
        });
}

function sendMessage() {
    if (!userInput) return;
    
    const message = userInput.value.trim();
    if (!message || isProcessing) return;
    
    console.log("Sending message:", message);
    
    // Add user message
    addMessage(message, 'user');
    
    // Clear input
    userInput.value = '';
    userInput.style.height = 'auto';
    if (sendBtn) sendBtn.disabled = true;
    
    // Show typing indicator
    isProcessing = true;
    if (typingIndicator) typingIndicator.style.display = 'block';
    
    // Send to backend
    fetch(`${API_BASE}/api/chat`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ message: message })
    })
    .then(response => {
        console.log("Chat response status:", response.status);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        console.log("Chat response data:", data);
        
        if (typingIndicator) typingIndicator.style.display = 'none';
        
        addMessage(data.response, 'bot', data.images || []);
        
        isProcessing = false;
    })
    .catch(error => {
        console.error('❌ Chat error:', error);
        if (typingIndicator) typingIndicator.style.display = 'none';
        addMessage(`❌ Error: ${error.message}. Make sure Flask is running at ${API_BASE}`, 'bot');
        isProcessing = false;
    });
}

function addMessage(text, sender, images = []) {
    if (!messagesContainer) {
        console.error("Messages container not found!");
        return;
    }
    
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${sender}`;
    
    const avatar = document.createElement('div');
    avatar.className = sender === 'bot' ? 'bot-avatar' : 'user-avatar';
    avatar.innerHTML = sender === 'bot' ? '<i class="fas fa-robot"></i>' : '<i class="fas fa-user"></i>';
    
    const content = document.createElement('div');
    content.className = 'message-content';
    
    // Format text
    const formattedText = text.replace(/\n/g, '<br>');
    let contentHtml = `<p>${formattedText}</p>`;
    
    // Add images if present
    if (images && images.length > 0) {
        contentHtml += '<div class="image-gallery">';
        images.forEach(img => {
            contentHtml += `
                <div class="image-card">
                    <img src="data:${img.mime_type};base64,${img.data_base64}" 
                         alt="${img.caption || 'Image'}"
                         onclick="window.open(this.src, '_blank')"
                         style="cursor: pointer;">
                    <div class="image-caption">
                        <i class="fas fa-file-image"></i> ${img.caption || 'Image'}
                    </div>
                </div>
            `;
        });
        contentHtml += '</div>';
    }
    
    content.innerHTML = contentHtml;
    
    messageDiv.appendChild(avatar);
    messageDiv.appendChild(content);
    
    messagesContainer.appendChild(messageDiv);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

// Check if server is reachable
fetch(`${API_BASE}/api/status`)
    .then(response => response.json())
    .then(data => {
        console.log("✅ Server status:", data);
        // Update status indicator
        const statusDot = document.querySelector('.status .dot');
        if (statusDot) {
            statusDot.style.backgroundColor = '#27ae60';
        }
    })
    .catch(error => {
        console.error("❌ Cannot reach server:", error);
        const statusDiv = document.querySelector('.status');
        if (statusDiv) {
            statusDiv.innerHTML = '<span class="dot" style="background:#ff4444;"></span> Server Offline';
        }
    });