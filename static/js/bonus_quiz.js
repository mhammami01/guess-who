const chatArea = document.getElementById("quizArea");
let currentTeamIndex = 0; // Keep track of which team is currently active
let teams = [];
let isQuizOver = false;


// Initialization
window.onload = function () {
    startQuiz();
    updateTeamStatus();
};

// Core Quiz Functions
function startQuiz() {
    appendMessage("QuizBot", chatBotImg, "left", "Let's begin the quiz! Your first question is coming up.");

    fetch(`${quizApiUrl}/start`, { method: 'POST' })
        .then(response => {
            if (response.ok) {
                return fetchNextQuestion();
            } else {
                return handleErrorResponse(response, "Error starting quiz");
            }
        })
        .catch(error => {
            handleError("An error occurred while starting the quiz.", error);
        });
}

function fetchNextQuestion() {
    if (isQuizOver) {
        console.log("Quiz is over. No more questions will be fetched.");
        return; // Exit early if the quiz is over
    }

    console.log("Starting fetchNextQuestion...");

    updateTeamStatus()
        .then(() => {
            console.log("Team status updated before fetching question");

            return fetch(`${quizApiUrl}/next`);
        })
        .then(response => {
            if (response.ok) {
                return response.json(); // Return the JSON data if the response is okay
            } else if (response.status === 400) {
                console.error("400 BAD REQUEST: No more questions available or quiz is over.");
                isQuizOver = true; // Mark quiz as over
                disableControls(); // Disable buttons immediately
                declareWinner(); // Call declareWinner to handle winner announcement
                return null; // Return `null` to signal no further processing
            } else {
                throw new Error("Error fetching question");
            }
        })
        .then(data => {
            if (data) { // Ensure `data` is not null or undefined
                console.log("Fetched question data:", data);
                appendMessage("QuizBot", chatBotImg, "left", `${data.team}'s turn: ${data.question}`);
                displayAnswerButtons(data.choices);
            }
        })
        .catch(error => {
            handleError("An error occurred while fetching the question.", error);
        });

    console.log("Completed fetchNextQuestion.");
}



// Event Handler for when a button is clicked
async function handleAnswerButtonClick(answer) {
    appendMessage("You", studentImg, "right", answer);
    console.log("This is the answer that will be submitted", answer)
    await submitAnswer(answer); // Submit the answer once the button is clicked
}

// Display the answer buttons dynamically
function displayAnswerButtons(choices) {
    const answerButtonsContainer = document.getElementById("answerButtonsContainer");
    // Clear any existing buttons
    answerButtonsContainer.innerHTML = '';

    choices.forEach(choice => {
        const button = document.createElement("button");
        button.classList.add("answer-button");
        button.textContent = choice;
        // Ensure only the selected choice is passed when the button is clicked
        button.onclick = () => {
            console.log("Selected choice:", choice);  // Log the choice that was clicked
            handleAnswerButtonClick(choice); // Pass only the selected choice
        };
        answerButtonsContainer.appendChild(button);
    });
}


function updateTeamStatus() {
    return fetch(`/game/${gameId}/status`)
        .then(response => {
            if (response.ok) {
                return response.json();
            } else {
                throw new Error("Failed to fetch game status");
            }
        })
        .then(data => {
            teams = data.teams;
            displayCurrentTeam();
        })
        .catch(error => {
            console.error("Error updating team status:", error);
        });
}

async function declareWinner() {
    try {
        const response = await fetch(`/game/${gameId}/winner`, { method: 'POST' });
        if (response.ok) {
            const data = await response.json();
            // Call the popup function and pass the winner's name
            showWinnerPopup(data.winner);
        } else {
            handleErrorResponse(response, "Error declaring winner");
        }
    } catch (error) {
        handleError("An error occurred while declaring the winner.", error);
    }
}

// Utility Functions
async function submitAnswer(answer) {
    console.log("submitting answer ...");

    fetch(`${quizApiUrl}/answer`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ answer })
    })
    .then(response => {
        if (response.ok) {
            return response.json();
        } else {
            return handleErrorResponse(response, "Error submitting answer");
        }
    })
    .then(data => {
        appendMessage("QuizBot", chatBotImg, "left", `Result: ${data.result}`);
        currentTeamIndex = (currentTeamIndex + 1) % teams.length;
        console.log("This happens when I switch the team index", currentTeamIndex);
        // Fetch the next question after updating the team index
        fetchNextQuestion();
    })
    .catch(error => {
        handleError("An error occurred while submitting the answer.", error);
    });
}


function displayCurrentTeam() {
    const currentTeam = teams[currentTeamIndex];
    console.log("This is the current team", currentTeam);
    if (currentTeam) {
        document.getElementById("teamName").textContent = `Team: ${currentTeam.name}`;
        document.getElementById("teamScore").textContent = `Score: ${currentTeam.total_score}`;
    }
}

function disableControls() {
    const answerButtonsContainer = document.getElementById("answerButtonsContainer");
    if (answerButtonsContainer) {
        const buttons = answerButtonsContainer.querySelectorAll("button");
        buttons.forEach(button => {
            button.disabled = true;
        });
    }
    console.log("Answer buttons disabled.");
}

function toggleElement(id, isVisible) {
    document.getElementById(id).style.display = isVisible ? "block" : "none";
}

// function resetAnswerField() {
//     document.getElementById("quizAnswer").value = '';
// }

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

function showWinnerPopup(winnerName) {
    const popup = document.createElement("div");
    popup.id = "winnerPopup";
    popup.style.position = "fixed";
    popup.style.top = "50%";
    popup.style.left = "50%";
    popup.style.transform = "translate(-50%, -50%)";
    popup.style.backgroundColor = "#fff";
    popup.style.padding = "30px";  // Reduced padding for a less wide layout
    popup.style.boxShadow = "0px 15px 25px rgba(0, 0, 0, 0.4)";
    popup.style.zIndex = "1000";
    popup.style.textAlign = "center";
    popup.style.borderRadius = "15px";
    popup.style.maxWidth = "400px";  // Reduced max width for a narrower popup
    popup.style.width = "80%";  // Slightly reduced width for a more compact look

    // Add a header with larger font size and more spacing
    const header = document.createElement("h2");
    header.textContent = "Bonus Quiz Over!";
    header.style.fontSize = "28px";
    header.style.fontWeight = "bold";
    header.style.color = "#4CAF50";
    header.style.marginBottom = "20px";

    const winnerText = document.createElement("p");
    winnerText.innerHTML = `The game winner is: <strong style="color: #8b4513;">${winnerName}</strong>`;
    winnerText.style.fontSize = "20px";
    winnerText.style.color = "#333";
    winnerText.style.marginBottom = "30px";

    // Adding some text padding and margin for better readability
    popup.appendChild(header);
    popup.appendChild(winnerText);

    // Append the popup to the body
    document.body.appendChild(popup);
}
