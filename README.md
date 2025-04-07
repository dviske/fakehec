# FakeHEC

FakeHEC is a small Flask app that emulates a Splunk HTTP Endpoint Collector to allow you to quickly and easily test services that are capable of exporting logs to Splunk.

At the moment, it only supports JSON logs through the `/services/collector` endpoint, but I'm happy to accept PRs for more support.

Features:
- Multiple collectors with individual authentication
- Authenticated collector endpoints
- Temporary (7 day default) log retention
- Ability to view submitted messages
- Each collector uses its own subdomain.

## How to deploy

Please note, deployment requires you to have a domain and (ideally) a wildcard subdomain. The Splunk HEC is differentiated by the hostname in many implementations, not the path. As such, each collector uses its own subdomain for separation.

To deploy using Docker, you can use the following `docker-compose.yml`:
```yaml
services:
  fakehec:
    container_name: fakehec
    env_file: ".env"
    ports:
      - 5000:5000
    image: ghcr.io/dviske/fakehec:latest
    volumes:
      - ./data/app.db:/app.db
```

The `.env` should be populated with at least the first two options below:
```ini
# Mandatory
SECRET_KEY="you-will-never-guess" # Generate one.
SERVER_NAME="fakehec.example.com"
# Optional for tracking
SENTRY_DSN="https://xxxx@xxxx.ingest.us.sentry.io/xxxx"
```

You can reverse-proxy the software via nginx using the following config:
```nginx
server {
    server_name fakehec.example.com *.fakehec.example.com;

    location / {
        proxy_pass http://127.0.0.1:5000;

        # Standard proxy headers
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    listen 443 ssl;
    ssl_certificate /etc/letsencrypt/live/fakehec.example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/fakehec.example.com/privkey.pem;
    include /etc/letsencrypt/options-ssl-nginx.conf;
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;
}
```