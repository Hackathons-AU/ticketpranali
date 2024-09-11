document.addEventListener('DOMContentLoaded', () => {
    function changeLanguage(lang) {
        console.log(`Changing language to: ${lang}`); // Debugging line
        const apiUrl = 'https://balascode.github.io/gitjson/db.json';


        fetch(apiUrl)
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then(data => {
                console.log('Data fetched:', data); // Debugging line

                // Access the specific language data directly
                const langData = data.content[lang];
                if (!langData) {
                    throw new Error(`Language data for "${lang}" not found.`);
                }

                // Update the text content of the elements
                document.getElementById('welcome').textContent = langData.welcome || 'Welcome';
                document.getElementById('about_heading').textContent = langData.about_heading || 'About';
                document.getElementById('about_paragraph').textContent = langData.about_paragraph || 'About paragraph';
                document.querySelector('a[href="#home"]').textContent = langData.home;
                document.querySelector('a[href="#aboutus"]').textContent = langData.aboutus;
                document.querySelector('a[href="#faq"]').textContent = langData.faq;
                document.querySelector('a[href="#info"]').textContent = langData.contactus;
                document.getElementById('lan').textContent = langData.lan;

                document.querySelector('.navhead').textContent = langData.head;
                document.getElementById('ap0').textContent = langData.aboutus;
                document.getElementById('ap1').textContent = langData.ap1;
                document.getElementById('ap2').textContent = langData.ap2;
                document.getElementById('ap3').textContent = langData.ap3;
                document.getElementById('ap4').textContent = langData.ap4;
                document.getElementById('ap5').textContent = langData.ap5;
                document.getElementById('ap6').textContent = langData.ap6;
                document.getElementById('ap7').textContent = langData.ap7;
                document.getElementById('ap8').textContent = langData.ap8;

                document.getElementById('fq1').textContent = langData.fq1;
                document.getElementById('fq2').textContent = langData.fq2;
                document.getElementById('fq3').textContent = langData.fq3;
                document.getElementById('fq4').textContent = langData.fq4;
                document.getElementById('fq5').textContent = langData.fq5;
                document.getElementById('fq6').textContent = langData.fq6;
                document.getElementById('fq7').textContent = langData.fq7;
                document.getElementById('fq8').textContent = langData.fq8;
                document.getElementById('fq9').textContent = langData.fq9;
                document.getElementById('fq10').textContent = langData.fq10;
                document.getElementById('fq11').textContent = langData.fq11;
                document.getElementById('fq12').textContent = langData.fq12;
                document.getElementById('fq13').textContent = langData.fq13;
                document.getElementById('fq14').textContent = langData.fq14;
                document.getElementById('fq15').textContent = langData.fq15;
                document.getElementById('fq16').textContent = langData.fq16;
                document.getElementById('fq17').textContent = langData.fq17;
                document.getElementById('fq18').textContent = langData.fq18;
                document.getElementById('fq19').textContent = langData.fq19;
                document.getElementById('fq20').textContent = langData.fq20;
                document.getElementById('fq21').textContent = langData.fq21;
                document.getElementById('fq22').textContent = langData.fq22;
                document.getElementById('fq23').textContent = langData.fq23;
                document.getElementById('fq24').textContent = langData.fq24;
                document.getElementById('fq25').textContent = langData.fq25;
                document.getElementById('fq26').textContent = langData.fq26;
                document.getElementById('fq27').textContent = langData.fq27;
                document.getElementById('fq28').textContent = langData.fq28;
                document.getElementById('fq29').textContent = langData.fq29;
                document.getElementById('fq30').textContent = langData.fq30;
                document.getElementById('fq31').textContent = langData.fq31;

                document.getElementById('ft1').textContent = langData.ft1;
                document.getElementById('ft2').textContent = langData.ft2;
                document.getElementById('ft12').textContent = langData.ft12;
                document.getElementById('ft3').textContent = langData.ft3;
                document.getElementById('ft4').textContent = langData.ft4;
                document.getElementById('ft5').textContent = langData.ft5;
                document.getElementById('ft6').textContent = langData.ft6;
                document.getElementById('ft7').textContent = langData.ft7;
                document.getElementById('ft8').textContent = langData.ft8;
                document.getElementById('ft9').textContent = langData.ft9;
                document.getElementById('ft10').textContent = langData.ft10;
                document.getElementById('ft11').textContent = langData.ft11;


                console.log('Language change successful.'); // Debugging line
            })
            .catch(error => {
                console.error('Error occurred:', error);
            });
    }

    // Ensure the dropdown items exist before adding event listeners
    const dropdownItems = document.querySelectorAll('.dropdown-item');   
    console.log('Dropdown items:', dropdownItems); // Debugging line
    if (dropdownItems.length > 0) {
        dropdownItems.forEach(item => {
            item.addEventListener('click', function (e) {
                e.preventDefault();
                const selectedLang = this.getAttribute('data-lang');
                console.log(`Language selected: ${selectedLang}`); // Debugging line
                changeLanguage(selectedLang);
            });
        });
    } else {
        console.warn('No dropdown items found.');
    }
    

    // Ensure the elements exist before trying to set default language content
    if (document.getElementById('welcome') && document.getElementById('about_heading') && document.getElementById('about_paragraph')) {
        changeLanguage('en'); // Default to English on page load
    } else {
        console.warn('One or more elements not found for setting default language content.');
    }
});



