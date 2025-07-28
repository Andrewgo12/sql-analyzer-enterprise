#!/usr/bin/env python3
"""
MULTI-FORMAT EXPORT ENGINE
Enterprise-grade export system supporting 20+ formats
"""

import json
import csv
import xml.etree.ElementTree as ET
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import asdict
import io
import base64

class ExportEngine:
    """Multi-format export engine for analysis results"""
    
    def __init__(self):
        self.supported_formats = {
            'sql': self.export_sql,
            'html': self.export_html,
            'pdf': self.export_pdf,
            'json': self.export_json,
            'xml': self.export_xml,
            'csv': self.export_csv,
            'excel': self.export_excel,
            'markdown': self.export_markdown,
            'latex': self.export_latex,
            'txt': self.export_txt,
            'yaml': self.export_yaml,
            'mysql_dump': self.export_mysql_dump,
            'postgresql_backup': self.export_postgresql_backup,
            'oracle_script': self.export_oracle_script,
            'sql_server_script': self.export_sql_server_script,
            'documentation': self.export_documentation,
            'report': self.export_report,
            'summary': self.export_summary,
            'errors_only': self.export_errors_only,
            'recommendations': self.export_recommendations
        }
    
    def export(self, analysis_result: Any, format_type: str, options: Dict[str, Any] = None) -> Dict[str, Any]:
        """Export analysis result in specified format"""
        if format_type not in self.supported_formats:
            raise ValueError(f"Unsupported format: {format_type}")
        
        options = options or {}
        export_func = self.supported_formats[format_type]
        
        try:
            content = export_func(analysis_result, options)
            
            return {
                'success': True,
                'format': format_type,
                'content': content,
                'filename': self.generate_filename(format_type, options),
                'mime_type': self.get_mime_type(format_type),
                'size': len(content) if isinstance(content, str) else len(str(content))
            }
        
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'format': format_type
            }
    
    def export_sql(self, result: Any, options: Dict[str, Any]) -> str:
        """Export corrected SQL"""
        header = f"""-- SQL ANALYZER ENTERPRISE - CORRECTED SQL
-- Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
-- Database Type: {result.database_type.value}
-- Quality Score: {result.quality_score}/100
-- Complexity Score: {result.complexity_score}/100

"""
        
        # Add intelligent comments
        commented_sql = result.corrected_sql
        for comment in result.intelligent_comments:
            lines = commented_sql.split('\n')
            if comment['line_number'] <= len(lines):
                lines.insert(comment['line_number'] - 1, comment['comment'])
                commented_sql = '\n'.join(lines)
        
        return header + commented_sql
    
    def export_html(self, result: Any, options: Dict[str, Any]) -> str:
        """Export HTML report"""
        html = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SQL Analysis Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; line-height: 1.6; }}
        .header {{ background: #f4f4f4; padding: 20px; border-radius: 8px; margin-bottom: 30px; }}
        .section {{ margin-bottom: 30px; }}
        .error {{ background: #ffe6e6; padding: 10px; border-left: 4px solid #ff4444; margin: 10px 0; }}
        .warning {{ background: #fff3cd; padding: 10px; border-left: 4px solid #ffc107; margin: 10px 0; }}
        .success {{ background: #d4edda; padding: 10px; border-left: 4px solid #28a745; margin: 10px 0; }}
        .code {{ background: #f8f9fa; padding: 15px; border-radius: 4px; font-family: monospace; }}
        table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
        th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }}
        th {{ background-color: #f2f2f2; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>📊 SQL Analysis Report</h1>
        <p><strong>Generated:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        <p><strong>Database Type:</strong> {result.database_type.value}</p>
        <p><strong>Processing Time:</strong> {result.processing_time:.3f} seconds</p>
    </div>

    <div class="section">
        <h2>📈 Quality Metrics</h2>
        <div class="{'success' if result.quality_score >= 80 else 'warning' if result.quality_score >= 60 else 'error'}">
            <strong>Quality Score:</strong> {result.quality_score}/100
        </div>
        <div class="{'success' if result.complexity_score <= 50 else 'warning' if result.complexity_score <= 75 else 'error'}">
            <strong>Complexity Score:</strong> {result.complexity_score}/100
        </div>
    </div>

    <div class="section">
        <h2>🔍 Analysis Summary</h2>
        <ul>
            <li><strong>Total Lines:</strong> {result.total_lines}</li>
            <li><strong>Total Statements:</strong> {result.total_statements}</li>
            <li><strong>Syntax Errors:</strong> {len(result.syntax_errors)}</li>
            <li><strong>Semantic Errors:</strong> {len(result.semantic_errors)}</li>
            <li><strong>Performance Issues:</strong> {len(result.performance_issues)}</li>
            <li><strong>Security Vulnerabilities:</strong> {len(result.security_vulnerabilities)}</li>
        </ul>
    </div>
"""
        
        # Add errors section
        if result.syntax_errors or result.semantic_errors:
            html += """
    <div class="section">
        <h2>❌ Errors and Warnings</h2>
"""
            for error in result.syntax_errors + result.semantic_errors:
                severity_class = 'error' if error.severity == 'high' else 'warning'
                html += f"""
        <div class="{severity_class}">
            <strong>Line {error.line_number}:</strong> {error.message}<br>
            <em>Suggestion:</em> {error.suggestion}
        </div>
"""
            html += "    </div>"
        
        # Add recommendations
        if result.recommendations:
            html += """
    <div class="section">
        <h2>💡 Recommendations</h2>
        <ul>
"""
            for rec in result.recommendations:
                html += f"            <li>{rec}</li>\n"
            html += """        </ul>
    </div>
"""
        
        html += """
</body>
</html>"""
        
        return html
    
    def export_json(self, result: Any, options: Dict[str, Any]) -> str:
        """Export JSON format"""
        # Convert dataclass to dict
        data = {
            'metadata': {
                'generated_at': datetime.now().isoformat(),
                'format_version': '1.0',
                'analyzer_version': '2.0.0'
            },
            'analysis_result': {
                'file_hash': result.file_hash,
                'processing_time': result.processing_time,
                'database_type': result.database_type.value,
                'total_lines': result.total_lines,
                'total_statements': result.total_statements,
                'quality_score': result.quality_score,
                'complexity_score': result.complexity_score,
                'syntax_errors': [asdict(error) for error in result.syntax_errors],
                'semantic_errors': [asdict(error) for error in result.semantic_errors],
                'performance_issues': result.performance_issues,
                'security_vulnerabilities': result.security_vulnerabilities,
                'tables': [asdict(table) for table in result.tables],
                'relationships': result.relationships,
                'recommendations': result.recommendations,
                'intelligent_comments': result.intelligent_comments
            }
        }
        
        return json.dumps(data, indent=2, ensure_ascii=False)
    
    def export_xml(self, result: Any, options: Dict[str, Any]) -> str:
        """Export XML format"""
        root = ET.Element('sql_analysis_report')
        
        # Metadata
        metadata = ET.SubElement(root, 'metadata')
        ET.SubElement(metadata, 'generated_at').text = datetime.now().isoformat()
        ET.SubElement(metadata, 'database_type').text = result.database_type.value
        ET.SubElement(metadata, 'processing_time').text = str(result.processing_time)
        
        # Scores
        scores = ET.SubElement(root, 'scores')
        ET.SubElement(scores, 'quality_score').text = str(result.quality_score)
        ET.SubElement(scores, 'complexity_score').text = str(result.complexity_score)
        
        # Errors
        errors = ET.SubElement(root, 'errors')
        for error in result.syntax_errors + result.semantic_errors:
            error_elem = ET.SubElement(errors, 'error')
            ET.SubElement(error_elem, 'line_number').text = str(error.line_number)
            ET.SubElement(error_elem, 'type').text = error.error_type
            ET.SubElement(error_elem, 'severity').text = error.severity
            ET.SubElement(error_elem, 'message').text = error.message
            ET.SubElement(error_elem, 'suggestion').text = error.suggestion
        
        # Recommendations
        recommendations = ET.SubElement(root, 'recommendations')
        for rec in result.recommendations:
            ET.SubElement(recommendations, 'recommendation').text = rec
        
        return ET.tostring(root, encoding='unicode')
    
    def export_csv(self, result: Any, options: Dict[str, Any]) -> str:
        """Export CSV format"""
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write headers
        writer.writerow(['Type', 'Line', 'Severity', 'Message', 'Suggestion'])
        
        # Write errors
        for error in result.syntax_errors + result.semantic_errors:
            writer.writerow([
                error.error_type,
                error.line_number,
                error.severity,
                error.message,
                error.suggestion
            ])
        
        return output.getvalue()
    
    def export_markdown(self, result: Any, options: Dict[str, Any]) -> str:
        """Export Markdown format"""
        md = f"""# 📊 SQL Analysis Report

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Database Type:** {result.database_type.value}  
**Processing Time:** {result.processing_time:.3f} seconds

## 📈 Quality Metrics

- **Quality Score:** {result.quality_score}/100
- **Complexity Score:** {result.complexity_score}/100

## 🔍 Analysis Summary

| Metric | Count |
|--------|-------|
| Total Lines | {result.total_lines} |
| Total Statements | {result.total_statements} |
| Syntax Errors | {len(result.syntax_errors)} |
| Semantic Errors | {len(result.semantic_errors)} |
| Performance Issues | {len(result.performance_issues)} |
| Security Vulnerabilities | {len(result.security_vulnerabilities)} |

"""
        
        # Add errors
        if result.syntax_errors or result.semantic_errors:
            md += "## ❌ Errors and Warnings\n\n"
            for error in result.syntax_errors + result.semantic_errors:
                md += f"### Line {error.line_number}: {error.error_type}\n"
                md += f"**Severity:** {error.severity}  \n"
                md += f"**Message:** {error.message}  \n"
                md += f"**Suggestion:** {error.suggestion}\n\n"
        
        # Add recommendations
        if result.recommendations:
            md += "## 💡 Recommendations\n\n"
            for rec in result.recommendations:
                md += f"- {rec}\n"
        
        return md
    
    def export_txt(self, result: Any, options: Dict[str, Any]) -> str:
        """Export plain text format"""
        txt = f"""SQL ANALYSIS REPORT
==================

Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Database Type: {result.database_type.value}
Processing Time: {result.processing_time:.3f} seconds

QUALITY METRICS
---------------
Quality Score: {result.quality_score}/100
Complexity Score: {result.complexity_score}/100

ANALYSIS SUMMARY
----------------
Total Lines: {result.total_lines}
Total Statements: {result.total_statements}
Syntax Errors: {len(result.syntax_errors)}
Semantic Errors: {len(result.semantic_errors)}
Performance Issues: {len(result.performance_issues)}
Security Vulnerabilities: {len(result.security_vulnerabilities)}

"""
        
        # Add errors
        if result.syntax_errors or result.semantic_errors:
            txt += "ERRORS AND WARNINGS\n"
            txt += "-------------------\n"
            for error in result.syntax_errors + result.semantic_errors:
                txt += f"Line {error.line_number}: {error.message}\n"
                txt += f"  Suggestion: {error.suggestion}\n\n"
        
        # Add recommendations
        if result.recommendations:
            txt += "RECOMMENDATIONS\n"
            txt += "---------------\n"
            for rec in result.recommendations:
                txt += f"- {rec}\n"
        
        return txt
    
    def export_mysql_dump(self, result: Any, options: Dict[str, Any]) -> str:
        """Export MySQL dump format"""
        dump = f"""-- MySQL dump generated by SQL Analyzer Enterprise
-- Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
-- Quality Score: {result.quality_score}/100

SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_AUTO_CREATE_USER,NO_ENGINE_SUBSTITUTION';

{result.corrected_sql}

SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;
"""
        return dump
    
    def export_postgresql_backup(self, result: Any, options: Dict[str, Any]) -> str:
        """Export PostgreSQL backup format"""
        backup = f"""--
-- PostgreSQL database dump generated by SQL Analyzer Enterprise
-- Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
-- Quality Score: {result.quality_score}/100
--

SET statement_timeout = 0;
SET lock_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SET check_function_bodies = false;
SET client_min_messages = warning;

{result.corrected_sql}

--
-- PostgreSQL database dump complete
--
"""
        return backup
    
    # Placeholder implementations for other formats
    def export_pdf(self, result: Any, options: Dict[str, Any]) -> str:
        return "PDF export requires additional libraries (reportlab)"
    
    def export_excel(self, result: Any, options: Dict[str, Any]) -> str:
        return "Excel export requires additional libraries (openpyxl)"
    
    def export_latex(self, result: Any, options: Dict[str, Any]) -> str:
        return "LaTeX export implementation"
    
    def export_yaml(self, result: Any, options: Dict[str, Any]) -> str:
        return "YAML export requires additional libraries (PyYAML)"
    
    def export_oracle_script(self, result: Any, options: Dict[str, Any]) -> str:
        return f"-- Oracle SQL Script\n{result.corrected_sql}"
    
    def export_sql_server_script(self, result: Any, options: Dict[str, Any]) -> str:
        return f"-- SQL Server Script\n{result.corrected_sql}"
    
    def export_documentation(self, result: Any, options: Dict[str, Any]) -> str:
        return self.export_html(result, options)
    
    def export_report(self, result: Any, options: Dict[str, Any]) -> str:
        return self.export_html(result, options)
    
    def export_summary(self, result: Any, options: Dict[str, Any]) -> str:
        return self.export_txt(result, options)
    
    def export_errors_only(self, result: Any, options: Dict[str, Any]) -> str:
        return self.export_csv(result, options)
    
    def export_recommendations(self, result: Any, options: Dict[str, Any]) -> str:
        return '\n'.join(result.recommendations)
    
    def generate_filename(self, format_type: str, options: Dict[str, Any]) -> str:
        """Generate appropriate filename"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        extensions = {
            'sql': 'sql',
            'html': 'html',
            'pdf': 'pdf',
            'json': 'json',
            'xml': 'xml',
            'csv': 'csv',
            'excel': 'xlsx',
            'markdown': 'md',
            'latex': 'tex',
            'txt': 'txt',
            'yaml': 'yml',
            'mysql_dump': 'sql',
            'postgresql_backup': 'sql'
        }
        
        ext = extensions.get(format_type, 'txt')
        return f"sql_analysis_{timestamp}.{ext}"
    
    def get_mime_type(self, format_type: str) -> str:
        """Get MIME type for format"""
        mime_types = {
            'sql': 'text/plain',
            'html': 'text/html',
            'pdf': 'application/pdf',
            'json': 'application/json',
            'xml': 'application/xml',
            'csv': 'text/csv',
            'excel': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'markdown': 'text/markdown',
            'latex': 'application/x-latex',
            'txt': 'text/plain',
            'yaml': 'application/x-yaml'
        }
        
        return mime_types.get(format_type, 'text/plain')
