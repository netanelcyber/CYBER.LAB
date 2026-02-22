const express = require('express');
const app = express();
const fs = require('fs');
const path = require('path');

const PORT = process.env.PORT || 3000;

// Mock SharePoint/OneDrive data
const documents = {
  'admin': [
    { id: 1, name: 'Budget2024.xlsx', size: 2048576, created: '2024-01-15', owner: 'admin' },
    { id: 2, name: 'CompanyStrategy.docx', size: 1048576, created: '2024-02-01', owner: 'admin' },
    { id: 3, name: 'Credentials.txt', size: 2048, created: '2024-02-10', owner: 'admin' },
    { id: 4, name: 'VPN_Config.ovpn', size: 4096, created: '2024-02-12', owner: 'admin' }
  ],
  'user': [
    { id: 5, name: 'ProjectFiles.zip', size: 5242880, created: '2024-02-14', owner: 'user' },
    { id: 6, name: 'Presentation.pptx', size: 3145728, created: '2024-02-15', owner: 'user' }
  ]
};

const sites = [
  { id: 'company', name: 'Company Portal', url: '/sites/company' },
  { id: 'hr', name: 'HR Department', url: '/sites/hr' },
  { id: 'it', name: 'IT Services', url: '/sites/it' },
  { id: 'finance', name: 'Finance', url: '/sites/finance' }
];

app.use(express.json());

// Vulnerable: No authentication required
app.get('/api/sites', (req, res) => {
  res.json({ sites });
});

// Vulnerable: Directory traversal
app.get('/api/documents/:folder', (req, res) => {
  const folder = req.params.folder;
  const docs = documents[folder] || documents['user'];
  res.json({ documents: docs });
});

// Vulnerable: Unauthorized access to any user's files
app.get('/api/user/:username/files', (req, res) => {
  const username = req.params.username;
  const docs = documents[username] || { files: [] };
  res.json({
    owner: username,
    files: docs
  });
});

// Vulnerable: File access without proper checks
app.get('/api/file/:id', (req, res) => {
  const fileId = parseInt(req.params.id);
  
  for (let user in documents) {
    const doc = documents[user].find(d => d.id === fileId);
    if (doc) {
      res.json({
        file: doc,
        content: `This would be the content of ${doc.name}`,
        server: 'sharepoint.cyber.lab',
        version: '16.0.9012.1000'
      });
      return;
    }
  }
  
  res.status(404).json({ error: 'File not found' });
});

// Vulnerable: List all files from all users
app.get('/api/all-documents', (req, res) => {
  const allDocs = [];
  for (let user in documents) {
    documents[user].forEach(doc => {
      allDocs.push({ ...doc, owner: user });
    });
  }
  res.json({ allDocuments: allDocs });
});

// Vulnerable: Metadata exposure
app.get('/api/file/:id/metadata', (req, res) => {
  res.json({
    fileId: req.params.id,
    metadata: {
      createdBy: 'admin@cyber.lab',
      lastModifiedBy: 'admin@cyber.lab',
      serverRelativeUrl: '/sites/company/documents/sensible.xlsx',
      versions: [
        { versionLabel: '1.0', modified: '2024-01-01' },
        { versionLabel: '2.0', modified: '2024-01-15' }
      ]
    }
  });
});

// Vulnerable: SSRF via URL
app.post('/api/open-file', (req, res) => {
  const { url } = req.body;
  res.json({
    status: 'file_accessed',
    url: url,
    content: 'Simulated file content'
  });
});

// Vulnerable: Sync external links
app.post('/api/share', (req, res) => {
  const { fileId, email } = req.body;
  res.json({
    status: 'shared',
    fileId,
    sharedWith: email,
    link: `https://cyber.sharepoint.com/files/share?id=${fileId}&token=INSECURE_TOKEN`,
    expiration: null  // No expiration!
  });
});

app.listen(PORT, () => {
  console.log(`[+] SharePoint/OneDrive Simulator running on port ${PORT}`);
  console.log('[+] Vulnerable endpoints:');
  console.log('  GET /api/sites - List all sites');
  console.log('  GET /api/documents/:folder - List documents');
  console.log('  GET /api/user/:username/files - Access user files');
  console.log('  GET /api/all-documents - Enumerate all files');
  console.log('  GET /api/file/:id - Download file');
});
