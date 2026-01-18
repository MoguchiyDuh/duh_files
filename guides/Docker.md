## Core Concepts

**Image** - Blueprint (read-only template)  
**Container** - Running instance of an image  
**Volume** - Persistent data storage  
**Network** - Communication between containers

## Essential Commands

### Images
```bash
docker images                    # List images
docker pull <image>              # Download image
docker rmi <image>               # Remove image
docker build -t <name> .         # Build from Dockerfile
```

### Containers
```bash
docker ps                        # List running
docker ps -a                     # List all
docker run <image>               # Create and start
docker start/stop <container>    # Start/stop
docker rm <container>            # Remove
docker logs -f <container>       # View logs
docker exec -it <container> sh   # Enter container
```

### Docker Compose
```bash
docker-compose up -d             # Start all services
docker-compose down              # Stop and remove
docker-compose ps                # List services
docker-compose logs -f           # View logs
docker-compose restart           # Restart services
docker-compose up -d --build     # Rebuild and start
```

## Dockerfile Basics

```dockerfile
FROM python:3.13-slim            # Base image
WORKDIR /app                     # Set working directory
COPY requirements.txt .          # Copy file
RUN pip install -r requirements.txt  # Execute command
EXPOSE 8000                      # Expose port
CMD ["uvicorn", "main:app"]      # Default command
```

## docker-compose.yml

```yaml
version: '3.8'

services:
  app:
    build: ./backend
    ports:
      - "8000:8000"
    volumes:
      - ./backend:/app
    environment:
      DATABASE_URL: postgres://...
    depends_on:
      - db
  
  db:
    image: postgres:16-alpine
    volumes:
      - db_data:/var/lib/postgresql/data
    environment:
      POSTGRES_PASSWORD: password

volumes:
  db_data:
```

## Useful Flags

**-d** - Detached (background)  
**-it** - Interactive terminal  
**-p** - Port mapping (host:container)  
**-v** - Volume mount  
**--rm** - Auto-remove on stop  
**--name** - Container name

## Cleanup

```bash
docker system prune              # Remove unused data
docker system prune -a           # Remove all unused
docker volume prune              # Remove unused volumes
```

## Arch Linux

```bash
sudo systemctl enable --now docker
sudo usermod -aG docker $USER
# Logout/login for group to apply
```

## Listify Project

```bash
cd ~/Documents/Listify
docker-compose up -d             # Start all
docker-compose logs -f backend   # View backend logs
docker-compose down              # Stop all
```

Services:
- Frontend: http://localhost:5173
- Backend: http://localhost:8000
- Postgres: localhost:5432
- Redis: localhost:6379

---

## See Also
- [[00 - Programming MOC]] - Programming overview