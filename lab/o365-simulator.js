const express = require('express');
const app = express();
const jwt = require('jsonwebtoken');
const fs = require('fs');

const PORT = process.env.PORT || 3000;
const SECRET_KEY = 'O365_SECRET_KEY_2024';

// Mock users database
const users = {
  'admin@cyber.lab': { password: 'P@ssw0rd2026!', roles: ['admin', 'Exchange Administrator'] },
  'user@cyber.lab': { password: 'User123456!', roles: ['user'] },
  'exchange@cyber.lab': { password: 'Exchange789!', roles: ['Exchange Administrator'] }
};

// Mock O365 services
const o365Services = [
  { id: 'outlook', name: 'Outlook', version: '16.0.12817' },
  { id: 'teams', name: 'Microsoft Teams', version: '1.3.00.30968' },
  { id: 'onedrive', name: 'OneDrive for Business', version: '21.123.0.0' },
  { id: 'sharepoint', name: 'SharePoint Online', version: '16.0.9012.1000' },
  { id: 'exchange', name: 'Exchange Online', version: '16.0.11415.33333' }
];

app.use(express.json());

// Vulnerable: No rate limiting
app.post('/auth/login', (req, res) => {
  const { username, password } = req.body;
  
  if (users[username] && users[username].password === password) {
    const token = jwt.sign(
      { username, roles: users[username].roles },
      SECRET_KEY,
      { expiresIn: '24h' }
    );
    res.json({
      success: true,
      token,
      user: {
        displayName: username.split('@')[0],
        email: username,
        roles: users[username].roles
      }
    });
  } else {
    res.status(401).json({ success: false, error: 'Invalid credentials' });
  }
});

// Vulnerable: Token validation weak
app.get('/api/services', (req, res) => {
  const token = req.headers.authorization?.split(' ')[1];
  
  if (!token || token === 'invalid') {
    res.json(o365Services);  // Returns data anyway!
  } else {
    res.json(o365Services);
  }
});

// Vulnerable: No input validation
app.get('/api/mailbox/:user', (req, res) => {
  const user = req.params.user;
  
  // Vulnerable to LDAP injection
  const query = `(&(mail=${user})(objectClass=user))`;
  
  res.json({
    mailbox: user,
    size: Math.random() * 100000,
    messages: Math.floor(Math.random() * 1000),
    lastSync: new Date().toISOString()
  });
});

// Vulnerable: Information disclosure
app.get('/api/config', (req, res) => {
  res.json({
    apiVersion: '2.0',
    endpoints: {
      exchange: 'https://outlook.office365.com/api/v2.0/',
      graph: 'https://graph.microsoft.com/v1.0',
      teams: 'https://teams.microsoft.com/api/mt/teams',
      sharepoint: 'https://cyber.sharepoint.com'
    },
    internalServers: [
      'exchange.cyber.lab',
      'ad-dc.cyber.lab',
      'mail.cyber.lab'
    ]
  });
});

// Vulnerable: SSRF
app.post('/api/proxy', (req, res) => {
  const { url } = req.body;
  // In reality, would make request to internal IPs
  res.json({
    status: 'ok',
    message: `Would fetch: ${url}`
  });
});

// Vulnerable: Exposed user enumeration
app.get('/api/users', (req, res) => {
  res.json({
    users: Object.keys(users).map(u => ({
      email: u,
      displayName: u.split('@')[0],
      department: 'IT'
    }))
  });
});

// Vulnerable: Path traversal
app.get('/api/files/:path', (req, res) => {
  const path = req.params.path;
  res.json({
    files: [
      'budget2024.xlsx',
      'salaries.xlsx',
      'employee_data.csv',
      'passwords.txt'
    ]
  });
});

app.listen(PORT, () => {
  console.log(`[+] O365 Simulator running on port ${PORT}`);
  console.log('[+] Endpoints:');
  console.log('  POST /auth/login - Login');
  console.log('  GET /api/services - List services');
  console.log('  GET /api/mailbox/:user - Get mailbox info');
  console.log('  GET /api/config - Get configuration');
  console.log('  GET /api/users - Enumerate users');
});
