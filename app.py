from collections import deque
from flask import Flask, request, jsonify, send_from_directory

app = Flask(__name__)


ROWS, COLS = 6, 6
PLAYER_1 = 1
PLAYER_2 = 2


grid = [[(0, 0) for _ in range(COLS)] for _ in range(ROWS)]
DIRECTIONS = [(-1, 0), (1, 0), (0, -1), (0, 1)]  
player_turn = PLAYER_1
move_count = 0

def bfs_chain_reaction(x, y, player):
    
    queue = deque([(x, y)])
    while queue:
        cx, cy = queue.popleft()
        count, owner = grid[cx][cy]

        
        max_capacity = 4
        if (cx == 0 or cx == ROWS - 1) and (cy == 0 or cy == COLS - 1):
            max_capacity = 2  
        elif cx == 0 or cx == ROWS - 1 or cy == 0 or cy == COLS - 1:
            max_capacity = 3  

        if count >= max_capacity:
            grid[cx][cy] = (0, 0) 
            for dx, dy in DIRECTIONS:
                nx, ny = cx + dx, cy + dy
                if 0 <= nx < ROWS and 0 <= ny < COLS:
                    neighbor_count, neighbor_owner = grid[nx][ny]
                    grid[nx][ny] = (neighbor_count + 1, player)  
                    if grid[nx][ny][0] >= max_capacity:  
                        queue.append((nx, ny))

def check_win():
    """Check if a player has won by capturing all cells."""
    player1_cells = sum(1 for row in grid for count, owner in row if owner == PLAYER_1 and count > 0)
    player2_cells = sum(1 for row in grid for count, owner in row if owner == PLAYER_2 and count > 0)

    if player1_cells == 0:
        return PLAYER_2  
    elif player2_cells == 0:
        return PLAYER_1  
    return None 

@app.route('/')
def index():
    """Serve the main game interface."""
    return send_from_directory('.', 'index.html')

@app.route('/move', methods=['POST'])
def make_move():
    """Handle a move made by a player."""
    global player_turn, move_count
    data = request.json
    x, y = data['x'], data['y']

    count, owner = grid[x][y]
    
    if owner == 0 or owner == player_turn:
        grid[x][y] = (count + 1, player_turn)  
        bfs_chain_reaction(x, y, player_turn) 
        move_count += 1

        winner = None
        if move_count >= 2:  
            winner = check_win()

        player_turn = PLAYER_2 if player_turn == PLAYER_1 else PLAYER_1
        return jsonify({'grid': grid, 'winner': winner, 'next_player': player_turn})

    
    return jsonify({'error': 'Invalid move', 'grid': grid})

@app.route('/reset', methods=['POST'])
def reset_game():
    """Reset the game state to start a new game."""
    global grid, player_turn, move_count
    grid = [[(0, 0) for _ in range(COLS)] for _ in range(ROWS)]
    player_turn = PLAYER_1
    move_count = 0
    return jsonify({'grid': grid})

if __name__ == '__main__':
    app.run(debug=True)
