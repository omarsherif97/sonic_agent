# SEQ_SONIC Docker Deployment

This directory contains all the necessary files to deploy the SEQ_SONIC application using Docker in a VM or any Docker-compatible environment.

## 🏗️ Architecture

The application is split into two main services:

- **Backend (FastAPI)**: Runs on port 8000, handles API requests and agent logic
- **Frontend (Chainlit)**: Runs on port 8001, provides the chatbot interface
- **Nginx (Optional)**: Reverse proxy on port 80 for production deployments

## 📋 Prerequisites

- Docker Engine 20.10+
- Docker Compose 2.0+
- At least 2GB RAM available
- Ports 8000, 8001 (and optionally 80) available

## 🚀 Quick Start

### 1. Clone and Navigate
```bash
cd /path/to/your/SEQ_SONIC/project
cd Docker
```

### 2. Set Up Environment Variables
Create a `.env` file in the project root (one level up from Docker/):
```bash
# SEQ_SONIC Environment Variables
GROQ_API_KEY=your_actual_groq_api_key
OPENAI_API_KEY=your_actual_openai_api_key
GEMINI_API_KEY=your_actual_gemini_api_key

# Optional: Override default models
GROQ_MODEL=llama-3.3-70b-versatile
OPENAI_MODEL=gpt-4o-mini
```

### 3. Deploy
```bash
# Make the deployment script executable
chmod +x deploy.sh

# Run the deployment script
./deploy.sh
```

## 🔧 Manual Deployment

If you prefer to deploy manually:

```bash
# Build the images
docker-compose build

# Start services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f
```

## 🌐 Access URLs

After successful deployment:

- **Backend API**: http://localhost:8000
- **Frontend Chat**: http://localhost:8001
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## 🐳 Docker Commands

### Service Management
```bash
# Start all services
docker-compose up -d

# Stop all services
docker-compose down

# Restart services
docker-compose restart

# View service status
docker-compose ps

# View logs
docker-compose logs -f [service_name]
```

### Individual Service Management
```bash
# Start only backend
docker-compose up -d backend

# Start only frontend
docker-compose up -d frontend

# View backend logs
docker-compose logs -f backend

# View frontend logs
docker-compose logs -f frontend
```

### Production Mode (with Nginx)
```bash
# Start with Nginx reverse proxy
docker-compose --profile production up -d

# This will expose the app on port 80
# Backend: http://localhost/api/
# Frontend: http://localhost/
```

## 🔍 Troubleshooting

### Port Conflicts
If you get port conflicts:
```bash
# Check what's using the ports
sudo netstat -tulpn | grep :8000
sudo netstat -tulpn | grep :8001

# Kill processes using those ports
sudo kill -9 <PID>
```

### Service Health Issues
```bash
# Check service health
docker-compose ps

# View detailed logs
docker-compose logs [service_name]

# Restart problematic service
docker-compose restart [service_name]
```

### Memory Issues
If you encounter memory issues:
```bash
# Check Docker resource usage
docker stats

# Increase Docker memory limit in Docker Desktop settings
# Or add memory limits to docker-compose.yml
```

## 📊 Monitoring

### Health Checks
The backend service includes health checks:
```bash
# Check backend health
curl http://localhost:8000/health

# Check from within Docker network
docker-compose exec backend curl http://localhost:8000/health
```

### Logs
```bash
# View all logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f backend
docker-compose logs -f frontend

# View logs with timestamps
docker-compose logs -f -t
```

## 🔒 Security Considerations

- The `.env` file contains sensitive API keys - keep it secure
- In production, consider using Docker secrets or environment variables
- The current setup allows all origins (CORS) - restrict this in production
- Consider using HTTPS in production with proper SSL certificates

## 📈 Scaling

To scale individual services:
```bash
# Scale backend to 3 instances
docker-compose up -d --scale backend=3

# Scale frontend to 2 instances
docker-compose up -d --scale frontend=2
```

## 🗑️ Cleanup

To completely remove the application:
```bash
# Stop and remove containers
docker-compose down

# Remove images
docker-compose down --rmi all

# Remove volumes (WARNING: This will delete all data)
docker-compose down -v

# Remove everything including networks
docker-compose down --rmi all -v --remove-orphans
```

## 📝 Environment Variables Reference

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `GROQ_API_KEY` | Groq API key for LLM access | - | ✅ |
| `OPENAI_API_KEY` | OpenAI API key for LLM access | - | ✅ |
| `GEMINI_API_KEY` | Gemini API key for LLM access | - | ✅ |
| `GROQ_MODEL` | Groq model to use | `llama-3.3-70b-versatile` | ❌ |
| `OPENAI_MODEL` | OpenAI model to use | `gpt-4o-mini` | ❌ |
| `BACKEND_URL` | Backend service URL (auto-set) | `http://backend:8000` | ❌ |

## 🤝 Support

If you encounter issues:
1. Check the logs: `docker-compose logs -f`
2. Verify environment variables are set correctly
3. Ensure ports are available
4. Check Docker and Docker Compose versions
5. Verify sufficient system resources
