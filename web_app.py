import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import io
import random
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import folium
from streamlit_folium import st_folium
import math

# =========================================================================
# ⚠️ CẤU HÌNH GMAIL GỬI TIN (THAY THÔNG TIN CỦA BẠN VÀO ĐÂY)
# =========================================================================
SENDER_EMAIL = "chuyen_email_cua_ban_vao_day@gmail.com" 
SENDER_PASSWORD = "abcdefghijklmnop"  # 16 ký tự mật khẩu ứng dụng Google

def send_real_gmail(receiver_email, subject, body):
    try:
        msg = MIMEMultipart()
        msg['From'] = SENDER_EMAIL
        msg['To'] = receiver_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain', 'utf-8'))
        
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()  
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        text = msg.as_string()
        server.sendmail(SENDER_EMAIL, receiver_email, text)
        server.quit()
        return True
    except Exception as e:
        st.error(f"❌ Lỗi hệ thống gửi thư tự động: {e}")
        return False

# Hàm tính khoảng cách giữa 2 tọa độ (Công thức Haversine)
def calculate_distance(lat1, lon1, lat2, lon2):
    R = 6371.0  # Bán kính Trái Đất (km)
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat / 2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return round(R * c, 2)

# =========================================================================
# KHỔI TẠO ĐỐI TƯỢNG VÀ CƠ SỞ DỮ LIỆU HỆ THỐNG
# =========================================================================
st.set_page_config(page_title="Hệ Thống Đặt Lịch Khám Bệnh", page_icon="🏥", layout="wide")

if 'initialized' not in st.session_state:
    # Vị trí click mặc định của người dùng (Nhà riêng giả lập ban đầu gần hồ Hoàn Kiếm)
    st.session_state.user_clicked_lat = 21.0285
    st.session_state.user_clicked_lon = 105.8520
    
    # Cập nhật Tên thành Bệnh viện K
    clinics_data = """id,name,address,distance_km,lat,lon
    1,Bệnh viện K,29 Lý Thường Kiệt - Hoàn Kiếm,0.32,21.0245,105.8542
    2,Phòng khám Đa khoa Cầu Giấy,45 Cầu Giấy - Hà Nội,5.0,21.0362,105.7997
    3,Phòng khám Hai Bà Trưng,88 Trần Khát Chân,1.2,21.0105,105.8585
    4,Phòng khám Ba Đình,12 Kim Mã - Ba Đình,4.1,21.0315,105.8242"""
    
    doctors_data = """id,name,specialty,clinic_id,symptoms_handled
    101,Bác sĩ Nguyễn Văn An,Nhi khoa,1,sốt ho sổ mũi biếng ăn
    102,Bác sĩ Trần Thị Bình,Tim mạch,2,đau ngực khó thở chóng mặt
    103,Bác sĩ Lê Hoàng Cường,Da liễu,3,ngứa phát ban mụn nhọt
    104,Bác sĩ Phạm Minh Dung,Nhi khoa,3,sốt ho tiêu chảy
    105,Bác sĩ Vũ Văn Em,Cơ xương khớp,4,đau lưng mỏi gối"""
    
    appointments_data = """booking_id,patient_id,patient_name,phone,insurance_id,doctor_id,appointment_time,status
    BK-9952,BN-4122,Nguyễn Văn Thử,0987654321,GD40101221,101,2026-06-20 09:00:00,Đã xác nhận"""

    st.session_state.df_clinics = pd.read_csv(io.StringIO(clinics_data))
    st.session_state.df_doctors = pd.read_csv(io.StringIO(doctors_data))
    st.session_state.df_appointments = pd.read_csv(io.StringIO(appointments_data))
    st.session_state.df_appointments['appointment_time'] = pd.to_datetime(st.session_state.df_appointments['appointment_time'])
    st.session_state.initialized = True

#專Thanh điều hướng bên cạnh
with st.sidebar:
    st.markdown("### 🏥 CỔNG THÔNG TIN Y TẾ")
    st.write("Hệ thống đặt lịch tự động kết hợp tìm kiếm đường đi thông minh.")
    st.info("💡 **Mẹo:** Bạn có thể click chuột vào bất kỳ vị trí nào trên bản đồ bên phải để chọn vị trí nhà của bạn. Hệ thống sẽ tự vẽ tuyến đường đi đến bệnh viện!")