//----------------------------------------------------------------
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
// Function to set the chatbot mode
let currentChatbotMode = 'alternate_chatbot'; // Default mode

// Assume currentChatbotMode is defined globally and set based on server-side data or initial API call

// Function to set the chatbot mode and display a response message
function setChatbotMode(mode) {
    fetch('/set-chatbot-mode', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ mode: mode })
    }).then(response => {
        if (response.ok) {
            // Update button states
            document.getElementById('main-chatbot-button').disabled = (mode === 'main_chatbot');
            document.getElementById('alternate-chatbot-button').disabled = (mode === 'alternate_chatbot');
            currentChatbotMode = mode; // Update the current mode

            // Display response message in the chat box
            displayModeChangeMessage(mode);
            showPopupMessage(mode);
        } else {
            console.error('Failed to switch chatbot mode');
        }
    }).catch(error => {
        console.error('Fetch error:', error);
    });
}

// Function to display a response message
function displayModeChangeMessage(mode) {
    const responseContainer = document.getElementById('chatbot-response');

    // Define messages for each mode
    const messages = {
        'main_chatbot': 'You are now using the Museum Information chatbot. You may ask anything you wish to know about the Booking process or the Museum.',
        'alternate_chatbot': 'You are now using the Ticket Booker chatbot. Please answer any questions asked of you, to book your ticket.'
    };

    // Create a new message element
    const messageElement = document.createElement('div');
    messageElement.className = 'chatbot-message'; // Add a class for styling
    messageElement.textContent = messages[mode] || 'Unknown mode selected.';

    // Append the message to the response container
    responseContainer.innerHTML = ''; // Clear previous messages
    responseContainer.appendChild(messageElement);

    // Optionally scroll to the bottom of the chat box
    document.getElementById('chat-box').scrollTop = document.getElementById('chat-box').scrollHeight;
}

function showPopupMessage(mode) {
    const popup = document.getElementById('popup-message');
    const messages = {
        'main_chatbot': 'Switched to Museum Information chatbot.',
        'alternate_chatbot': 'Switched to Ticket Booker chatbot.'
    };

    // Set popup message
    popup.textContent = messages[mode] || 'Mode change detected.';

    // Show the popup
    popup.classList.add('show');

    // Hide the popup after 3 seconds
    setTimeout(() => {
        popup.classList.remove('show');
    }, 3000); // 3000 milliseconds = 3 seconds
}
// Event listeners for the buttons
document.getElementById('main-chatbot-button').addEventListener('click', () => {
    setChatbotMode('main_chatbot');
});

