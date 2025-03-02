# Self-Hosted Deployment Guide

This guide provides step-by-step instructions for deploying the Transportation Dashboard application on your own server or VPS.

## Prerequisites

1. A Linux server (Ubuntu 22.04 LTS recommended)
2. Root or sudo access
3. Domain name (optional but recommended)
4. Docker and Docker Compose installed
5. Git installed

## Step 1: Server Preparation

### Update System Packages

```bash
sudo apt update
sudo apt upgrade -y
```

### Install Required Packages

```bash
sudo apt install -y curl git nginx certbot python3-certbot-nginx ufw
```

### Set Up Firewall

```bash
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

### Install Docker and Docker Compose

```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Add your user to the docker group
sudo usermod -aG docker $USER

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.3/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Verify installations
docker --version
docker-compose --version
```

## Step 2: Clone the Repository

```bash
# Create a directory for the application
sudo mkdir -p /opt/transportation-dashboard
sudo chown $USER:$USER /opt/transportation-dashboard

# Clone the repository
git clone https://github.com/yourusername/transportation-dashboard.git /opt/transportation-dashboard
cd /opt/transportation-dashboard
```

## Step 3: Configure the Application

### Set Up Environment Variables

Create a `.env` file with the necessary environment variables:

```bash
cat > .env << EOF
# Environment configuration
ENVIRONMENT=production
DATABASE_URL=postgresql://postgres:postgres@db:5432/transportation

# API Keys
SAMSARA_API_KEY=your_samsara_api_key_here
GOOGLE_MAPS_API_KEY=your_google_maps_api_key_here
WEATHER_API_KEY=your_weather_api_key_here

# Optimization Settings
MAX_OPTIMIZATION_TIME=30
REVENUE_WEIGHT=0.5
COST_WEIGHT=0.3
TIME_WEIGHT=0.2
EOF
```

### Configure Nginx

Create an Nginx configuration file:

```bash
sudo nano /etc/nginx/sites-available/transportation-dashboard
```

Add the following configuration:

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:80;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Enable the site:

```bash
sudo ln -s /etc/nginx/sites-available/transportation-dashboard /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### Set Up SSL with Let's Encrypt (Optional but Recommended)

```bash
sudo certbot --nginx -d your-domain.com
```

## Step 4: Deploy with Docker Compose

### Copy the Docker Compose File

Ensure the `docker-compose.yml` file is in the project directory. If not, create it:

```bash
cat > docker-compose.yml << EOF
version: '3.8'

services:
  # Backend API service
  backend:
    build:
      context: .
      dockerfile: Dockerfile.backend
    ports:
      - "8000:8000"
    environment:
      - ENVIRONMENT=production
      - DATABASE_URL=postgresql://postgres:postgres@db:5432/transportation
      - SAMSARA_API_KEY=\${SAMSARA_API_KEY:-your_samsara_api_key_here}
      - GOOGLE_MAPS_API_KEY=\${GOOGLE_MAPS_API_KEY:-}
      - WEATHER_API_KEY=\${WEATHER_API_KEY:-placeholder_for_weather_api_key}
      - MAX_OPTIMIZATION_TIME=30
      - REVENUE_WEIGHT=0.5
      - COST_WEIGHT=0.3
      - TIME_WEIGHT=0.2
    volumes:
      - ./server:/app/server
      - ./rate_sheets:/app/rate_sheets
      - ./SampleOrders:/app/SampleOrders
      - ./pdf_extraction_results:/app/pdf_extraction_results
    depends_on:
      - db
    restart: unless-stopped

  # Frontend service
  frontend:
    build:
      context: .
      dockerfile: Dockerfile.frontend
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/conf.d/default.conf
    depends_on:
      - backend
    restart: unless-stopped

  # Database service
  db:
    image: postgres:15-alpine
    ports:
      - "5432:5432"
    environment:
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=postgres
      - POSTGRES_DB=transportation
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped

volumes:
  postgres_data:
EOF
```

### Build and Start the Containers

```bash
docker-compose up -d
```

### Initialize the Database

```bash
docker-compose exec backend python -m server.database.init_db
```

## Step 5: Set Up Automatic Updates (Optional)

