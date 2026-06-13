# Doctor Appointment Booking System — v3 (All upgrades)
This version includes:
- MongoDB (docker-compose with a mongo service)
- Docker support (app container + mongo)
- Stateful chatbot (stores chat history per patient)
- Tailwind CSS frontend (CDN) with improved UI
- Security: Flask-Login, Flask-WTF (CSRF), password reset via token (printed in console)
- Analytics page with basic metrics
- API endpoints for search and chat

## Quick start (with Docker)
1. Build and run with docker-compose (recommended):
   ```bash
   docker-compose up --build
   ```
   This will start the Flask app on port 5000 and MongoDB on 27017.
2. Open http://localhost:5000

## Quick start (without Docker)
1. Install dependencies in a venv:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```
2. Ensure MongoDB is running locally (or set MONGO_URI env var).
3. Run:
   ```bash
   flask run --host=0.0.0.0
   ```

## Notes & Limitations
- Password reset tokens are printed to the server console for demo purposes.
- For production, replace SECRET_KEY and enable HTTPS, email service, better input validation, and secure MongoDB credentials.
