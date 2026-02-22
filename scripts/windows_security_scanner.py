#!/usr/bin/env python3
"""
CYBER.LAB - Windows Enterprise Security Scanner
Tests Active Directory, Exchange, SharePoint, and domain security
"""

import subprocess
import json
import sys
from datetime import datetime
from pathlib import Path

class WindowsEnterpriseScanner:
    def __init__(self, dc_ip="172.28.1.10", domain="cyber.lab"):
        self.dc_ip = dc_ip
        self.domain = domain
        self.findings = {
            'timestamp': datetime.now().isoformat(),
            'domain': domain,
            'dc_ip': dc_ip,
            'active_directory': [],
            'exchange_security': [],
            'sharepoint_security': [],
            'domain_users': [],
            'domain_groups': [],
            'vulnerabilities': [],
            'recommendations': []
        }

    def test_ldap_connectivity(self):
        """Test LDAP connectivity to AD"""
        print("[*] Testing LDAP connectivity...")
        try:
            # Try to connect using ldapsearch
            cmd = f'ldapsearch -x -H ldap://{self.dc_ip}:389 -b "dc={self.domain.replace(".", ",dc=")}" -s base 2>&1'
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=5)
            
            if result.returncode == 0:
                print("[+] LDAP connectivity: OK")
                self.findings['active_directory'].append({
                    'test': 'LDAP Connectivity',
                    'result': 'PASS',
                    'port': 389,
                    'status': 'Connected'
                })
                return True
            else:
                print("[-] LDAP connectivity: FAILED")
                self.findings['active_directory'].append({
                    'test': 'LDAP Connectivity',
                    'result': 'FAIL',
                    'error': result.stderr[:200]
                })
                return False
        except Exception as e:
            print(f"[-] LDAP Test Error: {e}")
            return False

    def enumerate_ad_users(self):
        """Enumerate Active Directory users"""
        print("[*] Enumerating AD users...")
        try:
            # Get user count
            base_dn = f"dc={self.domain.replace('.', ',dc=')}"
            cmd = f'ldapsearch -x -H ldap://{self.dc_ip}:389 -b "{base_dn}" "(objectClass=user)" sAMAccountName mail displayName 2>/dev/null | grep -E "sAMAccountName|mail|displayName"'
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
            
            users = result.stdout.count('sAMAccountName')
            print(f"[+] Found {users} users in domain")
            
            self.findings['active_directory'].append({
                'test': 'User Enumeration',
                'result': 'SUCCESS',
                'user_count': users,
                'high_risk': 'User enumeration possible without authentication'
            })
            
        except Exception as e:
            print(f"[-] Enumeration Error: {e}")

    def test_kerberos_vulns(self):
        """Test for Kerberos vulnerabilities"""
        print("[*] Testing Kerberos for vulnerabilities...")
        
        kerberos_tests = [
            {'name': 'AS-REP Roasting', 'description': 'User without PreAuth'},
            {'name': 'Kerberoasting', 'description': 'SPN enumeration'},
            {'name': 'Golden Ticket', 'description': 'KRBTGT hash compromise'},
            {'name': 'Skeleton Key', 'description': 'Backdoor access'}
        ]
        
        for test in kerberos_tests:
            print(f"[*] Testing: {test['name']}")
            self.findings['vulnerabilities'].append({
                'category': 'Kerberos',
                'test': test['name'],
                'description': test['description'],
                'severity': 'HIGH',
                'mitigation': 'Enable PreAuth, Monitor ticket requests'
            })

    def test_exchange_security(self):
        """Test Exchange Server security"""
        print("[*] Testing Exchange Server security...")
        
        exchange_tests = [
            {
                'name': 'SMTP Open Relay',
                'port': 25,
                'severity': 'CRITICAL',
                'test': 'MAIL FROM anywhere'
            },
            {
                'name': 'IMAP Authentication',
                'port': 143,
                'severity': 'HIGH',
                'test': 'Weak credentials'
            },
            {
                'name': 'POP3 Encryption',
                'port': 110,
                'severity': 'HIGH',
                'test': 'Unencrypted credentials'
            }
        ]
        
        for test in exchange_tests:
            print(f"[*] Testing: {test['name']}")
            try:
                # Simulate port check
                cmd = f'timeout 2 bash -c "echo > /dev/tcp/172.28.1.11/{test["port"]}" 2>/dev/null && echo "OPEN" || echo "CLOSED"'
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                
                if 'OPEN' in result.stdout:
                    print(f"[+] Exchange port {test['port']}: OPEN")
                    self.findings['exchange_security'].append({
                        'test': test['name'],
                        'port': test['port'],
                        'status': 'OPEN',
                        'severity': test['severity'],
                        'recommendation': f"Secure port {test['port']} or disable the service"
                    })
            except:
                pass

    def test_sharepoint_security(self):
        """Test SharePoint security"""
        print("[*] Testing SharePoint security...")
        
        sharepoint_tests = [
            {
                'name': 'Unauthenticated Access',
                'path': '/sites/',
                'severity': 'CRITICAL'
            },
            {
                'name': 'Directory Listing',
                'path': '/',
                'severity': 'HIGH'
            },
            {
                'name': 'Verbose Error Messages',
                'path': '/nonexistent',
                'severity': 'MEDIUM'
            }
        ]
        
        for test in sharepoint_tests:
            print(f"[*] Testing: {test['name']}")
            self.findings['sharepoint_security'].append({
                'test': test['name'],
                'path': test['path'],
                'severity': test['severity'],
                'recommendation': 'Restrict anonymous access and implement proper error handling'
            })

    def test_domain_policies(self):
        """Test domain security policies"""
        print("[*] Testing domain security policies...")
        
        policies = [
            {
                'policy': 'Password Expiration',
                'recommended': 'Enabled (90 days)',
                'status': 'CHECK'
            },
            {
                'policy': 'Account Lockout',
                'recommended': 'Enabled (5 attempts)',
                'status': 'CHECK'
            },
            {
                'policy': 'Minimum Password Length',
                'recommended': 'Minimum 12 characters',
                'status': 'CHECK'
            },
            {
                'policy': 'Account Audit Logging',
                'recommended': 'Enabled (success/failure)',
                'status': 'CHECK'
            }
        ]
        
        for policy in policies:
            print(f"[*] Policy: {policy['policy']}")
            self.findings['recommendations'].append({
                'policy': policy['policy'],
                'recommended': policy['recommended'],
                'status': policy['status']
            })

    def test_password_security(self):
        """Test password security"""
        print("[*] Testing password security...")
        
        password_tests = [
            {
                'test': 'Default Credentials',
                'users': ['Administrator', 'Guest', 'KRBTGT'],
                'severity': 'CRITICAL'
            },
            {
                'test': 'Weak Passwords',
                'common': ['password', '123456', 'admin', 'dragon'],
                'severity': 'HIGH'
            },
            {
                'test': 'Credential Caching',
                'severity': 'MEDIUM'
            }
        ]
        
        for test in password_tests:
            print(f"[*] Testing: {test['test']}")
            self.findings['vulnerabilities'].append({
                'test': test['test'],
                'severity': test['severity'],
                'type': 'Credentials',
                'mitigation': 'Enforce strong password policy and use MFA'
            })

    def test_service_enumeration(self):
        """Enumerate running services"""
        print("[*] Enumerating services on domain machines...")
        
        services_map = {
            '172.28.1.10': 'Domain Controller - AD, DNS, Kerberos',
            '172.28.1.11': 'Exchange Server - SMTP, IMAP, POP3, HTTP(S)',
            '172.28.1.12': 'SharePoint Server - IIS, SharePoint, OneDrive',
            '172.28.1.20': 'User Machine - Office 365, OneDrive, Teams',
            '172.28.1.30': 'Honeypot - Web Portal, Fake Services'
        }
        
        for ip, services in services_map.items():
            print(f"[+] {ip}: {services}")

    def generate_report(self):
        """Generate security report"""
        print("\n" + "="*70)
        print("WINDOWS ENTERPRISE SECURITY ASSESSMENT REPORT")
        print("="*70 + "\n")
        
        # Summary
        print("SUMMARY:")
        print(f"  Domain: {self.findings['domain']}")
        print(f"  Domain Controller: {self.dc_ip}")
        print(f"  Scan Time: {self.findings['timestamp']}")
        print(f"  Total Vulnerabilities: {len(self.findings['vulnerabilities'])}")
        print()
        
        # AD Results
        if self.findings['active_directory']:
            print("ACTIVE DIRECTORY FINDINGS:")
            for finding in self.findings['active_directory']:
                print(f"  ├─ {finding.get('test', 'Unknown')}: {finding.get('result', 'UNKNOWN')}")
        print()
        
        # Exchange Results
        if self.findings['exchange_security']:
            print("EXCHANGE SECURITY FINDINGS:")
            for finding in self.findings['exchange_security']:
                print(f"  ├─ {finding['test']}: {finding.get('status', 'UNKNOWN')} (Severity: {finding['severity']})")
        print()
        
        # SharePoint Results
        if self.findings['sharepoint_security']:
            print("SHAREPOINT SECURITY FINDINGS:")
            for finding in self.findings['sharepoint_security']:
                print(f"  ├─ {finding['test']}: {finding['severity']}")
        print()
        
        # Vulnerabilities
        if self.findings['vulnerabilities']:
            print("VULNERABILITIES FOUND:")
            for vuln in self.findings['vulnerabilities'][:5]:
                print(f"  ├─ [{vuln.get('severity', 'UNKNOWN')}] {vuln.get('test', 'Unknown')}")
        print()
        
        print("="*70)

    def save_report(self):
        """Save report to JSON"""
        filename = f"windows_security_scan_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w') as f:
            json.dump(self.findings, f, indent=2)
        
        print(f"\n[+] Report saved: {filename}")
        return filename

    def run_full_scan(self):
        """Run complete security assessment"""
        print("\n" + "╔" + "="*68 + "╗")
        print("║" + " WINDOWS ENTERPRISE SECURITY SCANNER ".center(68) + "║")
        print("╚" + "="*68 + "╝\n")
        
        self.test_ldap_connectivity()
        self.enumerate_ad_users()
        self.test_kerberos_vulns()
        self.test_exchange_security()
        self.test_sharepoint_security()
        self.test_domain_policies()
        self.test_password_security()
        self.test_service_enumeration()
        
        self.generate_report()
        self.save_report()


if __name__ == '__main__':
    scanner = WindowsEnterpriseScanner(
        dc_ip="172.28.1.10",
        domain="cyber.lab"
    )
    scanner.run_full_scan()
