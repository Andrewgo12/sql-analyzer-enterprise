#!/usr/bin/env python3
"""
SQL ANALYZER ENTERPRISE - ANALYTICS DASHBOARD GENERATOR
Creates interactive analytics dashboards with charts and visualizations
"""

import json
import datetime
from pathlib import Path
from typing import Dict, List, Any

class DashboardGenerator:
    """Generate interactive analytics dashboards."""
    
    def __init__(self, output_dir: str = "conclusions_arc/analytics"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def generate_interactive_dashboard(self, analytics_data: Dict[str, Any]) -> str:
        """Generate interactive HTML dashboard with charts."""
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        dashboard_file = self.output_dir / f"interactive_dashboard_{timestamp}.html"
        
        html_content = self._create_dashboard_html(analytics_data)
        
        with open(dashboard_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return str(dashboard_file)
    
    def _create_dashboard_html(self, data: Dict[str, Any]) -> str:
        """Create complete HTML dashboard with interactive charts."""
        return f"""
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SQL Analyzer - Analytics Dashboard</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #f5f7fa; }}
        .dashboard {{ max-width: 1400px; margin: 0 auto; padding: 20px; }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 15px; margin-bottom: 30px; text-align: center; }}
        .header h1 {{ font-size: 2.5em; margin-bottom: 10px; }}
        .header p {{ font-size: 1.1em; opacity: 0.9; }}
        .metrics-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin-bottom: 30px; }}
        .metric-card {{ background: white; padding: 25px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); text-align: center; }}
        .metric-value {{ font-size: 2.5em; font-weight: bold; margin-bottom: 5px; }}
        .metric-label {{ color: #666; font-size: 0.9em; text-transform: uppercase; letter-spacing: 1px; }}
        .charts-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(400px, 1fr)); gap: 30px; margin-bottom: 30px; }}
        .chart-container {{ background: white; padding: 25px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }}
        .chart-title {{ font-size: 1.3em; font-weight: 600; margin-bottom: 20px; color: #333; text-align: center; }}
        .recommendations {{ background: white; padding: 25px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }}
        .recommendations h3 {{ color: #333; margin-bottom: 15px; }}
        .recommendation {{ background: #f8f9fa; padding: 15px; margin: 10px 0; border-left: 4px solid #007bff; border-radius: 5px; }}
        .footer {{ text-align: center; margin-top: 40px; color: #666; }}
        .success {{ color: #28a745; }}
        .warning {{ color: #ffc107; }}
        .error {{ color: #dc3545; }}
        .info {{ color: #17a2b8; }}
    </style>
</head>
<body>
    <div class="dashboard">
        <div class="header">
            <h1>📊 SQL Analytics Dashboard</h1>
            <p>Comprehensive Analysis Overview - Generated on {datetime.datetime.now().strftime('%Y-%m-%d at %H:%M:%S')}</p>
        </div>
        
        <div class="metrics-grid">
            <div class="metric-card">
                <div class="metric-value success">{data.get('summary', {}).get('total_files', 0)}</div>
                <div class="metric-label">Files Analyzed</div>
            </div>
            <div class="metric-card">
                <div class="metric-value info">{data.get('summary', {}).get('total_lines', 0):,}</div>
                <div class="metric-label">Lines of Code</div>
            </div>
            <div class="metric-card">
                <div class="metric-value success">{data.get('summary', {}).get('success_rate', 100):.1f}%</div>
                <div class="metric-label">Success Rate</div>
            </div>
            <div class="metric-card">
                <div class="metric-value info">{data.get('summary', {}).get('processing_time', 0):.1f}s</div>
                <div class="metric-label">Processing Time</div>
            </div>
        </div>
        
        <div class="charts-grid">
            <div class="chart-container">
                <div class="chart-title">📁 File Types Distribution</div>
                <canvas id="fileTypesChart"></canvas>
            </div>
            
            <div class="chart-container">
                <div class="chart-title">⚠️ Error Distribution</div>
                <canvas id="errorDistributionChart"></canvas>
            </div>
            
            <div class="chart-container">
                <div class="chart-title">⏱️ Processing Timeline</div>
                <canvas id="processingTimelineChart"></canvas>
            </div>
            
            <div class="chart-container">
                <div class="chart-title">📈 Success Rate Trend</div>
                <canvas id="successRateChart"></canvas>
            </div>
        </div>
        
        <div class="recommendations">
            <h3>💡 Recommendations</h3>
            {self._generate_recommendations_html(data.get('recommendations', []))}
        </div>
        
        <div class="footer">
            <p>Generated by SQL Analyzer Enterprise | © 2025 | Dashboard ID: {data.get('dashboard_id', 'N/A')}</p>
        </div>
    </div>
    
    <script>
        // Chart.js configuration
        Chart.defaults.font.family = 'Segoe UI, Tahoma, Geneva, Verdana, sans-serif';
        Chart.defaults.color = '#666';
        
        // File Types Chart
        const fileTypesCtx = document.getElementById('fileTypesChart').getContext('2d');
        new Chart(fileTypesCtx, {{
            type: 'doughnut',
            data: {{
                labels: {json.dumps(list(data.get('charts', {}).get('file_types', {}).keys()))},
                datasets: [{{
                    data: {json.dumps(list(data.get('charts', {}).get('file_types', {}).values()))},
                    backgroundColor: ['#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF', '#FF9F40'],
                    borderWidth: 2,
                    borderColor: '#fff'
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{
                    legend: {{
                        position: 'bottom',
                        labels: {{
                            padding: 20,
                            usePointStyle: true
                        }}
                    }}
                }}
            }}
        }});
        
        // Error Distribution Chart
        const errorDistCtx = document.getElementById('errorDistributionChart').getContext('2d');
        new Chart(errorDistCtx, {{
            type: 'bar',
            data: {{
                labels: {json.dumps(list(data.get('charts', {}).get('error_distribution', {}).keys()))},
                datasets: [{{
                    label: 'Error Count',
                    data: {json.dumps(list(data.get('charts', {}).get('error_distribution', {}).values()))},
                    backgroundColor: ['#FF6384', '#FF9F40', '#FFCE56', '#4BC0C0'],
                    borderColor: ['#FF6384', '#FF9F40', '#FFCE56', '#4BC0C0'],
                    borderWidth: 2
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                scales: {{
                    y: {{
                        beginAtZero: true,
                        ticks: {{
                            stepSize: 1
                        }}
                    }}
                }},
                plugins: {{
                    legend: {{
                        display: false
                    }}
                }}
            }}
        }});
        
        // Processing Timeline Chart
        const timelineCtx = document.getElementById('processingTimelineChart').getContext('2d');
        const timelineData = {json.dumps(data.get('charts', {}).get('processing_timeline', []))};
        new Chart(timelineCtx, {{
            type: 'line',
            data: {{
                labels: timelineData.map(item => item.file),
                datasets: [{{
                    label: 'Processing Time (seconds)',
                    data: timelineData.map(item => item.duration),
                    borderColor: '#36A2EB',
                    backgroundColor: 'rgba(54, 162, 235, 0.1)',
                    borderWidth: 3,
                    fill: true,
                    tension: 0.4
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                scales: {{
                    y: {{
                        beginAtZero: true
                    }}
                }},
                plugins: {{
                    legend: {{
                        display: false
                    }}
                }}
            }}
        }});
        
        // Success Rate Chart
        const successRateCtx = document.getElementById('successRateChart').getContext('2d');
        new Chart(successRateCtx, {{
            type: 'gauge',
            data: {{
                datasets: [{{
                    data: [{data.get('summary', {}).get('success_rate', 100)}],
                    backgroundColor: ['#28a745'],
                    borderWidth: 0
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                circumference: 180,
                rotation: 270,
                cutout: '80%',
                plugins: {{
                    legend: {{
                        display: false
                    }},
                    tooltip: {{
                        enabled: false
                    }}
                }}
            }}
        }});
    </script>
</body>
</html>
        """
    
    def _generate_recommendations_html(self, recommendations: List[str]) -> str:
        """Generate HTML for recommendations section."""
        if not recommendations:
            return '<div class="recommendation">No specific recommendations at this time. System is performing well!</div>'
        
        html = ""
        for i, rec in enumerate(recommendations, 1):
            html += f'<div class="recommendation"><strong>{i}.</strong> {rec}</div>'
        
        return html

if __name__ == "__main__":
    # Example usage
    sample_analytics = {
        "summary": {
            "total_files": 8,
            "total_lines": 25000,
            "success_rate": 92.5,
            "processing_time": 67.3
        },
        "charts": {
            "file_types": {"sql": 5, "txt": 2, "pdf": 1},
            "error_distribution": {"syntax": 3, "semantic": 1, "performance": 2, "security": 0},
            "processing_timeline": [
                {"file": "schema.sql", "duration": 12.3},
                {"file": "queries.sql", "duration": 8.7},
                {"file": "procedures.sql", "duration": 15.2}
            ]
        },
        "recommendations": [
            "Review and fix identified SQL syntax errors",
            "Consider optimizing large files for better performance",
            "Regular code reviews recommended"
        ]
    }
    
    generator = DashboardGenerator()
    dashboard_file = generator.generate_interactive_dashboard(sample_analytics)
    print(f"✅ Interactive dashboard generated: {dashboard_file}")
