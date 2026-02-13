// API Configuration
const API_BASE_URL = window.location.origin;
const API_ENDPOINT = `${API_BASE_URL}/api/v1/chat`;

// State
let sessionId = null;
let isAnalyzing = false;

// DOM Elements
const formContainer = document.getElementById('formContainer');
const resultsContainer = document.getElementById('resultsContainer');
const birthForm = document.getElementById('birthForm');
const placeInput = document.getElementById('placeOfBirth');
const suggestionsDiv = document.getElementById('suggestions');
const submitBtn = document.getElementById('submitBtn');
const newAnalysisBtn = document.getElementById('newAnalysisBtn');
const loadingDiv = document.getElementById('loading');
const errorMessageDiv = document.getElementById('errorMessage');
const messagesDiv = document.getElementById('messages');
const analysisSections = document.getElementById('analysisSections');
const chartSection = document.getElementById('chartSection');
const dashaSection = document.getElementById('dashaSection');
const goalSection = document.getElementById('goalSection');
const recommendationsSection = document.getElementById('recommendationsSection');
const summarySection = document.getElementById('summarySection');
const expandableSections = document.getElementById('expandableSections');
const detailedSections = document.getElementById('detailedSections');
const toggleDetailsBtn = document.getElementById('toggleDetailsBtn');
const chatInterface = document.getElementById('chatInterface');
const chatMessagesContainer = document.getElementById('chatMessagesContainer');
const chatMessages = document.getElementById('chatMessages');
const chatInput = document.getElementById('chatInput');
const sendChatBtn = document.getElementById('sendChatBtn');

// Location autocomplete using Nominatim (OpenStreetMap)
// This provides comprehensive coverage of all locations in India and worldwide
let locationSearchTimeout = null;
let currentSearchAbortController = null;

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    // Generate session ID
    sessionId = generateSessionId();
    
    // Setup form submission
    birthForm.addEventListener('submit', handleFormSubmit);
    
    // Setup location autocomplete
    setupLocationAutocomplete();
    
    // Setup new analysis button
    newAnalysisBtn.addEventListener('click', resetForm);
    
    // Setup email checkbox
    const sendEmailCheckbox = document.getElementById('sendEmailCheckbox');
    const emailInputGroup = document.getElementById('emailInputGroup');
    const emailInput = document.getElementById('email');
    
    if (sendEmailCheckbox && emailInputGroup && emailInput) {
        sendEmailCheckbox.addEventListener('change', function() {
            if (this.checked) {
                emailInputGroup.style.display = 'block';
                emailInput.required = true;
            } else {
                emailInputGroup.style.display = 'none';
                emailInput.required = false;
                emailInput.value = '';
            }
        });
    }
    
    // Setup toggle details button
    if (toggleDetailsBtn) {
        toggleDetailsBtn.addEventListener('click', () => {
            const isVisible = detailedSections.style.display !== 'none';
            detailedSections.style.display = isVisible ? 'none' : 'block';
            toggleDetailsBtn.querySelector('span:first-child').style.display = isVisible ? 'inline' : 'none';
            toggleDetailsBtn.querySelector('span:last-child').style.display = isVisible ? 'none' : 'inline';
        });
    }
    
    // Setup chat interface
    if (sendChatBtn && chatInput) {
        sendChatBtn.addEventListener('click', handleChatSubmit);
        chatInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                handleChatSubmit();
            }
        });
    }
    
    // Keyboard navigation will be handled inside setupLocationAutocomplete
});

