// Sample chat data array with "Chat Title" instead of "User"
const chatData = [
    { title: "Project Meeting", message: "Discussion about the upcoming project.", time: "10:30 AM", link: "/frontend/index.html" },
    { title: "Client Call", message: "Meeting at 3 PM to discuss requirements.", time: "Yesterday", link: "/frontend/index.html" },
    { title: "Report Review", message: "Check the updated report.", time: "2 days ago", link: "/frontend/index.html" }
];

// Function to create chat item
function createChatItem(title, message, time, link) {
    const chatItem = document.createElement('a');
    chatItem.href = link;
    chatItem.className = 'list-group-item list-group-item-action d-flex justify-content-between align-items-center';

    const chatContent = document.createElement('div');
    const chatTitle = document.createElement('h5');
    chatTitle.className = 'mb-1';
    chatTitle.textContent = title;

    const chatMessage = document.createElement('p');
    chatMessage.className = 'mb-1 text-muted';
    chatMessage.textContent = message;

    const chatTime = document.createElement('small');
    chatTime.textContent = time;

    chatContent.appendChild(chatTitle);
    chatContent.appendChild(chatMessage);
    chatItem.appendChild(chatContent);
    chatItem.appendChild(chatTime);

    return chatItem;
}

// Render chat items
const chatList = document.getElementById('chat-list');
chatData.forEach(chat => {
    const chatItem = createChatItem(chat.title, chat.message, chat.time, chat.link);
    chatList.appendChild(chatItem);
});
