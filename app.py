import streamlit as st
import pandas as pd
import google.generativeai as genai
import gspread
from google.oauth2.service_account import Credentials
import json
import datetime

# 1. CẤU HÌNH GIAO DIỆN TỐI GIẢN (Dải màu navy-teal, thẻ bo góc tròn)
st.set_page_config(page_title="PHY-LIFE 10", page_icon="🚀", layout="centered")

st.markdown('''
<style>
    @import url('https://fonts.googleapis.com/css2?family=Quicksand:wght@400;500;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Quicksand', sans-serif !important; }
    
    /* Phông nền pastel nhẹ nhàng giảm mỏi mắt */
    .stApp { background: linear-gradient(135deg, #f8fafc 0%, #e0f2fe 100%); }
    
    /* Thiết kế thẻ bo tròn */
    .main-card { 
        background-color: white; 
        padding: 2rem; 
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
    .stButton>button:hover { background-color: #0f766e; transform: translateY(-2px); box-shadow: 0 4px 12px rgba(13, 148, 136, 0.2); }
</style>
''', unsafe_allow_html=True)

# 2. HÀM QUẢN TRỊ ZERO-TOUCH (Tự động ghi Google Sheets)
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
        pass # Lỗi kết nối sẽ được bỏ qua ngầm để không gián đoạn luồng học của học sinh

# 3. KẾT NỐI NGÂN HÀNG DỮ LIỆU EXCEL
@st.cache_data
def load_pretest_data():
    try:
        # Chỉ cần tải duy nhất 1 sheet Pre-test
        df = pd.read_excel('du_lieu_tinh_huong_dong_hoc_vat_li_10.xlsx', sheet_name='Pre-test')
        return df
    except Exception:
        return pd.DataFrame()

# Khởi tạo trạng thái phiên làm việc
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.student_name = ""
    st.session_state.student_class = ""

