# Deploy SoHam On An E2E Node

This README records the steps used to deploy the SoHam React + FastAPI app on an E2E Ubuntu node.

It is written so the node can be deleted to avoid charges and recreated later.

## Current Example Values

Replace these values when creating a new node.

```text
Server IP: 151.185.32.75
SSH key on local machine: ~/.ssh/e2e_soham_001
Root login: root@151.185.32.75
Deploy user: soham
Domain: vimarsha.co.in
Repo: https://github.com/VijayChand1993/SoHam.git
```

## 1. Create A Fresh E2E Node

In E2E portal:

1. Go to **Compute > Nodes**.
2. Click **Add New Node**.
3. Choose a CPU node, not GPU.
4. Choose Ubuntu, for example Ubuntu 24.04 LTS.
5. Choose the smallest suitable plan for testing.
6. Use hourly/on-demand billing.
7. Attach or enable a public IPv4 address.
8. Add/select your SSH public key.
9. Launch the node.

After the node is running, note the public IP address.

## 2. Connect As Root

From your local machine:

```bash
ssh -i ~/.ssh/e2e_soham_001 root@151.185.32.75
```

If prompted:

```text
Are you sure you want to continue connecting?
```

Type:

```text
yes
```

## 3. Initial Server Update

Run on the server:

```bash
apt update
apt upgrade -y
apt install -y git curl unzip ca-certificates build-essential
```

Check the server:

```bash
lsb_release -a
free -h
df -h
```

## 4. Create A Non-Root Deploy User

Create user:

```bash
adduser soham
usermod -aG sudo soham
```

Copy the root user's allowed SSH public key to the new user:

```bash
mkdir -p /home/soham/.ssh
cp /root/.ssh/authorized_keys /home/soham/.ssh/authorized_keys
chown -R soham:soham /home/soham/.ssh
chmod 700 /home/soham/.ssh
chmod 600 /home/soham/.ssh/authorized_keys
```

Important: do not copy the private key to the server. The server only needs the public key inside `authorized_keys`.

From your local machine, test login as `soham`:

```bash
ssh -i ~/.ssh/e2e_soham_001 soham@151.185.32.75
```

Use the `soham` user for the remaining steps.

## 5. Install Base Tools

On the server as `soham`:

```bash
sudo apt update
sudo apt install -y git curl ca-certificates build-essential
```

## 6. Install uv For Python Backend

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
source ~/.bashrc
uv --version
```

If `uv` is not found:

```bash
export PATH="$HOME/.local/bin:$PATH"
uv --version
```

## 7. Install Node.js LTS

```bash
curl -fsSL https://deb.nodesource.com/setup_lts.x | sudo -E bash -
sudo apt install -y nodejs
node --version
npm --version
```

## 8. Clone The Repo

```bash
cd ~
git clone https://github.com/VijayChand1993/SoHam.git
cd SoHam
ls
```

Expected folders:

```text
backend
frontend
README.md
```

## 9. Install Backend Dependencies

```bash
cd ~/SoHam/backend
uv sync
```

If `pyswisseph` fails with this error:

```text
fatal error: Python.h: No such file or directory
```

Install Python development headers and retry:

```bash
sudo apt update
sudo apt install -y python3.12-dev build-essential pkg-config
cd ~/SoHam/backend
rm -rf .venv
uv sync
```

## 10. Run Backend Manually For First Test

```bash
cd ~/SoHam/backend
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000
```

In another SSH terminal, test:

```bash
curl http://127.0.0.1:8000/api/health
```

After confirming it works, stop the manual backend process with `Ctrl + C`.

## 11. Build Frontend

Create production env file:

```bash
cd ~/SoHam/frontend
cat > .env.production <<'EOF'
VITE_API_BASE_URL=
EOF
```

Install and build:

```bash
npm install
npm run build
ls dist
```

Expected:

```text
assets
index.html
```

## 12. Install And Configure Nginx

Install Nginx:

```bash
sudo apt install -y nginx
```

Copy frontend build:

```bash
sudo mkdir -p /var/www/soham
sudo rsync -av --delete ~/SoHam/frontend/dist/ /var/www/soham/
sudo chown -R www-data:www-data /var/www/soham
```

Create Nginx site config:

```bash
sudo nano /etc/nginx/sites-available/soham
```

Paste:

```nginx
server {
    listen 80;
    server_name 151.185.32.75;

    root /var/www/soham;
    index index.html;

    location /api/ {
        proxy_pass http://127.0.0.1:8000/api/;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /docs {
        proxy_pass http://127.0.0.1:8000/docs;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
    }

    location /openapi.json {
        proxy_pass http://127.0.0.1:8000/openapi.json;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
    }

    location / {
        try_files $uri $uri/ /index.html;
    }
}
```

Enable the site:

```bash
sudo ln -s /etc/nginx/sites-available/soham /etc/nginx/sites-enabled/soham
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl restart nginx
```

Open in browser:

```text
http://151.185.32.75
```

## 13. Run Backend As A Permanent Service

Create a `systemd` service:

```bash
sudo nano /etc/systemd/system/soham-backend.service
```

Paste:

```ini
[Unit]
Description=SoHam FastAPI Backend
After=network.target

