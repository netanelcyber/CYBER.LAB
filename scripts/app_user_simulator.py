#!/usr/bin/env python3
"""
CYBER.LAB - Application User Simulator
Creates realistic application users and simulates user behavior across all lab services
"""

import random
import json
import hashlib
from datetime import datetime, timedelta
from typing import List, Dict
import requests
import subprocess

class ApplicationUserSimulator:
    def __init__(self):
        self.users = []
        self.logs = []
        self.app_users_db = {
            'drupal': [],
            'wordpress': [],
            'exchange': [],
            'sharepoint': [],
            'ldap': []
        }
        
    def create_user_personas(self) -> List[Dict]:
        """Create realistic user personas"""
        
        departments = ['IT', 'Finance', 'HR', 'Marketing', 'Engineering', 'Operations']
        roles = {
            'IT': ['System Admin', 'Network Admin', 'Help Desk', 'Security Officer'],
            'Finance': ['Accountant', 'Finance Manager', 'Controller', 'Auditor'],
            'HR': ['HR Manager', 'Recruiter', 'Compensation Analyst'],
            'Marketing': ['Marketing Manager', 'Content Creator', 'Social Media Manager'],
            'Engineering': ['Developer', 'DevOps', 'QA Engineer', 'Tech Lead'],
            'Operations': ['Operations Manager', 'Project Manager', 'Coordinator']
        }
        
        first_names = [
            'John', 'Sarah', 'Michael', 'Emily', 'David', 'Jessica', 
            'James', 'Lisa', 'Robert', 'Mary', 'William', 'Jennifer'
        ]
        
        last_names = [
            'Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia',
            'Miller', 'Davis', 'Rodriguez', 'Martinez', 'Taylor', 'Anderson'
        ]
        
        users = []
        user_id = 1000
        
        for dept in departments:
            dept_role = random.choice(roles[dept])
            for i in range(random.randint(2, 5)):
                first_name = random.choice(first_names)
                last_name = random.choice(last_names)
                username = f"{first_name.lower()}.{last_name.lower()}"
                
                user = {
                    'user_id': user_id,
                    'username': username,
                    'email': f"{username}@cyber.lab",
                    'first_name': first_name,
                    'last_name': last_name,
                    'department': dept,
                    'role': dept_role,
                    'employee_id': f"EMP{user_id}",
                    'password': self.generate_password(),
                    'created_date': (datetime.now() - timedelta(days=random.randint(30, 365))).isoformat(),
                    'last_login': (datetime.now() - timedelta(days=random.randint(0, 30))).isoformat(),
                    'status': 'active',
                    'permissions': self.assign_permissions(dept),
                    'applications': self.assign_applications(dept)
                }
                
                users.append(user)
                user_id += 1
        
        self.users = users
        return users
    
    def generate_password(self) -> str:
        """Generate secure password"""
        chars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%'
        password = ''.join(random.choice(chars) for _ in range(12))
        return password
    
    def assign_permissions(self, department: str) -> List[str]:
        """Assign permissions based on department"""
        perms = {
            'IT': ['admin', 'domain_admin', 'backup', 'security_audit'],
            'Finance': ['finance_reports', 'budget_access', 'ledger_view'],
            'HR': ['employee_records', 'payroll_view', 'benefits_admin'],
            'Marketing': ['content_create', 'social_media', 'analytics'],
            'Engineering': ['code_commit', 'deployment', 'ci_cd'],
            'Operations': ['project_management', 'resource_planning', 'reporting']
        }
        return perms.get(department, ['user'])
    
    def assign_applications(self, department: str) -> Dict:
        """Assign applications per department"""
        return {
            'drupal': True,
            'wordpress': department in ['Marketing', 'Operations'],
            'exchange': True,
            'sharepoint': True,
            'vpn': department == 'IT',
            'timesheet': True
        }
    
    def create_drupal_users(self):
        """Create users in Drupal 7"""
        print("[*] Creating Drupal users...")
        
        for user in self.users:
            if user['applications']['drupal']:
                drupal_user = {
                    'uid': user['user_id'],
                    'name': user['username'],
                    'mail': user['email'],
                    'pass': hashlib.md5(user['password'].encode()).hexdigest(),
                    'created': int(datetime.fromisoformat(user['created_date']).timestamp()),
                    'access': int(datetime.fromisoformat(user['last_login']).timestamp()),
                    'status': 1 if user['status'] == 'active' else 0,
                    'roles': self.get_drupal_roles(user['department']),
                    'timezone': 'UTC'
                }
                self.app_users_db['drupal'].append(drupal_user)
                print(f"  [+] Drupal user created: {user['username']}")
        
        return self.app_users_db['drupal']
    
    def get_drupal_roles(self, department: str) -> List[str]:
        """Get Drupal roles based on department"""
        roles = {
            'IT': ['administrator', 'site_manager'],
            'Finance': ['accountant', 'report_viewer'],
            'HR': ['human_resources', 'content_editor'],
            'Marketing': ['content_creator', 'editor'],
            'Engineering': ['developer', 'technical_staff'],
            'Operations': ['project_manager', 'staff']
        }
        return roles.get(department, ['authenticated'])
    
    def create_wordpress_users(self):
        """Create users in WordPress"""
        print("[*] Creating WordPress users...")
        
        for user in self.users:
            if user['applications']['wordpress']:
                wp_user = {
                    'ID': user['user_id'],
                    'user_login': user['username'],
                    'user_email': user['email'],
                    'user_registered': user['created_date'],
                    'user_pass': hashlib.md5(user['password'].encode()).hexdigest(),
                    'display_name': f"{user['first_name']} {user['last_name']}",
                    'user_status': 0,
                    'user_url': f"http://cyber.lab/author/{user['username']}/",
                    'capabilities': self.get_wordpress_capabilities(user['department'])
                }
                self.app_users_db['wordpress'].append(wp_user)
                print(f"  [+] WordPress user created: {user['username']}")
        
        return self.app_users_db['wordpress']
    
    def get_wordpress_capabilities(self, department: str) -> Dict:
        """Get WordPress user capabilities"""
        capabilities = {
            'Marketing': {'editor': True, 'publish_posts': True},
            'Engineering': {'author': True, 'upload_files': True, 'edit_posts': True},
            'Operations': {'contributor': True, 'upload_files': True}
        }
        return capabilities.get(department, {'subscriber': True})
    
    def create_exchange_mailboxes(self):
        """Create Exchange mailboxes"""
        print("[*] Creating Exchange mailboxes...")
        
        for user in self.users:
            mailbox = {
                'DisplayName': f"{user['first_name']} {user['last_name']}",
                'UserPrincipalName': user['email'],
                'SamAccountName': user['username'],
                'mailNickname': user['username'],
                'ProxyAddresses': [f"SMTP:{user['email']}"],
                'Department': user['department'],
                'Title': user['role'],
                'Manager': random.choice([u['email'] for u in self.users if u['department'] == user['department']]),
                'MailboxSize': f"{random.randint(50, 500)} MB",
                'ItemCount': random.randint(100, 5000),
                'CreatedDate': user['created_date'],
                'LastLogin': user['last_login']
            }
            self.app_users_db['exchange'].append(mailbox)
            print(f"  [+] Exchange mailbox created: {user['email']}")
        
        return self.app_users_db['exchange']
    
    def create_sharepoint_users(self):
        """Create SharePoint users and site permissions"""
        print("[*] Creating SharePoint users...")
        
        sites = ['/sites/company', '/sites/finance', '/sites/hr', '/sites/it']
        permissions = ['View', 'Contribute', 'Edit', 'Full Control']
        
        for user in self.users:
            sp_user = {
                'LoginName': f"cyber\\{user['username']}",
                'DisplayName': f"{user['first_name']} {user['last_name']}",
                'Email': user['email'],
                'Department': user['department'],
                'SitePermissions': []
            }
            
            # Assign permissions to sites
            for site in sites:
                if (site == '/sites/finance' and user['department'] == 'Finance') or \
                   (site == '/sites/hr' and user['department'] == 'HR') or \
                   (site == '/sites/it' and user['department'] == 'IT') or \
                   site == '/sites/company':
                    perm_level = random.choice(permissions[:2]) if user['department'] != 'IT' else random.choice(permissions)
                    sp_user['SitePermissions'].append({
                        'Site': site,
                        'PermissionLevel': perm_level
                    })
            
            self.app_users_db['sharepoint'].append(sp_user)
            print(f"  [+] SharePoint user created: {user['email']}")
        
        return self.app_users_db['sharepoint']
    
    def create_ldap_users(self):
        """Create LDAP/AD users"""
        print("[*] Creating LDAP/AD users...")
        
        for user in self.users:
            ldap_user = {
                'dn': f"cn={user['first_name']} {user['last_name']},ou={user['department']},dc=cyber,dc=lab",
                'cn': f"{user['first_name']} {user['last_name']}",
                'sAMAccountName': user['username'],
                'mail': user['email'],
                'departmentNumber': user['department'],
                'title': user['role'],
                'employeeNumber': user['employee_id'],
                'objectClass': ['person', 'organizationalPerson', 'user'],
                'userAccountControl': 512,  # Enabled
                'pwdLastSet': int(datetime.fromisoformat(user['created_date']).timestamp()),
                'lastLogon': int(datetime.fromisoformat(user['last_login']).timestamp()),
                'memberOf': self.get_ad_groups(user['department'])
            }
            self.app_users_db['ldap'].append(ldap_user)
            print(f"  [+] LDAP user created: {user['username']}")
        
        return self.app_users_db['ldap']
    
    def get_ad_groups(self, department: str) -> List[str]:
        """Get AD groups for user"""
        groups = {
            'IT': ['cn=IT-Admins,ou=IT,dc=cyber,dc=lab', 'cn=Domain Admins,cn=Builtin,dc=cyber,dc=lab'],
            'Finance': ['cn=Finance-Team,ou=Finance,dc=cyber,dc=lab'],
            'HR': ['cn=HR-Team,ou=HR,dc=cyber,dc=lab'],
            'Marketing': ['cn=Marketing-Team,ou=Marketing,dc=cyber,dc=lab'],
            'Engineering': ['cn=Engineering-Team,ou=Engineering,dc=cyber,dc=lab'],
            'Operations': ['cn=Operations-Team,ou=Operations,dc=cyber,dc=lab']
        }
        return groups.get(department, ['cn=Users,cn=Builtin,dc=cyber,dc=lab'])
    
    def simulate_user_activity(self):
        """Simulate user activity and logins"""
        print("[*] Simulating user activity...")
        
        activities = [
            'login',
            'email_send',
            'email_receive',
            'sharepoint_document_view',
            'sharepoint_document_edit',
            'drupal_content_view',
            'drupal_content_create',
            'wordpress_post_create',
            'file_access',
            'report_generate',
            'logout'
        ]
        
        for user in self.users[:5]:  # Simulate for first 5 users
            for _ in range(random.randint(3, 8)):
                activity = random.choice(activities)
                log_entry = {
                    'timestamp': (datetime.now() - timedelta(minutes=random.randint(0, 1440))).isoformat(),
                    'user': user['username'],
                    'email': user['email'],
                    'department': user['department'],
                    'activity': activity,
                    'application': random.choice(['drupal', 'wordpress', 'exchange', 'sharepoint']),
                    'status': 'SUCCESS',
                    'ip_address': f"172.28.{random.randint(0, 255)}.{random.randint(1, 254)}",
                    'user_agent': f"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                }
                self.logs.append(log_entry)
                print(f"  [+] Activity logged: {user['username']} - {activity}")
    
    def generate_report(self):
        """Generate comprehensive user report"""
        print("\n" + "="*70)
        print("APPLICATION USER SIMULATION REPORT")
        print("="*70 + "\n")
        
        print("SUMMARY:")
        print(f"  Total Users Created: {len(self.users)}")
        print(f"  Drupal Users: {len(self.app_users_db['drupal'])}")
        print(f"  WordPress Users: {len(self.app_users_db['wordpress'])}")
        print(f"  Exchange Mailboxes: {len(self.app_users_db['exchange'])}")
        print(f"  SharePoint Users: {len(self.app_users_db['sharepoint'])}")
        print(f"  LDAP/AD Users: {len(self.app_users_db['ldap'])}")
        print(f"  Total Activities Logged: {len(self.logs)}\n")
        
        print("USER DISTRIBUTION BY DEPARTMENT:")
        dept_count = {}
        for user in self.users:
            dept = user['department']
            dept_count[dept] = dept_count.get(dept, 0) + 1
        
        for dept, count in sorted(dept_count.items()):
            print(f"  ├─ {dept}: {count} users")
        
        print("\nSAMPLE USERS:")
        for user in self.users[:3]:
            print(f"  ├─ {user['first_name']} {user['last_name']} ({user['email']})")
            print(f"  │  Department: {user['department']}, Role: {user['role']}")
            print(f"  │  Permission Level: {', '.join(user['permissions'])}")
            print()
        
        print("="*70)
    
    def save_to_json(self, filename='app_users_simulation.json'):
        """Save simulation to JSON"""
        data = {
            'timestamp': datetime.now().isoformat(),
            'summary': {
                'total_users': len(self.users),
                'total_activities': len(self.logs),
                'drupal_users': len(self.app_users_db['drupal']),
                'wordpress_users': len(self.app_users_db['wordpress']),
                'exchange_mailboxes': len(self.app_users_db['exchange']),
                'sharepoint_users': len(self.app_users_db['sharepoint']),
                'ldap_users': len(self.app_users_db['ldap'])
            },
            'users': self.users,
            'app_users': self.app_users_db,
            'activity_logs': self.logs
        }
        
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"\n[+] Simulation saved to {filename}")
        return filename
    
    def run_full_simulation(self):
        """Run complete user simulation"""
        print("\n╔" + "="*68 + "╗")
        print("║" + " APPLICATION USER SIMULATOR ".center(68) + "║")
        print("╚" + "="*68 + "╝\n")
        
        print("[*] Phase 1: Creating user personas...")
        self.create_user_personas()
        print(f"[+] Created {len(self.users)} user personas\n")
        
        print("[*] Phase 2: Creating application users...")
        self.create_drupal_users()
        print()
        self.create_wordpress_users()
        print()
        self.create_exchange_mailboxes()
        print()
        self.create_sharepoint_users()
        print()
        self.create_ldap_users()
        print()
        
        print("[*] Phase 3: Simulating user activities...")
        self.simulate_user_activity()
        print()
        
        self.generate_report()
        self.save_to_json()


if __name__ == '__main__':
    simulator = ApplicationUserSimulator()
    simulator.run_full_simulation()
    
    print("\n[+] User simulation complete!")
    print("\nUsage with curl/ldapsearch:")
    print("  ldapsearch -x -H ldap://localhost:389 -b 'dc=cyber,dc=lab' 'objectClass=user'")
    print("\nLogin credentials can be imported into:")
    print("  - Drupal at: http://localhost:8001 (/user/login)")
    print("  - WordPress at: http://localhost:8002 (/wp-login.php)")
    print("  - Exchange IMAP: telnet localhost 143")
    print("  - SharePoint: http://localhost:8080")
