# AI Audit Agent - Deployment Guide

Complete guide for deploying AI Audit Agent to production environments.

## 🎯 Deployment Options

1. **Docker Container** (Recommended)
2. **Cloud Platforms** (AWS, GCP, Azure)
3. **Traditional VPS** (DigitalOcean, Linode, etc.)
4. **Kubernetes** (For scale)

---

## 🐳 Docker Deployment

### Prerequisites

- Docker installed
- Docker Compose (optional but recommended)
- Domain name (for HTTPS)

### Quick Deploy with Docker Compose

1. **Create docker-compose.yml**

```yaml
version: '3.8'

services:
  ai-audit-agent:
    build: .
    container_name: ai-audit-agent
    ports:
      - "8000:8000"
    environment:
      - HF_API_KEY=${HF_API_KEY}
      - SENDER_EMAIL=${SENDER_EMAIL}
      - SMTP_PASSWORD=${SMTP_PASSWORD}
      - SMTP_HOST=smtp.gmail.com
      - SMTP_PORT=465
      - LOG_LEVEL=INFO
    restart: unless-stopped
    volumes:
      - ./logs:/app/logs
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 10s
```

2. **Create .env file**

```bash
HF_API_KEY=your_huggingface_api_key
SENDER_EMAIL=your-email@gmail.com
SMTP_PASSWORD=your_gmail_app_password
```

3. **Deploy**

```bash
docker-compose up -d
```

4. **Check Status**

```bash
docker-compose ps
docker-compose logs -f
```

---

## ☁️ AWS Deployment

### Option 1: EC2 Instance

**1. Launch EC2 Instance**

```bash
# Choose Ubuntu 22.04 LTS
# Instance type: t3.medium (2 vCPU, 4GB RAM)
# Security Group: Allow port 80, 443, 8000
```

**2. Connect and Install Docker**

```bash
ssh -i your-key.pem ubuntu@your-ec2-ip

# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker ubuntu

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Logout and login again
exit
```

**3. Clone and Deploy**

```bash
# Create app directory
mkdir ai-audit-agent
cd ai-audit-agent

# Upload your files (using scp or git)
scp -i your-key.pem -r * ubuntu@your-ec2-ip:~/ai-audit-agent/

# Or use git
git clone your-repo-url .

# Create .env file
nano .env
# Add your environment variables

# Deploy
docker-compose up -d
```

**4. Configure Nginx (Optional)**

```bash
sudo apt install nginx -y

# Create Nginx config
sudo nano /etc/nginx/sites-available/ai-audit-agent
```

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/ai-audit-agent /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

**5. Setup SSL with Let's Encrypt**

```bash
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d your-domain.com
```

### Option 2: AWS ECS (Elastic Container Service)

**1. Create ECR Repository**

```bash
aws ecr create-repository --repository-name ai-audit-agent
```

**2. Build and Push Image**

```bash
# Login to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin your-account-id.dkr.ecr.us-east-1.amazonaws.com

# Build image
docker build -t ai-audit-agent .

# Tag image
docker tag ai-audit-agent:latest your-account-id.dkr.ecr.us-east-1.amazonaws.com/ai-audit-agent:latest

# Push image
docker push your-account-id.dkr.ecr.us-east-1.amazonaws.com/ai-audit-agent:latest
```

**3. Create ECS Task Definition** (via AWS Console or CLI)

**4. Create ECS Service**

**5. Configure Load Balancer**

---

## 🌐 Google Cloud Platform (GCP)

### Cloud Run Deployment (Serverless)

**1. Install gcloud CLI**

```bash
# Install gcloud
curl https://sdk.cloud.google.com | bash
gcloud init
```

**2. Deploy to Cloud Run**

```bash
# Build and deploy in one command
gcloud run deploy ai-audit-agent \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars HF_API_KEY="your-key",SENDER_EMAIL="your-email",SMTP_PASSWORD="your-password"
```

**3. Get Service URL**

```bash
gcloud run services describe ai-audit-agent --region us-central1 --format 'value(status.url)'
```

### Compute Engine (VM)

Similar to AWS EC2 deployment.

---

## 🔷 Microsoft Azure

### Azure Container Instances

**1. Create Resource Group**

```bash
az group create --name ai-audit-agent-rg --location eastus
```

**2. Create Container Registry**

```bash
az acr create --resource-group ai-audit-agent-rg --name aiauditagent --sku Basic
```

**3. Build and Push Image**

```bash
az acr build --registry aiauditagent --image ai-audit-agent:latest .
```

**4. Deploy Container**

```bash
az container create \
  --resource-group ai-audit-agent-rg \
  --name ai-audit-agent \
  --image aiauditagent.azurecr.io/ai-audit-agent:latest \
  --dns-name-label ai-audit-agent-unique \
  --ports 8000 \
  --environment-variables \
    HF_API_KEY="your-key" \
    SENDER_EMAIL="your-email" \
    SMTP_PASSWORD="your-password"
```

---

## 🖥️ Traditional VPS (DigitalOcean, Linode, Vultr)

**1. Create Droplet/Server**

- OS: Ubuntu 22.04
- Size: 2GB RAM minimum
- Add SSH key

**2. Initial Setup**

```bash
# Login
ssh root@your-server-ip

# Create user
adduser deploy
usermod -aG sudo deploy
su - deploy

# Update system
sudo apt update && sudo apt upgrade -y
```

**3. Install Dependencies**

