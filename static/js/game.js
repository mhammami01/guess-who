const chatArea = document.getElementById("chatArea");
const msgerInput = document.getElementById("textInput");
const msgerForm = document.querySelector(".msger-inputarea");
const nextGroupBtn = document.getElementById("nextGroupBtn");
const hintBtn = document.getElementById("hint");
const GuessBtn = document.getElementById("guess");


let stage = 1; // Game stage (1 = character selection, 2 = guessing phase)
let selectedCharacter = null;
let constraints = "";
const typingSpeed = 10; // Speed in milliseconds per character

// Get the full URL
const urlParams = new URLSearchParams(window.location.search);

// Extract the game_id
const gameId = urlParams.get('id');
const rounds = urlParams.get('r');
const team1Name = urlParams.get('t1');
const team2Name = urlParams.get('t2');

// Dynamically update the header with team name and score
document.getElementById("teamName").textContent = `Team1: ${team1Name}`;
//document.getElementById("teamScore").textContent = `Score: ${mockData.teamScore}`;


msgerForm.addEventListener("submit", (event) => {
    event.preventDefault();
    sendMessage();
});

msgerInput.addEventListener("keydown", (event) => {
    if (event.key === "Enter" && !event.shiftKey) {
    event.preventDefault();
    sendMessage();
    }
});

function sendMessage() {
    const userText = msgerInput.value.trim();
    if (!userText) return;

    appendMessage("You", PERSON_IMG, "right", userText, false);
    msgerInput.value = "";

    if (stage === 1) {
    handleStage1(userText);
    } else if (stage === 2) {
    handleStage2(userText);
    }
}

function handleStage1(input) {
    if (!selectedCharacter) {
    selectedCharacter = input;
    appendMessage("ChatBot", BOT_IMG, "left", `You selected "${selectedCharacter}". Now, provide instructions for the chatbot.`, true);
    } else {
    constraints = input;
    appendMessage(
        "ChatBot",
        BOT_IMG,
        "left",
        `Instructions saved! When you're ready, click the button right  and give the computer to Group 2.`,
        true
    );
    stage = 2;
    document.getElementById("teamName").textContent = `Team2: ${team2Name}`;
    nextGroupBtn.style.display = "block";
    }
}

nextGroupBtn.addEventListener("click", () => {
    chatArea.innerHTML = "";
    appendMessage(
    "ChatBot",
    BOT_IMG,
    "left",
    "Group 2, it's your turn! Start asking yes-or-no questions to guess the character.",
    true
    );
    nextGroupBtn.style.display = "none";
    hintBtn.style.display = "block";
    GuessBtn.style.display = "block";
    stage = 2;
});

function handleStage2(input) {
    
    const botResponse = simulateBotResponse(input);
    appendMessage("ChatBot", BOT_IMG, "left", botResponse, true);
}

function simulateBotResponse(question) {
    if (constraints.toLowerCase().includes("avoid") && question.toLowerCase().includes("is it")) {
    return "I'm sorry, I can't answer that directly.";
    }
    return `Good question! Let me think... ${question} might lead to something interesting.`;
}

function appendMessage(name, img, side, text, isBotMessage) {
    const msgContainer = document.createElement("div");
    msgContainer.className = `msg ${side}-msg`;

    const msgImg = document.createElement("div");
    msgImg.className = "msg-img";
    msgImg.style.backgroundImage = `url(${img})`;

    const msgBubble = document.createElement("div");
    msgBubble.className = "msg-bubble";

    const msgInfo = document.createElement("div");
    msgInfo.className = "msg-info";

    const msgInfoName = document.createElement("div");
    msgInfoName.className = "msg-info-name";
    msgInfoName.textContent = name;

    const msgInfoTime = document.createElement("div");
    msgInfoTime.className = "msg-info-time";
    msgInfoTime.textContent = new Date().toLocaleTimeString();

    msgInfo.appendChild(msgInfoName);
    msgInfo.appendChild(msgInfoTime);

    const msgText = document.createElement("div");
    msgText.className = "msg-text";

    msgBubble.appendChild(msgInfo);
    msgBubble.appendChild(msgText);
    msgContainer.appendChild(msgImg);
    msgContainer.appendChild(msgBubble);

    chatArea.appendChild(msgContainer);
    chatArea.scrollTop += 500;

    if (isBotMessage) {
    displayTextWithTypingEffect(msgText, text);
    } else {
    msgText.textContent = text;
    }
}

function displayTextWithTypingEffect(element, text) {
    let i = 0;
    const interval = setInterval(() => {
    element.textContent += text[i];
    i++;
    if (i >= text.length) clearInterval(interval);
    }, typingSpeed);
}