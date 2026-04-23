import streamlit as st
import google.generativeai as genai
from PIL import Image
from streamlit_cropper import st_cropper
import os

# 1. KONFIGURASI KUNCI API GEMINI
# Ganti dengan API Key Gemini kamu sendiri!
os.environ["GOOGLE_API_KEY"] = "AIzaSyBIpMzkOH4mg9ySvf1ZRzOXOEwO9CmWwyk"
genai.configure(api_key=os.environ["GOOGLE_API_KEY"])

# Inisialisasi Model Gemini Vision
model = genai.GenerativeModel('gemini-pro-vision')

# 2. PENGATURAN LAYOUT STREAMLIT
st.set_page_config(layout="wide", page_title="ChemCompute Pro")
st.title("🧪 ChemCompute Pro: Asisten Kimia AI")

# Sidebar untuk navigasi
st.sidebar.header("Fitur")
app_mode = st.sidebar.selectbox("Pilih Mode", ["Photo Solver", "Tabel Periodik", "Referensi Formula"])

if app_mode == "Photo Solver":
    st.header("📸 Selesaikan Soal Lewat Foto")
    
    # 3. FITUR UNGGAH GAMBAR
    uploaded_file = st.file_uploader("Unggah foto soal kimia...", type=["jpg", "jpeg", "png"])
    
    if uploaded_file is not None:
        img = Image.open(uploaded_file)
        
        col1, col2 = st.columns([1, 1]) # Membuat dua kolom
        
        with col1:
            st.subheader("Pilih Bagian Soal (Crop)")
            # 4. FITUR CROP INTERAKTIF (streamlit-cropper)
            # Menampilkan gambar dan mengambil hasil crop
            cropped_img = st_cropper(img, realtime_update=True, box_color='#007bff', aspect_ratio=None)
            
            # Tombol untuk memicu perhitungan
            hitung_btn = st.button("Lakukan Perhitungan")

        with col2:
            st.subheader("Analisis & Solusi AI")
            
            if hitung_btn:
                if cropped_img:
                    with st.spinner("Gemini sedang menganalisis soal..."):
                        # 5. MENGIRIM GAMBAR KE GEMINI
                        # Prompt khusus agar Gemini menjawab rinci
                        prompt = (
                            "Analisis gambar soal kimia ini. Pertama, tulis ulang teks soalnya. "
                            "Kemudian, berikan penjelasan konsep kimia yang relevan, tuliskan rumus yang digunakan dalam format LaTeX, "
                            "tunjukkan langkah-langkah perhitungan secara rinci beserta unitnya, dan berikan jawaban akhir yang jelas."
                        )
                        
                        # Memanggil Gemini Vision
                        response = model.generate_content([prompt, cropped_img])
                        
                        # 6. MENAMPILKAN HASIL DARI AI
                        st.markdown("### Hasil Perhitungan Gemini AI")
                        st.markdown(response.text) # Gemini akan mengembalikan format Markdown/LaTeX
                        
                        # Menampilkan gambar yang di-crop sebagai referensi
                        st.image(cropped_img, caption="Bagian soal yang dianalisis.", use_column_width=True)
                else:
                    st.error("Silakan crop bagian gambar soal terlebih dahulu.")
