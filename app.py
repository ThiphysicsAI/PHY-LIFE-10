import streamlit as st
import pandas as pd
import os
import google.generativeai as genai

# 1. CAU HINH TRANG WEB & MAU SAC TUY CHINH
st.set_page_config(page_title="PHY-LIFE 10", page_icon="🚀", layout="wide", initial_sidebar_state="expanded")

# CAU HINH GEMINI API TU STREAMLIT SECRETS
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel('gemini-3.5-flash-lite')
    api_ready = True
except Exception as e:
    api_ready = False

# Nhung CSS tuy chinh
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

# 2. DOC DU LIEU TU EXCEL
@st.cache_data
def load_data():
    df = pd.read_excel('du_lieu_tinh_huong_dong_hoc_vat_li_10.xlsx')
    return df

# 3. DIEU HUONG TRANG
st.sidebar.markdown("<h2 style='color: #0D9488; font-weight: 700;'>🚀 PHY-LIFE 10</h2>", unsafe_allow_html=True)
menu = st.sidebar.radio("CHUYEN MUC", ["🏠 Trang chu", "📚 Kham pha Hien tuong", "🤖 Hoi Nha kham pha AI"])
st.sidebar.markdown("---")
st.sidebar.markdown("*Ung dung ho tro hoc sinh lop 10 hoc bo sach Ket noi tri thuc.*")

if not api_ready:
    st.sidebar.warning("Vui long cau hinh GEMINI_API_KEY trong Settings > Secrets tren Streamlit Cloud de su dung tinh nang AI.")

