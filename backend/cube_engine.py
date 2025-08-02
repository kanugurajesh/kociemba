import numpy as np
from fastapi import APIRouter, Request, HTTPException
from kociemba import solve

# --- Core Cube Logic & State Representation ---

# Using integers for faces for internal representation.
# U:0, R:1, F:2, D:3, L:4, B:5
FACE_MAP = {
    0: "U",
    1: "R",
    2: "F",
    3: "D",
    4: "L",
    5: "B",
}
SOLVED_KOCIEMBA_STRING = "".join([f * 9 for f in "URFDLB"])


class Polyhedron:
    """
    Represents the state and operations of a 3x3x3 cube.
    The internal representation uses a NumPy array and integer face identifiers.
    """

    def __init__(self):
        self.matrix = self._get_pristine_state()
        self._initialize_move_dispatcher()

    def _get_pristine_state(self) -> np.array:
        """Generates the matrix for a solved cube."""
        return np.array(
            [
                [[face_id] * 3 for _ in range(3)]
                for face_id in range(6)
            ],
            dtype=int
        )

    def to_kociemba_string(self) -> str:
        """Converts the internal integer matrix to a Kociemba-compatible string."""
        flat_array = self.matrix.flatten()
        return "".join([FACE_MAP[face_id] for face_id in flat_array])

    def reset_to_solved(self):
        """Resets the cube to its initial, solved state."""
        self.matrix = self._get_pristine_state()

    # --- Matrix Transformations (internal helpers) ---

    def _rotate_layer_clockwise(self, face_idx: int):
        self.matrix[face_idx] = np.rot90(self.matrix[face_idx], -1)

    def _rotate_layer_counter_clockwise(self, face_idx: int):
        self.matrix[face_idx] = np.rot90(self.matrix[face_idx], 1)

    # --- Face Turn Implementations (private methods) ---

    def _turn_F_cw(self):
        self._rotate_layer_clockwise(2)
        temp = self.matrix[0][2, :].copy()
        self.matrix[0][2, :] = np.flip(self.matrix[4][:, 2])
        self.matrix[4][:, 2] = self.matrix[3][0, :]
        self.matrix[3][0, :] = np.flip(self.matrix[1][:, 0])
        self.matrix[1][:, 0] = temp

    def _turn_F_ccw(self):
        self._rotate_layer_counter_clockwise(2)
        temp = self.matrix[0][2, :].copy()
        self.matrix[0][2, :] = self.matrix[1][:, 0]
        self.matrix[1][:, 0] = np.flip(self.matrix[3][0, :])
        self.matrix[3][0, :] = self.matrix[4][:, 2]
        self.matrix[4][:, 2] = np.flip(temp)

    def _turn_R_cw(self):
        self._rotate_layer_clockwise(1)
        temp = np.flip(self.matrix[0][:, 2]).copy()
        self.matrix[0][:, 2] = self.matrix[2][:, 2]
        self.matrix[2][:, 2] = self.matrix[3][:, 2]
        self.matrix[3][:, 2] = np.flip(self.matrix[5][:, 0])
        self.matrix[5][:, 0] = temp

    def _turn_R_ccw(self):
        self._rotate_layer_counter_clockwise(1)
        temp = self.matrix[0][:, 2].copy()
        self.matrix[0][:, 2] = self.matrix[5][:, 0]
        self.matrix[5][:, 0] = np.flip(self.matrix[3][:, 2])
        self.matrix[3][:, 2] = self.matrix[2][:, 2]
        self.matrix[2][:, 2] = temp

    def _turn_U_cw(self):
        self._rotate_layer_clockwise(0)
        temp = self.matrix[4][0, :].copy()
        self.matrix[4][0, :] = self.matrix[2][0, :]
        self.matrix[2][0, :] = self.matrix[1][0, :]
        self.matrix[1][0, :] = self.matrix[5][0, :]
        self.matrix[5][0, :] = temp

    def _turn_U_ccw(self):
        self._rotate_layer_counter_clockwise(0)
        temp = self.matrix[4][0, :].copy()
        self.matrix[4][0, :] = self.matrix[5][0, :]
        self.matrix[5][0, :] = self.matrix[1][0, :]
        self.matrix[1][0, :] = self.matrix[2][0, :]
        self.matrix[2][0, :] = temp

    def _turn_L_cw(self):
        self._rotate_layer_clockwise(4)
        temp = self.matrix[0][:, 0].copy()
        self.matrix[0][:, 0] = np.flip(self.matrix[5][:, 2])
        self.matrix[5][:, 2] = np.flip(self.matrix[3][:, 0])
        self.matrix[3][:, 0] = self.matrix[2][:, 0]
        self.matrix[2][:, 0] = temp

    def _turn_L_ccw(self):
        self._rotate_layer_counter_clockwise(4)
        temp = np.flip(self.matrix[0][:, 0]).copy()
        self.matrix[0][:, 0] = self.matrix[2][:, 0]
        self.matrix[2][:, 0] = self.matrix[3][:, 0]
        self.matrix[3][:, 0] = np.flip(self.matrix[5][:, 2])
        self.matrix[5][:, 2] = temp

    def _turn_D_cw(self):
        self._rotate_layer_clockwise(3)
        temp = self.matrix[4][2, :].copy()
        self.matrix[4][2, :] = self.matrix[5][2, :]
        self.matrix[5][2, :] = self.matrix[1][2, :]
        self.matrix[1][2, :] = self.matrix[2][2, :]
        self.matrix[2][2, :] = temp

    def _turn_D_ccw(self):
        self._rotate_layer_counter_clockwise(3)
        temp = self.matrix[4][2, :].copy()
        self.matrix[4][2, :] = self.matrix[2][2, :]
        self.matrix[2][2, :] = self.matrix[1][2, :]
        self.matrix[1][2, :] = self.matrix[5][2, :]
        self.matrix[5][2, :] = temp

    def _turn_B_cw(self):
        self._rotate_layer_clockwise(5)
        temp = np.flip(self.matrix[0][0, :]).copy()
        self.matrix[0][0, :] = self.matrix[1][:, 2]
        self.matrix[1][:, 2] = np.flip(self.matrix[3][2, :])
        self.matrix[3][2, :] = self.matrix[4][:, 0]
        self.matrix[4][:, 0] = temp

    def _turn_B_ccw(self):
        self._rotate_layer_counter_clockwise(5)
        temp = self.matrix[0][0, :].copy()
        self.matrix[0][0, :] = np.flip(self.matrix[4][:, 0])
        self.matrix[4][:, 0] = self.matrix[3][2, :]
        self.matrix[3][2, :] = np.flip(self.matrix[1][:, 2])
        self.matrix[1][:, 2] = temp
        
    def _orient_x_pos(self):
        temp = self.matrix[0].copy()
        self.matrix[0] = self.matrix[2]
        self.matrix[2] = self.matrix[3]
        self.matrix[3] = np.flipud(self.matrix[5])
        self.matrix[5] = np.flipud(temp)
        self._rotate_layer_clockwise(1)
        self._rotate_layer_counter_clockwise(4)

    def _orient_x_neg(self):
        temp = self.matrix[0].copy()
        self.matrix[0] = np.flipud(self.matrix[5])
        self.matrix[5] = np.flipud(self.matrix[3])
        self.matrix[3] = self.matrix[2]
        self.matrix[2] = temp
        self._rotate_layer_counter_clockwise(1)
        self._rotate_layer_clockwise(4)

    # --- Public Move Execution ---

    def _initialize_move_dispatcher(self):
        """Initializes the mapping from move strings to methods."""
        self._move_dispatcher = {
            "F": self._turn_F_cw, "F'": self._turn_F_ccw,
            "R": self._turn_R_cw, "R'": self._turn_R_ccw,
            "U": self._turn_U_cw, "U'": self._turn_U_ccw,
            "L": self._turn_L_cw, "L'": self._turn_L_ccw,
            "D": self._turn_D_cw, "D'": self._turn_D_ccw,
            "B": self._turn_B_cw, "B'": self._turn_B_ccw,
            "M": lambda: [self._turn_R_ccw(), self._turn_L_cw(), self._orient_x_pos()],
            "M'": lambda: [self._turn_R_cw(), self._turn_L_ccw(), self._orient_x_neg()],
        }

    def execute_manipulation(self, move_notation: str):
        """Executes a single move notation (e.g., 'R', 'F'')."""
        if move_notation not in self._move_dispatcher:
            raise ValueError(f"Unknown move notation: {move_notation}")
        self._move_dispatcher[move_notation]()


