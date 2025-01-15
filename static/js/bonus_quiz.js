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

    // Start the quiz
    fetch(`${quizApiUrl}/start`, { method: 'POST' })
        .then(response => {
            if (response.ok) {
                // Once the quiz is started, get the game_id and fetch the quiz status
                return response.json(); // Assuming the response contains the game_id
            } else {
                return handleErrorResponse(response, "Error starting quiz");
            }
        })
        .then(data => {
            return fetch(`${quizApiUrl}/status`);
        })
        .then(response => {
            if (response.ok) {
                return response.json(); // Get the quiz status
            } else {
                return handleErrorResponse(response, "Error fetching quiz status");
            }
        })
        .then(statusData => {
            const quizStatus = statusData.quiz_status;
            console.log("Quiz Status:", quizStatus);

            if (quizStatus === "in_progress") {
                return fetchNextQuestion();
            } else {
                appendMessage("QuizBot", chatBotImg, "left", "The quiz has already ended.");
            }
        })
        .catch(error => {
            handleError("An error occurred while starting the quiz or fetching its status.", error);
        });
}

function fetchNextQuestion() {
    console.log("Starting fetchNextQuestion...");

    // Check quiz status first
    fetch(`${quizApiUrl}/status`)
        .then(response => {
            if (!response.ok) {
                throw new Error("Failed to fetch quiz status.");
            }
            return response.json();
        })
        .then(statusData => {
            const quizStatus = statusData.quiz_status;
            console.log("Quiz Status:", quizStatus);

            if (quizStatus !== "in_progress") {
                console.log("Quiz is not in progress. Ending quiz.");
                disableControls(); // Disable the controls
                declareWinner(); // Announce the winner
                return Promise.reject('Quiz has ended'); // This will skip the remaining promise chain
            }

            // Proceed to update team status and fetch the next question
            return updateTeamStatus(); // This will return a promise
        })
        .then(() => {
            console.log("Team status updated. Fetching next question...");
            return fetch(`${quizApiUrl}/next`); // Fetch the next question
        })
        .then(response => {
            if (!response.ok) {
                throw new Error("Error fetching the next question.");
            }
            return response.json();  // Parse the JSON response
        })
        .then(data => {
            console.log("Fetched question data:", data);
            appendMessage("QuizBot", chatBotImg, "left", `${data.team}'s turn: ${data.question}`);
            displayAnswerButtons(data.choices);
        })
        .catch(error => {
            // If we hit the 'Quiz has ended' rejection, we don't need to display it as an error
            if (error !== 'Quiz has ended') {
                handleError("An error occurred during fetchNextQuestion.", error);
            }
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
    // Create the popup container
    const popup = document.createElement("div");
    popup.id = "winnerPopup";
    popup.classList.add("winner-popup");

    // Create the header
    const header = document.createElement("h2");
    header.textContent = "Bonus Quiz Over!";
    header.classList.add("winner-header");

    // Create the winner text
    const winnerText = document.createElement("p");
    if (winnerName === "It's a tie!") {
        winnerText.innerHTML = `<strong class="tie-text">${winnerName}</strong>`;
    } else {
        winnerText.innerHTML = `The game winner is: <strong class="winner-name">${winnerName}</strong>`;
    }
    winnerText.classList.add("winner-text");

    // Create the trophy icon
    const icon = document.createElement("img");
    icon.src =  "../../static/images/trophy.gif"; // Use the variable from HTML
    icon.alt = "Trophy Icon";
    icon.classList.add("winner-icon")

    // Buttons for actions
    const buttonContainer = document.createElement("div");
    buttonContainer.classList.add("popup-buttons");

    const playAgainButton = document.createElement("button");
    playAgainButton.textContent = "Play Again";
    playAgainButton.classList.add("popup-button");
    playAgainButton.onclick = function() {
        window.location.href = '/game_setup'; // Redirect to the game page
    };

    const backButton = document.createElement("button");
    backButton.textContent = "proceed";
    backButton.classList.add("popup-button");
    backButton.onclick = function() {
        window.location.href = '/final_carousel'; // Redirect to the initial page
    };

    buttonContainer.appendChild(playAgainButton);
    buttonContainer.appendChild(backButton);

    // Append elements to the popup
    popup.appendChild(header);
    popup.appendChild(winnerText);
    popup.appendChild(icon);
    popup.appendChild(buttonContainer);

    // Append the popup to the body
    document.body.appendChild(popup);
}