Create a script to pull the latest changes and restart the containers:

```bash
cat > /opt/transportation-dashboard/update.sh << EOF
#!/bin/bash
cd /opt/transportation-dashboard
git pull
docker-compose down
docker-compose build
docker-compose up -d
EOF

chmod +x /opt/transportation-dashboard/update.sh
```

Set up a cron job to run the update script weekly:

```bash
(crontab -l 2>/dev/null; echo "0 2 * * 0 /opt/transportation-dashboard/update.sh >> /var/log/transportation-update.log 2>&1") | crontab -
```

## Step 6: Set Up Monitoring

### Install and Configure Prometheus (Optional)

```bash
# Create directories for Prometheus
sudo mkdir -p /opt/prometheus/data
sudo mkdir -p /opt/prometheus/config

# Create Prometheus configuration
cat > /opt/prometheus/config/prometheus.yml << EOF
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']
  
  - job_name: 'node'
    static_configs:
      - targets: ['node-exporter:9100']
  
  - job_name: 'cadvisor'
    static_configs:
      - targets: ['cadvisor:8080']
EOF

# Create Docker Compose file for monitoring
cat > /opt/prometheus/docker-compose.yml << EOF
version: '3.8'

services:
  prometheus:
    image: prom/prometheus
    volumes:
      - ./config/prometheus.yml:/etc/prometheus/prometheus.yml
      - ./data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
    ports:
      - "9090:9090"
    restart: unless-stopped

  node-exporter:
    image: prom/node-exporter
    volumes:
      - /proc:/host/proc:ro
      - /sys:/host/sys:ro
      - /:/rootfs:ro
    command:
      - '--path.procfs=/host/proc'
      - '--path.sysfs=/host/sys'
      - '--collector.filesystem.ignored-mount-points=^/(sys|proc|dev|host|etc)($$|/)'
    ports:
      - "9100:9100"
    restart: unless-stopped

  cadvisor:
    image: gcr.io/cadvisor/cadvisor
    volumes:
      - /:/rootfs:ro
      - /var/run:/var/run:ro
      - /sys:/sys:ro
      - /var/lib/docker/:/var/lib/docker:ro
      - /dev/disk/:/dev/disk:ro
    ports:
      - "8080:8080"
    restart: unless-stopped

  grafana:
    image: grafana/grafana
    depends_on:
      - prometheus
    ports:
      - "3000:3000"
    volumes:
      - grafana_data:/var/lib/grafana
    restart: unless-stopped

volumes:
  grafana_data:
EOF

# Start monitoring services
cd /opt/prometheus
docker-compose up -d
```

### Set Up Log Rotation

```bash
sudo nano /etc/logrotate.d/transportation-dashboard
```

Add the following configuration:

```
/var/log/transportation-*.log {
    daily
    missingok
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 root root
}
```

## Step 7: Set Up Backups

### Create a Backup Script

```bash
cat > /opt/transportation-dashboard/backup.sh << EOF
#!/bin/bash
TIMESTAMP=\$(date +"%Y%m%d%H%M%S")
BACKUP_DIR="/opt/backups/transportation-dashboard"

# Create backup directory if it doesn't exist
mkdir -p \$BACKUP_DIR

# Backup the database
docker-compose exec -T db pg_dump -U postgres transportation > \$BACKUP_DIR/transportation_db_\$TIMESTAMP.sql

# Backup environment variables
cp /opt/transportation-dashboard/.env \$BACKUP_DIR/env_\$TIMESTAMP.backup

# Backup PDF files
tar -czf \$BACKUP_DIR/pdf_files_\$TIMESTAMP.tar.gz /opt/transportation-dashboard/SampleOrders /opt/transportation-dashboard/pdf_extraction_results

# Remove backups older than 30 days
find \$BACKUP_DIR -type f -name "*.sql" -mtime +30 -delete
find \$BACKUP_DIR -type f -name "*.backup" -mtime +30 -delete
find \$BACKUP_DIR -type f -name "*.tar.gz" -mtime +30 -delete
EOF

chmod +x /opt/transportation-dashboard/backup.sh
```

### Set Up a Daily Backup Cron Job

