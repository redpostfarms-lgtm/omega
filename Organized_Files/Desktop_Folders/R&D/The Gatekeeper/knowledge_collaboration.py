# -*- coding: utf-8 -*-
# PROPRIETARY SOFTWARE - RED POST FARMS, LLC
# Copyright (c) 2025-2026 Red Post Farms, LLC
# All Rights Reserved

"""
Knowledge Collaboration
Collaboration features for knowledge management
"""

import json
import time
from pathlib import Path
from typing import Dict, List, Optional, Any

BRAIN = Path(r'D:\RPF_BRAIN')
ARCHIVED = BRAIN / 'Archived'
COLLAB_DIR = ARCHIVED / 'knowledge_collaboration'
COLLAB_DIR.mkdir(parents=True, exist_ok=True)

class KnowledgeCollaboration:
    """Collaboration features for knowledge management."""
    
    def __init__(self):
        self.shared_notes = {}
        self.comments = {}
        self.change_history = {}
        self.data_file = COLLAB_DIR / 'collaboration_data.json'
        self._load_data()
    
    def _load_data(self):
        """Load collaboration data."""
        if self.data_file.exists():
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.shared_notes = data.get('shared_notes', {})
                    self.comments = data.get('comments', {})
                    self.change_history = data.get('change_history', {})
            except:
                self.shared_notes = {}
                self.comments = {}
                self.change_history = {}
        else:
            self.shared_notes = {}
            self.comments = {}
            self.change_history = {}
    
    def _save_data(self):
        """Save collaboration data."""
        data = {
            'shared_notes': self.shared_notes,
            'comments': self.comments,
            'change_history': self.change_history,
            'updated_at': time.time()
        }
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def share_note(self, note_id: str, user_id: str, permissions: List[str] = ['read']) -> bool:
        """
        Share a note with a user.
        
        Args:
            note_id: Note identifier
            user_id: User identifier
            permissions: List of permissions ('read', 'write', 'comment')
        
        Returns:
            True if shared successfully
        """
        if note_id not in self.shared_notes:
            self.shared_notes[note_id] = {}
        
        self.shared_notes[note_id][user_id] = {
            'permissions': permissions,
            'shared_at': time.time()
        }
        
        self._save_data()
        return True
    
    def add_comment(self, note_id: str, user_id: str, comment: str) -> Dict[str, Any]:
        """
        Add a comment to a note.
        
        Args:
            note_id: Note identifier
            user_id: User identifier
            comment: Comment text
        
        Returns:
            Comment object
        """
        if note_id not in self.comments:
            self.comments[note_id] = []
        
        comment_obj = {
            'id': f"comment_{int(time.time() * 1000)}",
            'note_id': note_id,
            'user_id': user_id,
            'comment': comment,
            'created_at': time.time()
        }
        
        self.comments[note_id].append(comment_obj)
        self._save_data()
        
        return comment_obj
    
    def track_changes(self, note_id: str, user_id: str, change_type: str, change_data: Dict[str, Any]):
        """
        Track changes to a note.
        
        Args:
            note_id: Note identifier
            user_id: User identifier
            change_type: Type of change ('created', 'updated', 'deleted')
            change_data: Change data
        """
        if note_id not in self.change_history:
            self.change_history[note_id] = []
        
        change_record = {
            'id': f"change_{int(time.time() * 1000)}",
            'note_id': note_id,
            'user_id': user_id,
            'change_type': change_type,
            'change_data': change_data,
            'timestamp': time.time()
        }
        
        self.change_history[note_id].append(change_record)
        
        # Keep last 1000 changes per note
        if len(self.change_history[note_id]) > 1000:
            self.change_history[note_id] = self.change_history[note_id][-1000:]
        
        self._save_data()
    
    def get_shared_notes(self, user_id: str) -> List[str]:
        """Get notes shared with a user."""
        shared = []
        for note_id, users in self.shared_notes.items():
            if user_id in users:
                shared.append(note_id)
        return shared
    
    def get_comments(self, note_id: str) -> List[Dict[str, Any]]:
        """Get comments for a note."""
        return self.comments.get(note_id, [])
    
    def get_change_history(self, note_id: str) -> List[Dict[str, Any]]:
        """Get change history for a note."""
        return self.change_history.get(note_id, [])
    
    def get_collaboration_statistics(self) -> Dict[str, Any]:
        """Get collaboration statistics."""
        return {
            'total_shared_notes': len(self.shared_notes),
            'total_comments': sum(len(comments) for comments in self.comments.values()),
            'total_changes': sum(len(changes) for changes in self.change_history.values()),
            'most_shared_notes': sorted(
                [(note_id, len(users)) for note_id, users in self.shared_notes.items()],
                key=lambda x: x[1],
                reverse=True
            )[:10]
        }