# -------------------------------------------------------------------------
# 2. KẾT QUẢ TÌM KIẾM & BẢN ĐỒ LỘ TRÌNH
# -------------------------------------------------------------------------
st.title("2. Kết quả tìm kiếm & Bản đồ lộ trình")
st.markdown("📍 **Xác định vị trí và chọn cơ sở khám bệnh:**")

# Tính lại khoảng cách động từ vị trí người dùng click đến các bệnh viện
st.session_state.df_clinics['distance_km'] = st.session_state.df_clinics.apply(
    lambda r: calculate_distance(st.session_state.user_clicked_lat, st.session_state.user_clicked_lon, r['lat'], r['lon']), axis=1
)

df_sorted_clinics = st.session_state.df_clinics.sort_values('distance_km')

clinic_options = {}
for _, row in df_sorted_clinics.iterrows():
    display_text = f"{row['name']} (Khoảng cách hiện tại: {row['distance_km']} km - Đ/c: {row['address']})"
    clinic_options[display_text] = row

selected_clinic_text = st.selectbox("", list(clinic_options.keys()), label_visibility="collapsed")
selected_clinic_row = clinic_options[selected_clinic_text]

st.info(f"🏥 **Cơ sở đang được chọn:** {selected_clinic_row['name']} | 📍 **Khoảng cách từ vị trí của bạn:** {selected_clinic_row['distance_km']} km")

# --- KHỞI TẠO BẢN ĐỒ VÀ GHIM CÁC ĐIỂM ---
map_center = [selected_clinic_row['lat'], selected_clinic_row['lon']]
m = folium.Map(location=map_center, zoom_start=13, control_scale=True)

# 1. Ghim vị trí của Người dùng (Nhà riêng do người dùng click chọn)
folium.Marker(
    location=[st.session_state.user_clicked_lat, st.session_state.user_clicked_lon],
    popup="<b>Vị trí của bạn (Điểm xuất phát)</b>",
    tooltip="Vị trí của bạn",
    icon=folium.Icon(color='blue', icon='home')
).add_to(m)

# 2. Ghim các bệnh viện/phòng khám (Điểm đến)
for _, row in st.session_state.df_clinics.iterrows():
    is_selected = (row['id'] == selected_clinic_row['id'])
    marker_color = 'red' if is_selected else 'orange'
    
    folium.Marker(
        location=[row['lat'], row['lon']],
        popup=f"<b>{row['name']}</b><br>{row['address']}",
        tooltip=row['name'],
        icon=folium.Icon(color=marker_color, icon="plus" if is_selected else "info-sign")
    ).add_to(m)

# -------------------------------------------------------------------------
# GIẢI THUẬT MÔ PHỎNG ĐƯỜNG ĐI UỐN LƯỢN (KHÔNG CẦN MÁY CHỦ API)
# -------------------------------------------------------------------------
start_lat = st.session_state.user_clicked_lat
start_lon = st.session_state.user_clicked_lon
end_lat = selected_clinic_row['lat']
end_lon = selected_clinic_row['lon']

# Tạo ra các điểm rẽ trung gian giả lập để đường đi uốn lượn theo góc phố
mid_lat1 = start_lat + (end_lat - start_lat) * 0.4 + 0.002  # Rẽ góc 1
mid_lon1 = start_lon + (end_lon - start_lon) * 0.3 - 0.001

mid_lat2 = start_lat + (end_lat - start_lat) * 0.7 - 0.001  # Rẽ góc 2
mid_lon2 = start_lon + (end_lon - start_lon) * 0.8 + 0.002

# Tập hợp chuỗi tọa độ bẻ góc mô phỏng đường phố
route_coordinates = [
    [start_lat, start_lon],   # Điểm xuất phát (Nhà)
    [mid_lat1, mid_lon1],     # Ngã rẽ mô phỏng 1
    [mid_lat2, mid_lon2],     # Ngã rẽ mô phỏng 2
    [end_lat, end_lon]        # Điểm đích (Bệnh viện)
]

# Cộng thêm một chút hao hụt khoảng cách đường bộ thực tế (độ vòng vèo)
selected_clinic_row['distance_km'] = round(selected_clinic_row['distance_km'] * 1.3, 2)

