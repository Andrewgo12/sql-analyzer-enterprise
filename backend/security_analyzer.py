#!/usr/bin/env python3
"""
SECURITY ANALYZER - ENTERPRISE SQL SECURITY SCANNER
Advanced SQL injection detection and security vulnerability analysis
"""

import re
import time
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum

class VulnerabilityType(Enum):
    SQL_INJECTION = "sql_injection"
    PRIVILEGE_ESCALATION = "privilege_escalation"
    DATA_EXPOSURE = "data_exposure"
    WEAK_AUTHENTICATION = "weak_authentication"
    INSECURE_FUNCTION = "insecure_function"
    INFORMATION_DISCLOSURE = "information_disclosure"

class RiskLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class SecurityVulnerability:
    line: int
    column: int
    vulnerability_type: VulnerabilityType
    risk_level: RiskLevel
    title: str
    description: str
    evidence: str
    recommendation: str
    cwe_id: Optional[str] = None
    owasp_category: Optional[str] = None

class SecurityAnalyzer:
    """Enterprise-grade SQL security analyzer"""
    
    def __init__(self):
        self.sql_injection_patterns = self._load_injection_patterns()
        self.dangerous_functions = self._load_dangerous_functions()
        self.privilege_keywords = self._load_privilege_keywords()
        self.information_schema_tables = self._load_info_schema_tables()
        
    def _load_injection_patterns(self) -> List[Dict[str, Any]]:
        """Load SQL injection detection patterns"""
        return [
            {
                'pattern': r"'\s*OR\s+'.*?'\s*=\s*'",
                'description': "Classic SQL injection pattern with OR condition",
                'risk': RiskLevel.CRITICAL,
                'cwe': "CWE-89"
            },
            {
                'pattern': r"'\s*;\s*DROP\s+TABLE",
                'description': "SQL injection attempting to drop tables",
                'risk': RiskLevel.CRITICAL,
                'cwe': "CWE-89"
            },
            {
                'pattern': r"UNION\s+SELECT.*FROM\s+information_schema",
                'description': "UNION-based SQL injection targeting information schema",
                'risk': RiskLevel.HIGH,
                'cwe': "CWE-89"
            },
            {
                'pattern': r"'\s*AND\s+1\s*=\s*1\s*--",
                'description': "Boolean-based blind SQL injection",
                'risk': RiskLevel.HIGH,
                'cwe': "CWE-89"
            },
            {
                'pattern': r"'\s*OR\s+1\s*=\s*1\s*--",
                'description': "Boolean-based SQL injection bypass",
                'risk': RiskLevel.CRITICAL,
                'cwe': "CWE-89"
            },
            {
                'pattern': r"SLEEP\s*\(\s*\d+\s*\)",
                'description': "Time-based blind SQL injection",
                'risk': RiskLevel.HIGH,
                'cwe': "CWE-89"
            },
            {
                'pattern': r"BENCHMARK\s*\(\s*\d+",
                'description': "MySQL benchmark function for time-based attacks",
                'risk': RiskLevel.HIGH,
                'cwe': "CWE-89"
            },
            {
                'pattern': r"WAITFOR\s+DELAY",
                'description': "SQL Server time delay for blind injection",
                'risk': RiskLevel.HIGH,
                'cwe': "CWE-89"
            }
        ]
    
    def _load_dangerous_functions(self) -> List[Dict[str, Any]]:
        """Load dangerous SQL functions that pose security risks"""
        return [
            {
                'function': 'LOAD_FILE',
                'description': 'Can read files from the server filesystem',
                'risk': RiskLevel.HIGH,
                'recommendation': 'Avoid using LOAD_FILE or restrict file access permissions'
            },
            {
                'function': 'INTO OUTFILE',
                'description': 'Can write data to server filesystem',
                'risk': RiskLevel.HIGH,
                'recommendation': 'Restrict file write permissions and validate file paths'
            },
            {
                'function': 'SYSTEM',
                'description': 'Can execute system commands',
                'risk': RiskLevel.CRITICAL,
                'recommendation': 'Never use SYSTEM function in production code'
            },
            {
                'function': 'xp_cmdshell',
                'description': 'SQL Server function to execute OS commands',
                'risk': RiskLevel.CRITICAL,
                'recommendation': 'Disable xp_cmdshell and use safer alternatives'
            },
            {
                'function': 'sp_OACreate',
                'description': 'Can create OLE objects and execute code',
                'risk': RiskLevel.CRITICAL,
                'recommendation': 'Disable OLE automation procedures'
            },
            {
                'function': 'OPENROWSET',
                'description': 'Can access remote data sources',
                'risk': RiskLevel.MEDIUM,
                'recommendation': 'Validate and restrict remote data access'
            }
        ]
    
    def _load_privilege_keywords(self) -> List[str]:
        """Load keywords related to privilege escalation"""
        return [
            'GRANT', 'REVOKE', 'CREATE USER', 'DROP USER', 'ALTER USER',
            'CREATE ROLE', 'DROP ROLE', 'SET ROLE', 'ADMIN OPTION',
            'WITH GRANT OPTION', 'SUPER', 'PROCESS', 'FILE', 'RELOAD',
            'SHUTDOWN', 'CREATE TEMPORARY TABLES', 'LOCK TABLES',
            'REPLICATION SLAVE', 'REPLICATION CLIENT', 'CREATE VIEW',
            'SHOW VIEW', 'CREATE ROUTINE', 'ALTER ROUTINE', 'EXECUTE',
            'EVENT', 'TRIGGER'
        ]
    
    def _load_info_schema_tables(self) -> List[str]:
        """Load information schema table names"""
        return [
            'information_schema.tables', 'information_schema.columns',
            'information_schema.schemata', 'information_schema.user_privileges',
            'information_schema.table_privileges', 'information_schema.column_privileges',
            'mysql.user', 'mysql.db', 'mysql.tables_priv', 'mysql.columns_priv',
            'sys.databases', 'sys.tables', 'sys.columns', 'sys.users',
            'pg_catalog.pg_tables', 'pg_catalog.pg_user', 'pg_catalog.pg_database'
        ]
    
    def analyze(self, sql_content: str) -> Dict[str, Any]:
        """
        Perform comprehensive security analysis
        
        Args:
            sql_content: SQL code to analyze
            
        Returns:
            Security analysis results
        """
        start_time = time.time()
        
        try:
            vulnerabilities = []
            
            # Check for SQL injection patterns
            vulnerabilities.extend(self._detect_sql_injection(sql_content))
            
            # Check for dangerous functions
            vulnerabilities.extend(self._detect_dangerous_functions(sql_content))
            
            # Check for privilege escalation attempts
            vulnerabilities.extend(self._detect_privilege_escalation(sql_content))
            
            # Check for information disclosure
            vulnerabilities.extend(self._detect_information_disclosure(sql_content))
            
            # Check for weak authentication patterns
            vulnerabilities.extend(self._detect_weak_authentication(sql_content))
            
            # Calculate security score
            security_score = self._calculate_security_score(vulnerabilities)
            
            # Generate risk assessment
            risk_assessment = self._generate_risk_assessment(vulnerabilities)
            
            processing_time = time.time() - start_time
            
            return {
                'status': 'success',
                'processing_time': round(processing_time, 3),
                'security_score': security_score,
                'risk_level': self._get_overall_risk_level(vulnerabilities),
                'vulnerabilities': [self._vulnerability_to_dict(v) for v in vulnerabilities],
                'vulnerability_summary': self._generate_vulnerability_summary(vulnerabilities),
                'risk_assessment': risk_assessment,
                'recommendations': self._generate_security_recommendations(vulnerabilities),
                'compliance_status': self._check_compliance_status(vulnerabilities)
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e),
                'processing_time': time.time() - start_time
            }
    
    def _detect_sql_injection(self, sql_content: str) -> List[SecurityVulnerability]:
        """Detect SQL injection vulnerabilities"""
        vulnerabilities = []
        lines = sql_content.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            line_upper = line.upper()
            
            for pattern_info in self.sql_injection_patterns:
                matches = re.finditer(pattern_info['pattern'], line_upper, re.IGNORECASE)
                
                for match in matches:
                    vulnerabilities.append(SecurityVulnerability(
                        line=line_num,
                        column=match.start(),
                        vulnerability_type=VulnerabilityType.SQL_INJECTION,
                        risk_level=pattern_info['risk'],
                        title="SQL Injection Vulnerability",
                        description=pattern_info['description'],
                        evidence=match.group(),
                        recommendation="Use parameterized queries and input validation",
                        cwe_id=pattern_info.get('cwe'),
                        owasp_category="A03:2021 – Injection"
                    ))
        
        return vulnerabilities
    
    def _detect_dangerous_functions(self, sql_content: str) -> List[SecurityVulnerability]:
        """Detect usage of dangerous SQL functions"""
        vulnerabilities = []
        lines = sql_content.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            line_upper = line.upper()
            
            for func_info in self.dangerous_functions:
                if func_info['function'] in line_upper:
                    # Find the exact position
                    match = re.search(re.escape(func_info['function']), line_upper)
                    if match:
                        vulnerabilities.append(SecurityVulnerability(
                            line=line_num,
                            column=match.start(),
                            vulnerability_type=VulnerabilityType.INSECURE_FUNCTION,
                            risk_level=func_info['risk'],
                            title=f"Dangerous Function: {func_info['function']}",
                            description=func_info['description'],
                            evidence=func_info['function'],
                            recommendation=func_info['recommendation'],
                            cwe_id="CWE-78",
                            owasp_category="A03:2021 – Injection"
                        ))
        
        return vulnerabilities
    
    def _detect_privilege_escalation(self, sql_content: str) -> List[SecurityVulnerability]:
        """Detect privilege escalation attempts"""
        vulnerabilities = []
        lines = sql_content.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            line_upper = line.upper()
            
            for keyword in self.privilege_keywords:
                if keyword in line_upper:
                    # Check if it's a potentially dangerous privilege operation
                    if any(danger in line_upper for danger in ['ALL PRIVILEGES', 'SUPER', 'FILE', 'PROCESS']):
                        vulnerabilities.append(SecurityVulnerability(
                            line=line_num,
                            column=line_upper.find(keyword),
                            vulnerability_type=VulnerabilityType.PRIVILEGE_ESCALATION,
                            risk_level=RiskLevel.HIGH,
                            title="Privilege Escalation Risk",
                            description=f"Potentially dangerous privilege operation: {keyword}",
                            evidence=keyword,
                            recommendation="Review privilege assignments and apply principle of least privilege",
                            cwe_id="CWE-269",
                            owasp_category="A01:2021 – Broken Access Control"
                        ))
        
        return vulnerabilities
    
    def _detect_information_disclosure(self, sql_content: str) -> List[SecurityVulnerability]:
        """Detect information disclosure vulnerabilities"""
        vulnerabilities = []
        lines = sql_content.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            line_upper = line.upper()
            
            # Check for information schema access
            for table in self.information_schema_tables:
                if table.upper() in line_upper:
                    vulnerabilities.append(SecurityVulnerability(
                        line=line_num,
                        column=line_upper.find(table.upper()),
                        vulnerability_type=VulnerabilityType.INFORMATION_DISCLOSURE,
                        risk_level=RiskLevel.MEDIUM,
                        title="Information Schema Access",
                        description=f"Access to sensitive system table: {table}",
                        evidence=table,
                        recommendation="Restrict access to information schema tables",
                        cwe_id="CWE-200",
                        owasp_category="A01:2021 – Broken Access Control"
                    ))
            
            # Check for password-related queries
            if re.search(r'password|pwd|passwd', line_upper):
                vulnerabilities.append(SecurityVulnerability(
                    line=line_num,
                    column=0,
                    vulnerability_type=VulnerabilityType.DATA_EXPOSURE,
                    risk_level=RiskLevel.HIGH,
                    title="Password Data Exposure",
                    description="Query involves password-related data",
                    evidence=line[:50] + "...",
                    recommendation="Ensure passwords are properly hashed and protected",
                    cwe_id="CWE-256",
                    owasp_category="A02:2021 – Cryptographic Failures"
                ))
        
        return vulnerabilities
    
    def _detect_weak_authentication(self, sql_content: str) -> List[SecurityVulnerability]:
        """Detect weak authentication patterns"""
        vulnerabilities = []
        lines = sql_content.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            line_upper = line.upper()
            
            # Check for hardcoded passwords
            password_patterns = [
                r"PASSWORD\s*=\s*['\"][^'\"]+['\"]",
                r"PWD\s*=\s*['\"][^'\"]+['\"]",
                r"IDENTIFIED\s+BY\s+['\"][^'\"]+['\"]"
            ]
            
            for pattern in password_patterns:
                matches = re.finditer(pattern, line_upper)
                for match in matches:
                    vulnerabilities.append(SecurityVulnerability(
                        line=line_num,
                        column=match.start(),
                        vulnerability_type=VulnerabilityType.WEAK_AUTHENTICATION,
                        risk_level=RiskLevel.HIGH,
                        title="Hardcoded Password",
                        description="Password appears to be hardcoded in SQL",
                        evidence=match.group()[:20] + "...",
                        recommendation="Use environment variables or secure credential storage",
                        cwe_id="CWE-798",
                        owasp_category="A07:2021 – Identification and Authentication Failures"
                    ))
        
        return vulnerabilities
    
    def _calculate_security_score(self, vulnerabilities: List[SecurityVulnerability]) -> int:
        """Calculate security score (0-100, higher is better)"""
        if not vulnerabilities:
            return 100
        
        score = 100
        
        for vuln in vulnerabilities:
            if vuln.risk_level == RiskLevel.CRITICAL:
                score -= 25
            elif vuln.risk_level == RiskLevel.HIGH:
                score -= 15
            elif vuln.risk_level == RiskLevel.MEDIUM:
                score -= 10
            elif vuln.risk_level == RiskLevel.LOW:
                score -= 5
        
        return max(score, 0)
    
    def _get_overall_risk_level(self, vulnerabilities: List[SecurityVulnerability]) -> str:
        """Determine overall risk level"""
        if not vulnerabilities:
            return "LOW"
        
        risk_levels = [v.risk_level for v in vulnerabilities]
        
        if RiskLevel.CRITICAL in risk_levels:
            return "CRITICAL"
        elif RiskLevel.HIGH in risk_levels:
            return "HIGH"
        elif RiskLevel.MEDIUM in risk_levels:
            return "MEDIUM"
        else:
            return "LOW"
    
    def _generate_vulnerability_summary(self, vulnerabilities: List[SecurityVulnerability]) -> Dict[str, int]:
        """Generate vulnerability count summary"""
        summary = {
            'critical': 0,
            'high': 0,
            'medium': 0,
            'low': 0,
            'total': len(vulnerabilities)
        }
        
        for vuln in vulnerabilities:
            summary[vuln.risk_level.value] += 1
        
        return summary
    
    def _generate_risk_assessment(self, vulnerabilities: List[SecurityVulnerability]) -> Dict[str, Any]:
        """Generate comprehensive risk assessment"""
        return {
            'overall_risk': self._get_overall_risk_level(vulnerabilities),
            'critical_issues': len([v for v in vulnerabilities if v.risk_level == RiskLevel.CRITICAL]),
            'injection_risks': len([v for v in vulnerabilities if v.vulnerability_type == VulnerabilityType.SQL_INJECTION]),
            'privilege_risks': len([v for v in vulnerabilities if v.vulnerability_type == VulnerabilityType.PRIVILEGE_ESCALATION]),
            'data_exposure_risks': len([v for v in vulnerabilities if v.vulnerability_type == VulnerabilityType.DATA_EXPOSURE]),
            'remediation_priority': self._get_remediation_priority(vulnerabilities)
        }
    
    def _get_remediation_priority(self, vulnerabilities: List[SecurityVulnerability]) -> List[str]:
        """Get prioritized list of remediation actions"""
        priorities = []
        
        critical_vulns = [v for v in vulnerabilities if v.risk_level == RiskLevel.CRITICAL]
        if critical_vulns:
            priorities.append("IMMEDIATE: Fix critical vulnerabilities")
        
        injection_vulns = [v for v in vulnerabilities if v.vulnerability_type == VulnerabilityType.SQL_INJECTION]
        if injection_vulns:
            priorities.append("HIGH: Implement parameterized queries")
        
        privilege_vulns = [v for v in vulnerabilities if v.vulnerability_type == VulnerabilityType.PRIVILEGE_ESCALATION]
        if privilege_vulns:
            priorities.append("HIGH: Review privilege assignments")
        
        if not priorities:
            priorities.append("LOW: Continue security monitoring")
        
        return priorities
    
    def _generate_security_recommendations(self, vulnerabilities: List[SecurityVulnerability]) -> List[str]:
        """Generate security recommendations"""
        recommendations = set()
        
        for vuln in vulnerabilities:
            recommendations.add(vuln.recommendation)
        
        # Add general recommendations
        recommendations.add("Implement input validation and sanitization")
        recommendations.add("Use parameterized queries for all database operations")
        recommendations.add("Apply principle of least privilege")
        recommendations.add("Regular security audits and penetration testing")
        recommendations.add("Keep database software updated")
        
        return list(recommendations)
    
    def _check_compliance_status(self, vulnerabilities: List[SecurityVulnerability]) -> Dict[str, Any]:
        """Check compliance with security standards"""
        return {
            'owasp_top_10_issues': len([v for v in vulnerabilities if v.owasp_category]),
            'cwe_issues': len([v for v in vulnerabilities if v.cwe_id]),
            'compliance_score': max(100 - len(vulnerabilities) * 10, 0),
            'requires_immediate_attention': len([v for v in vulnerabilities if v.risk_level == RiskLevel.CRITICAL]) > 0
        }
    
    def _vulnerability_to_dict(self, vuln: SecurityVulnerability) -> Dict[str, Any]:
        """Convert SecurityVulnerability to dictionary"""
        return {
            'line': vuln.line,
            'column': vuln.column,
            'type': vuln.vulnerability_type.value,
            'risk_level': vuln.risk_level.value,
            'title': vuln.title,
            'description': vuln.description,
            'evidence': vuln.evidence,
            'recommendation': vuln.recommendation,
            'cwe_id': vuln.cwe_id,
            'owasp_category': vuln.owasp_category
        }
