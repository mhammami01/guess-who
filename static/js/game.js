const chatArea = document.getElementById("chatArea");
const msgerInput = document.getElementById("textInput");
const msgerForm = document.querySelector(".msger-inputarea");
const nextGroupBtn = document.getElementById("nextGroupBtn");
const buttonsForm = document.getElementById("guessers-buttons");
const hintBtn = document.getElementById("hint");
const guessBtn = document.getElementById("guess");	


let stage = 1; // Game stage (1 = character selection, 2 = guessing phase)
let swap = 0;
let selectedCharacter = null;
let constraints = "";
const typingSpeed = 10; // Speed in milliseconds per character

// Get the full URL
const urlParams = new URLSearchParams(window.location.search);

// Extract the game_id
let  gameId = urlParams.get('id');
let rounds = urlParams.get('r');
//const team1Name = urlParams.get('t1');
//const team2Name = urlParams.get('t2');

// Game State Variables (to be populated after fetching game status)
//let rounds = 0;
let team1Name = '';
let team2Name = '';
let team1Score = 0;
let team2Score = 0;
let current_round = 1;
init = true;

// Initialize the game by fetching the game status
update_status();




async function update_status() {
    
    try {
        const gameStatus = await getGameStatus(gameId);
        if (gameStatus) {
            team1Name = gameStatus.teams[0].name;
            team2Name = gameStatus.teams[1].name;
            team1Score = gameStatus.teams[0].round_score;
            team2Score = gameStatus.teams[1].round_score;

            // Update UI with team names and scores
            if (stage === 1) {
                document.getElementById("teamName").textContent = `Team: ${team1Name}`;
                document.getElementById("teamScore").textContent = `Score: ${team1Score}`;
            } else {
                document.getElementById("teamName").textContent = `Team: ${team2Name}`;
                document.getElementById("teamScore").textContent = `Score: ${team2Score}`;
            }
            document.getElementById("Round").textContent = `Current Round: ${current_round}/${rounds}`;
            if (init) {
                appendMessage("ChatBot", BOT_IMG, "left", `Welcome ${team1Name}!, please choose a famous Character and add instructions in the next prompt to prevent easy guessing:<br><strong>Example Characters:</strong> Napoleon Bonaparte, Albert Einstein, Cleopatra, Leonardo da Vinci`, false);
                init = false;
            }    
        } else {
            console.error("Failed to get game status.");
        }
    } catch (error) {
        console.error("Error getting game status", error);
    }
}




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

guessBtn.addEventListener("click", (event) => {
    event.preventDefault();
    setupGuessingButton();
});	

hintBtn.addEventListener("click", (event) => {    
    event.preventDefault();
    useHint(gameId);
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
        startRound(gameId);
        appendMessage("ChatBot", BOT_IMG, "left", `You selected "${selectedCharacter}". Now, provide instructions for the chatbot.`, true);
    } else {
        constraints = input;
        addPersonToRound(gameId, selectedCharacter, constraints);
    }

}

nextGroupBtn.addEventListener("click", () => {
    chatArea.innerHTML = "";
    appendMessage(
    "ChatBot",
    BOT_IMG,
    "left",
    "Guessing group, it's your turn! Start asking questions to guess the character.",
    true
    );
    nextGroupBtn.style.display = "none";
    buttonsForm.style.display = "block";
    stage = 2;
});

function handleStage2(input) {
    const botResponse = simulateBotResponse(input);
    appendMessage("ChatBot", BOT_IMG, "left", botResponse, true);
    //checkGameEnd(gameId);
}

function simulateBotResponse(question) {
    askQuestion(gameId, question);

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
        if (text.includes("<")) {
            //msgText.textContent = "test";
            msgText.innerHTML = text;
        } else {
        msgText.textContent = text;
        }
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

async function checkGameEnd() {
    try {
        const response = await fetch(`/game/${gameId}/status`);
        if (response.ok) {
            const gameStatus = await response.json();
            //TODO: check whether this works in the context of the game
            const isGameFinished = gameStatus.game_status === "finished";
            // const isGameFinished = true;

            if (isGameFinished) {
                showGameOverPopup();
            }
        } else {
            console.error("Failed to fetch game status.");
        }
    } catch (error) {
        console.error("Error checking game status:", error);
    }
}


async function getGameStatus(gameId) {
    try {
        const response = await fetch(`/game/${gameId}/status`);

        if (response.ok) {
            const gameStatus = await response.json();
            console.log("Game Status:", gameStatus);
            return gameStatus;
        } else {
            // Handle HTTP errors
            console.error("Failed to fetch game status:", await response.text());
            return null;
        }
    } catch (error) {
        // Handle network or other errors
        console.error("Error fetching game status:", error);
        return null;
    }
}

async function startRound(gameId) {
    try {
        const response = await fetch(`/game/${gameId}/round/start`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            }
        });

        if (response.ok) {
            const data = await response.json();
            console.log("Round started:", data);
        } else {
            console.error("Failed to start round:", await response.text());
        }
    } catch (error) {
        console.error("Error starting round:", error);
    }
}



