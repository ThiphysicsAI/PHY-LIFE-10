import streamlit as st
import pandas as pd
import os
import google.generativeai as genai
import time

# 1. CẤU HÌNH TRANG WEB & MÀU SẮC TÙY CHỈNH
st.set_page_config(page_title="PHY-LIFE 10", page_icon="🚀", layout="wide", initial_sidebar_state="expanded")

# CẤU HÌNH GEMINI API TỪ STREAMLIT SECRETS
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel('gemini-3.5-flash-lite')
    api_ready = True
except Exception as e:
    api_ready = False

# Nhúng CSS tùy chỉnh cơ bản
st.markdown('''
<style>
    @import url('https://fonts.googleapis.com/css2?family=Quicksand:wght@400;500;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Quicksand', sans-serif !important; }
    .stApp { background-color: #FCFBF4; }
    .main-text { color: #1E293B; }
    [data-testid="stSidebar"] { background-color: #ffffff; border-right: 1px solid #e2e8f0; }
    .stAlert { border-radius: 1rem !important; border: none !important; }
    .phy-card { background-color: white; padding: 2rem 1.5rem; border-radius: 1rem; border: 1px solid #e2e8f0; box-shadow: 0 1px 3px rgba(0,0,0,0.1); transition: transform 0.3s, box-shadow 0.3s, border-color 0.3s; height: 100%; text-align: center; display: flex; flex-direction: column; align-items: center; justify-content: center; margin-bottom: 10px; }
    .phy-card:hover { transform: translateY(-5px); box-shadow: 0 10px 15px -3px rgba(0,0,0,0.1); border-color: #0D9488; background-color: #F0FDFA; }
    .icon-box { width: 60px; height: 60px; border-radius: 16px; display: flex; align-items: center; justify-content: center; font-size: 28px; margin-bottom: 15px; }
    .pretest-box { background-color: white; padding: 25px; border-radius: 15px; border: 2px solid #0D9488; box-shadow: 0 4px 6px rgba(13,148,136,0.1); margin-bottom: 20px;}
</style>
''', unsafe_allow_html=True)

# 2. ĐỌC DỮ LIỆU TỪ EXCEL (3 Sheet: Thư viện, Game, Khởi động)
@st.cache_data
def load_data():
    xls = pd.ExcelFile('du_lieu_tinh_huong_dong_hoc_vat_li_10.xlsx')
    sheet_names = xls.sheet_names
    
    # Đọc sheet Thư viện (mặc định sheet 1)
    df_main = pd.read_excel(xls, sheet_name=sheet_names[0])
    
    # Đọc sheet Game
    if 'Du_lieu_Game' in sheet_names:
        df_game = pd.read_excel(xls, sheet_name='Du_lieu_Game')
    else:
        df_game = pd.DataFrame()
        
    # Đọc sheet Khởi động (Pre-test)
    if 'Du_lieu_Khoi_dong' in sheet_names:
        df_pretest = pd.read_excel(xls, sheet_name='Du_lieu_Khoi_dong')
    else:
        df_pretest = pd.DataFrame()
        
    return df_main, df_game, df_pretest

# ==========================================
# 3. KHỞI TẠO TRẠNG THÁI HỆ THỐNG
# ==========================================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.pretest_done = False
    st.session_state.student_name = ""
    st.session_state.student_class = ""
    st.session_state.student_level = "" 
    st.session_state.nav_page = "🏠 Cổng Khởi động"
    
    # Biến cho Pre-test
    st.session_state.pretest_step = 1
    st.session_state.pretest_answers = {} # Lưu đáp án đúng/sai từng câu
    
    # Biến cho Game
    st.session_state.station = 1
    st.session_state.passcodes = ["_", "_", "_", "_"]
    st.session_state.tram2_matched = False
    st.session_state.play_sound = False
    st.session_state.force_unlock_game = False

st.sidebar.markdown("<h2 style='color: #0D9488; font-weight: 700;'>🚀 PHY-LIFE 10</h2>", unsafe_allow_html=True)

# Điều khiển hiển thị Menu
if not st.session_state.pretest_done:
    menu_list = ["🏠 Cổng Khởi động"]
else:
    menu_list = ["📚 Khám phá Hiện tượng", "🎮 Bản đồ Thử thách (Game)", "🤖 Gia sư AI"]

selected_menu = st.sidebar.radio("CHUYÊN MỤC", menu_list, index=menu_list.index(st.session_state.nav_page) if st.session_state.nav_page in menu_list else 0)

if selected_menu != st.session_state.nav_page:
    st.session_state.nav_page = selected_menu
    st.rerun()

st.sidebar.markdown("---")

# Thẻ học sinh ở Sidebar
if st.session_state.logged_in:
    st.sidebar.success(f"👨‍🎓 Học sinh: **{st.session_state.student_name}**\n\n🏫 Lớp: **{st.session_state.student_class}**")
    if st.session_state.pretest_done:
        if st.session_state.student_level == "Cơ bản":
            st.sidebar.warning("📊 Phân luồng: **Cần củng cố nền tảng**")
        else:
            st.sidebar.info("📊 Phân luồng: **Sẵn sàng chinh phục**")

