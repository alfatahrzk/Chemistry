import streamlit as st
import google.generativeai as genai
from PIL import Image
from streamlit_cropper import st_cropper

# 1. KONFIGURASI KUNCI API GEMINI
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
model = genai.GenerativeModel('gemini-2.5-flash')

# 2. PENGATURAN LAYOUT
st.set_page_config(layout="wide", page_title="ChemCompute Pro")
st.title("🧪 ChemCompute Pro: Asisten Kimia AI")

uploaded_file = st.file_uploader("Unggah foto soal kimia...", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    # Membuka gambar
    img = Image.open(uploaded_file)
    
    # --- FIX BUG SKALA: Resize gambar agar muat di layar tanpa terpotong ---
    # Kita tentukan lebar maksimal (misal 1000px) agar muat di kolom Streamlit
    max_width = 1000
    if img.width > max_width:
        ratio = max_width / float(img.width)
        new_height = int(float(img.height) * float(ratio))
        img = img.resize((max_width, new_height), Image.Resampling.LANCZOS)
    
    col1, col2 = st.columns([1.2, 0.8]) 
    
    with col1:
        st.subheader("Pilih Bagian Soal (Crop)")
        
        # Hapus 'use_container_width' karena menyebabkan error
        # Kita gunakan 'realtime_update' agar preview di kanan langsung muncul
        cropped_img = st_cropper(
            img, 
            realtime_update=True, 
            box_color='#007bff', 
            aspect_ratio=None
        )
        
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
            else:
                st.error("Silakan tentukan bagian gambar yang ingin dihitung.")
