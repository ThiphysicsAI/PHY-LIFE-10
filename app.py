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
    /* Màu chữ chính cho trang sáng */
    .main-text { color: #1E293B; }
    [data-testid="stSidebar"] { background-color: #ffffff; border-right: 1px solid #e2e8f0; }
    .stAlert { border-radius: 1rem !important; border: none !important; }
    .phy-card { background-color: white; padding: 2rem 1.5rem; border-radius: 1rem; border: 1px solid #e2e8f0; box-shadow: 0 1px 3px rgba(0,0,0,0.1); transition: transform 0.3s, box-shadow 0.3s, border-color 0.3s; height: 100%; text-align: center; display: flex; flex-direction: column; align-items: center; justify-content: center; margin-bottom: 10px; }
    .phy-card:hover { transform: translateY(-5px); box-shadow: 0 10px 15px -3px rgba(0,0,0,0.1); border-color: #0D9488; background-color: #F0FDFA; }
    .icon-box { width: 60px; height: 60px; border-radius: 16px; display: flex; align-items: center; justify-content: center; font-size: 28px; margin-bottom: 15px; }
</style>
''', unsafe_allow_html=True)

# 2. ĐỌC DỮ LIỆU TỪ EXCEL (Đọc cả thư viện và game)
@st.cache_data
def load_data():
    xls = pd.ExcelFile('du_lieu_tinh_huong_dong_hoc_vat_li_10.xlsx')
    sheet_names = xls.sheet_names
    df_main = pd.read_excel(xls, sheet_name=sheet_names[0])
    if 'Du_lieu_Game' in sheet_names:
        df_game = pd.read_excel(xls, sheet_name='Du_lieu_Game')
    else:
        df_game = pd.DataFrame()
    return df_main, df_game

# 3. ĐIỀU HƯỚNG TRANG THÔNG MINH
if "nav_page" not in st.session_state:
    st.session_state.nav_page = "🏠 Trang chủ"

st.sidebar.markdown("<h2 style='color: #0D9488; font-weight: 700;'>🚀 PHY-LIFE 10</h2>", unsafe_allow_html=True)
menu_list = ["🏠 Trang chủ", "📚 Khám phá Hiện tượng", "🎮 Bản đồ Thử thách (Game)", "🤖 Hỏi Nhà khám phá AI"]
selected_menu = st.sidebar.radio("CHUYÊN MỤC", menu_list, index=menu_list.index(st.session_state.nav_page) if st.session_state.nav_page in menu_list else 0)

if selected_menu != st.session_state.nav_page:
    st.session_state.nav_page = selected_menu
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.markdown("*Ứng dụng hỗ trợ học sinh lớp 10 học bộ sách Kết nối tri thức.*")

if not api_ready:
    st.sidebar.warning("Vui lòng cấu hình GEMINI_API_KEY trong Settings > Secrets trên Streamlit Cloud.")

try:
    df_main, df_game = load_data()
    
    # === GIAO DIỆN 1: TRANG CHỦ ===
    if st.session_state.nav_page == "🏠 Trang chủ":
        col_text, col_img = st.columns([1.2, 1])
        with col_text:
            st.markdown("<br>", unsafe_allow_html=True) 
            st.markdown('''
            <div style="display: inline-block; padding: 4px 16px; background-color: #FEF08A; border-radius: 999px; font-weight: 700; font-size: 0.9rem; margin-bottom: 1rem; color: #1E293B;">
                ✨ Chương trình Lớp 10 Mới
            </div>
            <h1 style="font-size: 3.5rem; font-weight: 800; line-height: 1.2; margin-bottom: 1rem; color: #1E293B;">Vật lí quanh ta!</h1>
            <p style="font-size: 1.2rem; color: #475569; margin-bottom: 2rem;">
                Khám phá chuyển động trong đời sống. Quan sát hiện tượng, kết nối kiến thức và tự mình tìm ra lời giải.
            </p>
            ''', unsafe_allow_html=True)
            st.info("👈 **Hãy chọn các mục ở Menu bên trái hoặc bấm trực tiếp vào các thẻ bên dưới để bắt đầu!**")

        with col_img:
            st.markdown('''
            <div style="border: 2px dashed #1E293B; border-radius: 1rem; padding: 2rem; background-color: white; position: relative; margin-top: 2rem; text-align: center; box-shadow: 8px 8px 0px #FEF08A;">
                <h3 style="font-family: 'Caveat', cursive; color: #0D9488;">v = s / t</h3>
                <p style="color: #64748b;"><i>(Khu vực hiển thị ảnh minh họa)</i></p>
                <div style="font-size: 4rem;">🚴‍♂️ 💨</div>
            </div>
            ''', unsafe_allow_html=True)

        st.markdown("<br><br><br>", unsafe_allow_html=True)
        st.markdown("<h2 style='text-align: center; margin-bottom: 2rem; color: #1E293B;'>Em muốn khám phá gì?</h2>", unsafe_allow_html=True)
        
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.markdown('''<div class="phy-card"><div class="icon-box" style="background-color: #EFF6FF; color: #3B82F6;">📖</div><h3 style="font-size: 1.1rem; margin-bottom: 8px; color: #1E293B;">Theo bài học</h3><p style="color: #64748b; font-size: 0.85rem; margin-bottom: 0;">Ôn tập vận tốc, gia tốc.</p></div>''', unsafe_allow_html=True)
            if st.button("👉 Khám phá", use_container_width=True, key="card_btn_1"):
                st.session_state.nav_page = "📚 Khám phá Hiện tượng"
                st.rerun()
                
        with c2:
            st.markdown('''<div class="phy-card"><div class="icon-box" style="background-color: #FEF08A; color: #A16207;">💡</div><h3 style="font-size: 1.1rem; margin-bottom: 8px; color: #1E293B;">Theo hiện tượng</h3><p style="color: #64748b; font-size: 0.85rem; margin-bottom: 0;">Tình huống thực tiễn.</p></div>''', unsafe_allow_html=True)
            if st.button("👉 Khám phá", use_container_width=True, key="card_btn_2"):
                st.session_state.nav_page = "📚 Khám phá Hiện tượng"
                st.rerun()
                
        with c3:
            st.markdown('''<div class="phy-card"><div class="icon-box" style="background-color: #E0F2FE; color: #0284C7;">🎮</div><h3 style="font-size: 1.1rem; margin-bottom: 8px; color: #1E293B;">Bản đồ Thử thách</h3><p style="color: #64748b; font-size: 0.85rem; margin-bottom: 0;">Điệp vụ PHYSIX.</p></div>''', unsafe_allow_html=True)
            if st.button("👉 Vào chơi Game", use_container_width=True, key="card_btn_game"):
                st.session_state.nav_page = "🎮 Bản đồ Thử thách (Game)"
                st.rerun()

        with c4:
            st.markdown('''<div class="phy-card"><div class="icon-box" style="background-color: #CCFBF1; color: #0D9488;">🤖</div><h3 style="font-size: 1.1rem; margin-bottom: 8px; color: #1E293B;">Hỏi AI Khám phá</h3><p style="color: #64748b; font-size: 0.85rem; margin-bottom: 0;">Trợ lý ảo thông minh.</p></div>''', unsafe_allow_html=True)
            if st.button("👉 Hỏi AI", use_container_width=True, key="card_btn_3"):
                st.session_state.nav_page = "🤖 Hỏi Nhà khám phá AI"
                st.rerun()

    # === GIAO DIỆN 2: THƯ VIỆN HIỆN TƯỢNG ===
    elif st.session_state.nav_page == "📚 Khám phá Hiện tượng":
        st.markdown("<h2 style='color: #0D9488;'>Thư viện Hiện tượng thực tiễn</h2>", unsafe_allow_html=True)
        col_loc1, col_loc2 = st.columns(2)
        with col_loc1:
            danh_sach_bai = df_main['Bài học liên quan'].unique()
            bai_hoc_chon = st.selectbox("📌 Chiều 1: Từ Sách giáo khoa (Bài học) đến Hiện tượng:", danh_sach_bai)
        
        df_loc = df_main[df_main['Bài học liên quan'] == bai_hoc_chon]
        with col_loc2:
            tinh_huong_chon = st.selectbox("🔍 Chiều 2: Chọn tình huống thực tiễn để xem kiến thức:", df_loc['Tên tình huống'])
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
            
            ten_file_anh = str(ho_so['Tên file ảnh'])
            duong_dan_anh = os.path.join("images", ten_file_anh)
            if os.path.exists(duong_dan_anh):
                st.image(duong_dan_anh, use_container_width=True)
            else:
                st.warning(f"✍️ Đang chờ nét vẽ Sketchnote... (Tên file cần có: {ten_file_anh})")
                
            st.markdown(f"<span style='color: #1E293B;'>**❓ Câu hỏi gợi mở:** *{ho_so['Câu hỏi gợi mở']}*</span>", unsafe_allow_html=True)
            
            st.markdown(f'''
            <div style="background-color: #F0FDF4; padding: 15px; border-radius: 10px; border-left: 5px solid #22C55E; margin-top: 20px; margin-bottom: 10px;">
                <h4 style="color: #15803D; margin-top: 0; display: flex; align-items: center; gap: 8px;">🤖 AI phân tích nhanh</h4>
                <p style="font-size: 0.95em; color: #1E293B; margin-bottom: 5px;"><strong>Dựa vào câu hỏi:</strong> <em>"{ho_so['Câu hỏi gợi mở']}"</em></p>
                <p style="font-size: 0.85em; color: #64748b;">Hãy nhập hoặc đọc câu trả lời để mở khóa bài học nhé!</p>
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
                            prompt_ai = f'''Bạn là cô giáo dạy Vật lí lớp 10, rất tâm lý và khích lệ học sinh. Tình huống: {ho_so['Tên tình huống']}. Câu hỏi đặt ra: {ho_so['Câu hỏi gợi mở']}. Lời giải đúng: {ho_so['Giải thích khoa học']}. Học sinh vừa trả lời: "{cau_tra_loi_hs}". Hãy viết 1 đoạn nhận xét ngắn gọn (khoảng 2-3 câu): Nếu học sinh nói không biết, từ bỏ, hoặc đùa giỡn: Nhẹ nhàng nhắc nhở, động viên. Nếu trả lời sai: Chỉnh sửa nhẹ nhàng. Nếu trả lời có ý đúng: Khen ngợi. Quy tắc BẮT BUỘC: 1. Xưng là "cô", gọi học sinh là "em". 2. Bất kể học sinh trả lời đúng hay sai, CÂU CHỐT CUỐI CÙNG LUÔN LÀ: "Em hãy xem phần 'Giải thích khoa học' bên cạnh để hiểu rõ hơn nhé!"'''
                            try:
                                response = model.generate_content(prompt_ai)
                                st.session_state.ai_response = f"**🤖 AI phân tích:** {response.text}"
                            except Exception as e:
                                st.session_state.ai_response = f"❌ AI đang bận, thử lại sau nhé! (Lỗi: {e})"
                    else:
                        st.session_state.ai_response = "⚠️ Tính năng AI chưa được kích hoạt (Thiếu API Key)."
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
                    st.markdown("<h4 style='color: #0D9488;'>🛠️ Hoạt động thực hành</h4>", unsafe_allow_html=True)
                    st.info(ho_so['Hoạt động thực hành'])
                    st.markdown("<h4 style='color: #0D9488;'>🏷️ Từ khóa</h4>", unsafe_allow_html=True)
                    
                    tu_khoa_list = str(ho_so['Từ khóa']).split(',')
                    html_tu_khoa = "".join([f"<span style='background-color: #E2E8F0; padding: 4px 8px; border-radius: 4px; margin-right: 5px; font-size: 0.85em; color: #1E293B;'>{tag.strip()}</span>" for tag in tu_khoa_list])
                    st.markdown(html_tu_khoa, unsafe_allow_html=True)
                    st.markdown("<br><p style='font-size: 0.8em; color: #94A3B8;'><strong>Nguồn tham khảo:</strong> " + str(ho_so['Nguồn tham khảo']) + "</p>", unsafe_allow_html=True)
            else:
                st.markdown('''
                <div style="background-color: #f8fafc; border: 2px dashed #cbd5e1; border-radius: 10px; padding: 40px 20px; text-align: center; margin-top: 20px;">
                    <div style="font-size: 3.5rem; margin-bottom: 15px;">🔒</div>
                    <h3 style="color: #64748b; margin-top: 0;">Nội dung đang khóa</h3>
                    <p style="color: #94a3b8; font-size: 1.05em; max-width: 90%; margin: 0 auto;">Em hãy suy nghĩ và <strong>Gửi AI phân tích</strong> câu trả lời ở cột bên trái để mở khóa phần Giải thích khoa học, Công thức và Ví dụ nhé!</p>
                </div>
                ''', unsafe_allow_html=True)

    # === GIAO DIỆN 3: BẢN ĐỒ THỬ THÁCH (ĐIỆP VỤ PHYSIX ĐỘNG) ===
    elif st.session_state.nav_page == "🎮 Bản đồ Thử thách (Game)":
        
        # CHỈNH SỬA CSS RIÊNG CHO TRANG GAME
        st.markdown('''
        <style>
            .stApp {
                background-color: #020617 !important;
                background-image: linear-gradient(rgba(56, 189, 248, 0.05) 1px, transparent 1px), linear-gradient(90deg, rgba(56, 189, 248, 0.05) 1px, transparent 1px) !important;
                background-size: 30px 30px !important;
            }
            .stMarkdown p, .stMarkdown li, .stMarkdown span { color: #f8fafc !important; }
            
            .neon-title { text-align: center; color: #ef4444 !important; font-weight: 900; font-size: 3.5rem; text-transform: uppercase; text-shadow: 0 0 10px #dc2626, 0 0 20px #991b1b, 0 0 30px #7f1d1d; margin-bottom: 0px; letter-spacing: 3px; }
            .cyber-warning { background-color: rgba(220, 38, 38, 0.1); border: 2px solid #ef4444; color: #fca5a5 !important; padding: 15px; border-radius: 8px; text-align: center; font-weight: bold; font-size: 1.2rem; margin-bottom: 30px; }
            .led-screen { background-color: #0f172a; border: 3px solid #38bdf8; box-shadow: 0 0 15px rgba(56, 189, 248, 0.4), inset 0 0 20px rgba(0, 0, 0, 0.8); padding: 20px; border-radius: 12px; text-align: center; font-size: 1.8rem; font-family: 'Courier New', Courier, monospace; letter-spacing: 8px; margin-bottom: 30px; }
            .led-code { color: #fde047 !important; font-weight: bold; text-shadow: 0 0 10px #facc15; }
            .mission-panel { background: rgba(15, 23, 42, 0.8); border-left: 5px solid #38bdf8; border-radius: 10px; padding: 25px; margin-bottom: 20px; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3); }
            .mission-header { color: #38bdf8 !important; font-size: 1.8rem !important; font-weight: 800; border-bottom: 1px solid #334155; padding-bottom: 10px; margin-bottom: 15px;}
            
            div[data-testid="stRadio"], div[data-testid="stSelectbox"], div[data-testid="stTextInput"] {
                background-color: #f8fafc !important; 
                padding: 20px !important;
                border-radius: 12px !important;
                border: 2px solid #38bdf8 !important;
                box-shadow: 0 0 15px rgba(56,189,248,0.2) !important;
                margin-top: 10px;
            }
            div[data-testid="stRadio"] p, div[data-testid="stRadio"] span, div[data-testid="stRadio"] div,
            div[data-testid="stSelectbox"] p, div[data-testid="stSelectbox"] span,
            div[data-testid="stTextInput"] p, div[data-testid="stTextInput"] span {
                color: #0f172a !important; 
                font-weight: 600 !important;
            }
        </style>
        ''', unsafe_allow_html=True)

        st.markdown("<div class='neon-title'>🕵️‍♂️ ĐIỆP VỤ PHYSIX</div>", unsafe_allow_html=True)
        st.markdown("<div class='cyber-warning'>🚨 CẢNH BÁO: Tàu tốc hành đang mất phanh. Các đặc vụ PHY-LIFE cần giải mã các trạm điều khiển để kích hoạt hệ thống phanh khẩn cấp!</div>", unsafe_allow_html=True)
        
        if df_game.empty:
            st.error("⚠️ Hệ thống chưa tìm thấy dữ liệu Game trong file Excel. Cô hãy tạo một Sheet tên là 'Du_lieu_Game' theo đúng mẫu và tải lên nhé!")
        else:
            if 'station' not in st.session_state:
                st.session_state.station = 1
                st.session_state.passcodes = ["_", "_", "_", "_"]
                st.session_state.tram2_matched = False
                st.session_state.play_sound = False
                
            tong_so_tram = len(df_game)
            
            progress_val = int(((st.session_state.station - 1) / tong_so_tram) * 100)
            st.progress((st.session_state.station - 1) / tong_so_tram)
            
            passcodes_display = []
            for i in range(tong_so_tram):
                if i < st.session_state.station - 1:
                    passcodes_display.append(str(df_game.iloc[i]['Đáp án']).strip())
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

            if st.session_state.station <= tong_so_tram:
                tram_data = df_game.iloc[st.session_state.station - 1]
                
                st.markdown(f"""
                <div class='mission-panel'>
                    <div class='mission-header'>📍 Trạm {tram_data['Trạm']}: {tram_data['Tên trạm']}</div>
                    <p><strong>Nhiệm vụ:</strong> {tram_data['Nhiệm vụ']}</p>
                </div>
                """, unsafe_allow_html=True)
                
                # --- XỬ LÝ HIỂN THỊ ẢNH (CANH GIỮA VÀ THU NHỎ DÀNH CHO GAME) ---
                if pd.notna(tram_data.get('Ảnh minh họa')) and str(tram_data['Ảnh minh họa']).strip() != "":
                    img_path = os.path.join("images", str(tram_data['Ảnh minh họa']).strip())
                    if os.path.exists(img_path):
                        # Chia 3 cột để ép ảnh vào giữa, làm ảnh gọn gàng lại
                        img_col1, img_col2, img_col3 = st.columns([1, 2, 1])
                        with img_col2:
                            st.image(img_path, use_container_width=True)
                    else:
                        st.warning(f"✍️ Đang chờ nét vẽ Sketchnote cho ảnh: {tram_data['Ảnh minh họa']}")

                loai_cau_hoi = str(tram_data['Loại câu hỏi']).strip()
                dap_an_dung = str(tram_data['Đáp án']).strip()
                
                if loai_cau_hoi == "Trắc nghiệm":
                    lua_chon = [opt.strip() for opt in str(tram_data['Các lựa chọn']).split("|")]
                    ans = st.radio("Chọn đáp án:", ["Chưa chọn"] + lua_chon, key=f"q_{st.session_state.station}")
                    
                    if st.button("🚀 Xác nhận mã", use_container_width=True):
                        if ans != "Chưa chọn" and ans.startswith(dap_an_dung):
                            st.success(f"✅ {tram_data['Phản hồi đúng']}")
                            st.session_state.play_sound = True
                            time.sleep(1.5)
                            st.session_state.station += 1
                            st.rerun()
                        else:
                            st.error(f"❌ {tram_data['Phản hồi sai']}")
                            
                else: 
                    ans = st.text_input("Nhập mật mã thu được:", key=f"q_{st.session_state.station}")
                    
                    if st.button("🚀 Xác nhận mã", use_container_width=True):
                        if ans.strip().lower() == dap_an_dung.lower():
                            st.success(f"✅ {tram_data['Phản hồi đúng']}")
                            st.session_state.play_sound = True
                            time.sleep(1.5)
                            st.session_state.station += 1
                            st.rerun()
                        else:
                            st.error(f"❌ {tram_data['Phản hồi sai']}")

            else:
                st.balloons()
                st.markdown("<div style='background-color: rgba(34, 197, 94, 0.2); padding: 40px; border-radius: 15px; text-align: center; border: 2px solid #4ade80; box-shadow: 0 0 30px rgba(74, 222, 128, 0.5);'><h1 style='color: #4ade80; font-size: 3.5rem; margin-bottom: 10px; text-shadow: 0 0 10px #4ade80;'>🎉 KÍCH HOẠT THÀNH CÔNG!</h1><h2 style='color: #86efac;'>CỨU HỘ HOÀN TẤT. KIỆN HÀNG TRI THỨC ĐÃ ĐƯỢC BẢO VỆ.</h2></div>", unsafe_allow_html=True)
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("🔄 Chơi lại Điệp vụ", use_container_width=True):
                    st.session_state.station = 1
                    st.rerun()

    # === GIAO DIỆN 4: AI CHAT (NHÀ KHÁM PHÁ VẬT LÍ) ===
    elif st.session_state.nav_page == "🤖 Hỏi Nhà khám phá AI":
        st.markdown("<h2 style='color: #0D9488;'>🤖 Nhà khám phá AI</h2>", unsafe_allow_html=True)
        st.markdown("<span class='main-text'>Chào em! Cô là Nhà khám phá Vật lí. Em có hiện tượng gì thú vị muốn kể cho cô nghe, nhập một khái niệm muốn tìm hiểu, hay muốn thử sức với bài tập vận dụng nào?</span>", unsafe_allow_html=True)

        if not api_ready:
            st.warning("⚠️ Tính năng AI chưa được kích hoạt. Vui lòng kiểm tra lại GEMINI_API_KEY trong Secrets.")
        else:
            if "chat_messages" not in st.session_state:
                st.session_state.chat_messages = []
            for msg in st.session_state.chat_messages:
                with st.chat_message(msg["role"]):
                    st.markdown(msg["content"])
            if prompt := st.chat_input("Nhập câu hỏi, hiện tượng hoặc khái niệm em muốn khám phá..."):
                st.session_state.chat_messages.append({"role": "user", "content": prompt})
                with st.chat_message("user"):
                    st.markdown(prompt)
                with st.chat_message("assistant"):
                    with st.spinner("Cô đang phân tích..."):
                        history_context = "".join([f"{'Học sinh' if m['role']=='user' else 'Cô giáo'}: {m['content']}\n" for m in st.session_state.chat_messages[-5:-1]])
                        sys_prompt = f'''Bạn là "Nhà khám phá Vật lí", chuyên gia sư phạm hướng dẫn học sinh lớp 10 (chương Động học). Xử lý câu hỏi của học sinh: "{prompt}". Lịch sử: {history_context}. Yêu cầu: Giải thích hiện tượng, tìm hiện tượng theo khái niệm, phân tích tình huống mới, tạo bài tập vận dụng, hoặc đặt câu hỏi gợi mở. Xưng "cô", gọi "em", ngôn ngữ thân thiện.'''
                        try:
                            response = model.generate_content(sys_prompt)
                            st.markdown(response.text)
                            st.session_state.chat_messages.append({"role": "assistant", "content": response.text})
                        except Exception as e:
                            st.error(f"Hệ thống đang bận, em thử lại sau nhé! (Lỗi chi tiết: {e})")

except Exception as e:
    st.error(f"Có lỗi khi đọc dữ liệu Excel: {e}")
