#!/usr/bin/env python3
"""
SQL ANALYZER ENTERPRISE - COMPREHENSIVE REPORTING SYSTEM
Generates detailed analysis reports, analytics dashboards, and export functionality
"""

import os
import json
import csv
import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
import logging

class AnalysisReportGenerator:
    """Comprehensive reporting system for SQL analysis results."""
    
    def __init__(self, output_dir: str = "conclusions_arc"):
        self.output_dir = Path(output_dir)
        self.reports_dir = self.output_dir / "reports"
        self.analytics_dir = self.output_dir / "analytics"
        self.exports_dir = self.output_dir / "exports"
        self.logs_dir = self.output_dir / "logs"
        
        # Create directories
        for dir_path in [self.reports_dir, self.analytics_dir, self.exports_dir, self.logs_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)
        
        # Setup logging
        self.setup_logging()
        
    def setup_logging(self):
        """Setup comprehensive logging system."""
        log_file = self.logs_dir / f"analysis_reports_{datetime.datetime.now().strftime('%Y%m%d')}.log"
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def generate_comprehensive_report(self, analysis_data: Dict[str, Any]) -> str:
        """Generate comprehensive analysis report."""
        try:
            timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
            report_file = self.reports_dir / f"comprehensive_analysis_{timestamp}.html"
            
            # Generate HTML report
            html_content = self._generate_html_report(analysis_data)
            
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            self.logger.info(f"Comprehensive report generated: {report_file}")
            return str(report_file)
            
        except Exception as e:
            self.logger.error(f"Error generating comprehensive report: {e}")
            raise
    
    def _generate_html_report(self, data: Dict[str, Any]) -> str:
        """Generate HTML report content."""
        return f"""
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SQL Analysis Report - {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</title>
    <style>
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }}
        .header {{ text-align: center; margin-bottom: 40px; padding-bottom: 20px; border-bottom: 3px solid #007bff; }}
        .header h1 {{ color: #007bff; margin: 0; font-size: 2.5em; }}
        .header p {{ color: #666; margin: 10px 0 0 0; font-size: 1.1em; }}
        .section {{ margin: 30px 0; }}
        .section h2 {{ color: #333; border-left: 4px solid #007bff; padding-left: 15px; }}
        .metrics {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin: 20px 0; }}
        .metric-card {{ background: #f8f9fa; padding: 20px; border-radius: 8px; border-left: 4px solid #28a745; }}
        .metric-value {{ font-size: 2em; font-weight: bold; color: #28a745; }}
        .metric-label {{ color: #666; font-size: 0.9em; text-transform: uppercase; }}
        .table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
        .table th, .table td {{ padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }}
        .table th {{ background: #007bff; color: white; }}
        .status-success {{ color: #28a745; font-weight: bold; }}
        .status-warning {{ color: #ffc107; font-weight: bold; }}
        .status-error {{ color: #dc3545; font-weight: bold; }}
        .footer {{ text-align: center; margin-top: 40px; padding-top: 20px; border-top: 1px solid #ddd; color: #666; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 SQL Analysis Report</h1>
            <p>Comprehensive Analysis Results - Generated on {datetime.datetime.now().strftime('%Y-%m-%d at %H:%M:%S')}</p>
        </div>
        
        <div class="section">
            <h2>📈 Executive Summary</h2>
            <div class="metrics">
                <div class="metric-card">
                    <div class="metric-value">{data.get('total_files', 0)}</div>
                    <div class="metric-label">Files Analyzed</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{data.get('total_lines', 0):,}</div>
                    <div class="metric-label">Lines of Code</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{data.get('errors_found', 0)}</div>
                    <div class="metric-label">Errors Found</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{data.get('success_rate', 100):.1f}%</div>
                    <div class="metric-label">Success Rate</div>
                </div>
            </div>
        </div>
        
        <div class="section">
            <h2>🔍 Analysis Details</h2>
            <table class="table">
                <thead>
                    <tr>
                        <th>File Name</th>
                        <th>Size</th>
                        <th>Status</th>
                        <th>Errors</th>
                        <th>Processing Time</th>
                    </tr>
                </thead>
                <tbody>
                    {self._generate_file_rows(data.get('files', []))}
                </tbody>
            </table>
        </div>
        
        <div class="section">
            <h2>⚠️ Issues Summary</h2>
            <div class="metrics">
                <div class="metric-card">
                    <div class="metric-value" style="color: #dc3545;">{data.get('critical_errors', 0)}</div>
                    <div class="metric-label">Critical Errors</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value" style="color: #ffc107;">{data.get('warnings', 0)}</div>
                    <div class="metric-label">Warnings</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value" style="color: #17a2b8;">{data.get('suggestions', 0)}</div>
                    <div class="metric-label">Suggestions</div>
                </div>
            </div>
        </div>
        
        <div class="footer">
            <p>Generated by SQL Analyzer Enterprise | © 2025 | Report ID: {data.get('report_id', 'N/A')}</p>
        </div>
    </div>
</body>
</html>
        """
    
    def _generate_file_rows(self, files: List[Dict]) -> str:
        """Generate table rows for file analysis results."""
        if not files:
            return '<tr><td colspan="5" style="text-align: center; color: #666;">No files analyzed</td></tr>'
        
        rows = []
        for file_data in files:
            status_class = "status-success" if file_data.get('status') == 'success' else "status-error"
            rows.append(f"""
                <tr>
                    <td>{file_data.get('name', 'Unknown')}</td>
                    <td>{file_data.get('size', 'N/A')}</td>
                    <td class="{status_class}">{file_data.get('status', 'Unknown').title()}</td>
                    <td>{file_data.get('errors', 0)}</td>
                    <td>{file_data.get('processing_time', 'N/A')}</td>
                </tr>
            """)
        return ''.join(rows)
    
    def generate_analytics_dashboard(self, analysis_data: Dict[str, Any]) -> str:
        """Generate analytics dashboard data."""
        try:
            timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
            analytics_file = self.analytics_dir / f"analytics_dashboard_{timestamp}.json"
            
            dashboard_data = {
                "timestamp": datetime.datetime.now().isoformat(),
                "summary": {
                    "total_files": analysis_data.get('total_files', 0),
                    "total_lines": analysis_data.get('total_lines', 0),
                    "success_rate": analysis_data.get('success_rate', 100),
                    "processing_time": analysis_data.get('total_processing_time', 0)
                },
                "charts": {
                    "file_types": self._analyze_file_types(analysis_data.get('files', [])),
                    "error_distribution": self._analyze_error_distribution(analysis_data.get('files', [])),
                    "processing_timeline": self._analyze_processing_timeline(analysis_data.get('files', []))
                },
                "recommendations": self._generate_recommendations(analysis_data)
            }
            
            with open(analytics_file, 'w', encoding='utf-8') as f:
                json.dump(dashboard_data, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Analytics dashboard generated: {analytics_file}")
            return str(analytics_file)
            
        except Exception as e:
            self.logger.error(f"Error generating analytics dashboard: {e}")
            raise
    
    def _analyze_file_types(self, files: List[Dict]) -> Dict[str, int]:
        """Analyze file type distribution."""
        file_types = {}
        for file_data in files:
            ext = file_data.get('extension', 'unknown').lower()
            file_types[ext] = file_types.get(ext, 0) + 1
        return file_types
    
    def _analyze_error_distribution(self, files: List[Dict]) -> Dict[str, int]:
        """Analyze error distribution across files."""
        error_types = {"syntax": 0, "semantic": 0, "performance": 0, "security": 0}
        for file_data in files:
            for error_type in file_data.get('error_types', []):
                if error_type in error_types:
                    error_types[error_type] += 1
        return error_types
    
    def _analyze_processing_timeline(self, files: List[Dict]) -> List[Dict]:
        """Analyze processing timeline."""
        timeline = []
        for file_data in files:
            timeline.append({
                "file": file_data.get('name', 'Unknown'),
                "start_time": file_data.get('start_time', ''),
                "end_time": file_data.get('end_time', ''),
                "duration": file_data.get('processing_time', 0)
            })
        return sorted(timeline, key=lambda x: x.get('start_time', ''))
    
    def _generate_recommendations(self, analysis_data: Dict[str, Any]) -> List[str]:
        """Generate improvement recommendations."""
        recommendations = []
        
        if analysis_data.get('errors_found', 0) > 0:
            recommendations.append("Review and fix identified SQL syntax errors")
        
        if analysis_data.get('success_rate', 100) < 90:
            recommendations.append("Improve code quality to achieve higher success rates")
        
        if analysis_data.get('total_processing_time', 0) > 300:  # 5 minutes
            recommendations.append("Consider optimizing large files for better performance")
        
        recommendations.append("Regular code reviews and automated testing recommended")
        
        return recommendations
    
    def export_to_csv(self, analysis_data: Dict[str, Any]) -> str:
        """Export analysis results to CSV format."""
        try:
            timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
            csv_file = self.exports_dir / f"analysis_export_{timestamp}.csv"
            
            with open(csv_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                
                # Write header
                writer.writerow(['File Name', 'Size', 'Status', 'Errors', 'Processing Time', 'Success Rate'])
                
                # Write data
                for file_data in analysis_data.get('files', []):
                    writer.writerow([
                        file_data.get('name', 'Unknown'),
                        file_data.get('size', 'N/A'),
                        file_data.get('status', 'Unknown'),
                        file_data.get('errors', 0),
                        file_data.get('processing_time', 'N/A'),
                        f"{file_data.get('success_rate', 100):.1f}%"
                    ])
            
            self.logger.info(f"CSV export generated: {csv_file}")
            return str(csv_file)
            
        except Exception as e:
            self.logger.error(f"Error exporting to CSV: {e}")
            raise

if __name__ == "__main__":
    # Example usage
    sample_data = {
        "total_files": 5,
        "total_lines": 15000,
        "errors_found": 3,
        "success_rate": 94.2,
        "total_processing_time": 45.6,
        "files": [
            {"name": "schema.sql", "size": "2.3 MB", "status": "success", "errors": 0, "processing_time": "12.3s"},
            {"name": "queries.sql", "size": "1.8 MB", "status": "success", "errors": 1, "processing_time": "8.7s"},
            {"name": "procedures.sql", "size": "3.1 MB", "status": "error", "errors": 2, "processing_time": "15.2s"}
        ]
    }
    
    generator = AnalysisReportGenerator()
    
    # Generate reports
    html_report = generator.generate_comprehensive_report(sample_data)
    analytics_dashboard = generator.generate_analytics_dashboard(sample_data)
    csv_export = generator.export_to_csv(sample_data)
    
    print(f"✅ Reports generated successfully:")
    print(f"   📄 HTML Report: {html_report}")
    print(f"   📊 Analytics Dashboard: {analytics_dashboard}")
    print(f"   📋 CSV Export: {csv_export}")
