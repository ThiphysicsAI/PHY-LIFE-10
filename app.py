import streamlit as st
import pandas as pd
import google.generativeai as genai
import gspread
from google.oauth2.service_account import Credentials
import json
import datetime

# ==========================================
# 1. CẤU HÌNH GIAO DIỆN TỐI GIẢN (UX/UI)
# ==========================================
st.set_page_config(page_title="PHY-LIFE 10", page_icon="🚀", layout="centered")

st.markdown('''
<style>
    @import url('https://fonts.googleapis.com/css2?family=Quicksand:wght@400;500;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Quicksand', sans-serif !important; }
    
    /* Phông nền pastel nhẹ nhàng */
    .stApp { background: linear-gradient(135deg, #f8fafc 0%, #e0f2fe 100%); }
    
    /* Thiết kế thẻ bo tròn */
    .main-card { 
        background-color: white; 
        padding: 1.5rem; 
        border-radius: 1.5rem; 
        box-shadow: 0 10px 25px rgba(13, 148, 136, 0.08); 
        margin-bottom: 1.5rem; 
        border-top: 5px solid #0d9488; 
    }
    
    h1, h2, h3 { color: #0f172a; font-weight: 700; }
    p, span, label { color: #334155; font-size: 1.05rem; }
    
    /* Nút bấm navy-teal */
    .stButton>button { 
        border-radius: 1rem; 
        background-color: #0d9488; 
        color: white; 
        font-weight: 600; 
        border: none; 
        padding: 0.5rem 2rem;
        transition: all 0.3s;
    }
    .stButton>button:hover { 
        background-color: #0f766e; 
        transform: translateY(-2px); 
        box-shadow: 0 4px 12px rgba(13, 148, 136, 0.2); 
    }
</style>
''', unsafe_allow_html=True)

# ==========================================
# 2. HỆ THỐNG DỮ LIỆU & ZERO-TOUCH LOGGING
# ==========================================
def ghi_du_lieu_vao_sheets(ho_ten, lop, hoat_dong, ket_qua, chi_tiet):
    try:
        if "GCP_CREDS" not in st.secrets or "SHEET_URL" not in st.secrets: 
            return
        
        creds_json = json.loads(st.secrets["GCP_CREDS"])
        scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
        creds = Credentials.from_service_account_info(creds_json, scopes=scopes)
        client = gspread.authorize(creds)
        
        sheet = client.open_by_url(st.secrets["SHEET_URL"]).sheet1
        thoi_gian = (datetime.datetime.utcnow() + datetime.timedelta(hours=7)).strftime("%d/%m/%Y %H:%M:%S")
        
        sheet.append_row([thoi_gian, ho_ten, lop, hoat_dong, ket_qua, chi_tiet])
    except Exception:
        pass # Lỗi kết nối sẽ bị bỏ qua ngầm để học sinh không bị gián đoạn

@st.cache_data
def load_pretest_data():
    try:
        df = pd.read_excel('du_lieu_tinh_huong_dong_hoc_vat_li_10.xlsx', sheet_name='Pre-test')
        return df
    except Exception:
        return pd.DataFrame()

# Khởi tạo trạng thái phiên (Session State)
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.student_name = ""
    st.session_state.student_class = ""
    st.session_state.pretest_completed = False
    st.session_state.pretest_step = 1
    st.session_state.wrong_answers = []

# ==========================================
# 3. GIAO DIỆN ĐĂNG NHẬP
# ==========================================
if not st.session_state.logged_in:
    # Dùng thẻ div ép kích thước 60px và màu đỏ
    st.markdown("""
    <div style='text-align: center; color: #d32f2f; font-size: 60px; font-weight: 900; margin-top: 30px; margin-bottom: 10px; text-shadow: 2px 2px 4px rgba(0,0,0,0.1); letter-spacing: 2px;'>
        PHY-LIFE 10
    </div>
    """, unsafe_allow_html=True)
    
    # Tiêu đề phụ
    st.markdown("""
    <div style='text-align: center; font-size: 1.5rem; margin-bottom: 3rem; color: #1e3a8a; font-weight: 600; text-transform: uppercase;'>
        AI ĐỒNG HÀNH TỰ HỌC CÁ NHÂN HOÁ, KẾT NỐI VẬT LÍ VỚI ĐỜI SỐNG
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
        <div class='main-card' style='margin-bottom: 3.5rem; padding: 2.5rem;'>
            <h3 style='text-align: center; margin-bottom: 0; color: #0f766e;'>Bắt đầu hành trình</h3>
        </div>
        """, unsafe_allow_html=True)
        
        name_input = st.text_input("Tên của em là gì?", placeholder="Ví dụ: Nguyễn Văn A")
        class_input = st.text_input("Em học lớp mấy?", placeholder="Ví dụ: 10A1")
        
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Truy cập hệ thống 🚀", use_container_width=True):
            if name_input and class_input:
                st.session_state.student_name = name_input
                st.session_state.student_class = class_input
                st.session_state.logged_in = True
                ghi_du_lieu_vao_sheets(name_input, class_input, "Đăng nhập", "Thành công", "")
                st.rerun()
            else:
                st.error("⚠️ Em nhớ nhập đầy đủ Tên và Lớp nhé!")