document.getElementById('alternate-chatbot-button').addEventListener('click', () => {
    setChatbotMode('alternate_chatbot');
});

// Initialize button states and message when the page loads
window.addEventListener('DOMContentLoaded', () => {
    initializeButtonStates();
});

function initializeButtonStates() {
    // Ensure currentChatbotMode is set before using it
    document.getElementById('main-chatbot-button').disabled = (currentChatbotMode === 'main_chatbot');
    document.getElementById('alternate-chatbot-button').disabled = (currentChatbotMode === 'alternate_chatbot');
    
    // Display the initial mode change message
    displayModeChangeMessage(currentChatbotMode);
}


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
    const chatcntrl = document.getElementById('chat-controls');

    if (isMinimized) {
        // Expand the chat container
        chatContainer.classList.remove('minimized');
        chatContainer.classList.remove('minimized-logo');
        document.getElementById('minimize-button').innerHTML = '<i class="fas fa-minus"></i>';
        isMinimized = false;

        // Delay setting the display property to ensure the container is fully expanded
        setTimeout(() => {
            chatcntrl.style.display = "block";
        }, 300); // Adjust delay if necessary
    } else {
        // Minimize the chat container
        chatContainer.classList.add('minimized');
        chatContainer.classList.add('minimized-logo');
        isMinimized = true;
        welcome.textContent = " ";
        map.className = 'container-fluid';
        chatcntrl.style.display = "none";
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
        const chatcntrl = document.getElementById('chat-controls');
        const welcome = document.getElementById('welcome');
        var map = document.getElementById('map');
        chatContainer.classList.remove('minimized');
        chatContainer.classList.remove('minimized-logo');
        document.getElementById('minimize-button').innerHTML = '<i class="fas fa-minus"></i>';
        isMinimized = false;
        welcome.textContent = "Welcome to Ticket Pranali";
        map.classList.replace('container-fluid', 'container');

        // Delay setting the display property to ensure the container is fully expanded
        setTimeout(() => {
            chatcntrl.style.display = "block";
        }, 300); // Adjust delay if necessary
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
    messageContent.innerHTML = `${sender}: ${message}`; // Use innerHTML to include HTML elements

    // Add specific content for step 8
    if (type === 'booking' && message.includes('step-8-content')) {
        messageContent.innerHTML += '<button id="setAmountButton">Set Amount and Go to Form</button>';
    }

    messageDiv.appendChild(logoDiv);
    messageDiv.appendChild(messageContent);

    // Add Back button for booking chatbot messages
    if (type === 'booking') {
        const backButton = document.createElement('button');
        backButton.textContent = 'Back';
        backButton.className = 'back-button';
        backButton.addEventListener('click', () => {
            if (currentChatbotMode === 'alternate_chatbot') {
                sendMessage({ message: 'back' }); // Handle back navigation
            }
        });

        // Store the back button reference
        currentBackButton = backButton;

        // Hide the back button if in main chatbot mode
        if (currentChatbotMode === 'main_chatbot') {
            backButton.style.display = 'none';
        } else {
            backButton.style.display = 'block'; // Ensure it's visible in alternate mode
        }

        messageDiv.appendChild(backButton);
    }

    chatBox.appendChild(messageDiv);
    chatBox.scrollTop = chatBox.scrollHeight;
}

// Event listener for the "Set Amount" button
document.addEventListener('click', function(event) {
    if (event.target && event.target.id === 'setAmountButton') {
        const amountElement = document.getElementById('total-cost');
        const amount = amountElement ? parseFloat(amountElement.textContent.replace('Total cost: $', '')) : 0;
        
        localStorage.setItem('amount', String(amount));
        
        window.location.href = 'pay'; // Redirect to payment form
    }
});
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

