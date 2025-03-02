# RAG

## Setup and Installation

1. Clone the repository
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Running the Application

To run the application:

```bash
uvicorn main:app --reload
```

The application will start on `http://localhost:8000`

### API Endpoints

- `GET /`: Welcome endpoint that returns a hello message
- Additional endpoints can be found in the routers:
    - Base router endpoints
    - Data router endpoints

## Development

- The application is built with FastAPI
- Environment variables should be configured in `.env` file (currently commented out in main.py)