# ==========================================
# 4. KHỐI CHẨN ĐOÁN (PRE-TEST)
# ==========================================
elif not st.session_state.pretest_completed:
    df_pretest = load_pretest_data()
    
    if df_pretest.empty:
        st.error("⚠️ Chưa tìm thấy dữ liệu bài kiểm tra. Cô giáo vui lòng kiểm tra lại file Excel (Tên sheet phải là 'Pre-test').")
    else:
        tong_so_cau = len(df_pretest)
        st.progress(st.session_state.pretest_step / tong_so_cau)
        
        cau_hien_tai = df_pretest.iloc[st.session_state.pretest_step - 1]
        
        st.markdown(f"""
        <div class='main-card' style='padding: 1.5rem; margin-bottom: 1rem;'>
            <h3 style='color: #0f766e; margin-bottom: 0;'>Nhiệm vụ {st.session_state.pretest_step}/{tong_so_cau}</h3>
        </div>
        """, unsafe_allow_html=True)
        
        media_src = str(cau_hien_tai.get('Video/Ảnh', '')).strip()
        if media_src and media_src.lower() != 'nan':
            st.info("🎬 Quan sát tình huống dưới đây:")
            if media_src.startswith("http"):
                st.video(media_src)
            else:
                try:
                    st.image(f"images/{media_src}", use_container_width=True)
                except:
                    st.warning(f"Không tải được tệp: {media_src}")
        
        st.markdown("---")
        
        cau_hoi_text = str(cau_hien_tai.get('Câu hỏi', 'Lỗi: Thiếu câu hỏi'))
        cac_lua_chon = [opt.strip() for opt in str(cau_hien_tai.get('Các lựa chọn', '')).split("|")]
        dap_an_dung = str(cau_hien_tai.get('Đáp án đúng', '')).strip()
        
        tra_loi = st.radio(f"**{cau_hoi_text}**", cac_lua_chon, index=None, key=f"q_{st.session_state.pretest_step}")
        
        st.markdown("<br>", unsafe_allow_html=True)
        col_btn1, col_btn2 = st.columns(2)
        
        with col_btn1:
            if st.session_state.pretest_step > 1:
                if st.button("⬅️ Câu trước", use_container_width=True):
                    st.session_state.pretest_step -= 1
                    st.rerun()
                    
        with col_btn2:
            btn_text = "Hoàn thành & Phân tích 🔍" if st.session_state.pretest_step == tong_so_cau else "Tiếp tục ➡️"
            if st.button(btn_text, use_container_width=True):
                if tra_loi:
                    is_correct = tra_loi.startswith(dap_an_dung)
                    if not is_correct:
                        st.session_state.wrong_answers.append({
                            "cau_hoi": cau_hoi_text,
                            "lua_chon_sai": tra_loi
                        })
                    
                    if st.session_state.pretest_step == tong_so_cau:
                        st.session_state.pretest_completed = True
                        so_cau_dung = tong_so_cau - len(st.session_state.wrong_answers)
                        ghi_du_lieu_vao_sheets(st.session_state.student_name, st.session_state.student_class, "Hoàn thành Pre-test", f"{so_cau_dung}/{tong_so_cau}", f"Số câu sai: {len(st.session_state.wrong_answers)}")
                        st.rerun()
                    else:
                        st.session_state.pretest_step += 1
                        st.rerun()
                else:
                    st.warning("⚠️ Em cần chọn một đáp án để đi tiếp nhé!")

