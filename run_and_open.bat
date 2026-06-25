@echo off
cd /d %~dp0
call .venv\Scripts\activate.bat
start "Streamlit App" cmd /k "call .venv\Scripts\activate.bat && streamlit run web_app.py --server.address 0.0.0.0 --server.port 8501"
timeout /t 5 /nobreak >nul
start "" "http://localhost:8501"
