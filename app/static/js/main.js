document.addEventListener('DOMContentLoaded', function() {
    // Theme Switcher
    const themeToggle = document.getElementById('checkbox');
    
    // Check for saved theme preference or respect OS preference
    const prefersDarkScheme = window.matchMedia('(prefers-color-scheme: dark)');
    const storedTheme = localStorage.getItem('theme');
    
    if (storedTheme === 'dark' || (!storedTheme && prefersDarkScheme.matches)) {
        document.body.setAttribute('data-theme', 'dark');
        themeToggle.checked = true;
    }
    
    // Toggle theme when checkbox changes
    themeToggle.addEventListener('change', function() {
        if (this.checked) {
            document.body.setAttribute('data-theme', 'dark');
            localStorage.setItem('theme', 'dark');
        } else {
            document.body.removeAttribute('data-theme');
            localStorage.setItem('theme', 'light');
        }
    });
    
    // DOM Elements
    const userInputForm = document.getElementById('userInputForm');
    const userInput = document.getElementById('userInput');
    const chatContainer = document.getElementById('chatContainer');
    const loadingContainer = document.getElementById('loadingContainer');
    const resultContainer = document.getElementById('resultContainer');
    const downloadTexBtn = document.getElementById('downloadTex');
    const downloadPdfBtn = document.getElementById('downloadPdf');
    const newCvBtn = document.getElementById('newCvBtn');
    const submitBtn = document.getElementById('submitBtn');
    
    let sessionId = null;
    
    // Add user message to chat
    function addUserMessage(text) {
        const messageDiv = document.createElement('div');
        messageDiv.className = 'message user';
        
        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';
        
        const paragraph = document.createElement('p');
        paragraph.textContent = text;
        
        contentDiv.appendChild(paragraph);
        messageDiv.appendChild(contentDiv);
        chatContainer.appendChild(messageDiv);
        
        // Scroll to bottom of chat
        chatContainer.scrollTop = chatContainer.scrollHeight;
    }
    
    // Add system message to chat
    function addSystemMessage(text) {
        const messageDiv = document.createElement('div');
        messageDiv.className = 'message system';
        
        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';
        
        const paragraph = document.createElement('p');
        paragraph.textContent = text;
        
        contentDiv.appendChild(paragraph);
        messageDiv.appendChild(contentDiv);
        chatContainer.appendChild(messageDiv);
        
        // Scroll to bottom of chat
        chatContainer.scrollTop = chatContainer.scrollHeight;
    }
    
    // Show loading state
    function showLoading() {
        loadingContainer.classList.remove('hidden');
        submitBtn.disabled = true;
        userInput.disabled = true;
    }
    
    // Hide loading state
    function hideLoading() {
        loadingContainer.classList.add('hidden');
    }
    
    // Show result container
    function showResult() {
        resultContainer.classList.remove('hidden');
    }
    
    // Handle form submission
    userInputForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const inputText = userInput.value.trim();
        if (!inputText) return;
        
        // Add user message to chat
        addUserMessage(inputText);
        
        // Show loading state
        showLoading();
        
        // Create form data
        const formData = new FormData();
        formData.append('user_input', inputText);
        
        try {
            // Send request to the backend
            const response = await fetch('/generate-cv', {
                method: 'POST',
                body: formData
            });
            
            if (!response.ok) {
                throw new Error('Failed to generate CV');
            }
            
            const data = await response.json();
            sessionId = data.session_id;
            
            // Hide loading and show result
            hideLoading();
            
            // Check if PDF is available
            if (data.pdf_available === false) {
                addSystemMessage('Your CV has been generated successfully! However, PDF generation is not available. You can still download the LaTeX file.');
                downloadPdfBtn.disabled = true;
                downloadPdfBtn.style.opacity = '0.5';
                downloadPdfBtn.title = 'PDF generation is not available';
            } else {
                addSystemMessage('Your CV has been generated successfully!');
            }
            
            showResult();
            
        } catch (error) {
            console.error('Error:', error);
            hideLoading();
            addSystemMessage('Sorry, there was an error generating your CV. Please try again.');
            submitBtn.disabled = false;
            userInput.disabled = false;
        }
    });
    
    // Download buttons event listeners
    downloadTexBtn.addEventListener('click', function() {
        if (sessionId) {
            window.location.href = `/download/tex/${sessionId}`;
        }
    });
    
    downloadPdfBtn.addEventListener('click', function() {
        if (sessionId) {
            window.location.href = `/download/pdf/${sessionId}`;
        }
    });
    
    // New CV button event listener
    newCvBtn.addEventListener('click', function() {
        // Reset the form
        userInputForm.reset();
        
        // Hide result container
        resultContainer.classList.add('hidden');
        
        // Enable input and button
        submitBtn.disabled = false;
        userInput.disabled = false;
        
        // Add system message about starting a new CV
        addSystemMessage('Let\'s create a new CV! What details would you like to include?');
    });
}); 