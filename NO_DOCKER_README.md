# Running this project locally (No Docker)

This is a Flask-based Doctor Appointment System prepared to run without Docker.

## Steps to run locally (Linux / macOS / WSL)
1. Install Python 3.8+ if you don't have it.
2. Create a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Run the app (detected entrypoint: `app.py`):
   ```bash
   python app.py
   ```

## Windows (PowerShell)
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
python app.py  # or set FLASK_APP and run `flask run`
```

## Notes
- I removed Docker-related files so you can run the project directly.
- If your app uses a different entrypoint or environment variables (database URI, secret keys), update a `.env` file or export them before running.
- If you want me to prepare a simple `run.sh` or to auto-detect and create a Flask `app.run()` wrapper file, reply and I'll add it.
