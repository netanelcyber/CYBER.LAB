#!/usr/bin/env python3
"""
CYBER.LAB - Blackbox Reconnaissance Scanner
External vulnerability discovery without internal knowledge
"""

import requests
import re
import json
import sys
from urllib.parse import urljoin, urlparse
from datetime import datetime
import warnings

warnings.filterwarnings('ignore', message='Unverified HTTPS request')

class BlackboxRecon:
    def __init__(self, target_url):
        self.target = target_url.rstrip('/')
        self.session = requests.Session()
        self.session.verify = False
        self.session.timeout = 10
        self.findings = {
            'timestamp': datetime.now().isoformat(),
            'target': target_url,
            'reconnaissance': {},
            'vulnerabilities': [],
            'endpoints': [],
            'technologies': []
        }
        
    def headers_user_agent(self):
        """Realistic user agents for blackbox testing"""
        return {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive'
        }

    def fingerprint_cms(self):
        """Detect CMS type from HTTP responses"""
        print("[*] Fingerprinting CMS...")
        
        try:
            resp = self.session.get(self.target, headers=self.headers_user_agent())
            
            fingerprints = {
                'Drupal': [
                    r'Drupal',
                    r'sites/default/files',
                    r'sites/all/modules',
                    r'/misc/drupal.js',
                    r'(?:node|user|admin)/\d+',
                    r'X-Generator.*Drupal',
                    r'sites/default/settings.php',
                ],
                'WordPress': [
                    r'wp-content',
                    r'wp-admin',
                    r'wp-includes',
                    r'/wp-json/',
                    r'X-Generator.*WordPress',
                    r'<link rel=["\']stylesheet["\'] id=["\']wp-',
                    r'wp-config.php',
                ],
                'Joomla': [
                    r'Joomla',
                    r'/components/',
                    r'/modules/',
                    r'administrator',
                    r'X-Generator.*Joomla',
                ],
            }
            
            for cms, patterns in fingerprints.items():
                for pattern in patterns:
                    if re.search(pattern, resp.text, re.IGNORECASE):
                        self.findings['reconnaissance']['cms'] = cms
                        print(f"[+] Detected: {cms}")
                        return cms
                        
            # Check headers
            if 'Server' in resp.headers:
                self.findings['reconnaissance']['server'] = resp.headers['Server']
                print(f"[+] Server: {resp.headers['Server']}")
                
        except Exception as e:
            print(f"[-] Error fingerprinting CMS: {e}")
        
        return None

    def detect_version(self):
        """Detect application version from various methods"""
        print("[*] Detecting version...")
        
        version_paths = [
            '/CHANGELOG.txt',
            '/CHANGELOG.md',
            '/README.md',
            '/VERSION',
            '/version',
            '/wp-json/',
            '/sites/default/settings.php',
        ]
        
        for path in version_paths:
            try:
                resp = self.session.get(urljoin(self.target, path), 
                                       headers=self.headers_user_agent(), 
                                       timeout=5)
                
                if resp.status_code == 200:
                    # Extract version from CHANGELOG
                    if 'CHANGELOG' in path:
                        version_match = re.search(r'([0-9]+\.[0-9]+\.[0-9]+)', resp.text)
                        if version_match:
                            version = version_match.group(1)
                            self.findings['reconnaissance']['version'] = version
                            print(f"[+] Version detected: {version}")
                            return version
                    
                    # Extract from JSON API
                    if path == '/wp-json/':
                        try:
                            data = resp.json()
                            if 'namespaces' in data:
                                print("[+] WordPress REST API found")
                                self.findings['endpoints'].append(path)
                        except:
                            pass
            except:
                pass
        
        return None

    def enumerate_endpoints(self):
        """Discover common endpoints"""
        print("[*] Enumerating endpoints...")
        
        endpoints = {
            'Drupal': [
                '/admin',
                '/user/login',
                '/user/register',
                '/nodes',
                '/views/ajax',
                '/entity/user',
                '/services/json',
                '/rest/me',
                '/jsonapi/user/user',
                '/cron.php',
                '/update.php',
            ],
            'WordPress': [
                '/wp-admin',
                '/wp-login.php',
                '/wp-json/',
                '/wp-json/wp/v2/users',
                '/wp-json/wp/v2/posts',
                '/wp-json/wp/v2/comments',
                '/wp-content/plugins',
                '/wp-includes/version.php',
                '/xmlrpc.php',
                '/feed',
                '/wp-admin/admin-ajax.php',
            ],
        }
        
        cms = self.findings['reconnaissance'].get('cms', 'Drupal')
        cms_endpoints = endpoints.get(cms, endpoints['Drupal'])
        
        found = []
        for endpoint in cms_endpoints:
            try:
                url = urljoin(self.target, endpoint)
                resp = self.session.get(url, headers=self.headers_user_agent(), timeout=5)
                
                if resp.status_code < 500:  # Not error
                    found.append({
                        'endpoint': endpoint,
                        'status_code': resp.status_code,
                        'size': len(resp.text)
                    })
                    print(f"[+] Found: {endpoint} ({resp.status_code})")
                    
            except:
                pass
        
        self.findings['endpoints'] = found
        return found

    def test_common_vulnerabilities(self):
        """Test for common blackbox vulnerabilities"""
        print("[*] Testing for common vulnerabilities...")
        
        # 1. SQL Injection in login
        print("  [*] Testing SQL injection in login...")
        try:
            resp = self.session.post(
                urljoin(self.target, '/user/login'),
                data={'name': "' OR '1'='1", 'pass': 'test'},
                headers=self.headers_user_agent(),
                timeout=5
            )
            
            if 'user' in resp.text.lower() or resp.status_code == 200:
                self.findings['vulnerabilities'].append({
                    'type': 'Potential SQL Injection',
                    'location': '/user/login',
                    'severity': 'HIGH',
                    'payload': "' OR '1'='1"
                })
                print("  [+] Potential SQL injection found!")
        except:
            pass
        
        # 2. Directory traversal
        print("  [*] Testing directory traversal...")
        traversal_tests = [
            ('../../etc/passwd', '/download'),
            ('..\\..\\windows\\system32\\config\\sam', '/file'),
        ]
        
        for payload, endpoint in traversal_tests:
            try:
                url = urljoin(self.target, f"{endpoint}?file={payload}")
                resp = self.session.get(url, headers=self.headers_user_agent(), timeout=5)
                
                if 'root:' in resp.text or 'Administrator' in resp.text:
                    self.findings['vulnerabilities'].append({
                        'type': 'Directory Traversal',
                        'location': endpoint,
                        'severity': 'CRITICAL',
                        'payload': payload
                    })
                    print("  [+] Directory traversal vulnerability found!")
            except:
                pass
        
        # 3. XXE Injection
        print("  [*] Testing XXE injection...")
        xxe_payload = '''<?xml version="1.0"?>
        <!DOCTYPE foo [
            <!ENTITY xxe SYSTEM "file:///etc/passwd">
        ]>
        <foo>&xxe;</foo>'''
        
        try:
            resp = self.session.post(
                urljoin(self.target, '/rest/me'),
                data=xxe_payload,
                headers={'Content-Type': 'application/xml'},
                timeout=5
            )
            
            if 'root:' in resp.text:
                self.findings['vulnerabilities'].append({
                    'type': 'XXE Injection',
                    'location': '/rest/me',
                    'severity': 'CRITICAL'
                })
                print("  [+] XXE vulnerability found!")
        except:
            pass
        
        # 4. CSRF Token missing
        print("  [*] Checking for CSRF protection...")
        try:
            resp = self.session.get(
                urljoin(self.target, '/user'),
                headers=self.headers_user_agent(),
                timeout=5
            )
            
            if 'csrf_token' not in resp.text and 'nonce' not in resp.text:
                self.findings['vulnerabilities'].append({
                    'type': 'Missing CSRF Protection',
                    'location': '/user',
                    'severity': 'HIGH'
                })
                print("  [+] Missing CSRF tokens detected!")
        except:
            pass
        
        # 5. Information Disclosure
        print("  [*] Checking for information disclosure...")
        try:
            resp = self.session.get(
                urljoin(self.target, '/admin'),
                headers=self.headers_user_agent(),
                timeout=5
            )
            
            if 'error' in resp.text.lower() or 'exception' in resp.text.lower():
                self.findings['vulnerabilities'].append({
                    'type': 'Information Disclosure',
                    'location': '/admin',
                    'severity': 'MEDIUM',
                    'detail': 'Error messages reveal system information'
                })
                print("  [+] Information disclosure found!")
        except:
            pass

    def check_authentication(self):
        """Test authentication mechanisms"""
        print("[*] Testing authentication...")
        
        # Check for weak credentials
        print("  [*] Testing common credentials...")
        credentials = [
            ('admin', 'admin'),
            ('admin', '123456'),
            ('admin', 'password'),
            ('test', 'test'),
        ]
        
        weak_creds = []
        for username, password in credentials:
            try:
                resp = self.session.post(
                    urljoin(self.target, '/user/login'),
                    data={'name': username, 'pass': password},
                    headers=self.headers_user_agent(),
                    timeout=5
                )
                
                if 'logout' in resp.text or 'dashboard' in resp.text or resp.status_code == 302:
                    weak_creds.append({'username': username, 'password': password})
                    print(f"  [!] Weak credentials found: {username}:{password}")
            except:
                pass
        
        if weak_creds:
            self.findings['vulnerabilities'].append({
                'type': 'Weak Credentials',
                'credentials': weak_creds,
                'severity': 'CRITICAL'
            })
        
        # Check password policy
        print("  [*] Checking password policy...")
        try:
            resp = self.session.get(
                urljoin(self.target, '/user/register'),
                headers=self.headers_user_agent(),
                timeout=5
            )
            
            if 'password' in resp.text and 'strength' not in resp.text.lower():
                print("  [+] Weak password policy detected")
        except:
            pass

    def check_security_headers(self):
        """Analyze HTTP security headers"""
        print("[*] Analyzing security headers...")
        
        required_headers = [
            ('X-Content-Type-Options', 'nosniff'),
            ('X-Frame-Options', ['DENY', 'SAMEORIGIN']),
            ('Strict-Transport-Security', 'max-age='),
            ('Content-Security-Policy', ''),
            ('X-XSS-Protection', '1; mode=block'),
        ]
        
        try:
            resp = self.session.get(
                self.target,
                headers=self.headers_user_agent(),
                timeout=5
            )
            
            missing_headers = []
            for header, expected in required_headers:
                if header not in resp.headers:
                    missing_headers.append(header)
                    print(f"  [-] Missing: {header}")
            
            if missing_headers:
                self.findings['vulnerabilities'].append({
                    'type': 'Missing Security Headers',
                    'headers': missing_headers,
                    'severity': 'MEDIUM'
                })
        except:
            pass

    def run_full_scan(self):
        """Execute complete blackbox reconnaissance"""
        print("="*60)
        print("CYBER.LAB - BLACKBOX RECONNAISSANCE SCAN")
        print("="*60)
        print(f"Target: {self.target}")
        print("="*60)
        print()
        
        self.fingerprint_cms()
        self.detect_version()
        self.enumerate_endpoints()
        self.test_common_vulnerabilities()
        self.check_authentication()
        self.check_security_headers()
        
        return self.findings

    def save_report(self, filename='blackbox_report.json'):
        """Save findings to JSON report"""
        with open(filename, 'w') as f:
            json.dump(self.findings, f, indent=2)
        print(f"\n[+] Report saved to: {filename}")

def main():
    if len(sys.argv) < 2:
        print("Usage: python blackbox_scanner.py <target_url>")
        print("Example: python blackbox_scanner.py http://localhost:8001")
        sys.exit(1)
    
    target = sys.argv[1]
    
    scanner = BlackboxRecon(target)
    findings = scanner.run_full_scan()
    
    # Print summary
    print("\n" + "="*60)
    print("SCAN SUMMARY")
    print("="*60)
    print(f"CMS: {findings['reconnaissance'].get('cms', 'Unknown')}")
    print(f"Version: {findings['reconnaissance'].get('version', 'Unknown')}")
    print(f"Endpoints Found: {len(findings['endpoints'])}")
    print(f"Vulnerabilities: {len(findings['vulnerabilities'])}")
    
    if findings['vulnerabilities']:
        print("\nVulnerabilities:")
        for vuln in findings['vulnerabilities']:
            print(f"  - {vuln['type']} ({vuln.get('severity', 'UNKNOWN')})")
    
    # Save report
    scanner.save_report('blackbox_report.json')

if __name__ == '__main__':
    main()