```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker deploy

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

**4. Deploy Application**

```bash
# Create directory
mkdir ~/ai-audit-agent
cd ~/ai-audit-agent

# Upload files or clone repo
git clone your-repo-url .

# Setup environment
cp .env.example .env
nano .env  # Edit with your values

# Deploy
docker-compose up -d
```

**5. Setup Firewall**

```bash
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

---

## ⚙️ Production Configuration

### 1. Environment Variables

Create production `.env`:

```bash
# LLM Configuration
HF_API_KEY=your_production_key
HF_MODEL_URL=https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.1

# Email Configuration
SENDER_EMAIL=noreply@yourdomain.com
SMTP_PASSWORD=your_app_password
SMTP_HOST=smtp.gmail.com
SMTP_PORT=465

# Application
LOG_LEVEL=INFO
OUTPUT_DIR=/tmp/ai_audit_reports

# Optional: Monitoring
SENTRY_DSN=your_sentry_dsn
```

### 2. Nginx Configuration

**Full Production Config:**

```nginx
# /etc/nginx/sites-available/ai-audit-agent

upstream ai_audit {
    server 127.0.0.1:8000;
}

# Rate limiting
limit_req_zone $binary_remote_addr zone=audit_limit:10m rate=10r/m;

server {
    listen 80;
    server_name your-domain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;

    # SSL Configuration
    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    # Security Headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;
    add_header Content-Security-Policy "default-src 'self' http: https: data: blob: 'unsafe-inline'" always;

    # Logging
    access_log /var/log/nginx/ai-audit-access.log;
    error_log /var/log/nginx/ai-audit-error.log;

    location / {
        proxy_pass http://ai_audit;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Timeouts for long-running requests
        proxy_connect_timeout 120s;
        proxy_send_timeout 120s;
        proxy_read_timeout 120s;
    }

    location /webhook/sheet-row {
        limit_req zone=audit_limit burst=5 nodelay;
        
        proxy_pass http://ai_audit;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Longer timeout for webhook
        proxy_read_timeout 180s;
    }

    location /health {
        proxy_pass http://ai_audit;
        access_log off;
    }
}
```

### 3. Systemd Service (Non-Docker)

If not using Docker:

```ini
# /etc/systemd/system/ai-audit-agent.service

[Unit]
Description=AI Audit Agent
After=network.target

[Service]
Type=simple
User=deploy
WorkingDirectory=/home/deploy/ai-audit-agent
Environment="PATH=/home/deploy/.local/bin:/usr/local/bin:/usr/bin:/bin"
EnvironmentFile=/home/deploy/ai-audit-agent/.env
ExecStart=/home/deploy/.local/bin/uvicorn main:app --host 0.0.0.0 --port 8000 --workers 2
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
sudo systemctl enable ai-audit-agent
sudo systemctl start ai-audit-agent
sudo systemctl status ai-audit-agent
```

---

## 📊 Monitoring & Logging

### 1. Application Logs

```bash
# Docker
docker-compose logs -f

# Systemd
journalctl -u ai-audit-agent -f

# Direct
tail -f /var/log/ai-audit-agent.log
```

### 2. Nginx Logs

```bash
tail -f /var/log/nginx/ai-audit-access.log
tail -f /var/log/nginx/ai-audit-error.log
```

### 3. Setup Log Rotation

```bash
sudo nano /etc/logrotate.d/ai-audit-agent
```

```
/var/log/ai-audit-agent.log {
    daily
    rotate 14
    compress
    delaycompress
    notifempty
    missingok
    create 0640 deploy deploy
}
```

---

## 🔒 Security Checklist

- [ ] Use HTTPS/SSL certificates
- [ ] Enable firewall (ufw/iptables)
- [ ] Use strong passwords/keys
- [ ] Keep secrets in environment variables
- [ ] Update system packages regularly
- [ ] Enable fail2ban for SSH
- [ ] Implement rate limiting
- [ ] Use security headers
- [ ] Regular backups
- [ ] Monitor logs for suspicious activity

---

## 🔄 CI/CD Pipeline

### GitHub Actions Example

```yaml
# .github/workflows/deploy.yml

name: Deploy AI Audit Agent

on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Build Docker image
      run: docker build -t ai-audit-agent .
    
    - name: Deploy to server
      env:
        SSH_PRIVATE_KEY: ${{ secrets.SSH_PRIVATE_KEY }}
        SERVER_IP: ${{ secrets.SERVER_IP }}
      run: |
        echo "$SSH_PRIVATE_KEY" > key.pem
        chmod 600 key.pem
        scp -i key.pem -r * deploy@$SERVER_IP:~/ai-audit-agent/
        ssh -i key.pem deploy@$SERVER_IP "cd ~/ai-audit-agent && docker-compose up -d --build"
```

---

## 🆘 Troubleshooting

### Service Won't Start

```bash
# Check logs
docker-compose logs

# Check port availability
sudo netstat -tulpn | grep 8000

# Verify environment variables
docker-compose config
```

### Cannot Connect

```bash
# Check if service is running
curl http://localhost:8000/health

# Check firewall
sudo ufw status

# Check Nginx
sudo nginx -t
sudo systemctl status nginx
```

### High Memory Usage

```bash
# Limit container memory
docker-compose.yml:
  services:
    ai-audit-agent:
      mem_limit: 2g
```

---

## 📞 Support

For deployment issues, check:
1. Application logs
2. Nginx logs (if using)
3. Docker logs
4. System logs

---

**Happy Deploying! 🚀**
