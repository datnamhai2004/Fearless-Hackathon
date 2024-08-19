document.getElementById('send-btn').addEventListener('click', function() {
    sendMessage();
});

document.getElementById('message-input').addEventListener('keypress', function(e) {
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

function sendMessage() {
    const messageInput = document.getElementById('message-input');
    const message = messageInput.value.trim();

    if (message !== '') {
        const chatBox = document.getElementById('chat-box');
        const messageElement = document.createElement('div');
        messageElement.className = 'chat-message user';
        messageElement.textContent = message;
        
        chatBox.appendChild(messageElement);
        chatBox.scrollTop = chatBox.scrollHeight;
        
        messageInput.value = '';
        messageInput.focus();
    }
}

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
                sendVoice(audioBlob);
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

function sendVoice(audioBlob) {
    if (audioBlob) {
        const chatBox = document.getElementById('chat-box');
        const audioElement = document.createElement('audio');
        audioElement.className = 'chat-message user';
        audioElement.src = URL.createObjectURL(audioBlob);
        audioElement.controls = true;
        audioElement.style.display = 'block';
        audioElement.style.display = 'block';
        audioElement.style.width = '300px';
        audioElement.style.marginBottom = '10px';
        audioElement.style.borderRadius = '10px';


        chatBox.appendChild(audioElement);
        chatBox.scrollTop = chatBox.scrollHeight;
    }
}
