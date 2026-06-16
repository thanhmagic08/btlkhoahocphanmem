# Hệ thống Đặt Lịch Khám Bệnh

Ứng dụng Streamlit này cho phép chọn bệnh viện, bác sĩ, đặt lịch và gửi email xác nhận.

## Chạy trên GitHub

1. Đẩy mã nguồn lên GitHub.
2. GitHub Actions sẽ chạy kiểm tra ngữ pháp Python mỗi khi push/pull request.
3. Nếu bạn muốn triển khai lên Streamlit Cloud hoặc dịch vụ tương tự, hãy sử dụng `requirements.txt`.

## Cấu hình email

Không lưu mật khẩu trong mã nguồn. Thay vào đó, thiết lập biến môi trường:

- `EMAIL_SENDER`: địa chỉ Gmail gửi đi
- `EMAIL_PASSWORD`: mật khẩu ứng dụng Gmail

Ví dụ khi chạy local:

```powershell
$env:EMAIL_SENDER = "your@gmail.com"
$env:EMAIL_PASSWORD = "app-password"
streamlit run web_app.py
```

## Chạy local

```powershell
pip install -r requirements.txt
streamlit run web_app.py
```
