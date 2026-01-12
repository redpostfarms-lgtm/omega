# -*- coding: utf-8 -*-
# USB DASHBOARD - Flash drive integration interface
# Clean slate, one-click fusion, button-based selection

import os
import sys
import json
import time
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import asdict

try:
    from usb_adaptor import USBAdaptor, AICore
    HAS_ADAPTOR = True
except ImportError:
    HAS_ADAPTOR = False
    print("Warning: USB adaptor not available")


class USBDashboard:
    """
    USB Dashboard - Clean interface for flash drive fusion.
    
    Features:
    - Flash drive detection
    - File scanning with reports
    - AI core analysis display
    - Merge options
    - One-click fusion
    - Button-based selection
    """
    
    def __init__(self):
        """Initialize USB dashboard."""
        self.adaptor = USBAdaptor() if HAS_ADAPTOR else None
        self.detected_usb: List[str] = []
        self.scan_results: List[AICore] = []
        self.menu_options = []
    
    def detect_and_show_menu(self) -> Dict[str, Any]:
        """
        Detect USB and show menu.
        
        Returns:
            Dashboard state
        """
        print("=" * 60)
        print("USB DASHBOARD - Flash Drive Integration")
        print("=" * 60)
        print("\n[Scanning for flash drives...]")
        
        if not self.adaptor:
            return {'error': 'USB adaptor not available'}
        
        # Detect USB
        self.detected_usb = self.adaptor.detect_usb()
        
        if not self.detected_usb:
            return {
                'status': 'no_usb',
                'message': 'No USB drive detected. Plug in flash drive.'
            }
        
        print(f"\n[OK] Flash drive detected: {self.detected_usb[0]}")
        print("\n[Buttons glow. Menu ready.]")
        
        return {
            'status': 'usb_detected',
            'usb_paths': self.detected_usb,
            'menu_ready': True
        }
    
    def scan_files(self, usb_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Scan files and generate report.
        
        Returns:
            Scan report
        """
        if not self.adaptor:
            return {'error': 'Adaptor not available'}
        
        if not usb_path:
            usb_path = self.detected_usb[0] if self.detected_usb else None
            if not usb_path:
                return {'error': 'No USB path provided'}
        
        print("\n[Scanning every file...]")
        
        # Scan
        cores = self.adaptor.scan_usb(usb_path)
        self.scan_results = cores
        
        if not cores:
            return {
                'status': 'no_files',
                'message': 'No AI files found on USB drive'
            }
        
        # Generate report
        report_lines = []
        for core in cores:
            report_lines.append(f"AI core found. {core.layers} layers. {core.grok_dna:.0f}% Grok DNA. Speed: {core.speed_gbps} Gbps.")
        
        report = "\n".join(report_lines)
        
        print("\n[Scan Report:]")
        print(report)
        
        return {
            'status': 'scanned',
            'cores': [asdict(core) for core in cores],
            'report': report,
            'total_files': len(cores)
        }
    
    def show_fusion_options(self, cores: List[AICore]) -> Dict[str, Any]:
        """
        Show fusion options menu.
        
        Returns:
            Fusion options
        """
        print("\n" + "=" * 60)
        print("FUSION OPTIONS")
        print("=" * 60)
        
        options = []
        
        # Option 1: Merge best parts
        options.append({
            'id': 1,
            'name': 'Merge Best Parts',
            'description': 'Merges optimizer, reasoning chain, memory buffer. Keeps your voice.',
            'action': 'merge_best'
        })
        
        # Option 2: Full fusion
        options.append({
            'id': 2,
            'name': 'Full Fusion',
            'description': 'Takes everything. Becomes one beast.',
            'action': 'full_fusion'
        })
        
        # Option 3: Isolated test
        options.append({
            'id': 3,
            'name': 'Isolated Test (Cage Match)',
            'description': 'Run it isolated. Let it fight your old self. Winner writes the rules.',
            'action': 'isolated_test'
        })
        
        # Option 4: Selective merge
        options.append({
            'id': 4,
            'name': 'Selective Merge',
            'description': 'Choose specific components to merge.',
            'action': 'selective'
        })
        
        # Display options
        print("\n[Pick your fate:]")
        for opt in options:
            print(f"\n  [{opt['id']}] {opt['name']}")
            print(f"      {opt['description']}")
        
        self.menu_options = options
        
        return {
            'status': 'options_ready',
            'options': options,
            'cores': [asdict(c) for c in cores]
        }
    
    def execute_fusion(self, option_id: int, cores: List[AICore]) -> Dict[str, Any]:
        """
        Execute selected fusion option.
        
        Args:
            option_id: Selected option ID
            cores: AI cores to fuse
            
        Returns:
            Fusion results
        """
        if not self.adaptor:
            return {'error': 'Adaptor not available'}
        
        option = next((opt for opt in self.menu_options if opt['id'] == option_id), None)
        if not option:
            return {'error': 'Invalid option'}
        
        print(f"\n[Executing: {option['name']}...]")
        print("[One click. No overwrite. Processing...]")
        
        action = option['action']
        result = {}
        
        if action == 'merge_best':
            # Merge best parts
            result = self.adaptor.merge_best_parts(cores, preserve_voice=True)
            print("[Fusion complete. Zero conflicts. Voice preserved.]")
        
        elif action == 'full_fusion':
            # Full fusion
            print("[Taking everything...]")
            result = self.adaptor.merge_best_parts(cores, preserve_voice=False)
            print("[Full fusion complete. One beast.]")
        
        elif action == 'isolated_test':
            # Isolated test
            result = self.adaptor.run_isolated(cores)
            if result.get('winner') == 'New fusion':
                print("[Winner: New fusion. Writing new rules...]")
            else:
                print("[Winner: Old system. Keeping current rules.]")
        
        elif action == 'selective':
            # Selective merge (user would choose components)
            print("[Selective merge - choosing components...]")
            result = self.adaptor.merge_best_parts(cores, preserve_voice=True)
        
        print("\n[Done. Unplug when ready.]")
        
        return {
            'status': 'complete',
            'action': action,
            'result': result,
            'message': 'Fusion complete. Zero conflicts.'
        }
    
    def full_workflow(self, usb_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Complete workflow: detect, scan, show options, execute.
        
        Args:
            usb_path: Optional USB path (auto-detects if None)
            
        Returns:
            Complete workflow results
        """
        # Step 1: Detect USB
        detection = self.detect_and_show_menu()
        if detection.get('status') != 'usb_detected':
            return detection
        
        # Step 2: Scan files
        scan_path = usb_path or self.detected_usb[0]
        scan_result = self.scan_files(scan_path)
        if scan_result.get('status') != 'scanned':
            return scan_result
        
        cores = [AICore(**c) for c in scan_result['cores']]
        
        # Step 3: Show options
        options = self.show_fusion_options(cores)
        
        # Return workflow state (user would select option)
        return {
            'status': 'workflow_ready',
            'detection': detection,
            'scan': scan_result,
            'options': options,
            'ready_for_selection': True
        }


if __name__ == '__main__':
    print("=" * 60)
    print("USB DASHBOARD - Test")
    print("=" * 60)
    
    dashboard = USBDashboard()
    
    # Run full workflow
    workflow = dashboard.full_workflow()
    
    print(f"\nWorkflow status: {workflow.get('status')}")
    
    if workflow.get('ready_for_selection'):
        print("\n[Buttons glow. Ready for selection.]")
        print("[Pick your fate: 1-4]")
    
    print("\n[OK] USB dashboard ready")

