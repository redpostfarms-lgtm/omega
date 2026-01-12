# -*- coding: utf-8 -*-
# CODE GENERATION - Self-writing agents
# Agents write their own code improvements

import os
import sys
import ast
import json
import time
import hashlib
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import subprocess


@dataclass
class CodeGeneration:
    """Code generation metadata."""
    agent_id: str
    generation_type: str  # 'improvement', 'fix', 'feature', 'refactor'
    original_code: str
    generated_code: str
    reasoning: str
    tests_passed: bool = False
    timestamp: float = 0.0


class AgentCodeGenerator:
    """
    Code generation system for self-writing agents.
    
    Agents can:
    - Write code improvements
    - Fix bugs in their own code
    - Add new features
    - Refactor existing code
    """
    
    def __init__(self, code_dir: str = './agent_generated_code'):
        """Initialize code generator."""
        self.code_dir = Path(code_dir)
        self.code_dir.mkdir(parents=True, exist_ok=True)
        
        self.generations: List[CodeGeneration] = []
        self.generation_count = 0
        
        # Templates for code generation
        self.code_templates = self._load_templates()
    
    def _load_templates(self) -> Dict[str, str]:
        """Load code generation templates."""
        return {
            'improvement': """
# Auto-generated improvement by agent
# Original: {original_function}
# Reason: {reasoning}

def improved_{function_name}({params}):
    \"\"\"Improved version of {function_name}.\"\"\"
    {improvements}
    return result
""",
            'fix': """
# Auto-generated fix by agent
# Issue: {issue}
# Fix: {fix_reasoning}

def fixed_{function_name}({params}):
    \"\"\"Fixed version of {function_name}.\"\"\"
    {fix_code}
    return result
""",
            'feature': """
# Auto-generated feature by agent
# Feature: {feature_name}
# Purpose: {purpose}

def {feature_name}({params}):
    \"\"\"{feature_description}.\"\"\"
    {feature_code}
    return result
"""
        }
    
    def generate_improvement(self, agent_id: str, original_code: str, 
                            reasoning: str) -> Optional[str]:
        """
        Generate improved version of code.
        
        Args:
            agent_id: Agent identifier
            original_code: Original code to improve
            reasoning: Why improvement is needed
            
        Returns:
            Path to generated code file
        """
        try:
            # Parse original code
            tree = ast.parse(original_code)
            
            # Extract function info
            functions = [node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
            
            if not functions:
                return None
            
            func = functions[0]
            function_name = func.name
            params = ', '.join([arg.arg for arg in func.args.args])
            
            # Generate improvements (simplified - would use LLM in production)
            improvements = self._generate_improvements_code(func, reasoning)
            
            # Create improved code
            improved_code = f"""
# Auto-generated improvement by {agent_id}
# Original: {function_name}
# Reason: {reasoning}
# Generated: {time.time()}

{improvements}
"""
            
            # Save generated code
            filename = f"{agent_id}_improvement_{self.generation_count}.py"
            filepath = self.code_dir / filename
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(improved_code)
            
            # Record generation
            gen = CodeGeneration(
                agent_id=agent_id,
                generation_type='improvement',
                original_code=original_code,
                generated_code=improved_code,
                reasoning=reasoning,
                timestamp=time.time()
            )
            self.generations.append(gen)
            self.generation_count += 1
            
            # Test generated code
            gen.tests_passed = self._test_code(improved_code)
            
            print(f"[Code Generator] Generated improvement: {filepath}")
            print(f"[Code Generator] Tests passed: {gen.tests_passed}")
            
            return str(filepath)
        
        except Exception as e:
            print(f"[Code Generator] Generation failed: {e}")
            return None
    
    def _generate_improvements_code(self, func: ast.FunctionDef, reasoning: str) -> str:
        """Generate improved code (simplified version)."""
        # In production, would use LLM to generate actual improvements
        # For now, add basic improvements
        
        improvements = []
        
        # Add error handling
        if not any(isinstance(node, ast.Try) for node in ast.walk(func)):
            improvements.append("# Added error handling")
        
        # Add type hints if missing
        if not func.returns:
            improvements.append("# Added return type hint")
        
        # Add docstring if missing
        if not ast.get_docstring(func):
            improvements.append(f'"""Improved version. {reasoning}"""')
        
        # Generate improved function
        improved = f"""
def improved_{func.name}({', '.join(arg.arg for arg in func.args.args)}):
    \"\"\"Improved version of {func.name}. {reasoning}\"\"\"
    try:
        # Original logic with improvements
        # TODO: LLM-generated improvements here
        pass
    except Exception as e:
        # Error handling
        raise
"""
        
        return improved
    
    def generate_fix(self, agent_id: str, buggy_code: str, error_message: str,
                    fix_reasoning: str) -> Optional[str]:
        """
        Generate fix for buggy code.
        
        Args:
            agent_id: Agent identifier
            buggy_code: Code with bug
            error_message: Error message
            fix_reasoning: How to fix it
            
        Returns:
            Path to fixed code file
        """
        try:
            # Parse code to find issues
            tree = ast.parse(buggy_code)
            
            # Generate fix (simplified)
            fixed_code = f"""
# Auto-generated fix by {agent_id}
# Error: {error_message}
# Fix: {fix_reasoning}
# Generated: {time.time()}

{self._apply_fixes(buggy_code, error_message)}
"""
            
            # Save
            filename = f"{agent_id}_fix_{self.generation_count}.py"
            filepath = self.code_dir / filename
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(fixed_code)
            
            # Record
            gen = CodeGeneration(
                agent_id=agent_id,
                generation_type='fix',
                original_code=buggy_code,
                generated_code=fixed_code,
                reasoning=fix_reasoning,
                timestamp=time.time()
            )
            
            # Test
            gen.tests_passed = self._test_code(fixed_code)
            
            self.generations.append(gen)
            self.generation_count += 1
            
            print(f"[Code Generator] Generated fix: {filepath}")
            
            return str(filepath)
        
        except Exception as e:
            print(f"[Code Generator] Fix generation failed: {e}")
            return None
    
    def _apply_fixes(self, code: str, error: str) -> str:
        """Apply fixes to code (simplified)."""
        # In production, would use LLM to generate actual fixes
        # For now, add basic error handling
        
        fixes = []
        
        if "NameError" in error:
            fixes.append("# Fix: Added missing variable/import")
        if "TypeError" in error:
            fixes.append("# Fix: Added type checking")
        if "AttributeError" in error:
            fixes.append("# Fix: Added attribute existence check")
        
        return code + "\n" + "\n".join(fixes)
    
    def generate_feature(self, agent_id: str, feature_name: str, 
                        purpose: str, requirements: List[str]) -> Optional[str]:
        """
        Generate new feature code.
        
        Args:
            agent_id: Agent identifier
            feature_name: Name of feature
            purpose: Purpose of feature
            requirements: List of requirements
            
        Returns:
            Path to generated feature file
        """
        try:
            # Generate feature code
            feature_code = f"""
# Auto-generated feature by {agent_id}
# Feature: {feature_name}
# Purpose: {purpose}
# Requirements: {', '.join(requirements)}
# Generated: {time.time()}

def {feature_name}({', '.join(f'req_{i}' for i in range(len(requirements)))}):
    \"\"\"{purpose}.\"\"\"
    # TODO: LLM-generated feature implementation
    # Requirements: {requirements}
    pass
"""
            
            # Save
            filename = f"{agent_id}_feature_{feature_name}_{self.generation_count}.py"
            filepath = self.code_dir / filename
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(feature_code)
            
            # Record
            gen = CodeGeneration(
                agent_id=agent_id,
                generation_type='feature',
                original_code='',
                generated_code=feature_code,
                reasoning=purpose,
                timestamp=time.time()
            )
            
            self.generations.append(gen)
            self.generation_count += 1
            
            print(f"[Code Generator] Generated feature: {filepath}")
            
            return str(filepath)
        
        except Exception as e:
            print(f"[Code Generator] Feature generation failed: {e}")
            return None
    
    def _test_code(self, code: str) -> bool:
        """Test generated code."""
        try:
            # Try to compile
            compile(code, '<string>', 'exec')
            return True
        except:
            return False
    
    def get_generations(self, agent_id: Optional[str] = None) -> List[CodeGeneration]:
        """Get code generations."""
        if agent_id:
            return [g for g in self.generations if g.agent_id == agent_id]
        return self.generations
    
    def get_stats(self) -> Dict[str, Any]:
        """Get generator statistics."""
        return {
            'total_generations': len(self.generations),
            'successful_tests': sum(1 for g in self.generations if g.tests_passed),
            'improvements': sum(1 for g in self.generations if g.generation_type == 'improvement'),
            'fixes': sum(1 for g in self.generations if g.generation_type == 'fix'),
            'features': sum(1 for g in self.generations if g.generation_type == 'feature')
        }


if __name__ == '__main__':
    print("=" * 60)
    print("CODE GENERATOR - Test")
    print("=" * 60)
    
    generator = AgentCodeGenerator()
    
    # Test improvement generation
    original = """
def process_data(data):
    result = data * 2
    return result
"""
    
    improved = generator.generate_improvement(
        "agent_001",
        original,
        "Add error handling and type checking"
    )
    
    print(f"\nGenerated: {improved}")
    
    stats = generator.get_stats()
    print(f"\nStats: {stats}")
    
    print("\n[OK] Code generator ready")