// Generate unique session ID
function generateSessionId() {
    return `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
}

// Setup location autocomplete using Nominatim API
function setupLocationAutocomplete() {
    let selectedIndex = -1;
    let currentSuggestions = [];
    
    placeInput.addEventListener('input', (e) => {
        const query = e.target.value.trim();
        
        // Cancel previous search
        if (currentSearchAbortController) {
            currentSearchAbortController.abort();
        }
        
        if (query.length < 2) {
            suggestionsDiv.classList.remove('show');
            return;
        }
        
        // Debounce API calls
        clearTimeout(locationSearchTimeout);
        locationSearchTimeout = setTimeout(() => {
            searchLocations(query);
        }, 300);
    });
    
    placeInput.addEventListener('blur', () => {
        // Delay to allow click event on suggestions
        setTimeout(() => {
            suggestionsDiv.classList.remove('show');
        }, 200);
    });
    
    async function searchLocations(query) {
        // Create new abort controller for this search
        currentSearchAbortController = new AbortController();
        
        try {
            // Search locations using Nominatim API (OpenStreetMap)
            // Prioritizes India but also searches worldwide if needed
            const url = `https://nominatim.openstreetmap.org/search?` +
                `q=${encodeURIComponent(query)}` +
                `&countrycodes=in` + // Prioritize India (country code: in)
                `&limit=10` +
                `&format=json` +
                `&addressdetails=1` +
                `&accept-language=en`;
            
            // Add delay to respect Nominatim rate limits (1 request per second)
            await new Promise(resolve => setTimeout(resolve, 1000));
            
            const response = await fetch(url, {
                signal: currentSearchAbortController.signal,
                headers: {
                    'User-Agent': 'AstroGuru-AI/1.0', // Required by Nominatim
                    'Accept': 'application/json'
                }
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            
            // Format results
            const suggestions = data.map(item => {
                const address = item.address || {};
                const parts = [];
                
                // Build location string: City, State, Country
                if (address.city || address.town || address.village) {
                    parts.push(address.city || address.town || address.village);
                }
                if (address.state) {
                    parts.push(address.state);
                }
                if (address.country) {
                    parts.push(address.country);
                }
                
                const locationString = parts.length > 0 
                    ? parts.join(', ')
                    : item.display_name;
                
                return {
                    display: locationString,
                    full: item.display_name,
                    lat: item.lat,
                    lon: item.lon,
                    city: address.city || address.town || address.village || '',
                    state: address.state || '',
                    country: address.country || 'India'
                };
            });
            
            currentSuggestions = suggestions;
            displaySuggestions(suggestions);
            selectedIndex = -1;
            
        } catch (error) {
            if (error.name === 'AbortError') {
                // Search was cancelled, ignore
                return;
            }
            console.error('Error searching locations:', error);
            // Fallback to empty suggestions
            suggestionsDiv.classList.remove('show');
        }
    }
    
    function displaySuggestions(suggestions) {
        if (suggestions.length === 0) {
            suggestionsDiv.classList.remove('show');
            return;
        }
        
        suggestionsDiv.innerHTML = suggestions.map((suggestion, index) => 
            `<div class="suggestion-item" data-index="${index}">
                <div class="suggestion-main">${highlightMatch(suggestion.display, placeInput.value)}</div>
                <div class="suggestion-detail">${suggestion.full}</div>
            </div>`
        ).join('');
        
        suggestionsDiv.classList.add('show');
        
        // Add click handlers
        suggestionsDiv.querySelectorAll('.suggestion-item').forEach((item, index) => {
            item.addEventListener('click', () => {
                const suggestion = suggestions[index];
                placeInput.value = suggestion.display;
                // Store coordinates in hidden fields
                document.getElementById('latitude').value = suggestion.lat || '';
                document.getElementById('longitude').value = suggestion.lon || '';
                suggestionsDiv.classList.remove('show');
            });
        });
    }
    
    function highlightMatch(text, query) {
        if (!query) return text;
        const regex = new RegExp(`(${escapeRegex(query)})`, 'gi');
        return text.replace(regex, '<strong>$1</strong>');
    }
    
    function escapeRegex(string) {
        return string.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    }
    
}

