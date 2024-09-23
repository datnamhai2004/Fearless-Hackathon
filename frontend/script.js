document.getElementById('send-btn').addEventListener('click', function() {
    sendMessage();
});

document.getElementById('user_input').addEventListener('keypress', function(e) {
    if (e.key === 'Enter') {
        sendMessage();
    }
});

document.getElementById('send-image-btn').addEventListener('click', function() {
    document.getElementById('image-input').click();
});

document.getElementById('toggle-voice-btn').addEventListener('click', function() {
    toggleRecording();
});

document.getElementById('image-input').addEventListener('change', function(event) {
    sendImage(event.target.files[0]);
});

let mediaRecorder;
let audioChunks = [];
let isRecording = false;

// function sendMessage() {
//     const messageInput = document.getElementById('user_input');
//     const message = messageInput.value.trim();

//     if (message !== '') {
//         const chatBox = document.getElementById('chat-box');
//         const messageElement = document.createElement('div');
//         messageElement.className = 'chat-message user';
//         messageElement.textContent = message;
        
//         chatBox.appendChild(messageElement);
//         chatBox.scrollTop = chatBox.scrollHeight;
        
//         messageInput.value = '';
//         messageInput.focus();
//     }
// }

function sendImage(imageFile) {
    if (imageFile) {
        const chatBox = document.getElementById('chat-box');
        const imageElement = document.createElement('img');
        imageElement.className = 'chat-message user';
        imageElement.src = URL.createObjectURL(imageFile);
        imageElement.style.maxWidth = '30%';
        imageElement.style.maxHeight = '30%';
        imageElement.style.borderRadius = '8px';
        imageElement.style.float = 'right';
        imageElement.style.marginBottom = '10px';

        chatBox.appendChild(imageElement);
        chatBox.scrollTop = chatBox.scrollHeight;
    }
}

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
        document.getElementById('toggle-voice-btn').textContent = '🎤';
    }
}

// function sendVoice(audioBlob) {
//     if (audioBlob) {
//         const chatBox = document.getElementById('chat-box');
//         const audioElement = document.createElement('audio');
//         audioElement.className = 'chat-message user';
//         audioElement.src = URL.createObjectURL(audioBlob);
//         audioElement.controls = true;
//         audioElement.style.display = 'block';
//         audioElement.style.display = 'block';
//         audioElement.style.width = '300px';
//         audioElement.style.marginBottom = '10px';
//         audioElement.style.borderRadius = '10px';


//         chatBox.appendChild(audioElement);
//         chatBox.scrollTop = chatBox.scrollHeight;
//     }
// }
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

        // Display user message
        const userMessageElement = document.createElement('div');
        userMessageElement.className = 'chat-message user';
        userMessageElement.textContent = message;
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



