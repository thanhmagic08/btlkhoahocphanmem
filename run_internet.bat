@echo off
cd /d %~dp0
call .venv\Scripts\activate.bat
start "Streamlit App" cmd /k "call .venv\Scripts\activate.bat && streamlit run web_app.py --server.address 0.0.0.0 --server.port 8501"
pause
echo.
echo Nếu bạn muốn mở truy cập internet công khai, hãy dùng ngrok hoặc cấu hình port forwarding trên router.
echo 1) Cài ngrok: https://ngrok.com/
echo 2) Đăng nhập với authtoken và chạy:
echo    ngrok http 8501
echo 3) Mở URL ngrok được tạo ra trên internet.
pause
