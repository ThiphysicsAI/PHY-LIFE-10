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

# 1. CẤU HÌNH TRANG WEB & MÀU SẮC TÙY CHỈNH
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
</style>
''', unsafe_allow_html=True)

# 2. ĐỌC DỮ LIỆU TỪ EXCEL
@st.cache_data
def load_data():
    xls = pd.ExcelFile('du_lieu_tinh_huong_dong_hoc_vat_li_10.xlsx')
    sheet_names = xls.sheet_names
    
    df_main = pd.read_excel(xls, sheet_name=sheet_names[0])
    
    if 'Du_lieu_Game' in sheet_names:
        df_game = pd.read_excel(xls, sheet_name='Du_lieu_Game')
    else:
        df_game = pd.DataFrame()
        
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
    
    st.session_state.pretest_step = 1
    st.session_state.pretest_answers = {} 
    
    st.session_state.station = 1
    st.session_state.passcodes = []
    st.session_state.play_sound = False
    st.session_state.force_unlock_game = False

st.sidebar.markdown("<h2 style='color: #0D9488; font-weight: 700;'>🚀 PHY-LIFE 10</h2>", unsafe_allow_html=True)

if not st.session_state.pretest_done:
    menu_list = ["🏠 Cổng Khởi động"]
else:
    menu_list = ["📚 Khám phá Hiện tượng", "🎮 Bản đồ Thử thách (Game)", "🤖 Gia sư AI"]

selected_menu = st.sidebar.radio("CHUYÊN MỤC", menu_list, index=menu_list.index(st.session_state.nav_page) if st.session_state.nav_page in menu_list else 0)

if selected_menu != st.session_state.nav_page:
    st.session_state.nav_page = selected_menu
    st.rerun()

st.sidebar.markdown("---")

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
    # GIAO DIỆN 1: CỔNG KHỞI ĐỘNG (PRE-TEST)
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
                st.error("⚠️ Hệ thống chưa tìm thấy dữ liệu Khởi động trong file Excel (Sheet: Du_lieu_Khoi_dong).")
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
                        nhan_nut = "Nộp bài & Mở khóa 🔓" if st.session_state.pretest_step == tong_so_cau else "Tiếp tục ➡️"
                        if st.button(nhan_nut, use_container_width=True):
                            if tra_loi:
                                is_correct = tra_loi.startswith(dap_an_dung)
                                st.session_state.pretest_answers[st.session_state.pretest_step] = is_correct
                                
                                if st.session_state.pretest_step == tong_so_cau:
                                    score = sum(st.session_state.pretest_answers.values())
                                    ti_le_dung = score / tong_so_cau
                                    
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
                                    st.session_state.pretest_step += 1
                                    st.rerun()
                            else:
                                st.warning("⚠️ Em cần chọn đáp án để đi tiếp nhé!")
                    st.markdown("</div>", unsafe_allow_html=True)

    # ==========================================
    # GIAO DIỆN 2: THƯ VIỆN HIỆN TƯỢNG
    # ==========================================
    elif st.session_state.nav_page == "📚 Khám phá Hiện tượng":
        col_title, col_stat = st.columns([3, 1])
        with col_title:
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
            
        # LOGIC ĐẾM LƯỢT TRA CỨU
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
                            prompt_ai = f'''Bạn là Gia sư Vật lí 10. Trình độ học sinh: {st.session_state.student_level}. 
                            Tình huống: {ho_so['Tên tình huống']}. Câu hỏi: {ho_so['Câu hỏi gợi mở']}. Lời giải đúng: {ho_so['Giải thích khoa học']}. Học sinh trả lời: "{cau_tra_loi_hs}". 
                            Quy tắc:
                            - Nếu học sinh Cơ bản: Động viên nhiều hơn, gợi ý từ từ.
                            - Nếu học sinh Khá giỏi: Yêu cầu phân tích sâu hơn.
                            - Nếu sai: ĐỪNG ĐƯA ĐÁP ÁN, hãy đặt một câu hỏi gợi mở để học sinh tự nhận ra lỗi.
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
    # GIAO DIỆN 3: BẢN ĐỒ THỬ THÁCH (GAME ENGINE TỪ EXCEL)
    # ==========================================
    elif st.session_state.nav_page == "🎮 Bản đồ Thử thách (Game)":
        
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
            st.markdown("<div class='cyber-warning'>🚨 CẢNH BÁO: Tàu tốc hành đang mất phanh. Các đặc vụ PHY-LIFE cần giải mã các trạm điều khiển để kích hoạt hệ thống phanh khẩn cấp!</div>", unsafe_allow_html=True)
            
            if df_game.empty:
                st.error("⚠️ Hệ thống chưa tìm thấy dữ liệu Game trong file Excel (Sheet 'Du_lieu_Game'). Cô hãy thêm dữ liệu vào nhé!")
            else:
                tong_so_tram = len(df_game)
                
                # Cập nhật số lượng passcodes dựa trên số trạm trong Excel
                if len(st.session_state.passcodes) != tong_so_tram:
                    st.session_state.passcodes = ["_"] * tong_so_tram
                
                progress_val = int(((st.session_state.station - 1) / tong_so_tram) * 100)
                st.progress((st.session_state.station - 1) / tong_so_tram)
                
                passcodes_display = []
                for i in range(tong_so_tram):
                    if i < st.session_state.station - 1:
                        ma_khoa = str(df_game.iloc[i].get('Mã khóa', '')).strip()
                        passcodes_display.append(ma_khoa if ma_khoa and ma_khoa != 'nan' else '✔️')
                    else:
                        passcodes_display.append("_")
                
                st.markdown(f"""
                <div class='led-screen'>
                    <span style='color: #38bdf8 !important;'>MÃ KÍCH HOẠT:</span> <span class='led-code'>{' '.join(passcodes_display)}</span>
                </div>
                """, unsafe_allow_html=True)

                if st.session_state.play_sound:
                    sound_html = '<audio autoplay><source src="https://assets.mixkit.co/active_storage/sfx/2013/2013-preview.mp3" type="audio/mpeg"></audio>'
                    st.markdown(sound_html, unsafe_allow_html=True)
                    st.session_state.play_sound = False

                # HIỂN THỊ CÂU HỎI TRẠM TỪ EXCEL
                if st.session_state.station <= tong_so_tram:
                    tram_data = df_game.iloc[st.session_state.station - 1]
                    
                    st.markdown(f"""
                    <div class='mission-panel'>
                        <div class='mission-header'>📍 Trạm {tram_data['Trạm']}: {tram_data['Tên trạm']}</div>
                        <p><strong>Mục tiêu:</strong> {tram_data['Mục tiêu']}</p>
                        <p><strong>Nhiệm vụ:</strong> {tram_data['Nhiệm vụ']}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Hiện ảnh
                    if pd.notna(tram_data.get('Ảnh minh họa')) and str(tram_data['Ảnh minh họa']).strip() != "":
                        img_path = os.path.join("images", str(tram_data['Ảnh minh họa']).strip())
                        if os.path.exists(img_path):
                            img_col1, img_col2, img_col3 = st.columns([1, 2, 1])
                            with img_col2:
                                st.image(img_path, use_container_width=True)
                        else:
                            st.warning(f"✍️ Đang chờ tải ảnh minh họa: {tram_data['Ảnh minh họa']}")

                    loai_cau_hoi = str(tram_data['Loại thử thách']).strip()
                    dap_an_dung = str(tram_data['Đáp án đúng']).strip()
                    
                    # LOGIC KIỂM TRA ĐỘNG TỪ EXCEL
                    if loai_cau_hoi == "Trắc nghiệm":
                        lua_chon = [opt.strip() for opt in str(tram_data['Dữ liệu lựa chọn']).split("|")]
                        ans = st.radio("Chọn đáp án:", ["Chưa chọn"] + lua_chon, key=f"q_{st.session_state.station}")
                        
                        if st.button("🚀 Xác nhận", use_container_width=True):
                            if ans != "Chưa chọn" and ans.startswith(dap_an_dung):
                                st.success(f"✅ {tram_data['Phản hồi đúng']}")
                                st.session_state.play_sound = True
                                time.sleep(1.5)
                                st.session_state.station += 1
                                st.rerun()
                            else:
                                st.error(f"❌ {tram_data['Phản hồi sai']}")
                                
                    elif loai_cau_hoi == "Ghép nối":
                        pairs = str(tram_data['Dữ liệu lựa chọn']).split("|")
                        vethrai = [p.split("=")[0].strip() for p in pairs if "=" in p]
                        vephai = [p.split("=")[1].strip() for p in pairs if "=" in p]
                        options = ["Chưa ghép"] + sorted(list(set(vephai)))
                        
                        user_answers = {}
                        col1, col2 = st.columns(2)
                        for idx, trai in enumerate(vethrai):
                            with col1 if idx % 2 == 0 else col2:
                                user_answers[trai] = st.selectbox(trai, options, key=f"match_{st.session_state.station}_{idx}")
                        
                        if not st.session_state.tram2_matched:
                            if st.button("🔍 Kiểm tra ghép nối", use_container_width=True):
                                correct = all(user_answers[trai] == phai for trai, phai in zip(vethrai, vephai))
                                if correct:
                                    st.session_state.tram2_matched = True
                                    st.rerun()
                                else:
                                    st.error("❌ Ghép thẻ thất bại. Hệ thống báo lỗi đồng bộ!")
                        
                        if st.session_state.tram2_matched:
                            st.success(f"✅ Ghép nối thành công! {tram_data['Phản hồi đúng']}")
                            ans2 = st.text_input("Nhập mã thu được sau khi ghép:", key=f"ans_match_{st.session_state.station}")
                            if st.button("🚀 Xác nhận mã", use_container_width=True):
                                if ans2.strip().lower() == dap_an_dung.lower():
                                    st.success("✅ Hệ thống ghi nhận mã thành công!")
                                    st.session_state.play_sound = True
                                    time.sleep(1.5)
                                    st.session_state.station += 1
                                    st.session_state.tram2_matched = False
                                    st.rerun()
                                else:
                                    st.error(f"❌ {tram_data['Phản hồi sai']}")
                                    
                    elif loai_cau_hoi == "Đúng/Sai":
                        statements = [opt.strip() for opt in str(tram_data['Dữ liệu lựa chọn']).split("|")]
                        correct_answers = [ans.strip() for ans in dap_an_dung.split("|")]
                        
                        user_answers = []
                        for idx, stmt in enumerate(statements):
                            ans = st.radio(f"{idx+1}. {stmt}", ["Chưa chọn", "Đúng", "Sai"], horizontal=True, key=f"tf_{st.session_state.station}_{idx}")
                            user_answers.append(ans)
                            
                        if st.button("🚀 Tổng hợp mã Nhị phân", use_container_width=True):
                            if "Chưa chọn" in user_answers:
                                st.warning("⚠️ Đặc vụ cần đánh giá toàn bộ nhận định!")
                            elif user_answers == correct_answers:
                                st.success(f"✅ {tram_data['Phản hồi đúng']}")
                                st.session_state.play_sound = True
                                time.sleep(2)
                                st.session_state.station += 1
                                st.rerun()
                            else:
                                st.error(f"❌ {tram_data['Phản hồi sai']}")
                                
                    elif loai_cau_hoi == "Điền khuyết": 
                        ans = st.text_input("Nhập kết quả/mã thu được:", key=f"q_{st.session_state.station}")
                        
                        if st.button("🚀 Xác nhận mã", use_container_width=True):
                            if ans.strip().lower() == dap_an_dung.lower():
                                st.success(f"✅ {tram_data['Phản hồi đúng']}")
                                st.session_state.play_sound = True
                                time.sleep(1.5)
                                st.session_state.station += 1
                                st.rerun()
                            else:
                                st.error(f"❌ {tram_data['Phản hồi sai']}")

                # KHI QUA HẾT CÁC TRẠM
                else:
                    st.markdown("<div class='game-station' style='background: linear-gradient(135deg, #b91c1c 0%, #7f1d1d 100%); border: 3px solid #fca5a5;'><h3 style='color: white !important;'>🛑 HỆ THỐNG PHANH KHẨN CẤP</h3></div>", unsafe_allow_html=True)
                    st.warning("⚠️ YÊU CẦU NHẬP LẠI TOÀN BỘ MÃ KÍCH HOẠT ĐÃ THU THẬP ĐỂ DỪNG TÀU!")
                    
                    correct_final_code = "".join([str(df_game.iloc[i].get('Mã khóa', '')).strip() for i in range(tong_so_tram) if str(df_game.iloc[i].get('Mã khóa', '')).strip() and str(df_game.iloc[i].get('Mã khóa', '')).strip() != 'nan'])
                    
                    final_code = st.text_input("Nhập mật mã:", type="password", placeholder="Nhập các chữ số viết liền...")
                    
                    if st.button("🔴 KÍCH HOẠT PHANH", use_container_width=True):
                        if final_code == correct_final_code:
                            st.balloons()
                            st.markdown("<div style='background-color: rgba(34, 197, 94, 0.2); padding: 40px; border-radius: 15px; text-align: center; border: 2px solid #4ade80; box-shadow: 0 0 30px rgba(74, 222, 128, 0.5);'><h1 style='color: #4ade80 !important; font-size: 3.5rem; margin-bottom: 10px; text-shadow: 0 0 10px #4ade80;'>🎉 KÍCH HOẠT THÀNH CÔNG!</h1><h2 style='color: #86efac !important;'>CỨU HỘ HOÀN TẤT. KIỆN HÀNG TRI THỨC ĐÃ ĐƯỢC BẢO VỆ.</h2><p style='font-size: 1.2rem; color: #f8fafc !important; margin-top: 20px;'>Các đặc vụ PHY-LIFE đã xuất sắc hoàn thành nhiệm vụ!</p></div>", unsafe_allow_html=True)
                            st.session_state.play_sound = True
                            
                            st.markdown("<br>", unsafe_allow_html=True)
                            if st.button("🔄 Chơi lại Điệp vụ", use_container_width=True):
                                st.session_state.station = 1
                                st.session_state.passcodes = []
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
