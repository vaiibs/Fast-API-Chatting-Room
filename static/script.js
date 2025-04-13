const ws = new WebSocket(`ws://${location.host}/ws/${username}`);

ws.onmessage = function(event) {
    const data = JSON.parse(event.data);
    if (data.type === "message") {
        const messages = document.getElementById("messages");
        const item = document.createElement("li");
        item.textContent = data.text;
        messages.appendChild(item);
        document.getElementById("typing").textContent = "";
    } else if (data.type === "typing") {
        document.getElementById("typing").textContent = data.text;
    }
};

const input = document.getElementById("messageText");

input.addEventListener("keypress", () => {
    ws.send(JSON.stringify({ type: "typing" }));
});

function sendMessage() {
    if (input.value.trim() !== "") {
        ws.send(JSON.stringify({ type: "message", text: input.value }));
        input.value = "";
    }
}