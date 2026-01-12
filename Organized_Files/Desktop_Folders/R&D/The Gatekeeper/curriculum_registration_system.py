#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# PROPRIETARY SOFTWARE - RED POST FARMS, LLC
# Copyright (c) 2025-2026 Red Post Farms, LLC
# All Rights Reserved
#
# CURRICULUM & REGISTRATION SYSTEM
# Learning path management, course enrollment, progress tracking

import json
import sys
import io
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

BRAIN = Path(r'D:\RPF_BRAIN')
GATE = BRAIN / 'The Gatekeeper'
CURRICULUM_DIR = BRAIN / 'Archived' / 'curriculum'
CURRICULUM_DIR.mkdir(parents=True, exist_ok=True)

class CurriculumRegistrationSystem:
    """Curriculum and registration management system."""
    
    def __init__(self):
        """Initialize curriculum system."""
        self.curriculum_file = CURRICULUM_DIR / 'curriculum.json'
        self.registrations_file = CURRICULUM_DIR / 'registrations.json'
        self.progress_file = CURRICULUM_DIR / 'progress.json'
        
        self.curriculum = self.load_curriculum()
        self.registrations = self.load_registrations()
        self.progress = self.load_progress()
    
    def load_curriculum(self) -> Dict:
        """Load curriculum catalog."""
        if self.curriculum_file.exists():
            try:
                with open(self.curriculum_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass
        
        # Default curriculum structure
        return {
            'courses': [
                {
                    'id': 'gatekeeper_basics',
                    'name': 'Gatekeeper Basics',
                    'description': 'Introduction to Gatekeeper system',
                    'duration': '4 hours',
                    'prerequisites': [],
                    'modules': ['Voice Commands', 'Agent Systems', 'Knowledge Base']
                },
                {
                    'id': 'farm_automation',
                    'name': 'Farm Automation',
                    'description': 'Farm automation systems',
                    'duration': '8 hours',
                    'prerequisites': ['gatekeeper_basics'],
                    'modules': ['IoT Sensors', 'Precision Ag', 'Irrigation']
                },
                {
                    'id': 'medical_core',
                    'name': 'Medical Core Operations',
                    'description': 'Medical emergency detection',
                    'duration': '6 hours',
                    'prerequisites': [],
                    'modules': ['Fall Detection', 'Vitals Monitoring', 'ER Protocols']
                },
                {
                    'id': 'hr_management',
                    'name': 'HR Management',
                    'description': 'HR automation with Harriet',
                    'duration': '4 hours',
                    'prerequisites': [],
                    'modules': ['New Hires', 'Payroll', 'Compliance']
                }
            ],
            'learning_paths': [
                {
                    'id': 'complete_farm_ops',
                    'name': 'Complete Farm Operations',
                    'courses': ['gatekeeper_basics', 'farm_automation', 'medical_core']
                }
            ]
        }
    
    def load_registrations(self) -> Dict:
        """Load registrations."""
        if self.registrations_file.exists():
            try:
                with open(self.registrations_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass
        return {'students': []}
    
    def load_progress(self) -> Dict:
        """Load progress tracking."""
        if self.progress_file.exists():
            try:
                with open(self.progress_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass
        return {'progress': []}
    
    def confirm_curriculum(self, course_id: str) -> Dict:
        """Confirm curriculum for a course."""
        course = next((c for c in self.curriculum['courses'] if c['id'] == course_id), None)
        if not course:
            return {'error': f'Course {course_id} not found'}
        
        confirmation = {
            'course_id': course_id,
            'course_name': course['name'],
            'confirmed_date': datetime.now().isoformat(),
            'modules': course['modules'],
            'duration': course['duration'],
            'prerequisites': course['prerequisites'],
            'status': 'confirmed'
        }
        
        return confirmation
    
    def register_for_course(self, student_name: str, course_id: str) -> Dict:
        """Register student for course."""
        course = next((c for c in self.curriculum['courses'] if c['id'] == course_id), None)
        if not course:
            return {'error': f'Course {course_id} not found'}
        
        # Check prerequisites
        student_progress = [p for p in self.progress.get('progress', []) 
                          if p.get('student') == student_name and p.get('status') == 'completed']
        completed_courses = [p['course_id'] for p in student_progress]
        
        missing_prereqs = [p for p in course['prerequisites'] if p not in completed_courses]
        if missing_prereqs:
            return {'error': f'Missing prerequisites: {", ".join(missing_prereqs)}'}
        
        # Register
        registration = {
            'student': student_name,
            'course_id': course_id,
            'course_name': course['name'],
            'registration_date': datetime.now().isoformat(),
            'status': 'registered',
            'progress': 0
        }
        
        self.registrations['students'].append(registration)
        self.save_registrations()
        
        return registration
    
    def save_registrations(self):
        """Save registrations."""
        with open(self.registrations_file, 'w', encoding='utf-8') as f:
            json.dump(self.registrations, f, indent=2, ensure_ascii=False)
    
    def update_progress(self, student_name: str, course_id: str, progress_percent: int):
        """Update student progress."""
        progress_entry = {
            'student': student_name,
            'course_id': course_id,
            'progress': progress_percent,
            'last_updated': datetime.now().isoformat(),
            'status': 'completed' if progress_percent >= 100 else 'in_progress'
        }
        
        # Update or add progress
        existing = [p for p in self.progress.get('progress', []) 
                   if p.get('student') == student_name and p.get('course_id') == course_id]
        
        if existing:
            existing[0].update(progress_entry)
        else:
            self.progress['progress'].append(progress_entry)
        
        with open(self.progress_file, 'w', encoding='utf-8') as f:
            json.dump(self.progress, f, indent=2, ensure_ascii=False)

def main():
    """Test curriculum system."""
    print("=" * 60)
    print("CURRICULUM & REGISTRATION SYSTEM")
    print("Red Post Farms, LLC | Copyright (c) 2025-2026")
    print("=" * 60)
    print()
    
    system = CurriculumRegistrationSystem()
    
    # Confirm curriculum
    print("Confirming curriculum...")
    confirmation = system.confirm_curriculum('gatekeeper_basics')
    print(json.dumps(confirmation, indent=2))
    print()
    
    # Register for course
    print("Registering for course...")
    registration = system.register_for_course('Test Student', 'gatekeeper_basics')
    print(json.dumps(registration, indent=2))

if __name__ == '__main__':
    main()

# RPF-GK-2026-7A3F9B2C-4D8E1F6A-9C2B5D7E-3F8A1C4E (ownership signature)

