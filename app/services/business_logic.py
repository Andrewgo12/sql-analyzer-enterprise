#!/usr/bin/env python3
"""
BUSINESS LOGIC LAYER
Enterprise business rules and domain logic for SQL analysis
"""

import logging
import time
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass

from app.models.analysis_models import (
    AnalysisResult, SQLError, SecurityVulnerability, PerformanceIssue,
    ErrorSeverity, DatabaseType
)
from app.utils.helpers import LoggingHelper

@dataclass
class QualityThresholds:
    """Quality assessment thresholds"""
    excellent: int = 90
    good: int = 75
    fair: int = 60
    poor: int = 40

@dataclass
class PerformanceThresholds:
    """Performance assessment thresholds (in seconds)"""
    excellent: float = 0.5
    good: float = 1.0
    fair: float = 2.0
    poor: float = 5.0

@dataclass
class SecurityRiskLevels:
    """Security risk assessment levels"""
    critical_threshold: int = 1  # Any critical vulnerability
    high_threshold: int = 1      # Any high-risk vulnerability
    medium_threshold: int = 5    # More than 5 medium-risk vulnerabilities

class QualityAssessmentEngine:
    """Enterprise quality assessment with business rules"""
    
    def __init__(self):
        self.logger = LoggingHelper.setup_logger('quality_assessment')
        self.quality_thresholds = QualityThresholds()
        self.performance_thresholds = PerformanceThresholds()
        self.security_risk_levels = SecurityRiskLevels()
    
    def assess_overall_quality(self, result: AnalysisResult) -> Dict[str, Any]:
        """Comprehensive quality assessment with business rules"""
        try:
            # Calculate individual scores
            syntax_score = self._assess_syntax_quality(result.syntax_errors)
            semantic_score = self._assess_semantic_quality(result.semantic_errors)
            security_score = self._assess_security_quality(result.security_vulnerabilities)
            performance_score = self._assess_performance_quality(result.performance_issues)
            complexity_score = self._assess_complexity_quality(result.complexity_score)
            
            # Calculate weighted overall score
            overall_score = self._calculate_weighted_score({
                'syntax': (syntax_score, 0.25),
                'semantic': (semantic_score, 0.20),
                'security': (security_score, 0.25),
                'performance': (performance_score, 0.20),
                'complexity': (complexity_score, 0.10)
            })
            
            # Determine quality level
            quality_level = self._determine_quality_level(overall_score)
            
            # Generate quality recommendations
            recommendations = self._generate_quality_recommendations(result)
            
            # Calculate improvement potential
            improvement_potential = self._calculate_improvement_potential(result)
            
            return {
                'overall_score': overall_score,
                'quality_level': quality_level,
                'component_scores': {
                    'syntax': syntax_score,
                    'semantic': semantic_score,
                    'security': security_score,
                    'performance': performance_score,
                    'complexity': complexity_score
                },
                'recommendations': recommendations,
                'improvement_potential': improvement_potential,
                'assessment_timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Quality assessment failed: {str(e)}")
            return {
                'overall_score': 0,
                'quality_level': 'unknown',
                'error': str(e)
            }
    
    def assess_security_posture(self, vulnerabilities: List[SecurityVulnerability]) -> Dict[str, Any]:
        """Comprehensive security posture assessment"""
        try:
            # Count vulnerabilities by severity
            severity_counts = {
                'critical': 0,
                'high': 0,
                'medium': 0,
                'low': 0
            }
            
            for vuln in vulnerabilities:
                severity_counts[vuln.risk_level.value] += 1
            
            # Assess overall risk level
            overall_risk = self._determine_security_risk_level(severity_counts)
            
            # Calculate security score
            security_score = self._calculate_security_score(severity_counts)
            
            # Generate security recommendations
            security_recommendations = self._generate_security_recommendations(vulnerabilities)
            
            # Identify critical issues
            critical_issues = [v for v in vulnerabilities if v.risk_level == ErrorSeverity.CRITICAL]
            
            # Calculate remediation priority
            remediation_priority = self._calculate_remediation_priority(vulnerabilities)
            
            return {
                'overall_risk': overall_risk,
                'security_score': security_score,
                'severity_breakdown': severity_counts,
                'total_vulnerabilities': len(vulnerabilities),
                'critical_issues': len(critical_issues),
                'recommendations': security_recommendations,
                'remediation_priority': remediation_priority,
                'compliance_status': self._assess_compliance_status(vulnerabilities)
            }
            
        except Exception as e:
            self.logger.error(f"Security assessment failed: {str(e)}")
            return {
                'overall_risk': 'unknown',
                'security_score': 0,
                'error': str(e)
            }
    
    def assess_performance_profile(self, issues: List[PerformanceIssue], 
                                 processing_time: float) -> Dict[str, Any]:
        """Comprehensive performance profile assessment"""
        try:
            # Categorize performance issues
            issue_categories = self._categorize_performance_issues(issues)
            
            # Calculate performance score
            performance_score = self._calculate_performance_score_detailed(issues)
            
            # Assess processing time
            processing_assessment = self._assess_processing_time(processing_time)
            
            # Calculate optimization potential
            optimization_potential = self._calculate_optimization_potential(issues)
            
            # Generate performance recommendations
            performance_recommendations = self._generate_performance_recommendations(issues)
            
            # Identify bottlenecks
            bottlenecks = self._identify_performance_bottlenecks(issues)
            
            return {
                'performance_score': performance_score,
                'processing_assessment': processing_assessment,
                'issue_categories': issue_categories,
                'optimization_potential': optimization_potential,
                'recommendations': performance_recommendations,
                'bottlenecks': bottlenecks,
                'total_issues': len(issues),
                'high_impact_issues': len([i for i in issues if i.impact == 'high'])
            }
            
        except Exception as e:
            self.logger.error(f"Performance assessment failed: {str(e)}")
            return {
                'performance_score': 0,
                'processing_assessment': 'unknown',
                'error': str(e)
            }
    
    def _assess_syntax_quality(self, syntax_errors: List[SQLError]) -> int:
        """Assess syntax quality based on errors"""
        if not syntax_errors:
            return 100
        
        base_score = 100
        for error in syntax_errors:
            if error.severity == ErrorSeverity.CRITICAL:
                base_score -= 20
            elif error.severity == ErrorSeverity.HIGH:
                base_score -= 15
            elif error.severity == ErrorSeverity.MEDIUM:
                base_score -= 10
            else:
                base_score -= 5
        
        return max(0, base_score)
    
    def _assess_semantic_quality(self, semantic_errors: List[SQLError]) -> int:
        """Assess semantic quality based on errors"""
        if not semantic_errors:
            return 100
        
        base_score = 100
        for error in semantic_errors:
            if error.severity == ErrorSeverity.HIGH:
                base_score -= 12
            elif error.severity == ErrorSeverity.MEDIUM:
                base_score -= 8
            else:
                base_score -= 4
        
        return max(0, base_score)
    
    def _assess_security_quality(self, vulnerabilities: List[SecurityVulnerability]) -> int:
        """Assess security quality based on vulnerabilities"""
        if not vulnerabilities:
            return 100
        
        base_score = 100
        for vuln in vulnerabilities:
            if vuln.risk_level == ErrorSeverity.CRITICAL:
                base_score -= 25
            elif vuln.risk_level == ErrorSeverity.HIGH:
                base_score -= 15
            elif vuln.risk_level == ErrorSeverity.MEDIUM:
                base_score -= 8
            else:
                base_score -= 3
        
        return max(0, base_score)
    
    def _assess_performance_quality(self, issues: List[PerformanceIssue]) -> int:
        """Assess performance quality based on issues"""
        if not issues:
            return 100
        
        base_score = 100
        for issue in issues:
            if issue.impact == 'high':
                base_score -= 15
            elif issue.impact == 'medium':
                base_score -= 8
            else:
                base_score -= 4
        
        return max(0, base_score)
    
    def _assess_complexity_quality(self, complexity_score: int) -> int:
        """Assess quality based on complexity score"""
        if complexity_score <= 25:
            return 100
        elif complexity_score <= 50:
            return 80
        elif complexity_score <= 75:
            return 60
        else:
            return 40
    
    def _calculate_weighted_score(self, scores: Dict[str, Tuple[int, float]]) -> int:
        """Calculate weighted overall score"""
        total_score = 0
        total_weight = 0
        
        for component, (score, weight) in scores.items():
            total_score += score * weight
            total_weight += weight
        
        return int(total_score / total_weight) if total_weight > 0 else 0
    
    def _determine_quality_level(self, score: int) -> str:
        """Determine quality level based on score"""
        if score >= self.quality_thresholds.excellent:
            return "Excellent"
        elif score >= self.quality_thresholds.good:
            return "Good"
        elif score >= self.quality_thresholds.fair:
            return "Fair"
        else:
            return "Poor"
    
    def _determine_security_risk_level(self, severity_counts: Dict[str, int]) -> str:
        """Determine overall security risk level"""
        if severity_counts['critical'] >= self.security_risk_levels.critical_threshold:
            return "Critical"
        elif severity_counts['high'] >= self.security_risk_levels.high_threshold:
            return "High"
        elif severity_counts['medium'] >= self.security_risk_levels.medium_threshold:
            return "Medium"
        elif sum(severity_counts.values()) > 0:
            return "Low"
        else:
            return "Minimal"
    
    def _calculate_security_score(self, severity_counts: Dict[str, int]) -> int:
        """Calculate security score based on vulnerability counts"""
        base_score = 100
        
        base_score -= severity_counts['critical'] * 25
        base_score -= severity_counts['high'] * 15
        base_score -= severity_counts['medium'] * 8
        base_score -= severity_counts['low'] * 3
        
        return max(0, base_score)
    
    def _generate_quality_recommendations(self, result: AnalysisResult) -> List[str]:
        """Generate quality improvement recommendations"""
        recommendations = []
        
        if result.syntax_errors:
            recommendations.append("Corregir errores de sintaxis para mejorar la calidad del código")
        
        if result.semantic_errors:
            recommendations.append("Revisar advertencias semánticas para optimizar la lógica")
        
        if result.security_vulnerabilities:
            recommendations.append("Abordar vulnerabilidades de seguridad identificadas")
        
        if result.performance_issues:
            recommendations.append("Implementar optimizaciones de rendimiento sugeridas")
        
        if result.complexity_score > 75:
            recommendations.append("Simplificar consultas complejas para mejorar mantenibilidad")
        
        return recommendations
    
    def _calculate_improvement_potential(self, result: AnalysisResult) -> Dict[str, Any]:
        """Calculate improvement potential across different areas"""
        potential = {
            'syntax': 0,
            'security': 0,
            'performance': 0,
            'overall': 0
        }
        
        # Syntax improvement potential
        if result.syntax_errors:
            auto_fixable = sum(1 for e in result.syntax_errors if e.auto_fixable)
            potential['syntax'] = (auto_fixable / len(result.syntax_errors)) * 100
        
        # Security improvement potential
        if result.security_vulnerabilities:
            high_impact = sum(1 for v in result.security_vulnerabilities 
                            if v.risk_level in [ErrorSeverity.CRITICAL, ErrorSeverity.HIGH])
            potential['security'] = (high_impact / len(result.security_vulnerabilities)) * 100
        
        # Performance improvement potential
        if result.performance_issues:
            high_impact = sum(1 for i in result.performance_issues if i.impact == 'high')
            potential['performance'] = (high_impact / len(result.performance_issues)) * 100
        
        # Overall improvement potential
        potential['overall'] = (potential['syntax'] + potential['security'] + potential['performance']) / 3
        
        return potential
    
    def _generate_security_recommendations(self, vulnerabilities: List[SecurityVulnerability]) -> List[str]:
        """Generate security-specific recommendations"""
        recommendations = []
        vuln_types = set(v.vulnerability_type for v in vulnerabilities)
        
        if 'sql_injection' in vuln_types:
            recommendations.append("Implementar consultas parametrizadas para prevenir inyección SQL")
        
        if 'hardcoded_credentials' in vuln_types:
            recommendations.append("Eliminar credenciales hardcodeadas y usar gestión segura de secretos")
        
        if 'information_disclosure' in vuln_types:
            recommendations.append("Revisar y restringir la exposición de información sensible")
        
        return recommendations
    
    def _calculate_remediation_priority(self, vulnerabilities: List[SecurityVulnerability]) -> List[Dict[str, Any]]:
        """Calculate remediation priority for vulnerabilities"""
        priority_list = []
        
        for vuln in vulnerabilities:
            priority_score = 0
            
            # Risk level weight
            if vuln.risk_level == ErrorSeverity.CRITICAL:
                priority_score += 100
            elif vuln.risk_level == ErrorSeverity.HIGH:
                priority_score += 75
            elif vuln.risk_level == ErrorSeverity.MEDIUM:
                priority_score += 50
            else:
                priority_score += 25
            
            # Vulnerability type weight
            if vuln.vulnerability_type == 'sql_injection':
                priority_score += 20
            elif vuln.vulnerability_type == 'hardcoded_credentials':
                priority_score += 15
            
            priority_list.append({
                'vulnerability_id': vuln.id,
                'priority_score': priority_score,
                'risk_level': vuln.risk_level.value,
                'type': vuln.vulnerability_type,
                'description': vuln.description
            })
        
        # Sort by priority score (highest first)
        priority_list.sort(key=lambda x: x['priority_score'], reverse=True)
        
        return priority_list
    
    def _assess_compliance_status(self, vulnerabilities: List[SecurityVulnerability]) -> Dict[str, Any]:
        """Assess compliance status based on vulnerabilities"""
        owasp_categories = set(v.owasp_category for v in vulnerabilities if v.owasp_category)
        cwe_ids = set(v.cwe_id for v in vulnerabilities if v.cwe_id)
        
        return {
            'owasp_violations': len(owasp_categories),
            'cwe_violations': len(cwe_ids),
            'compliance_score': max(0, 100 - len(vulnerabilities) * 5),
            'affected_categories': list(owasp_categories),
            'affected_cwe_ids': list(cwe_ids)
        }
    
    def _categorize_performance_issues(self, issues: List[PerformanceIssue]) -> Dict[str, int]:
        """Categorize performance issues by type"""
        categories = {}
        
        for issue in issues:
            issue_type = issue.issue_type
            categories[issue_type] = categories.get(issue_type, 0) + 1
        
        return categories
    
    def _calculate_performance_score_detailed(self, issues: List[PerformanceIssue]) -> int:
        """Calculate detailed performance score"""
        if not issues:
            return 100
        
        base_score = 100
        
        for issue in issues:
            if issue.impact == 'high':
                base_score -= 15
            elif issue.impact == 'medium':
                base_score -= 8
            else:
                base_score -= 4
        
        return max(0, base_score)
    
    def _assess_processing_time(self, processing_time: float) -> Dict[str, Any]:
        """Assess processing time performance"""
        if processing_time <= self.performance_thresholds.excellent:
            level = "Excellent"
        elif processing_time <= self.performance_thresholds.good:
            level = "Good"
        elif processing_time <= self.performance_thresholds.fair:
            level = "Fair"
        else:
            level = "Poor"
        
        return {
            'level': level,
            'time': processing_time,
            'meets_target': processing_time <= 2.0
        }
    
    def _calculate_optimization_potential(self, issues: List[PerformanceIssue]) -> str:
        """Calculate optimization potential level"""
        if not issues:
            return "Minimal"
        
        high_impact_count = sum(1 for issue in issues if issue.impact == 'high')
        
        if high_impact_count >= 5:
            return "Very High"
        elif high_impact_count >= 3:
            return "High"
        elif len(issues) >= 5:
            return "Medium"
        else:
            return "Low"
    
    def _generate_performance_recommendations(self, issues: List[PerformanceIssue]) -> List[str]:
        """Generate performance-specific recommendations"""
        recommendations = []
        issue_types = set(issue.issue_type for issue in issues)
        
        if 'select_star' in issue_types:
            recommendations.append("Especificar columnas específicas en lugar de SELECT *")
        
        if 'missing_index' in issue_types:
            recommendations.append("Agregar índices en columnas frecuentemente consultadas")
        
        if 'leading_wildcard' in issue_types:
            recommendations.append("Evitar patrones LIKE con comodines al inicio")
        
        if 'cartesian_product' in issue_types:
            recommendations.append("Revisar JOINs para evitar productos cartesianos")
        
        return recommendations
    
    def _identify_performance_bottlenecks(self, issues: List[PerformanceIssue]) -> List[Dict[str, Any]]:
        """Identify performance bottlenecks"""
        bottlenecks = []
        
        # Group issues by line number to identify hotspots
        line_issues = {}
        for issue in issues:
            line = issue.line_number
            if line not in line_issues:
                line_issues[line] = []
            line_issues[line].append(issue)
        
        # Identify lines with multiple high-impact issues
        for line, line_issue_list in line_issues.items():
            high_impact_count = sum(1 for issue in line_issue_list if issue.impact == 'high')
            
            if high_impact_count >= 2 or len(line_issue_list) >= 3:
                bottlenecks.append({
                    'line_number': line,
                    'issue_count': len(line_issue_list),
                    'high_impact_count': high_impact_count,
                    'severity': 'high' if high_impact_count >= 2 else 'medium'
                })
        
        return sorted(bottlenecks, key=lambda x: x['high_impact_count'], reverse=True)
