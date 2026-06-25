@echo off
cd /d c:\SQL2022\btlkhoahocphanmem
call .venv\Scripts\activate.bat
streamlit run web_app.py --server.address 0.0.0.0 --server.port 8501
