# SDM review application

This is a Django application for reviewing SDMs used by the [MPA Europe project](https://mpa-europe.eu/).

You can adapt this application for your own use. It can be useful for:

1. Reviewing SDMs collaboratively online
2. Reviewing SDMs in workshops

# Instructions of use

## Development Setup

### Prerequisites

- Docker and Docker Compose
- Python 3.12+ (if running without Docker)

### Quick Start

1. **Clone the repository** (if applicable)

2. **Start services with Docker Compose**:
   ```bash
   docker compose up --build
   ```

3. **Run migrations**:
   ```bash
   docker compose run --rm web python manage.py migrate
   ```

4. **Create admin user**:
   ```bash
   docker compose run --rm web python manage.py createsuperuser
   ```

5. **Access the admin interface**:
   - Open `http://localhost:8000/admin/`
   - Log in with the credentials you created

### Development Environment Variables

The following environment variables can be set (defaults are used if not provided):

<!-- - `POSTGRES_DB`: Database name (default: `edna`)
- `POSTGRES_USER`: Database user (default: `edna`)
- `POSTGRES_PASSWORD`: Database password (default: `edna`)
- `DB_HOST`: Database host (default: `localhost` or `db` in Docker)
- `DB_PORT`: Database port (default: `5432`) -->
- `SECRET_KEY`: Django secret key (default: insecure dev key)
- `DEBUG`: Set to `True` for development (default: `True`)
- `ALLOWED_HOSTS`: Comma-separated list (default: `*` in dev)

## Production Deployment

### Prerequisites

- Server with Docker and Docker Compose installed
- Domain name configured
- SSL certificate (recommended: Let's Encrypt via Certbot)
- Reverse proxy (Nginx or similar) for SSL termination

### Deployment Steps

1. **Clone the repository on your server**:
   ```bash
   git clone <repository-url> /opt/my-server
   cd /opt/my-server
   ```

2. **Create production environment file** (`.env` or set in Docker Compose):
   ```bash
   # Django
   SECRET_KEY=<generate-strong-secret-key>
   DEBUG=False
   ALLOWED_HOSTS=your-domain-name.com,localhost
   ```

3. **Update `docker-compose.yml` for production**:
   - Remove volume mounts for code (use COPY in Dockerfile instead)
   - Update environment variables to use production values
   - Consider using a production WSGI server (gunicorn) instead of `runserver`
   - Set up proper logging

4. **Build and start services**:
   ```bash
   docker compose up -d --build
   ```

5. **Run migrations**:
   ```bash
   docker compose exec web python manage.py migrate
   ```

6. **Create admin user**:
   ```bash
   docker compose exec web python manage.py createsuperuser
   ```

7. **Collect static files** (if using Django's static file serving):
   ```bash
   docker compose exec web python manage.py collectstatic --noinput
   ```

8. **Set up reverse proxy (Nginx example)**:

   Create `/etc/nginx/sites-available/ your-domain-name.com`:
   ```nginx
   server {
       listen 80;
       server_name your-domain-name.com;
       return 301 https://$server_name$request_uri;
   }

   server {
       listen 443 ssl;  # No http2 - fixes ERR_HTTP2_PROTOCOL_ERROR for images
       server_name  your-domain-name.com;

       ssl_certificate /etc/letsencrypt/live/ your-domain-name.com/fullchain.pem;
       ssl_certificate_key /etc/letsencrypt/live/ your-domain-name.com/privkey.pem;
       include /etc/letsencrypt/options-ssl-nginx.conf;
       ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;

       # Security headers
       add_header X-Frame-Options "SAMEORIGIN" always;
       add_header X-Content-Type-Options "nosniff" always;
       add_header X-XSS-Protection "1; mode=block" always;

       # Timeouts and upload limit
       proxy_connect_timeout 300s;
       proxy_send_timeout 300s;
       proxy_read_timeout 300s;
       send_timeout 300s;
       client_max_body_size 10M;

       # Serve media files directly (fixes ERR_HTTP2_PROTOCOL_ERROR)
       # NOTE: Update the path below to match your actual project location
       # Common locations: /root/edna-platform/data/media/ or /opt/edna-platform/data/media/
       location /media/ {
           alias /root/edna-platform/data/media/;
           expires 30d;
           add_header Cache-Control "public, immutable";
           add_header X-Content-Type-Options "nosniff" always;
           
           # Don't use try_files with alias - let Nginx handle file resolution naturally
           # If file doesn't exist, it will return 404 automatically
           
           # Explicitly set connection to keep-alive for HTTP/1.1
           keepalive_timeout 65;
       }

       # API endpoints - let Django's corsheaders handle CORS
       location /api/ {
           proxy_pass http://127.0.0.1:8000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
           proxy_set_header X-Forwarded-Proto $scheme;
           proxy_set_header X-Forwarded-Host $host;
           proxy_set_header X-Forwarded-Port $server_port;
           proxy_buffering off;
           proxy_redirect off;
           
           # Don't add CORS headers here - Django's corsheaders middleware handles it
           # Adding them here causes duplicate headers (e.g., "*, *")
       }

       # Everything else (admin, etc.)
       location / {
           proxy_pass http://127.0.0.1:8000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
           proxy_set_header X-Forwarded-Proto $scheme;
           proxy_set_header X-Forwarded-Host $host;
           proxy_set_header X-Forwarded-Port $server_port;
           proxy_buffering off;
           proxy_redirect off;
       }
   }
   ```

   Enable the site:
   ```bash
   sudo ln -s /etc/nginx/sites-available/ your-domain-name.com /etc/nginx/sites-enabled/
   sudo nginx -t
   sudo systemctl reload nginx
   ```

9. **Set up SSL certificate** (Let's Encrypt):
   ```bash
   sudo certbot --nginx -d  your-domain-name.com
   ```

10. **Verify deployment**:
    - Check admin interface: `https:// your-domain-name.com/admin/`
    - Test API endpoints from frontend apps
    - Monitor logs: `docker compose logs -f web`

### Production Checklist

- [ ] `DEBUG=False` is set in environment
- [ ] Strong `SECRET_KEY` is generated and set
- [ ] `ALLOWED_HOSTS` includes ` your-domain-name.com`
- [ ] CORS is configured for your domain
- [ ] Database uses strong passwords
- [ ] SSL/TLS is configured (HTTPS)
- [ ] Media files directory has proper permissions
- [ ] Database backups are configured
- [ ] Logging is configured and monitored
- [ ] Firewall rules allow only necessary ports

### Using Gunicorn (Recommended for Production)

Update `Dockerfile` CMD:
```dockerfile
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "4", "your-domain-name.wsgi:application"]
```

Add to `requirements.txt`:
```
gunicorn==21.2.0
```