try:
    df = load_data()
    
    # === GIAO DIEN 1: TRANG CHU ===
    if menu == "🏠 Trang chu":
        col_text, col_img = st.columns([1.2, 1])
        with col_text:
            st.markdown("<br>", unsafe_allow_html=True) 
            st.markdown("""
            <div style="display: inline-block; padding: 4px 16px; background-color: #FEF08A; border-radius: 999px; font-weight: 700; font-size: 0.9rem; margin-bottom: 1rem;">
                ✨ Chuong trinh Lop 10 Moi
            </div>
            <h1 style="font-size: 3.5rem; font-weight: 800; line-height: 1.2; margin-bottom: 1rem;">Vat li quanh ta!</h1>
            <p style="font-size: 1.2rem; color: #475569; margin-bottom: 2rem;">
                Kham pha chuyen dong trong doi song. Quan sat hien tuong, ket noi kien thuc va tu minh tim ra loi giai.
            </p>
            """, unsafe_allow_html=True)
            st.info("👈 **Hay chon '📚 Kham pha Hien tuong' o Menu ben trai de bat dau!**")

        with col_img:
            st.markdown("""
            <div style="border: 2px dashed #1E293B; border-radius: 1rem; padding: 2rem; background-color: white; position: relative; margin-top: 2rem; text-align: center; box-shadow: 8px 8px 0px #FEF08A;">
                <h3 style="font-family: 'Caveat', cursive; color: #0D9488;">v = s / t</h3>
                <p style="color: #64748b;"><i>(Khu vuc hien thi anh minh hoa)</i></p>
                <div style="font-size: 4rem;">🚴‍♂️ 💨</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<br><br><br>", unsafe_allow_html=True)
        st.markdown("<h2 style='text-align: center; margin-bottom: 2rem;'>Em muon kham pha gi?</h2>", unsafe_allow_html=True)
        
        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown("""<div class="phy-card"><div class="icon-box" style="background-color: #EFF6FF; color: #3B82F6;">📖</div><h3 style="font-size: 1.25rem;">Theo bai hoc</h3><p style="color: #64748b; font-size: 0.95rem;">On tap van toc, gia toc va do thi chuyen dong.</p></div>""", unsafe_allow_html=True)
        with c2:
            st.markdown("""<div class="phy-card"><div class="icon-box" style="background-color: #FEF08A; color: #A16207;">💡</div><h3 style="font-size: 1.25rem;">Theo hien tuong</h3><p style="color: #64748b; font-size: 0.95rem;">Kham pha cac tinh huong giao thong, the thao.</p></div>""", unsafe_allow_html=True)
        with c3:
            st.markdown("""<div class="phy-card"><div class="icon-box" style="background-color: #CCFBF1; color: #0D9488;">🤖</div><h3 style="font-size: 1.25rem;">Hoi AI Kham pha</h3><p style="color: #64748b; font-size: 0.95rem;">Mo xe hien tuong Vat li cung tro ly ao.</p></div>""", unsafe_allow_html=True)

    # === GIAO DIEN 2: THU VIEN HIEN TUONG ===
    elif menu == "📚 Kham pha Hien tuong":
        st.markdown("<h2 style='color: #0D9488;'>Thu vien Hien tuong</h2>", unsafe_allow_html=True)
        
        col_loc1, col_loc2 = st.columns(2)
        with col_loc1:
            danh_sach_bai = df['Bài học liên quan'].unique()
            bai_hoc_chon = st.selectbox("📌 Chon bai hoc:", danh_sach_bai)
        
        df_loc = df[df['Bài học liên quan'] == bai_hoc_chon]
        with col_loc2:
            tinh_huong_chon = st.selectbox("🔍 Chon tinh huong thuc tien:", df_loc['Tên tình huống'])
        st.markdown("---")
        
        ho_so = df_loc[df_loc['Tên tình huống'] == tinh_huong_chon].iloc[0]
        st.markdown(f"<h1 style='font-size: 2.2rem; margin-bottom: 1rem;'>{ho_so['Tên tình huống']}</h1>", unsafe_allow_html=True)
        
        col_trai, col_phai = st.columns([1.1, 1])
        with col_trai:
            st.info(f"📍 **Boi canh:** {ho_so['Bối cảnh']}")
            st.markdown(f"**Quan sat:** {ho_so['Mô tả quan sát']}")
            
            ten_file_anh = str(ho_so['Tên file ảnh'])
            duong_dan_anh = os.path.join("images", ten_file_anh)
            if os.path.exists(duong_dan_anh):
                st.image(duong_dan_anh, use_container_width=True)
            else:
                st.warning(f"✍️ Dang cho net ve Sketchnote... (Ten file: {ten_file_anh})")
                
            st.markdown(f"**❓ Cau hoi goi mo:** *{ho_so['Câu hỏi gợi mở']}*")
            
            # --- AI PHAN TICH NHANH ---
            st.markdown(f"""
            <div style="background-color: #F0FDF4; padding: 15px; border-radius: 10px; border-left: 5px solid #22C55E; margin-top: 20px; margin-bottom: 10px;">
                <h4 style="color: #15803D; margin-top: 0; display: flex; align-items: center; gap: 8px;">🤖 AI phan tich nhanh</h4>
                <p style="font-size: 0.95em; color: #1E293B; margin-bottom: 5px;"><strong>Dua vao cau hoi:</strong> <em>"{ho_so['Câu hỏi gợi mở']}"</em></p>
                <p style="font-size: 0.85em; color: #64748b;">Hay nhap hoac doc cau tra loi, AI se dinh huong nhe!</p>
            </div>
            """, unsafe_allow_html=True)
            
            cau_tra_loi_hs = st.text_area("Cau tra loi cua em:", height=80, placeholder="Go cau tra loi vao day...")
            col_btn1, col_btn2 = st.columns([1, 1])
            with col_btn1:
                gui_ai = st.button("🚀 Gui AI phan tich", use_container_width=True)
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
                <button class="btn" onclick="startDictation()">🎤 Nhap bang Giong noi</button>
                <script>
                function startDictation() {
                  if (window.hasOwnProperty('webkitSpeechRecognition') || window.hasOwnProperty('SpeechRecognition')) {
                    var SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
                    var recognition = new SpeechRecognition();
                    recognition.lang = "vi-VN";
                    recognition.start();
                    
                    var btn = document.querySelector('.btn');
                    btn.innerHTML = "🔴 Dang nghe... (Hay noi di)";
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
                        btn.innerHTML = "🎤 Nhap bang Giong noi";
                        btn.style.backgroundColor = "#f1f5f9";
                        btn.style.color = "#334155";
                        btn.style.borderColor = "#cbd5e1";
                        recognition.stop();
                    };
                    recognition.onerror = function(e) {
                        btn.innerHTML = "🎤 Nhap bang Giong noi";
                        btn.style.backgroundColor = "#f1f5f9";
                        btn.style.color = "#334155";
                        btn.style.borderColor = "#cbd5e1";
                        recognition.stop();
                        alert("Khong nghe ro. Vui long thu lai!");
                    }
                  } else {
                    alert("Trinh duyet khong ho tro, dung Chrome nhe!");
                  }
                }
                </script>
                </body>
                </html>
                """, height=45)

            if gui_ai:
                if cau_tra_loi_hs:
                    if api_ready:
                        with st.spinner("AI dang suy nghi..."):
                            # PROMPT ĐÃ ĐƯỢC CẬP NHẬT ĐỂ AI LUÔN NHẤN MẠNH PHẦN GIẢI THÍCH
                            prompt_ai = f"""
                            Bạn là cô giáo dạy Vật lí lớp 10, rất tâm lý và khích lệ học sinh.
                            Tình huống: {ho_so['Tên tình huống']}.
                            Câu hỏi đặt ra: {ho_so['Câu hỏi gợi mở']}.
                            Lời giải đúng: {ho_so['Giải thích khoa học']}.
                            Học sinh vừa trả lời: "{cau_tra_loi_hs}".
                            
                            Hãy viết 1 đoạn nhận xét ngắn gọn (khoảng 2-3 câu):
                            - Nếu học sinh nói không biết, từ bỏ, hoặc đùa giỡn (như 'alo alo'): Nhẹ nhàng nhắc nhở, động viên.
                            - Nếu trả lời sai: Chỉnh sửa nhẹ nhàng.
                            - Nếu trả lời có ý đúng: Khen ngợi.
                            Quy tắc BẮT BUỘC: 
                            1. Xưng là "cô", gọi học sinh là "em".
                            2. Bất kể học sinh trả lời đúng hay sai, CÂU CHỐT CUỐI CÙNG LUÔN LÀ: "Em hãy xem phần 'Giải thích khoa học' bên cạnh để hiểu rõ hơn nhé!"
                            """
                            try:
                                response = model.generate_content(prompt_ai)
                                st.success(f"**🤖 AI phân tích:** {response.text}")
                            except Exception as e:
                                st.error(f"AI dang ban, thu lai sau nhe! (Loi: {e})")
                    else:
                        st.warning("Tinh nang AI chua duoc kich hoat (Thieu API Key).")
                else:
                    st.warning("⚠️ Hay nhap cau tra loi truoc khi gui!")

        with col_phai:
            with st.container():
                st.markdown("<h3 style='color: #0D9488;'>Giai thich khoa hoc</h3>", unsafe_allow_html=True)
                st.write(ho_so['Giải thích khoa học'])
                st.markdown("<h3 style='color: #0D9488;'>Cong thuc van dung</h3>", unsafe_allow_html=True)
                st.markdown(ho_so['Công thức'])
                st.markdown("<h3 style='color: #0D9488;'>Vi du dinh luong</h3>", unsafe_allow_html=True)
                st.write(ho_so['Ví dụ định lượng'])
                st.markdown("<h3 style='color: #0D9488;'>Thu thach tuong tac</h3>", unsafe_allow_html=True)
                st.markdown(str(ho_so['Câu hỏi tương tác']).replace('\\n', '\n\n'))
                with st.expander("💡 Bam vao day de xem Goi y / Phan hoi"):
                    st.success(str(ho_so['Đáp án/phản hồi']).replace('\\n', '\n\n'))
                
                st.markdown("---")
                st.markdown("<h4 style='color: #0D9488;'>🛠️ Hoat dong thuc hanh</h4>", unsafe_allow_html=True)
                st.info(ho_so['Hoạt động thực hành'])
                st.markdown("<h4 style='color: #0D9488;'>🏷️ Tu khoa</h4>", unsafe_allow_html=True)
                
                tu_khoa_list = str(ho_so['Từ khóa']).split(',')
                html_tu_khoa = "".join([f"<span style='background-color: #E2E8F0; padding: 4px 8px; border-radius: 4px; margin-right: 5px; font-size: 0.85em;'>{tag.strip()}</span>" for tag in tu_khoa_list])
                st.markdown(html_tu_khoa, unsafe_allow_html=True)
                st.markdown("<br><p style='font-size: 0.8em; color: #94A3B8;'><strong>Nguon tham khao:</strong> " + str(ho_so['Nguồn tham khảo']) + "</p>", unsafe_allow_html=True)

    # === GIAO DIEN 3: AI CHAT ===
    elif menu == "🤖 Hoi Nha kham pha AI":
        st.markdown("<h2 style='color: #0D9488;'>Nha kham pha AI</h2>", unsafe_allow_html=True)
        st.info("Tinh nang AI Chat dang duoc hoan thien.")

except Exception as e:
    st.error(f"Co loi khi doc du lieu Excel: {e}")
