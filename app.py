import streamlit as st
import pandas as pd
import os
import google.generativeai as genai
import time
import json
import gspread
from google.oauth2.service_account import Credentials
import datetime

# --- HÀM GHI DỮ LIỆU LÊN GOOGLE SHEETS ---
def ghi_du_lieu_vao_sheets(loai_hoat_dong, ho_ten, lop, ket_qua, chi_tiet):
    try:
        if "GCP_CREDS" not in st.secrets or "SHEET_URL" not in st.secrets:
            return 
        
        creds_json = json.loads(st.secrets["GCP_CREDS"])
        scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
        creds = Credentials.from_service_account_info(creds_json, scopes=scopes)
        client = gspread.authorize(creds)
        
        sheet = client.open_by_url(st.secrets["SHEET_URL"]).sheet1
        thoi_gian = (datetime.datetime.utcnow() + datetime.timedelta(hours=7)).strftime("%d/%m/%Y %H:%M:%S")
        
        row = [thoi_gian, ho_ten, lop, loai_hoat_dong, ket_qua, chi_tiet]
        sheet.append_row(row)
    except Exception:
        pass 

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

st.set_page_config(page_title="PHY-LIFE 10", page_icon="🚀", layout="wide", initial_sidebar_state="expanded")

try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel('gemini-3.5-flash-lite')
    api_ready = True
except Exception:
    api_ready = False

st.markdown('''
<style>
    @import url('https://fonts.googleapis.com/css2?family=Quicksand:wght@400;500;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Quicksand', sans-serif !important; }
    .stApp { background-color: #FCFBF4; }
    .main-text { color: #1E293B; }
    [data-testid="stSidebar"] { background-color: #ffffff; border-right: 1px solid #e2e8f0; }
    .pretest-box { background-color: white; padding: 25px; border-radius: 15px; border: 2px solid #0D9488; box-shadow: 0 4px 6px rgba(13,148,136,0.1); margin-bottom: 20px;}
    .chat-box { background-color: #F8FAFC; padding: 20px; border-radius: 12px; border: 1px solid #CBD5E1; margin-top: 30px;}
</style>
''', unsafe_allow_html=True)

@st.cache_data
def load_data():
    xls = pd.ExcelFile('du_lieu_tinh_huong_dong_hoc_vat_li_10.xlsx')
    sheet_names = xls.sheet_names
    df_main = pd.read_excel(xls, sheet_name=sheet_names[0])
    df_pretest = pd.read_excel(xls, sheet_name='Du_lieu_Khoi_dong') if 'Du_lieu_Khoi_dong' in sheet_names else pd.DataFrame()
    return df_main, df_pretest

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.pretest_done = False
    st.session_state.student_name = ""
    st.session_state.student_class = ""
    st.session_state.student_level = "" 
    st.session_state.nav_page = "🏠 Cổng Khởi động"
    st.session_state.pretest_step = 1
    st.session_state.pretest_answers = {} 

st.sidebar.markdown("<h2 style='color: #0D9488; font-weight: 700;'>🚀 PHY-LIFE 10</h2>", unsafe_allow_html=True)

if not st.session_state.pretest_done:
    menu_list = ["🏠 Cổng Khởi động"]
else:
    if st.session_state.student_level in ["Khá giỏi", "Tốt"]:
        menu_list = ["📚 Khám phá Hiện tượng & AI"]
    else: 
        menu_list = ["📖 Ôn tập cốt lõi"]

selected_menu = st.sidebar.radio("CHUYÊN MỤC", menu_list, index=menu_list.index(st.session_state.nav_page) if st.session_state.nav_page in menu_list else 0)

if selected_menu != st.session_state.nav_page:
    st.session_state.nav_page = selected_menu
    st.rerun()

st.sidebar.markdown("---")

if st.session_state.logged_in:
    st.sidebar.success(f"👨‍🎓 Học sinh: **{st.session_state.student_name}**\n\n🏫 Lớp: **{st.session_state.student_class}**")
    if st.session_state.pretest_done:
        if st.session_state.student_level == "Cơ bản":
            st.sidebar.error("📊 Phân luồng: **Cần ôn tập cốt lõi**")
        else:
            st.sidebar.info("📊 Phân luồng: **Đã mở khóa Thư viện & AI**")