async function addPersonToRound(gameId, personName, personDescription) {
    try {
        const response = await fetch(`/game/${gameId}/round/add_person`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                person_name: personName,
                person_description: personDescription
            }),
        });

        if (response.ok) {
            const data = await response.json();
            console.log("Person added:", data);
            appendMessage(
                "ChatBot",
                BOT_IMG,
                "left",
                `Instructions saved! When you're ready, click the button right  and give the computer to other team `,
                true
            );
            stage = 2;
            update_status();
            nextGroupBtn.style.display = "block";
            buttonsForm.style.display = "block";
        } else {
            appendMessage("ChatBot", BOT_IMG, "left", "Failed to add person. Please try again. choose a new person", true);
            selectedCharacter = null;
        }
    } catch (error) {
        console.error("Error adding person:", error);
    }
}


async function askQuestion(gameId, question) {
    try {
        const response = await fetch(`/game/${gameId}/round/ask`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ question }),
        });

        if (response.ok) {
            const data = await response.json();
            console.log("Question asked:", data);
            update_status();
            appendMessage("ChatBot", BOT_IMG, "left", `${data.response}`, true);
            if (data.identity_revealed) {
                appendMessage("ChatBot", BOT_IMG, "left", "Identity revealed!", true);
                endRound(gameId);
                //showRoundOverPopup();
                //showGameOverPopup();
            }
        } else {
            console.error("Failed to ask question:", await response.text());
        }
    } catch (error) {
        console.error("Error asking question:", error);
    }
}


async function makeGuess(gameId, guess) {
    try {
        const response = await fetch(`/game/${gameId}/round/make_guess`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ guess }),
        });

        if (response.ok) {
            const data = await response.json();
            console.log("Guess result:", data);
            appendMessage("ChatBot", BOT_IMG, "left", data.message, true);
            update_status();
            if (data.identity_revealed) {
                //appendMessage("ChatBot", BOT_IMG, "left", "Correct identity guessed!", true);
                endRound(gameId);
            }
        } else {
            console.error("Failed to make guess:", await response.text());
        }
    } catch (error) {
        console.error("Error making guess:", error);
    }
}
async function useHint(gameId) {
    try {
        const response = await fetch(`/game/${gameId}/round/use_hint`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
        });

        if (response.ok) {
            const data = await response.json();
            console.log("Hint used:", data);
            update_status();
            appendMessage("ChatBot", BOT_IMG, "left", `Hint: ${data.hint}`, true);
        } else {
            console.error("Failed to use hint:", await response.text());
        }
    } catch (error) {
        console.error("Error using hint:", error);
    }
}
async function endRound(gameId) {
    try {
        const response = await fetch(`/game/${gameId}/round/end`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
        });

        if (response.ok) {
            const data = await response.json();
            console.log("Round ended", data);
            if (current_round < rounds) {
                team1_summary = data.round_summary.team1.name + ": you have reached in this round " + data.round_summary.team1.round_score + " points";
                team2_summary = data.round_summary.team2.name + ": you have reached in this round " + data.round_summary.team2.round_score  + " points";
                current_round += 1;
                showRoundOverPopup(team1_summary, team2_summary);
            } else {
                const gameStatus = await getGameStatus(gameId);
                team1_summary =  gameStatus.teams[0].name + ": you have reached in this game " + gameStatus.teams[0].total_score + " points";
                team2_summary =  gameStatus.teams[1].name + ": you have reached in this game " + gameStatus.teams[1].total_score + " points";
                if (gameStatus.teams[0].total_score > gameStatus.teams[1].total_score) {
                    winner_text = gameStatus.teams[0].name + " is the winner!";
                } else if (gameStatus.teams[0].total_score < gameStatus.teams[1].total_score) {
                    winner_text = gameStatus.teams[1].name + " is the winner!";
                } else {
                    winner_text = "It's a draw!";
                }


                showGameOverPopup(team1_summary, team2_summary, winner_text);
            }   
            //appendMessage("ChatBot", BOT_IMG, "left", `Round Summary: ${data.round_summary}`, true);
        } else {
            console.error("Failed to end round:", await response.text());
        }
    } catch (error) {
        console.error("Error ending round:", error);
    }
}



