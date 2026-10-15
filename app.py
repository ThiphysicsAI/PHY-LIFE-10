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

# Nhúng CSS tùy chỉnh
st.markdown('''
<style>
    @import url('https://fonts.googleapis.com/css2?family=Quicksand:wght@400;500;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Quicksand', sans-serif !important; }
    .stApp { background-color: #FCFBF4; }
    h1, h2, h3, h4, h5, h6, p, span, div { color: #1E293B; }
    [data-testid="stSidebar"] { background-color: #ffffff; border-right: 1px solid #e2e8f0; }
    .stAlert { border-radius: 1rem !important; border: none !important; }
    .phy-card { background-color: white; padding: 2rem 1.5rem; border-radius: 1rem; border: 1px solid #e2e8f0; box-shadow: 0 1px 3px rgba(0,0,0,0.1); transition: transform 0.3s, box-shadow 0.3s, border-color 0.3s; height: 100%; text-align: center; display: flex; flex-direction: column; align-items: center; justify-content: center; }
    .phy-card:hover { transform: translateY(-5px); box-shadow: 0 10px 15px -3px rgba(0,0,0,0.1); border-color: #0D9488; background-color: #F0FDFA; }
    .icon-box { width: 60px; height: 60px; border-radius: 16px; display: flex; align-items: center; justify-content: center; font-size: 28px; margin-bottom: 15px; }
    .game-box { background-color: white; padding: 25px; border-radius: 15px; border-left: 6px solid #0D9488; box-shadow: 0 4px 6px rgba(0,0,0,0.05); margin-bottom: 20px;}
    .locked-box { background-color: #f8fafc; padding: 25px; border-radius: 15px; border: 2px dashed #cbd5e1; text-align: center; color: #94a3b8; margin-bottom: 20px;}
</style>
''', unsafe_allow_html=True)

# 2. ĐỌC DỮ LIỆU TỪ EXCEL
@st.cache_data
def load_data():
    df = pd.read_excel('du_lieu_tinh_huong_dong_hoc_vat_li_10.xlsx')
    return df

# === NGÂN HÀNG CÂU HỎI GAME (Tích hợp sẵn) ===
# Sau này cô có thể chuyển dữ liệu này sang 1 sheet mới trong file Excel
NGAN_HANG_GAME = [
    {
        "tram": 1,
        "loai": "Trắc nghiệm",
        "tieu_de": "🚩 Trạm 1: Khởi động (Gia tốc)",
        "cau_hoi": "Khi một chiếc xe máy đang đứng yên bắt đầu vọt đi khi đèn xanh, vectơ gia tốc của xe có hướng như thế nào so với vectơ vận tốc?",
        "lua_chon": ["A. Hướng ngược chiều với vận tốc.", "B. Hướng cùng chiều với vận tốc.", "C. Vuông góc với phương chuyển động.", "D. Bằng không."],
        "dap_an": "B",
        "giai_thich": "Trong chuyển động nhanh dần đều (tăng tốc), gia tốc và vận tốc luôn cùng chiều nhau em nhé!"
    },
    {
        "tram": 2,
        "loai": "Ghép nối",
        "tieu_de": "🚩 Trạm 2: Vượt chướng ngại vật (Phân loại chuyển động)",
        "cau_hoi": "Hãy chọn loại chuyển động đúng nhất cho hiện tượng: 'Trực thăng đang bay ngang thả thùng hàng cứu trợ xuống vùng lũ'.",
        "lua_chon": ["A. Chuyển động rơi tự do", "B. Chuyển động thẳng đều", "C. Chuyển động ném ngang", "D. Chuyển động ném xiên"],
        "dap_an": "C",
        "giai_thich": "Thùng hàng có vận tốc đầu theo phương ngang bằng vận tốc trực thăng, đồng thời rơi xuống dưới tác dụng của trọng lực nên quỹ đạo là một Parabol (ném ngang)."
    },
    {
        "tram": 3,
        "loai": "Điền khuyết",
        "tieu_de": "🚩 Trạm 3: Giải mã công thức",
        "cau_hoi": "Điền hệ số thích hợp vào chỗ trống để hoàn thành công thức tính quãng đường trong chuyển động thẳng nhanh dần đều không vận tốc đầu ($v_0 = 0$): \n\n $$s = [......] * a * t^2$$",
        "lua_chon": [], # Điền khuyết không có lựa chọn
        "dap_an": ["1/2", "0.5"], # Các cách ghi được chấp nhận
        "giai_thich": "Công thức chuẩn là $s = \\frac{1}{2}at^2$ (hoặc 0.5 * a * t^2)."
    }
]
TONG_SO_TRAM = len(NGAN_HANG_GAME)

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

