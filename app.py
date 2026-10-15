import streamlit as st
import pandas as pd
import os

# 1. CẤU HÌNH TRANG WEB & MÀU SẮC TÙY CHỈNH
st.set_page_config(page_title="PHY-LIFE 10", page_icon="🚀", layout="wide", initial_sidebar_state="expanded")

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
    # Đọc tự động sheet đầu tiên, không lo bị lỗi "not found"
    df = pd.read_excel('du_lieu_tinh_huong_dong_hoc_vat_li_10.xlsx')
    return df

# 3. ĐIỀU HƯỚNG TRANG (ROUTING)
st.sidebar.markdown("<h2 style='color: #0D9488; font-weight: 700;'>🚀 PHY-LIFE 10</h2>", unsafe_allow_html=True)
menu = st.sidebar.radio("CHUYÊN MỤC", ["🏠 Trang chủ", "📚 Khám phá Hiện tượng", "🤖 Hỏi Nhà khám phá AI"])
st.sidebar.markdown("---")
st.sidebar.markdown("*Ứng dụng hỗ trợ học sinh lớp 10 học bộ sách Kết nối tri thức.*")

try:
    df = load_data()
    
    # ==========================================
    # GIAO DIỆN 1: TRANG CHỦ (Theo Wireframe)
    # ==========================================
    if menu == "🏠 Trang chủ":
        # KHU VỰC CHÀO MỪNG (Hero Section)
        col_text, col_img = st.columns([1.2, 1])
        
        with col_text:
            st.markdown("<br>", unsafe_allow_html=True) # Khoảng trắng
            st.markdown("""
            <div style="display: inline-block; padding: 4px 16px; background-color: #FEF08A; border-radius: 999px; font-weight: 700; font-size: 0.9rem; margin-bottom: 1rem;">
                ✨ Chương trình Lớp 10 Mới
            </div>
            <h1 style="font-size: 3.5rem; font-weight: 800; line-height: 1.2; margin-bottom: 1rem;">Vật lí quanh ta!</h1>
            <p style="font-size: 1.2rem; color: #475569; margin-bottom: 2rem;">
                Khám phá chuyển động trong đời sống. Quan sát hiện tượng, kết nối kiến thức và tự mình tìm ra lời giải.
            </p>
            """, unsafe_allow_html=True)
            
            # Nút bấm chuyển hướng (Trong Streamlit để chuyển trang mượt ta hướng dẫn người dùng bấm Sidebar)
            st.info("👈 **Hãy chọn '📚 Khám phá Hiện tượng' ở Menu bên trái để bắt đầu!**")

        with col_img:
            # Mô phỏng ô Sketchnote trong bản thiết kế
            st.markdown("""
            <div style="border: 2px dashed #1E293B; border-radius: 1rem; padding: 2rem; background-color: white; position: relative; margin-top: 2rem; text-align: center; box-shadow: 8px 8px 0px #FEF08A;">
                <h3 style="font-family: 'Caveat', cursive; color: #0D9488;">v = s / t</h3>
                <p style="color: #64748b;"><i>(Khu vực hiển thị ảnh minh họa)</i></p>
                <div style="font-size: 4rem;">🚴‍♂️ 💨</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<br><br><br>", unsafe_allow_html=True)
        
        # KHU VỰC THẺ TÍNH NĂNG (Feature Cards)
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
        
        # Bộ lọc
        col_loc1, col_loc2 = st.columns(2)
        with col_loc1:
            danh_sach_bai = df['Bài học liên quan'].unique()
            bai_hoc_chon = st.selectbox("📌 Chọn bài học:", danh_sach_bai)
        
        df_loc = df[df['Bài học liên quan'] == bai_hoc_chon]
        
        with col_loc2:
            tinh_huong_chon = st.selectbox("🔍 Chọn tình huống thực tiễn:", df_loc['Tên tình huống'])
        
        st.markdown("---")
        
        # Lấy dữ liệu hồ sơ
        ho_so = df_loc[df_loc['Tên tình huống'] == tinh_huong_chon].iloc[0]
        
        # Tiêu đề tình huống
        st.markdown(f"<h1 style='font-size: 2.2rem; margin-bottom: 1rem;'>{ho_so['Tên tình huống']}</h1>", unsafe_allow_html=True)
        
        col_trai, col_phai = st.columns([1.1, 1])
        
        with col_trai:
            st.info(f"📍 **Bối cảnh:** {ho_so['Bối cảnh']}")
            st.markdown(f"**Quan sát:** {ho_so['Mô tả quan sát']}")
            
            # Xử lý hiển thị ảnh
            ten_file_anh = str(ho_so['Tên file ảnh'])
            duong_dan_anh = os.path.join("images", ten_file_anh)
            
            if os.path.exists(duong_dan_anh):
                st.image(duong_dan_anh, use_container_width=True)
            else:
                st.warning(f"✍️ Đang chờ nét vẽ Sketchnote cho hiện tượng này... (Tên file cần có: {ten_file_anh})")
                
            st.markdown(f"**❓ Câu hỏi gợi mở:** *{ho_so['Câu hỏi gợi mở']}*")

        with col_phai:
            with st.container():
                st.markdown("<h3 style='color: #0D9488;'>Giải thích khoa học</h3>", unsafe_allow_html=True)
                st.write(ho_so['Giải thích khoa học'])
                
                st.markdown("<h3 style='color: #0D9488;'>Công thức vận dụng</h3>", unsafe_allow_html=True)
                # ĐÃ SỬA LỖI LA-TEX: Dùng st.markdown để nhận dạng chữ tiếng Việt và công thức xen kẽ
                st.markdown(ho_so['Công thức'])
                
                st.markdown("<h3 style='color: #0D9488;'>Ví dụ định lượng</h3>", unsafe_allow_html=True)
                st.write(ho_so['Ví dụ định lượng'])
                
                st.markdown("<h3 style='color: #0D9488;'>Thử thách tương tác</h3>", unsafe_allow_html=True)
                st.write(ho_so['Câu hỏi tương tác'])
                
                with st.expander("💡 Bấm vào đây để xem Gợi ý / Phản hồi"):
                    st.success(ho_so['Đáp án/phản hồi'])

    # ==========================================
    # GIAO DIỆN 3: AI CHAT (Sẽ phát triển sau)
    # ==========================================
    elif menu == "🤖 Hỏi Nhà khám phá AI":
        st.markdown("<h2 style='color: #0D9488;'>Nhà khám phá AI</h2>", unsafe_allow_html=True)
        st.info("Tính năng trò chuyện tương tác trực tiếp với mô hình Gemini AI đang được lắp ráp và sẽ sớm ra mắt. Em hãy quay lại sau nhé!")

except Exception as e:
    st.error(f"Có lỗi khi đọc dữ liệu Excel: {e}")
    st.write("Vui lòng kiểm tra lại file 'du_lieu_tinh_huong_dong_hoc_vat_li_10.xlsx' trên GitHub.")
