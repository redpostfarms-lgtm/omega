# -*- coding: utf-8 -*-
# CHECKERS DISPLAY - Visual board representation

def display_checkers_board(board):
    """Display checkers board in ASCII."""
    print("\n  " + " ".join(str(i) for i in range(8)))
    print("  " + "-" * 23)
    
    for row in range(8):
        line = f"{row}|"
        for col in range(8):
            piece = board[row][col]
            if piece == 0:
                symbol = " "
            elif piece == 1:
                symbol = "R"  # Red
            elif piece == 2:
                symbol = "B"  # Black
            elif piece == 3:
                symbol = "K"  # Red King
            elif piece == 4:
                symbol = "Q"  # Black King
            else:
                symbol = "?"
            
            line += symbol + "|"
        print(line)
        print("  " + "-" * 23)
    
    print("\nLegend: R=Red, B=Black, K=Red King, Q=Black King")
    print("Red moves first (bottom rows)\n")