# ========================================================
# 4. GIAO DIỆN ĐĂNG NHẬP (Luồng tuyến tính)
if not st.session_state.logged_in:
    st.markdown("<h1 style='text-align: center; color: #0d9488; margin-top: 2rem;'>PHY-LIFE 10</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; font-size: 1.2rem; margin-bottom: 3rem;'>Hệ sinh thái Học tập Thích ứng - Chương Động học</p>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        # Gộp chung khung và chữ vào một lệnh để chữ nằm gọn trong khung
        st.markdown("""
        <div class='main-card' style='margin-bottom: 1.5rem; padding: 1.5rem;'>
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
                st.session_state.pretest_completed = False
                st.session_state.pretest_step = 1
                st.session_state.wrong_answers = [] # Lưu các câu sai để đẩy cho AI
                ghi_du_lieu_vao_sheets(name_input, class_input, "Đăng nhập", "Thành công", "")
                st.rerun()
            else:
                st.error("⚠️ Em nhớ nhập đầy đủ Tên và Lớp nhé!")

# 5. KHỐI CHẨN ĐOÁN PRE-TEST
elif not getattr(st.session_state, 'pretest_completed', False):
    df_pretest = load_pretest_data()
    
    if df_pretest.empty:
        st.error("⚠️ Chưa tìm thấy dữ liệu bài kiểm tra. Cô giáo vui lòng kiểm tra lại file Excel (Tên sheet phải là 'Pre-test').")
    else:
        tong_so_cau = len(df_pretest)
        
        # --- THÊM PHẦN GIỚI THIỆU PRE-TEST ---
        st.markdown(f"""
        <div style='background-color: #e0f2fe; padding: 1.5rem; border-radius: 1rem; border-left: 5px solid #0284c7; margin-bottom: 2rem;'>
            <h4 style='color: #0369a1; margin-top: 0;'>Chào {st.session_state.student_name}, Chào mừng em đến với Trạm Chẩn Đoán! 🎯</h4>
            <p style='color: #334155; margin-bottom: 0;'>Để AI có thể thiết kế lộ trình học tập phù hợp nhất, em hãy hoàn thành {tong_so_cau} nhiệm vụ khởi động dưới đây. Hãy quan sát kỹ các hiện tượng thực tế và suy luận nhé.</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Thanh tiến trình
        st.progress(st.session_state.pretest_step / tong_so_cau)
        
        cau_hien_tai = df_pretest.iloc[st.session_state.pretest_step - 1]
        
        st.markdown(f"""
        <div class='main-card' style='padding: 1.5rem; margin-bottom: 1rem;'>
            <h3 style='color: #0f766e; margin-bottom: 0;'>Nhiệm vụ {st.session_state.pretest_step}/{tong_so_cau}</h3>
        </div>
        """, unsafe_allow_html=True)
        
        # --- SỬA LẠI LOGIC ĐỌC MEDIA (HỖ TRỢ LOCAL VIDEO .MP4) ---
        media_src = str(cau_hien_tai.get('Video/Ảnh', '')).strip()
        if media_src and media_src.lower() != 'nan':
            st.info("🎬 Quan sát tình huống dưới đây:")
            if media_src.startswith("http"):
                st.video(media_src)
            else:
                file_path = f"images/{media_src}"
                # Kiểm tra đuôi file để quyết định dùng st.video hay st.image
                if media_src.lower().endswith(('.mp4', '.mov', '.webm')):
                    try:
                        st.video(file_path)
                    except Exception:
                        st.warning(f"Không tải được video: {media_src}. Đảm bảo file nằm trong thư mục 'images'")
                else:
                    try:
                        st.image(file_path, use_container_width=True)
                    except Exception:
                        st.warning(f"Không tải được hình ảnh: {media_src}. Đảm bảo file nằm trong thư mục 'images'")
        
        st.markdown("---")
        
        # Phần Câu hỏi & Trắc nghiệm
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
                    # Nếu câu sai, lưu lại để AI phân tích
                    if not is_correct:
                        # Kiểm tra xem câu này đã có trong danh sách sai chưa (tránh trùng lặp khi quay lại)
                        if not any(item['cau_hoi'] == cau_hoi_text for item in st.session_state.wrong_answers):
                            st.session_state.wrong_answers.append({
                                "cau_hoi": cau_hoi_text,
                                "lua_chon_sai": tra_loi,
                                "dap_an_dung": dap_an_dung
                            })
                    else:
                        # Nếu chọn đúng mà trước đó từng lưu sai thì xóa đi
                        st.session_state.wrong_answers = [item for item in st.session_state.wrong_answers if item['cau_hoi'] != cau_hoi_text]

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
        
        st.markdown("</div>", unsafe_allow_html=True)
# ========================================================
# 6. KHỐI GIA SƯ SOCRATIC AI & THƯ VIỆN HIỆN TƯỢNG
else:
    # 6.1 Khởi tạo API và Cấu hình System Prompt
    if "GEMINI_API_KEY" not in st.secrets:
        st.error("⚠️ Chưa cấu hình GEMINI_API_KEY trong Streamlit Secrets.")
    else:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        
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
        
        # Khởi tạo mô hình Gemini 3.5 Flash Lite
        model = genai.GenerativeModel(
            model_name="gemini-3.5-flash-lite",
            system_instruction=system_instruction
        )

        # 6.2 Xử lý phân luồng và Tạo câu chào mồi (Prompt mồi)
        if "chat_history" not in st.session_state:
            st.session_state.chat_history = []
            
            # Phân tích kết quả Pre-test
            so_cau_sai = len(st.session_state.wrong_answers)
            
            if so_cau_sai == 0:
                # Nhóm Đạt 100%
                loi_chao = f"🎉 Chúc mừng {st.session_state.student_name}! Em đã xuất sắc vượt qua bài kiểm tra với điểm tuyệt đối.\n\nBây giờ, em đã mở khóa **Trợ lý AI Đa năng**. Em có thể hỏi tôi giải thích bất kỳ hiện tượng vật lí nào trong cuộc sống, hoặc yêu cầu tôi tạo ra một bài toán thử thách dành riêng cho em (ví dụ: bài toán gia tốc trong bóng đá). Em muốn khám phá điều gì nào?"
                st.session_state.chat_history.append({"role": "model", "content": loi_chao})
            else:
                # Nhóm cần hỗ trợ (Có câu sai) - Tạo Prompt mồi ẩn để AI tự sinh lời chào
                danh_sach_loi = ""
                for i, loi in enumerate(st.session_state.wrong_answers):
                    danh_sach_loi += f"\n- Câu hỏi {i+1}: '{loi['cau_hoi']}' | Học sinh chọn sai: '{loi['lua_chon_sai']}'"

                prompt_moi_ngam = f"""
                Học sinh {st.session_state.student_name} vừa làm bài kiểm tra Pre-test và làm sai {so_cau_sai} câu sau:
                {danh_sach_loi}
                
                Nhiệm vụ của bạn:
                Hãy viết một câu chào đầu tiên gửi đến {st.session_state.student_name}.
                1. Động viên em ấy vì đã hoàn thành bài thi.
                2. Chọn ra CÂU SAI ĐẦU TIÊN trong danh sách trên để bắt đầu sửa lỗi. Nhắc lại ngắn gọn câu hỏi và lựa chọn sai của học sinh.
                3. BẮT BUỘC: Lấy ngay 1 ví dụ thực tiễn (như thể thao, xe cộ...) liên quan đến lỗi sai đó, và đặt 1 câu hỏi gợi mở đầu tiên dựa trên ví dụ thực tiễn này để ép học sinh suy luận. 
                (Không được in ra các chỉ dẫn kỹ thuật trong ngoặc vuông, hãy nói chuyện tự nhiên).
                """
                
                # Gọi AI tạo lời chào đầu tiên một cách tự nhiên
                with st.spinner("Gia sư đang phân tích bài làm của em..."):
                    try:
                        chat = model.start_chat()
                        response = chat.send_message(prompt_moi_ngam)
                        st.session_state.chat_history.append({"role": "model", "content": response.text})
                    except Exception as e:
                        # Fallback nếu API lỗi
                        st.session_state.chat_history.append({"role": "model", "content": f"Chào {st.session_state.student_name}, em đã hoàn thành bài kiểm tra rất cố gắng! Chúng ta có {so_cau_sai} câu cần làm rõ. Em hãy nhắn 'Bắt đầu sửa lỗi' để chúng ta đi vào câu đầu tiên nhé!"})
