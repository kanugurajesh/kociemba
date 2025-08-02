import { resetMode } from './modes.js';
import { makeAutoMove } from './action_utils.js'; 
import { getSolution } from './api.js';


// TODO: Refactor to separate getting solution, animating, and handling display
async function handleSolve() {
    const solutionDisplay = document.getElementById("solution-display");
    solutionDisplay.textContent = "";

    let data  = await getSolution();
    let solutionMoves = data.solutionString.split(" "); // using notation from the kociemba solver, which includes double moves like "F2"
    let parsedMoves = data.parsedMoves;
    console.log(data);

    let i = 0;
    async function nextMove() {
        if (parsedMoves.length === 0) return;
        if (i < parsedMoves.length) { // important to check against parsedMoves which can be empty.
            const move = parsedMoves[i];
            if (typeof move === "string") { // single rotation
                solutionDisplay.textContent += " " + solutionMoves[i];
                await makeAutoMove(move, true);
            } else if (Array.isArray(move) && move.length === 2) { // double rotations
                solutionDisplay.textContent += " " + solutionMoves[i];
                await makeAutoMove(move[0], true);
                await makeAutoMove(move[1], true);
            } else {
                console.error("Unexpected move: ", move);
            }
            i++;
            nextMove();
        } else {
            resetMode(); // reset to default (manual) mode when done
        }
    }
    nextMove();
}
window.handleSolve = handleSolve;
