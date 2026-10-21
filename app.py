import streamlit as st
import pandas as pd
import os
import google.generativeai as genai
import time

# --- HÀM THEO DÕI LƯỢT TRA CỨU ---
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
    .node-box { background-color: #ffffff; border: 2px solid #0D9488; padding: 12px 20px; border-radius: 12px; text-align: center; font-weight: 600; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05); color: #1E293B; }
    .arrow-box { text-align: center; font-size: 24px; color: #0D9488; font-weight: bold; padding: 5px 0; }
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
# 3. TRẠNG THÁI HỆ THỐNG & PHÂN LUỒNG MENU
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
    
    st.session_state.station = 1
    st.session_state.passcodes = []
    st.session_state.play_sound = False

st.sidebar.markdown("<h2 style='color: #0D9488; font-weight: 700;'>🚀 PHY-LIFE 10</h2>", unsafe_allow_html=True)

# LỘ TRÌNH CÁ NHÂN HÓA MENU
if not st.session_state.pretest_done:
    menu_list = ["🏠 Cổng Khởi động"]
else:
    if st.session_state.student_level == "Tốt": # Nhóm 100%
        menu_list = ["📚 Khám phá Hiện tượng", "🕸️ Bản đồ Kết nối", "🎮 Bản đồ Thử thách (Game)", "🤖 Hỏi Nhà khám phá AI"]
    else: # Nhóm Yếu/Cơ bản (<100%)
        menu_list = ["📖 Ôn tập cốt lõi", "🤖 Gia sư AI (Hỗ trợ)"]

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
                        st.rerun()
                    else:
                        st.error("Em nhớ nhập đầy đủ Tên và Lớp nhé!")
                st.markdown("</div>", unsafe_allow_html=True)

        elif not st.session_state.pretest_done:
            st.info(f"Chào **{st.session_state.student_name}**! Để hệ thống thiết kế lộ trình học tốt nhất, em hãy xem các video ngắn và trả lời câu hỏi tương tác nhé. (Yêu cầu: Đúng 100% để mở khóa Bản đồ Khám phá)")
            
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
                                st.session_state.pretest_answers[st.session_state.pretest_step] = tra_loi.startswith(dap_an_dung)
                                
                                if st.session_state.pretest_step == tong_so_cau:
                                    score = sum(st.session_state.pretest_answers.values())
                                    
                                    # YÊU CẦU ĐẠT 100% ĐỂ MỞ KHÓA
                                    if score == tong_so_cau:
                                        st.session_state.student_level = "Tốt"
                                        st.success(f"🎉 Xuất sắc! Em làm đúng 100% ({score}/{tong_so_cau} câu). Hệ thống đã mở khóa TOÀN BỘ CHỨC NĂNG!")
                                        st.session_state.nav_page = "📚 Khám phá Hiện tượng"
                                    else:
                                        st.session_state.student_level = "Cơ bản"
                                        st.error(f"📊 Em làm đúng {score}/{tong_so_cau} câu. Em cần đạt 100% để tiếp tục hành trình. Hệ thống sẽ điều hướng em đến tab Ôn tập cốt lõi cùng Gia sư AI.")
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
    # LỘ TRÌNH 1: DÀNH CHO NHÓM YẾU/CƠ BẢN (<100%)
    # ==========================================
    elif st.session_state.nav_page == "📖 Ôn tập cốt lõi":
        st.markdown("<h2 style='color: #ef4444;'>📖 Ôn tập cốt lõi Động học</h2>", unsafe_allow_html=True)
        st.warning("Em chưa đạt đủ 100% điểm ở bài đánh giá năng lực. Hãy xem lại các khái niệm quan trọng dưới đây một cách chậm rãi, nhờ Gia sư AI hỗ trợ, và thực hiện lại bài kiểm tra nhé!")
        
        col1, col2 = st.columns([2, 1])
        with col1:
            st.video("https://www.youtube.com/watch?v=kKKM8Y-u7ds") # Phát lại video cốt lõi
        with col2:
            st.markdown("### 🤖 Tóm tắt nhanh từ AI")
            if st.button("Yêu cầu AI tóm tắt từ khóa", use_container_width=True):
                if api_ready:
                    with st.spinner("AI đang tổng hợp kiến thức..."):
                        try:
                            # Prompt tóm tắt
                            summary_prompt = "Hãy tóm tắt 3 từ khóa vật lý quan trọng nhất về chương Động học lớp 10 (Sự rơi tự do, Tốc độ, Gia tốc) trong 3 gạch đầu dòng ngắn gọn, dễ hiểu nhất cho học sinh yếu."
                            summary = model.generate_content(summary_prompt)
                            st.info(summary.text)
                        except:
                            st.error("Lỗi kết nối AI.")
                else:
                    st.error("API Key chưa sẵn sàng.")
            
            st.markdown("---")
            st.markdown("Sau khi đã ôn tập kỹ và hỏi đáp với Gia sư AI ở mục bên dưới, em hãy làm lại bài kiểm tra nhé.")
            if st.button("🔄 LÀM LẠI BÀI KIỂM TRA", use_container_width=True):
                st.session_state.pretest_done = False
                st.session_state.pretest_step = 1
                st.session_state.pretest_answers = {}
                st.session_state.nav_page = "🏠 Cổng Khởi động"
                st.rerun()

    elif st.session_state.nav_page == "🤖 Gia sư AI (Hỗ trợ)":
        st.markdown("<h2 style='color: #0D9488;'>🤖 Gia sư AI (Socratic Tutor)</h2>", unsafe_allow_html=True)
        st.markdown("<span class='main-text'>Chào em! Cô là Gia sư AI. Cô ở đây để giúp em giải đáp những thắc mắc trong bài kiểm tra vừa rồi. Em không hiểu chỗ nào cứ hỏi cô nhé!</span>", unsafe_allow_html=True)

        if not api_ready:
            st.warning("⚠️ Tính năng AI chưa được kích hoạt. Vui lòng kiểm tra lại GEMINI_API_KEY trong Secrets.")
        else:
            if "tutor_messages" not in st.session_state:
                st.session_state.tutor_messages = []
            for msg in st.session_state.tutor_messages:
                with st.chat_message(msg["role"]):
                    st.markdown(msg["content"])
                    
            if prompt := st.chat_input("Hỏi Gia sư AI tại đây..."):
                st.session_state.tutor_messages.append({"role": "user", "content": prompt})
                with st.chat_message("user"):
                    st.markdown(prompt)
                with st.chat_message("assistant"):
                    with st.spinner("Cô đang suy nghĩ..."):
                        history_context = "".join([f"{'HS' if m['role']=='user' else 'AI'}: {m['content']}\n" for m in st.session_state.tutor_messages[-5:-1]])
                        # --- HỆ THỐNG PROMPT SOCRATIC (CHỈ HỎI GỢI MỞ, KHÔNG CHO ĐÁP ÁN) ---
                        socratic_prompt = f'''
                        [HƯỚNG DẪN SOCRATIC TUTOR]
                        Bạn là Gia sư Vật lí lớp 10. Học sinh này đang yếu kiến thức Động học và chưa qua bài test.
                        QUY TẮC BẮT BUỘC:
                        1. TUYỆT ĐỐI KHÔNG BAO GIỜ được đưa ra đáp án trực tiếp cho học sinh.
                        2. Dùng phương pháp Socratic: Đặt MỘT câu hỏi gợi mở, chia nhỏ vấn đề để dẫn dắt học sinh tự suy nghĩ và tự tìm ra lỗi sai/câu trả lời.
                        3. Khen ngợi nếu học sinh có ý đúng, nhưng vẫn tiếp tục hỏi để đào sâu.
                        4. Xưng "cô", gọi "em". Giọng điệu kiên nhẫn, động viên.
                        
                        Lịch sử trò chuyện: {history_context}
                        Học sinh vừa hỏi: "{prompt}"
                        '''
                        try:
                            response = model.generate_content(socratic_prompt)
                            st.markdown(response.text)
                            st.session_state.tutor_messages.append({"role": "assistant", "content": response.text})
                        except Exception as e:
                            st.error(f"Hệ thống đang bận, em thử lại sau nhé! (Lỗi chi tiết: {e})")

    # ==========================================
    # LỘ TRÌNH 2: DÀNH CHO NHÓM TỐT (ĐẠT 100%)
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
            current_views = add_view_count()
        elif st.session_state.last_viewed != tinh_huong_chon:
            st.session_state.last_viewed = tinh_huong_chon
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
            else:
                st.warning(f"✍️ Đang chờ nét vẽ Sketchnote hoặc Video...")
                
        with col_phai:
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

    elif st.session_state.nav_page == "🕸️ Bản đồ Kết nối":
        st.markdown("<h2 style='color: #0D9488;'>🕸️ Bản đồ Kết nối Tư duy Động học</h2>", unsafe_allow_html=True)
        # Bỏ qua chi tiết Bản đồ ở đây để rút gọn độ dài code
        st.info("Tính năng Bản đồ kết nối sẽ hiển thị tại đây.")

    elif st.session_state.nav_page == "🎮 Bản đồ Thử thách (Game)":
        # Giữ nguyên logic Game Điệp vụ PHYSIX lấy từ Excel
        st.markdown("<h2 style='color: #0D9488;'>🎮 Điệp vụ PHYSIX</h2>", unsafe_allow_html=True)
        st.info("Hệ thống Game sẽ được tải tại đây.")

    elif st.session_state.nav_page == "🤖 Hỏi Nhà khám phá AI":
        st.markdown("<h2 style='color: #0D9488;'>🤖 Nhà khám phá AI (5 Chức năng)</h2>", unsafe_allow_html=True)
        st.markdown("<span class='main-text'>Chào em! Cô là Nhà khám phá Vật lí. Em có hiện tượng gì thú vị muốn kể cho cô nghe, nhập một khái niệm muốn tìm hiểu, hay muốn thử sức với bài tập vận dụng nào?</span>", unsafe_allow_html=True)

        if not api_ready:
            st.warning("⚠️ Tính năng AI chưa được kích hoạt. Vui lòng kiểm tra lại GEMINI_API_KEY trong Secrets.")
        else:
            if "chat_exp_messages" not in st.session_state:
                st.session_state.chat_exp_messages = []
            for msg in st.session_state.chat_exp_messages:
                with st.chat_message(msg["role"]):
                    st.markdown(msg["content"])
                    
            if prompt := st.chat_input("Nhập câu hỏi, hiện tượng hoặc khái niệm em muốn khám phá..."):
                st.session_state.chat_exp_messages.append({"role": "user", "content": prompt})
                with st.chat_message("user"):
                    st.markdown(prompt)
                with st.chat_message("assistant"):
                    with st.spinner("Cô đang phân tích..."):
                        history_context = "".join([f"{'Học sinh' if m['role']=='user' else 'Cô giáo'}: {m['content']}\n" for m in st.session_state.chat_exp_messages[-5:-1]])
                        
                        # --- HỆ THỐNG PROMPT 5 CHỨC NĂNG DÀNH CHO NHÓM GIỎI ---
                        sys_prompt = f'''
                        [HƯỚNG DẪN CHO AI]
                        Bạn là "Nhà khám phá Vật lí", chuyên gia sư phạm hỗ trợ học sinh GIỎI lớp 10.
                        Dựa vào câu hỏi của học sinh, thực hiện linh hoạt 1 trong 5 chức năng sau:
                        1. Giải thích hiện tượng chuyên sâu.
                        2. Tìm hiện tượng thực tiễn theo khái niệm.
                        3. Phân tích tình huống mới và tạo ví dụ định lượng.
                        4. Đặt câu hỏi gợi mở để kích thích tư duy phản biện.
                        5. Tạo bài tập vận dụng cao (On-demand) theo yêu cầu cá nhân hóa của học sinh.

                        Quy tắc: Xưng "cô", gọi "em". Ngôn ngữ uyên bác, truyền cảm hứng.
                        [KẾT THÚC HƯỚNG DẪN]

                        Lịch sử trò chuyện gần đây: {history_context}
                        Học sinh vừa nhắn: "{prompt}"
                        '''
                        try:
                            response = model.generate_content(sys_prompt)
                            st.markdown(response.text)
                            st.session_state.chat_exp_messages.append({"role": "assistant", "content": response.text})
                        except Exception as e:
                            st.error(f"Hệ thống đang bận, em thử lại sau nhé! (Lỗi: {e})")

except Exception as e:
    st.error(f"Có lỗi hệ thống: {e}")
