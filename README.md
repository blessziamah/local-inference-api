# BLACKSTAR-AI

A production-ready FastAPI service providing authenticated access to Large Language Models through an Ollama backend.

## Features

- **Multi-user API Management**: Role-based access control with superuser and regular user roles
- **Secure Authentication**: API key-based authentication with cryptographically secure key generation
- **LLM Integration**: Seamless integration with Ollama for text generation and chat completion
- **OpenAI-Compatible API**: Chat completion endpoint compatible with OpenAI format
- **MongoDB Storage**: Persistent user and API key management
- **Docker Ready**: Production-ready containerization with Docker Compose

## Quick Start with Docker

### Prerequisites

- Docker Engine 20.10+
- Docker Compose 2.0+
- MongoDB running on host (localhost:27017)
- Ollama running on host (localhost:11434)

### 1. Clone the Repository

```bash
git clone <repository-url>
cd blackstar-ai
```

### 2. Start Host Services

Ensure MongoDB and Ollama are running on your host machine:

```bash
# Start MongoDB (if not already running)
# Example: mongod --dbpath /path/to/data

# Start Ollama (if not already running)
# Example: ollama serve

# Pull the llama3.1 model (if not already downloaded)
ollama pull llama3.1
```

### 3. Configure Environment Variables

```bash
cp .env.example .env
```

Edit `.env` to set your configuration:

```env
MONGODB_URI=mongodb://host.docker.internal:27017
LLM_URL=http://host.docker.internal:11434
REFRESH_TOKEN_URL=http://your-auth-service:3000/api/auth/refresh
```

### 4. Start API Service

```bash
# Build and start the API service
make build
make up

# Or using docker-compose directly
docker-compose up -d

# View logs
make logs

# Check service status
make ps
```

The API service will be available at:
- **API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

## API Endpoints

### Health Check
```bash
GET /
```

### User Management

```bash
# Create a new user (requires superuser API key)
POST /user/create
Headers: x-api-key: <superuser-api-key>
Body: {"username": "john_doe", "role": "user"}

# Get current user info
GET /user/me
Headers: x-api-key: <your-api-key>

# List all users (requires superuser)
GET /users
Headers: x-api-key: <superuser-api-key>

# Activate/Deactivate user (requires superuser)
POST /user/activate
POST /user/deactivate
Headers: x-api-key: <superuser-api-key>
Body: {"api_key": "<target-user-api-key>"}

# Delete user (requires superuser)
DELETE /users/{user_id}
Headers: x-api-key: <superuser-api-key>
```

### LLM Operations

```bash
# Text generation
POST /generate
Headers: x-api-key: <your-api-key>
Body: {"prompt": "Explain quantum computing"}

# Chat completion (OpenAI-compatible)
POST /chat
Headers: x-api-key: <your-api-key>
Body: {
  "messages": [
    {"role": "user", "content": "What is FastAPI?"}
  ]
}
```

## Docker Architecture

### Services

1. **api**: FastAPI application (containerized)
   - Runs on port 8000
   - Non-root user for security
   - Health checks enabled
   - Connects to host MongoDB and Ollama via `host.docker.internal`

2. **MongoDB**: Running on host machine
   - Must be running on localhost:27017
   - Stores user and API key data in `BLACKSTAR_AI` database

3. **Ollama**: Running on host machine
   - Must be running on localhost:11434
   - Provides LLM inference (llama3.1 recommended)

## Production Deployment

### Using Custom Ollama Models

Since Ollama runs on the host, you can manage models directly:

```bash
# List available models
ollama list

# Pull a different model
ollama pull llama3.2

# Remove unused models
ollama rm model-name
```

Update your application code in `llm/api.py` to use the desired model name.

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `MONGODB_URI` | MongoDB connection string | `mongodb://host.docker.internal:27017` |
| `LLM_URL` | Ollama API endpoint | `http://host.docker.internal:11434` |
| `REFRESH_TOKEN_URL` | Token refresh endpoint | - |

### Security Best Practices

1. **API Keys**: Store API keys securely, never commit them to version control
2. **Network**: Use Docker networks to isolate services
3. **Non-root User**: The API runs as a non-root user inside the container
4. **Health Checks**: All services have health checks for automatic recovery
5. **CORS**: Configure `allow_origins` in production (currently allows all origins)

## Development

### Local Development without Docker

```bash
# Install uv package manager
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies
uv pip install -e .

# Run locally
uvicorn main:app --reload
```

### Building the Docker Image

```bash
# Build the image
docker build -t blackstar-ai:latest .

# Run the container
docker run -p 8000:8000 \
  -e MONGODB_URI=mongodb://host.docker.internal:27017 \
  -e LLM_URL=http://host.docker.internal:11434 \
  blackstar-ai:latest
```

## Monitoring

### View Logs

```bash
# API service logs
make logs

# Or using docker-compose directly
docker-compose logs -f api
```

### Service Health

```bash
# Check all services health
make health

# Check API health
curl http://localhost:8000/

# Check MongoDB (on host)
mongosh --eval "db.adminCommand('ping')"

# Check Ollama (on host)
curl http://localhost:11434/api/tags
```

## Troubleshooting

### API cannot connect to MongoDB or Ollama

Ensure host services are accessible from Docker:

```bash
# Check if services are running on host
mongosh --eval "db.adminCommand('ping')"
curl http://localhost:11434/api/tags

# On Linux, you may need to use --network=host or update firewall rules
# The container accesses host via host.docker.internal (macOS/Windows)
# or host-gateway (Linux with extra_hosts in docker-compose.yml)
```

### Ollama model not available

```bash
# Pull the model on host
ollama pull llama3.1

# List available models
ollama list
```

### MongoDB connection issues

```bash
# Verify MongoDB is listening on all interfaces
# Check mongod.conf: bindIp should include 0.0.0.0 or 127.0.0.1

# Test connection
mongosh "mongodb://localhost:27017"
```

### API not responding

```bash
# Check logs
make logs

# Restart API
make restart

# Check if API container is running
make ps
```

## Tech Stack

- **FastAPI**: Modern Python web framework
- **MongoDB**: Document database
- **Ollama**: Local LLM engine
- **Docker**: Containerization
- **uv**: Fast Python package manager

## License

[Add your license here]

## Contributing

[Add contribution guidelines here]
