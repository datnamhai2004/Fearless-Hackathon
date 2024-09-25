document.getElementById('send-btn').addEventListener('click', function() {
    sendMessage();
});

document.getElementById('user_input').addEventListener('keypress', function(e) {
    if (e.key === 'Enter') {
        sendMessage();
    }
});

document.getElementById('toggle-voice-btn').addEventListener('click', function() {
    toggleRecording();
});



let mediaRecorder;
let audioChunks = [];
let isRecording = false;


function toggleRecording() {
    if (isRecording) {
        stopRecording();
    } else {
        startRecording();
    }
}

function startRecording() {
    navigator.mediaDevices.getUserMedia({ audio: true })
        .then(stream => {
            mediaRecorder = new MediaRecorder(stream);
            mediaRecorder.ondataavailable = event => {
                audioChunks.push(event.data);
            };
            mediaRecorder.onstop = () => {
                const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
                audioChunks = [];
                sendVoiceMessage(audioBlob);
            };
            mediaRecorder.start();
            isRecording = true;
            document.getElementById('toggle-voice-btn').textContent = '🔴 Recording';
        })
        .catch(error => {
            console.error('Error accessing microphone:', error);
        });
}

function stopRecording() {
    if (mediaRecorder) {
        mediaRecorder.stop();
        isRecording = false;
        document.getElementById('toggle-voice-btn').textContent = 'url';
    }
}

async function sendVoiceMessage(audioBlob) {
    const formData = new FormData();
    formData.append('voice', audioBlob);

    const response = await fetch('/chat-voice', {
        method: 'POST',
        body: formData
    });

    const data = await response.json();

    const chatBox = document.getElementById('chat-box');

    // Hiển thị âm thanh ghi âm từ người dùng
    const userVoiceElement = document.createElement('audio');
    userVoiceElement.src = URL.createObjectURL(audioBlob);
    userVoiceElement.controls = true;
    userVoiceElement.style.marginBottom = '10px';
    chatBox.appendChild(userVoiceElement);
    chatBox.scrollTop = chatBox.scrollHeight;
   

    // Hiển thị phản hồi văn bản từ bot
    const botMessageElement = document.createElement('div');
    botMessageElement.className = 'chat-message bot';
    botMessageElement.textContent = data.response; // Hiển thị phản hồi
    chatBox.appendChild(botMessageElement);
    chatBox.scrollTop = chatBox.scrollHeight;

    // Hiển thị âm thanh phản hồi từ bot (nếu có)
    if (data.audio_url) {
        const botVoiceElement = document.createElement('audio');
        botVoiceElement.src = data.audio_url;
        botVoiceElement.controls = true;
        botVoiceElement.style.marginBottom = '10px';
        chatBox.appendChild(botVoiceElement);
        chatBox.scrollTop = chatBox.scrollHeight;
        botVoiceElement.play();
    }
}



async function loadChatHistory() {
    const response = await fetch('/chats');
    const data = await response.json();
    const chatBox = document.getElementById('chat-box');

    data.chat_history.forEach(entry => {
        const [userMessage, botMessage] = entry.split('|'); // Assuming you save messages as "user|bot"
        
        // Display user message
        const userMessageElement = document.createElement('div');
        userMessageElement.className = 'chat-message user';
        userMessageElement.textContent = userMessage;
        chatBox.appendChild(userMessageElement);

        // Display bot response
        const botMessageElement = document.createElement('div');
        botMessageElement.className = 'chat-message bot';
        botMessageElement.textContent = botMessage;
        chatBox.appendChild(botMessageElement);
    });
}

async function sendMessage() {
    const messageInput = document.getElementById('user_input');
    const message = messageInput.value.trim();

    if (message !== '') {
        const chatBox = document.getElementById('chat-box');

        // Display user message (Ensuring each message is on a new line)
        const userMessageElement = document.createElement('div');
        userMessageElement.className = 'chat-message user';
        userMessageElement.textContent = message;
        userMessageElement.style.display = 'block'; // Ensure each message is block-level (new line)
        chatBox.appendChild(userMessageElement);
        chatBox.scrollTop = chatBox.scrollHeight;

        // Send the message to the server
        const response = await fetch('/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: new URLSearchParams({'user_input': message})
        });

        const data = await response.json();

        // Display bot's text response
        const botMessageElement = document.createElement('div');
        botMessageElement.className = 'chat-message bot';
        botMessageElement.textContent = data.response;
        botMessageElement.style.display = 'block'; // Ensure each bot message is block-level (new line)
        chatBox.appendChild(botMessageElement);
        chatBox.scrollTop = chatBox.scrollHeight;

        // Display bot's audio response if available
        if (data.audio_url) {
            const botVoiceElement = document.createElement('audio');
            botVoiceElement.src = data.audio_url;
            botVoiceElement.controls = true;
            botVoiceElement.style.marginBottom = '10px';
            chatBox.appendChild(botVoiceElement);
            chatBox.scrollTop = chatBox.scrollHeight;

            // Optional: play the audio automatically
            botVoiceElement.play();
        }

        // Clear the input
        messageInput.value = '';
    }
}




