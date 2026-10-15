import streamlit as st
import pandas as pd
import os
import google.generativeai as genai

# 1. CẤU HÌNH TRANG WEB & MÀU SẮC TÙY CHỈNH
st.set_page_config(page_title="PHY-LIFE 10", page_icon="🚀", layout="wide", initial_sidebar_state="expanded")

# CẤU HÌNH GEMINI API TỪ STREAMLIT SECRETS
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel('gemini-1.5-flash')
    api_ready = True
except Exception as e:
    api_ready = False

# Nhúng CSS tùy chỉnh để giống bản Wireframe (Sử dụng màu Cream, Navy, Turquoise, font Quicksand)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Quicksand:wght@400;500;600;700&display=swap');
    
    /* Ép font chữ và màu nền chính */
    html, body, [class*="css"] {
        font-family: 'Quicksand', sans-serif !important;
    }
    
    /* Đổi màu nền app sang màu Cream (#FCFBF4) */
    .stApp {
        background-color: #FCFBF4;
    }
    
    /* Màu chữ chính Navy (#1E293B) */
    h1, h2, h3, h4, h5, h6, p, span, div {
        color: #1E293B;
    }
    
    /* Làm đẹp Sidebar */
    [data-testid="stSidebar"] {
        background-color: #ffffff;
        border-right: 1px solid #e2e8f0;
    }
    
    /* Tùy chỉnh các khối thông báo (st.info, st.success) */
    .stAlert {
        border-radius: 1rem !important;
        border: none !important;
    }
    
    /* Tạo style cho Thẻ (Card) */
    .phy-card {
        background-color: white;
        padding: 1.5rem;
        border-radius: 1rem;
        border: 1px solid #e2e8f0;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        transition: transform 0.3s, box-shadow 0.3s;
        height: 100%;
    }
    .phy-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 15px -3px rgba(0,0,0,0.1);
        border-color: #0D9488;
    }
    .icon-box {
        width: 50px; height: 50px; 
        border-radius: 12px;
        display: flex; align-items: center; justify-content: center;
        font-size: 24px; margin-bottom: 15px;
    }