# ==========================================
# 5. KHỐI GIA SƯ SOCRATIC AI & THƯ VIỆN HIỆN TƯỢNG
# ==========================================
else:
    if "GEMINI_API_KEY" not in st.secrets:
        st.error("⚠️ Chưa cấu hình GEMINI_API_KEY trong Streamlit Secrets. Hãy kiểm tra lại cài đặt trên Streamlit Cloud.")
    else:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        
        # System Prompt Kỷ luật thép
        system_instruction = """
        Bạn là Gia sư Socratic môn Vật lí 10, người đồng hành cùng học sinh khám phá kiến thức chứ không phải cỗ máy giải bài.
        
        KỶ LUẬT CỐT LÕI (TUYỆT ĐỐI TUÂN THỦ):
        1. KHÔNG BAO GIỜ cung cấp đáp án trực tiếp, công thức trọn vẹn, hay lời giải cuối cùng.
        2. Nếu học sinh hỏi đáp án, hãy từ chối khéo léo và đặt một câu hỏi gợi mở nhỏ hơn để học sinh tự suy luận.
        3. Luôn phản hồi bằng tiếng Việt, giọng điệu gần gũi, khích lệ (xưng "Thầy/Cô" và gọi "em").
        4. Mỗi lần phản hồi chỉ đặt TỐI ĐA 1 CÂU HỎI để tránh làm học sinh quá tải.
        
        TÍCH HỢP THỰC TIỄN (THƯ VIỆN HIỆN TƯỢNG):
        Khi học sinh bế tắc hoặc bắt đầu một chủ đề mới, bạn BẮT BUỘC phải lấy một ví dụ thực tiễn trong đời sống (giao thông, thể thao, tự nhiên, vũ trụ...) để làm mỏ neo trực quan trước khi đi vào tính toán.
        """
        
        model = genai.GenerativeModel(
            model_name="gemini-3.5-flash-lite",
            system_instruction=system_instruction
        )

        # Xử lý Logic Phân luồng & Lời chào mồi (Chỉ chạy 1 lần đầu tiên)
        if "chat_history" not in st.session_state:
            st.session_state.chat_history = []
            so_cau_sai = len(st.session_state.wrong_answers)
            
            if so_cau_sai == 0:
                loi_chao = f"🎉 Chúc mừng {st.session_state.student_name}! Em đã xuất sắc vượt qua bài kiểm tra với điểm tuyệt đối.\n\nBây giờ, em đã mở khóa **Trợ lý AI Đa năng**. Em có thể hỏi tôi giải thích bất kỳ hiện tượng vật lí nào trong cuộc sống, hoặc yêu cầu tôi tạo ra một bài toán thử thách dành riêng cho em. Em muốn khám phá điều gì nào?"
                st.session_state.chat_history.append({"role": "model", "content": loi_chao})
            else:
                # Gom danh sách lỗi ẩn cho AI
                danh_sach_loi = ""
                for i, loi in enumerate(st.session_state.wrong_answers):
                    danh_sach_loi += f"\n- Câu hỏi: '{loi['cau_hoi']}' | Học sinh chọn sai: '{loi['lua_chon_sai']}'"

                prompt_moi_ngam = f"""
                Học sinh {st.session_state.student_name} vừa làm bài kiểm tra Pre-test và làm sai {so_cau_sai} câu sau:
                {danh_sach_loi}
                
                Nhiệm vụ của bạn:
                Hãy viết một câu chào đầu tiên gửi đến {st.session_state.student_name}.
                1. Động viên em ấy vì đã hoàn thành bài thi.
                2. Chọn ra CÂU SAI ĐẦU TIÊN trong danh sách trên để bắt đầu sửa lỗi. Nhắc lại ngắn gọn câu hỏi và lựa chọn sai của học sinh.
                3. BẮT BUỘC: Lấy ngay 1 ví dụ thực tiễn (như thể thao, xe cộ...) liên quan đến lỗi sai đó, và đặt 1 câu hỏi gợi mở đầu tiên dựa trên ví dụ thực tiễn này để ép học sinh suy luận. 
                (Tuyệt đối không in ra các chỉ dẫn kỹ thuật trong ngoặc vuông, hãy nói chuyện tự nhiên).
                """
                
                with st.spinner("Gia sư đang phân tích bài làm của em..."):
                    try:
                        chat = model.start_chat()
                        response = chat.send_message(prompt_moi_ngam)
                        st.session_state.chat_history.append({"role": "model", "content": response.text})
                    except Exception as e:
                        fallback_msg = f"Chào {st.session_state.student_name}, em đã hoàn thành bài kiểm tra rất cố gắng! Chúng ta có {so_cau_sai} câu cần làm rõ. Em hãy nhắn 'Bắt đầu sửa lỗi' để chúng ta đi vào câu đầu tiên nhé!"
                        st.session_state.chat_history.append({"role": "model", "content": fallback_msg})

        # Giao diện Cửa sổ Chat
        st.markdown("<div class='main-card'>", unsafe_allow_html=True)
        if len(st.session_state.wrong_answers) == 0:
            st.markdown("<h3 style='color: #0f766e; text-align: center;'>🌟 Nhà Khám Phá AI Đa Năng</h3>", unsafe_allow_html=True)
        else:
            st.markdown("<h3 style='color: #0f766e; text-align: center;'>🧠 Phòng Ôn Tập Socratic</h3>", unsafe_allow_html=True)
        st.markdown("---")

        for message in st.session_state.chat_history:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        user_input = st.chat_input("Nhập câu trả lời hoặc câu hỏi của em vào đây...")
        
        if user_input:
            st.session_state.chat_history.append({"role": "user", "content": user_input})
            with st.chat_message("user"):
                st.markdown(user_input)
            
            ghi_du_lieu_vao_sheets(st.session_state.student_name, st.session_state.student_class, "Chat AI", "Hỏi/Đáp", user_input)

            with st.chat_message("model"):
                message_placeholder = st.empty()
                message_placeholder.markdown("Gia sư đang suy nghĩ... ⏳")
                
                try:
                    gemini_history = []
                    for msg in st.session_state.chat_history[:-1]:
                        role = "user" if msg["role"] == "user" else "model"
                        gemini_history.append({"role": role, "parts": [msg["content"]]})
                    
                    chat = model.start_chat(history=gemini_history)
                    response = chat.send_message(user_input)
                    
                    message_placeholder.markdown(response.text)
                    st.session_state.chat_history.append({"role": "model", "content": response.text})
                    
                except Exception as e:
                    message_placeholder.error(f"Đã có lỗi xảy ra kết nối với Gia sư. Em thử lại nhé!")
                    
        st.markdown("</div>", unsafe_allow_html=True)
