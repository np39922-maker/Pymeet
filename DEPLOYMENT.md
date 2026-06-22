# PyMeet deployment guide

Official references: [Docker Engine on Ubuntu](https://docs.docker.com/engine/install/ubuntu/),
[WSL on Windows Server](https://learn.microsoft.com/windows/wsl/install-on-server),
[Docker Desktop on Windows](https://docs.docker.com/desktop/setup/install/windows-install/), and
[Caddy automatic HTTPS](https://caddyserver.com/docs/automatic-https).

## Choose the host

For a live service, the simplest reliable host is an Ubuntu VM/VPS with a public IPv4
address. If the machine must be Windows Server 2022, run the Linux containers inside
an Ubuntu Hyper-V VM (most predictable) or Ubuntu on WSL 2. Docker Desktop is intended
for desktop Windows and is not supported on Windows Server.

A local Windows PC with WSL can also host the domain, but only while the PC, WSL, and
internet connection stay online. It additionally needs a public IP, router forwarding,
and may be blocked by CGNAT. Treat that route as a test/small personal deployment.

## 1. Prepare the project and secrets

Copy this folder to the host, then create the real environment file:

```bash
cp .env.example .env
openssl rand -hex 32     # use this output for POSTGRES_PASSWORD
openssl rand -base64 48  # use this output for JWT_SECRET_KEY
nano .env
```

Set these values:

```dotenv
POSTGRES_PASSWORD=<unique-random-password>
JWT_SECRET_KEY=<unique-random-secret>
DOMAIN=meet.example.com
FRONTEND_ORIGIN=https://meet.example.com
BIND_ADDRESS=127.0.0.1
```

Do not commit `.env`. If this deployment reuses an existing PostgreSQL volume, do not
change `POSTGRES_PASSWORD` only in `.env`; PostgreSQL applies it only on first database
creation. Change the database user's password inside PostgreSQL as well.

## 2. Point the domain and open the firewall

At the DNS provider, create an `A` record for `meet.example.com` pointing to the host's
public IPv4 address. Add `AAAA` only when IPv6 is correctly routed to the host.

Allow inbound TCP 80 and TCP/UDP 443 at the cloud firewall and host firewall. Caddy
uses port 80 for certificate issuance/redirects and 443 for HTTPS. Do not expose 5432
or 8000.

On Windows Server, run elevated PowerShell:

```powershell
New-NetFirewallRule -DisplayName "PyMeet HTTP" -Direction Inbound -Protocol TCP -LocalPort 80 -Action Allow
New-NetFirewallRule -DisplayName "PyMeet HTTPS TCP" -Direction Inbound -Protocol TCP -LocalPort 443 -Action Allow
New-NetFirewallRule -DisplayName "PyMeet HTTPS UDP" -Direction Inbound -Protocol UDP -LocalPort 443 -Action Allow
```

## 3A. Ubuntu VM/VPS (recommended)

Install Docker Engine and the Compose plugin from Docker's official Ubuntu repository,
copy the project to (for example) `/opt/pymeet`, and run:

```bash
cd /opt/pymeet
sudo docker compose -f docker-compose.yml -f compose.production.yml config
sudo docker compose -f docker-compose.yml -f compose.production.yml up -d --build
sudo docker compose -f docker-compose.yml -f compose.production.yml ps
sudo docker compose -f docker-compose.yml -f compose.production.yml logs -f caddy frontend backend
```

Open `https://meet.example.com/api/health`, then the domain home page. Caddy obtains and
renews the TLS certificate automatically. DNS must already resolve publicly and ports
80/443 must reach this host.

## 3B. Windows Server 2022 with WSL 2

Run elevated PowerShell, reboot if requested, then install Ubuntu:

```powershell
wsl --install
wsl --install -d Ubuntu
wsl --set-default-version 2
```

Open Ubuntu, install Docker Engine plus the Compose plugin, and run the same Compose
commands from section 3A. Keep the project in the Linux filesystem (such as
`/opt/pymeet`), not under `/mnt/c`, for better filesystem behavior.

If remote requests do not reach WSL's NAT address, forward Windows ports to the current
WSL address from elevated PowerShell:

```powershell
$WslIp = (wsl -d Ubuntu hostname -I).Trim().Split(' ')[0]
netsh interface portproxy add v4tov4 listenaddress=0.0.0.0 listenport=80 connectaddress=$WslIp connectport=80
netsh interface portproxy add v4tov4 listenaddress=0.0.0.0 listenport=443 connectaddress=$WslIp connectport=443
```

WSL's address can change after shutdown/reboot, so refresh these rules at startup or use
an Ubuntu Hyper-V VM with a stable address. `portproxy` handles TCP; Caddy will still work
over HTTPS/TCP when UDP 443 is unavailable.

## 3C. Local PC + WSL on a public domain

Follow section 3B, reserve the PC's LAN address in the router, then forward router TCP
80 and 443 to that Windows PC. Point DNS to the router's public address. If the public
address changes, configure dynamic DNS. If the router WAN address differs from an IP
checker result, the connection is probably behind CGNAT; ask the ISP for a public IP or
use a VPS/tunnel design.

## 4. Production operations

Update and restart:

```bash
git pull
sudo docker compose -f docker-compose.yml -f compose.production.yml up -d --build
sudo docker image prune -f
```

Database backup and restore:

```bash
sudo docker compose exec -T postgres pg_dump -U pymeet -d pymeet > pymeet-$(date +%F).sql
cat pymeet-2026-01-01.sql | sudo docker compose exec -T postgres psql -U pymeet -d pymeet
```

Back up the SQL dumps and the Caddy data volume off-host. Test restores periodically.

## 5. WebRTC/TURN caveat

HTTPS secures camera/microphone access and WebSocket signaling, but STUN alone cannot
connect every pair of users. Corporate networks, symmetric NAT, and strict firewalls
often require a TURN relay. Obtain a managed TURN service or run coturn separately, then
set `VITE_TURN_URL`, `VITE_TURN_USERNAME`, and `VITE_TURN_CREDENTIAL` in `.env` and
rebuild the frontend. TURN credentials delivered to browsers are inherently visible;
prefer time-limited credentials for a serious public service.

## Troubleshooting

```bash
docker compose -f docker-compose.yml -f compose.production.yml ps
docker compose -f docker-compose.yml -f compose.production.yml logs --tail=200
curl -I http://127.0.0.1:5173
curl https://meet.example.com/api/health
```

- Certificate failure: verify public DNS and inbound ports 80/443.
- Camera/mic missing: use the HTTPS domain and grant browser permissions.
- Page works but calls fail between networks: configure TURN.
- `502 Bad Gateway`: inspect `frontend` and `backend` logs/health.
- Database authentication failure after changing `.env`: reconcile the existing
  PostgreSQL user's password or intentionally recreate an empty volume.
