# -*- coding: utf-8 -*-
# PROPRIETARY SOFTWARE - RED POST FARMS, LLC
# Report Generator with Template Engine - Legitimate Use Cases
#
# Purpose: Generate reports for your own systems and assessments
# Use for: Security reports, performance reports, documentation

from jinja2 import Template
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional
import json

class ReportGenerator:
    """Template-based report generator for legitimate use cases.
    
    Use for:
    - Security assessment reports (your own systems)
    - Performance reports
    - Documentation generation
    - Code review reports
    
    NOT for:
    - Automated vulnerability reporting to unauthorized systems
    - Spam generation
    - Unauthorized automation
    """
    
    def __init__(self):
        """Initialize report generator."""
        self.templates = {}
        self._load_default_templates()
    
    def _load_default_templates(self):
        """Load default report templates."""
        # Security Assessment Report Template
        self.templates['security'] = Template("""
# Security Assessment Report

**Generated:** {{ date }}
**System:** {{ system_name }}
**Assessment Type:** {{ assessment_type }}

## Executive Summary

Total Findings: {{ findings|length }}
- Critical: {{ critical_count }}
- High: {{ high_count }}
- Medium: {{ medium_count }}
- Low: {{ low_count }}

## Findings

{% for finding in findings %}
### {{ finding.type }}

**Severity:** {{ finding.severity }}
**Location:** {{ finding.file }}:{{ finding.line }}
**Description:** {{ finding.message }}

{% if finding.code %}
**Code:**
```
{{ finding.code }}
```
{% endif %}

**Recommendation:** {{ finding.recommendation }}

---
{% endfor %}

## Summary

This assessment was conducted on your own systems with proper authorization.
All findings should be reviewed and addressed according to your security policies.

**Report Generated:** {{ date }}
""")
        
        # Performance Report Template
        self.templates['performance'] = Template("""
# Performance Assessment Report

**Generated:** {{ date }}
**System:** {{ system_name }}

## Performance Metrics

{% for metric in metrics %}
### {{ metric.name }}

- **Value:** {{ metric.value }} {{ metric.unit }}
- **Target:** {{ metric.target }} {{ metric.unit }}
- **Status:** {{ metric.status }}

{% endfor %}

## Recommendations

{% for rec in recommendations %}
- {{ rec }}
{% endfor %}

**Report Generated:** {{ date }}
""")
    
    def generate_security_report(self, findings: List[Dict[str, Any]], 
                                 system_name: str = "My System",
                                 assessment_type: str = "Code Review") -> str:
        """Generate security assessment report.
        
        Args:
            findings: List of vulnerability findings
            system_name: Name of system assessed
            assessment_type: Type of assessment
        
        Returns:
            Generated report as string
        """
        # Categorize findings
        critical = [f for f in findings if f.get('severity') == 'critical']
        high = [f for f in findings if f.get('severity') == 'high']
        medium = [f for f in findings if f.get('severity') == 'medium']
        low = [f for f in findings if f.get('severity') == 'low']
        
        # Add recommendations if not present
        for finding in findings:
            if 'recommendation' not in finding:
                finding['recommendation'] = self._get_recommendation(finding.get('type', ''))
        
        return self.templates['security'].render(
            date=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            system_name=system_name,
            assessment_type=assessment_type,
            findings=findings,
            critical_count=len(critical),
            high_count=len(high),
            medium_count=len(medium),
            low_count=len(low)
        )
    
    def generate_performance_report(self, metrics: List[Dict[str, Any]],
                                   system_name: str = "My System",
                                   recommendations: List[str] = None) -> str:
        """Generate performance assessment report.
        
        Args:
            metrics: List of performance metrics
            system_name: Name of system assessed
            recommendations: List of recommendations
        
        Returns:
            Generated report as string
        """
        if recommendations is None:
            recommendations = []
        
        # Add status to metrics
        for metric in metrics:
            if 'status' not in metric:
                metric['status'] = self._evaluate_metric_status(metric)
        
        return self.templates['performance'].render(
            date=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            system_name=system_name,
            metrics=metrics,
            recommendations=recommendations
        )
    
    def _get_recommendation(self, vuln_type: str) -> str:
        """Get recommendation for vulnerability type."""
        recommendations = {
            "Hardcoded password": "Use environment variables or secure credential storage",
            "SQL Injection Risk": "Use parameterized queries with placeholders",
            "Command Injection Risk": "Sanitize input and use subprocess with shell=False",
            "Path Traversal Risk": "Validate and sanitize file paths using os.path functions",
            "Unsafe deserialization": "Use safe deserialization methods (yaml.safe_load, etc.)",
        }
        return recommendations.get(vuln_type, "Review and address according to security best practices")
    
    def _evaluate_metric_status(self, metric: Dict[str, Any]) -> str:
        """Evaluate if metric meets target."""
        value = metric.get('value', 0)
        target = metric.get('target', 0)
        
        if value <= target:
            return "✅ Meets Target"
        elif value <= target * 1.1:
            return "⚠️  Slightly Over"
        else:
            return "❌ Exceeds Target"
    
    def save_report(self, report: str, output_path: Path, format: str = 'markdown'):
        """Save report to file.
        
        Args:
            report: Report content
            output_path: Path to save report
            format: Report format ('markdown', 'txt')
        """
        output_path = Path(output_path)
        
        if format == 'markdown':
            if not output_path.suffix:
                output_path = output_path.with_suffix('.md')
        elif format == 'txt':
            if not output_path.suffix:
                output_path = output_path.with_suffix('.txt')
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"Report saved to: {output_path}")


def main():
    """Example usage (generate reports for your own systems)."""
    print("Report Generator - Legitimate Use Cases Only")
    print("=" * 60)
    
    generator = ReportGenerator()
    
    # Example: Generate security report
    example_findings = [
        {
            "type": "Hardcoded password",
            "severity": "high",
            "file": "config.py",
            "line": 42,
            "message": "Hardcoded password detected",
            "code": "password = 'secret123'"
        },
        {
            "type": "SQL Injection Risk",
            "severity": "high",
            "file": "database.py",
            "line": 15,
            "message": "SQL query uses string formatting",
            "code": "cursor.execute(f'SELECT * FROM users WHERE id = {user_id}')"
        }
    ]
    
    print("Generating security report...")
    security_report = generator.generate_security_report(
        findings=example_findings,
        system_name="My Application",
        assessment_type="Code Security Review"
    )
    
    # Save report
    output_path = Path("security_report_example.md")
    generator.save_report(security_report, output_path)
    
    print("\n✅ Report generation complete (your own systems only)")


if __name__ == '__main__':
    main()
