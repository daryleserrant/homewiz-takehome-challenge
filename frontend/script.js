const chatForm = document.getElementById("chat-form");
const chatInput = document.getElementById("chat-input");
const chatBox = document.getElementById("chat-box");

const sessionId = Math.random().toString(36).substring(2, 16);

const loadingIndicator = document.getElementById("loading-indicator");

function appendMessage(content, sender) {
  const messageDiv = document.createElement("div");
  messageDiv.classList.add("chat-message", sender);
  messageDiv.textContent = content;
  chatBox.appendChild(messageDiv);
  chatBox.scrollTop = chatBox.scrollHeight;
}

chatForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  const userMessage = chatInput.value.trim();
  if (!userMessage) return;

  appendMessage(userMessage, "user");
  chatInput.value = "";

    // Show loading animation
  chatBox.appendChild(loadingIndicator); 
  loadingIndicator.classList.remove("hidden");

  try {
    const response = await fetch("http://localhost:8000/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        session_id: sessionId,
        message: userMessage
      })
    });

    const data = await response.json();
    appendMessage(data.reply, "bot");
  } catch (err) {
    appendMessage("⚠️ Error: Could not reach the server.", "bot");
    console.error(err);
  } finally {
    // Hide loading animation
    loadingIndicator.classList.add("hidden");
  }
});
