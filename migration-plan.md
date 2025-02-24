# Backend Migration Plan: ai-resume-optimizer to ResWave (FastAPI Version)

## Overview
This document outlines the steps to integrate the existing Python backend from ai-resume-optimizer with ResWave's Next.js frontend, utilizing FastAPI for improved performance and modern API features.

## Pre-Migration: Containerization of Existing System
### 1. Dockerize Current Flask Backend
- Create Dockerfile for Flask application:
  ```dockerfile
  FROM python:3.9-slim
  
  WORKDIR /app
  COPY backend/requirements.txt .
  RUN pip install --no-cache-dir -r requirements.txt
  
  COPY backend/ .
  COPY .env .
  
  EXPOSE 5000
  CMD ["python", "app.py"]
  ```

### 2. Dockerize Current Frontend
- Create Dockerfile for React frontend:
  ```dockerfile
  FROM node:18-alpine

  WORKDIR /app
  COPY frontend/package*.json ./
  RUN npm install

  COPY frontend/ .
  
  # Build the application
  RUN npm run build
  
  # Install serve to run the built application
  RUN npm install -g serve
  
  EXPOSE 3000
  CMD ["serve", "-s", "dist", "-l", "3000"]
  ```

### 3. Create Docker Compose Configuration
- Create docker-compose.yml for full stack:
  ```yaml
  version: '3.8'
  services:
    flask-backend:
      build:
        context: .
        dockerfile: backend/Dockerfile
      ports:
        - "5000:5000"
      volumes:
        - ./backend:/app
      environment:
        - FLASK_ENV=development
      networks:
        - app-network

    react-frontend:
      build:
        context: .
        dockerfile: frontend/Dockerfile
      ports:
        - "3000:3000"
      volumes:
        - ./frontend:/app
        - /app/node_modules
      environment:
        - VITE_API_URL=http://flask-backend:5000
      depends_on:
        - flask-backend
      networks:
        - app-network

  networks:
    app-network:
      driver: bridge
  ```

### 4. Test and Version Containers
- Build and test Docker images locally
- Tag images with version numbers:
  * ai-resume-optimizer-flask:v1.x.x
  * ai-resume-optimizer-frontend:v1.x.x
- Document all environment variables
- Create container registry
- Push versioned images to registry

### 5. Backup and Documentation
- Export container images to tar files
- Document all API endpoints and frontend routes
- Save configuration files
- Create deployment instructions
- Archive codebase with git tag

## Architecture Approach
- Migrate Flask to FastAPI backend
- Integrate with ResWave's Next.js frontend
- Maintain Clerk authentication
- Use Supabase for storage
- Implement OpenAPI documentation

## Implementation Steps

### 1. FastAPI Backend Setup
- Create new FastAPI application structure:
  ```
  backend/
  ├── app/
  │   ├── __init__.py
  │   ├── main.py
  │   ├── config.py
  │   ├── dependencies.py
  │   ├── routers/
  │   │   ├── __init__.py
  │   │   ├── resume.py
  │   │   └── health.py
  │   ├── services/
  │   │   ├── __init__.py
  │   │   └── resume_optimizer.py
  │   └── models/
  │       ├── __init__.py
  │       └── resume.py
  ```
- Implement Pydantic models for request/response validation
- Add CORS middleware
- Configure environment variables
- Set up logging and error handling

### 2. API Implementation
- Convert existing Flask routes to FastAPI endpoints
- Add type hints and request/response models
- Implement async handlers for improved performance
- Add OpenAPI documentation
- Implement rate limiting and request validation

### 3. Authentication Integration
- Implement Clerk JWT validation
- Add authentication dependencies
- Create user context middleware
- Handle session management
- Add role-based access control

### 4. Supabase Integration
- Add Supabase client configuration
- Implement file storage service
- Add async file operations
- Handle storage quotas and limits
- Implement file metadata tracking

### 5. Frontend Integration (In Progress)
- [x] Add ResWave frontend to workspace (as frontend(Copy))
- [x] Update docker-compose.yml for Next.js configuration:
  ```yaml
  # Updated frontend service configuration for Next.js
  nextjs-frontend:
    build:
      context: .
      dockerfile: frontend (Copy)/Dockerfile
    volumes:
      - ./frontend (Copy):/app
      - /app/node_modules
      - /app/.next
    environment:
      - NEXT_PUBLIC_API_URL=http://flask-backend:5000
  ```
- [x] Remove original frontend folder
- [ ] Test new frontend integration
- [ ] Update API client configuration
- [ ] Implement type-safe API calls
- [ ] Add error handling and retries
- [ ] Update file upload/download logic
- [ ] Implement progress tracking