// Handle form submission
async function handleFormSubmit(e) {
    e.preventDefault();
    
    if (isAnalyzing) return;
    
    // Get form data
    const formData = new FormData(birthForm);
    const name = formData.get('name');
    const dateOfBirth = formData.get('dateOfBirth');
    const timeOfBirth = formData.get('timeOfBirth');
    const placeOfBirth = formData.get('placeOfBirth');
    const latitude = formData.get('latitude');
    const longitude = formData.get('longitude');
    const goals = Array.from(formData.getAll('goals'));
    const sendEmail = document.getElementById('sendEmailCheckbox').checked;
    const email = sendEmail ? formData.get('email') : null;
    
    // Validate
    if (!name || !dateOfBirth || !timeOfBirth || !placeOfBirth) {
        showError('Please fill in all required fields.');
        return;
    }
    
    // Validate goals - at least one must be selected
    if (goals.length === 0) {
        showError('Please select at least one goal.');
        return;
    }
    
    // Validate email if email option is selected
    if (sendEmail && !email) {
        showError('Please provide your email address to receive the report.');
        return;
    }
    
    // Basic email validation
    if (sendEmail && email) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(email)) {
            showError('Please enter a valid email address.');
            return;
        }
    }
    
    // Show results container
    formContainer.style.display = 'none';
    resultsContainer.style.display = 'block';
    loadingDiv.style.display = 'block';
    errorMessageDiv.style.display = 'none';
    analysisSections.style.display = 'none';
    messagesDiv.innerHTML = '';
    
    // Build message with coordinates if available
    let message = `Hi, I'd like to get my horoscope analyzed. My details:\n- Name: ${name}\n- Date of Birth: ${dateOfBirth}\n- Time of Birth: ${timeOfBirth}\n- Place of Birth: ${placeOfBirth}`;
    
    // Add coordinates if available from autocomplete
    if (latitude && longitude) {
        message += `\n- Coordinates: Latitude ${latitude}, Longitude ${longitude}`;
    }
    
    if (goals.length > 0) {
        message += `\n- Goals: ${goals.join(', ')}`;
    }
    
    // Add user message
    addMessage('user', message);
    
    // Show email confirmation message if email is selected
    if (sendEmail && email) {
        addMessage('assistant', `📧 Great! Your analysis is being prepared. We'll send it to ${email} when ready. You can also view it here once it's complete.`);
    }
    
    isAnalyzing = true;
    submitBtn.disabled = true;
    
    try {
        // Send initial request with email options
        const response = await sendChatMessage(message, sendEmail, email);
        
        // Add assistant response
        addMessage('assistant', response.response);
        
        // If analysis is complete, show all sections
        if (response.analysis_complete) {
            displayAnalysisResults(response);
            // Show email confirmation if email was sent
            if (sendEmail && email) {
                addMessage('assistant', `✅ Your complete astrology report has been sent to ${email}! You can also view it below.`);
            }
        } else {
            // Continue conversation if needed
            await continueAnalysis(sendEmail, email);
        }
        
        // Show chat interface immediately for continuous conversation
        chatInterface.style.display = 'block';
        chatInput.disabled = false;
        sendChatBtn.disabled = false;
    } catch (error) {
        showError(`Error: ${error.message}`);
    } finally {
        isAnalyzing = false;
        loadingDiv.style.display = 'none';
    }
}

// Continue analysis conversation
async function continueAnalysis(sendEmail = false, email = null) {
    let attempts = 0;
    const maxAttempts = 20;
    let lastResponse = '';
    let sameResponseCount = 0;
    
    // Show chat loading during analysis continuation
    const chatLoading = document.getElementById('chatLoading');
    
    while (attempts < maxAttempts) {
        // Show loading indicator
        if (chatLoading) {
            chatLoading.style.display = 'flex';
        }
        
        await new Promise(resolve => setTimeout(resolve, 2000));
        
        try {
            const response = await sendChatMessage('Please continue with the analysis.', sendEmail, email);
            
            // Hide loading indicator
            if (chatLoading) {
                chatLoading.style.display = 'none';
            }
            
            if (response.response) {
                // Check if we're getting the same response (loop detection)
                if (response.response === lastResponse) {
                    sameResponseCount++;
                    if (sameResponseCount >= 3) {
                        addMessage('assistant', 'I have all the information I need. Please check your report below or ask me any questions!');
                        // Show chat interface for follow-up questions
                        chatInterface.style.display = 'block';
                        chatInput.disabled = false;
                        sendChatBtn.disabled = false;
                        break;
                    }
                } else {
                    sameResponseCount = 0;
                    lastResponse = response.response;
                }
                
                addMessage('assistant', response.response);
            }
            
            if (response.analysis_complete) {
                displayAnalysisResults(response);
                // Show email confirmation if email was sent
                if (sendEmail && email) {
                    addMessage('assistant', `✅ Your complete astrology report has been sent to ${email}! You can also view it below.`);
                }
                break;
            }
            
            attempts++;
        } catch (error) {
            console.error('Error continuing analysis:', error);
            if (chatLoading) {
                chatLoading.style.display = 'none';
            }
            addMessage('assistant', `I encountered an issue: ${error.message}. Please check your report or ask me a question.`);
            // Show chat interface for follow-up questions
            chatInterface.style.display = 'block';
            chatInput.disabled = false;
            sendChatBtn.disabled = false;
            break;
        }
    }
    
    // Hide loading if still showing
    if (chatLoading) {
        chatLoading.style.display = 'none';
    }
    
    if (attempts >= maxAttempts && !response?.analysis_complete) {
        addMessage('assistant', 'The analysis is taking longer than expected. Your report is available below. Feel free to ask me any questions!');
        // Show chat interface for follow-up questions
        chatInterface.style.display = 'block';
        chatInput.disabled = false;
        sendChatBtn.disabled = false;
    }
}

