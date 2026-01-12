# -*- coding: utf-8 -*-
# CHESS AGENT - Plays and teaches chess
# Built on agent_anonymous base with chess knowledge

import os
import sys
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime

# Import base agent
try:
    from agent_anonymous import Agent, AgentConfig
except ImportError:
    # Fallback if not in path
    sys.path.insert(0, str(Path(__file__).parent))
    from agent_anonymous import Agent, AgentConfig


class ChessAgent(Agent):
    """
    Chess-playing and teaching agent.
    
    Features:
    - Plays chess games
    - Analyzes positions
    - Teaches chess strategy
    - Evaluates moves
    - Generates move suggestions
    """
    
    def __init__(self, goal: str = "play and teach chess"):
        """Initialize chess agent."""
        config = AgentConfig(
            skills_dir='./.skills',
            max_retries=3,
            retry_delay=1.0
        )
        super().__init__(goal, config)
        self.board_state = self._init_board()
        self.move_history = []
        self.turn = 'white'  # white starts
        
    def _init_board(self) -> Dict[str, Any]:
        """Initialize chess board."""
        return {
            'a8': 'r', 'b8': 'n', 'c8': 'b', 'd8': 'q', 'e8': 'k', 'f8': 'b', 'g8': 'n', 'h8': 'r',
            'a7': 'p', 'b7': 'p', 'c7': 'p', 'd7': 'p', 'e7': 'p', 'f7': 'p', 'g7': 'p', 'h7': 'p',
            'a6': None, 'b6': None, 'c6': None, 'd6': None, 'e6': None, 'f6': None, 'g6': None, 'h6': None,
            'a5': None, 'b5': None, 'c5': None, 'd5': None, 'e5': None, 'f5': None, 'g5': None, 'h5': None,
            'a4': None, 'b4': None, 'c4': None, 'd4': None, 'e4': None, 'f4': None, 'g4': None, 'h4': None,
            'a3': None, 'b3': None, 'c3': None, 'd3': None, 'e3': None, 'f3': None, 'g3': None, 'h3': None,
            'a2': 'P', 'b2': 'P', 'c2': 'P', 'd2': 'P', 'e2': 'P', 'f2': 'P', 'g2': 'P', 'h2': 'P',
            'a1': 'R', 'b1': 'N', 'c1': 'B', 'd1': 'Q', 'e1': 'K', 'f1': 'B', 'g1': 'N', 'h1': 'R',
            'white_king': 'e1',
            'black_king': 'e8',
            'white_castled': False,
            'black_castled': False,
            'en_passant': None
        }
    
    def run_task(self) -> bool:
        """Main task: play chess or analyze position."""
        try:
            print("\n" + "=" * 60)
            print("CHESS AGENT - Ready to Play")
            print("=" * 60)
            print("\nCommands:")
            print("  - 'play' - Start new game")
            print("  - 'move <from><to>' - Make move (e.g., 'move e2e4')")
            print("  - 'analyze' - Analyze current position")
            print("  - 'suggest' - Suggest best move")
            print("  - 'teach <topic>' - Teach chess concept")
            print("  - 'reset' - Reset board")
            
            self.log_run('chess_agent', 'initialized', True)
            return True
        except Exception as e:
            self.log_run('chess_agent', f'error: {str(e)}', False)
            return False
    
    def make_move(self, move: str) -> Dict[str, Any]:
        """
        Make a chess move.
        
        Args:
            move: Move in algebraic notation (e.g., 'e2e4')
            
        Returns:
            Move result
        """
        try:
            # Parse move
            from_sq = move[:2].lower()
            to_sq = move[2:4].lower()
            
            # Validate squares
            if not self._valid_square(from_sq) or not self._valid_square(to_sq):
                return {'success': False, 'error': 'Invalid square'}
            
            piece = self.board_state.get(from_sq)
            if not piece:
                return {'success': False, 'error': 'No piece on source square'}
            
            # Check if it's the right color's turn
            is_white = piece.isupper()
            if (self.turn == 'white' and not is_white) or (self.turn == 'black' and is_white):
                return {'success': False, 'error': f"Not {self.turn}'s turn"}
            
            # Validate move (simplified - would check legality)
            if self._is_legal_move(from_sq, to_sq, piece):
                # Execute move
                captured = self.board_state.get(to_sq)
                self.board_state[to_sq] = piece
                self.board_state[from_sq] = None
                
                # Update king position
                if piece.upper() == 'K':
                    if is_white:
                        self.board_state['white_king'] = to_sq
                    else:
                        self.board_state['black_king'] = to_sq
                
                # Record move
                move_notation = self._to_algebraic(from_sq, to_sq, piece, captured)
                self.move_history.append(move_notation)
                
                # Switch turn
                self.turn = 'black' if self.turn == 'white' else 'white'
                
                result = {
                    'success': True,
                    'move': move_notation,
                    'captured': captured,
                    'turn': self.turn
                }
                
                self.log_run(f'move: {move}', f'success: {move_notation}', True)
                return result
            else:
                return {'success': False, 'error': 'Illegal move'}
                
        except Exception as e:
            self.log_run(f'move: {move}', f'error: {str(e)}', False)
            return {'success': False, 'error': str(e)}
    
    def _valid_square(self, sq: str) -> bool:
        """Check if square is valid."""
        if len(sq) != 2:
            return False
        return sq[0] in 'abcdefgh' and sq[1] in '12345678'
    
    def _is_legal_move(self, from_sq: str, to_sq: str, piece: str) -> bool:
        """Check if move is legal (simplified)."""
        # Basic validation - would implement full rules
        piece_upper = piece.upper()
        
        # Can't capture own piece
        target = self.board_state.get(to_sq)
        is_white = piece.isupper()
        if target:
            target_white = target.isupper()
            if is_white == target_white:
                return False
        
        # Basic piece movement (simplified)
        if piece_upper == 'P':
            return self._is_legal_pawn_move(from_sq, to_sq, piece, is_white)
        elif piece_upper == 'R':
            return self._is_legal_rook_move(from_sq, to_sq)
        elif piece_upper == 'N':
            return self._is_legal_knight_move(from_sq, to_sq)
        elif piece_upper == 'B':
            return self._is_legal_bishop_move(from_sq, to_sq)
        elif piece_upper == 'Q':
            return self._is_legal_queen_move(from_sq, to_sq)
        elif piece_upper == 'K':
            return self._is_legal_king_move(from_sq, to_sq)
        
        return False
    
    def _is_legal_pawn_move(self, from_sq: str, to_sq: str, piece: str, is_white: bool) -> bool:
        """Check legal pawn move."""
        from_file, from_rank = from_sq[0], int(from_sq[1])
        to_file, to_rank = to_sq[0], int(to_sq[1])
        
        if is_white:
            # Forward move
            if from_file == to_file:
                if to_rank == from_rank + 1:
                    return self.board_state[to_sq] is None
                elif to_rank == from_rank + 2 and from_rank == 2:
                    return self.board_state[to_sq] is None and self.board_state[f"{from_file}{from_rank+1}"] is None
            # Capture
            elif abs(ord(to_file) - ord(from_file)) == 1 and to_rank == from_rank + 1:
                return self.board_state[to_sq] is not None
        else:
            # Black pawn
            if from_file == to_file:
                if to_rank == from_rank - 1:
                    return self.board_state[to_sq] is None
                elif to_rank == from_rank - 2 and from_rank == 7:
                    return self.board_state[to_sq] is None and self.board_state[f"{from_file}{from_rank-1}"] is None
            elif abs(ord(to_file) - ord(from_file)) == 1 and to_rank == from_rank - 1:
                return self.board_state[to_sq] is not None
        
        return False
    
    def _is_legal_rook_move(self, from_sq: str, to_sq: str) -> bool:
        """Check legal rook move."""
        from_file, from_rank = from_sq[0], int(from_sq[1])
        to_file, to_rank = to_sq[0], int(to_sq[1])
        
        # Horizontal or vertical only
        if from_file != to_file and from_rank != to_rank:
            return False
        
        # Check for pieces in between
        return self._path_clear(from_sq, to_sq)
    
    def _is_legal_knight_move(self, from_sq: str, to_sq: str) -> bool:
        """Check legal knight move."""
        from_file, from_rank = ord(from_sq[0]), int(from_sq[1])
        to_file, to_rank = ord(to_sq[0]), int(to_sq[1])
        
        file_diff = abs(to_file - from_file)
        rank_diff = abs(to_rank - from_rank)
        
        return (file_diff == 2 and rank_diff == 1) or (file_diff == 1 and rank_diff == 2)
    
    def _is_legal_bishop_move(self, from_sq: str, to_sq: str) -> bool:
        """Check legal bishop move."""
        from_file, from_rank = from_sq[0], int(from_sq[1])
        to_file, to_rank = to_sq[0], int(to_sq[1])
        
        # Diagonal only
        if abs(ord(to_file) - ord(from_file)) != abs(to_rank - from_rank):
            return False
        
        return self._path_clear(from_sq, to_sq)
    
    def _is_legal_queen_move(self, from_sq: str, to_sq: str) -> bool:
        """Check legal queen move."""
        return self._is_legal_rook_move(from_sq, to_sq) or self._is_legal_bishop_move(from_sq, to_sq)
    
    def _is_legal_king_move(self, from_sq: str, to_sq: str) -> bool:
        """Check legal king move."""
        from_file, from_rank = ord(from_sq[0]), int(from_sq[1])
        to_file, to_rank = ord(to_sq[0]), int(to_sq[1])
        
        file_diff = abs(to_file - from_file)
        rank_diff = abs(to_rank - from_rank)
        
        return file_diff <= 1 and rank_diff <= 1
    
    def _path_clear(self, from_sq: str, to_sq: str) -> bool:
        """Check if path between squares is clear."""
        from_file, from_rank = from_sq[0], int(from_sq[1])
        to_file, to_rank = to_sq[0], int(to_sq[1])
        
        file_step = 0 if from_file == to_file else (1 if ord(to_file) > ord(from_file) else -1)
        rank_step = 0 if from_rank == to_rank else (1 if to_rank > from_rank else -1)
        
        current_file, current_rank = ord(from_file) + file_step, from_rank + rank_step
        
        while current_file != ord(to_file) or current_rank != to_rank:
            sq = f"{chr(current_file)}{current_rank}"
            if self.board_state.get(sq):
                return False
            current_file += file_step
            current_rank += rank_step
        
        return True
    
    def _to_algebraic(self, from_sq: str, to_sq: str, piece: str, captured: Optional[str]) -> str:
        """Convert to algebraic notation."""
        piece_upper = piece.upper()
        if piece_upper == 'P':
            notation = to_sq if not captured else f"{from_sq[0]}x{to_sq}"
        else:
            notation = f"{piece_upper}{to_sq}" if not captured else f"{piece_upper}x{to_sq}"
        return notation
    
    def analyze_position(self) -> Dict[str, Any]:
        """Analyze current board position."""
        analysis = {
            'material': self._count_material(),
            'center_control': self._evaluate_center(),
            'piece_activity': self._evaluate_activity(),
            'turn': self.turn,
            'move_count': len(self.move_history)
        }
        
        self.log_run('analyze', f"position: {len(self.move_history)} moves", True)
        return analysis
    
    def _count_material(self) -> Dict[str, int]:
        """Count material on board."""
        material = {'white': 0, 'black': 0}
        values = {'P': 1, 'N': 3, 'B': 3, 'R': 5, 'Q': 9, 'K': 0}
        
        for sq, piece in self.board_state.items():
            if piece and sq not in ['white_king', 'black_king', 'white_castled', 'black_castled', 'en_passant']:
                value = values.get(piece.upper(), 0)
                if piece.isupper():
                    material['white'] += value
                else:
                    material['black'] += value
        
        return material
    
    def _evaluate_center(self) -> Dict[str, int]:
        """Evaluate center control."""
        center_squares = ['d4', 'd5', 'e4', 'e5']
        control = {'white': 0, 'black': 0}
        
        for sq in center_squares:
            piece = self.board_state.get(sq)
            if piece:
                if piece.isupper():
                    control['white'] += 1
                else:
                    control['black'] += 1
        
        return control
    
    def _evaluate_activity(self) -> str:
        """Evaluate piece activity."""
        # Simplified - would calculate actual piece activity
        return "Normal"
    
    def suggest_move(self) -> Dict[str, Any]:
        """Suggest best move (simplified)."""
        # Would implement minimax or engine integration
        suggestions = []
        
        # Find legal moves for current player
        is_white = self.turn == 'white'
        
        for sq, piece in self.board_state.items():
            if piece and sq not in ['white_king', 'black_king', 'white_castled', 'black_castled', 'en_passant']:
                piece_white = piece.isupper()
                if piece_white == is_white:
                    # Would find legal moves for this piece
                    pass
        
        suggestion = {
            'move': 'e2e4',  # Placeholder
            'evaluation': '+0.3',
            'explanation': 'Good opening move - controls center'
        }
        
        self.log_run('suggest', f"move: {suggestion['move']}", True)
        return suggestion
    
    def teach(self, topic: str) -> str:
        """Teach chess concept."""
        topics = {
            'opening': 'Opening principles: control center (d4/d5/e4/e5), develop pieces (knights before bishops), castle early, don\'t move same piece twice, don\'t bring queen out too early.',
            'tactics': 'Tactical patterns: fork (attack two pieces), pin (piece cannot move), skewer (line attack), discovered attack, double check, deflection, decoy.',
            'endgame': 'Endgame fundamentals: king activity is crucial, opposition (kings facing with odd squares), zugzwang (forced bad move), passed pawns win games.',
            'strategy': 'Positional play: pawn structure matters, piece placement (good vs bad squares), space control, piece coordination, weak squares cannot be defended by pawns.'
        }
        
        explanation = topics.get(topic.lower(), f"Chess concept: {topic}. Would provide detailed explanation here.")
        
        self.log_run(f'teach: {topic}', 'lesson delivered', True)
        return explanation
    
    def reset_board(self):
        """Reset board to initial position."""
        self.board_state = self._init_board()
        self.move_history = []
        self.turn = 'white'
        self.log_run('reset', 'board reset', True)
    
    def print_board(self):
        """Print board in ASCII."""
        print("\n  a b c d e f g h")
        print("  -" * 8)
        
        for rank in range(8, 0, -1):
            line = f"{rank}|"
            for file in 'abcdefgh':
                sq = f"{file}{rank}"
                piece = self.board_state.get(sq, ' ')
                if piece:
                    line += piece + "|"
                else:
                    line += " |"
            print(line)
            print("  -" * 8)
        
        print(f"\nTurn: {self.turn}")
        if self.move_history:
            print(f"Last move: {self.move_history[-1]}")


if __name__ == '__main__':
    agent = ChessAgent("play and teach chess")
    agent.run_task()
    
    print("\n[Example usage:]")
    agent.print_board()
    print("\n[Making move e2e4...]")
    result = agent.make_move('e2e4')
    print(f"Result: {result}")
    agent.print_board()
    
    print("\n[Analyzing position...]")
    analysis = agent.analyze_position()
    print(f"Analysis: {analysis}")
    
    print("\n[Teaching opening principles...]")
    lesson = agent.teach('opening')
    print(f"Lesson: {lesson}")
    
    print("\n[OK] Chess agent ready")

