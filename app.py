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
    df_pretest = pd.read_excel(xls, sheet_name='Du_lieu_Khoi_dong') if 'Du_lieu_Khoi_dong' in sheet_names else pd.DataFrame()
    return df_main, df_pretest

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
    st.session_state.passcodes = ["_", "_", "_", "_"]
    st.session_state.tram2_matched = False
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
    df_main, df_pretest = load_data()
    
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
            st.info(f"Chào **{st.session_state.student_name}**! Để hệ thống thiết kế lộ trình học tốt nhất, em hãy xem các video ngắn và trả lời câu hỏi tương tác nhé. (Yêu cầu: Đúng 100% để mở khóa toàn bộ Hệ thống)")
            
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

    # ==========================================
    # GIAO DIỆN MỚI: BẢN ĐỒ KẾT NỐI (MẠNG LƯỚI TƯ DUY)
    # ==========================================
    elif st.session_state.nav_page == "🕸️ Bản đồ Kết nối":
        st.markdown("<h2 style='color: #0D9488;'>🕸️ Bản đồ Kết nối Tư duy Động học</h2>", unsafe_allow_html=True)
        st.markdown("Hệ thống sơ đồ chuỗi trực quan giúp em liên kết từ **Khái niệm Vật lí** sang **Hiện tượng thực tiễn** và ngược lại. Nhấp vào các nút bên dưới để khám phá chi tiết.")
        st.markdown("---")

        chuoi_tu_duy = st.selectbox("Chọn chuỗi hiện tượng cần phân tích:", [
            "1. Gia tốc → Xe tăng tốc tại ngã tư → Vận tốc theo thời gian → Đồ thị → Bài toán định lượng",
            "2. Quãng đường & Độ dịch chuyển → Chạy bộ 5km vòng quanh hồ → So sánh s và Δx",
            "3. Rơi tự do → Thả rơi chùm chìa khóa → Đo thời gian → Tính độ cao",
            "4. Chuyển động ném ngang → Trực thăng thả hàng cứu trợ → Quỹ đạo Parabol → Tầm xa"
        ])

        st.markdown("<br>", unsafe_allow_html=True)

        col1, col2, col3, col4, col5 = st.columns(5)
        
        if "1. Gia tốc" in chuoi_tu_duy:
            nodes = [
                ("Khái niệm: Gia tốc (a)", "Đại lượng đặc trưng cho sự thay đổi nhanh chậm của vận tốc theo thời gian."),
                ("Hiện tượng: Xe tăng tốc", "Xe máy hoặc ô tô vọt đi ngay khi đèn giao thông chuyển sang màu xanh."),
                ("Đại lượng đo đạc", "Đo độ biến thiên vận tốc Δv trong khoảng thời gian Δt."),
                ("Mô hình & Đồ thị", "Sử dụng đồ thị vận tốc - thời gian (v-t) hoặc phương trình chuyển động thẳng biến đổi đều."),
                ("Bài toán vận dụng", "Tính quãng đường phanh, thời gian đạt vận tốc tối đa và ứng dụng an toàn giao thông.")
            ]
        elif "2. Quãng đường" in chuoi_tu_duy:
            nodes = [
                ("Khái niệm: s và Δx", "Phân biệt tổng chiều dài quỹ đạo (s) và vectơ nối đầu-cuối (Δx)."),
                ("Hiện tượng: Chạy bộ 5km", "Học sinh chạy trọn vẹn một vòng quanh hồ hoặc sân vận động về vạch xuất phát."),
                ("Đại lượng đo đạc", "Sử dụng thiết bị định vị GPS (Garmin, Strava) ghi nhận lộ trình."),
                ("Mô hình & Đồ thị", "Hệ tọa độ không gian, xác định vị trí ban đầu x1 và vị trí cuối x2."),
                ("Bài toán vận dụng", "Giải thích vì sao tốn sức chạy 5km nhưng độ dịch chuyển tổng cộng lại bằng 0.")
            ]
        elif "3. Rơi tự do" in chuoi_tu_duy:
            nodes = [
                ("Khái niệm: Rơi tự do", "Chuyển động chỉ dưới tác dụng của trọng lực, v0 = 0, gia tốc g."),
                ("Hiện tượng: Rơi chìa khóa", "Sự cố lỡ tay làm rơi chùm chìa khóa từ hành lang tầng cao xuống mặt đất."),
                ("Đại lượng đo đạc", "Sử dụng đồng hồ bấm giờ (stopwatch) đo thời gian rơi t từ lúc buông."),
                ("Mô hình & Đồ thị", "Phương trình rơi tự do: h = 1/2 * g * t^2, bỏ qua lực cản không khí."),
                ("Bài toán vận dụng", "Tính ngược lại độ cao của tầng nhà hoặc độ sâu của giếng nước.")
            ]
        else:
            nodes = [
                ("Khái niệm: Ném ngang", "Tổng hợp độc lập chuyển động thẳng đều ngang và rơi tự do đứng."),
                ("Hiện tượng: Thả hàng cứu trợ", "Trực thăng bay ngang thả thùng hàng xuống vùng ngập lụt miền Trung."),
                ("Đại lượng đo đạc", "Độ cao bay h, vận tốc ngang của máy bay v0 và tầm xa L."),
                ("Mô hình & Đồ thị", "Quỹ đạo hình parabol y = (g / 2v0^2) * x^2."),
                ("Bài toán vận dụng", "Xác định thời điểm cắt dây thả hàng chính xác để trúng mục tiêu.")
            ]

        with col1:
            st.markdown(f"<div class='node-box'><b>Bước 1</b><br>{nodes[0][0]}</div>", unsafe_allow_html=True)
            with st.expander("Xem chi tiết"):
                st.write(nodes[0][1])
        with col2:
            st.markdown("<div class='arrow-box'>➔</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='node-box'><b>Bước 2</b><br>{nodes[1][0]}</div>", unsafe_allow_html=True)
            with st.expander("Xem chi tiết"):
                st.write(nodes[1][1])
        with col3:
            st.markdown("<div class='arrow-box'>➔</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='node-box'><b>Bước 3</b><br>{nodes[2][0]}</div>", unsafe_allow_html=True)
            with st.expander("Xem chi tiết"):
                st.write(nodes[2][1])
        with col4:
            st.markdown("<div class='arrow-box'>➔</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='node-box'><b>Bước 4</b><br>{nodes[3][0]}</div>", unsafe_allow_html=True)
            with st.expander("Xem chi tiết"):
                st.write(nodes[3][1])
        with col5:
            st.markdown("<div class='arrow-box'>➔</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='node-box'><b>Bước 5</b><br>{nodes[4][0]}</div>", unsafe_allow_html=True)
            with st.expander("Xem chi tiết"):
                st.write(nodes[4][1])

    # ==========================================
    # GIAO DIỆN 4: BẢN ĐỒ THỬ THÁCH (GAME HARDCODE)
    # ==========================================
    elif st.session_state.nav_page == "🎮 Bản đồ Thử thách (Game)":
        
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
            else:
                st.warning("⚠️ Đang chờ tải ảnh đồ thị... (Cần có file 'do_thi_tram2.jpg' trong thư mục images)")
            st.markdown("<br>", unsafe_allow_html=True)
            
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
            q4 = st.radio("4. Ngay trước khi chạm đất, vận tốc ngang của thùng hàng vẫn bằng vận tốc máy bay lúc thả.", ["Chưa chọn", "Đúng (1)", "Sai (0)"], horizontal=True)

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

    # === GIAO DIỆN 5: CHATBOT AI 5 CHỨC NĂNG ===
    elif st.session_state.nav_page == "🤖 Hỏi Nhà khám phá AI":
        st.markdown("<h2 style='color: #0D9488;'>🤖 Nhà khám phá AI</h2>", unsafe_allow_html=True)
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
