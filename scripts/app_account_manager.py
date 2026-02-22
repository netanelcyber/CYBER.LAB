#!/usr/bin/env python3
"""
CYBER.LAB - Application Account Manager
Advanced account management and password handling across applications
"""

import json
import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Dict, List

class ApplicationAccountManager:
    def __init__(self):
        self.accounts = {}
        self.password_policies = {}
        self.account_lifecycles = []
        
    def set_password_policy(self, app_name: str, config: Dict):
        """Set password policy for application"""
        self.password_policies[app_name] = {
            'min_length': config.get('min_length', 8),
            'require_uppercase': config.get('require_uppercase', True),
            'require_lowercase': config.get('require_lowercase', True),
            'require_digits': config.get('require_digits', True),
            'require_special': config.get('require_special', False),
            'expiration_days': config.get('expiration_days', 90),
            'history_count': config.get('history_count', 5),
            'lockout_attempts': config.get('lockout_attempts', 3),
            'lockout_duration_minutes': config.get('lockout_duration_minutes', 30)
        }
    
    def generate_password(self, policy: Dict) -> str:
        """Generate password following policy"""
        chars = ''
        
        if policy.get('require_lowercase', True):
            chars += 'abcdefghijklmnopqrstuvwxyz'
        if policy.get('require_uppercase', True):
            chars += 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        if policy.get('require_digits', True):
            chars += '0123456789'
        if policy.get('require_special', False):
            chars += '!@#$%^&*()'
        
        min_length = policy.get('min_length', 12)
        password = ''.join(secrets.choice(chars) for _ in range(min_length))
        
        return password
    
    def create_account(self, username: str, email: str, app: str, 
                      department: str, role: str) -> Dict:
        """Create application account"""
        
        policy = self.password_policies.get(app, {
            'min_length': 12,
            'require_uppercase': True,
            'require_lowercase': True,
            'require_digits': True,
            'expiration_days': 90
        })
        
        password = self.generate_password(policy)
        
        account = {
            'username': username,
            'email': email,
            'application': app,
            'department': department,
            'role': role,
            'password_hash': hashlib.sha256(password.encode()).hexdigest(),
            'created_date': datetime.now().isoformat(),
            'last_password_change': datetime.now().isoformat(),
            'password_expires': (datetime.now() + timedelta(days=policy['expiration_days'])).isoformat(),
            'account_status': 'active',
            'failed_login_attempts': 0,
            'last_login': None,
            'password_history': [hashlib.sha256(password.encode()).hexdigest()],
            'mfa_enabled': False,
            'groups': []
        }
        
        key = f"{app}_{username}"
        self.accounts[key] = account
        
        self.account_lifecycles.append({
            'action': 'CREATE',
            'username': username,
            'application': app,
            'timestamp': datetime.now().isoformat(),
            'status': 'SUCCESS'
        })
        
        return account
    
    def set_mfa(self, username: str, app: str, enabled: bool = True) -> bool:
        """Enable/disable MFA for account"""
        key = f"{app}_{username}"
        
        if key in self.accounts:
            self.accounts[key]['mfa_enabled'] = enabled
            self.account_lifecycles.append({
                'action': 'MFA_CHANGE',
                'username': username,
                'application': app,
                'mfa_enabled': enabled,
                'timestamp': datetime.now().isoformat()
            })
            return True
        
        return False
    
    def reset_password(self, username: str, app: str) -> str:
        """Reset user password"""
        key = f"{app}_{username}"
        
        if key not in self.accounts:
            return None
        
        policy = self.password_policies.get(app, {})
        new_password = self.generate_password(policy)
        new_hash = hashlib.sha256(new_password.encode()).hexdigest()
        
        account = self.accounts[key]
        
        # Save to password history
        if len(account['password_history']) >= policy.get('history_count', 5):
            account['password_history'].pop(0)
        account['password_history'].append(new_hash)
        
        account['password_hash'] = new_hash
        account['last_password_change'] = datetime.now().isoformat()
        account['password_expires'] = (datetime.now() + timedelta(
            days=policy.get('expiration_days', 90)
        )).isoformat()
        account['failed_login_attempts'] = 0
        
        self.account_lifecycles.append({
            'action': 'PASSWORD_RESET',
            'username': username,
            'application': app,
            'timestamp': datetime.now().isoformat(),
            'status': 'SUCCESS'
        })
        
        return new_password
    
    def disable_account(self, username: str, app: str, reason: str = "") -> bool:
        """Disable user account"""
        key = f"{app}_{username}"
        
        if key not in self.accounts:
            return False
        
        self.accounts[key]['account_status'] = 'disabled'
        self.account_lifecycles.append({
            'action': 'ACCOUNT_DISABLE',
            'username': username,
            'application': app,
            'reason': reason,
            'timestamp': datetime.now().isoformat()
        })
        
        return True
    
    def list_accounts_by_app(self, app: str) -> List[Dict]:
        """List all accounts for an application"""
        return [acc for key, acc in self.accounts.items() if acc['application'] == app]
    
    def check_password_expiration(self) -> List[Dict]:
        """Check for expiring passwords"""
        expiring = []
        today = datetime.now()
        
        for key, account in self.accounts.items():
            expires = datetime.fromisoformat(account['password_expires'])
            days_until_expiry = (expires - today).days
            
            if 0 <= days_until_expiry <= 14:
                expiring.append({
                    'username': account['username'],
                    'application': account['application'],
                    'days_until_expiry': days_until_expiry,
                    'expires': account['password_expires']
                })
        
        return expiring
    
    def generate_audit_report(self) -> Dict:
        """Generate account audit report"""
        total_accounts = len(self.accounts)
        active_accounts = sum(1 for acc in self.accounts.values() if acc['account_status'] == 'active')
        disabled_accounts = total_accounts - active_accounts
        mfa_enabled = sum(1 for acc in self.accounts.values() if acc['mfa_enabled'])
        
        return {
            'report_date': datetime.now().isoformat(),
            'total_accounts': total_accounts,
            'active_accounts': active_accounts,
            'disabled_accounts': disabled_accounts,
            'mfa_enabled': mfa_enabled,
            'mfa_percentage': f"{(mfa_enabled/total_accounts*100):.1f}%" if total_accounts > 0 else "0%",
            'expiring_passwords': self.check_password_expiration(),
            'account_lifecycles': self.account_lifecycles[-50:]  # Last 50 actions
        }