# Vẽ tuyến đường mô phỏng lên bản đồ m
folium.PolyLine(
    locations=route_coordinates,
    color="#1E90FF",  
    weight=5,         
    opacity=0.8,
    tooltip="Tuyến đường di chuyển mô phỏng qua các tuyến phố"
).add_to(m)

# 5. Render bản đồ ra giao diện Web Streamlit
map_data = st_folium(m, width="100%", height=450)

# Cập nhật tọa độ mới nếu người dùng bấm chọn một điểm khác trên bản đồ
if map_data and map_data.get("last_clicked"):
    clicked_lat = map_data["last_clicked"]["lat"]
    clicked_lon = map_data["last_clicked"]["lng"]
    
    # Tránh tải lại liên tục nếu bấm trùng vị trí cũ
    if clicked_lat != st.session_state.user_clicked_lat or clicked_lon != st.session_state.user_clicked_lon:
        st.session_state.user_clicked_lat = clicked_lat
        st.session_state.user_clicked_lon = clicked_lon
        st.rerun()

st.success(f"🗺️ **Tọa độ vị trí xuất phát của bạn:** Vĩ độ: {st.session_state.user_clicked_lat:.4f} | Kinh độ: {st.session_state.user_clicked_lon:.4f}")

st.write("---")

# -------------------------------------------------------------------------
# CÁC BƯỚC TIẾP THEO: CHỌN TRIỆU CHỨNG, BÁC SĨ VÀ ĐẶT LỊCH KHÁM
# -------------------------------------------------------------------------
col1, col2 = st.columns(2)

with col1:
    st.header("📋 3. Lựa chọn triệu chứng & Đề xuất Bác sĩ")
    symptom_list = ["Sốt", "Ho", "Sổ mũi", "Biếng ăn", "Tiêu chảy", "Đau ngực", "Khó thở", "Chóng mặt", "Ngứa", "Phát ban", "Mụn nhọt", "Đau lưng", "Mỏi gối"]
    selected_symptoms = st.multiselect("Chọn các triệu chứng hiện tại của bạn:", symptom_list)
    
    selected_doctor_info = None
    if selected_symptoms:
        matched_rows = []
        for _, doc_row in st.session_state.df_doctors.iterrows():
            if doc_row['clinic_id'] == selected_clinic_row['id']:
                if any(smp.lower() in doc_row['symptoms_handled'].lower() for smp in selected_symptoms):
                    matched_rows.append(doc_row)
        
        if matched_rows:
            df_matched_docs = pd.DataFrame(matched_rows)
            st.success(f"👨‍⚕️ Tìm thấy Bác sĩ phù hợp tại {selected_clinic_row['name']}:")
            st.dataframe(df_matched_docs[['name', 'specialty']], use_container_width=True, hide_index=True)
            
            doc_options = {f"{row['name']} ({row['specialty']})": row for _, row in df_matched_docs.iterrows()}
            selected_doc_name = st.selectbox("Chọn bác sĩ khám:", list(doc_options.keys()))
            selected_doctor_info = doc_options[selected_doc_name]
        else:
            st.warning(f"Cơ sở hiện tại ({selected_clinic_row['name']}) chưa có bác sĩ chuyên khoa phù hợp với triệu chứng này.")
    else:
        st.info("Vui lòng chọn triệu chứng để hệ thống tự động đề xuất bác sĩ tương ứng.")

