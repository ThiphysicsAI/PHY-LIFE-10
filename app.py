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

# 1. CẤU HÌNH TRANG WEB
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
    .pretest-box { background-color: white; padding: 25px; border-radius: 15px; border: 2px solid #0D9488; box-shadow: 0 4px 6px rgba(13,148,136,0.1); margin-bottom: 20px;}
    .socratic-box { border-left: 5px solid #f59e0b; background-color: #fffbeb; padding: 20px; border-radius: 10px; margin-bottom: 20px;}
</style>
''', unsafe_allow_html=True)

# 2. ĐỌC DỮ LIỆU TỪ EXCEL (TỰ ĐỘNG HÓA HOÀN TOÀN)
@st.cache_data
def load_data():
    xls = pd.ExcelFile('du_lieu_tinh_huong_dong_hoc_vat_li_10.xlsx')
    sheet_names = xls.sheet_names
    df_main = pd.read_excel(xls, sheet_name=sheet_names[0])
    df_pretest = pd.read_excel(xls, sheet_name='Du_lieu_Khoi_dong') if 'Du_lieu_Khoi_dong' in sheet_names else pd.DataFrame()
    return df_main, df_pretest

# 3. TRẠNG THÁI HỆ THỐNG
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.student_name = ""
    st.session_state.student_class = ""
    st.session_state.pretest_done = False
    st.session_state.nav_page = "🏠 Chẩn đoán & Sửa lỗi"
    st.session_state.pretest_answers = {} 
    st.session_state.wrong_questions = []

st.sidebar.markdown("<h2 style='color: #0D9488; font-weight: 700;'>🚀 PHY-LIFE 10</h2>", unsafe_allow_html=True)

menu_list = ["🏠 Chẩn đoán & Sửa lỗi", "🌍 Khám phá Thực tiễn"] if st.session_state.pretest_done else ["🏠 Chẩn đoán & Sửa lỗi"]
selected_menu = st.sidebar.radio("CHUYÊN MỤC", menu_list)
if selected_menu != st.session_state.nav_page:
    st.session_state.nav_page = selected_menu
    st.rerun()

st.sidebar.markdown("---")
if st.session_state.logged_in:
    st.sidebar.success(f"👨‍🎓 **{st.session_state.student_name}** | 🏫 **{st.session_state.student_class}**")

if not api_ready:
    st.sidebar.warning("⚠️ API Key chưa được cấu hình.")

try:
    df_main, df_pretest = load_data()
    
    # ==========================================
    # LUỒNG 1: CHẨN ĐOÁN & GIA SƯ SOCRATIC
    # ==========================================
    if st.session_state.nav_page == "🏠 Chẩn đoán & Sửa lỗi":
        st.markdown("<h1 style='text-align: center; color: #0D9488;'>Hệ thống Chẩn đoán Thích ứng</h1>", unsafe_allow_html=True)

        if not st.session_state.logged_in:
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                st.markdown("<div class='pretest-box'><h3 style='text-align: center;'>Đăng nhập</h3>", unsafe_allow_html=True)
                name_input = st.text_input("Họ và Tên:")
                class_input = st.text_input("Lớp (VD: 10A1):")
                if st.button("Bắt đầu 🚀", use_container_width=True):
                    if name_input and class_input:
                        st.session_state.student_name = name_input
                        st.session_state.student_class = class_input
                        st.session_state.logged_in = True
                        st.rerun()
                st.markdown("</div>", unsafe_allow_html=True)

        elif not st.session_state.pretest_done:
            st.info("Hãy hoàn thành bài kiểm tra để hệ thống phân tích năng lực của em.")
            with st.form("pretest_form"):
                for idx, row in df_pretest.iterrows():
                    st.markdown(f"**Câu {idx+1}: {row['Câu hỏi']}**")
                    if pd.notna(row['Video']):
                        vid = str(row['Video']).strip()
                        if vid.startswith("http"): st.video(vid)
                        else:
                            p = os.path.join("images", vid)
                            if os.path.exists(p): st.video(p)
                    
                    opts = [opt.strip() for opt in str(row['Các lựa chọn']).split("|")]
                    st.session_state.pretest_answers[idx] = st.radio("Chọn đáp án:", opts, key=f"q_{idx}", index=None)
                    st.markdown("---")
                
                submitted = st.form_submit_button("Nộp bài & Phân luồng", use_container_width=True)
                if submitted:
                    missing = [i for i in range(len(df_pretest)) if st.session_state.pretest_answers[i] is None]
                    if missing:
                        st.warning("⚠️ Em cần chọn đáp án cho tất cả các câu!")
                    else:
                        st.session_state.wrong_questions = []
                        correct_count = 0
                        for idx, row in df_pretest.iterrows():
                            ans = st.session_state.pretest_answers[idx]
                            if ans and ans.startswith(str(row['Đáp án đúng']).strip()):
                                correct_count += 1
                            else:
                                st.session_state.wrong_questions.append({
                                    "idx": idx, "q": row['Câu hỏi'], "opts": row['Các lựa chọn'],
                                    "ans": row['Đáp án đúng'], "user_ans": ans
                                })
                        
                        score = f"{correct_count}/{len(df_pretest)}"
                        st.session_state.pretest_done = True
                        ghi_du_lieu_vao_sheets("Pre-test", st.session_state.student_name, st.session_state.student_class, score, "Hoàn thành")
                        st.rerun()

        else:
            if not st.session_state.wrong_questions:
                st.success("🎉 Xuất sắc! Em đã làm đúng 100%. Hãy chuyển sang tab **Khám phá Thực tiễn** để tiếp tục!")
            else:
                st.error(f"📊 Em làm sai {len(st.session_state.wrong_questions)} câu. Hãy cùng Gia sư AI sửa lỗi ngay bên dưới nhé!")
                
                for wq in st.session_state.wrong_questions:
                    st.markdown(f"<div class='socratic-box'>", unsafe_allow_html=True)
                    st.markdown(f"#### 🎯 Câu {wq['idx']+1}: {wq['q']}")
                    st.markdown(f"❌ Đáp án em chọn: **{wq['user_ans']}**")
                    
                    chat_key = f"soc_chat_{wq['idx']}"
                    if chat_key not in st.session_state:
                        st.session_state[chat_key] = []
                    
                    for msg in st.session_state[chat_key]:
                        with st.chat_message(msg["role"]): st.markdown(msg["content"])
                    
                    prompt_hs = st.chat_input(f"Nhắn cho Gia sư AI để tìm hiểu vì sao em sai câu {wq['idx']+1}...", key=f"inp_{wq['idx']}")
                    if prompt_hs:
                        st.session_state[chat_key].append({"role": "user", "content": prompt_hs})
                        with st.chat_message("user"): st.markdown(prompt_hs)
                        
                        with st.chat_message("assistant"):
                            with st.spinner("Gia sư đang phân tích..."):
                                history = "".join([f"{'HS' if m['role']=='user' else 'AI'}: {m['content']}\n" for m in st.session_state[chat_key][-4:]])
                                prompt = f'''
                                [KỶ LUẬT THÉP] Bạn là Gia sư Vật lí 10. Học sinh làm sai câu: "{wq['q']}". Đáp án đúng là: "{wq['ans']}".
                                QUY TẮC:
                                1. KHÔNG nói thẳng đáp án.
                                2. Dùng phương pháp Socratic đặt câu hỏi gợi mở.
                                3. BẮT BUỘC lồng ghép 1 VÍ DỤ THỰC TIỄN trong đời sống (xe cộ, thể thao...) để giải thích bản chất vật lí trước khi hỏi.
                                Lịch sử: {history}
                                HS hỏi: {prompt_hs}
                                '''
                                try:
                                    res = model.generate_content(prompt).text
                                    st.markdown(res)
                                    st.session_state[chat_key].append({"role": "assistant", "content": res})
                                except Exception as e:
                                    st.error(f"Lỗi kết nối AI: {e}")
                    st.markdown("</div>", unsafe_allow_html=True)
                
                if st.button("🔄 Làm lại bài kiểm tra", use_container_width=True):
                    st.session_state.pretest_done = False
                    st.session_state.pretest_answers = {}
                    st.rerun()

    # ==========================================
    # LUỒNG 2: KHÁM PHÁ THỰC TIỄN & CHATBOT ĐA NĂNG
    # ==========================================
    elif st.session_state.nav_page == "🌍 Khám phá Thực tiễn":
        st.markdown("<h2 style='color: #0D9488;'>Thư viện Hiện tượng & Nhà Khám phá AI</h2>", unsafe_allow_html=True)
        st.info("Chọn một hiện tượng bên dưới để nghiên cứu. Em có thể trò chuyện trực tiếp với AI về hiện tượng này hoặc yêu cầu AI tạo bài tập vận dụng mới!")
        
        tinh_huong = st.selectbox("🔍 Chọn tình huống thực tiễn:", df_main['Tên tình huống'])
        ho_so = df_main[df_main['Tên tình huống'] == tinh_huong].iloc[0]
        
        col1, col2 = st.columns([1.2, 1])
        with col1:
            st.markdown(f"### {ho_so['Tên tình huống']}")
            st.write(f"📍 **Bối cảnh:** {ho_so['Bối cảnh']}")
            st.write(f"👁️ **Quan sát:** {ho_so['Mô tả quan sát']}")
            img = str(ho_so['Tên file ảnh']).strip()
            if os.path.exists(os.path.join("images", img)):
                if img.endswith(('.mp4', '.mov')): st.video(os.path.join("images", img))
                else: st.image(os.path.join("images", img), use_container_width=True)
        
        with col2:
            st.markdown("### 🤖 Trò chuyện cùng AI")
            chat_exp_key = f"chat_exp_{tinh_huong}"
            if chat_exp_key not in st.session_state:
                st.session_state[chat_exp_key] = [{"role": "assistant", "content": f"Chào em! Dựa vào hiện tượng '{tinh_huong}', em muốn cô giải thích thêm, hay muốn thử sức với một bài tập thực tế tương tự?"}]
            
            chat_container = st.container(height=400)
            with chat_container:
                for msg in st.session_state[chat_exp_key]:
                    with st.chat_message(msg["role"]): st.markdown(msg["content"])
                    
            prompt = st.chat_input("Nhập câu hỏi hoặc yêu cầu bài tập...", key="exp_inp")
            if prompt:
                st.session_state[chat_exp_key].append({"role": "user", "content": prompt})
                with chat_container:
                    with st.chat_message("user"): st.markdown(prompt)
                    with st.chat_message("assistant"):
                        with st.spinner("AI đang suy nghĩ..."):
                            sys_prompt = f'''
                            Bạn là cô giáo Vật lí. Đang hỗ trợ học sinh về tình huống: "{tinh_huong}".
                            Giải thích khoa học gốc: "{ho_so['Giải thích khoa học']}".
                            Nhiệm vụ: Giải đáp thắc mắc, lật ngược vấn đề, hoặc tạo bài tập định lượng thực tế theo yêu cầu của học sinh. Xưng "cô", gọi "em".
                            Học sinh hỏi: "{prompt}"
                            '''
                            try:
                                res = model.generate_content(sys_prompt).text
                                st.markdown(res)
                                st.session_state[chat_exp_key].append({"role": "assistant", "content": res})
                                ghi_du_lieu_vao_sheets("Hỏi AI Thực tiễn", st.session_state.student_name, st.session_state.student_class, "Tương tác", f"Chủ đề: {tinh_huong} | Hỏi: {prompt}")
                            except Exception as e:
                                st.error(f"Lỗi: {e}")

except Exception as e:
    st.error(f"Lỗi hệ thống: {e}")
