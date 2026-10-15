import streamlit as st
import pandas as pd
import os

# 1. CẤU HÌNH TRANG WEB
st.set_page_config(page_title="PHY-LIFE 10", page_icon="🚀", layout="wide")
st.title("🚀 PHY-LIFE 10 - KẾT NỐI VẬT LÍ VỚI CUỘC SỐNG")
st.markdown("*Ứng dụng hỗ trợ học sinh lớp 10 khám phá hiện tượng Vật lí từ thực tiễn.*")

# 2. ĐỌC DỮ LIỆU TỪ EXCEL
@st.cache_data # Lưu cache để web chạy nhanh hơn
def load_data():
    # Đọc sheet chứa dữ liệu (thay tên sheet nếu cần, mặc định pandas đọc sheet đầu tiên hoặc chỉ định sheet_name)
    df = pd.read_excel('du_lieu_tinh_huong_dong_hoc_vat_li_10.xlsx', sheet_name='Du_lieu_45')
    return df

try:
    df = load_data()
    # 3. THIẾT KẾ MENU THANH BÊN (SIDEBAR)
    st.sidebar.title("Danh mục")
    menu = st.sidebar.radio("Chọn chức năng:", ["📚 Thư viện hiện tượng", "🤖 Trợ lý AI Khám phá"])

    if menu == "📚 Thư viện hiện tượng":
        st.header("Khám phá các hiện tượng")
        
        # Tạo thanh chọn bài học
        danh_sach_bai = df['Bài học liên quan'].unique()
        bai_hoc_chon = st.selectbox("Chọn bài học:", danh_sach_bai)
        
        # Lọc dữ liệu theo bài học đã chọn
        df_loc = df[df['Bài học liên quan'] == bai_hoc_chon]
        
        # Chọn tình huống
        tinh_huong_chon = st.selectbox("Chọn tình huống thực tiễn:", df_loc['Tên tình huống'])
        
        # Lấy chi tiết hồ sơ của tình huống đã chọn
        ho_so = df_loc[df_loc['Tên tình huống'] == tinh_huong_chon].iloc[0]
        
        # 4. HIỂN THỊ NỘI DUNG (Ảnh & Thông tin)
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.subheader(ho_so['Tên tình huống'])
            st.info(f"**Bối cảnh:** {ho_so['Bối cảnh']}")
            
            # Hiển thị ảnh sketchnote
            ten_file_anh = str(ho_so['Gợi ý hình ảnh/video'])
            duong_dan_anh = os.path.join("images", ten_file_anh)
            
            if os.path.exists(duong_dan_anh):
                st.image(duong_dan_anh, use_container_width=True, caption=ho_so['Mô tả quan sát'])
            else:
                st.warning(f"Đang chờ nét vẽ Sketchnote cho hiện tượng này...")

        with col2:
            st.markdown("### Giải thích khoa học")
            st.write(ho_so['Giải thích khoa học'])
            
            st.markdown("### Công thức vận dụng")
            # Hiển thị công thức Toán học định dạng LaTeX
            st.latex(ho_so['Công thức'])
            
            st.markdown("### Câu hỏi tương tác")
            st.write(ho_so['Câu hỏi tương tác'])
            
            with st.expander("Bấm vào đây để xem Đáp án / Phản hồi"):
                st.success(ho_so['Đáp án/phản hồi'])

    elif menu == "🤖 Trợ lý AI Khám phá":
        st.header("Trò chuyện với Nhà khám phá Vật lí")
        st.info("Chức năng tích hợp AI đang được cấu hình...")
        # Ở các bước sau, chúng ta sẽ lắp mã Gemini API vào đây

except Exception as e:
    st.error(f"Có lỗi khi đọc dữ liệu: {e}")