```bash
(crontab -l 2>/dev/null; echo "0 1 * * * /opt/transportation-dashboard/backup.sh >> /var/log/transportation-backup.log 2>&1") | crontab -
```

## Step 8: Set Up Systemd Service (Alternative to Docker Compose)

If you prefer to manage the application with systemd instead of Docker Compose:

```bash
sudo nano /etc/systemd/system/transportation-dashboard.service
```

Add the following configuration:

```
[Unit]
Description=Transportation Dashboard
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/transportation-dashboard
ExecStart=/usr/local/bin/docker-compose up
ExecStop=/usr/local/bin/docker-compose down
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start the service:

```bash
sudo systemctl enable transportation-dashboard
sudo systemctl start transportation-dashboard
```

## Troubleshooting

### Docker Compose Issues

If you encounter issues with Docker Compose:

```bash
# Check container status
docker-compose ps

# View container logs
docker-compose logs

# View logs for a specific service
docker-compose logs backend
docker-compose logs frontend
docker-compose logs db
```

### Database Connection Issues

If the backend cannot connect to the database:

```bash
# Check if the database container is running
docker-compose ps db

# Check database logs
docker-compose logs db

# Connect to the database directly
docker-compose exec db psql -U postgres -d transportation
```

### Nginx Issues

If you encounter issues with Nginx:

```bash
# Check Nginx configuration
sudo nginx -t

# Check Nginx status
sudo systemctl status nginx

# Check Nginx logs
sudo tail -f /var/log/nginx/error.log
```

## Performance Optimization

### Optimize Nginx Configuration

```bash
sudo nano /etc/nginx/nginx.conf
```

Add or modify the following settings:

```nginx
worker_processes auto;
worker_rlimit_nofile 65535;

events {
    worker_connections 1024;
    multi_accept on;
    use epoll;
}

http {
    # Basic settings
    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;
    types_hash_max_size 2048;
    server_tokens off;

    # SSL settings
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_prefer_server_ciphers on;
    ssl_ciphers 'ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES128-GCM-SHA256:DHE-RSA-AES256-GCM-SHA384';
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;

    # Gzip settings
    gzip on;
    gzip_disable "msie6";
    gzip_vary on;
    gzip_proxied any;
    gzip_comp_level 6;
    gzip_buffers 16 8k;
    gzip_http_version 1.1;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript;

    # Include other configuration files
    include /etc/nginx/conf.d/*.conf;
    include /etc/nginx/sites-enabled/*;
}
```

### Optimize PostgreSQL Configuration

Create a custom PostgreSQL configuration:

```bash
cat > /opt/transportation-dashboard/postgres-custom.conf << EOF
# Memory settings
shared_buffers = 128MB
work_mem = 4MB
maintenance_work_mem = 64MB

# Checkpoint settings
checkpoint_timeout = 15min
checkpoint_completion_target = 0.9

# Query planner settings
random_page_cost = 1.1
effective_cache_size = 512MB

# WAL settings
wal_buffers = 4MB
EOF
```

Update the Docker Compose file to use this configuration:

```bash
# Add this volume to the db service in docker-compose.yml
volumes:
  - ./postgres-custom.conf:/etc/postgresql/postgresql.conf
  - postgres_data:/var/lib/postgresql/data

# Add this command to the db service
command: postgres -c config_file=/etc/postgresql/postgresql.conf
```

## Security Best Practices

1. **Keep Software Updated**:
   ```bash
   sudo apt update && sudo apt upgrade -y
   docker-compose pull
   docker-compose build --no-cache
   docker-compose up -d
   ```

2. **Use Strong Passwords**:
   - Change default database passwords in the `.env` file
   - Use a password manager to generate strong passwords

3. **Secure Nginx**:
   - Enable HTTPS with Let's Encrypt
   - Configure HTTP Strict Transport Security (HSTS)
   - Add security headers

4. **Restrict Access**:
   - Use SSH key authentication instead of password
   - Disable root login
   - Use a firewall (UFW)

5. **Regular Backups**:
   - Ensure the backup script is running correctly
   - Test restoring from backups periodically

6. **Monitor Logs**:
   - Check logs regularly for suspicious activity
   - Set up log monitoring and alerting
