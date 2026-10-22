import streamlit as st
import pandas as pd
import os
import google.generativeai as genai
import time
import datetime

# --- HÀM THEO DÕI LƯỢT TRA CỨU TỔNG ---
def get_view_count():
    try:
        with open("view_count.txt", "r") as f:
            return int(f.read())
    except Exception:
        return 0

def add_view_count():
    count = get_view_count() + 1
    with open("view_count.txt", "w") as f:
        f.write(str(count))
    return count

# 1. CẤU HÌNH TRANG WEB & MÀU SẮC
st.set_page_config(page_title="PHY-LIFE 10", page_icon="🚀", layout="wide", initial_sidebar_state="expanded")

try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel('gemini-3.5-flash-lite')
    api_ready = True
except Exception as e:
    api_ready = False

# Nhúng CSS tùy chỉnh
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
    .report-box { background: linear-gradient(135deg, #ffffff 0%, #f0fdf4 100%); border: 2px solid #22c55e; padding: 30px; border-radius: 15px; box-shadow: 0 10px 15px rgba(34,197,94,0.1); }
</style>
''', unsafe_allow_html=True)

# 2. ĐỌC DỮ LIỆU TỪ EXCEL
@st.cache_data
def load_data():
    xls = pd.ExcelFile('du_lieu_tinh_huong_dong_hoc_vat_li_10.xlsx')
    sheet_names = xls.sheet_names
    df_main = pd.read_excel(xls, sheet_name=sheet_names[0])
    df_game = pd.read_excel(xls, sheet_name='Du_lieu_Game') if 'Du_lieu_Game' in sheet_names else pd.DataFrame()
    df_pretest = pd.read_excel(xls, sheet_name='Du_lieu_Khoi_dong') if 'Du_lieu_Khoi_dong' in sheet_names else pd.DataFrame()
    return df_main, df_game, df_pretest

# ==========================================
# 3. KHỞI TẠO TRẠNG THÁI HỆ THỐNG & TRACKING DỮ LIỆU
# ==========================================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.pretest_done = False
    st.session_state.student_name = ""
    st.session_state.student_class = ""
    st.session_state.student_level = "" 
    st.session_state.nav_page = "🏠 Cổng Khởi động"
    st.session_state.pretest_step = 1
    st.session_state.pretest_answers = {} 

if "station" not in st.session_state:
    st.session_state.station = 1
if "passcodes" not in st.session_state:
    st.session_state.passcodes = []
if "tram2_matched" not in st.session_state:
    st.session_state.tram2_matched = False
if "play_sound" not in st.session_state:
    st.session_state.play_sound = False
if "force_unlock_game" not in st.session_state:
    st.session_state.force_unlock_game = False

# --- CÁC BIẾN "CAMERA NGẦM" THU THẬP DỮ LIỆU HỌC TẬP ---
if "login_time" not in st.session_state:
    st.session_state.login_time = None # Thời điểm đăng nhập
if "error_count" not in st.session_state:
    st.session_state.error_count = 0 # Số lần làm sai Game/Pre-test
if "viewed_topics" not in st.session_state:
    st.session_state.viewed_topics = [] # Các hiện tượng đã tra cứu
if "questions_asked" not in st.session_state:
    st.session_state.questions_asked = [] # Câu hỏi đã hỏi AI
if "ai_report_generated" not in st.session_state:
    st.session_state.ai_report_generated = "" # Lưu báo cáo AI

st.sidebar.markdown("<h2 style='color: #0D9488; font-weight: 700;'>🚀 PHY-LIFE 10</h2>", unsafe_allow_html=True)

# LỘ TRÌNH CÁ NHÂN HÓA MENU CÓ THÊM BÁO CÁO
if not st.session_state.pretest_done:
    menu_list = ["🏠 Cổng Khởi động"]
else:
    if st.session_state.student_level in ["Khá giỏi", "Tốt"]:
        menu_list = ["📚 Khám phá Hiện tượng", "🎮 Thử thách (Game)", "🤖 Hỏi Nhà khám phá AI", "📊 Báo cáo Năng lực"]
    else: 
        menu_list = ["📖 Ôn tập cốt lõi", "🤖 Gia sư AI (Hỗ trợ)", "📊 Báo cáo Năng lực"]

selected_menu = st.sidebar.radio("CHUYÊN MỤC", menu_list, index=menu_list.index(st.session_state.nav_page) if st.session_state.nav_page in menu_list else 0)

if selected_menu != st.session_state.nav_page:
    st.session_state.nav_page = selected_menu
    st.rerun()

st.sidebar.markdown("---")

if st.session_state.logged_in:
    st.sidebar.success(f"👨‍🎓 Học sinh: **{st.session_state.student_name}**\n\n🏫 Lớp: **{st.session_state.student_class}**")
    if st.session_state.pretest_done:
        if st.session_state.student_level == "Cơ bản":
            st.sidebar.error("📊 Phân luồng: **Cần ôn tập cốt lõi**")
        else:
            st.sidebar.info("📊 Phân luồng: **Đã mở khóa hệ thống**")

if not api_ready:
    st.sidebar.warning("Vui lòng cấu hình GEMINI_API_KEY trong Settings > Secrets trên Streamlit Cloud.")

try:
    df_main, df_game, df_pretest = load_data()
    
    # ==========================================
    # CỔNG KHỞI ĐỘNG (PRE-TEST)
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
                        st.session_state.login_time = time.time() # Bắt đầu bấm giờ học
                        st.rerun()
                    else:
                        st.error("Em nhớ nhập đầy đủ Tên và Lớp nhé!")
                st.markdown("</div>", unsafe_allow_html=True)

        elif not st.session_state.pretest_done:
            st.info(f"Chào **{st.session_state.student_name}**! Để hệ thống thiết kế lộ trình học tốt nhất, em hãy xem các video ngắn và trả lời câu hỏi tương tác dưới đây nhé. (Yêu cầu: Đúng 100% để mở khóa toàn bộ Hệ thống)")
            
            if df_pretest.empty:
                st.error("⚠️ Lỗi: Không tìm thấy dữ liệu Sheet 'Du_lieu_Khoi_dong'.")
            else:
                tong_so_cau = len(df_pretest)
                
                if st.session_state.pretest_step <= tong_so_cau:
                    cau_hien_tai = df_pretest.iloc[st.session_state.pretest_step - 1]
                    
                    st.markdown(f"<h3 style='color: #1E293B;'>Bài kiểm tra chẩn đoán năng lực (Câu {st.session_state.pretest_step}/{tong_so_cau})</h3>", unsafe_allow_html=True)
                    st.markdown("<div class='pretest-box'>", unsafe_allow_html=True)
                    st.markdown(f"#### 🎬 Xem video tình huống:")
                    
                    video_src = str(cau_hien_tai['Video']).strip()
                    start_t = int(cau_hien_tai['Thời gian bắt đầu']) if pd.notna(cau_hien_tai['Thời gian bắt đầu']) else 0
                    
                    if video_src.startswith("http"):
                        st.video(video_src, start_time=start_t, autoplay=True)
                    else:
                        vid_path = os.path.join("images", video_src)
                        if os.path.exists(vid_path):
                            st.video(vid_path, start_time=start_t, autoplay=True)
                        else:
                            st.warning(f"⚠️ Không tìm thấy video: {video_src}.")
                    
                    st.markdown("---")
                    
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
                        nhan_nut = "Nộp bài & Phân luồng 🔓" if st.session_state.pretest_step == tong_so_cau else "Tiếp tục ➡️"
                        if st.button(nhan_nut, use_container_width=True):
                            if tra_loi:
                                is_correct = tra_loi.startswith(dap_an_dung)
                                st.session_state.pretest_answers[st.session_state.pretest_step] = is_correct
                                
                                if not is_correct:
                                    st.session_state.error_count += 1 # Đếm số lỗi
                                
                                if st.session_state.pretest_step == tong_so_cau:
                                    score = sum(st.session_state.pretest_answers.values())
                                    if score == tong_so_cau:
                                        st.session_state.student_level = "Tốt"
                                        st.success(f"🎉 Xuất sắc! Em làm đúng 100% ({score}/{tong_so_cau} câu). Hệ thống đã mở khóa TOÀN BỘ CHỨC NĂNG!")
                                        st.session_state.nav_page = "📚 Khám phá Hiện tượng"
                                    else:
                                        st.session_state.student_level = "Cơ bản"
                                        st.error(f"📊 Em làm đúng {score}/{tong_so_cau} câu. Dưới 100% điểm, hệ thống sẽ điều hướng em đến tab Ôn tập cốt lõi cùng Gia sư AI.")
                                        st.session_state.nav_page = "📖 Ôn tập cốt lõi"
                                    
                                    time.sleep(3)
                                    st.session_state.pretest_done = True
                                    st.rerun()
                                else:
                                    st.session_state.pretest_step += 1
                                    st.rerun()
                            else:
                                st.warning("⚠️ Em cần chọn đáp án để đi tiếp nhé!")
                    st.markdown("</div>", unsafe_allow_html=True)

    # ==========================================
    # LỘ TRÌNH 1: NHÓM CƠ BẢN
    # ==========================================
    elif st.session_state.nav_page == "📖 Ôn tập cốt lõi":
        st.markdown("<h2 style='color: #ef4444;'>📖 Ôn tập cốt lõi Động học</h2>", unsafe_allow_html=True)
        st.warning("Em chưa đạt đủ 100% điểm ở bài đánh giá năng lực. Hãy xem lại các khái niệm quan trọng dưới đây một cách chậm rãi, nhờ Gia sư AI hỗ trợ, và thực hiện lại bài kiểm tra nhé!")
        
        col1, col2 = st.columns([2, 1])
        with col1:
            st.video("https://www.youtube.com/watch?v=kKKM8Y-u7ds")
        with col2:
            st.markdown("### 🤖 Tóm tắt nhanh từ AI")
            if st.button("Yêu cầu AI tóm tắt từ khóa", use_container_width=True):
                if api_ready:
                    with st.spinner("AI đang tổng hợp..."):
                        try:
                            summary_prompt = "Tóm tắt 3 từ khóa vật lý quan trọng về chương Động học lớp 10 (Sự rơi tự do, Tốc độ, Gia tốc) ngắn gọn, dễ hiểu cho học sinh yếu."
                            summary = model.generate_content(summary_prompt)
                            st.info(summary.text)
                        except:
                            st.error("Lỗi kết nối AI.")
                else:
                    st.error("API Key chưa sẵn sàng.")
            
            st.markdown("---")
            if st.button("🔄 LÀM LẠI BÀI KIỂM TRA", use_container_width=True):
                st.session_state.pretest_done = False
                st.session_state.pretest_step = 1
                st.session_state.pretest_answers = {}
                st.session_state.nav_page = "🏠 Cổng Khởi động"
                st.rerun()

    elif st.session_state.nav_page == "🤖 Gia sư AI (Hỗ trợ)":
        st.markdown("<h2 style='color: #0D9488;'>🤖 Gia sư AI (Socratic Tutor)</h2>", unsafe_allow_html=True)
        st.markdown("<span class='main-text'>Chào em! Cô là Gia sư AI. Cô ở đây để giúp em giải đáp những thắc mắc. Em không hiểu chỗ nào cứ hỏi cô nhé!</span>", unsafe_allow_html=True)

        if not api_ready:
            st.warning("⚠️ Tính năng AI chưa được kích hoạt.")
        else:
            if "tutor_messages" not in st.session_state:
                st.session_state.tutor_messages = []
            for msg in st.session_state.tutor_messages:
                with st.chat_message(msg["role"]):
                    st.markdown(msg["content"])
                    
            if prompt := st.chat_input("Hỏi Gia sư AI tại đây..."):
                st.session_state.tutor_messages.append({"role": "user", "content": prompt})
                st.session_state.questions_asked.append(prompt) # Lưu câu hỏi vào data
                with st.chat_message("user"):
                    st.markdown(prompt)
                with st.chat_message("assistant"):
                    with st.spinner("Cô đang suy nghĩ..."):
                        history_context = "".join([f"{'HS' if m['role']=='user' else 'AI'}: {m['content']}\n" for m in st.session_state.tutor_messages[-5:-1]])
                        socratic_prompt = f'''
                        Bạn là Gia sư Vật lí lớp 10. Dùng phương pháp Socratic: Đặt MỘT câu hỏi gợi mở để học sinh tự tìm ra đáp án. Tuyệt đối không giải bài hộ. Xưng cô, gọi em.
                        Lịch sử: {history_context}
                        Học sinh hỏi: "{prompt}"
                        '''
                        try:
                            response = model.generate_content(socratic_prompt)
                            st.markdown(response.text)
                            st.session_state.tutor_messages.append({"role": "assistant", "content": response.text})
                        except Exception as e:
                            st.error(f"Lỗi: {e}")

    # ==========================================
    # LỘ TRÌNH 2: NHÓM TỐT
    # ==========================================
    elif st.session_state.nav_page == "📚 Khám phá Hiện tượng":
        col_title, col_stat = st.columns([3, 1])
        with col_title:
            st.markdown("<h2 style='color: #0D9488;'>Thư viện Hiện tượng thực tiễn</h2>", unsafe_allow_html=True)
            
        col_loc1, col_loc2 = st.columns(2)
        with col_loc1:
            danh_sach_bai = df_main['Bài học liên quan'].unique()
            bai_hoc_chon = st.selectbox("📌 Chiều 1: Từ Sách giáo khoa đến Hiện tượng:", danh_sach_bai)
        
        df_loc = df_main[df_main['Bài học liên quan'] == bai_hoc_chon]
        with col_loc2:
            tinh_huong_chon = st.selectbox("🔍 Chiều 2: Chọn tình huống thực tiễn:", df_loc['Tên tình huống'])
            
        if "last_viewed" not in st.session_state:
            st.session_state.last_viewed = tinh_huong_chon
            if tinh_huong_chon not in st.session_state.viewed_topics:
                st.session_state.viewed_topics.append(tinh_huong_chon) # Ghi nhận đã xem
            current_views = add_view_count()
        elif st.session_state.last_viewed != tinh_huong_chon:
            st.session_state.last_viewed = tinh_huong_chon
            if tinh_huong_chon not in st.session_state.viewed_topics:
                st.session_state.viewed_topics.append(tinh_huong_chon) # Ghi nhận đã xem
            current_views = add_view_count()
        else:
            current_views = get_view_count()

        with col_stat:
            st.markdown(f'''
            <div style="background-color: #FEF2F2; padding: 6px 10px; border-radius: 8px; border: 1.5px solid #EF4444; text-align: center; float: right; width: 130px; margin-top: 15px;">
                <p style="margin: 0; color: #991B1B; font-weight: 700; font-size: 0.75rem; text-transform: uppercase;">🔥 Lượt tra cứu</p>
                <h4 style="margin: 0; color: #DC2626; font-size: 1.3rem; line-height: 1.2;">{current_views}</h4>
            </div>
            ''', unsafe_allow_html=True)
            
        st.markdown("---")
        
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
                    
            st.markdown(f"<span style='color: #1E293B;'>**❓ Câu hỏi gợi mở:** *{ho_so['Câu hỏi gợi mở']}*</span>", unsafe_allow_html=True)
            
            st.markdown(f'''
            <div style="background-color: #F0FDF4; padding: 15px; border-radius: 10px; border-left: 5px solid #22C55E; margin-top: 20px; margin-bottom: 10px;">
                <h4 style="color: #15803D; margin-top: 0;">🤖 Gia sư AI phân tích</h4>
                <p style="font-size: 0.85em; color: #64748b;">Hãy nhập hoặc đọc câu trả lời để mở khóa kiến thức nhé!</p>
            </div>
            ''', unsafe_allow_html=True)
            
            cau_tra_loi_hs = st.text_area("Câu trả lời của em:", height=80)
            if st.button("🚀 Gửi AI phân tích", use_container_width=True):
                if cau_tra_loi_hs:
                    st.session_state.da_tra_loi = True
                    st.session_state.questions_asked.append(cau_tra_loi_hs) # Ghi nhận câu trả lời
                    if api_ready:
                        with st.spinner("AI đang suy nghĩ..."):
                            prompt_ai = f'''Bạn là cô giáo Vật lí 10. Tình huống: {ho_so['Tên tình huống']}. Câu hỏi: {ho_so['Câu hỏi gợi mở']}. Giải thích đúng: {ho_so['Giải thích khoa học']}. HS trả lời: "{cau_tra_loi_hs}". Nhận xét 2-3 câu. Khen nếu đúng, sửa nếu sai. LUÔN CHỐT CÂU CUỐI: "Em hãy xem phần 'Giải thích khoa học' bên cạnh để hiểu rõ hơn nhé!"'''
                            try:
                                response = model.generate_content(prompt_ai)
                                st.session_state.ai_response = f"**🤖 AI phân tích:** {response.text}"
                            except:
                                st.session_state.ai_response = "❌ Lỗi kết nối AI."
                else:
                    st.warning("⚠️ Hãy nhập câu trả lời trước khi gửi!")

            if getattr(st.session_state, 'da_tra_loi', False) and getattr(st.session_state, 'ai_response', ""):
                st.success(st.session_state.ai_response)

        with col_phai:
            if getattr(st.session_state, 'da_tra_loi', False):
                with st.container():
                    st.markdown("<h3 style='color: #0D9488;'>Giải thích khoa học</h3>", unsafe_allow_html=True)
                    st.write(ho_so['Giải thích khoa học'])
                    st.markdown("<h3 style='color: #0D9488;'>Công thức vận dụng</h3>", unsafe_allow_html=True)
                    st.markdown(ho_so['Công thức'])
                    st.markdown("<h3 style='color: #0D9488;'>Ví dụ định lượng</h3>", unsafe_allow_html=True)
                    st.write(ho_so['Ví dụ định lượng'])
                    with st.expander("💡 Bấm vào đây để xem Gợi ý / Phản hồi"):
                        st.success(str(ho_so['Đáp án/phản hồi']).replace('\\n', '\n\n'))
            else:
                st.markdown('''<div style="background-color: #f8fafc; border: 2px dashed #cbd5e1; border-radius: 10px; padding: 40px 20px; text-align: center; margin-top: 20px;"><div style="font-size: 3.5rem; margin-bottom: 15px;">🔒</div><h3 style="color: #64748b; margin-top: 0;">Nội dung đang khóa</h3></div>''', unsafe_allow_html=True)

    # ==========================================
    # GIAO DIỆN 3: THỬ THÁCH (GAME)
    # ==========================================
    elif st.session_state.nav_page == "🎮 Thử thách (Game)":
        if st.session_state.student_level == "Cơ bản" and not st.session_state.force_unlock_game:
            st.error("### 🔒 Chuyên mục bị khóa")
            if st.button("Mở khóa đặc quyền (Dành cho Giáo viên Test)"):
                st.session_state.force_unlock_game = True
                st.rerun()
        else:
            st.markdown('''
            <style>
                .stApp { background-color: #020617 !important; background-image: linear-gradient(rgba(56, 189, 248, 0.05) 1px, transparent 1px), linear-gradient(90deg, rgba(56, 189, 248, 0.05) 1px, transparent 1px) !important; background-size: 30px 30px !important; }
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
            st.markdown("<div class='cyber-warning'>🚨 CẢNH BÁO: Tàu tốc hành đang mất phanh. Giải mã 4 trạm điều khiển để kích hoạt phanh khẩn cấp!</div>", unsafe_allow_html=True)
            
            if df_game.empty:
                st.error("⚠️ Không tìm thấy dữ liệu Game.")
            else:
                tong_so_tram = len(df_game)
                if len(st.session_state.passcodes) != tong_so_tram:
                    st.session_state.passcodes = ["_"] * tong_so_tram
                
                st.progress((st.session_state.station - 1) / tong_so_tram)
                
                passcodes_display = []
                for i in range(tong_so_tram):
                    if i < st.session_state.station - 1:
                        ma_khoa = str(df_game.iloc[i].get('Mã khóa', '')).strip()
                        passcodes_display.append(ma_khoa if ma_khoa and ma_khoa != 'nan' else '✔️')
                    else:
                        passcodes_display.append("_")
                
                st.markdown(f"<div class='led-screen'><span style='color: #38bdf8 !important;'>MÃ KÍCH HOẠT:</span> <span class='led-code'>{' '.join(passcodes_display)}</span></div>", unsafe_allow_html=True)

                if st.session_state.station <= tong_so_tram:
                    tram_data = df_game.iloc[st.session_state.station - 1]
                    
                    st.markdown(f"""
                    <div class='mission-panel'>
                        <div class='mission-header'>📍 Trạm {tram_data.get('Trạm', st.session_state.station)}: {tram_data.get('Tên trạm', '')}</div>
                        <p><strong>Nhiệm vụ:</strong> {tram_data.get('Nhiệm vụ', '')}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    anh_minh_hoa = str(tram_data.get('Ảnh minh họa', '')).strip()
                    if anh_minh_hoa and anh_minh_hoa != 'nan':
                        img_path = os.path.join("images", anh_minh_hoa)
                        if os.path.exists(img_path):
                            img_col1, img_col2, img_col3 = st.columns([1, 2, 1])
                            with img_col2: st.image(img_path, use_container_width=True)

                    loai_cau_hoi = str(tram_data.get('Loại thử thách', '')).strip()
                    dap_an_dung = str(tram_data.get('Đáp án đúng', '')).strip()
                    du_lieu_chon = str(tram_data.get('Dữ liệu lựa chọn', '')).strip()
                    
                    if loai_cau_hoi == "Trắc nghiệm":
                        lua_chon = [opt.strip() for opt in du_lieu_chon.split("|")]
                        ans = st.radio("Chọn đáp án:", ["Chưa chọn"] + lua_chon, key=f"q_{st.session_state.station}")
                        if st.button("🚀 Xác nhận"):
                            if ans != "Chưa chọn" and ans.startswith(dap_an_dung):
                                st.session_state.station += 1
                                st.rerun()
                            else:
                                st.session_state.error_count += 1 # ĐẾM LỖI
                                st.error("❌ Sai rồi!")
                                
                    elif loai_cau_hoi == "Ghép nối":
                        pairs = du_lieu_chon.split("|")
                        vethrai = [p.split("=")[0].strip() for p in pairs if "=" in p]
                        vephai = [p.split("=")[1].strip() for p in pairs if "=" in p]
                        options = ["Chưa ghép"] + sorted(list(set(vephai)))
                        
                        user_answers = {}
                        col1, col2 = st.columns(2)
                        for idx, trai in enumerate(vethrai):
                            with col1 if idx % 2 == 0 else col2:
                                user_answers[trai] = st.selectbox(trai, options, key=f"match_{st.session_state.station}_{idx}")
                        
                        if not st.session_state.tram2_matched:
                            if st.button("🔍 Kiểm tra ghép nối"):
                                correct = all(user_answers[trai] == phai for trai, phai in zip(vethrai, vephai))
                                if correct:
                                    st.session_state.tram2_matched = True
                                    st.rerun()
                                else:
                                    st.session_state.error_count += 1 # ĐẾM LỖI
                                    st.error("❌ Ghép thẻ thất bại!")
                        
                        if st.session_state.tram2_matched:
                            st.success(f"✅ Ghép nối thành công! {tram_data.get('Phản hồi đúng', '')}")
                            ans2 = st.text_input("Nhập mã thu được sau khi ghép:", key=f"ans_match_{st.session_state.station}")
                            if st.button("🚀 Xác nhận mã"):
                                if ans2.strip().lower() == dap_an_dung.lower():
                                    st.session_state.station += 1
                                    st.session_state.tram2_matched = False
                                    st.rerun()
                                else:
                                    st.session_state.error_count += 1 # ĐẾM LỖI
                                    st.error("❌ Sai mã số.")
                                    
                    elif loai_cau_hoi == "Đúng/Sai":
                        statements = [opt.strip() for opt in du_lieu_chon.split("|")]
                        correct_answers = [ans.strip() for ans in dap_an_dung.split("|")]
                        user_answers = []
                        for idx, stmt in enumerate(statements):
                            ans = st.radio(f"{idx+1}. {stmt}", ["Chưa chọn", "Đúng", "Sai"], horizontal=True, key=f"tf_{st.session_state.station}_{idx}")
                            user_answers.append(ans)
                        if st.button("🚀 Tổng hợp mã Nhị phân"):
                            if user_answers == correct_answers:
                                st.session_state.station += 1
                                st.rerun()
                            else:
                                st.session_state.error_count += 1 # ĐẾM LỖI
                                st.error("❌ Mã nhị phân bị sai lệch.")
                                
                    elif loai_cau_hoi == "Điền khuyết": 
                        ans = st.text_input("Nhập kết quả/mã thu được:", key=f"q_{st.session_state.station}")
                        if st.button("🚀 Xác nhận mã"):
                            if ans.strip().lower() == dap_an_dung.lower():
                                st.session_state.station += 1
                                st.rerun()
                            else:
                                st.session_state.error_count += 1 # ĐẾM LỖI
                                st.error("❌ Tính toán sai lệch.")

                else:
                    st.balloons()
                    correct_final_code = "".join([str(df_game.iloc[i].get('Mã khóa', '')).strip() for i in range(tong_so_tram) if str(df_game.iloc[i].get('Mã khóa', '')).strip() and str(df_game.iloc[i].get('Mã khóa', '')).strip() != 'nan'])
                    st.markdown("<div style='background-color: rgba(34, 197, 94, 0.2); padding: 40px; border-radius: 15px; text-align: center; border: 2px solid #4ade80;'><h1 style='color: #4ade80;'>🎉 KÍCH HOẠT THÀNH CÔNG!</h1></div>", unsafe_allow_html=True)
                    st.markdown("<br>", unsafe_allow_html=True)
                    if st.button("🔄 Chơi lại Điệp vụ"):
                        st.session_state.station = 1
                        st.rerun()

    # === GIAO DIỆN 5: CHATBOT AI ===
    elif st.session_state.nav_page == "🤖 Hỏi Nhà khám phá AI":
        if st.session_state.student_level == "Cơ bản" and not st.session_state.force_unlock_game:
            st.error("### 🔒 Chuyên mục bị khóa")
        else:
            st.markdown("<h2 style='color: #0D9488;'>🤖 Nhà khám phá AI</h2>", unsafe_allow_html=True)
            if not api_ready:
                st.warning("⚠️ Tính năng AI chưa được kích hoạt.")
            else:
                if "chat_exp_messages" not in st.session_state:
                    st.session_state.chat_exp_messages = []
                for msg in st.session_state.chat_exp_messages:
                    with st.chat_message(msg["role"]):
                        st.markdown(msg["content"])
                if prompt := st.chat_input("Nhập câu hỏi..."):
                    st.session_state.chat_exp_messages.append({"role": "user", "content": prompt})
                    st.session_state.questions_asked.append(prompt) # Lưu câu hỏi
                    with st.chat_message("user"):
                        st.markdown(prompt)
                    with st.chat_message("assistant"):
                        with st.spinner("Cô đang phân tích..."):
                            sys_prompt = f'Bạn là "Nhà khám phá Vật lí", chuyên gia sư phạm. Học sinh hỏi: "{prompt}"'
                            try:
                                response = model.generate_content(sys_prompt)
                                st.markdown(response.text)
                                st.session_state.chat_exp_messages.append({"role": "assistant", "content": response.text})
                            except:
                                st.error(f"Hệ thống đang bận!")

    # ==========================================
    # GIAO DIỆN 6: BÁO CÁO NĂNG LỰC CÁ NHÂN (AI TỰ ĐỘNG XUẤT)
    # ==========================================
    elif st.session_state.nav_page == "📊 Báo cáo Năng lực":
        st.markdown("<h2 style='color: #0D9488;'>📊 Báo cáo Năng lực Cá nhân</h2>", unsafe_allow_html=True)
        st.markdown("Hệ thống AI sẽ thu thập toàn bộ dữ liệu học tập của em (từ lúc đăng nhập đến hiện tại) để phân tích và đưa ra lời khuyên cá nhân hóa.")
        
        # 1. Thu thập dữ liệu
        thoi_gian_hoc = round((time.time() - st.session_state.login_time) / 60) if st.session_state.login_time else 0
        so_loi = st.session_state.error_count
        chu_de_da_xem = ", ".join(list(set(st.session_state.viewed_topics))) if st.session_state.viewed_topics else "Chưa tra cứu hiện tượng nào"
        cau_hoi_ai = ", ".join(st.session_state.questions_asked) if st.session_state.questions_asked else "Chưa đặt câu hỏi nào cho AI"
        
        # 2. Hiển thị Dashboard mini
        col1, col2, col3 = st.columns(3)
        col1.metric("⏳ Thời gian học tập", f"{thoi_gian_hoc} phút")
        col2.metric("❌ Số lần mắc lỗi (Game/Test)", f"{so_loi} lỗi")
        col3.metric("🔍 Chủ đề đã khám phá", f"{len(set(st.session_state.viewed_topics))} chủ đề")
        
        st.markdown("---")
        
        # 3. Xuất báo cáo bằng AI
        if st.button("TẠO BÁO CÁO BẰNG AI 🚀", use_container_width=True):
            if api_ready:
                with st.spinner("AI đang tổng hợp và phân tích dữ liệu học tập của em..."):
                    prompt_report = f"""
                    Bạn là Chuyên gia Giáo dục Vật lý đánh giá học sinh.
                    Tên học sinh: {st.session_state.student_name}.
                    Phân luồng năng lực ban đầu: {st.session_state.student_level}.
                    Thời gian đã học trên hệ thống: {thoi_gian_hoc} phút.
                    Số lần giải bài tập/chơi game sai: {so_loi}.
                    Các hiện tượng đã quan tâm tra cứu: {chu_de_da_xem}.
                    Các câu hỏi đã hỏi AI: {cau_hoi_ai}.
                    
                    Hãy viết một "Báo cáo Năng lực Cá nhân" (khoảng 150-200 chữ) gửi trực tiếp cho học sinh (xưng Cô, gọi Em).
                    Cấu trúc báo cáo:
                    1. Đánh giá thái độ học tập (dựa vào thời gian và sự tò mò qua câu hỏi/tra cứu).
                    2. Nhận xét về kỹ năng giải quyết vấn đề (dựa vào số lỗi sai và phân luồng, nếu sai nhiều thì khuyên kiên nhẫn, sai ít thì khen ngợi).
                    3. Đề xuất lộ trình tiếp theo (Cụ thể em nên làm gì tiếp theo trong môn Vật lí).
                    Giọng điệu: Chuyên nghiệp, truyền cảm hứng, thấu hiểu tâm lý học sinh.
                    """
                    try:
                        response = model.generate_content(prompt_report)
                        st.session_state.ai_report_generated = response.text
                    except Exception as e:
                        st.error("Lỗi khi tạo báo cáo AI.")
            else:
                st.error("Tính năng AI chưa được kích hoạt.")
                
        # Hiển thị kết quả báo cáo
        if st.session_state.ai_report_generated:
            st.markdown("<div class='report-box'>", unsafe_allow_html=True)
            st.markdown(f"<h3 style='color: #15803D; text-align: center;'>BÁO CÁO NĂNG LỰC: {st.session_state.student_name.upper()}</h3>", unsafe_allow_html=True)
            st.markdown(st.session_state.ai_report_generated)
            st.markdown("</div>", unsafe_allow_html=True)

except Exception as e:
    st.error(f"Có lỗi hệ thống: {e}")
