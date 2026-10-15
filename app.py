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

# Nhúng CSS tùy chỉnh
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Quicksand:wght@400;500;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Quicksand', sans-serif !important; }
    .stApp { background-color: #FCFBF4; }
    h1, h2, h3, h4, h5, h6, p, span, div { color: #1E293B; }
    [data-testid="stSidebar"] { background-color: #ffffff; border-right: 1px solid #e2e8f0; }
    .stAlert { border-radius: 1rem !important; border: none !important; }
    .phy-card { background-color: white; padding: 1.5rem; border-radius: 1rem; border: 1px solid #e2e8f0; box-shadow: 0 1px 3px rgba(0,0,0,0.1); transition: transform 0.3s, box-shadow 0.3s; height: 100%; }
    .phy-card:hover { transform: translateY(-5px); box-shadow: 0 10px 15px -3px rgba(0,0,0,0.1); border-color: #0D9488; }
    .icon-box { width: 50px; height: 50px; border-radius: 12px; display: flex; align-items: center; justify-content: center; font-size: 24px; margin-bottom: 15px; }
</style>
""", unsafe_allow_html=True)

# 2. ĐỌC DỮ LIỆU TỪ EXCEL
@st.cache_data
def load_data():
    df = pd.read_excel('du_lieu_tinh_huong_dong_hoc_vat_li_10.xlsx')
    return df

# 3. ĐIỀU HƯỚNG TRANG
st.sidebar.markdown("<h2 style='color: #0D9488; font-weight: 700;'>🚀 PHY-LIFE 10</h2>", unsafe_allow_html=True)
menu = st.sidebar.radio("CHUYÊN MỤC", ["🏠 Trang chủ", "📚 Khám phá Hiện tượng", "🤖 Hỏi Nhà khám phá AI"])
st.sidebar.markdown("---")
st.sidebar.markdown("*Ứng dụng hỗ trợ học sinh lớp 10 học bộ sách Kết nối tri thức.*")

if not api_ready:
    st.sidebar.warning("Vui lòng cấu hình GEMINI_API_KEY trong Settings > Secrets trên Streamlit Cloud để sử dụng tính năng AI.")

try:
    df = load_data()
    
    # === GIAO DIỆN 1: TRANG CHỦ ===
    if menu == "🏠 Trang chủ":
        col_text, col_img = st.columns([1.2, 1])
        with col_text:
            st.markdown("<br>", unsafe_allow_html=True) 
            st.markdown("""
            <div style="display: inline-block; padding: 4px 16px; background-color: #FEF08A; border-radius: 999px; font-weight: 700; font-size: 0.9rem; margin-bottom: 1rem;">
                ✨ Chương trình Lớp 10 Mới
            </div>
            <h1 style="font-size: 3.5rem; font-weight: 800; line-height: 1.2; margin-bottom: 1rem;">Vật lí quanh ta!</h1>
            <p style="font-size: 1.2rem; color: #475569; margin-bottom: 2rem;">
                Khám phá chuyển động trong đời sống. Quan sát hiện tượng, kết nối kiến thức và tự mình tìm ra lời giải.
            </p>
            """, unsafe_allow_html=True)
            st.info("👈 **Hãy chọn '📚 Khám phá Hiện tượng' ở Menu bên trái để bắt đầu!**")

        with col_img:
            st.markdown("""
            <div style="border: 2px dashed #1E293B; border-radius: 1rem; padding: 2rem; background-color: white; position: relative; margin-top: 2rem; text-align: center; box-shadow: 8px 8px 0px #FEF08A;">
                <h3 style="font-family: 'Caveat', cursive; color: #0D9488;">v = s / t</h3>
                <p style="color: #64748b;"><i>(Khu vực hiển thị ảnh minh họa)</i></p>
                <div style="font-size: 4rem;">🚴‍♂️ 💨</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<br><br><br>", unsafe_allow_html=True)
        st.markdown("<h2 style='text-align: center; margin-bottom: 2rem;'>Em muốn khám phá gì?</h2>", unsafe_allow_html=True)
        
        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown("""<div class="phy-card"><div class="icon-box" style="background-color: #EFF6FF; color: #3B82F6;">📖</div><h3 style="font-size: 1.25rem;">Theo bài học</h3><p style="color: #64748b; font-size: 0.95rem;">Ôn tập vận tốc, gia tốc và đồ thị chuyển động.</p></div>""", unsafe_allow_html=True)
        with c2:
            st.markdown("""<div class="phy-card"><div class="icon-box" style="background-color: #FEF08A; color: #A16207;">💡</div><h3 style="font-size: 1.25rem;">Theo hiện tượng</h3><p style="color: #64748b; font-size: 0.95rem;">Khám phá các tình huống giao thông, thể thao.</p></div>""", unsafe_allow_html=True)
        with c3:
            st.markdown("""<div class="phy-card"><div class="icon-box" style="background-color: #CCFBF1; color: #0D9488;">🤖</div><h3 style="font-size: 1.25rem;">Hỏi AI Khám phá</h3><p style="color: #64748b; font-size: 0.95rem;">Mổ xẻ hiện tượng Vật lí cùng trợ lý ảo.</p></div>""", unsafe_allow_html=True)

    # === GIAO DIỆN 2: THƯ VIỆN HIỆN TƯỢNG ===
    elif menu == "📚 Khám phá Hiện tượng":
        st.markdown("<h2 style='color: #0D9488;'>Thư viện Hiện tượng</h2>", unsafe_allow_html=True)
        
        col_loc1, col_loc2 = st.columns(2)
        with col_loc1:
            danh_sach_bai = df['Bài học liên quan'].unique()
            bai_hoc_chon = st.selectbox("📌 Chọn bài học:", danh_sach_bai)
        
        df_loc = df[df['Bài học liên quan'] == bai_hoc_chon]
        with col_loc2:
            tinh_huong_chon = st.selectbox("🔍 Chọn tình huống thực tiễn:", df_loc['Tên tình huống'])
        st.markdown("---")
        
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
            
            # --- AI PHÂN TÍCH NHANH ---
            st.markdown(f"""
            <div style="background-color: #F0FDF4; padding: 15px; border-radius: 10px; border-left: 5px solid #22C55E; margin-top: 20px; margin-bottom: 10px;">
                <h4 style="color: #15803D; margin-top: 0; display: flex; align-items: center; gap: 8px;">🤖 AI phân tích nhanh</h4>
                <p style="font-size: 0.95em; color: #1E293B; margin-bottom: 5px;"><strong>Dựa vào câu hỏi:</strong> <em>"{ho_so['Câu hỏi gợi mở']}"</em></p>
                <p style="font-size: 0.85em; color: #64748b;">Hãy nhập hoặc đọc câu trả lời, AI sẽ định hướng nhé!</p>
            </div>
            """, unsafe_allow_html=True)
            
            cau_tra_loi_hs = st.text_area("Câu trả lời của em:", height=80, placeholder="Gõ câu trả lời vào đây...")
            col_btn1, col_btn2 = st.columns([1, 1])
            with col_btn1:
                gui_ai = st.button("🚀 Gửi AI phân tích", use_container_width=True)
            with col_btn2:
                import streamlit.components.v1 as components
                components.html("""
                <!DOCTYPE html>
                <html>
                <head>
                <style>
                .btn {
                    width: 100%; padding: 0.5rem; background-color: #f1f5f9; border: 1px solid #cbd5e1; border-radius: 0.5rem; cursor: pointer; font-weight: 600; font-family: 'Quicksand', sans-serif; color: #334155; display: flex; align-items: center; justify-content: center; gap: 8px; box-sizing: border-box; font-size: 1rem; transition: background-color 0.3s;
                }
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
                    recognition.lang = "vi-VN";
                    recognition.start();
                    
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