function setupGuessingButton() {
    // Create the popup window for the guess input
    const popup = document.createElement("div");
    popup.id = "guessPopup";
    popup.style.position = "fixed";
    popup.style.top = "50%";
    popup.style.left = "50%";
    popup.style.transform = "translate(-50%, -50%)";
    popup.style.backgroundColor = "#fff";
    popup.style.padding = "20px";
    popup.style.boxShadow = "0px 0px 10px rgba(0, 0, 0, 0.5)";
    popup.style.zIndex = "1000";
    popup.style.textAlign = "center";

    // Create the content of the popup
    const popupContent = `
        <h2>Make a Guess</h2>
        <br>
        <input type="text" id="guessInput" placeholder="Enter your guess" style="width: 80%; padding: 10px; margin-bottom: 10px;">
        <br>
        <button id="submitGuessBtn" style="padding: 10px 20px; background: rgb(0, 196, 65); color: white; border: none; border-radius: 5px; cursor: pointer;">Submit</button>
        <button id="closeGuessPopupBtn" style="padding: 10px 20px; background: rgb(255, 65, 54); color: white; border: none; border-radius: 5px; cursor: pointer; margin-left: 10px;">Close</button>
    `;
    popup.innerHTML = popupContent;
    document.body.appendChild(popup);

    // Add event listener to the submit button
    document.getElementById("submitGuessBtn").addEventListener("click", (event) => {
        event.preventDefault(); // Prevent form submission and page refresh
        const guessInput = document.getElementById("guessInput").value.trim();
        if (guessInput) {
            console.log("Submitting guess:", guessInput);
            makeGuess(gameId, guessInput); // Call the already implemented makeGuess function
            document.body.removeChild(popup); // Close the popup after submission
        } else {
            alert("Please enter a guess.");
        }
    });

    // Add event listener to the close button
    document.getElementById("closeGuessPopupBtn").addEventListener("click", () => {
        document.body.removeChild(popup); // Close the popup
    });
}





function showRoundOverPopup(team1_summary, team2_summary) {
    const popup = document.createElement("div");
    popup.id = "roundOverPopup";
    popup.style.position = "fixed";
    popup.style.top = "50%";
    popup.style.left = "50%";
    popup.style.transform = "translate(-50%, -50%)";
    popup.style.backgroundColor = "#fff";
    popup.style.padding = "20px";
    popup.style.boxShadow = "0px 0px 10px rgba(0, 0, 0, 0.5)";
    popup.style.zIndex = "1000";
    popup.style.textAlign = "center";


    const popupContent = `
        <h2>Round Over!</h2>
        <p>Round Summary:</p>
        <p>Team1: ${team1_summary}</p>
        <br>
        <p>Team2: ${team2_summary}</p>
        <br>
        <p>Now both teams will be switched up</p>
        <button id="proceedToNextRound" style="padding: 10px 20px; background: rgb(0, 196, 65); color: white; border: none; border-radius: 5px; cursor: pointer;">Proceed</button>
    `;
    popup.innerHTML = popupContent;
    document.body.appendChild(popup);

    document.getElementById("proceedToNextRound").addEventListener("click", () => {
        document.body.removeChild(popup);
        proceedToNextRound();
    });

}

function proceedToNextRound() {
    // Reset UI elements for the new round
    chatArea.innerHTML = "";
    appendMessage("ChatBot", BOT_IMG, "left", `Welcome ${team1Name}! Please choose a famous character and provide instructions to prevent easy guessing.`, false); 

    // Reset stage to 1 for character selection
    stage = 1;
    selectedCharacter = null;
    constraints = "";
    update_status();

    // Hide buttons not needed for character selection
    nextGroupBtn.style.display = "none";
    buttonsForm.style.display = "none";
}

function showGameOverPopup(Team1_summary, Team2_summary, winner_text) {
    const popup = document.createElement("div");
    popup.id = "gameOverPopup";
    popup.style.position = "fixed";
    popup.style.top = "50%";
    popup.style.left = "50%";
    popup.style.transform = "translate(-50%, -50%)";
    popup.style.backgroundColor = "#fff";
    popup.style.padding = "20px";
    popup.style.boxShadow = "0px 0px 10px rgba(0, 0, 0, 0.5)";
    popup.style.zIndex = "1000";
    popup.style.textAlign = "center";

    const popupContent = `
        <h2>Game Over!</h2>
        <p>Game Summary:</p>
        <p>${Team1_summary}</p>
        <br>
        <p>${Team2_summary}</p>
        <br>
        <p>${winner_text}</p>
        <br>
        <p>Now you can test your knowledge about LLMs and gain some bonus points. Let's proceed to the bonus quiz!</p>
        <button id="proceedToQuizBtn" style="padding: 10px 20px; background: rgb(0, 196, 65); color: white; border: none; border-radius: 5px; cursor: pointer;">Proceed</button>
    `;
    popup.innerHTML = popupContent;
    document.body.appendChild(popup);

    document.getElementById("proceedToQuizBtn").addEventListener("click", () => {
        window.location.href = `/game/${gameId}/bonus-quiz`;
    });
}