// Send chat message to API
async function sendChatMessage(message, sendEmail = false, email = null) {
    const requestBody = {
        message: message,
        session_id: sessionId
    };
    
    // Add email fields if provided
    if (sendEmail && email) {
        requestBody.send_email = true;
        requestBody.email = email;
    }
    
    const response = await fetch(API_ENDPOINT, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestBody)
    });
    
    if (!response.ok) {
        const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
        throw new Error(error.detail || `HTTP error! status: ${response.status}`);
    }
    
    return await response.json();
}

// Display analysis results
function displayAnalysisResults(response) {
    loadingDiv.style.display = 'none';
    analysisSections.style.display = 'block';
    
    // Show only summary by default
    if (response.summary) {
        summarySection.style.display = 'block';
        document.getElementById('summaryContent').innerHTML = formatMarkdown(response.summary);
    }
    
    // Store detailed sections but hide them initially
    let hasDetails = false;
    
    if (response.chart_data_analysis) {
        chartSection.style.display = 'block';
        document.getElementById('chartContent').innerHTML = formatMarkdown(response.chart_data_analysis);
        hasDetails = true;
    }
    
    if (response.dasha_analysis) {
        dashaSection.style.display = 'block';
        document.getElementById('dashaContent').innerHTML = formatMarkdown(response.dasha_analysis);
        hasDetails = true;
    }
    
    if (response.goal_analysis) {
        goalSection.style.display = 'block';
        document.getElementById('goalContent').innerHTML = formatMarkdown(response.goal_analysis);
        hasDetails = true;
    }
    
    if (response.recommendations) {
        recommendationsSection.style.display = 'block';
        document.getElementById('recommendationsContent').innerHTML = formatMarkdown(response.recommendations);
        hasDetails = true;
    }
    
    // Show expandable sections toggle if there are details
    if (hasDetails) {
        expandableSections.style.display = 'block';
    }
    
    // Show chat interface after analysis is complete
    if (response.analysis_complete) {
        chatInterface.style.display = 'block';
        // Enable chat input
        chatInput.disabled = false;
        sendChatBtn.disabled = false;
        chatInput.focus();
    }
    
    // Scroll to results
    resultsContainer.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

// Handle chat submission
async function handleChatSubmit() {
    const message = chatInput.value.trim();
    if (!message || isAnalyzing) return;
    
    // Add user message to chat
    addChatMessage('user', message);
    chatInput.value = '';
    
    // Show loading indicator
    isAnalyzing = true;
    sendChatBtn.disabled = true;
    chatInput.disabled = true;
    const chatLoading = document.getElementById('chatLoading');
    if (chatLoading) {
        chatLoading.style.display = 'flex';
    }
    
    try {
        const response = await sendChatMessage(message);
        
        if (response.response) {
            addChatMessage('assistant', response.response);
        }
        
        // Update analysis sections if new data is available
        if (response.analysis_complete || response.summary) {
            displayAnalysisResults(response);
        }
    } catch (error) {
        addChatMessage('assistant', `Error: ${error.message}`);
    } finally {
        isAnalyzing = false;
        sendChatBtn.disabled = false;
        chatInput.disabled = false;
        if (chatLoading) {
            chatLoading.style.display = 'none';
        }
        chatInput.focus();
    }
}

// Add message to chat interface
function addChatMessage(role, content) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${role}`;
    messageDiv.innerHTML = formatMarkdown(content);
    chatMessages.appendChild(messageDiv);
    chatMessagesContainer.scrollTop = chatMessagesContainer.scrollHeight;
}

// Format markdown to HTML (improved)
function formatMarkdown(text) {
    if (!text) return '';
    
    // Split into lines for better processing
    const lines = text.split('\n');
    let html = '';
    let inList = false;
    let inParagraph = false;
    
    for (let i = 0; i < lines.length; i++) {
        const line = lines[i].trim();
        
        // Skip empty lines (but close paragraphs/lists)
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
        
        // Headers
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
        }
        // Horizontal rule
        else if (line.startsWith('---')) {
            if (inList) { html += '</ul>'; inList = false; }
            if (inParagraph) { html += '</p>'; inParagraph = false; }
            html += '<hr>';
        }
        // List items
        else if (line.match(/^[\-\*] /) || line.match(/^\d+\. /)) {
            if (!inList) {
                if (inParagraph) { html += '</p>'; inParagraph = false; }
                html += '<ul>';
                inList = true;
            }
            const listContent = line.replace(/^[\-\*] /, '').replace(/^\d+\. /, '');
            html += `<li>${processInlineMarkdown(listContent)}</li>`;
        }
        // Regular paragraph
        else {
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
    
    // Close any open tags
    if (inList) html += '</ul>';
    if (inParagraph) html += '</p>';
    
    return html;
}

// Process inline markdown (bold, italic, etc.)
function processInlineMarkdown(text) {
    return text
        // Bold
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(/__(.*?)__/g, '<strong>$1</strong>')
        // Italic
        .replace(/\*(.*?)\*/g, '<em>$1</em>')
        .replace(/_(.*?)_/g, '<em>$1</em>')
        // Code
        .replace(/`(.*?)`/g, '<code>$1</code>');
}

// Add message to chat
function addMessage(role, content) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${role}`;
    messageDiv.textContent = content;
    messagesDiv.appendChild(messageDiv);
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
}