# --- API Layer ---

# A single, global instance of our cube engine.
polyhedron_engine_instance = Polyhedron()

# Renamed the router
polyhedron_api_router = APIRouter()

def _tokenize_solution_string(solution_str: str) -> list:
    """Parses the Kociemba solver output into a list of moves."""
    tokens = []
    for move in solution_str.split():
        if "2" in move:
            base_move = move[0]
            tokens.append([base_move, base_move])
        else:
            tokens.append(move)
    return tokens

@polyhedron_api_router.post("/move")
async def process_manipulation(request: Request):
    payload = await request.json()
    move = payload.get("move")
    if not move:
        raise HTTPException(status_code=400, detail="Move not specified in payload.")
    
    try:
        polyhedron_engine_instance.execute_manipulation(move)
        return {
            "move": move,
            "cube_string": polyhedron_engine_instance.to_kociemba_string(),
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@polyhedron_api_router.get("/solve")
async def discover_solution_path():
    current_state_str = polyhedron_engine_instance.to_kociemba_string()

    if current_state_str == SOLVED_KOCIEMBA_STRING:
        return {"solutionString": "", "parsedMoves": []}
    
    try:
        solution_path = solve(current_state_str)
        move_sequence = _tokenize_solution_string(solution_path)
        return {"solutionString": solution_path, "parsedMoves": move_sequence}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception:
        raise HTTPException(status_code=500, detail="An internal error occurred during solving.")

@polyhedron_api_router.post("/reset-cube")
async def restore_pristine_state():
    polyhedron_engine_instance.reset_to_solved()
    return {}