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
    
    /* Giao diện Game */
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
                            prompt_ai = f'''Bạn là cô giáo dạy Vật lí lớp 10, khích lệ học sinh. Tình huống: {ho_so['Tên tình huống']}. Câu hỏi: {ho_so['Câu hỏi gợi mở']}. Giải thích đúng: {ho_so['Giải thích khoa học']}. HS trả lời: "{cau_tra_loi_hs}". Nhận xét 2-3 câu: nếu không biết/đùa giỡn thì động viên; sai thì sửa; đúng thì khen. Xưng "cô", gọi "em". BẮT BUỘC CHỐT CÂU CUỐI: "Em hãy xem phần 'Giải thích khoa học' bên cạnh để hiểu rõ hơn nhé!"'''
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
                st.markdown('''<div style="background-color: #f8fafc; border: 2px dashed #cbd5e1; border-radius: 10px; padding: 40px 20px; text-align: center; margin-top: 20px;"><div style="font-size: 3.5rem; margin-bottom: 15px;">🔒</div><h3 style="color: #64748b; margin-top: 0;">Nội dung đang khóa</h3><p style="color: #94a3b8; font-size: 1.05em; max-width: 90%; margin: 0 auto;">Em hãy suy nghĩ và <strong>Gửi AI phân tích</strong> câu trả lời ở cột bên trái để mở khóa nhé!</p></div>''', unsafe_allow_html=True)

    # === GIAO DIỆN 3: BẢN ĐỒ THỬ THÁCH (ĐIỆP VỤ PHYSIX) ===
    elif st.session_state.nav_page == "🎮 Bản đồ Thử thách (Game)":
        if 'station' not in st.session_state:
            st.session_state.station = 1
            st.session_state.play_sound = False
            
        st.markdown("<div class='game-title'>🕵️‍♂️ Điệp vụ PHYSIX: Mật mã Động học</div>", unsafe_allow_html=True)
        st.markdown("<div class='game-warning'>🚨 CẢNH BÁO: Tàu tốc hành đang mất phanh. Các đặc vụ 12A7 cần giải mã 4 trạm điều khiển để kích hoạt hệ thống phanh khẩn cấp!</div>", unsafe_allow_html=True)
        
        # Thanh tiến trình
        progress_val = int(((st.session_state.station - 1) / 4) * 100)
        st.markdown(f"**Mức độ giải mã hệ thống: {progress_val}%**")
        st.progress((st.session_state.station - 1) / 4)
        
        # Phát âm thanh khi qua trạm
        if st.session_state.play_sound:
            sound_html = '<audio autoplay><source src="https://assets.mixkit.co/active_storage/sfx/2013/2013-preview.mp3" type="audio/mpeg"></audio>'
            st.markdown(sound_html, unsafe_allow_html=True)
            st.session_state.play_sound = False

        if st.session_state.station == 1:
            st.markdown("<div class='game-station'><h3>Trạm 1: Không Lưu</h3></div>", unsafe_allow_html=True)
            st.markdown("<div class='mission-box'>**Nhiệm vụ:** Một vận động viên nhảy dù nhảy khỏi máy bay. Sau khi bung dù một lúc, người đó rơi xuống mặt đất với vận tốc không đổi. Hiện tượng này được giải thích bằng khái niệm nào?<br><br> * A. Gia tốc rơi tự do giảm dần.<br> * B. Quán tính triệt tiêu trọng lực.<br> * C. Lực cản không khí cân bằng với trọng lực.<br> * D. Động năng ban đầu đã tiêu hao hết.</div>", unsafe_allow_html=True)
            
            ans1 = st.radio("Chọn đáp án để trích xuất mã kích hoạt:", ["Chưa chọn", "A", "B", "C", "D"])
            if st.button("Xác nhận mã Trạm 1", use_container_width=True):
                if ans1 == "C":
                    st.success("✅ Hệ thống ghi nhận mã: 4. Đã mở khóa Trạm 2!")
                    st.session_state.play_sound = True
                    time.sleep(1) 
                    st.session_state.station = 2
                    st.rerun()
                else:
                    st.error("❌ Truy cập bị từ chối. Tàu vẫn đang lao dốc!")

        elif st.session_state.station == 2:
            st.markdown("<div class='game-station'><h3>Trạm 2: Động Cơ</h3></div>", unsafe_allow_html=True)
            st.markdown("<div class='mission-box'>**Nhiệm vụ:** Ghép đặc điểm đồ thị v-t với chuyển động thực tế của xe buýt.<br> 1. Đạp phanh (D)<br> 2. Dừng chờ đèn đỏ (A)<br> 3. Nhấn ga khởi hành (C)<br> 4. Chạy ổn định trên cao tốc (B)<br><br> *Thông điệp ẩn từ hệ thống:* <code>(D + A) x (C - B)</code>. Biết rằng D=5, A=3, C=4, B=3.</div>", unsafe_allow_html=True)
            
            ans2 = st.text_input("Nhập mật mã số học (1 chữ số):")
            if st.button("Xác nhận mã Trạm 2", use_container_width=True):
                if ans2 == "8":
                    st.success("✅ Hệ thống ghi nhận mã: 8. Đã mở khóa Trạm 3!")
                    st.session_state.play_sound = True
                    time.sleep(1)
                    st.session_state.station = 3
                    st.rerun()
                else:
                    st.error("❌ Sai mã số. Động cơ đang quá tải!")

        elif st.session_state.station == 3:
            st.markdown("<div class='game-station'><h3>Trạm 3: Ảo Giác</h3></div>", unsafe_allow_html=True)
            st.markdown("<div class='mission-box'>**Nhiệm vụ:** Thả thùng hàng từ máy bay đang bay ngang. Xác định Đúng (1) / Sai (0):<br> * [ ] Người đứng trên đảo thấy quỹ đạo thẳng đứng.<br> * [ ] Phi công thấy quỹ đạo thẳng đứng.<br> * [ ] Bay nhanh hơn thì rơi chạm đất lâu hơn.<br> * [ ] Ngay trước khi chạm đất, vận tốc ngang vẫn bằng vận tốc máy bay lúc thả.<br><br> *Chuyển chuỗi Đúng/Sai thành mã nhị phân 4 bít, sau đó dịch sang hệ thập phân.*</div>", unsafe_allow_html=True)
            
            ans3 = st.text_input("Nhập mã thập phân tương ứng:")
            if st.button("Xác nhận mã Trạm 3", use_container_width=True):
                if ans3 == "5":
                    st.success("✅ Hệ thống ghi nhận mã: 5. Đã mở khóa Trạm cuối!")
                    st.session_state.play_sound = True
                    time.sleep(1)
                    st.session_state.station = 4
                    st.rerun()
                else:
                    st.error("❌ Lỗi hệ quy chiếu. Hãy tính lại chuỗi nhị phân 0101!")

        elif st.session_state.station == 4:
            st.markdown("<div class='game-station'><h3>Trạm 4: Bứt Tốc</h3></div>", unsafe_allow_html=True)
            st.markdown("<div class='mission-box'>**Nhiệm vụ:** Băng chuyền sân bay di chuyển 1 m/s. An đi bộ trên băng chuyền với tốc độ 2 m/s so với băng chuyền. Vali của An bị bỏ quên, trôi theo băng chuyền cách An 14m phía trước.<br>Hỏi An mất bao nhiêu giây để bắt kịp vali?</div>", unsafe_allow_html=True)
            
            ans4 = st.text_input("Nhập thời gian (giây):")
            if st.button("KÍCH HOẠT PHANH KHẨN CẤP 🛑", use_container_width=True):
                if ans4 == "7":
                    st.success("✅ Hệ thống ghi nhận mã: 7.")
                    st.session_state.play_sound = True
                    time.sleep(1)
                    st.session_state.station = 5
                    st.rerun()
                else:
                    st.error("❌ Cảnh báo va chạm cận kề!")

        elif st.session_state.station == 5:
            st.balloons()
            st.markdown("<div style='background-color: #dcfce7; padding: 30px; border-radius: 15px; text-align: center; border: 2px solid #22c55e;'><h1 style='color: #166534; font-size: 3rem;'>🎉 PHANH KÍCH HOẠT THÀNH CÔNG!</h1><h3 style='color: #15803d;'>KIỆN HÀNG TRI THỨC ĐÃ ĐƯỢC BẢO VỆ.</h3><h2 style='color: #b91c1c; margin-top: 20px;'>Mã bí mật toàn chiến dịch: 4 - 8 - 5 - 7</h2></div>", unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("🔄 Chơi lại từ đầu", use_container_width=True):
                st.session_state.station = 1
                st.rerun()

    # === GIAO DIỆN 4: AI CHAT ===
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
                        sys_prompt = f'''Bạn là "Nhà khám phá Vật lí", chuyên gia sư phạm hướng dẫn học sinh lớp 10 (chương Động học). Xử lý câu hỏi của học sinh: "{prompt}". Lịch sử: {history_context}. Yêu cầu: Giải thích hiện tượng, tìm hiện tượng theo khái niệm, phân tích tình huống mới, tạo bài tập vận dụng, hoặc đặt câu hỏi gợi mở. Xưng "cô", gọi "em", ngôn ngữ thân thiện.'''
                        try:
                            response = model.generate_content(sys_prompt)
                            st.markdown(response.text)
                            st.session_state.chat_messages.append({"role": "assistant", "content": response.text})
                        except Exception as e:
                            st.error(f"Hệ thống đang bận, em thử lại sau nhé! (Lỗi: {e})")

except Exception as e:
    st.error(f"Có lỗi khi đọc dữ liệu Excel: {e}")