try:
    df = load_data()
    
    # === GIAO DIỆN 1: TRANG CHỦ ===
    if st.session_state.nav_page == "🏠 Trang chủ":
        col_text, col_img = st.columns([1.2, 1])
        with col_text:
            st.markdown("<br>", unsafe_allow_html=True) 
            st.markdown('''
            <div style="display: inline-block; padding: 4px 16px; background-color: #FEF08A; border-radius: 999px; font-weight: 700; font-size: 0.9rem; margin-bottom: 1rem;">
                ✨ Chương trình Lớp 10 Mới
            </div>
            <h1 style="font-size: 3.5rem; font-weight: 800; line-height: 1.2; margin-bottom: 1rem;">Vật lí quanh ta!</h1>
            <p style="font-size: 1.2rem; color: #475569; margin-bottom: 2rem;">
                Khám phá chuyển động trong đời sống. Quan sát hiện tượng, kết nối kiến thức và tự mình tìm ra lời giải.
            </p>
            ''', unsafe_allow_html=True)
            st.info("👈 **Hãy chọn các chuyên mục ở Menu bên trái hoặc bấm trực tiếp vào các thẻ bên dưới!**")

        with col_img:
            st.markdown('''
            <div style="border: 2px dashed #1E293B; border-radius: 1rem; padding: 2rem; background-color: white; position: relative; margin-top: 2rem; text-align: center; box-shadow: 8px 8px 0px #FEF08A;">
                <h3 style="font-family: 'Caveat', cursive; color: #0D9488;">v = s / t</h3>
                <p style="color: #64748b;"><i>(Khu vực hiển thị ảnh minh họa)</i></p>
                <div style="font-size: 4rem;">🚴‍♂️ 💨</div>
            </div>
            ''', unsafe_allow_html=True)

        st.markdown("<br><br><br>", unsafe_allow_html=True)
        st.markdown("<h2 style='text-align: center; margin-bottom: 2rem;'>Em muốn khám phá gì?</h2>", unsafe_allow_html=True)
        
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.markdown('''<div class="phy-card"><div class="icon-box" style="background-color: #EFF6FF; color: #3B82F6;">📖</div><h3 style="font-size: 1.1rem; margin-bottom: 8px;">Theo bài học</h3><p style="color: #64748b; font-size: 0.85rem; margin-bottom: 0;">Ôn tập vận tốc, gia tốc.</p></div>''', unsafe_allow_html=True)
            if st.button("👉 Khám phá", use_container_width=True, key="card_btn_1"):
                st.session_state.nav_page = "📚 Khám phá Hiện tượng"
                st.rerun()
                
        with c2:
            st.markdown('''<div class="phy-card"><div class="icon-box" style="background-color: #FEF08A; color: #A16207;">💡</div><h3 style="font-size: 1.1rem; margin-bottom: 8px;">Theo hiện tượng</h3><p style="color: #64748b; font-size: 0.85rem; margin-bottom: 0;">Tình huống thực tiễn.</p></div>''', unsafe_allow_html=True)
            if st.button("👉 Khám phá", use_container_width=True, key="card_btn_2"):
                st.session_state.nav_page = "📚 Khám phá Hiện tượng"
                st.rerun()
                
        with c3:
            st.markdown('''<div class="phy-card"><div class="icon-box" style="background-color: #E0F2FE; color: #0284C7;">🎮</div><h3 style="font-size: 1.1rem; margin-bottom: 8px;">Bản đồ Thử thách</h3><p style="color: #64748b; font-size: 0.85rem; margin-bottom: 0;">Vượt ải nhận điểm thưởng.</p></div>''', unsafe_allow_html=True)
            if st.button("👉 Vào chơi Game", use_container_width=True, key="card_btn_game"):
                st.session_state.nav_page = "🎮 Bản đồ Thử thách (Game)"
                st.rerun()

        with c4:
            st.markdown('''<div class="phy-card"><div class="icon-box" style="background-color: #CCFBF1; color: #0D9488;">🤖</div><h3 style="font-size: 1.1rem; margin-bottom: 8px;">Hỏi AI Khám phá</h3><p style="color: #64748b; font-size: 0.85rem; margin-bottom: 0;">Trợ lý ảo thông minh.</p></div>''', unsafe_allow_html=True)
            if st.button("👉 Hỏi AI", use_container_width=True, key="card_btn_3"):
                st.session_state.nav_page = "🤖 Hỏi Nhà khám phá AI"
                st.rerun()

    # === GIAO DIỆN 2: THƯ VIỆN HIỆN TƯỢNG ===
    elif st.session_state.nav_page == "📚 Khám phá Hiện tượng":
        st.markdown("<h2 style='color: #0D9488;'>Thư viện Hiện tượng thực tiễn</h2>", unsafe_allow_html=True)
        col_loc1, col_loc2 = st.columns(2)
        with col_loc1:
            danh_sach_bai = df['Bài học liên quan'].unique()
            bai_hoc_chon = st.selectbox("📌 Chiều 1: Từ Sách giáo khoa (Bài học) đến Hiện tượng:", danh_sach_bai)
        
        df_loc = df[df['Bài học liên quan'] == bai_hoc_chon]
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
        st.markdown(f"<h1 style='font-size: 2.2rem; margin-bottom: 1rem;'>{ho_so['Tên tình huống']}</h1>", unsafe_allow_html=True)
        
        col_trai, col_phai = st.columns([1.1, 1])
        with col_trai:
            st.info(f"📍 **Bối cảnh:** {ho_so['Bối cảnh']}")
            st.markdown(f"**Quan sát:** {ho_so['Mô tả quan sát']}")
            ten_file_anh = str(ho_so['Tên file ảnh'])
            duong_dan_anh = os.path.join("images", ten_file_anh)
            if os.path.exists(duong_dan_anh):
                st.image(duong_dan_anh, use_container_width=True)
            else:
                st.warning(f"✍️ Đang chờ nét vẽ Sketchnote... (Tên file: {ten_file_anh})")
                
            st.markdown(f"**❓ Câu hỏi gợi mở:** *{ho_so['Câu hỏi gợi mở']}*")
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
                            prompt_ai = f'''Bạn là cô giáo Vật lí 10. Tình huống: {ho_so['Tên tình huống']}. Câu hỏi: {ho_so['Câu hỏi gợi mở']}. Giải thích đúng: {ho_so['Giải thích khoa học']}. Học sinh trả lời: "{cau_tra_loi_hs}". Nhận xét 2-3 câu. Khen nếu đúng, sửa nếu sai, động viên nếu không biết. LUÔN CHỐT CÂU CUỐI: "Em hãy xem phần 'Giải thích khoa học' bên cạnh để hiểu rõ hơn nhé!"'''
                            try:
                                response = model.generate_content(prompt_ai)
                                st.session_state.ai_response = f"**🤖 AI phân tích:** {response.text}"
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
                    html_tu_khoa = "".join([f"<span style='background-color: #E2E8F0; padding: 4px 8px; border-radius: 4px; margin-right: 5px; font-size: 0.85em;'>{tag.strip()}</span>" for tag in tu_khoa_list])
                    st.markdown(html_tu_khoa, unsafe_allow_html=True)
            else:
                st.markdown('''<div class="locked-box"><div style="font-size: 3.5rem; margin-bottom: 15px;">🔒</div><h3 style="margin-top: 0;">Nội dung đang khóa</h3><p>Em hãy <strong>Gửi AI phân tích</strong> để mở khóa nhé!</p></div>''', unsafe_allow_html=True)

    # === GIAO DIỆN MỚI: GAME HÓA (GAMIFICATION) ===
    elif st.session_state.nav_page == "🎮 Bản đồ Thử thách (Game)":
        st.markdown("<h2 style='color: #0D9488;'>🎮 Bản đồ Thử thách: Hành trình Động học</h2>", unsafe_allow_html=True)
        
        # Khởi tạo trạng thái Game
        if "current_station" not in st.session_state:
            st.session_state.current_station = 1
            st.session_state.game_score = 0
            st.session_state.play_sound = False
            
        # Hàm phát âm thanh khi trả lời đúng (nhúng HTML audio)
        if st.session_state.play_sound:
            # File âm thanh "ting" chúc mừng
            sound_html = '<audio autoplay><source src="https://assets.mixkit.co/active_storage/sfx/2013/2013-preview.mp3" type="audio/mpeg"></audio>'
            st.markdown(sound_html, unsafe_allow_html=True)
            st.session_state.play_sound = False

        # THANH TIẾN TRÌNH (Progress Bar)
        progress_val = int(((st.session_state.current_station - 1) / TONG_SO_TRAM) * 100)
        st.markdown(f"**🌟 Tiến trình vượt ải: {progress_val}% (Đã qua {st.session_state.current_station - 1}/{TONG_SO_TRAM} Trạm)**")
        st.progress((st.session_state.current_station - 1) / TONG_SO_TRAM)
        
        st.markdown("---")

        # Hiển thị tuần tự các trạm
        for i, station in enumerate(NGAN_HANG_GAME):
            station_num = station["tram"]
            
            # Nếu trạm này chưa được mở khóa
            if station_num > st.session_state.current_station:
                st.markdown(f'''<div class="locked-box"><div style="font-size: 2rem;">🔒</div><h3>Trạm {station_num} đang khóa</h3><p>Hãy vượt qua Trạm {station_num - 1} để đi tiếp!</p></div>''', unsafe_allow_html=True)
            
            # Nếu trạm này đã vượt qua (hiển thị chế độ thu gọn)
            elif station_num < st.session_state.current_station:
                with st.expander(f"✅ {station['tieu_de']} (Đã vượt qua)"):
                    st.success(f"**Câu hỏi:** {station['cau_hoi']}")
                    st.info(f"**Giải thích:** {station['giai_thich']}")
            
            # Nếu ĐANG ở trạm này (hiển thị form câu hỏi)
            else:
                st.markdown(f"<div class='game-box'><h3 style='color: #0D9488; margin-top:0;'>{station['tieu_de']}</h3></div>", unsafe_allow_html=True)
                st.write(f"**❓ {station['cau_hoi']}**")
                
                # Render UI theo loại câu hỏi
                if station['loai'] in ["Trắc nghiệm", "Ghép nối"]:
                    tra_loi = st.radio("Chọn đáp án của em:", station['lua_chon'], index=None, key=f"q_{station_num}")
                else: # Điền khuyết
                    tra_loi = st.text_input("Nhập đáp án của em:", key=f"q_{station_num}")
                
                # Nút xác nhận
                if st.button("Chốt đáp án 🎯", key=f"btn_{station_num}"):
                    if not tra_loi:
                        st.warning("Em chưa nhập đáp án kìa!")
                    else:
                        # Kiểm tra đáp án
                        is_correct = False
                        if station['loai'] in ["Trắc nghiệm", "Ghép nối"]:
                            if tra_loi.startswith(station['dap_an']):
                                is_correct = True
                        else: # Điền khuyết
                            # Kiểm tra xem chuỗi nhập vào có khớp 1 trong các đáp án đúng không
                            if any(ans in tra_loi.lower() for ans in station['dap_an']):
                                is_correct = True

                        if is_correct:
                            st.session_state.current_station += 1
                            st.session_state.game_score += 10
                            st.session_state.play_sound = True # Bật cờ phát âm thanh
                            st.rerun() # Tải lại trang để mở khóa trạm tiếp theo
                        else:
                            st.error("❌ Sai rồi em ơi! Thử suy nghĩ lại xem nào.")
                st.markdown("---")

        # KHI HOÀN THÀNH TOÀN BỘ GAME
        if st.session_state.current_station > TONG_SO_TRAM:
            st.balloons() # Hiệu ứng thả bóng bay của Streamlit
            st.success(f"🏆 **CHÚC MỪNG! EM ĐÃ HOÀN THÀNH XUẤT SẮC BẢN ĐỒ THỬ THÁCH VỚI {st.session_state.game_score} ĐIỂM!**")
            if st.button("🔄 Chơi lại từ đầu"):
                st.session_state.current_station = 1
                st.session_state.game_score = 0
                st.rerun()

    # === GIAO DIỆN 4: AI CHAT ===
    elif st.session_state.nav_page == "🤖 Hỏi Nhà khám phá AI":
        st.markdown("<h2 style='color: #0D9488;'>🤖 Nhà khám phá AI</h2>", unsafe_allow_html=True)
        st.markdown("Chào em! Cô là Nhà khám phá Vật lí. Em có hiện tượng gì thú vị muốn kể cho cô nghe không?")

        if not api_ready:
            st.warning("⚠️ Tính năng AI chưa được kích hoạt. Vui lòng kiểm tra lại GEMINI_API_KEY trong Secrets.")
        else:
            if "chat_messages" not in st.session_state:
                st.session_state.chat_messages = []
            for msg in st.session_state.chat_messages:
                with st.chat_message(msg["role"]):
                    st.markdown(msg["content"])
            if prompt := st.chat_input("Nhập câu hỏi..."):
                st.session_state.chat_messages.append({"role": "user", "content": prompt})
                with st.chat_message("user"):
                    st.markdown(prompt)
                with st.chat_message("assistant"):
                    with st.spinner("Cô đang suy nghĩ..."):
                        sys_prompt = f"Bạn là giáo viên Vật lý lớp 10 hướng dẫn học sinh. Học sinh hỏi: {prompt}. Hãy trả lời ngắn gọn, gợi mở, xưng 'cô' và gọi 'em'."
                        try:
                            response = model.generate_content(sys_prompt)
                            st.markdown(response.text)
                            st.session_state.chat_messages.append({"role": "assistant", "content": response.text})
                        except Exception as e:
                            st.error("Lỗi kết nối AI.")

except Exception as e:
    st.error(f"Có lỗi khi đọc dữ liệu Excel: {e}")
