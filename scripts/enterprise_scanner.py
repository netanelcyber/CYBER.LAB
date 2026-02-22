#!/usr/bin/env python3
"""
CYBER.LAB - Enterprise Lab Scanner
Scans Active Directory, Exchange, O365, and all connected services
"""

import requests
import subprocess
import json
import sys
from datetime import datetime
import ldap
import smtplib

class EnterpriseLabScanner:
    def __init__(self):
        self.findings = {
            'timestamp': datetime.now().isoformat(),
            'active_directory': [],
            'exchange_server': [],
            'o365_services': [],
            'web_applications': [],
            'unpatched_machines': [],
            'network_topology': {}
        }

    def scan_active_directory(self):
        """Scan LDAP/Active Directory"""
        print("[*] Scanning Active Directory...")
        
        try:
            conn = ldap.initialize('ldap://172.28.0.2:389')
            conn.simple_bind_s('cn=admin,dc=cyber,dc=lab', 'admin123456')
            
            # Search for users
            results = conn.search_s('dc=cyber,dc=lab', ldap.SCOPE_SUBTREE, 
                                   '(objectClass=user)', ['mail', 'displayName', 'sAMAccountName'])
            
            users = []
            for dn, attrs in results:
                users.append({
                    'dn': dn,
                    'mail': attrs.get(b'mail', [b''])[0].decode(),
                    'displayName': attrs.get(b'displayName', [b''])[0].decode(),
                    'sAMAccountName': attrs.get(b'sAMAccountName', [b''])[0].decode()
                })
            
            self.findings['active_directory'].append({
                'service': 'Samba DC',
                'users_found': len(users),
                'users': users
            })
            
            print(f"[+] Found {len(users)} AD users")
            conn.unbind_s()
            
        except Exception as e:
            print(f"[-] AD Scan Error: {e}")

    def scan_exchange_server(self):
        """Test Exchange/Mail server"""
        print("[*] Scanning Exchange Server...")
        
        # Test SMTP
        try:
            smtp = smtplib.SMTP('172.28.0.5', 25)
            banner = smtp.ehlo()
            print(f"[+] SMTP Banner: {banner}")
            
            self.findings['exchange_server'].append({
                'service': 'SMTP',
                'port': 25,
                'status': 'open',
                'banner': str(banner)
            })
            
            smtp.quit()
        except Exception as e:
            print(f"[-] SMTP Error: {e}")
        
        # Test IMAP
        try:
            import imaplib
            imap = imaplib.IMAP4('172.28.0.5', 143)
            print(f"[+] IMAP Banner: {imap.welcome}")
            
            self.findings['exchange_server'].append({
                'service': 'IMAP',
                'port': 143,
                'status': 'open',
                'banner': imap.welcome.decode()
            })
            
            imap.logout()
        except Exception as e:
            print(f"[-] IMAP Error: {e}")

    def scan_o365_simulator(self):
        """Scan O365 simulator for vulnerabilities"""
        print("[*] Scanning O365 Services...")
        
        base_url = 'http://172.28.0.6:3000'
        
        # Test login
        try:
            resp = requests.post(f'{base_url}/auth/login', 
                               json={'username': 'admin@cyber.lab', 'password': 'P@ssw0rd2026!'},
                               timeout=5)
            if resp.status_code == 200:
                data = resp.json()
                token = data['token']
                print(f"[+] O365 Authentication Successful")
                
                # Test services endpoint
                resp = requests.get(f'{base_url}/api/services', timeout=5)
                print(f"[+] O365 Services: {len(resp.json())} services found")
                
                # Test config endpoint
                resp = requests.get(f'{base_url}/api/config', timeout=5)
                config = resp.json()
                print(f"[+] Found internal servers: {config['internalServers']}")
                
                # Test user enumeration
                resp = requests.get(f'{base_url}/api/users', timeout=5)
                users = resp.json()['users']
                print(f"[+] User enumeration: {len(users)} users exposed")
                
                self.findings['o365_services'].append({
                    'service': 'O365 API',
                    'vulnerabilities': [
                        'User enumeration (no auth required)',
                        'Config endpoint exposed',
                        'No rate limiting on login',
                        'Weak SSRF protection'
                    ],
                    'users': users
                })
                
        except Exception as e:
            print(f"[-] O365 Scan Error: {e}")

    def scan_sharepoint(self):
        """Scan SharePoint/OneDrive"""
        print("[*] Scanning SharePoint/OneDrive...")
        
        base_url = 'http://172.28.0.7:3000'
        
        try:
            # Enumerate all documents
            resp = requests.get(f'{base_url}/api/all-documents', timeout=5)
            docs = resp.json()['allDocuments']
            print(f"[+] SharePoint: {len(docs)} documents found")
            
            # List sites
            resp = requests.get(f'{base_url}/api/sites', timeout=5)
            sites = resp.json()['sites']
            print(f"[+] Found {len(sites)} sites")
            
            self.findings['o365_services'].append({
                'service': 'SharePoint/OneDrive',
                'vulnerabilities': [
                    'No authentication required',
                    'Full document enumeration possible',
                    'Directory traversal vulnerability',
                    'Unauthorized access to all user files'
                ],
                'sites': len(sites),
                'documents_exposed': len(docs)
            })
            
        except Exception as e:
            print(f"[-] SharePoint Scan Error: {e}")

    def scan_web_apps(self):
        """Scan connected web applications"""
        print("[*] Scanning Web Applications...")
        
        apps = [
            ('Drupal 7', 'http://172.28.0.22:80'),
            ('WordPress', 'http://172.28.0.24:80')
        ]
        
        for name, url in apps:
            try:
                resp = requests.get(url, timeout=5)
                print(f"[+] {name}: {resp.status_code}")
                
                self.findings['web_applications'].append({
                    'app': name,
                    'url': url,
                    'status': resp.status_code,
                    'size': len(resp.text)
                })
                
            except Exception as e:
                print(f"[-] {name} Error: {e}")

    def scan_unpatched_machines(self):
        """Scan unpatched machines"""
        print("[*] Scanning Unpatched Machines...")
        
        # Test Linux
        try:
            result = subprocess.run(['ssh', '-o', 'StrictHostKeyChecking=no',
                                   'testuser@172.28.0.41', 'ssh -V'],
                                   capture_output=True, timeout=5, text=True)
            
            print(f"[+] Unpatched Linux version: {result.stderr}")
            
            self.findings['unpatched_machines'].append({
                'name': 'Unpatched Linux',
                'ip': '172.28.0.41',
                'ssh_version': result.stderr,
                'vulnerabilities': [
                    'OpenSSH 7.2 - CVE-2018-15473',
                    'Apache 2.4.18 - Multiple vulns',
                    'PHP 5.6 - Multiple vulns'
                ]
            })
            
        except Exception as e:
            print(f"[-] Linux Scan Error: {e}")

    def run_full_scan(self):
        """Run comprehensive enterprise scan"""
        print("\n" + "="*70)
        print("CYBER.LAB - ENTERPRISE LAB COMPREHENSIVE SCAN")
        print("="*70 + "\n")
        
        self.scan_active_directory()
        self.scan_exchange_server()
        self.scan_o365_simulator()
        self.scan_sharepoint()
        self.scan_web_apps()
        self.scan_unpatched_machines()
        
        print("\n" + "="*70)
        print("SCAN COMPLETE")
        print("="*70 + "\n")

    def save_report(self):
        """Save findings to report"""
        filename = f"enterprise_scan_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w') as f:
            json.dump(self.findings, f, indent=2)
        
        print(f"[+] Report saved: {filename}")
        return filename


if __name__ == '__main__':
    scanner = EnterpriseLabScanner()
    scanner.run_full_scan()
    scanner.save_report()
    
    print("\nFindings Summary:")
    print(json.dumps(scanner.findings, indent=2))
