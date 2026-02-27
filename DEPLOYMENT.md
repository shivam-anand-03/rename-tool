# VM Deployment Guide - File Rename Tool

This guide provides instructions for deploying the File Rename Tool on a Virtual Machine (VM).

## Table of Contents
- [Prerequisites](#prerequisites)
- [Deployment Options](#deployment-options)
  - [Option 1: Docker Compose (Recommended)](#option-1-docker-compose-recommended)
  - [Option 2: Docker (Manual)](#option-2-docker-manual)
  - [Option 3: Native Python](#option-3-native-python)
- [Production Configuration](#production-configuration)
- [Nginx Reverse Proxy Setup](#nginx-reverse-proxy-setup)
- [SSL/HTTPS Setup](#sslhttps-setup)
- [Firewall Configuration](#firewall-configuration)
- [Monitoring & Logs](#monitoring--logs)
- [Troubleshooting](#troubleshooting)

## Prerequisites

### VM Requirements
- **OS**: Ubuntu 20.04/22.04 LTS or CentOS 7+
- **RAM**: Minimum 1GB, Recommended 2GB+
- **Storage**: Minimum 10GB free space
- **CPU**: 1+ cores
- **Network**: Public IP or accessible network

### Software Requirements
- Docker & Docker Compose (for Docker deployment)
- Python 3.8+ (for native deployment)
- Nginx (optional, for reverse proxy)
- Git (for cloning repository)

---

## Deployment Options

### Option 1: Docker Compose (Recommended)

This is the easiest and recommended method for production deployment.

#### 1. Install Docker and Docker Compose

**Ubuntu/Debian:**
```bash
# Update package index
sudo apt update

# Install dependencies
sudo apt install -y apt-transport-https ca-certificates curl software-properties-common

# Add Docker's official GPG key
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

# Add Docker repository
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Install Docker
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Add current user to docker group
sudo usermod -aG docker $USER

# Log out and log back in, or run:
newgrp docker
```

**CentOS/RHEL:**
```bash
sudo yum install -y yum-utils
sudo yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
sudo yum install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -aG docker $USER
```

#### 2. Clone the Repository

```bash
cd ~
git clone <your-repository-url>
cd rename-tool
```

Or upload your files manually:
```bash
mkdir -p ~/rename-tool
cd ~/rename-tool
# Upload files via SCP, SFTP, or other method
```

#### 3. Configure Environment (Optional)

Edit `docker-compose.yml` if you need to change the port:
```yaml
ports:
  - "5173:5173"  # Change first port to desired external port
```

#### 4. Deploy

```bash
# Build and start the container
docker compose up -d --build

# Check if running
docker compose ps

# View logs
docker compose logs -f
```

#### 5. Verify

```bash
curl http://localhost:5173
```

Your app should now be accessible at `http://<your-vm-ip>:5173`

#### 6. Manage the Application

```bash
# Stop the application
docker compose down

# Restart the application
docker compose restart

# View logs
docker compose logs -f

# Update application (after code changes)
docker compose down
docker compose up -d --build
```

---

### Option 2: Docker (Manual)

#### 1. Install Docker (see Option 1, step 1)

#### 2. Clone/Upload Files (see Option 1, step 2)

#### 3. Build Docker Image

```bash
cd ~/rename-tool
docker build -t rename-tool:latest .
```

#### 4. Run Container

```bash
docker run -d \
  --name rename-tool \
  -p 5173:5173 \
  -v /tmp/uploads:/tmp/uploads \
  --restart unless-stopped \
  rename-tool:latest
```

#### 5. Manage Container

```bash
# View logs
docker logs -f rename-tool

# Stop container
docker stop rename-tool

# Start container
docker start rename-tool

# Restart container
docker restart rename-tool

# Remove container
docker rm -f rename-tool

# Update (rebuild and run)
docker stop rename-tool
docker rm rename-tool
docker build -t rename-tool:latest .
docker run -d --name rename-tool -p 5173:5173 -v /tmp/uploads:/tmp/uploads --restart unless-stopped rename-tool:latest
```

---

### Option 3: Native Python

For development or when Docker is not available.

#### 1. Install Python

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install -y python3 python3-pip python3-venv
```

**CentOS/RHEL:**
```bash
sudo yum install -y python3 python3-pip
```

#### 2. Clone/Upload Files

```bash
cd ~
git clone <your-repository-url>
cd rename-tool
```

#### 3. Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate
```

#### 4. Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

#### 5. Run Application

**For Development:**
```bash
python app.py
```

**For Production (with Gunicorn):**
```bash
# Install Gunicorn
pip install gunicorn

# Run with Gunicorn
gunicorn --bind 0.0.0.0:5173 --workers 4 --timeout 300 app:app
```

#### 6. Create Systemd Service (Production)

Create `/etc/systemd/system/rename-tool.service`:

```ini
[Unit]
Description=File Rename Tool
After=network.target

[Service]
Type=simple
User=<your-username>
WorkingDirectory=/home/<your-username>/rename-tool
Environment="PATH=/home/<your-username>/rename-tool/venv/bin"
ExecStart=/home/<your-username>/rename-tool/venv/bin/gunicorn --bind 0.0.0.0:5173 --workers 4 --timeout 300 app:app
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl daemon-reload
sudo systemctl enable rename-tool
sudo systemctl start rename-tool
sudo systemctl status rename-tool
```

---

## Production Configuration

### 1. Disable Debug Mode

Edit `app.py`:
```python
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5173, debug=False)  # Set debug=False
```

### 2. Set Production Environment Variables

```bash
export FLASK_ENV=production
export PYTHONDONTWRITEBYTECODE=1
export PYTHONUNBUFFERED=1
```

### 3. Increase File Upload Limits (if needed)

Edit `app.py`:
```python
app.config['MAX_CONTENT_LENGTH'] = 1024 * 1024 * 1024  # 1GB
```

---

## Nginx Reverse Proxy Setup

Using Nginx as a reverse proxy provides better performance, SSL termination, and security.

### 1. Install Nginx

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install -y nginx
```

**CentOS/RHEL:**
```bash
sudo yum install -y nginx
sudo systemctl start nginx
sudo systemctl enable nginx
```

### 2. Configure Nginx

Create `/etc/nginx/sites-available/rename-tool`:

```nginx
server {
    listen 80;
    server_name your-domain.com;  # Replace with your domain or IP
    
    client_max_body_size 1G;
    
    location / {
        proxy_pass http://127.0.0.1:5173;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Timeout settings for large file uploads
        proxy_connect_timeout 300s;
        proxy_send_timeout 300s;
        proxy_read_timeout 300s;
    }
}
```

### 3. Enable Site

**Ubuntu/Debian:**
```bash
sudo ln -s /etc/nginx/sites-available/rename-tool /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

**CentOS/RHEL:**
```bash
sudo cp /etc/nginx/sites-available/rename-tool /etc/nginx/conf.d/rename-tool.conf
sudo nginx -t
sudo systemctl restart nginx
```

Now access your app at `http://your-domain.com` (port 80).

---

## SSL/HTTPS Setup

Use Let's Encrypt for free SSL certificates.

### 1. Install Certbot

**Ubuntu/Debian:**
```bash
sudo apt install -y certbot python3-certbot-nginx
```

**CentOS/RHEL:**
```bash
sudo yum install -y certbot python3-certbot-nginx
```

### 2. Obtain Certificate

```bash
sudo certbot --nginx -d your-domain.com
```

Follow the prompts. Certbot will automatically configure Nginx for HTTPS.

### 3. Auto-Renewal

```bash
# Test renewal
sudo certbot renew --dry-run

# Certbot automatically sets up a cron job for renewal
```

Your app is now accessible at `https://your-domain.com` 🔒

---

## Firewall Configuration

### Ubuntu (UFW)

```bash
# Enable firewall
sudo ufw enable

# Allow SSH
sudo ufw allow 22/tcp

# If using Nginx:
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# If accessing app directly (without Nginx):
sudo ufw allow 5173/tcp

# Check status
sudo ufw status
```

### CentOS (Firewalld)

```bash
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --permanent --add-service=https
sudo firewall-cmd --permanent --add-port=5173/tcp  # If needed
sudo firewall-cmd --reload
```

---

## Monitoring & Logs

### Docker Logs
```bash
# Docker Compose
docker compose logs -f

# Docker (manual)
docker logs -f rename-tool
```

### Native/Systemd Logs
```bash
sudo journalctl -u rename-tool -f
```

### Nginx Logs
```bash
# Access logs
sudo tail -f /var/log/nginx/access.log

# Error logs
sudo tail -f /var/log/nginx/error.log
```

### Disk Space Monitoring
```bash
# Check disk usage
df -h

# Check tmp folder (where uploads are stored)
du -sh /tmp/uploads 2>/dev/null || echo "No uploads directory"

# Clean old temp files (optional cron job)
find /tmp -type f -name "*.zip" -mtime +1 -delete
```

---

## Troubleshooting

### Port Already in Use
```bash
# Find process using port 5173
sudo lsof -i :5173
sudo netstat -tulpn | grep 5173

# Kill the process
sudo kill -9 <PID>
```

### Cannot Connect to App
```bash
# Check if app is running
docker compose ps  # For Docker
systemctl status rename-tool  # For systemd

# Check if port is listening
sudo netstat -tulpn | grep 5173

# Check firewall
sudo ufw status
sudo firewall-cmd --list-all
```

### Permission Errors
```bash
# Fix permissions for uploads directory
sudo chmod 777 /tmp/uploads

# For Docker
sudo chown -R 1000:1000 /tmp/uploads
```

### Large File Upload Fails
- Increase Nginx `client_max_body_size`
- Increase Flask `MAX_CONTENT_LENGTH`
- Check disk space: `df -h`

### Container Won't Start
```bash
# Check logs
docker logs rename-tool

# Check if port is available
sudo lsof -i :5173

# Rebuild image
docker compose down
docker compose up -d --build --force-recreate
```

### "JSON Parse Error" Issues
This has been fixed in the latest version. Make sure you've pulled the latest code:
```bash
git pull origin main
docker compose down
docker compose up -d --build
```

---

## Security Best Practices

1. **Change default ports** if exposed directly to the internet
2. **Use HTTPS** in production (via Let's Encrypt)
3. **Set up firewall** rules (UFW/Firewalld)
4. **Disable debug mode** in production
5. **Regular updates**: Keep Docker, Python, and dependencies updated
6. **Limit file upload size** appropriately
7. **Use strong passwords** for VM access
8. **Enable fail2ban** to prevent brute force attacks
9. **Regular backups** of configuration files
10. **Monitor logs** for suspicious activity

---

## Quick Start Commands

### Docker Compose (Recommended)
```bash
cd ~/rename-tool
docker compose up -d --build
docker compose logs -f
```

### Access Application
- **Direct**: `http://<vm-ip>:5173`
- **With Nginx**: `http://<domain-or-ip>`
- **With SSL**: `https://<domain>`

### Stop Application
```bash
docker compose down
```

---

## Support

For issues or questions:
1. Check the logs (see Monitoring & Logs section)
2. Review the Troubleshooting section
3. Check firewall and network settings
4. Verify all dependencies are installed

---

**Last Updated**: February 2026  
**Version**: 1.0
