import streamlit as st
import pandas as pd
import os
import google.generativeai as genai

# 1. CẤU HÌNH TRANG WEB & MÀU SẮC TÙY CHỈNH
st.set_page_config(page_title="PHY-LIFE 10", page_icon="🚀", layout="wide", initial_sidebar_state="expanded")

# CẤU HÌNH GEMINI API TỪ STREAMLIT SECRETS
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel('gemini-3.5-flash-lite')
    api_ready = True
except Exception as e:
    api_ready = False

# Nhúng CSS tùy chỉnh cho Game hóa (Gamification)
st.markdown('''
<style>
    @import url('https://fonts.googleapis.com/css2?family=Quicksand:wght@400;500;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Quicksand', sans-serif !important; }
    .stApp { background-color: #FCFBF4; }
    h1, h2, h3, h4, h5, h6, p, span, div { color: #1E293B; }
    [data-testid="stSidebar"] { background-color: #ffffff; border-right: 1px solid #e2e8f0; }
    .stAlert { border-radius: 1rem !important; border: none !important; }
    
    .phy-card {
        background-color: white;
        padding: 2rem 1.5rem;
        border-radius: 1rem;
        border: 1px solid #e2e8f0;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        transition: transform 0.3s, box-shadow 0.3s, border-color 0.3s;
        height: 100%;
        text-align: center;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
    }
    .phy-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 15px -3px rgba(0,0,0,0.1);
        border-color: #0D9488;
        background-color: #F0FDFA;
    }
    .icon-box {
        width: 60px; height: 60px; 
        border-radius: 16px;
        display: flex; align-items: center; justify-content: center;
        font-size: 28px; margin-bottom: 15px;
    }
    
    /* Giao diện Thẻ trạm game */
    .game-station {
        background: linear-gradient(135deg, #0D9488 0%, #0F766E 100%);
        color: white;
        padding: 20px;
        border-radius: 16px;
        text-align: center;
        box-shadow: 0 10px 15px -3px rgba(13, 148, 136, 0.3);
        margin-bottom: 20px;
    }
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
                <!DOCTYPE html>
                <html>
                <head>
                <style>
                .btn { width: 100%; padding: 0.5rem; background-color: #f1f5f9; border: 1px solid #cbd5e1; border-radius: 0.5rem; cursor: pointer; font-weight: 600; font-family: 'Quicksand', sans-serif; color: #334155; display: flex; align-items: center; justify-content: center; gap: 8px; box-sizing: border-box; font-size: 1rem; transition: background-color 0.3s; }
                .btn:hover { background-color: #e2e8f0; }
                </style>
                </head>
                <body style="margin: 0; overflow: hidden;">
                <button class="btn" onclick="startDictation()">🎤 Nhập bằng Giọng nói</button>
                <script>
                function startDictation() {
                  if (window.hasOwnProperty('webkitSpeechRecognition') || window.hasOwnProperty('SpeechRecognition')) {
                    var SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
                    var recognition = new SpeechRecognition();
                    recognition.lang = "vi-VN"; recognition.start();
                    
                    var btn = document.querySelector('.btn');
                    btn.innerHTML = "🔴 Đang nghe... (Hãy nói đi)";
                    btn.style.backgroundColor = "#fee2e2";
                    btn.style.color = "#991b1b";
                    btn.style.borderColor = "#fca5a5";
                    
                    recognition.onresult = function(e) {
                        var text = e.results[0][0].transcript;
                        var textarea = window.parent.document.querySelector('textarea');
                        if(textarea) {
                            var nativeInputValueSetter = Object.getOwnPropertyDescriptor(window.parent.HTMLTextAreaElement.prototype, "value").set;
                            nativeInputValueSetter.call(textarea, text);
                            var ev2 = new Event('input', { bubbles: true});
                            textarea.dispatchEvent(ev2);
                        }
                        btn.innerHTML = "🎤 Nhập bằng Giọng nói";
                        btn.style.backgroundColor = "#f1f5f9";
                        btn.style.color = "#334155";
                        btn.style.borderColor = "#cbd5e1";
                        recognition.stop();
                    };
                    recognition.onerror = function(e) {
                        btn.innerHTML = "🎤 Nhập bằng Giọng nói";
                        btn.style.backgroundColor = "#f1f5f9";
                        btn.style.color = "#334155";
                        btn.style.borderColor = "#cbd5e1";
                        recognition.stop();
                        alert("Không nghe rõ. Vui lòng thử lại!");
                    }
                  } else {
                    alert("Trình duyệt không hỗ trợ, hãy dùng Chrome nhé!");
                  }
                }
                </script>
                </body>
                </html>
                ''', height=45)

            if gui_ai:
                if cau_tra_loi_hs:
                    st.session_state.da_tra_loi = True
                    if api_ready:
                        with st.spinner("AI đang suy nghĩ..."):
                            prompt_ai = f'''
                            Bạn là cô giáo dạy Vật lí lớp 10, rất tâm lý và khích lệ học sinh.
                            Tình huống: {ho_so['Tên tình huống']}.
                            Câu hỏi đặt ra: {ho_so['Câu hỏi gợi mở']}.
                            Lời giải đúng: {ho_so['Giải thích khoa học']}.
                            Học sinh vừa trả lời: "{cau_tra_loi_hs}".
                            
                            Hãy viết 1 đoạn nhận xét ngắn gọn (khoảng 2-3 câu):
                            - Nếu học sinh nói không biết, từ bỏ, hoặc đùa giỡn: Nhẹ nhàng nhắc nhở, động viên.
                            - Nếu trả lời sai: Chỉnh sửa nhẹ nhàng.
                            - Nếu trả lời có ý đúng: Khen ngợi.
                            Quy tắc BẮT BUỘC: 
                            1. Xưng là "cô", gọi học sinh là "em".
                            2. Bất kể học sinh trả lời đúng hay sai, CÂU CHỐT CUỐI CÙNG LUÔN LÀ: "Em hãy xem phần 'Giải thích khoa học' bên cạnh để hiểu rõ hơn nhé!"
                            '''
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
                    html_tu_khoa = "".join([f"<span style='background-color: #E2E8F0; padding: 4px 8px; border-radius: 4px; margin-right: 5px; font-size: 0.85em;'>{tag.strip()}</span>" for tag in tu_khoa_list])
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

    # === GIAO DIỆN MỚI: BẢN ĐỒ THỬ THÁCH (MINI-GAME VƯỢT ẢI) ===
    elif st.session_state.nav_page == "🎮 Bản đồ Thử thách (Game)":
        st.markdown("<h2 style='color: #0D9488;'>🎮 Trạm Thử Thách Động Học - Vượt Ải Nhận Điểm Thưởng</h2>", unsafe_allow_html=True)
        st.markdown("Hành trình chinh phục Vật lí lớp 10 qua 4 thử thách tương tác: Trắc nghiệm, Ghép nối khái niệm, Điền khuyết công thức và Xử lý tình huống thực tế.")
        st.markdown("---")

        # Khởi tạo điểm số trong game
        if "game_score" not in st.session_state:
            st.session_state.game_score = 0

        # Chia các trạm thử thách thành các tab (Tabs)
        tab1, tab2, tab3, tab4 = st.tabs(["🎯 Thử thách 1: Trắc nghiệm nhanh", "🔗 Thử thách 2: Ghép nối hiện tượng", "✍️ Thử thách 3: Điền khuyết công thức", "🚀 Thử thách 4: Giải quyết tình huống"])

        with tab1:
            st.markdown("<div class='game-station'><h3>Trạm 1: Phản xạ nhanh cùng Gia tốc & Vận tốc</h3></div>", unsafe_allow_html=True)
            
            q1 = st.radio("Câu hỏi 1: Khi một chiếc xe máy đang đứng yên bắt đầu tăng tốc độ chuyển động trên đường, vectơ gia tốc của xe có hướng như thế nào so với vectơ vận tốc?", 
                          ["A. Hướng ngược chiều với vận tốc.", "B. Hướng cùng chiều với vận tốc.", "C. Vuông góc với phương chuyển động.", "D. Bằng không vì xe chưa chạy ổn định."])
            
            if st.button("Kiểm tra đáp án Trạm 1", key="check_q1"):
                if "B." in q1:
                    st.success("🎉 Chính xác! Trong chuyển động nhanh dần đều (tăng tốc), gia tốc và vận tốc luôn cùng chiều.")
                    st.session_state.game_score += 10
                else:
                    st.error("❌ Chưa chính xác. Em hãy nhớ lại: Tăng tốc nghĩa là gia tốc thúc đẩy vận tốc tăng lên, nên chúng phải cùng chiều nhé!")

        with tab2:
            st.markdown("<div class='game-station'><h3>Trạm 2: Ghép nối Hiện tượng với Loại chuyển động</h3></div>", unsafe_allow_html=True)
            
            col_g1, col_g2 = st.columns(2)
            with col_g1:
                hien_tuong = st.selectbox("Chọn hiện tượng thực tiễn:", ["Trực thăng thả hàng cứu trợ mùa lũ", "Chùm chìa khóa rơi từ hành lang tầng 3", "Xe máy bóp phanh gấp trước ngã tư"])
            with col_g2:
                loai_cd = st.selectbox("Ghép với loại chuyển động tương ứng:", ["Chuyển động chậm dần đều", "Chuyển động rơi tự do", "Chuyển động ném ngang"])

            if st.button("Xác nhận ghép nối", key="check_q2"):
                if (hien_tuong.startswith("Trực thăng") and loai_cd.endswith("ném ngang")) or \
                   (hien_tuong.startswith("Chùm chìa") and loai_cd.endswith("rơi tự do")) or \
                   (hien_tuong.startswith("Xe máy") and loai_cd.startswith("Chuyển động chậm")):
                    st.success("🏆 Ghép đôi hoàn hảo! Em đã hiểu sâu sắc bản chất chuyển động.")
                    st.session_state.game_score += 15
                else:
                    st.error("❌ Chưa đúng rồi. Em hãy đọc lại mô hình vật lí của từng hiện tượng nhé!")

        with tab3:
            st.markdown("<div class='game-station'><h3>Trạm 3: Thử thách Điền khuyết Công thức Động học</h3></div>", unsafe_allow_html=True)
            
            st.markdown("Điền biểu thức đúng cho công thức tính quãng đường trong chuyển động thẳng nhanh dần đều (với $v_0 = 0$):")
            dap_an_dien = st.text_input("Nhập công thức của em (ví dụ: 0.5*a*t**2 hoặc 1/2*a*t^2):")
            
            if st.button("Nộp bài Trạm 3", key="check_q3"):
                if "0.5*a*t" in dap_an_dien or "1/2" in dap_an_dien or "0.5 * a" in dap_an_dien:
                    st.success("⭐ Tuyệt vời! Công thức $s = \frac{1}{2}at^2$ hoàn toàn chính xác.")
                    st.session_state.game_score += 15
                else:
                    st.error("❌ Chưa đúng. Công thức đầy đủ là s bằng một nửa gia tốc nhân với bình phương thời gian.")

        with tab4:
            st.markdown("<div class='game-station'><h3>Trạm 4: Thách thức Pháp y Giao thông (Tình huống mới)</h3></div>", unsafe_allow_html=True)
            st.write("Một ô tô để lại vết trượt bánh dài 20m trên mặt đường trước khi dừng hẳn. Biết gia tốc hãm phanh của xe là $a = -5 m/s^2$. Em hãy tính vận tốc ban đầu của xe trước khi phanh bằng cách nhập số vào ô dưới:")
            
            v_input = st.number_input("Nhập vận tốc tính được (đơn vị m/s):", min_value=0.0, step=1.0)
            if st.button("Phá giải vụ án", key="check_q4"):
                # Công thức: v^2 - v0^2 = 2as => 0 - v0^2 = 2*(-5)*20 => v0^2 = 200 => v0 = sqrt(200) ≈ 14.14 m/s
                if 13.5 <= v_input <= 14.5:
                    st.success("🕵️‍♂️ Xuất sắc! Em đã vận dụng công thức độc lập thời gian $v^2 - v_0^2 = 2as$ để phá án chính xác tuyệt đối (vận tốc xấp xỉ 14.14 m/s hay ~51 km/h).")
                    st.session_state.game_score += 20
                else:
                    st.error("❌ Chưa chính xác. Gợi ý công thức: $v^2 - v_0^2 = 2as$ (với $v = 0$, $s = 20$, $a = -5$). Em hãy tính lại nhé!")

        st.markdown("<br><hr>", unsafe_allow_html=True)
        col_sc1, col_sc2 = st.columns([2, 1])
        with col_sc1:
            st.info(f"🏆 **Tổng điểm thành tích tích lũy của em:** **{st.session_state.game_score} Điểm**")
        with col_sc2:
            if st.button("🔄 Chơi lại từ đầu", use_container_width=True):
                st.session_state.game_score = 0
                st.rerun()

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
                        history_context = ""
                        for msg in st.session_state.chat_messages[-5:-1]:
                            role_name = "Học sinh" if msg["role"] == "user" else "Cô giáo"
                            history_context += f"{role_name}: {msg['content']}\n"
                            
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