// Show error message
function showError(message) {
    errorMessageDiv.textContent = message;
    errorMessageDiv.style.display = 'block';
    loadingDiv.style.display = 'none';
}

// Reset form
function resetForm() {
    formContainer.style.display = 'block';
    resultsContainer.style.display = 'none';
    birthForm.reset();
    messagesDiv.innerHTML = '';
    chatMessages.innerHTML = '';
    analysisSections.style.display = 'none';
    expandableSections.style.display = 'none';
    detailedSections.style.display = 'none';
    chatInterface.style.display = 'none';
    
    // Clear hidden coordinate fields
    document.getElementById('latitude').value = '';
    document.getElementById('longitude').value = '';
    
    // Reset email fields
    const sendEmailCheckbox = document.getElementById('sendEmailCheckbox');
    const emailInput = document.getElementById('email');
    const emailInputGroup = document.getElementById('emailInputGroup');
    if (sendEmailCheckbox) sendEmailCheckbox.checked = false;
    if (emailInput) {
        emailInput.value = '';
        emailInput.required = false;
    }
    if (emailInputGroup) emailInputGroup.style.display = 'none';
    
    // Reset loading states
    const chatLoading = document.getElementById('chatLoading');
    if (chatLoading) {
        chatLoading.style.display = 'none';
    }
    
    sessionId = generateSessionId();
    isAnalyzing = false;
    submitBtn.disabled = false;
    sendChatBtn.disabled = false;
    chatInput.disabled = false;
    
    // Reset toggle button
    if (toggleDetailsBtn) {
        toggleDetailsBtn.querySelector('span:first-child').style.display = 'inline';
        toggleDetailsBtn.querySelector('span:last-child').style.display = 'none';
    }
    
    // Scroll to top
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