class DefaultApplicationPolicies:
    """Pre-configured password policies for common applications"""
    
    @staticmethod
    def get_all_policies() -> Dict:
        return {
            'drupal': {
                'min_length': 12,
                'require_uppercase': True,
                'require_lowercase': True,
                'require_digits': True,
                'require_special': True,
                'expiration_days': 90,
                'history_count': 5,
                'lockout_attempts': 5,
                'lockout_duration_minutes': 15
            },
            'wordpress': {
                'min_length': 10,
                'require_uppercase': True,
                'require_lowercase': True,
                'require_digits': True,
                'require_special': False,
                'expiration_days': 90,
                'history_count': 3,
                'lockout_attempts': 5,
                'lockout_duration_minutes': 30
            },
            'exchange': {
                'min_length': 14,
                'require_uppercase': True,
                'require_lowercase': True,
                'require_digits': True,
                'require_special': True,
                'expiration_days': 60,
                'history_count': 10,
                'lockout_attempts': 3,
                'lockout_duration_minutes': 30
            },
            'sharepoint': {
                'min_length': 12,
                'require_uppercase': True,
                'require_lowercase': True,
                'require_digits': True,
                'require_special': True,
                'expiration_days': 90,
                'history_count': 5,
                'lockout_attempts': 5,
                'lockout_duration_minutes': 20
            },
            'ldap_ad': {
                'min_length': 15,
                'require_uppercase': True,
                'require_lowercase': True,
                'require_digits': True,
                'require_special': True,
                'expiration_days': 90,
                'history_count': 24,
                'lockout_attempts': 3,
                'lockout_duration_minutes': 30
            }
        }


def demo_account_management():
    """Demo account management"""
    manager = ApplicationAccountManager()
    policies = DefaultApplicationPolicies.get_all_policies()
    
    # Set policies for each app
    for app, policy in policies.items():
        manager.set_password_policy(app, policy)
    
    print("\n╔════════════════════════════════════════════════════════════════════╗")
    print("║           APPLICATION ACCOUNT MANAGEMENT DEMONSTRATION             ║")
    print("╚════════════════════════════════════════════════════════════════════╝\n")
    
    # Create sample accounts
    print("[*] Creating sample accounts...\n")
    
    sample_users = [
        {'username': 'john.smith', 'email': 'john.smith@cyber.lab', 'dept': 'IT'},
        {'username': 'sarah.jones', 'email': 'sarah.jones@cyber.lab', 'dept': 'Finance'},
        {'username': 'mike.davis', 'email': 'mike.davis@cyber.lab', 'dept': 'HR'}
    ]
    
    for app in ['drupal', 'exchange', 'sharepoint']:
        print(f"Creating accounts in {app.upper()}:")
        for user in sample_users:
            account = manager.create_account(
                username=user['username'],
                email=user['email'],
                app=app,
                department=user['dept'],
                role='User'
            )
            print(f"  [+] {user['username']} - {app}")
        print()
    
    # Enable MFA
    print("[*] Enabling MFA...")
    manager.set_mfa('john.smith', 'exchange', True)
    print("[+] MFA enabled for john.smith on Exchange\n")
    
    # Show audit report
    print("[*] Account Audit Report:")
    report = manager.generate_audit_report()
    print(f"  Total Accounts: {report['total_accounts']}")
    print(f"  Active Accounts: {report['active_accounts']}")
    print(f"  MFA Enabled: {report['mfa_enabled']} ({report['mfa_percentage']})\n")
    
    # List accounts
    print("[*] Drupal Accounts:")
    for acc in manager.list_accounts_by_app('drupal'):
        print(f"  ├─ {acc['username']} ({acc['account_status']})")
    
    print("\n[+] Account management demonstration complete!")


if __name__ == '__main__':
    demo_account_management()
