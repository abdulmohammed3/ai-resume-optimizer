# Development Guide

## Setup

### Prerequisites
- Python 3.9+
- Node.js 18+
- Docker and Docker Compose
- Supabase account
- Clerk account
- OpenAI API key

### Environment Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd ai-resume-optimizer
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # Linux/macOS
# or
.\venv\Scripts\activate  # Windows
```

3. Install dependencies:
```bash
cd backend
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your credentials
```

Required environment variables:
- `CLERK_PUBLISHABLE_KEY`
- `CLERK_SECRET_KEY`
- `CLERK_JWT_KEY`
- `SUPABASE_URL`
- `SUPABASE_KEY`
- `SUPABASE_JWT_SECRET`
- `OPENAI_API_KEY`

### Database Setup

1. Create a new Supabase project
2. Navigate to the SQL editor
3. Execute migrations from `backend/migrations/001_create_tables.sql`
4. Verify tables and policies are created correctly

### Storage Setup

1. Create a new storage bucket named "resumes"
2. Configure CORS settings for your frontend domain
3. Set up proper RLS policies

## Development

### Running the Development Server

1. Start the FastAPI server:
```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

2. Start the frontend development server:
```bash
cd frontend
npm install
npm run dev
```

### Code Structure

```
backend/
├── app/
│   ├── core/            # Core functionality
│   │   ├── security.py  # Authentication
│   │   ├── storage.py   # File storage
│   │   └── database.py  # Database operations
│   ├── models/          # Pydantic models
│   ├── routers/         # API endpoints
│   ├── services/        # Business logic
│   └── main.py         # Application entry
├── migrations/          # Database migrations
└── docs/               # Documentation
```

### Adding New Features

1. Create/update models in `app/models/`
2. Implement business logic in `app/services/`
3. Add API endpoints in `app/routers/`
4. Update documentation

## Testing

### Running Tests

```bash
pytest
```

### Test Structure

```
tests/
├── conftest.py         # Test configuration
├── test_api/          # API tests
├── test_services/     # Service tests
└── test_models/       # Model tests
```

### Testing Guidelines

1. Write tests for new features
2. Maintain test coverage above 80%
3. Mock external services
4. Use test fixtures

## Deployment

### Docker Deployment

1. Build images:
```bash
docker compose build
```

2. Run containers:
```bash
docker compose up -d
```

### Manual Deployment

1. Build frontend:
```bash
cd frontend
npm run build
```

2. Start backend:
```bash
cd backend
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker
```

## Monitoring

### Logging

Logs are written to:
- Console in development
- Files in production
- Structured JSON format

### Metrics

Monitor:
- API response times
- Error rates
- Storage usage
- Database performance

## Troubleshooting

### Common Issues

1. Authentication errors:
   - Verify Clerk configuration
   - Check token expiration
   - Validate JWT settings

2. Storage issues:
   - Check bucket permissions
   - Verify file paths
   - Monitor quotas

3. Database issues:
   - Check connections
   - Verify RLS policies
   - Monitor query performance

### Debug Mode

Enable debug mode in .env:
```
DEBUG=True
```

### Support

For issues:
1. Check logs
2. Review documentation
3. Open GitHub issue