if not api_ready:
    st.sidebar.warning("Vui lòng cấu hình GEMINI_API_KEY trong Settings > Secrets trên Streamlit Cloud.")

try:
    df_main, df_game, df_pretest = load_data()
    
    # ==========================================
    # GIAO DIỆN 1: CỔNG KHỞI ĐỘNG (PRE-TEST ĐỘNG TỪ EXCEL)
    # ==========================================
    if st.session_state.nav_page == "🏠 Cổng Khởi động":
        st.markdown("<h1 style='text-align: center; color: #0D9488;'>Chào mừng đến với PHY-LIFE 10!</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; font-size: 1.2rem; color: #64748b; margin-bottom: 2rem;'>Hệ thống học tập Vật lí thích ứng thông minh</p>", unsafe_allow_html=True)

        if not st.session_state.logged_in:
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                st.markdown("<div class='pretest-box'>", unsafe_allow_html=True)
                st.markdown("<h3 style='text-align: center; color: #1E293B;'>Đăng nhập Hệ thống</h3>", unsafe_allow_html=True)
                name_input = st.text_input("Họ và Tên em là gì?")
                class_input = st.text_input("Em học lớp mấy? (VD: 10A1)")
                
                if st.button("Bắt đầu hành trình 🚀", use_container_width=True):
                    if name_input and class_input:
                        st.session_state.student_name = name_input
                        st.session_state.student_class = class_input
                        st.session_state.logged_in = True
                        st.rerun()
                    else:
                        st.error("Em nhớ nhập đầy đủ Tên và Lớp nhé!")
                st.markdown("</div>", unsafe_allow_html=True)

        elif not st.session_state.pretest_done:
            st.info(f"Chào **{st.session_state.student_name}**! Trước khi mở khóa hệ thống, em hãy xem các đoạn video ngắn và trả lời câu hỏi tương tác dưới đây nhé.")
            
            if df_pretest.empty:
                st.error("⚠️ Hệ thống chưa tìm thấy dữ liệu Khởi động trong file Excel. Cô hãy tạo một Sheet tên là 'Du_lieu_Khoi_dong' nhé!")
            else:
                tong_so_cau = len(df_pretest)
                
                # Render bài test theo tiến trình
                if st.session_state.pretest_step <= tong_so_cau:
                    cau_hien_tai = df_pretest.iloc[st.session_state.pretest_step - 1]
                    
                    st.markdown(f"<h3 style='color: #1E293B;'>Bài kiểm tra chẩn đoán năng lực (Câu {st.session_state.pretest_step}/{tong_so_cau})</h3>", unsafe_allow_html=True)
                    
                    st.markdown("<div class='pretest-box'>", unsafe_allow_html=True)
                    st.markdown(f"#### 🎬 Xem video tình huống:")
                    
                    video_src = str(cau_hien_tai['Video']).strip()
                    start_t = int(cau_hien_tai['Thời gian bắt đầu']) if pd.notna(cau_hien_tai['Thời gian bắt đầu']) else 0
                    
                    # Phát video (Xử lý cả link YouTube và file tải lên thư mục images)
                    if video_src.startswith("http"):
                        st.video(video_src, start_time=start_t)
                    else:
                        vid_path = os.path.join("images", video_src)
                        if os.path.exists(vid_path):
                            st.video(vid_path, start_time=start_t)
                        else:
                            st.warning(f"⚠️ Không tìm thấy video: {video_src}. Em hãy đọc câu hỏi bên dưới nhé.")
                    
                    st.markdown("---")
                    
                    # Lấy danh sách lựa chọn
                    cac_lua_chon = [opt.strip() for opt in str(cau_hien_tai['Các lựa chọn']).split("|")]
                    dap_an_dung = str(cau_hien_tai['Đáp án đúng']).strip()
                    
                    cau_hoi_text = f"**Câu {st.session_state.pretest_step}:** {cau_hien_tai['Câu hỏi']}"
                    tra_loi = st.radio(cau_hoi_text, cac_lua_chon, index=None, key=f"pretest_q_{st.session_state.pretest_step}")
                    
                    col_b1, col_b2 = st.columns(2)
                    with col_b1:
                        if st.session_state.pretest_step > 1:
                            if st.button("⬅️ Quay lại", use_container_width=True):
                                st.session_state.pretest_step -= 1
                                st.rerun()
                    with col_b2:
                        nhan_nut = "Nộp bài & Mở khóa 🔓" if st.session_state.pretest_step == tong_so_cau else "Tiếp tục ➡️"
                        if st.button(nhan_nut, use_container_width=True):
                            if tra_loi:
                                # Chấm điểm ngầm
                                is_correct = tra_loi.startswith(dap_an_dung)
                                st.session_state.pretest_answers[st.session_state.pretest_step] = is_correct
                                
                                # Nếu là câu cuối cùng
                                if st.session_state.pretest_step == tong_so_cau:
                                    score = sum(st.session_state.pretest_answers.values())
                                    ti_le_dung = score / tong_so_cau
                                    
                                    # Phân luồng học sinh (Dựa trên mốc 50%)
                                    if ti_le_dung >= 0.5:
                                        st.session_state.student_level = "Khá giỏi"
                                        st.success(f"🎉 Xuất sắc! Em làm đúng {score}/{tong_so_cau} câu. Nền tảng của em rất vững. Hệ thống đã mở khóa đặc quyền Game Điệp vụ PHYSIX!")
                                    else:
                                        st.session_state.student_level = "Cơ bản"
                                        st.info(f"📊 Em làm đúng {score}/{tong_so_cau} câu. Đừng lo lắng, hệ thống Gia sư AI sẽ đồng hành và hướng dẫn em ôn tập lại thật kỹ nhé!")
                                    
                                    time.sleep(2.5)
                                    st.session_state.pretest_done = True
                                    st.session_state.nav_page = "📚 Khám phá Hiện tượng"
                                    st.rerun()
                                else:
                                    # Chuyển câu tiếp theo
                                    st.session_state.pretest_step += 1
                                    st.rerun()
                            else:
                                st.warning("⚠️ Em cần chọn đáp án để đi tiếp nhé!")
                    st.markdown("</div>", unsafe_allow_html=True)

    # ==========================================
    # GIAO DIỆN 2: THƯ VIỆN HIỆN TƯỢNG (PHÂN LUỒNG)
    # ==========================================
    elif st.session_state.nav_page == "📚 Khám phá Hiện tượng":
        st.markdown("<h2 style='color: #0D9488;'>Thư viện Hiện tượng thực tiễn</h2>", unsafe_allow_html=True)
        
        if st.session_state.student_level == "Cơ bản":
            st.warning(f"🔔 **Gia sư AI:** {st.session_state.student_name} ơi, em hãy đọc thật kỹ phần **'Quan sát'** trước khi trả lời câu hỏi để mở khóa bài học nhé. Cô luôn ở đây để giúp em!")
        else:
            st.success(f"🔔 **Gia sư AI:** Nền tảng của em rất vững! Hãy thử sức phân tích sâu bản chất của các hiện tượng này nhé, {st.session_state.student_name}!")
            
        col_loc1, col_loc2 = st.columns(2)
        with col_loc1:
            danh_sach_bai = df_main['Bài học liên quan'].unique()
            bai_hoc_chon = st.selectbox("📌 Chiều 1: Từ Sách giáo khoa đến Hiện tượng:", danh_sach_bai)
        
        df_loc = df_main[df_main['Bài học liên quan'] == bai_hoc_chon]
        with col_loc2:
            tinh_huong_chon = st.selectbox("🔍 Chiều 2: Chọn tình huống thực tiễn:", df_loc['Tên tình huống'])
        st.markdown("---")
        
        if "current_scenario" not in st.session_state:
            st.session_state.current_scenario = tinh_huong_chon
            st.session_state.da_tra_loi = False
            st.session_state.ai_response = ""
        elif st.session_state.current_scenario != tinh_huong_chon:
            st.session_state.current_scenario = tinh_huong_chon
            st.session_state.da_tra_loi = False
            st.session_state.ai_response = ""
        
        ho_so = df_loc[df_loc['Tên tình huống'] == tinh_huong_chon].iloc[0]
        st.markdown(f"<h1 style='font-size: 2.2rem; margin-bottom: 1rem; color: #1E293B;'>{ho_so['Tên tình huống']}</h1>", unsafe_allow_html=True)
        
        col_trai, col_phai = st.columns([1.1, 1])
        with col_trai:
            st.info(f"📍 **Bối cảnh:** {ho_so['Bối cảnh']}")
            st.markdown(f"<span style='color: #1E293B;'>**Quan sát:** {ho_so['Mô tả quan sát']}</span>", unsafe_allow_html=True)
            
            ten_file_anh = str(ho_so['Tên file ảnh']).strip()
            duong_dan_anh = os.path.join("images", ten_file_anh)
            
            if os.path.exists(duong_dan_anh):
                if ten_file_anh.lower().endswith(('.mp4', '.mov', '.webm')):
                    st.video(duong_dan_anh)
                else:
                    st.image(duong_dan_anh, use_container_width=True)
            else:
                st.warning(f"✍️ Đang chờ nét vẽ Sketchnote hoặc Video... (Tên file cần có: {ten_file_anh})")
                
            st.markdown(f"<span style='color: #1E293B;'>**❓ Câu hỏi gợi mở:** *{ho_so['Câu hỏi gợi mở']}*</span>", unsafe_allow_html=True)
            
            st.markdown(f'''
            <div style="background-color: #F0FDF4; padding: 15px; border-radius: 10px; border-left: 5px solid #22C55E; margin-top: 20px; margin-bottom: 10px;">
                <h4 style="color: #15803D; margin-top: 0; display: flex; align-items: center; gap: 8px;">🤖 Gia sư AI phân tích</h4>
                <p style="font-size: 0.95em; color: #1E293B; margin-bottom: 5px;"><strong>Dựa vào câu hỏi:</strong> <em>"{ho_so['Câu hỏi gợi mở']}"</em></p>
                <p style="font-size: 0.85em; color: #64748b;">Hãy nhập hoặc đọc câu trả lời để mở khóa kiến thức nhé!</p>
            </div>
            ''', unsafe_allow_html=True)
            
            cau_tra_loi_hs = st.text_area("Câu trả lời của em:", height=80, placeholder="Gõ câu trả lời vào đây...")
            col_btn1, col_btn2 = st.columns([1, 1])
            with col_btn1:
                gui_ai = st.button("🚀 Gửi AI phân tích", use_container_width=True)
            with col_btn2:
                import streamlit.components.v1 as components
                components.html('''
                <!DOCTYPE html><html><head><style>.btn { width: 100%; padding: 0.5rem; background-color: #f1f5f9; border: 1px solid #cbd5e1; border-radius: 0.5rem; cursor: pointer; font-weight: 600; font-family: 'Quicksand', sans-serif; color: #334155; display: flex; align-items: center; justify-content: center; gap: 8px; box-sizing: border-box; font-size: 1rem; transition: background-color 0.3s; } .btn:hover { background-color: #e2e8f0; }</style></head>
                <body style="margin: 0; overflow: hidden;"><button class="btn" onclick="startDictation()">🎤 Nhập bằng Giọng nói</button><script>
                function startDictation() { if (window.hasOwnProperty('webkitSpeechRecognition') || window.hasOwnProperty('SpeechRecognition')) { var SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition; var recognition = new SpeechRecognition(); recognition.lang = "vi-VN"; recognition.start(); var btn = document.querySelector('.btn'); btn.innerHTML = "🔴 Đang nghe... (Hãy nói đi)"; btn.style.backgroundColor = "#fee2e2"; btn.style.color = "#991b1b"; btn.style.borderColor = "#fca5a5"; recognition.onresult = function(e) { var text = e.results[0][0].transcript; var textarea = window.parent.document.querySelector('textarea'); if(textarea) { var nativeInputValueSetter = Object.getOwnPropertyDescriptor(window.parent.HTMLTextAreaElement.prototype, "value").set; nativeInputValueSetter.call(textarea, text); var ev2 = new Event('input', { bubbles: true}); textarea.dispatchEvent(ev2); } btn.innerHTML = "🎤 Nhập bằng Giọng nói"; btn.style.backgroundColor = "#f1f5f9"; btn.style.color = "#334155"; btn.style.borderColor = "#cbd5e1"; recognition.stop(); }; recognition.onerror = function(e) { btn.innerHTML = "🎤 Nhập bằng Giọng nói"; btn.style.backgroundColor = "#f1f5f9"; btn.style.color = "#334155"; btn.style.borderColor = "#cbd5e1"; recognition.stop(); alert("Không nghe rõ. Vui lòng thử lại!"); } } else { alert("Trình duyệt không hỗ trợ, hãy dùng Chrome nhé!"); } }
                </script></body></html>''', height=45)

            if gui_ai:
                if cau_tra_loi_hs:
                    st.session_state.da_tra_loi = True
                    if api_ready:
                        with st.spinner("AI đang suy nghĩ..."):
                            prompt_ai = f'''Bạn là Gia sư Vật lí 10 (Socratic Tutor). Trình độ học sinh: {st.session_state.student_level}. 
                            Tình huống: {ho_so['Tên tình huống']}. Câu hỏi đặt ra: {ho_so['Câu hỏi gợi mở']}. Lời giải đúng: {ho_so['Giải thích khoa học']}. Học sinh trả lời: "{cau_tra_loi_hs}". 
                            Quy tắc:
                            - Nếu học sinh Cơ bản: Động viên nhiều hơn, gợi ý từ từ.
                            - Nếu học sinh Khá giỏi: Yêu cầu phân tích sâu hơn.
                            - Nếu sai: ĐỪNG ĐƯA ĐÁP ÁN, hãy đặt một câu hỏi gợi mở để học sinh nhận ra lỗi sai.
                            - BẮT BUỘC CHỐT CÂU CUỐI: "Em hãy xem phần 'Giải thích khoa học' bên cạnh để đối chiếu nhé!"'''
                            try:
                                response = model.generate_content(prompt_ai)
                                st.session_state.ai_response = f"**🤖 Gia sư AI phân tích:** {response.text}"
                            except Exception as e:
                                st.session_state.ai_response = f"❌ AI đang bận, thử lại sau nhé! (Lỗi: {e})"
                    else:
                        st.session_state.ai_response = "⚠️ Tính năng AI chưa được kích hoạt."
                else:
                    st.warning("⚠️ Hãy nhập câu trả lời trước khi gửi!")

            if st.session_state.da_tra_loi and st.session_state.ai_response:
                if "❌" in st.session_state.ai_response or "⚠️" in st.session_state.ai_response:
                    st.error(st.session_state.ai_response)
                else:
                    st.success(st.session_state.ai_response)

        with col_phai:
            if st.session_state.da_tra_loi:
                with st.container():
                    st.markdown("<h3 style='color: #0D9488;'>Giải thích khoa học</h3>", unsafe_allow_html=True)
                    st.write(ho_so['Giải thích khoa học'])
                    st.markdown("<h3 style='color: #0D9488;'>Công thức vận dụng</h3>", unsafe_allow_html=True)
                    st.markdown(ho_so['Công thức'])
                    st.markdown("<h3 style='color: #0D9488;'>Ví dụ định lượng</h3>", unsafe_allow_html=True)
                    st.write(ho_so['Ví dụ định lượng'])
                    st.markdown("<h3 style='color: #0D9488;'>Thử thách tương tác</h3>", unsafe_allow_html=True)
                    st.markdown(str(ho_so['Câu hỏi tương tác']).replace('\\n', '\n\n'))
                    with st.expander("💡 Bấm vào đây để xem Gợi ý / Phản hồi"):
                        st.success(str(ho_so['Đáp án/phản hồi']).replace('\\n', '\n\n'))
                    
                    st.markdown("---")
                    st.info(ho_so['Hoạt động thực hành'])
                    tu_khoa_list = str(ho_so['Từ khóa']).split(',')
                    html_tu_khoa = "".join([f"<span style='background-color: #E2E8F0; padding: 4px 8px; border-radius: 4px; margin-right: 5px; font-size: 0.85em; color: #1E293B;'>{tag.strip()}</span>" for tag in tu_khoa_list])
                    st.markdown(html_tu_khoa, unsafe_allow_html=True)
            else:
                st.markdown('''
                <div style="background-color: #f8fafc; border: 2px dashed #cbd5e1; border-radius: 10px; padding: 40px 20px; text-align: center; margin-top: 20px;">
                    <div style="font-size: 3.5rem; margin-bottom: 15px;">🔒</div>
                    <h3 style="color: #64748b; margin-top: 0;">Nội dung đang khóa</h3>
                    <p style="color: #94a3b8; font-size: 1.05em; max-width: 90%; margin: 0 auto;">Em hãy suy nghĩ và <strong>Gửi AI phân tích</strong> câu trả lời ở cột bên trái để mở khóa phần Giải thích khoa học nhé!</p>
                </div>
                ''', unsafe_allow_html=True)

    # ==========================================
    # GIAO DIỆN 3: BẢN ĐỒ THỬ THÁCH (HARDCODE GAME)
    # ==========================================
    elif st.session_state.nav_page == "🎮 Bản đồ Thử thách (Game)":
        
        # Kiểm tra phân luồng
        if st.session_state.student_level == "Cơ bản" and not st.session_state.force_unlock_game:
            st.markdown("<br><br>", unsafe_allow_html=True)
            st.error("### 🔒 Chuyên mục bị khóa")
            st.markdown("Phần **Bản đồ Thử thách** đòi hỏi vận dụng cao. Dựa vào bài kiểm tra đầu vào, em cần ôn tập lại lý thuyết ở phần **Khám phá Hiện tượng** trước khi nhận nhiệm vụ nhé!")
            if st.button("Mở khóa đặc quyền (Dành cho Giáo viên Test)"):
                st.session_state.force_unlock_game = True
                st.rerun()
        
        else:
            # CSS RIÊNG BIỆT CHO TRANG GAME
            st.markdown('''
            <style>
                .stApp {
                    background-color: #020617 !important;
                    background-image: linear-gradient(rgba(56, 189, 248, 0.05) 1px, transparent 1px), linear-gradient(90deg, rgba(56, 189, 248, 0.05) 1px, transparent 1px) !important;
                    background-size: 30px 30px !important;
                }
                .stMarkdown p, .stMarkdown li, .stMarkdown span, .stMarkdown strong { color: #f8fafc !important; font-size: 1.15rem; }
                .neon-title { text-align: center; color: #ef4444 !important; font-weight: 900; font-size: 3.5rem; text-transform: uppercase; text-shadow: 0 0 10px #dc2626, 0 0 20px #991b1b, 0 0 30px #7f1d1d; margin-bottom: 0px; letter-spacing: 3px; }
                .cyber-warning { background-color: rgba(220, 38, 38, 0.1); border: 2px solid #ef4444; color: #fca5a5 !important; padding: 15px; border-radius: 8px; text-align: center; font-weight: bold; font-size: 1.2rem; margin-bottom: 30px; }
                .led-screen { background-color: #0f172a; border: 3px solid #38bdf8; box-shadow: 0 0 15px rgba(56, 189, 248, 0.4), inset 0 0 20px rgba(0, 0, 0, 0.8); padding: 20px; border-radius: 12px; text-align: center; font-size: 1.8rem; font-family: 'Courier New', Courier, monospace; letter-spacing: 8px; margin-bottom: 30px; color: #38bdf8 !important; }
                .led-code { color: #fde047 !important; font-weight: bold; text-shadow: 0 0 10px #facc15; }
                .mission-panel { background: rgba(15, 23, 42, 0.8); border-left: 5px solid #38bdf8; border-radius: 10px; padding: 25px; margin-bottom: 20px; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3); }
                .mission-header { color: #38bdf8 !important; font-size: 1.8rem !important; font-weight: 800; border-bottom: 1px solid #334155; padding-bottom: 10px; margin-bottom: 15px;}
                div[data-testid="stRadio"], div[data-testid="stSelectbox"], div[data-testid="stTextInput"] { background-color: #f8fafc !important; padding: 20px !important; border-radius: 12px !important; border: 2px solid #38bdf8 !important; box-shadow: 0 0 15px rgba(56,189,248,0.2) !important; margin-top: 10px; margin-bottom: 20px; }
                div[data-testid="stRadio"] p, div[data-testid="stRadio"] span, div[data-testid="stRadio"] div, div[data-testid="stRadio"] label, div[data-testid="stSelectbox"] p, div[data-testid="stSelectbox"] span, div[data-testid="stSelectbox"] label, div[data-testid="stTextInput"] p, div[data-testid="stTextInput"] span, div[data-testid="stTextInput"] label { color: #0f172a !important; font-weight: 700 !important; font-size: 1.1rem !important; }
            </style>
            ''', unsafe_allow_html=True)

            st.markdown("<div class='neon-title'>🕵️‍♂️ ĐIỆP VỤ PHYSIX</div>", unsafe_allow_html=True)
            st.markdown("<div class='cyber-warning'>🚨 CẢNH BÁO: Tàu tốc hành đang mất phanh. Các đặc vụ PHY-LIFE cần giải mã 4 trạm điều khiển để kích hoạt hệ thống phanh khẩn cấp!</div>", unsafe_allow_html=True)
            
            progress_val = int(((st.session_state.station - 1) / 4) * 100)
            st.progress((st.session_state.station - 1) / 4)
            
            st.markdown(f"""
            <div class='led-screen'>
                <span style='color: #38bdf8 !important;'>MÃ KÍCH HOẠT:</span> <span class='led-code'>{st.session_state.passcodes[0]} {st.session_state.passcodes[1]} {st.session_state.passcodes[2]} {st.session_state.passcodes[3]}</span>
            </div>
            """, unsafe_allow_html=True)

            if st.session_state.play_sound:
                sound_html = '<audio autoplay><source src="https://assets.mixkit.co/active_storage/sfx/2013/2013-preview.mp3" type="audio/mpeg"></audio>'
                st.markdown(sound_html, unsafe_allow_html=True)
                st.session_state.play_sound = False

            if st.session_state.station == 1:
                st.markdown("""
                <div class='mission-panel'>
                    <div class='mission-header'>📍 Trạm 1: Không Lưu</div>
                    <p><strong>Mục tiêu:</strong> Vượt qua rào cản tư duy về Rơi tự do & Lực cản.</p>
                    <p><strong>Nhiệm vụ:</strong> Một vận động viên nhảy dù nhảy khỏi máy bay. Sau khi bung dù một lúc, người đó rơi xuống mặt đất với vận tốc không đổi. Hiện tượng này được giải thích bằng khái niệm nào?</p>
                </div>
                """, unsafe_allow_html=True)
                
                ans1 = st.radio("Chọn đáp án để quét mã in chìm:", ["A. Gia tốc rơi tự do giảm dần.", "B. Quán tính triệt tiêu trọng lực.", "C. Lực cản không khí cân bằng với trọng lực.", "D. Động năng ban đầu đã tiêu hao hết."], index=None)
                if st.button("🚀 Xác nhận mã Trạm 1", use_container_width=True):
                    if ans1 and ans1.startswith("C"):
                        st.success("✅ Phân tích đáp án C... Phát hiện mã in chìm! Hệ thống ghi nhận mã số: 4. Đã mở khóa Trạm 2!")
                        st.session_state.passcodes[0] = "4"
                        st.session_state.play_sound = True
                        time.sleep(1.5)
                        st.session_state.station = 2
                        st.rerun()
                    elif ans1:
                        st.error("❌ Truy cập bị từ chối. Tàu vẫn đang lao dốc!")
                    else:
                        st.warning("⚠️ Đặc vụ cần chọn một đáp án!")

            elif st.session_state.station == 2:
                st.markdown("""
                <div class='mission-panel'>
                    <div class='mission-header'>⚙️ Trạm 2: Động Cơ</div>
                    <p><strong>Mục tiêu:</strong> Dịch ngôn ngữ thực tế sang đồ thị v-t.</p>
                    <p><strong>Nhiệm vụ:</strong> Hãy quan sát các đồ thị dưới đây và sắp xếp các thẻ Hiện tượng (1, 2, 3, 4) khớp với các thẻ Đồ thị (A, B, C, D).</p>
                </div>
                """, unsafe_allow_html=True)
                
                anh_do_thi = os.path.join("images", "do_thi_tram2.jpg") 
                if os.path.exists(anh_do_thi):
                    img_col1, img_col2, img_col3 = st.columns([1, 2, 1])
                    with img_col2:
                        st.image(anh_do_thi, use_container_width=True)
                
                col1, col2 = st.columns(2)
                with col1:
                    g1 = st.selectbox("1. Đạp phanh", ["Chưa ghép", "Thẻ A", "Thẻ B", "Thẻ C", "Thẻ D"])
                    g2 = st.selectbox("2. Dừng chờ đèn đỏ", ["Chưa ghép", "Thẻ A", "Thẻ B", "Thẻ C", "Thẻ D"])
                with col2:
                    g3 = st.selectbox("3. Nhấn ga khởi hành", ["Chưa ghép", "Thẻ A", "Thẻ B", "Thẻ C", "Thẻ D"])
                    g4 = st.selectbox("4. Chạy ổn định trên cao tốc", ["Chưa ghép", "Thẻ A", "Thẻ B", "Thẻ C", "Thẻ D"])

                if not st.session_state.tram2_matched:
                    if st.button("🔍 Kiểm tra ghép nối", use_container_width=True):
                        if g1 == "Thẻ D" and g2 == "Thẻ A" and g3 == "Thẻ C" and g4 == "Thẻ B":
                            st.session_state.tram2_matched = True
                            st.rerun()
                        else:
                            st.error("❌ Ghép thẻ thất bại. Động cơ báo lỗi đồng bộ!")
                
                if st.session_state.tram2_matched:
                    st.success("✅ Ghép nối thành công! Mặt sau của 4 thẻ lật lên hiện ra một thông điệp ẩn...")
                    st.info("💻 **Hệ thống báo:** Giải mã phép toán `(D + A) x (C - B)`. Biết rằng D=5, A=3, C=4, B=3.")
                    ans2 = st.text_input("Nhập mật mã số học (1 chữ số) thu được:")
                    if st.button("🚀 Xác nhận mã Trạm 2", use_container_width=True):
                        if ans2.strip() == "8":
                            st.success("✅ Hệ thống ghi nhận mã số: 8. Đã mở khóa Trạm 3!")
                            st.session_state.passcodes[1] = "8"
                            st.session_state.play_sound = True
                            time.sleep(1.5)
                            st.session_state.station = 3
                            st.rerun()
                        else:
                            st.error("❌ Sai mã số. Động cơ đang quá tải!")

            elif st.session_state.station == 3:
                st.markdown("""
                <div class='mission-panel'>
                    <div class='mission-header'>👁️ Trạm 3: Ảo Giác</div>
                    <p><strong>Mục tiêu:</strong> Phá vỡ góc nhìn tuyệt đối về hệ quy chiếu.</p>
                    <p><strong>Nhiệm vụ:</strong> Thả thùng hàng từ máy bay đang bay ngang. Đặc vụ hãy xác định Đúng (1) hoặc Sai (0) cho các nhận định sau:</p>
                </div>
                """, unsafe_allow_html=True)
                
                q1 = st.radio("1. Người đứng trên đảo thấy quỹ đạo của thùng hàng là đường thẳng đứng.", ["Chưa chọn", "Đúng (1)", "Sai (0)"], horizontal=True)
                q2 = st.radio("2. Phi công thấy quỹ đạo của thùng hàng là đường thẳng đứng.", ["Chưa chọn", "Đúng (1)", "Sai (0)"], horizontal=True)
                q3 = st.radio("3. Máy bay bay càng nhanh thì thùng hàng rơi chạm đất càng lâu.", ["Chưa chọn", "Đúng (1)", "Sai (0)"], horizontal=True)
                q4 = st.radio("4. Ngay trước khi chạm đất, vận tốc ngang của thùng hàng vẫn bằng vận tốc máy bay lúc thả (bỏ qua sức cản).", ["Chưa chọn", "Đúng (1)", "Sai (0)"], horizontal=True)

                if st.button("🚀 Tổng hợp mã Nhị phân", use_container_width=True):
                    if q1 == "Sai (0)" and q2 == "Đúng (1)" and q3 == "Sai (0)" and q4 == "Đúng (1)":
                        st.success("✅ Dữ liệu nhị phân thu được: **0101**. Quy đổi sang hệ thập phân chính là số 5!")
                        st.session_state.passcodes[2] = "5"
                        st.session_state.play_sound = True
                        time.sleep(2)
                        st.session_state.station = 4
                        st.rerun()
                    elif "Chưa chọn" in [q1, q2, q3, q4]:
                        st.warning("⚠️ Đặc vụ cần đánh giá toàn bộ 4 nhận định!")
                    else:
                        st.error("❌ Lỗi hệ quy chiếu! Mã nhị phân bị sai lệch. Hãy tính lại!")

            elif st.session_state.station == 4:
                st.markdown("""
                <div class='mission-panel'>
                    <div class='mission-header'>⚡ Trạm 4: Bứt Tốc</div>
                    <p><strong>Mục tiêu:</strong> Chọn hệ quy chiếu linh hoạt để giải quyết định lượng.</p>
                    <p><strong>Nhiệm vụ:</strong> Băng chuyền sân bay di chuyển với tốc độ 1 m/s. An đi bộ trên băng chuyền với tốc độ 2 m/s so với băng chuyền. Vali của An bị bỏ quên, trôi theo băng chuyền cách An 14 mét phía trước.<br>Hỏi An mất bao nhiêu giây để bắt kịp vali?</p>
                </div>
                """, unsafe_allow_html=True)
                
                ans4 = st.text_input("Nhập thời gian (giây):")
                if st.button("🚀 Xác nhận mã Trạm 4", use_container_width=True):
                    if ans4.strip() == "7":
                        st.success("✅ Phân tích chuẩn xác! Vali đứng yên so với băng chuyền, nên thời gian = 14m / 2(m/s) = 7s. Hệ thống ghi nhận mã số: 7.")
                        st.session_state.passcodes[3] = "7"
                        st.session_state.play_sound = True
                        time.sleep(2)
                        st.session_state.station = 5
                        st.rerun()
                    else:
                        st.error("❌ Tính toán sai lệch. Cảnh báo va chạm cận kề!")

            elif st.session_state.station == 5:
                st.markdown("<div class='game-station' style='background: linear-gradient(135deg, #b91c1c 0%, #7f1d1d 100%); border: 3px solid #fca5a5;'><h3 style='color: white !important;'>🛑 HỆ THỐNG PHANH KHẨN CẤP</h3></div>", unsafe_allow_html=True)
                st.warning("⚠️ YÊU CẦU NHẬP MÃ KÍCH HOẠT 4 CHỮ SỐ ĐỂ DỪNG TÀU!")
                
                final_code = st.text_input("Nhập mật mã:", type="password", placeholder="Nhập 4 chữ số thu thập được...")
                if st.button("🔴 KÍCH HOẠT PHANH", use_container_width=True):
                    if final_code == "4857":
                        st.balloons()
                        st.markdown("<div style='background-color: rgba(34, 197, 94, 0.2); padding: 40px; border-radius: 15px; text-align: center; border: 2px solid #4ade80; box-shadow: 0 0 30px rgba(74, 222, 128, 0.5);'><h1 style='color: #4ade80 !important; font-size: 3.5rem; margin-bottom: 10px; text-shadow: 0 0 10px #4ade80;'>🎉 KÍCH HOẠT THÀNH CÔNG!</h1><h2 style='color: #86efac !important;'>CỨU HỘ HOÀN TẤT. KIỆN HÀNG TRI THỨC ĐÃ ĐƯỢC BẢO VỆ.</h2><p style='font-size: 1.2rem; color: #f8fafc !important; margin-top: 20px;'>Các đặc vụ PHY-LIFE đã xuất sắc hoàn thành nhiệm vụ!</p></div>", unsafe_allow_html=True)
                        st.session_state.play_sound = True
                        st.markdown("<br>", unsafe_allow_html=True)
                        if st.button("🔄 Chơi lại Điệp vụ", use_container_width=True):
                            st.session_state.station = 1
                            st.session_state.passcodes = ["_", "_", "_", "_"]
                            st.session_state.tram2_matched = False
                            st.rerun()
                    else:
                        st.error("❌ HỆ THỐNG TỪ CHỐI. TÀU VẪN ĐANG LAO DỐC!")

    # === GIAO DIỆN 4: GIA SƯ AI ===
    elif st.session_state.nav_page == "🤖 Gia sư AI":
        st.markdown("<h2 style='color: #0D9488;'>🤖 Gia sư AI (Phòng Tập Gym Vật Lí)</h2>", unsafe_allow_html=True)
        st.markdown(f"<span class='main-text'>Chào {st.session_state.student_name}! Cô là Gia sư AI. Em muốn tạo thêm bài tập luyện tập, hỏi đáp hay khám phá hiện tượng nào?</span>", unsafe_allow_html=True)

        if not api_ready:
            st.warning("⚠️ Tính năng AI chưa được kích hoạt. Vui lòng kiểm tra lại GEMINI_API_KEY trong Secrets.")
        else:
            if "chat_messages" not in st.session_state:
                st.session_state.chat_messages = []
            for msg in st.session_state.chat_messages:
                with st.chat_message(msg["role"]):
                    st.markdown(msg["content"])
            if prompt := st.chat_input("Nhập yêu cầu của em (VD: Tạo cho em 1 bài tập về gia tốc)..."):
                st.session_state.chat_messages.append({"role": "user", "content": prompt})
                with st.chat_message("user"):
                    st.markdown(prompt)
                with st.chat_message("assistant"):
                    with st.spinner("Cô đang phân tích..."):
                        history_context = "".join([f"{'Học sinh' if m['role']=='user' else 'Cô giáo'}: {m['content']}\n" for m in st.session_state.chat_messages[-5:-1]])
                        sys_prompt = f'''Bạn là Gia sư Vật lí lớp 10 (Socratic Tutor). Trình độ của học sinh này là: {st.session_state.student_level}.
                        Học sinh yêu cầu: "{prompt}". Lịch sử: {history_context}. 
                        Yêu cầu: Giải đáp, tạo bài tập, hoặc sửa lỗi sai. Bắt buộc dùng phương pháp gợi mở (không đưa đáp án ngay). Xưng "cô", gọi "em".'''
                        try:
                            response = model.generate_content(sys_prompt)
                            st.markdown(response.text)
                            st.session_state.chat_messages.append({"role": "assistant", "content": response.text})
                        except Exception as e:
                            st.error(f"Hệ thống đang bận, em thử lại sau nhé! (Lỗi chi tiết: {e})")

except Exception as e:
    st.error(f"Có lỗi hệ thống: {e}")
