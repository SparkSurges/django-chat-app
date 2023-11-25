console.log("Sanity check from room.js.");

let chatSocket = null;
let chatLog = document.querySelector("#chatLog");
let chatMessageInput = document.querySelector("#chatMessageInput");
let chatMessageSend = document.querySelector("#chatMessageSend");
let onlineUsersSelector = document.querySelector("#onlineUsersSelector");

const roomName = JSON.parse(document.getElementById('roomName').textContent);

function onlineUsersSelectorAdd(value) {
    if (document.querySelector("option[value='" + value + "']")) return;
    let newOption = document.createElement("option");
    newOption.value = value;
    newOption.innerHTML = value;
    onlineUsersSelector.appendChild(newOption);
}

function onlineUsersSelectorRemove(value) {
    let oldOption = document.querySelector("option[value='" + value + "']");
    if (oldOption !== null) oldOption.remove();
}

function connect() {
    const webSocketServerName = 'ws://' + window.location.host + '/ws/chat/' + roomName + '/';
    chatSocket = new WebSocket(webSocketServerName);

    chatSocket.onopen = (e) => {
        console.log('Successfully connected to the webSocket server: ' + webSocketServerName);
    }

    chatSocket.onclose = (e) => {
        console.log('webSocket connection closed unexpectedly. Trying to reconnect in 2s...');
        setTimeout(() => {
            console.log('Reconnecting...');
            connect();
        }, 2000);
    }

    chatSocket.onmessage = (e) => {
        const data = JSON.parse(e.data);
        console.log(data);

        switch (data.type) {
            case 'chat_message':
                chatLog.value += data.user + ": " + data.message + "\n"; 
                break;
            case "user_list":
                for (let i = 0; i < data.users.length; i++) {
                    onlineUsersSelectorAdd(data.users[i]);
                }
                break;
            case "user_join":
                chatLog.value += data.user + " joined the room.\n";
                onlineUsersSelectorAdd(data.user);
                break;
            case "user_leave":
                chatLog.value += data.user + " left the room.\n";
                onlineUsersSelectorRemove(data.user);
                break;
            default:
                console.error('Unknown message type!');
                break;
        }

        chatLog.scrollTop = chatLog.scrollHeight;
    }

    chatSocket.onerror = (err) => {
        console.log("WebSocket encountered an error: " + err.message);
        console.log("Closing the socket.");
        chatSocket.close();
    }
}

chatMessageInput.focus();

chatMessageInput.onkeyup = function(e) {
    if (e.keyCode === 13) {  // enter key
        chatMessageSend.click();
    }
};

chatMessageSend.onclick = function() {
    if (chatMessageInput.value.length === 0) return;
    chatSocket.send(JSON.stringify({
        'message': chatMessageInput.value,
    }));
    chatMessageInput.value = "";
};

connect();