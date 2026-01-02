# NFL Football Game (2005 Era)

A web-based NFL football simulation game built with Flask, featuring teams from the 2005 era. Play against the CPU with strategic offensive and defensive play calling.

## Features

- Team selection from 8 NFL teams (2005 era)
- Real-time play simulation with strategic depth
- Offensive and defensive play calling
- Score tracking and game log
- Quarter-based gameplay
- Production-ready deployment options

## Quick Start

### Development Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd ryan_application
```

2. Run the setup script:
```bash
./scripts/setup.sh
```

3. Start the development server:
```bash
./scripts/dev.sh
```

4. Open your browser to `http://localhost:5000`

### Manual Setup

1. Create a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create `.env` file from template:
```bash
cp .env.example .env
```

4. Generate a secure SECRET_KEY:
```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```
Add this to your `.env` file.

5. Run the application:
```bash
python app.py
```

## Production Deployment

### Option 1: Using Gunicorn (Recommended for VPS/Cloud)

1. Set up environment variables:
```bash
cp .env.example .env
# Edit .env and set production values
```

2. Run the production server:
```bash
./scripts/prod.sh
```

Or manually:
```bash
export FLASK_ENV=production
export SECRET_KEY=your-secure-secret-key
gunicorn --config gunicorn.conf.py wsgi:app
```

### Option 2: Using Docker

1. Build the Docker image:
```bash
./scripts/docker-build.sh
```

Or manually:
```bash
docker build -t nfl-game:latest .
```

2. Run with Docker:
```bash
docker run -p 5000:5000 \
  -e SECRET_KEY=$(python3 -c 'import secrets; print(secrets.token_hex(32))') \
  nfl-game:latest
```

### Option 3: Using Docker Compose

1. Set SECRET_KEY in your environment or `.env` file

2. Run with docker-compose:
```bash
docker-compose up -d
```

3. View logs:
```bash
docker-compose logs -f
```

4. Stop the application:
```bash
docker-compose down
```

## Configuration

### Environment Variables

Create a `.env` file based on `.env.example`:

- `FLASK_ENV`: Environment (development/production)
- `SECRET_KEY`: Secret key for session management (required in production)
- `HOST`: Server host (default: 0.0.0.0)
- `PORT`: Server port (default: 5000)
- `WORKERS`: Number of Gunicorn workers (production only)
- `THREADS`: Number of threads per worker (production only)
- `TIMEOUT`: Request timeout in seconds (production only)

### Security Considerations

- **SECRET_KEY**: Always use a cryptographically secure secret key in production
- **HTTPS**: Use a reverse proxy (nginx/Apache) with SSL/TLS in production
- **Firewall**: Configure firewall rules to restrict access as needed
- **Session Security**: Sessions use secure cookies in production mode

## Project Structure

```
ryan_application/
├── app.py                 # Main application file
├── config.py              # Configuration classes
├── wsgi.py                # WSGI entry point for production
├── gunicorn.conf.py       # Gunicorn configuration
├── requirements.txt       # Production dependencies
├── requirements-dev.txt   # Development dependencies
├── Dockerfile             # Docker image definition
├── docker-compose.yml     # Docker Compose configuration
├── .env.example           # Environment variable template
├── .gitignore            # Git ignore rules
├── static/               # Static files (CSS, JS, images)
│   └── style.css
├── templates/            # HTML templates
│   └── index.html
└── scripts/              # Utility scripts
    ├── setup.sh          # Initial setup
    ├── dev.sh            # Development server
    ├── prod.sh           # Production server
    └── docker-build.sh   # Docker build helper
```

## Gameplay

1. Select your team from the available NFL teams
2. Choose offensive plays when you have possession
3. Choose defensive plays when the CPU has possession
4. Try to outscore the CPU across 4 quarters
5. Use strategic play calling based on down, distance, and field position

### Available Plays

**Offensive:**
- HB Dive
- HB Toss
- Play Action Pass
- Slants
- Deep Post
- Screen Pass

**Defensive:**
- Cover 2
- Blitz
- 4-3 Normal
- Goal Line
- Prevent

## Development

### Running Tests

```bash
pip install -r requirements-dev.txt
pytest
```

### Code Quality

```bash
# Format code
black .

# Lint code
flake8 .
pylint app.py

# Security scan
bandit -r .
safety check
```

## Deployment Platforms

This application can be deployed to various platforms:

- **VPS/Cloud Servers**: Use Gunicorn with nginx reverse proxy
- **Docker-based platforms**: Use Docker or Docker Compose
- **PaaS platforms**: Heroku, Railway, Render, etc.
- **Container orchestration**: Kubernetes, Docker Swarm

### Example: Nginx Reverse Proxy Configuration

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## Monitoring

The Docker image includes a health check endpoint. Monitor your application using:

```bash
# Docker health status
docker ps

# Application logs
docker logs <container-id>

# Or with docker-compose
docker-compose logs -f
```

## Troubleshooting

### Common Issues

1. **Port already in use**: Change the PORT in `.env` or kill the process using the port
2. **Secret key error**: Ensure SECRET_KEY is set in production environment
3. **Permission denied on scripts**: Run `chmod +x scripts/*.sh`
4. **Docker build fails**: Check Docker is installed and running

## License

This project is for educational and entertainment purposes.

## Credits

NFL team data and game mechanics inspired by Madden NFL 2005.
