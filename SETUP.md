# CodeShield AI Backend - Setup Guide

## Quick Start

### 1. Install Dependencies

```bash
cd codeshield-backend
pip install -r requirements.txt
```

### 2. Set Up Environment Variables

Create a `.env` file in the root directory:

```env
# Database Configuration
DATABASE_URL=postgresql://user:password@localhost:5432/codeshield

# Google Gemini API (REQUIRED)
GEMINI_API_KEY=your_gemini_api_key_here

# Application Configuration
APP_ENV=development
SECRET_KEY=your-secret-key-here
DEBUG=true
PORT=8000

# CORS Configuration
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
```

**Important:** Get your Gemini API key from [Google AI Studio](https://makersuite.google.com/app/apikey)

### 3. Set Up Database

#### Option A: Using PostgreSQL CLI

```bash
# Create database
createdb codeshield

# Run SQL script
psql -U your_user -d codeshield -f scripts/init_database.sql
```

#### Option B: Using psql

```bash
psql -U your_user -d postgres
```

Then in psql:
```sql
CREATE DATABASE codeshield;
\c codeshield
\i scripts/init_database.sql
```

### 4. Run the Server

```bash
python start_server.py
```

Or:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

The server will start on `http://localhost:8000`

## API Endpoints

### Analyze Code
- **POST** `/analyze` or `/api/v1/analyze`
- **Body:** `{"code": "your code here"}`
- **Response:** Analysis results with vulnerabilities, fixes, risk score, and explanation

### Get Analysis History
- **GET** `/api/v1/analyze/history?limit=10&offset=0`

### Get Analysis by ID
- **GET** `/api/v1/analyze/{analysis_id}`

### Health Check
- **GET** `/health`

### API Documentation
- **GET** `/docs` (Swagger UI)
- **GET** `/redoc` (ReDoc)

## Testing

### Test with curl

```bash
curl -X POST "http://localhost:8000/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "code": "def login(username, password):\n    query = f\"SELECT * FROM users WHERE username = {username}\"\n    return execute(query)"
  }'
```

### Test with Python

```python
import requests

response = requests.post(
    "http://localhost:8000/analyze",
    json={
        "code": """
def login(username, password):
    query = f"SELECT * FROM users WHERE username = {username}"
    return execute(query)
        """
    }
)

print(response.json())
```

## Project Structure

```
codeshield-backend/
├── app/
│   ├── api/
│   │   ├── routes/
│   │   │   └── analyze.py          # Analysis endpoints
│   │   ├── schemas/
│   │   │   ├── analyze_schemas.py  # Request/Response schemas
│   │   │   └── common_schemas.py   # Common response format
│   │   └── exception.py            # Custom exceptions
│   ├── config/
│   │   ├── config.py               # Configuration
│   │   └── logger.py               # Logging
│   ├── infra/
│   │   └── db/
│   │       └── postgres/
│   │           ├── base.py
│   │           ├── postgres_config.py
│   │           └── models/
│   │               └── code_analysis.py
│   ├── services/
│   │   └── gemini_service.py       # Gemini AI integration
│   └── main.py                     # FastAPI app
├── scripts/
│   └── init_database.sql           # Database schema
├── requirements.txt
├── start_server.py
└── README.md
```

## Troubleshooting

### Database Connection Error

- Check your `DATABASE_URL` in `.env`
- Ensure PostgreSQL is running
- Verify database exists: `psql -l | grep codeshield`

### Gemini API Error

- Verify `GEMINI_API_KEY` is set in `.env`
- Check API key is valid at [Google AI Studio](https://makersuite.google.com/app/apikey)
- Ensure you have API quota available

### CORS Error

- Add your frontend URL to `CORS_ORIGINS` in `.env`
- Default includes `http://localhost:3000` and `http://localhost:5173`

### Port Already in Use

- Change `PORT` in `.env` or use a different port
- Kill the process using port 8000: `lsof -ti:8000 | xargs kill`

## Deployment

### Vercel

1. Push code to GitHub
2. Import project in Vercel
3. Set environment variables in Vercel dashboard
4. Deploy!

The `vercel.json` is already configured.

### Docker

```bash
docker build -t codeshield-backend .
docker run -p 8000:8000 --env-file .env codeshield-backend
```

## Next Steps

1. ✅ Backend is ready
2. ✅ Database schema is created
3. ✅ Gemini integration is complete
4. ✅ API endpoints are working
5. 🔄 Connect frontend to backend
6. 🔄 Test end-to-end flow

## Support

For issues or questions, check the main README.md file.

