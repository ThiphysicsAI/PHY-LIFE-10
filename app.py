import streamlit as st
import pandas as pd
import google.generativeai as genai
import gspread
from google.oauth2.service_account import Credentials
import json
import datetime

# 1. CẤU HÌNH GIAO DIỆN TỐI GIẢN (Dải màu navy-teal, thẻ bo góc tròn)
st.set_page_config(page_title="PHY-LIFE 10", page_icon="🚀", layout="centered")

st.markdown('''
<style>
    @import url('https://fonts.googleapis.com/css2?family=Quicksand:wght@400;500;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Quicksand', sans-serif !important; }
    
    /* Phông nền pastel nhẹ nhàng giảm mỏi mắt */
    .stApp { background: linear-gradient(135deg, #f8fafc 0%, #e0f2fe 100%); }
    
    /* Thiết kế thẻ bo tròn */
    .main-card { 
        background-color: white; 
        padding: 2rem; 
        border-radius: 1.5rem; 
        box-shadow: 0 10px 25px rgba(13, 148, 136, 0.08); 
        margin-bottom: 1.5rem; 
        border-top: 5px solid #0d9488; 
    }
    
    h1, h2, h3 { color: #0f172a; font-weight: 700; }
    p, span, label { color: #334155; font-size: 1.05rem; }
    
    /* Nút bấm navy-teal */
    .stButton>button { 
        border-radius: 1rem; 
        background-color: #0d9488; 
        color: white; 
        font-weight: 600; 
        border: none; 
        padding: 0.5rem 2rem;
        transition: all 0.3s;
    }
    .stButton>button:hover { background-color: #0f766e; transform: translateY(-2px); box-shadow: 0 4px 12px rgba(13, 148, 136, 0.2); }
</style>
''', unsafe_allow_html=True)

# 2. HÀM QUẢN TRỊ ZERO-TOUCH (Tự động ghi Google Sheets)
def ghi_du_lieu_vao_sheets(ho_ten, lop, hoat_dong, ket_qua, chi_tiet):
    try:
        if "GCP_CREDS" not in st.secrets or "SHEET_URL" not in st.secrets: 
            return
        
        creds_json = json.loads(st.secrets["GCP_CREDS"])
        scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
        creds = Credentials.from_service_account_info(creds_json, scopes=scopes)
        client = gspread.authorize(creds)
        
        sheet = client.open_by_url(st.secrets["SHEET_URL"]).sheet1
        thoi_gian = (datetime.datetime.utcnow() + datetime.timedelta(hours=7)).strftime("%d/%m/%Y %H:%M:%S")
        
        sheet.append_row([thoi_gian, ho_ten, lop, hoat_dong, ket_qua, chi_tiet])
    except Exception:
        pass # Lỗi kết nối sẽ được bỏ qua ngầm để không gián đoạn luồng học của học sinh

# 3. KẾT NỐI NGÂN HÀNG DỮ LIỆU EXCEL
@st.cache_data
def load_pretest_data():
    try:
        # Chỉ cần tải duy nhất 1 sheet Pre-test
        df = pd.read_excel('du_lieu_tinh_huong_dong_hoc_vat_li_10.xlsx', sheet_name='Pre-test')
        return df
    except Exception:
        return pd.DataFrame()

# Khởi tạo trạng thái phiên làm việc
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.student_name = ""
    st.session_state.student_class = ""