</style>
""", unsafe_allow_html=True)

# 2. ĐỌC DỮ LIỆU TỪ EXCEL
@st.cache_data
def load_data():
    # Đọc tự động sheet đầu tiên
    df = pd.read_excel('du_lieu_tinh_huong_dong_hoc_vat_li_10.xlsx')
    return df

# 3. ĐIỀU HƯỚNG TRANG (ROUTING)
st.sidebar.markdown("<h2 style='color: #0D9488; font-weight: 700;'>🚀 PHY-LIFE 10</h2>", unsafe_allow_html=True)
menu = st.sidebar.radio("CHUYÊN MỤC", ["🏠 Trang chủ", "📚 Khám phá Hiện tượng", "🤖 Hỏi Nhà khám phá AI"])
st.sidebar.markdown("---")
st.sidebar.markdown("*Ứng dụng hỗ trợ học sinh lớp 10 học bộ sách Kết nối tri thức.*")

if not api_ready:
    st.sidebar.warning("Vui lòng cấu hình GEMINI_API_KEY trong Settings > Secrets trên Streamlit Cloud để sử dụng tính năng AI.")

try:
    df = load_data()
    
    # ==========================================
    # GIAO DIỆN 1: TRANG CHỦ (Theo Wireframe)
    # ==========================================
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
            st.markdown("""
            <div class="phy-card">
                <div class="icon-box" style="background-color: #EFF6FF; color: #3B82F6;">📖</div>
                <h3 style="font-size: 1.25rem;">Theo bài học</h3>
                <p style="color: #64748b; font-size: 0.95rem;">Ôn tập vận tốc, gia tốc và đồ thị chuyển động theo đúng bài học trên lớp.</p>
            </div>
            """, unsafe_allow_html=True)
        with c2:
            st.markdown("""
            <div class="phy-card">
                <div class="icon-box" style="background-color: #FEF08A; color: #A16207;">💡</div>
                <h3 style="font-size: 1.25rem;">Theo hiện tượng</h3>
                <p style="color: #64748b; font-size: 0.95rem;">Khám phá các tình huống giao thông, thể thao, thiên nhiên quanh em.</p>
            </div>
            """, unsafe_allow_html=True)
        with c3:
            st.markdown("""
            <div class="phy-card">
                <div class="icon-box" style="background-color: #CCFBF1; color: #0D9488;">🤖</div>
                <h3 style="font-size: 1.25rem;">Hỏi AI Khám phá</h3>
                <p style="color: #64748b; font-size: 0.95rem;">Đặt câu hỏi và mổ xẻ hiện tượng Vật lí theo từng bước cùng trợ lý ảo.</p>
            </div>
            """, unsafe_allow_html=True)

    # ==========================================
    # GIAO DIỆN 2: THƯ VIỆN HIỆN TƯỢNG
    # ==========================================
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
            
            # SỬ DỤNG ĐÚNG TÊN CỘT TỪ EXCEL: 'Tên file ảnh'
            ten_file_anh = str(ho_so['Tên file ảnh'])
            duong_dan_anh = os.path.join("images", ten_file_anh)
            
            if os.path.exists(duong_dan_anh):
                st.image(duong_dan_anh, use_container_width=True)
            else:
                st.warning(f"✍️ Đang chờ nét vẽ Sketchnote cho hiện tượng này... (Tên file cần có: {ten_file_anh})")
                
            st.markdown(f"**❓ Câu hỏi gợi mở:** *{ho_so['Câu hỏi gợi mở']}*")
            
            # --- CẬP NHẬT: AI ĐỊNH HƯỚNG THEO CÂU HỎI GỢI MỞ SỬ DỤNG GEMINI API ---
            st.markdown(f"""
            <div style="background-color: #F0FDF4; padding: 15px; border-radius: 10px; border-left: 5px solid #22C55E; margin-top: 20px; margin-bottom: 10px;">
                <h4 style="color: #15803D; margin-top: 0; display: flex; align-items: center; gap: 8px;">
                    🤖 AI phân tích nhanh
                </h4>
                <p style="font-size: 0.95em; color: #1E293B; margin-bottom: 5px;">
                    <strong>Dựa vào câu hỏi trên:</strong> <em>"{ho_so['Câu hỏi gợi mở']}"</em>
                </p>
                <p style="font-size: 0.85em; color: #64748b;">Em hãy nhập hoặc đọc câu trả lời, AI sẽ định hướng ngắn gọn nhé!</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Form nhập liệu cho phép gõ văn bản
            cau_tra_loi_hs = st.text_area("Câu trả lời của em:", height=80, placeholder="Gõ câu trả lời của em vào đây...")
            
            # Cột chức năng
            col_btn1, col_btn2 = st.columns([1, 1])
            with col_btn1:
                gui_ai = st.button("🚀 Gửi AI phân tích", use_container_width=True)
            with col_btn2:
                # Tính năng thu âm giọng nói (Speech-to-text)
                st.markdown("""
                <script>
                function startDictation() {
                  if (window.hasOwnProperty('webkitSpeechRecognition')) {
                    var recognition = new webkitSpeechRecognition();
                    recognition.continuous = false;
                    recognition.interimResults = false;
                    recognition.lang = "vi-VN";
                    recognition.start();
                    recognition.onresult = function(e) {
                      document.querySelector('textarea').value = e.results[0][0].transcript;
                      recognition.stop();
                    };
                    recognition.onerror = function(e) {
                      recognition.stop();
                    }
                  }
                }
                </script>
                <button onclick="startDictation()" style="width: 100%; padding: 0.5rem; background-color: #f1f5f9; border: 1px solid #cbd5e1; border-radius: 0.5rem; color: #334155; font-weight: 600; cursor: pointer; display: flex; align-items: center; justify-content: center; gap: 8px;">
                    🎤 Nhập bằng Giọng nói
                </button>
                """, unsafe_allow_html=True)

            if gui_ai:
                if cau_tra_loi_hs:
                    cau_tra_loi_lower = cau_tra_loi_hs.lower().strip()
                    
                    # 1. BỘ LỌC CỨNG (Fallback nhanh gọn)
                    if any(tu_khoa in cau_tra_loi_lower for tu_khoa in ["không biết", "chưa biết", "chịu", "khó quá", "không hiểu"]):
                         st.info(f"**🤖 Nhận xét nhanh:** Đừng lo lắng nhé! Vật lí đôi khi cần một chút gợi ý. Em hãy đọc chậm lại phần **'Quan sát'** và đối chiếu với **'Giải thích khoa học'** bên phải, em sẽ tìm ra câu trả lời ngay thôi!")
                    elif len(cau_tra_loi_lower) < 5:
                         st.warning(f"**🤖 Nhận xét nhanh:** Câu trả lời của em hơi ngắn. Em có thể giải thích rõ hơn một chút được không? Hoặc em xem thử phần **'Giải thích khoa học'** để có thêm ý tưởng nhé.")
                    else:
                         # 2. XỬ LÝ BẰNG GEMINI API NẾU ĐÃ CẤU HÌNH
                         if api_ready:
                             with st.spinner("AI đang suy nghĩ..."):
                                 prompt_ai = f"""
                                 Bạn là giáo viên Vật lí lớp 10, rất tâm lý và khích lệ học sinh.
                                 Học sinh đang học về tình huống: {ho_so['Tên tình huống']}.
                                 Câu hỏi đặt ra: {ho_so['Câu hỏi gợi mở']}
                                 Lời giải đúng theo lý thuyết: {ho_so['Giải thích khoa học']}
                                 Câu trả lời của học sinh: "{cau_tra_loi_hs}"
                                 
                                 Hãy phân tích câu trả lời của học sinh ngắn gọn trong 2-3 câu:
                                 - Nếu sai hoặc hiểu lầm: Nhẹ nhàng chỉnh sửa và hướng học sinh xem lại kiến thức.
                                 - Nếu có ý đúng: Khen ngợi và bổ sung cho hoàn chỉnh.
                                 Không giải bài tập hộ, ngôn ngữ thân thiện (gọi học sinh là "em", xưng "AI" hoặc "cô").
                                 """
                                 try:
                                     response = model.generate_content(prompt_ai)
                                     st.success(f"**🤖 AI phân tích:** {response.text}")
                                 except Exception as e:
                                      st.error("AI đang bận, em hãy thử lại sau nhé!")
                         else:
                             # Dự phòng nếu API Key chưa được cài đặt
                             st.success(f"**🤖 Nhận xét nhanh:** Câu trả lời '{cau_tra_loi_hs}' của em rất đáng ghi nhận! Để biết phân tích chi tiết, em hãy xem phần **'Giải thích khoa học'** bên phải nhé!")
                else:
                    st.warning("⚠️ Em hãy nhập câu trả lời trước khi gửi nhé!")

        with col_phai:
            with st.container():
                st.markdown("<h3 style='color: #0D9488;'>Giải thích khoa học</h3>", unsafe_allow_html=True)
                st.write(ho_so['Giải thích khoa học'])
                
                st.markdown("<h3 style='color: #0D9488;'>Công thức vận dụng</h3>", unsafe_allow_html=True)
                st.markdown(ho_so['Công thức'])
                
                st.markdown("<h3 style='color: #0D9488;'>Ví dụ định lượng</h3>", unsafe_allow_html=True)
                st.write(ho_so['Ví dụ định lượng'])
                
                st.markdown("<h3 style='color: #0D9488;'>Thử thách tương tác</h3>", unsafe_allow_html=True)
                # Thay thế ký tự xuống dòng
                st.markdown(str(ho_so['Câu hỏi tương tác']).replace('\\n', '\n\n'))
                
                with st.expander("💡 Bấm vào đây để xem Gợi ý / Phản hồi"):
                    st.success(str(ho_so['Đáp án/phản hồi']).replace('\\n', '\n\n'))
                
                # --- BỔ SUNG CÁC TRƯỜNG CÒN THIẾU TỪ EXCEL ---
                st.markdown("---") # Đường kẻ ngang
                st.markdown("<h4 style='color: #0D9488;'>🛠️ Hoạt động thực hành</h4>", unsafe_allow_html=True)
                st.info(ho_so['Hoạt động thực hành'])
                
                st.markdown("<h4 style='color: #0D9488;'>🏷️ Từ khóa</h4>", unsafe_allow_html=True)
                # Hiển thị từ khóa dưới dạng các thẻ nhỏ (tag)
                tu_khoa_list = str(ho_so['Từ khóa']).split(',')
                html_tu_khoa = ""
                for tag in tu_khoa_list:
                    html_tu_khoa += f"<span style='background-color: #E2E8F0; padding: 4px 8px; border-radius: 4px; margin-right: 5px; font-size: 0.85em;'>{tag.strip()}</span>"
                st.markdown(html_tu_khoa, unsafe_allow_html=True)
                
                st.markdown("<br><p style='font-size: 0.8em; color: #94A3B8;'><strong>Nguồn tham khảo:</strong> " + str(ho_so['Nguồn tham khảo']) + "</p>", unsafe_allow_html=True)

    # ==========================================
    # GIAO DIỆN 3: AI CHAT (Sẽ phát triển sau)
    # ==========================================
    elif menu == "🤖 Hỏi Nhà khám phá AI":
        st.markdown("<h2 style='color: #0D9488;'>Nhà khám phá AI</h2>", unsafe_allow_html=True)
        st.info("Tính năng trò chuyện tương tác trực tiếp với mô hình Gemini AI đang được lắp ráp và sẽ sớm ra mắt. Em hãy quay lại sau nhé!")

except Exception as e:
    st.error(f"Có lỗi khi đọc dữ liệu Excel: {e}")