### 5.1 Next.js Integration Notes
- Environment Configuration
  * Use NEXT_PUBLIC_* prefix for client-side environment variables
  * Configure API endpoints through next.config.js for proper routing
  * Set up proper CORS configuration in FastAPI backend
  
- Development Workflow
  * Next.js hot-reload enabled through volume mounts
  * API proxy configuration for local development
  * TypeScript types generation from OpenAPI spec
  
- Build Optimization
  * Configure output: 'standalone' in next.config.js
  * Implement proper caching strategies
  * Setup proper static file handling

### 6. Testing Strategy
- Unit tests with pytest and pytest-asyncio
- Integration tests with TestClient
- End-to-end tests with Playwright
- Performance testing with locust
- API contract testing

### 7. Deployment Configuration
- Create Dockerfile for FastAPI backend:
  ```dockerfile
  FROM python:3.9-slim
  
  WORKDIR /app
  COPY backend/requirements.txt .
  RUN pip install --no-cache-dir -r requirements.txt
  
  COPY backend/ .
  
  EXPOSE 8000
  CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
  ```

- Create Dockerfile for Next.js frontend:
  ```dockerfile
  FROM node:18-alpine AS builder
  
  WORKDIR /app
  COPY frontend/package*.json ./
  RUN npm install
  
  COPY frontend/ .
  RUN npm run build
  
  FROM node:18-alpine
  WORKDIR /app
  
  COPY --from=builder /app/.next ./.next
  COPY --from=builder /app/node_modules ./node_modules
  COPY --from=builder /app/package*.json ./
  COPY --from=builder /app/public ./public
  
  EXPOSE 3000
  CMD ["npm", "start"]
  ```

- Create production docker-compose.yml:
  ```yaml
  version: '3.8'
  services:
    fastapi-backend:
      build:
        context: .
        dockerfile: backend/Dockerfile
      ports:
        - "8000:8000"
      environment:
        - ENV=production
      networks:
        - app-network

    nextjs-frontend:
      build:
        context: .
        dockerfile: frontend/Dockerfile
      ports:
        - "3000:3000"
      environment:
        - NEXT_PUBLIC_API_URL=http://fastapi-backend:8000
      depends_on:
        - fastapi-backend
      networks:
        - app-network

  networks:
    app-network:
      driver: bridge
  ```

## Timeline
1. Pre-Migration Containerization (3 days)
   - Backend containerization (1 day)
   - Frontend containerization (1 day)
   - Integration and testing (1 day)
2. FastAPI Setup (2 days)
3. API Implementation (3 days)
4. Authentication Integration (2 days)
5. Supabase Integration (2 days)
6. Frontend Updates (2 days)
7. Testing Implementation (2 days)
8. Deployment Setup (2 days)

Total Estimated Time: 18 days

## Technical Benefits of FastAPI
1. Performance
   - Async/await support
   - Automatic concurrency
   - Fast request handling

2. Developer Experience
   - Automatic OpenAPI documentation
   - Type safety with Pydantic
   - Built-in request validation
   - Better IDE support

3. Modern Features
   - WebSocket support
   - Dependency injection
   - Background tasks
   - File handling

## Dependencies
- Python 3.8+
- FastAPI
- Uvicorn
- Pydantic
- httpx
- python-multipart
- python-jose
- pytest
- Docker and Docker Compose
- Node.js 18+
- Next.js

## Risks and Mitigation
1. Migration Complexity
   - Risk: Data loss during migration
   - Mitigation: Comprehensive testing and rollback plan
   - Fallback: Containerized original stack available

2. Performance Impact
   - Risk: Increased latency during file processing
   - Mitigation: Implement async processing and caching

3. Integration Issues
   - Risk: Authentication/authorization gaps
   - Mitigation: Thorough security testing and audit

4. Learning Curve
   - Risk: Team adaptation to FastAPI
   - Mitigation: Documentation and training sessions

## Rollback Plan
1. Stop FastAPI and Next.js services
2. Pull original container images from registry
3. Start original containers
4. Verify system functionality

## Container Registry Details
- Registry URL: [To be determined]
- Image naming conventions:
  * Backend: ai-resume-optimizer-flask:v1.x.x
  * Frontend: ai-resume-optimizer-frontend:v1.x.x
- Required environment variables documented in .env.example
- Backup location: [To be determined]

## Development Workflow
1. Run development environment:
   ```bash
   docker-compose up --build
   ```
2. Access services:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:5000
   - API Documentation: http://localhost:5000/docs

3. Monitor logs:
   ```bash
   docker-compose logs -f [service-name]
   ```

4. Rebuild services:
   ```bash
   docker-compose up --build [service-name]