try:
    df_main, df_pretest = load_data()
    
    # 1. CỔNG KHỞI ĐỘNG
    if st.session_state.nav_page == "🏠 Cổng Khởi động":
        st.markdown("<h1 style='text-align: center; color: #0D9488;'>Chào mừng đến với PHY-LIFE 10!</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; font-size: 1.2rem; color: #64748b; margin-bottom: 2rem;'>Hệ thống học tập Vật lí thích ứng thông minh</p>", unsafe_allow_html=True)

        if not st.session_state.logged_in:
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                st.markdown("<div class='pretest-box'>", unsafe_allow_html=True)
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
            st.info("Hãy xem video và trả lời câu hỏi để hệ thống phân luồng (Yêu cầu: Đúng 100% để mở khóa).")
            if not df_pretest.empty:
                tong_so_cau = len(df_pretest)
                if st.session_state.pretest_step <= tong_so_cau:
                    cau_hien_tai = df_pretest.iloc[st.session_state.pretest_step - 1]
                    st.markdown(f"<div class='pretest-box'>", unsafe_allow_html=True)
                    video_src = str(cau_hien_tai['Video']).strip()
                    if video_src.startswith("http"):
                        st.video(video_src)
                    
                    st.markdown("---")
                    cac_lua_chon = [opt.strip() for opt in str(cau_hien_tai['Các lựa chọn']).split("|")]
                    tra_loi = st.radio(f"**Câu {st.session_state.pretest_step}:** {cau_hien_tai['Câu hỏi']}", cac_lua_chon, index=None)
                    
                    if st.button("Tiếp tục ➡️" if st.session_state.pretest_step < tong_so_cau else "Nộp bài 🔓", use_container_width=True):
                        if tra_loi:
                            st.session_state.pretest_answers[st.session_state.pretest_step] = tra_loi.startswith(str(cau_hien_tai['Đáp án đúng']).strip())
                            if st.session_state.pretest_step == tong_so_cau:
                                score = sum(st.session_state.pretest_answers.values())
                                if score == tong_so_cau:
                                    st.session_state.student_level = "Tốt"
                                    st.session_state.nav_page = "📚 Khám phá Hiện tượng & AI"
                                else:
                                    st.session_state.student_level = "Cơ bản"
                                    st.session_state.nav_page = "📖 Ôn tập cốt lõi"
                                ghi_du_lieu_vao_sheets("Pre-test (Chẩn đoán)", st.session_state.student_name, st.session_state.student_class, f"{score}/{tong_so_cau}", st.session_state.student_level)
                                st.session_state.pretest_done = True
                                st.rerun()
                            else:
                                st.session_state.pretest_step += 1
                                st.rerun()
                    st.markdown("</div>", unsafe_allow_html=True)

    # 2. ÔN TẬP CỐT LÕI & GIA SƯ SOCRATIC
    elif st.session_state.nav_page == "📖 Ôn tập cốt lõi":
        st.warning("Em chưa đạt 100%. Hãy nhờ Gia sư AI gợi ý để hiểu rõ bản chất nhé!")
        for index, row in df_pretest.iterrows():
            cau_so = index + 1
            st.markdown(f"<div class='pretest-box' style='border-left: 5px solid #f59e0b;'>", unsafe_allow_html=True)
            st.markdown(f"**Câu {cau_so}: {row['Câu hỏi']}**")
            with st.expander(f"🤖 Hỏi Gia sư AI về Câu {cau_so}"):
                chat_key = f"chat_q_{cau_so}"
                if chat_key not in st.session_state: st.session_state[chat_key] = []
                for msg in st.session_state[chat_key]:
                    with st.chat_message(msg["role"]): st.markdown(msg["content"])
                
                if prompt_hs := st.chat_input(f"Em chưa hiểu đoạn nào?", key=f"in_{cau_so}"):
                    st.session_state[chat_key].append({"role": "user", "content": prompt_hs})
                    with st.chat_message("user"): st.markdown(prompt_hs)
                    with st.chat_message("assistant"):
                        socratic_prompt = f"Bạn là Gia sư Socratic. Học sinh sai câu: '{row['Câu hỏi']}'. Đáp án là: '{row['Đáp án đúng']}'. TUYỆT ĐỐI KHÔNG cho đáp án trực tiếp, chỉ đặt 1 câu hỏi gợi mở. Xưng cô gọi em. Hỏi: {prompt_hs}"
                        res = model.generate_content(socratic_prompt).text
                        st.markdown(res)
                        st.session_state[chat_key].append({"role": "assistant", "content": res})
            st.markdown("</div>", unsafe_allow_html=True)
        
        if st.button("🔄 LÀM LẠI BÀI ĐỂ MỞ KHÓA", use_container_width=True):
            st.session_state.pretest_done = False
            st.session_state.pretest_step = 1
            st.session_state.nav_page = "🏠 Cổng Khởi động"
            st.rerun()

    # 3. THƯ VIỆN HIỆN TƯỢNG TÍCH HỢP CHATBOT
    elif st.session_state.nav_page == "📚 Khám phá Hiện tượng & AI":
        bai_hoc_chon = st.selectbox("📌 Chọn bài học:", df_main['Bài học liên quan'].unique())
        df_loc = df_main[df_main['Bài học liên quan'] == bai_hoc_chon]
        tinh_huong_chon = st.selectbox("🔍 Chọn tình huống:", df_loc['Tên tình huống'])
        
        ho_so = df_loc[df_loc['Tên tình huống'] == tinh_huong_chon].iloc[0]
        st.markdown(f"<h2 style='color: #1E293B;'>{ho_so['Tên tình huống']}</h2>", unsafe_allow_html=True)
        
        col_trai, col_phai = st.columns([1.1, 1])
        with col_trai:
            st.info(f"📍 **Bối cảnh:** {ho_so['Bối cảnh']}")
            if str(ho_so['Tên file ảnh']) != 'nan':
                st.image(os.path.join("images", str(ho_so['Tên file ảnh'])), use_container_width=True)
            st.markdown(f"**❓ {ho_so['Câu hỏi gợi mở']}**")
            cau_tra_loi_hs = st.text_area("Trả lời để mở khóa bài học:", key=f"ans_{tinh_huong_chon}")
            if st.button("🚀 Gửi AI duyệt"):
                res = model.generate_content(f"Học sinh trả lời: {cau_tra_loi_hs} cho câu hỏi: {ho_so['Câu hỏi gợi mở']}. Giải thích đúng là: {ho_so['Giải thích khoa học']}. Hãy nhận xét 2 câu. Xưng cô gọi em.").text
                st.session_state[f"ai_res_{tinh_huong_chon}"] = res
                st.session_state[f"unlocked_{tinh_huong_chon}"] = True
                ghi_du_lieu_vao_sheets("Trả lời Hiện tượng", st.session_state.student_name, st.session_state.student_class, "Hoàn thành", tinh_huong_chon)
            
            if st.session_state.get(f"ai_res_{tinh_huong_chon}"):
                st.success(f"🤖 **AI:** {st.session_state[f'ai_res_{tinh_huong_chon}']}")

        with col_phai:
            if st.session_state.get(f"unlocked_{tinh_huong_chon}"):
                st.markdown("### 📖 Giải thích khoa học")
                st.write(ho_so['Giải thích khoa học'])
                st.markdown("### 🧮 Công thức & Ví dụ")
                st.write(ho_so['Công thức'])
                st.write(ho_so['Ví dụ định lượng'])
            else:
                st.markdown("🔒 *Gửi câu trả lời để xem lời giải chi tiết.*")

        # KHUNG CHATBOT MỞ RỘNG TÍCH HỢP BÊN DƯỚI
        if st.session_state.get(f"unlocked_{tinh_huong_chon}"):
            st.markdown("<div class='chat-box'>", unsafe_allow_html=True)
            st.markdown("<h3 style='color: #0D9488;'>🤖 Khám phá sâu hơn cùng AI</h3>", unsafe_allow_html=True)
            st.markdown("Em muốn xin bài tập vận dụng về hiện tượng này, hay có thắc mắc gì thêm không?")
            
            chat_exp_key = f"chat_exp_{tinh_huong_chon}"
            if chat_exp_key not in st.session_state: st.session_state[chat_exp_key] = []
            
            for msg in st.session_state[chat_exp_key]:
                with st.chat_message(msg["role"]): st.markdown(msg["content"])
                
            if p := st.chat_input("Nhập câu hỏi mở rộng của em..."):
                st.session_state[chat_exp_key].append({"role": "user", "content": p})
                with st.chat_message("user"): st.markdown(p)
                with st.chat_message("assistant"):
                    prompt = f"Bạn là Nhà khám phá AI môn Vật lí. Đang hỗ trợ HS về tình huống: {tinh_huong_chon}. HS hỏi: {p}. Hãy giải thích, cho ví dụ hoặc tạo bài tập. Xưng cô gọi em."
                    ans = model.generate_content(prompt).text
                    st.markdown(ans)
                    st.session_state[chat_exp_key].append({"role": "assistant", "content": ans})
                    ghi_du_lieu_vao_sheets("Hỏi AI Mở rộng", st.session_state.student_name, st.session_state.student_class, "Hỏi thêm", p)
            st.markdown("</div>", unsafe_allow_html=True)

except Exception as e:
    st.error(f"Lỗi: {e}")
