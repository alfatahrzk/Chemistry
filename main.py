import streamlit as st
import google.generativeai as genai
from PIL import Image
from streamlit_cropper import st_cropper

# 1. KONFIGURASI KUNCI API GEMINI
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
model = genai.GenerativeModel('gemini-2.5-flash')

# 2. PENGATURAN LAYOUT (Tetap Wide untuk fleksibilitas desktop, tapi urutan kode vertikal)
st.set_page_config(layout="wide", page_title="ChemCompute Pro")
st.title("🧪 ChemCompute Pro")
st.subheader("Asisten Kimia AI Mobile-Friendly")

uploaded_file = st.file_uploader("Unggah foto soal kimia...", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    img = Image.open(uploaded_file)
    
    # Resize agar tidak melebihi lebar layar mobile umumnya
    max_width = 800
    if img.width > max_width:
        ratio = max_width / float(img.width)
        new_height = int(float(img.height) * float(ratio))
        img = img.resize((max_width, new_height), Image.Resampling.LANCZOS)
    
    # --- TAMPILAN ATAS: FITUR CROP ---
    st.markdown("### 1. Pilih Bagian Soal")
    cropped_img = st_cropper(
        img, 
        realtime_update=True, 
        box_color='#007bff', 
        aspect_ratio=None
    )
    
    # Jarak pemisah agar tombol terlihat jelas
    st.write("")
    hitung_btn = st.button("🚀 Lakukan Perhitungan", use_container_width=True)
    st.divider()

    # --- TAMPILAN BAWAH: ANALISIS & SOLUSI ---
    if hitung_btn:
        if cropped_img:
            st.markdown("### 2. Analisis & Solusi AI")
            with st.spinner("Gemini sedang memproses soal Anda..."):
                prompt = (
                    "Analisis gambar soal kimia ini. Pertama, tulis ulang teks soalnya. "
                    "Kemudian, berikan penjelasan konsep kimia yang relevan, tuliskan rumus yang digunakan dalam format LaTeX, "
                    "tunjukkan langkah-langkah perhitungan secara rinci beserta unitnya, dan berikan jawaban akhir yang jelas."
                )
                
                response = model.generate_content([prompt, cropped_img])
                
                # Menampilkan Hasil
                st.info("Berhasil dianalisis!")
                st.markdown(response.text)
                
                # Preview area yang dihitung (Opsional)
                with st.expander("Lihat area yang di-crop"):
                    st.image(cropped_img, use_container_width=True)
        else:
            st.error("Silakan tentukan bagian gambar yang ingin dihitung.")
