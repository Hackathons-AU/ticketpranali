function showInfo(id) {
    // Hide all info boxes
    document.querySelectorAll('.info-box').forEach(box => {
        box.style.display = 'none';
    });
    // Show the selected info box
    const box = document.getElementById(id);
    box.style.display = 'block';
}

function closeInfo(id) {
    var element = document.getElementById(id);
    element.style.display = 'none';
}

let isMinimized = false;

async function sendMessage({ message = null } = {}) {
    const userInput = message || document.getElementById('user-input').value.trim();
    if (userInput === '' && !message) return;

    if (!message) {
        appendMessage('You', userInput, 'user');
        document.getElementById('user-input').value = '';
    }

    const spinner = document.getElementById('loading-spinner');
    spinner.style.display = 'block';

    try {
        const response = await fetch('/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ message: userInput })
        });

        if (!response.ok) {
            console.error('Server response error:', response.statusText);
            return;
        }

        const data = await response.json();
        appendMessage('Chatbot', data.reply || 'No reply', 'booking');
    } catch (error) {
        console.error('Fetch error:', error);
    } finally {
        spinner.style.display = 'none';
    }
}

document.getElementById('user-input').addEventListener('keydown', (event) => {
    if (event.key === 'Enter') {
        event.preventDefault();
        sendMessage();
    }
});

// Add event listener for the "Send" button
document.getElementById('send-button').addEventListener('click', () => {
    sendMessage();
});

isMinimized = false;

document.getElementById('minimize-button').addEventListener('click', (event) => {
    event.stopPropagation(); // Prevents the event from bubbling up and expanding the chat container again

    const chatContainer = document.getElementById('chat-container');
    const welcome = document.getElementById('welcome');
    var map = document.getElementById('map');

    if (isMinimized) {
        // Expand the chat container
        chatContainer.classList.remove('minimized');
        chatContainer.classList.remove('minimized-logo');
        document.getElementById('minimize-button').innerHTML = '<i class="fas fa-minus"></i>';
        isMinimized = false;
    } else {
        // Minimize the chat container
        chatContainer.classList.add('minimized');
        chatContainer.classList.add('minimized-logo');
        isMinimized = true;
        welcome.textContent = " ";
        map.className = 'container-fluid';
        map.scrollIntoView({ 
            behavior: 'smooth', // Smooth scrolling
            block: 'start' // Align to the top of the element (can be 'start', 'center', 'end', 'nearest')
        });
    }
});

document.getElementById('chat-container').addEventListener('click', () => {
    if (isMinimized) {
        // Expand the chat container when clicking the minimized logo
        const chatContainer = document.getElementById('chat-container');
        chatContainer.classList.remove('minimized');
        chatContainer.classList.remove('minimized-logo');
        document.getElementById('minimize-button').innerHTML = '<i class="fas fa-minus"></i>';
        isMinimized = false;
        welcome.textContent = "Welcome to Ticket Pranali";
        map.classList.replace('container-fluid', 'container');
    }
});

let currentBackButton = null; // Keep track of the current back button

function appendMessage(sender, message, type) {
    const chatBox = document.getElementById('chat-box');
    
    // Remove the previous back button if it exists
    if (currentBackButton) {
        currentBackButton.style.display = 'none';
    }
    
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${type}`;
    
    const logoDiv = document.createElement('div');
    logoDiv.className = 'message-logo';

    const profileLogo = document.createElement('img');
    profileLogo.className = 'profile-logo';

    if (type === 'user') {
        profileLogo.src = '../static/images/p1.avif'; // Replace with actual path
        profileLogo.alt = 'User Logo';
    } else {
        profileLogo.src = '../static/images/c1.jpg'; // Replace with actual path
        profileLogo.alt = 'Chatbot Logo';
    }

    logoDiv.appendChild(profileLogo);

    const messageContent = document.createElement('div');
    messageContent.className = 'message-content';
    messageContent.textContent = `${sender}: ${message}`;

    messageDiv.appendChild(logoDiv);
    messageDiv.appendChild(messageContent);

    // Add Back button for booking chatbot messages
    if (type === 'booking') {
        const backButton = document.createElement('button');
        backButton.textContent = 'Back';
        backButton.className = 'back-button';
        backButton.addEventListener('click', () => {
            sendMessage({ message: 'back' }); // Handle back navigation
        });
        
        // Store the back button reference
        currentBackButton = backButton;

        messageDiv.appendChild(backButton);
    }

    chatBox.appendChild(messageDiv);
    chatBox.scrollTop = chatBox.scrollHeight;
}

// Ensure only one back button is visible
function clearBackButton() {
    if (currentBackButton) {
        currentBackButton.style.display = 'none';
    }
}

document.getElementById('chat-container').addEventListener('click', () => {
    if (isMinimized) {
        const chatContainer = document.getElementById('chat-container');
        chatContainer.classList.remove('minimized');
        chatContainer.classList.remove('minimized-logo');
        document.getElementById('minimize-button').innerHTML = '<i class="fas fa-minus"></i>';
        isMinimized = false;
    }
});

