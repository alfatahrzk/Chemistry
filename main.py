import streamlit as st
import google.generativeai as genai
from PIL import Image
from streamlit_cropper import st_cropper

# 1. KONFIGURASI KUNCI API GEMINI
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
model = genai.GenerativeModel('gemini-1.5-flash')

# 2. PENGATURAN LAYOUT
st.set_page_config(layout="wide", page_title="ChemCompute Pro")
st.title("🧪 ChemCompute Pro: Asisten Kimia AI")

uploaded_file = st.file_uploader("Unggah foto soal kimia...", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    # Membuka gambar dan memastikan rotasi benar (berdasarkan metadata EXIF)
    img = Image.open(uploaded_file)
    
    # Perbaikan Bug: Gunakan columns untuk membagi space
    col1, col2 = st.columns([1.2, 0.8]) 
    
    with col1:
        st.subheader("Pilih Bagian Soal (Crop)")
        
        # --- FIX BUG DI SINI ---
        # use_container_width=True: Memaksa canvas mengikuti lebar kolom
        # aspect_ratio=None: Memungkinkan crop bebas (tidak kaku kotak)
        cropped_img = st_cropper(
            img, 
            realtime_update=True, 
            box_color='#007bff', 
            aspect_ratio=None,
            use_container_width=True 
        )
        # ------------------------
        
        hitung_btn = st.button("Lakukan Perhitungan", use_container_width=True)

    with col2:
        st.subheader("Analisis & Solusi AI")
        if hitung_btn:
            if cropped_img:
                with st.spinner("Gemini sedang menganalisis..."):
                    prompt = (
                        "Analisis gambar soal kimia ini. Tulis ulang soalnya, "
                        "jelaskan konsepnya, berikan rumus dalam LaTeX, dan langkah perhitungan rinci."
                    )
                    response = model.generate_content([prompt, cropped_img])
                    
                    st.markdown("### Hasil Perhitungan")
                    st.markdown(response.text)
                    st.image(cropped_img, caption="Area yang dianalisis", width=250)
