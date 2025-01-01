const chatArea = document.getElementById("quizArea");
let currentTeamIndex = 0; // Keep track of which team is currently active
let teams = [];

// Event listeners
document.getElementById("quizForm").addEventListener("submit", handleSubmitAnswer);
document.getElementById("quizAnswer").addEventListener("keydown", handleAnswerKeydown);

// Initialization
window.onload = function () {
    startQuiz();
    updateTeamStatus();
};

// Core Quiz Functions
async function startQuiz() {
    toggleElement("startQuizButton", false);
    appendMessage("QuizBot", chatBotImg, "left", "Let's begin the quiz! Your first question is coming up.");

    try {
        const response = await fetch(`${quizApiUrl}/start`, { method: 'POST' });
        response.ok ? fetchNextQuestion() : handleErrorResponse(response, "Error starting quiz");
    } catch (error) {
        handleError("An error occurred while starting the quiz.", error);
    }
}

async function fetchNextQuestion() {
    try {
        const response = await fetch(`${quizApiUrl}/next`);
        if (response.ok) {
            const data = await response.json();
            appendMessage("QuizBot", chatBotImg, "left", `${data.team}'s turn: ${data.question}`);
            toggleElement("quizForm", true);
            updateTeamStatus();
        } else {
            declareWinner();
        }
    } catch (error) {
        handleError("An error occurred while fetching the question.", error);
    }
}

async function updateTeamStatus() {
    try {
        const response = await fetch(`/game/${gameId}/status`);
        if (response.ok) {
            const data = await response.json();
            teams = data.teams;
            displayCurrentTeam();
        } else {
            console.error("Failed to fetch game status");
        }
    } catch (error) {
        console.error("Error updating team status:", error);
    }
}

async function declareWinner() {
    try {
        const response = await fetch(`/game/${gameId}/winner`, { method: 'POST' });
        if (response.ok) {
            const data = await response.json();
            appendMessage("QuizBot", chatBotImg, "left", `Quiz is over! The winner is: ${data.winner}`);
            disableControls();
        } else {
            handleErrorResponse(response, "Error declaring winner");
        }
    } catch (error) {
        handleError("An error occurred while declaring the winner.", error);
    }
}

// Event Handlers
function handleSubmitAnswer(event) {
    event.preventDefault();
    const answer = document.getElementById("quizAnswer").value.trim();
    if (!answer) {
        alert("Please provide an answer.");
        return;
    }

    appendMessage("You", studentImg, "right", answer);
    submitAnswer(answer);
}

function handleAnswerKeydown(event) {
    if (event.key === "Enter") {
        event.preventDefault();
        document.getElementById("quizForm").dispatchEvent(new Event("submit"));
    }
}

// Utility Functions
async function submitAnswer(answer) {
    try {
        const response = await fetch(`${quizApiUrl}/answer`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ answer })
        });

        if (response.ok) {
            const data = await response.json();
            appendMessage("QuizBot", chatBotImg, "left", `Result: ${data.result}`);
            resetAnswerField();
            fetchNextQuestion();
            updateTeamStatus();
            currentTeamIndex = (currentTeamIndex + 1) % teams.length;
        } else {
            handleErrorResponse(response, "Error submitting answer");
        }
    } catch (error) {
        handleError("An error occurred while submitting the answer.", error);
    }
}

function displayCurrentTeam() {
    const currentTeam = teams[currentTeamIndex];
    if (currentTeam) {
        document.getElementById("teamName").textContent = `Team: ${currentTeam.name}`;
        document.getElementById("teamScore").textContent = `Score: ${currentTeam.total_score}`;
    }
}

function disableControls() {
    ["quizForm", "startQuizButton", "nextGroupBtn", "startBonusQuiz"].forEach(id =>
        toggleElement(id, false)
    );
    document.getElementById("quizAnswer").disabled = true;
}

function toggleElement(id, isVisible) {
    document.getElementById(id).style.display = isVisible ? "block" : "none";
}

function resetAnswerField() {
    document.getElementById("quizAnswer").value = '';
}

function appendMessage(name, img, side, text) {
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
    msgText.textContent = text;

    msgBubble.appendChild(msgInfo);
    msgBubble.appendChild(msgText);
    msgContainer.appendChild(msgImg);
    msgContainer.appendChild(msgBubble);

    chatArea.appendChild(msgContainer);
    chatArea.scrollTop += 500;
}

function handleError(message, error) {
    console.error(message, error);
    alert(message);
}

async function handleErrorResponse(response, message) {
    const error = await response.json();
    alert(`${message}: ${error.error}`);
}
