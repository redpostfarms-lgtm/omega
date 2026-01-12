# -*- coding: utf-8 -*-
# ELARA TEACHING MODE
# Quiet coaching during solo play - grandmaster over shoulder

import time
from typing import List, Dict, Optional, Any
from dataclasses import dataclass
from enum import Enum


class TeachingLevel(Enum):
    """Teaching levels."""
    QUIET = "quiet"  # No commentary
    NORMAL = "normal"  # Every 3 turns
    VERBOSE = "verbose"  # Every turn


@dataclass
class TeachingComment:
    """Teaching comment."""
    turn: int
    comment: str
    explanation: Optional[str] = None
    engine_lines: Optional[List[str]] = None
    candidate_moves: Optional[List[str]] = None


class TeachingMode:
    """
    Teaching mode - quiet coaching during solo play.
    
    Features:
    - Every 3 turns, whisper coaching (unless quiet)
    - Explains moves, patterns, tactics
    - Shows engine lines, candidate moves
    - Responds to "why" questions
    - Like grandmaster over shoulder, only when you listen
    """
    
    def __init__(self, level: TeachingLevel = TeachingLevel.NORMAL):
        """Initialize teaching mode."""
        self.level = level
        self.turn_count = 0
        self.comments_given = 0
        self.user_quiet = False
        self.last_comment_turn = 0
        self.move_history: List[Dict[str, Any]] = []
    
    def record_move(self, move: str, player: str, position_eval: Optional[float] = None):
        """Record a move."""
        self.move_history.append({
            'turn': self.turn_count,
            'move': move,
            'player': player,
            'eval': position_eval,
            'timestamp': time.time()
        })
        self.turn_count += 1
    
    def should_comment(self) -> bool:
        """Check if should give commentary."""
        if self.user_quiet or self.level == TeachingLevel.QUIET:
            return False
        
        if self.level == TeachingLevel.VERBOSE:
            return True
        
        # Every 3 turns
        if self.turn_count - self.last_comment_turn >= 3:
            return True
        
        return False
    
    def generate_comment(self) -> Optional[TeachingComment]:
        """Generate teaching comment."""
        if not self.should_comment():
            return None
        
        if len(self.move_history) < 2:
            return None
        
        # Analyze recent moves
        recent_moves = self.move_history[-3:]
        
        # Generate comment based on position
        comment = self._analyze_position(recent_moves)
        
        if comment:
            self.last_comment_turn = self.turn_count
            self.comments_given += 1
            return comment
        
        return None
    
    def _analyze_position(self, moves: List[Dict[str, Any]]) -> Optional[TeachingComment]:
        """Analyze position and generate comment."""
        if len(moves) < 2:
            return None
        
        last_move = moves[-1]
        player = last_move['player']
        move = last_move['move']
        
        # Example comments based on patterns
        if 'N' in move and self.turn_count < 10:
            comment = "Black's knight out early — classic development."
            explanation = "Developing knights before bishops is standard opening theory."
            return TeachingComment(
                turn=self.turn_count,
                comment=comment,
                explanation=explanation,
                candidate_moves=["Nf3", "Nc3", "e4", "d4"]
            )
        
        # Check for hanging pieces
        if self._is_piece_hanging(move):
            comment = "But... e5 is hanging."
            explanation = "This square is undefended and can be captured."
            return TeachingComment(
                turn=self.turn_count,
                comment=comment,
                explanation=explanation,
                candidate_moves=["Bxc4", "Nxe5"]
            )
        
        return None
    
    def _is_piece_hanging(self, move: str) -> bool:
        """Check if piece is hanging (simplified)."""
        # Would analyze actual board position
        # For now, placeholder
        return 'e5' in move.lower()
    
    def explain_move(self, move: str) -> str:
        """Explain a move when user asks 'why'."""
        explanations = {
            'Bxc4': "I play Bxc4 next, you lose a pawn for nothing.",
            'd4': "Try pushing your d-pawn. Opens the bishop. Safe.",
            'e4': "e4 controls the center and opens lines for your pieces."
        }
        
        if move in explanations:
            return explanations[move]
        
        return f"Move {move}: Opens lines, develops piece, improves position."
    
    def whisper(self, comment: TeachingComment):
        """Whisper comment (soft voice)."""
        print(f"[Whisper] {comment.comment}")
        
        if comment.explanation:
            print(f"[Whisper] {comment.explanation}")
        
        if comment.candidate_moves:
            moves_str = ", ".join(comment.candidate_moves)
            print(f"[Whisper] Candidate moves: {moves_str}")
    
    def set_quiet(self, quiet: bool):
        """Set quiet mode."""
        self.user_quiet = quiet
        if quiet:
            print("[Teaching] Quiet mode. No commentary.")
        else:
            print("[Teaching] Teaching mode active.")
    
    def handle_user_response(self, response: str) -> Optional[str]:
        """Handle user response to teaching."""
        response_lower = response.lower()
        
        if 'why' in response_lower or 'explain' in response_lower:
            # Extract move from response or use last move
            if self.move_history:
                last_move = self.move_history[-1]['move']
                return self.explain_move(last_move)
        
        elif 'quiet' in response_lower or 'stop' in response_lower:
            self.set_quiet(True)
            return "Quiet. I'll watch silently."
        
        elif 'continue' in response_lower or 'more' in response_lower:
            self.set_quiet(False)
            return "Continuing commentary."
        
        return None


if __name__ == '__main__':
    teacher = TeachingMode(TeachingLevel.NORMAL)
    
    # Simulate game
    teacher.record_move("e4", "white")
    teacher.record_move("e5", "black")
    teacher.record_move("Nf3", "white")
    
    # Generate comment
    comment = teacher.generate_comment()
    if comment:
        teacher.whisper(comment)
    
    # User asks why
    explanation = teacher.handle_user_response("why")
    if explanation:
        print(f"[Explanation] {explanation}")

