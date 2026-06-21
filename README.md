# Ứng dụng Streamlit đặt lịch khám bệnh

Ứng dụng chính là `web_app.py`.

## Chạy nhanh tại máy

1. Kích hoạt virtualenv (nếu chưa có):
   - Windows: `.venv\Scripts\activate.bat`
   - macOS/Linux: `source .venv/bin/activate`
2. Cài thư viện:
   ```bash
   pip install -r requirements.txt
   ```
3. Chạy ứng dụng:
   ```bash
   streamlit run web_app.py --server.address 0.0.0.0 --server.port 8501
   ```

Sau đó mở trình duyệt vào `http://localhost:8501` hoặc `http://<ĐỊA_CHỈ_IP_CỦA_BẠN>:8501`.

---

## Ghi chú

- `index.html` tự động chuyển hướng tới `http://192.168.1.32:8501` khi click link repo trên GitHub.
- Repo chỉ chạy bằng `web_app.py` (Streamlit app).