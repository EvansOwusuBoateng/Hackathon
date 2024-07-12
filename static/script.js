const themeToggle = document.querySelector('.theme-toggle');
const body = document.body;

themeToggle.addEventListener('click', () => {
    body.classList.toggle('dark-mode');
});

document.getElementById('file-input').addEventListener('change', function() {
    var file = this.files[0];
    var formData = new FormData();
    formData.append('file', file);

    fetch('/upload', {
        method: 'POST',
        body: formData
    })
    .then(response => {
        if (response.ok) {
            console.log('File uploaded successfully');
            // Optionally reload the page or update the dashboard with the new data
        } else {
            console.error('Error uploading file');
        }
    })
    .catch(error => {
        console.error('Error:', error);
    });
});

document.getElementById('user-input').addEventListener('keyup', function(event) {
    if (event.key === 'Enter') {
        sendMessage();
    }
});

document.getElementById('send-button').addEventListener('click', sendMessage);

function sendMessage() {
    var userInput = document.getElementById('user-input').value;
    if (userInput.trim() !== '') {
        displayMessage(userInput, 'user');
        var formData = new FormData();
        formData.append('message', userInput);

        fetch('/chat', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            displayMessage(data.reply, 'bot');
        })
        .catch(error => {
            console.error('Error:', error);
        });

        document.getElementById('user-input').value = '';
    }
}

function displayMessage(message, sender) {
    var chatMessages = document.getElementById('chat-messages');
    var messageElement = document.createElement('div');
    messageElement.classList.add('chat-message', sender);
    messageElement.textContent = message;
    chatMessages.appendChild(messageElement);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}