with col2:
    st.header("📋 4. Nhập thông tin & Đặt lịch")
    patient_name_input = st.text_input("Họ và tên bệnh nhân:", placeholder="Ví dụ: Nguyễn Văn A")
    receiver_email_input = st.text_input("Địa chỉ Gmail nhận thông báo lịch:", placeholder="username@gmail.com")
    phone_number = st.text_input("Số điện thoại liên hệ:", placeholder="Ví dụ: 0912345678")
    insurance_id = st.text_input("Mã số thẻ Bảo Hiểm Y Tế (Nếu có):")
    
    appointment_date = st.date_input("Chọn ngày khám:", datetime.now().date() + timedelta(days=1))
    appointment_time = st.time_input("Chọn giờ khám:", datetime.strptime("09:00", "%H:%M").time())
    desired_datetime = pd.to_datetime(f"{appointment_date} {appointment_time}")
    
    if st.button("🚀 GỬI YÊU CẦU ĐẶT LỊCH & GỬI GMAIL"):
        if not patient_name_input:
            st.error("Vui lòng điền họ và tên bệnh nhân.")
        elif not receiver_email_input:
            st.error("Vui lòng nhập địa chỉ Gmail nhận thông báo lịch.")
        elif not phone_number:
            st.error("Vui lòng nhập số điện thoại liên hệ.")
        elif selected_doctor_info is None:
            st.error("Vui lòng chọn triệu chứng để xác định bác sĩ ở Cột 1 trước.")
        else:
            doctor_id = selected_doctor_info['id']
            
            is_conflict = not st.session_state.df_appointments[
                (st.session_state.df_appointments['doctor_id'] == doctor_id) & 
                (st.session_state.df_appointments['appointment_time'] == desired_datetime)
            ].empty
            
            if not is_conflict:
                rand_booking = f"BK-{random.randint(1000, 9999)}"
                rand_patient = f"BN-{random.randint(1000, 9999)}"
                ins_code = insurance_id if insurance_id else "Không đăng ký"
                
                new_booking = pd.DataFrame([{
                    'booking_id': rand_booking, 'patient_id': rand_patient,
                    'patient_name': patient_name_input, 'phone': phone_number,
                    'insurance_id': ins_code, 'doctor_id': doctor_id,
                    'appointment_time': desired_datetime, 'status': 'Đã xác nhận'
                }])
                st.session_state.df_appointments = pd.concat([st.session_state.df_appointments, new_booking], ignore_index=True)
                
                st.success(f"🎉 Đặt lịch thành công! Mã đơn: {rand_booking}")
                
                subject = f"🏥 [XÁC NHẬN] Thư Cảm Ơn Kết Quả Đặt Lịch - Mã Số {rand_booking}"
                body = f"""Kính gửi quý bệnh nhân {patient_name_input},

Hệ thống Quản lý Đặt lịch Khám bệnh Thông minh chân thành cảm ơn quý khách đã sử dụng hệ thống trực tuyến.

Lịch hẹn của quý khách đã được hệ thống phê duyệt thành công:

✨ THÔNG TIN CHI TIẾT LỊCH HẸN Y TẾ:
- Mã số đặt lịch (Booking ID): {rand_booking}
- Mã số bệnh nhân (Patient ID): {rand_patient}
- Họ và tên bệnh nhân: {patient_name_input}
- Triệu chứng ghi nhận: {', '.join(selected_symptoms)}

✨ THÔNG TIN CƠ SỞ Y TẾ & BÁC SĨ CHUYÊN KHOA:
- Bác sĩ phụ trách: {selected_doctor_info['name']}
- Chuyên khoa: {selected_doctor_info['specialty']}
- Địa điểm cơ sở y tế: {selected_clinic_row['name']}
- Địa chỉ chi tiết: {selected_clinic_row['address']}
- Khoảng cách di chuyển ước tính từ điểm chọn: {selected_clinic_row['distance_km']} km
- Thời gian tiếp đón: {desired_datetime.strftime('%H:%M')} ngày {desired_datetime.strftime('%d/%m/%Y')}
- Trạng thái hồ sơ: ĐÃ XÁC NHẬN LỊCH HẸN

⚠️ LƯU Ý: Vui lòng tới quầy đón tiếp của {selected_clinic_row['name']} trước giờ hẹn 10-15 phút và xuất trình mã đơn {rand_booking}.

Kính chúc quý bệnh nhân luôn mạnh khỏe!

Trân trọng,
Ban Điều Hành Hệ Thống Quản Lý Đặt Lịch Y Tế Trực Tuyến.
"""
                with st.spinner("📧 Đang tiến hành gửi Gmail thật, vui lòng chờ..."):
                    if send_real_gmail(receiver_email_input, subject, body):
                        st.balloons()
                        st.success(f"📧 Thư xác nhận kèm khoảng cách lộ trình thực tế đã gửi tới: {receiver_email_input}")
            else:
                st.error("⚠️ Khung giờ của bác sĩ này tại cơ sở đã kín lịch! Vui lòng chọn mốc thời gian khác.")

st.write("---")
st.subheader("📊 Danh sách lịch hẹn hệ thống thời gian thực")
st.dataframe(st.session_state.df_appointments, use_container_width=True, hide_index=True)