import os
import sys
import re
import random
import subprocess

README_PATH = "README.md"
REPO = os.environ.get("GITHUB_REPOSITORY", "septiandwica/septiandwica")

# Symbols
EMPTY = "⬜"
X_SYM = "❌"
O_SYM = "⭕"

def get_board(readme_content):
    match = re.search(r"<!-- ttt_board_start -->(.*?)<!-- ttt_board_end -->", readme_content, re.DOTALL)
    if not match:
        return None
    
    board_str = match.group(1).strip()
    board = [[EMPTY for _ in range(3)] for _ in range(3)]
    lines = board_str.split('\n')
    
    # Check if lines have enough rows (header + divider + 3 rows = 5 lines)
    if len(lines) >= 5:
        for r in range(3):
            cols = lines[r+2].split('|')
            if len(cols) >= 4:
                for c in range(3):
                    if X_SYM in cols[c+1]:
                        board[r][c] = X_SYM
                    elif O_SYM in cols[c+1]:
                        board[r][c] = O_SYM
    return board

def render_board(board):
    lines = ["\n| 0 | 1 | 2 |", "|---|---|---|"]
    for r in range(3):
        row_str = "|"
        for c in range(3):
            if board[r][c] == EMPTY:
                url = f"https://github.com/{REPO}/issues/new?title=ttt_move_{r}_{c}&body=Just+submit+the+issue+to+make+a+move!"
                row_str += f" [{EMPTY}]({url}) |"
            else:
                row_str += f" {board[r][c]} |"
        lines.append(row_str)
    return "\n".join(lines) + "\n"

def check_win(board, player):
    for i in range(3):
        if all(board[i][j] == player for j in range(3)): return True
        if all(board[j][i] == player for j in range(3)): return True
    if all(board[i][i] == player for i in range(3)): return True
    if all(board[i][2-i] == player for i in range(3)): return True
    return False

def get_empty(board):
    return [(r, c) for r in range(3) for c in range(3) if board[r][c] == EMPTY]

def main():
    issue_title = os.environ.get("ISSUE_TITLE", "")

    if not issue_title.startswith("ttt_move_"):
        print("Not a tic-tac-toe move.")
        sys.exit(0)
    
    try:
        _, _, r, c = issue_title.split("_")
        r, c = int(r), int(c)
    except:
        print("Invalid move format.")
        sys.exit(0)

    with open(README_PATH, "r", encoding="utf-8") as f:
        content = f.read()
    
    board = get_board(content)
    if not board:
        # Initialize an empty board if not parseable
        board = [[EMPTY]*3 for _ in range(3)]

    if board[r][c] != EMPTY:
        print("Cell already taken.")
    else:
        board[r][c] = X_SYM # User is X
        
        if check_win(board, X_SYM):
            print("User wins!")
            board = [[EMPTY]*3 for _ in range(3)] # Reset
        elif not get_empty(board):
            print("Draw!")
            board = [[EMPTY]*3 for _ in range(3)] # Reset
        else:
            ai_r, ai_c = random.choice(get_empty(board))
            board[ai_r][ai_c] = O_SYM
            if check_win(board, O_SYM):
                print("AI wins!")
                board = [[EMPTY]*3 for _ in range(3)] # Reset
            elif not get_empty(board):
                print("Draw after AI move!")
                board = [[EMPTY]*3 for _ in range(3)] # Reset
    
    new_board_str = render_board(board)
    new_content = re.sub(r"<!-- ttt_board_start -->.*?<!-- ttt_board_end -->", 
                         f"<!-- ttt_board_start -->{new_board_str}<!-- ttt_board_end -->", 
                         content, flags=re.DOTALL)
    
    with open(README_PATH, "w", encoding="utf-8") as f:
        f.write(new_content)
    
    print("Board updated.")

if __name__ == "__main__":
    main()
