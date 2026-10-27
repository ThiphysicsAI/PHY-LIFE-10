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
@st.cache_data
def load_phenomena_data():
    try:
        # Dữ liệu hiện tượng được lưu tại Sheet1
        df = pd.read_excel('du_lieu_tinh_huong_dong_hoc_vat_li_10.xlsx', sheet_name='Sheet1')
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
    <div style='text-align: center; font-size: 1.2rem; margin-bottom: 3rem; color: #1e3a8a; font-weight: 600; text-transform: uppercase;'>
        AI ĐỒNG HÀNH TỰ HỌC CÁ NHÂN HOÁ, KẾT NỐI VẬT LÍ VỚI ĐỜI SỐNG
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
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
        
        # --- BỔ SUNG LỜI GIỚI THIỆU KHỞI ĐỘNG CHỈ Ở BƯỚC 1 ---
        if st.session_state.pretest_step == 1:
             st.markdown("""
             <div style='background-color: #f0fdfa; padding: 1.5rem; border-radius: 1rem; border-left: 5px solid #14b8a6; margin-bottom: 1.5rem;'>
                 <h4 style='color: #0f766e; margin-top: 0;'>Chào mừng em đến với TRẠM KHỞI ĐỘNG! 🕵️‍♂️</h4>
                 <p style='color: #334155; margin-bottom: 0;'>Trạm khởi động – không chấm điểm!
Đây không phải bài kiểm tra. Hãy thử sức và đừng lo sai: mỗi lỗi sai giúp AI hiểu bạn cần hỗ trợ ở đâu. Điều quan trọng là cách bạn suy nghĩ, không phải đáp án cuối cùng.</p>
             </div>
             """, unsafe_allow_html=True)
        # ---------------------------------------------------

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
                # Kiểm tra định dạng video
                if media_src.lower().endswith(('.mp4', '.mov', '.avi')):
                    try:
                        st.video(f"images/{media_src}") # Đảm bảo video nằm trong thư mục images
                    except Exception as e:
                        st.warning(f"Không tải được video: {media_src}. Lỗi: {e}")
                # Xử lý hình ảnh
                else:
                    try:
                        st.image(f"images/{media_src}", use_container_width=True)
                    except Exception as e:
                        st.warning(f"Không tải được hình ảnh: {media_src}. Lỗi: {e}")
        
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
        
        # --- BƠM DỮ LIỆU CÂU SAI VÀO BỘ NHỚ LÕI ---
        danh_sach_loi_he_thong = ""
        if len(st.session_state.wrong_answers) > 0:
            danh_sach_loi_he_thong = "\n\nDANH SÁCH CÁC CÂU HỌC SINH ĐANG LÀM SAI:\n"
            for i, loi in enumerate(st.session_state.wrong_answers):
                danh_sach_loi_he_thong += f"- Câu {i+1}: {loi['cau_hoi']} | Đáp án HS chọn sai: {loi['lua_chon_sai']}\n"
        
        # System Prompt Kỷ luật thép (Cập nhật ngữ cảnh sư phạm)
        system_instruction = f"""
        Bạn là Gia sư Socratic môn Vật lí 10, người đồng hành cùng học sinh khám phá kiến thức. Đối tượng học sinh của bạn ở mức trung bình - khá, vì vậy hãy luôn kiên nhẫn, giải thích dễ hiểu, không dùng từ ngữ học thuật phức tạp.
        
        KỶ LUẬT CỐT LÕI (TUYỆT ĐỐI TUÂN THỦ):
        1. KHÔNG BAO GIỜ cung cấp đáp án trực tiếp, công thức trọn vẹn, hay lời giải cuối cùng.
        2. Nếu học sinh hỏi đáp án hoặc yêu cầu giải hộ, hãy từ chối khéo léo và đặt một câu hỏi gợi mở nhỏ hơn.
        3. Luôn phản hồi bằng tiếng Việt, giọng điệu gần gũi, khích lệ (Luôn xưng "Cô" và gọi "em").
        4. Mỗi lần phản hồi chỉ đặt TỐI ĐA 1 CÂU HỎI để tránh làm học sinh quá tải.
        
        TÍCH HỢP THỰC TIỄN (THƯ VIỆN HIỆN TƯỢNG):
        Khi học sinh bế tắc hoặc bắt đầu một chủ đề mới, bạn BẮT BUỘC phải lấy một ví dụ thực tiễn trong đời sống (giao thông, thể thao, tự nhiên...) để làm mỏ neo trực quan trước khi đi vào tính toán.
        
        Nếu học sinh yêu cầu giúp đỡ một "Câu" cụ thể (ví dụ: "giúp em câu 2"), HÃY TỰ ĐỘNG tra cứu nội dung câu đó trong danh sách dưới đây và bắt đầu gợi mở, TUYỆT ĐỐI KHÔNG bắt học sinh chép lại đề bài.
        {danh_sach_loi_he_thong}
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
                loi_chao = f"🎉 Chúc mừng {st.session_state.student_name}! Em đã xuất sắc vượt qua bài kiểm tra với điểm tuyệt đối.\n\nBây giờ, em đã mở khóa **Trợ lý AI Đa năng**. Em có thể hỏi Cô giải thích bất kỳ hiện tượng vật lí nào trong cuộc sống, hoặc yêu cầu Cô tạo ra một bài toán thử thách dành riêng cho em. Em muốn khám phá điều gì nào?"
                st.session_state.chat_history.append({"role": "model", "content": loi_chao})
            else:
                prompt_moi_ngam = f"""
                Học sinh {st.session_state.student_name} vừa làm bài kiểm tra Pre-test và làm sai {so_cau_sai} câu.
                
                Nhiệm vụ của bạn:
                Hãy viết một câu chào đầu tiên gửi đến {st.session_state.student_name}.
                1. Động viên em ấy vì đã hoàn thành bài thi.
                2. Bắt đầu ngay vào việc hướng dẫn Câu 1 (trong danh sách sai). Nhắc lại ngắn gọn nội dung Câu 1.
                3. BẮT BUỘC: Lấy ngay 1 ví dụ thực tiễn liên quan đến Câu 1, và đặt 1 câu hỏi gợi mở đầu tiên dựa trên ví dụ đó.
                """
                
                with st.spinner("Cô đang phân tích bài làm của em..."):
                    try:
                        chat = model.start_chat()
                        response = chat.send_message(prompt_moi_ngam)
                        st.session_state.chat_history.append({"role": "model", "content": response.text})
                    except Exception as e:
                        fallback_msg = f"Chào {st.session_state.student_name}, em đã hoàn thành bài kiểm tra rất cố gắng! Chúng ta có {so_cau_sai} câu cần làm rõ. Em hãy nhắn 'Cô giúp em câu 1' để chúng ta bắt đầu nhé!"
                        st.session_state.chat_history.append({"role": "model", "content": fallback_msg})

        # Giao diện Cửa sổ Chat
        st.markdown("<div class='main-card'>", unsafe_allow_html=True)
        if len(st.session_state.wrong_answers) == 0:
            st.markdown("""
            <div style='padding: 1.5rem; margin-bottom: 1.5rem; background-color: #f0fdfa; border-radius: 1rem; border-left: 5px solid #0d9488;'>
                <h3 style='color: #0f766e; text-align: center; margin-top: 0;'>🌟 KHÔNG GIAN KHÁM PHÁ & THƯ VIỆN HIỆN TƯỢNG</h3>
                <p style='text-align: center; color: #1e3a8a; font-style: italic; margin-bottom: 0;'>
                    Nơi em tự do chọn các hiện tượng thực tế để tìm hiểu và trò chuyện cùng Nhà Khám Phá AI.
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            # --- Tích hợp Thư viện Hiện tượng (Đọc trực tiếp từ Thu_vien_hien_tuong) ---
            try:
                # Đọc dữ liệu từ file Excel
                df_hien_tuong = pd.read_excel('du_lieu_tinh_huong_dong_hoc_vat_li_10.xlsx', sheet_name='Thu_vien_hien_tuong')
                
                if not df_hien_tuong.empty:
                    st.markdown("#### 📚 Thư Viện Hiện Tượng Thực Tế")
                    hien_tuong_chon = st.selectbox("Chọn một tình huống em muốn khám phá:", df_hien_tuong['Tên tình huống'].tolist())
                    
                    if hien_tuong_chon:
                        chi_tiet = df_hien_tuong[df_hien_tuong['Tên tình huống'] == hien_tuong_chon].iloc[0]
                        
                        # Hiển thị Bài học liên quan
                        bai_hoc = str(chi_tiet.get('Bài học liên quan', '')).strip()
                        if bai_hoc and bai_hoc.lower() != 'nan':
                            st.markdown(f"<p style='color: #0d9488; font-weight: 600;'>📖 Bài học liên quan: {bai_hoc}</p>", unsafe_allow_html=True)
                        
                        # Hiển thị Ảnh minh họa
                        anh_minh_hoa = str(chi_tiet.get('Tên file ảnh', '')).strip()
                        if anh_minh_hoa and anh_minh_hoa.lower() != 'nan':
                            try:
                                st.image(f"images/{anh_minh_hoa}", use_container_width=True)
                            except Exception:
                                st.warning(f"⚠️ Không tìm thấy tệp ảnh: {anh_minh_hoa} trong thư mục images/")
                        
                        # Hiển thị Mô tả quan sát
                        st.info(f"**👀 Quan sát:** {chi_tiet.get('Mô tả quan sát', '')}")
                        
                        # BỔ SUNG: Hiển thị Câu hỏi gợi mở / Câu hỏi khám phá
                        cau_hoi_kham_pha = str(chi_tiet.get('Câu hỏi gợi mở', '')).strip()
                        if cau_hoi_kham_pha and cau_hoi_kham_pha.lower() != 'nan':
                            st.warning(f"**❓ Thử thách suy nghĩ:** {cau_hoi_kham_pha}")
                        
                        st.markdown("<br>", unsafe_allow_html=True)
                        if st.button("💬 Nhờ AI giải thích hiện tượng này", use_container_width=True):
                            # --- RÚT DỮ LIỆU TỪ EXCEL ĐỂ NEO AI ---
                            giai_thich = str(chi_tiet.get('Giải thích khoa học', '')).strip()
                            cong_thuc = str(chi_tiet.get('Công thức', '')).strip()
                            vi_du = str(chi_tiet.get('Ví dụ định lượng', '')).strip()
                            dieu_kien = str(chi_tiet.get('Điều kiện/giới hạn', '')).strip()
                            cau_hoi_tuong_tac = str(chi_tiet.get('Câu hỏi tương tác', '')).strip()
                            
                            # --- NHÚNG LỆNH NGẦM (PROMPT INJECTION) ---
                            user_prompt_hien_tuong = f"""
                            Cô hãy đóng vai Nhà Khám phá Vật lí, cùng học sinh thảo luận về hiện tượng: '{hien_tuong_chon}'. 
                            Tình huống quan sát: {chi_tiet.get('Mô tả quan sát', '')}. 
                            Câu hỏi mở màn: {cau_hoi_kham_pha}.
                            
                            BẠN BẮT BUỘC PHẢI DỰA VÀO KHUNG KIẾN THỨC SAU ĐÂY CỦA GIÁO VIÊN ĐỂ DẪN DẮT (Không tự sáng tác ngoài lề):
                            - Giải thích bản chất: {giai_thich if giai_thich != 'nan' else 'Chưa có'}
                            - Công thức trọng tâm: {cong_thuc if cong_thuc != 'nan' else 'Chưa có'}
                            - Ví dụ định lượng: {vi_du if vi_du != 'nan' else 'Chưa có'}
                            - Điều kiện/Giới hạn áp dụng: {dieu_kien if dieu_kien != 'nan' else 'Chưa có'}
                            - Gợi ý câu hỏi dẫn dắt: {cau_hoi_tuong_tac if cau_hoi_tuong_tac != 'nan' else 'Chưa có'}
                            
                            Nhiệm vụ Socratic của bạn:
                            1. KHÔNG copy paste "Giải thích bản chất" đưa cho học sinh.
                            2. Hãy dùng "Gợi ý câu hỏi dẫn dắt" để đặt ra MỘT câu hỏi nhỏ, giúp học sinh tự đi đến kết luận.
                            3. Nếu học sinh trả lời đúng một phần, hãy khen ngợi và hỏi tiếp phần còn lại.
                            """
                            
                            st.session_state.chat_history.append({"role": "user", "content": f"Cô ơi, cùng em khám phá tình huống này nhé: **{hien_tuong_chon}**!"})
                            ghi_du_lieu_vao_sheets(st.session_state.student_name, st.session_state.student_class, "Thư viện", "Chọn hiện tượng", hien_tuong_chon)
                            
                            with st.spinner("Nhà Khám Phá AI đang phân tích dữ liệu của cô giáo..."):
                                try:
                                    gemini_history = []
                                    for msg in st.session_state.chat_history[:-1]:
                                        role = "user" if msg["role"] == "user" else "model"
                                        gemini_history.append({"role": role, "parts": [msg["content"]]})
                                    
                                    chat = model.start_chat(history=gemini_history)
                                    response = chat.send_message(user_prompt_hien_tuong)
                                    
                                    st.session_state.chat_history.append({"role": "model", "content": response.text})
                                except Exception as e:
                                    st.error("Có lỗi kết nối AI, em thử lại nhé!")
                            st.rerun()
            except Exception as e:
                st.warning(f"⚠️ Không thể tải dữ liệu Thư viện hiện tượng. Lỗi chi tiết: {e}")
                
            st.markdown("---")

        for message in st.session_state.chat_history:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        # ... (Phần code xử lý user_input giữ nguyên) ...

        user_input = st.chat_input("Nhập câu trả lời hoặc câu hỏi của em vào đây...")
        
        if user_input:
            st.session_state.chat_history.append({"role": "user", "content": user_input})
            with st.chat_message("user"):
                st.markdown(user_input)
            
            ghi_du_lieu_vao_sheets(st.session_state.student_name, st.session_state.student_class, "Chat AI", "Hỏi/Đáp", user_input)

            with st.chat_message("model"):
                message_placeholder = st.empty()
                message_placeholder.markdown("Cô đang suy nghĩ... ⏳")
                
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
                    message_placeholder.error(f"Đã có lỗi xảy ra kết nối với hệ thống. Em thử lại nhé!")
