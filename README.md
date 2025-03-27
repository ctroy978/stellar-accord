# Stellar Accord

## Interstellar Diplomacy Simulation Game

Stellar Accord is an educational simulation game for classroom use that models complex interstellar diplomacy among six distinct alien civilizations. The game combines resource management, diplomatic negotiation, strategic project development, and treaty building in a digital platform that supports 20-30 students.

## Quick Start

1. Make sure you have Docker and Docker Compose installed
2. Run `docker-compose up --build`
3. Access the application at http://localhost
4. Test API directly at http://localhost/api/game-info
5. Use the test page at http://localhost/test.html to verify API connectivity

## Troubleshooting

If you encounter issues with the frontend connecting to the backend:
1. Check that all containers are running: `docker-compose ps`
2. Test the API directly: `curl http://localhost/api/game-info`
3. Check the logs: `docker-compose logs backend` and `docker-compose logs frontend`
4. Ensure nginx is properly routing requests: `docker-compose logs nginx`

## Development

This is a skeleton application with:
- React frontend
- FastAPI backend
- PostgreSQL database
- nginx as reverse proxy

All running in Docker containers.

## Architecture

- **Frontend**: React.js application (port 3000 internally, accessed via nginx)
- **Backend**: FastAPI (Python) application (port 8000 internally, accessed via nginx)
- **Database**: PostgreSQL (port 5432)
- **Reverse Proxy**: nginx (ports 80, 443)
