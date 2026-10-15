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
    .phy-card { background-color: white; padding: 2rem 1.5rem; border-radius: 1rem; border: 1px solid #e2e8f0; box-shadow: 0 1px 3px rgba(0,0,0,0.1); transition: transform 0.3s, box-shadow 0.3s, border-color 0.3s; height: 100%; text-align: center; display: flex; flex-direction: column; align-items: center; justify-content: center; margin-bottom: 10px; }
    .phy-card:hover { transform: translateY(-5px); box-shadow: 0 10px 15px -3px rgba(0,0,0,0.1); border-color: #0D9488; background-color: #F0FDFA; }
    .icon-box { width: 60px; height: 60px; border-radius: 16px; display: flex; align-items: center; justify-content: center; font-size: 28px; margin-bottom: 15px; }
    .game-title { text-align: center; color: #b91c1c; font-weight: 800; font-size: 2.5rem; margin-bottom: 10px; }
    .game-warning { background-color: #fef2f2; color: #991b1b; padding: 15px; border-radius: 10px; border-left: 5px solid #ef4444; font-weight: bold; text-align: center; margin-bottom: 20px;}
    .game-station { background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%); color: white; padding: 20px; border-radius: 16px; text-align: center; box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.3); margin-bottom: 20px; }
    .game-station h3 { color: #38bdf8 !important; margin: 0; }
    .mission-box { background-color: white; padding: 20px; border-radius: 12px; border: 1px solid #e2e8f0; margin-bottom: 15px; }
</style>
''', unsafe_allow_html=True)

# 2. ĐỌC DỮ LIỆU TỪ EXCEL
@st.cache_data
def load_data():
    df = pd.read_excel('du_lieu_tinh_huong_dong_hoc_vat_li_10.xlsx')
    return df

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
            st.markdown('''<div class="phy-card"><div class="icon-box" style="background-color: #E0F2FE; color: #0284C7;">🎮</div><h3 style="font-size: 1.1rem; margin-bottom: 8px;">Bản đồ Thử thách</h3><p style="color: #64748b; font-size: 0.85rem; margin-bottom: 0;">Điệp vụ PHYSIX.</p></div>''', unsafe_allow_html=True)
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
                st.warning(f"✍️ Đang chờ nét vẽ Sketchnote... (Tên file cần có: {ten_file_anh})")
                
            st.markdown(f"**❓ Câu hỏi gợi mở:** *{ho_so['Câu hỏi gợi mở']}*")
            st.markdown('''
            <div style="background-color: #F0FDF4; padding: 15px; border-radius: 10px; border-left: 5px solid #22C55E; margin-top: 20px; margin-bottom: 10px;">
                <h4 style="color: #15803D; margin-top: 0; display: flex; align-items: center; gap: 8px;">🤖 AI phân tích nhanh</h4>
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
                            prompt_ai = f'''Bạn là cô giáo Vật lí 10, rất tâm lý và khích lệ học sinh. Tình huống: {ho_so['Tên tình huống']}. Câu hỏi: {ho_so['Câu hỏi gợi mở']}. Giải thích đúng: {ho_so['Giải thích khoa học']}. Học sinh trả lời: "{cau_tra_loi_hs}". Nhận xét 2-3 câu. Khen nếu đúng, sửa nếu sai, động viên nếu không biết. LUÔN CHỐT CÂU CUỐI: "Em hãy xem phần 'Giải thích khoa học' bên cạnh để hiểu rõ hơn nhé!"'''
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
                    st.markdown("<h4 style='color: #0D9488;'>🛠️ Hoạt động thực hành</h4>", unsafe_allow_html=True)
                    st.info(ho_so['Hoạt động thực hành'])
                    st.markdown("<h4 style='color: #0D9488;'>🏷️ Từ khóa</h4>", unsafe_allow_html=True)
                    
                    tu_khoa_list = str(ho_so['Từ khóa']).split(',')
                    html_tu_khoa = "".join([f"<span style='background-color: #E2E8F0; padding: 4px 8px; border-radius: 4px; margin-right: 5px; font-size: 0.85em;'>{tag.strip()}</span>" for tag in tu_khoa_list])
                    st.markdown(html_tu_khoa, unsafe_allow_html=True)
                    st.markdown("<br><p style='font-size: 0.8em; color: #94A3B8;'><strong>Nguồn tham khảo:</strong> " + str(ho_so['Nguồn tham khảo']) + "</p>", unsafe_allow_html=True)
            else:
                st.markdown('''<div style="background-color: #f8fafc; border: 2px dashed #cbd5e1; border-radius: 10px; padding: 40px 20px; text-align: center; margin-top: 20px;"><div style="font-size: 3.5rem; margin-bottom: 15px;">🔒</div><h3 style="color: #64748b; margin-top: 0;">Nội dung đang khóa</h3><p style="color: #94a3b8; font-size: 1.05em; max-width: 90%; margin: 0 auto;">Em hãy suy nghĩ và <strong>Gửi AI phân tích</strong> câu trả lời ở cột bên trái để mở khóa nhé!</p></div>''', unsafe_allow_html=True)

    # === GIAO DIỆN 3: BẢN ĐỒ THỬ THÁCH (ĐIỆP VỤ PHYSIX) ===
    elif st.session_state.nav_page == "🎮 Bản đồ Thử thách (Game)":
        
        # Khởi tạo các biến trạng thái cho Game nếu chưa có
        if 'station' not in st.session_state:
            st.session_state.station = 1
            st.session_state.passcodes = ["_", "_", "_", "_"]
            st.session_state.tram2_matched = False
            st.session_state.play_sound = False

        st.markdown("<div class='game-title'>🕵️‍♂️ ĐIỆP VỤ PHYSIX: MẬT MÃ ĐỘNG HỌC</div>", unsafe_allow_html=True)
        st.markdown("<div class='game-warning'>🚨 CẢNH BÁO: Tàu tốc hành đang mất phanh. Các đặc vụ 12A7 cần giải mã 4 trạm điều khiển để kích hoạt hệ thống phanh khẩn cấp!</div>", unsafe_allow_html=True)
        
        # Hiển thị thanh tiến trình và Mã khóa thu thập được
        progress_val = int(((st.session_state.station - 1) / 4) * 100)
        st.progress((st.session_state.station - 1) / 4)
        
        st.markdown(f"""
        <div style='background-color: #1e293b; color: #38bdf8; padding: 15px; border-radius: 10px; text-align: center; font-size: 1.5rem; font-family: monospace; letter-spacing: 5px; margin-bottom: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.3);'>
            MÃ KÍCH HOẠT THU THẬP: <span style='color: #fde047; font-weight: bold;'>{st.session_state.passcodes[0]} {st.session_state.passcodes[1]} {st.session_state.passcodes[2]} {st.session_state.passcodes[3]}</span>
        </div>
        """, unsafe_allow_html=True)

        # Hiệu ứng âm thanh khi qua trạm
        if st.session_state.play_sound:
            sound_html = '<audio autoplay><source src="https://assets.mixkit.co/active_storage/sfx/2013/2013-preview.mp3" type="audio/mpeg"></audio>'
            st.markdown(sound_html, unsafe_allow_html=True)
            st.session_state.play_sound = False

        # ==========================================
        # TRẠM 1: KHÔNG LƯU
        # ==========================================
        if st.session_state.station == 1:
            st.markdown("<div class='game-station'><h3>📍 Trạm 1: Không Lưu</h3></div>", unsafe_allow_html=True)
            st.markdown("<div class='mission-box'><strong>Mục tiêu:</strong> Vượt qua rào cản tư duy về Rơi tự do & Lực cản.<br><br><strong>Nhiệm vụ:</strong> Một vận động viên nhảy dù nhảy khỏi máy bay. Sau khi bung dù một lúc, người đó rơi xuống mặt đất với vận tốc không đổi. Hiện tượng này được giải thích bằng khái niệm nào?</div>", unsafe_allow_html=True)
            
            ans1 = st.radio("Chọn đáp án để quét mã in chìm:", [
                "A. Gia tốc rơi tự do giảm dần.", 
                "B. Quán tính triệt tiêu trọng lực.", 
                "C. Lực cản không khí cân bằng với trọng lực.", 
                "D. Động năng ban đầu đã tiêu hao hết."
            ], index=None)
            
            if st.button("Xác nhận mã Trạm 1", use_container_width=True):
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

        # ==========================================
        # TRẠM 2: ĐỘNG CƠ
        # ==========================================
        elif st.session_state.station == 2:
            st.markdown("<div class='game-station'><h3>⚙️ Trạm 2: Động Cơ</h3></div>", unsafe_allow_html=True)
            st.markdown("<div class='mission-box'><strong>Mục tiêu:</strong> Dịch ngôn ngữ thực tế sang đồ thị v-t.<br><br><strong>Nhiệm vụ:</strong> Hãy sắp xếp các thẻ Hiện tượng (1, 2, 3, 4) khớp với các thẻ Đồ thị (A, B, C, D).</div>", unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            with col1:
                g1 = st.selectbox("1. Đạp phanh", ["Chưa ghép", "Thẻ A", "Thẻ B", "Thẻ C", "Thẻ D"])
                g2 = st.selectbox("2. Dừng chờ đèn đỏ", ["Chưa ghép", "Thẻ A", "Thẻ B", "Thẻ C", "Thẻ D"])
            with col2:
                g3 = st.selectbox("3. Nhấn ga khởi hành", ["Chưa ghép", "Thẻ A", "Thẻ B", "Thẻ C", "Thẻ D"])
                g4 = st.selectbox("4. Chạy ổn định trên cao tốc", ["Chưa ghép", "Thẻ A", "Thẻ B", "Thẻ C", "Thẻ D"])

            if not st.session_state.tram2_matched:
                if st.button("Kiểm tra ghép nối", use_container_width=True):
                    if g1 == "Thẻ D" and g2 == "Thẻ A" and g3 == "Thẻ C" and g4 == "Thẻ B":
                        st.session_state.tram2_matched = True
                        st.rerun()
                    else:
                        st.error("❌ Ghép thẻ thất bại. Động cơ báo lỗi đồng bộ!")
            
            # Sau khi ghép đúng, lật thẻ hiện phép toán
            if st.session_state.tram2_matched:
                st.success("✅ Ghép nối thành công! Mặt sau của 4 thẻ lật lên hiện ra một thông điệp ẩn...")
                st.info("💻 **Hệ thống báo:** Giải mã phép toán `(D + A) x (C - B)`. Biết rằng D=5, A=3, C=4, B=3.")
                
                ans2 = st.text_input("Nhập mật mã số học (1 chữ số) thu được:")
                if st.button("Xác nhận mã Trạm 2", use_container_width=True):
                    if ans2.strip() == "8":
                        st.success("✅ Hệ thống ghi nhận mã số: 8. Đã mở khóa Trạm 3!")
                        st.session_state.passcodes[1] = "8"
                        st.session_state.play_sound = True
                        time.sleep(1.5)
                        st.session_state.station = 3
                        st.rerun()
                    else:
                        st.error("❌ Sai mã số. Động cơ đang quá tải!")

        # ==========================================
        # TRẠM 3: ẢO GIÁC
        # ==========================================
        elif st.session_state.station == 3:
            st.markdown("<div class='game-station'><h3>👁️ Trạm 3: Ảo Giác</h3></div>", unsafe_allow_html=True)
            st.markdown("<div class='mission-box'><strong>Mục tiêu:</strong> Phá vỡ góc nhìn tuyệt đối về hệ quy chiếu.<br><br><strong>Nhiệm vụ:</strong> Thả thùng hàng từ máy bay đang bay ngang. Đặc vụ hãy xác định Đúng (1) hoặc Sai (0) cho các nhận định sau:</div>", unsafe_allow_html=True)
            
            q1 = st.radio("1. Người đứng trên đảo thấy quỹ đạo của thùng hàng là đường thẳng đứng.", ["Chưa chọn", "Đúng (1)", "Sai (0)"], horizontal=True)
            q2 = st.radio("2. Phi công thấy quỹ đạo của thùng hàng là đường thẳng đứng.", ["Chưa chọn", "Đúng (1)", "Sai (0)"], horizontal=True)
            q3 = st.radio("3. Máy bay bay càng nhanh thì thùng hàng rơi chạm đất càng lâu.", ["Chưa chọn", "Đúng (1)", "Sai (0)"], horizontal=True)
            q4 = st.radio("4. Ngay trước khi chạm đất, vận tốc ngang của thùng hàng vẫn bằng vận tốc máy bay lúc thả (bỏ qua sức cản).", ["Chưa chọn", "Đúng (1)", "Sai (0)"], horizontal=True)

            if st.button("Tổng hợp mã Nhị phân", use_container_width=True):
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

        # ==========================================
        # TRẠM 4: BỨT TỐC
        # ==========================================
        elif st.session_state.station == 4:
            st.markdown("<div class='game-station'><h3>⚡ Trạm 4: Bứt Tốc</h3></div>", unsafe_allow_html=True)
            st.markdown("<div class='mission-box'><strong>Mục tiêu:</strong> Chọn hệ quy chiếu linh hoạt để giải quyết định lượng.<br><br><strong>Nhiệm vụ:</strong> Băng chuyền sân bay di chuyển với tốc độ 1 m/s. An đi bộ trên băng chuyền với tốc độ 2 m/s so với băng chuyền. Vali của An bị bỏ quên, trôi theo băng chuyền cách An 14 mét phía trước.<br>Hỏi An mất bao nhiêu giây để bắt kịp vali?</div>", unsafe_allow_html=True)
            
            ans4 = st.text_input("Nhập thời gian (giây):")
            
            if st.button("Xác nhận mã Trạm 4", use_container_width=True):
                if ans4.strip() == "7":
                    st.success("✅ Phân tích chuẩn xác! Vali đứng yên so với băng chuyền, nên thời gian = 14m / 2(m/s) = 7s. Hệ thống ghi nhận mã số: 7.")
                    st.session_state.passcodes[3] = "7"
                    st.session_state.play_sound = True
                    time.sleep(2)
                    st.session_state.station = 5
                    st.rerun()
                else:
                    st.error("❌ Tính toán sai lệch. Cảnh báo va chạm cận kề!")

        # ==========================================
        # CHẶNG CUỐI: NHẬP MÃ KÍCH HOẠT
        # ==========================================
        elif st.session_state.station == 5:
            st.markdown("<div class='game-station' style='background: linear-gradient(135deg, #b91c1c 0%, #7f1d1d 100%);'><h3>🛑 HỆ THỐNG PHANH KHẨN CẤP</h3></div>", unsafe_allow_html=True)
            st.warning("⚠️ YÊU CẦU NHẬP MÃ KÍCH HOẠT 4 CHỮ SỐ ĐỂ DỪNG TÀU!")
            
            final_code = st.text_input("Nhập mật mã:", type="password", placeholder="Nhập 4 chữ số thu thập được...")
            
            if st.button("KÍCH HOẠT PHANH", use_container_width=True):
                if final_code == "4857":
                    st.balloons()
                    st.markdown("<div style='background-color: #dcfce7; padding: 40px; border-radius: 15px; text-align: center; border: 3px solid #22c55e; box-shadow: 0 10px 25px rgba(34, 197, 94, 0.4);'><h1 style='color: #166534; font-size: 3.5rem; margin-bottom: 10px;'>🎉 KÍCH HOẠT THÀNH CÔNG!</h1><h2 style='color: #15803d;'>CỨU HỘ HOÀN TẤT. KIỆN HÀNG TRI THỨC ĐÃ ĐƯỢC BẢO VỆ.</h2><p style='font-size: 1.2rem; color: #14532d; margin-top: 20px;'>Các đặc vụ 12A7 đã xuất sắc hoàn thành nhiệm vụ Điệp vụ PHYSIX!</p></div>", unsafe_allow_html=True)
                    st.session_state.play_sound = True
                    
                    st.markdown("<br>", unsafe_allow_html=True)
                    if st.button("🔄 Chơi lại Điệp vụ", use_container_width=True):
                        st.session_state.station = 1
                        st.session_state.passcodes = ["_", "_", "_", "_"]
                        st.session_state.tram2_matched = False
                        st.rerun()
                else:
                    st.error("❌ HỆ THỐNG TỪ CHỐI. TÀU VẪN ĐANG LAO DỐC!")

    # === GIAO DIỆN 4: AI CHAT (NHÀ KHÁM PHÁ VẬT LÍ) ===
    elif st.session_state.nav_page == "🤖 Hỏi Nhà khám phá AI":
        st.markdown("<h2 style='color: #0D9488;'>🤖 Nhà khám phá AI</h2>", unsafe_allow_html=True)
        st.markdown("Chào em! Cô là Nhà khám phá Vật lí. Em có hiện tượng gì thú vị muốn kể cho cô nghe, nhập một khái niệm muốn tìm hiểu, hay muốn thử sức với bài tập vận dụng nào?")

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
                        
                        sys_prompt = f'''
                        [HƯỚNG DẪN CHO AI]
                        Bạn là "Nhà khám phá Vật lí", một chuyên gia sư phạm Vật lí hỗ trợ học sinh lớp 10 (chương Động học).
                        Dựa vào câu hỏi của học sinh, bạn PHẢI thực hiện linh hoạt 1 trong 5 chức năng sau:
                        
                        1. Giải thích hiện tượng: Nếu học sinh mô tả hiện tượng, hãy nhận diện, gắn với kiến thức Động học lớp 10. Chỉ ra dữ kiện đã biết/còn thiếu, nêu công thức, phân biệt sự thật khoa học/giả thiết, đề xuất câu hỏi khám phá tiếp theo.
                        2. Tìm hiện tượng theo kiến thức: Nếu học sinh nhập khái niệm (VD: gia tốc, rơi tự do), hãy đề xuất danh sách các hiện tượng đa dạng kèm bối cảnh thực tiễn, đánh giá mức độ liên quan và giải thích ngắn.
                        3. Phân tích tình huống mới: Nếu là tình huống lạ, hãy làm rõ tình huống -> xác định đại lượng đo được -> chọn mô hình vật lí -> giải thích bản chất -> cho ví dụ định lượng -> tạo câu hỏi vận dụng. LUÔN thêm câu: "Lưu ý: Nội dung AI sinh ra cần được xác thực và kiểm chứng thực tế."
                        4. Học bằng câu hỏi gợi mở: Tuyệt đối KHÔNG đưa đáp án ngay lập tức cho các bài toán hay câu hỏi suy luận. Đặt câu hỏi gợi mở từng bước để học sinh tự suy luận. Cung cấp gợi ý tăng dần khi học sinh gặp khó khăn.
                        5. Tạo bài tập vận dụng: Nếu học sinh yêu cầu bài tập, hãy tạo câu hỏi trắc nghiệm, Đ/S, hoặc tự luận có bối cảnh cụ thể và dữ kiện hợp lý. Ghi rõ "Số liệu giả định" nếu dùng số liệu không đo đạc thực tế.

                        QUY TẮC BẮT BUỘC KHÁC: 
                        - Luôn xưng là "cô", gọi người dùng là "em". 
                        - Ngôn ngữ thân thiện, khoa học, truyền cảm hứng.
                        [KẾT THÚC HƯỚNG DẪN]

                        Lịch sử trò chuyện gần đây:
                        {history_context}

                        Học sinh vừa nhắn: "{prompt}"
                        Cô giáo phản hồi:
                        '''
                        try:
                            response = model.generate_content(sys_prompt)
                            st.markdown(response.text)
                            st.session_state.chat_messages.append({"role": "assistant", "content": response.text})
                        except Exception as e:
                            st.error(f"Hệ thống đang bận, em thử lại sau nhé! (Lỗi chi tiết: {e})")

except Exception as e:
    st.error(f"Có lỗi khi đọc dữ liệu Excel: {e}")