[Service]
Type=simple
User=soham
Group=soham
WorkingDirectory=/home/soham/SoHam/backend
Environment=PATH=/home/soham/SoHam/backend/.venv/bin:/home/soham/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
ExecStart=/home/soham/.local/bin/uv run uvicorn app.main:app --host 127.0.0.1 --port 8000
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
sudo systemctl daemon-reload
sudo systemctl enable soham-backend
sudo systemctl start soham-backend
sudo systemctl status soham-backend
```

Test:

```bash
curl http://127.0.0.1:8000/api/health
curl http://151.185.32.75/api/health
```

## 14. Create A Repeatable Deploy Script

Create:

```bash
nano ~/deploy-soham.sh
```

Paste:

```bash
#!/usr/bin/env bash
set -e

cd /home/soham/SoHam

echo "Pulling latest code..."
git pull

echo "Updating backend dependencies..."
cd /home/soham/SoHam/backend
uv sync

echo "Restarting backend..."
sudo systemctl restart soham-backend

echo "Building frontend..."
cd /home/soham/SoHam/frontend
npm install
npm run build

echo "Publishing frontend..."
sudo rsync -av --delete /home/soham/SoHam/frontend/dist/ /var/www/soham/
sudo chown -R www-data:www-data /var/www/soham

echo "Testing Nginx..."
sudo nginx -t

echo "Reloading Nginx..."
sudo systemctl reload nginx

echo "Done."
```

Make executable:

```bash
chmod +x ~/deploy-soham.sh
```

Run:

```bash
~/deploy-soham.sh
```

Future deployment:

```bash
ssh -i ~/.ssh/e2e_soham_001 soham@151.185.32.75
~/deploy-soham.sh
```

## 15. Basic Server Hardening

Enable firewall:

```bash
sudo ufw allow OpenSSH
sudo ufw allow 'Nginx Full'
sudo ufw enable
sudo ufw status
```

Expected allowed ports:

```text
22/tcp
80/tcp
443/tcp
```

Check backend port is not publicly exposed:

```bash
curl http://151.185.32.75:8000/api/health
```

This should fail or timeout.

Check public API through Nginx:

```bash
curl http://151.185.32.75/api/health
```

Check services:

```bash
sudo systemctl status nginx --no-pager
sudo systemctl status soham-backend --no-pager
```

Check disk and memory:

```bash
df -h
free -h
```

## 16. E2E Cost Safety

In E2E portal, check:

- running nodes
- reserved/static public IP charges
- attached volumes
- snapshots
- backups
- load balancers

Delete or disable anything not needed.

To avoid charges while not testing, stop or delete the node from E2E portal.

If deleting the node, remember that local server changes will be lost unless pushed to GitHub or saved elsewhere.

## 17. Add Domain In E2E DNS

Domain used:

```text
vimarsha.co.in
```

In E2E portal:

1. Go to **Network > DNS**.
2. Click **Add Domain**.
3. Enter:

```text
Domain: vimarsha.co.in
IPv4 Address: 151.185.32.75
```

4. Submit.

Then go to the domain registrar where `vimarsha.co.in` was purchased and update nameservers to:

```text
ns50.e2enetworks.net.in
ns51.e2enetworks.net.in
```

Test DNS from local machine:

```bash
dig @ns50.e2enetworks.net.in vimarsha.co.in A +short
dig vimarsha.co.in A +short
```

Expected:

```text
151.185.32.75
```

## 18. Future Domain Nginx Update

After DNS resolves, update Nginx:

```bash
sudo nano /etc/nginx/sites-available/soham
```

Change:

```nginx
server_name 151.185.32.75;
```

to:

```nginx
server_name vimarsha.co.in www.vimarsha.co.in;
```

Then:

```bash
sudo nginx -t
sudo systemctl reload nginx
```

## 19. Future HTTPS Setup

After domain is working, install HTTPS:

```bash
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx
```

Follow prompts for:

```text
vimarsha.co.in
www.vimarsha.co.in
```

Certbot will update Nginx and enable HTTPS.

## 20. Useful Commands

Backend logs:

```bash
sudo journalctl -u soham-backend -f
```

Restart backend:

```bash
sudo systemctl restart soham-backend
```

Restart Nginx:

```bash
sudo systemctl restart nginx
```

Check Nginx config:

```bash
sudo nginx -t
```

Check public health:

```bash
curl http://151.185.32.75/api/health
```

Check local backend:

```bash
curl http://127.0.0.1:8000/api/health
```

## 21. Recreate Deployment Later

If the node is deleted:

1. Create a new Ubuntu E2E node.
2. Note the new IP.
3. Repeat steps in this README.
4. Update DNS records to the new IP.
5. Update Nginx `server_name` if needed.
6. Run Certbot again after DNS points to the new node.
