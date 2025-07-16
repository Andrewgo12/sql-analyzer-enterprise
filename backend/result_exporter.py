#!/usr/bin/env python3
"""
RESULT EXPORTER - ENTERPRISE EXPORT FUNCTIONALITY
Multi-format export capabilities for analysis results
"""

import json
import csv
import xml.etree.ElementTree as ET
from xml.dom import minidom
import tempfile
import os
from typing import Dict, Any, List, Optional
from datetime import datetime
from pathlib import Path

class ResultExporter:
    """Enterprise-grade result exporter with multiple format support"""
    
    def __init__(self):
        self.supported_formats = {
            'json': self.export_json,
            'html': self.export_html,
            'txt': self.export_txt,
            'csv': self.export_csv,
            'xml': self.export_xml,
            'pdf': self.export_pdf,
            'markdown': self.export_markdown,
            'excel': self.export_excel,
            'sql': self.export_sql
        }
    
    def export_results(self, results: Dict[str, Any], format_type: str, filename: Optional[str] = None) -> Dict[str, Any]:
        """Export analysis results in specified format"""
        try:
            if format_type not in self.supported_formats:
                return {
                    'success': False,
                    'error': f'Unsupported format: {format_type}. Supported: {", ".join(self.supported_formats.keys())}'
                }
            
            # Generate filename if not provided
            if not filename:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f'sql_analysis_{timestamp}.{format_type}'
            
            # Export using appropriate method
            export_method = self.supported_formats[format_type]
            export_result = export_method(results, filename)
            
            return export_result
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Export failed: {str(e)}'
            }
    
    def export_json(self, results: Dict[str, Any], filename: str) -> Dict[str, Any]:
        """Export results as JSON"""
        try:
            # Create temporary file
            temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8')
            
            # Prepare export data
            export_data = {
                'export_info': {
                    'format': 'JSON',
                    'exported_at': datetime.now().isoformat(),
                    'filename': filename,
                    'version': '1.0'
                },
                'analysis_results': results
            }
            
            # Write JSON with pretty formatting
            json.dump(export_data, temp_file, indent=2, ensure_ascii=False, default=str)
            temp_file.close()
            
            return {
                'success': True,
                'file_path': temp_file.name,
                'filename': filename,
                'format': 'json',
                'size': os.path.getsize(temp_file.name)
            }
            
        except Exception as e:
            return {'success': False, 'error': f'JSON export failed: {str(e)}'}
    
    def export_html(self, results: Dict[str, Any], filename: str) -> Dict[str, Any]:
        """Export results as HTML report"""
        try:
            temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8')
            
            html_content = self._generate_html_report(results)
            temp_file.write(html_content)
            temp_file.close()
            
            return {
                'success': True,
                'file_path': temp_file.name,
                'filename': filename,
                'format': 'html',
                'size': os.path.getsize(temp_file.name)
            }
            
        except Exception as e:
            return {'success': False, 'error': f'HTML export failed: {str(e)}'}
    
    def export_txt(self, results: Dict[str, Any], filename: str) -> Dict[str, Any]:
        """Export results as plain text"""
        try:
            temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8')
            
            txt_content = self._generate_text_report(results)
            temp_file.write(txt_content)
            temp_file.close()
            
            return {
                'success': True,
                'file_path': temp_file.name,
                'filename': filename,
                'format': 'txt',
                'size': os.path.getsize(temp_file.name)
            }
            
        except Exception as e:
            return {'success': False, 'error': f'TXT export failed: {str(e)}'}
    
    def export_csv(self, results: Dict[str, Any], filename: str) -> Dict[str, Any]:
        """Export results as CSV"""
        try:
            temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, encoding='utf-8', newline='')
            
            writer = csv.writer(temp_file)
            
            # Write header
            writer.writerow(['Category', 'Item', 'Value', 'Details'])
            
            # Write analysis data
            self._write_csv_data(writer, results)
            
            temp_file.close()
            
            return {
                'success': True,
                'file_path': temp_file.name,
                'filename': filename,
                'format': 'csv',
                'size': os.path.getsize(temp_file.name)
            }
            
        except Exception as e:
            return {'success': False, 'error': f'CSV export failed: {str(e)}'}
    
    def export_xml(self, results: Dict[str, Any], filename: str) -> Dict[str, Any]:
        """Export results as XML"""
        try:
            temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.xml', delete=False, encoding='utf-8')
            
            xml_content = self._generate_xml_report(results)
            temp_file.write(xml_content)
            temp_file.close()
            
            return {
                'success': True,
                'file_path': temp_file.name,
                'filename': filename,
                'format': 'xml',
                'size': os.path.getsize(temp_file.name)
            }
            
        except Exception as e:
            return {'success': False, 'error': f'XML export failed: {str(e)}'}
    
    def export_pdf(self, results: Dict[str, Any], filename: str) -> Dict[str, Any]:
        """Export results as PDF (simplified implementation)"""
        try:
            # For now, create HTML and suggest PDF conversion
            html_result = self.export_html(results, filename.replace('.pdf', '.html'))
            
            if html_result['success']:
                return {
                    'success': True,
                    'file_path': html_result['file_path'],
                    'filename': filename,
                    'format': 'pdf',
                    'size': html_result['size'],
                    'note': 'PDF export generated as HTML. Use browser print-to-PDF for PDF format.'
                }
            else:
                return html_result
                
        except Exception as e:
            return {'success': False, 'error': f'PDF export failed: {str(e)}'}
    
    def export_markdown(self, results: Dict[str, Any], filename: str) -> Dict[str, Any]:
        """Export results as Markdown"""
        try:
            temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False, encoding='utf-8')
            
            md_content = self._generate_markdown_report(results)
            temp_file.write(md_content)
            temp_file.close()
            
            return {
                'success': True,
                'file_path': temp_file.name,
                'filename': filename,
                'format': 'markdown',
                'size': os.path.getsize(temp_file.name)
            }
            
        except Exception as e:
            return {'success': False, 'error': f'Markdown export failed: {str(e)}'}
    
    def export_excel(self, results: Dict[str, Any], filename: str) -> Dict[str, Any]:
        """Export results as Excel (simplified as CSV)"""
        try:
            # For now, export as CSV which can be opened in Excel
            csv_result = self.export_csv(results, filename.replace('.xlsx', '.csv'))
            
            if csv_result['success']:
                return {
                    'success': True,
                    'file_path': csv_result['file_path'],
                    'filename': filename,
                    'format': 'excel',
                    'size': csv_result['size'],
                    'note': 'Excel export generated as CSV format.'
                }
            else:
                return csv_result
                
        except Exception as e:
            return {'success': False, 'error': f'Excel export failed: {str(e)}'}
    
    def export_sql(self, results: Dict[str, Any], filename: str) -> Dict[str, Any]:
        """Export results as SQL script"""
        try:
            temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.sql', delete=False, encoding='utf-8')
            
            sql_content = self._generate_sql_script(results)
            temp_file.write(sql_content)
            temp_file.close()
            
            return {
                'success': True,
                'file_path': temp_file.name,
                'filename': filename,
                'format': 'sql',
                'size': os.path.getsize(temp_file.name)
            }
            
        except Exception as e:
            return {'success': False, 'error': f'SQL export failed: {str(e)}'}
    
    def _generate_html_report(self, results: Dict[str, Any]) -> str:
        """Generate HTML report"""
        html = f"""
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SQL Analysis Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        h1 {{ color: #2563eb; border-bottom: 2px solid #2563eb; padding-bottom: 10px; }}
        h2 {{ color: #1f2937; margin-top: 30px; }}
        .section {{ margin: 20px 0; padding: 15px; background: #f8fafc; border-left: 4px solid #3b82f6; }}
        .error {{ background: #fef2f2; border-left-color: #ef4444; }}
        .warning {{ background: #fffbeb; border-left-color: #f59e0b; }}
        .success {{ background: #f0fdf4; border-left-color: #10b981; }}
        table {{ width: 100%; border-collapse: collapse; margin: 10px 0; }}
        th, td {{ padding: 8px 12px; text-align: left; border-bottom: 1px solid #e5e7eb; }}
        th {{ background: #f3f4f6; font-weight: 600; }}
        .score {{ font-size: 24px; font-weight: bold; }}
        .timestamp {{ color: #6b7280; font-size: 12px; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>📊 SQL Analysis Report</h1>
        <p class="timestamp">Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        
        {self._generate_html_sections(results)}
    </div>
</body>
</html>
"""
        return html
    
    def _generate_html_sections(self, results: Dict[str, Any]) -> str:
        """Generate HTML sections for different result types"""
        sections = []
        
        # SQL Analysis section
        if 'sql_analysis' in results:
            sql_data = results['sql_analysis']
            sections.append(f"""
            <div class="section">
                <h2>🔍 SQL Analysis</h2>
                <p><strong>Quality Score:</strong> <span class="score">{sql_data.get('quality_score', 'N/A')}/100</span></p>
                <p><strong>Processing Time:</strong> {sql_data.get('processing_time', 'N/A')}s</p>
                <p><strong>Complexity Score:</strong> {sql_data.get('complexity_score', 'N/A')}/100</p>
            </div>
            """)
        
        # Security Analysis section
        if 'security_analysis' in results:
            sec_data = results['security_analysis']
            sections.append(f"""
            <div class="section">
                <h2>🛡️ Security Analysis</h2>
                <p><strong>Security Score:</strong> <span class="score">{sec_data.get('security_score', 'N/A')}/100</span></p>
                <p><strong>Risk Level:</strong> {sec_data.get('risk_level', 'N/A')}</p>
                <p><strong>Vulnerabilities Found:</strong> {len(sec_data.get('vulnerabilities', []))}</p>
            </div>
            """)
        
        # Performance Analysis section
        if 'performance_analysis' in results:
            perf_data = results['performance_analysis']
            sections.append(f"""
            <div class="section">
                <h2>⚡ Performance Analysis</h2>
                <p><strong>Performance Score:</strong> <span class="score">{perf_data.get('performance_score', 'N/A')}/100</span></p>
                <p><strong>Issues Found:</strong> {len(perf_data.get('performance_issues', []))}</p>
                <p><strong>Index Suggestions:</strong> {len(perf_data.get('index_suggestions', []))}</p>
            </div>
            """)
        
        return '\n'.join(sections)
    
    def _generate_text_report(self, results: Dict[str, Any]) -> str:
        """Generate plain text report"""
        lines = [
            "=" * 60,
            "SQL ANALYSIS REPORT",
            "=" * 60,
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
        ]
        
        # Add sections for each analysis type
        for section_name, section_data in results.items():
            lines.append(f"\n{section_name.upper().replace('_', ' ')}")
            lines.append("-" * 40)
            
            if isinstance(section_data, dict):
                for key, value in section_data.items():
                    lines.append(f"{key}: {value}")
            else:
                lines.append(str(section_data))
        
        return '\n'.join(lines)
    
    def _write_csv_data(self, writer, results: Dict[str, Any]):
        """Write results data to CSV"""
        for category, data in results.items():
            if isinstance(data, dict):
                for key, value in data.items():
                    writer.writerow([category, key, str(value), ''])
            elif isinstance(data, list):
                for i, item in enumerate(data):
                    writer.writerow([category, f'Item {i+1}', str(item), ''])
            else:
                writer.writerow([category, 'Value', str(data), ''])
    
    def _generate_xml_report(self, results: Dict[str, Any]) -> str:
        """Generate XML report"""
        root = ET.Element('sql_analysis_report')
        root.set('generated', datetime.now().isoformat())
        
        for section_name, section_data in results.items():
            section_elem = ET.SubElement(root, section_name)
            
            if isinstance(section_data, dict):
                for key, value in section_data.items():
                    item_elem = ET.SubElement(section_elem, key)
                    item_elem.text = str(value)
            elif isinstance(section_data, list):
                for i, item in enumerate(section_data):
                    item_elem = ET.SubElement(section_elem, f'item_{i}')
                    item_elem.text = str(item)
            else:
                section_elem.text = str(section_data)
        
        # Pretty print XML
        rough_string = ET.tostring(root, 'unicode')
        reparsed = minidom.parseString(rough_string)
        return reparsed.toprettyxml(indent="  ")
    
    def _generate_markdown_report(self, results: Dict[str, Any]) -> str:
        """Generate Markdown report"""
        lines = [
            "# 📊 SQL Analysis Report",
            "",
            f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
        ]
        
        for section_name, section_data in results.items():
            lines.append(f"## {section_name.replace('_', ' ').title()}")
            lines.append("")
            
            if isinstance(section_data, dict):
                for key, value in section_data.items():
                    lines.append(f"- **{key}:** {value}")
            elif isinstance(section_data, list):
                for item in section_data:
                    lines.append(f"- {item}")
            else:
                lines.append(str(section_data))
            
            lines.append("")
        
        return '\n'.join(lines)
    
    def _generate_sql_script(self, results: Dict[str, Any]) -> str:
        """Generate SQL script with analysis results as comments"""
        lines = [
            "-- SQL ANALYSIS RESULTS",
            "-- Generated: " + datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "--",
        ]
        
        for section_name, section_data in results.items():
            lines.append(f"-- {section_name.upper().replace('_', ' ')}")
            lines.append("-- " + "-" * 40)
            
            if isinstance(section_data, dict):
                for key, value in section_data.items():
                    lines.append(f"-- {key}: {value}")
            elif isinstance(section_data, list):
                for item in section_data:
                    lines.append(f"-- {item}")
            else:
                lines.append(f"-- {section_data}")
            
            lines.append("--")
        
        lines.append("")
        lines.append("-- End of analysis results")
        
        return '\n'.join(lines)
