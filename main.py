import streamlit as st
import google.generativeai as genai
from PIL import Image
from streamlit_cropper import st_cropper

# 1. KONFIGURASI KUNCI API GEMINI (Tetap menggunakan 2.5-flash sesuai permintaan)
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
model = genai.GenerativeModel('gemini-2.5-flash')

# 2. PENGATURAN LAYOUT
st.set_page_config(layout="wide", page_title="ChemCompute Pro")

# CSS Tambahan untuk menyembunyikan overflow dan merapikan tampilan mobile
st.markdown("""
    <style>
    /* Menghilangkan padding berlebih di mobile */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        padding-left: 1rem;
        padding-right: 1rem;
    }
    /* Memastikan komponen cropper dan gambar responsif */
    .stCropper, .img-container img {
        width: 100% !important;
        height: auto !important;
    }
    /* Membuat tombol lebih besar dan mudah diklik di HP */
    .stButton button {
        height: 3em;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🧪 ChemCompute Pro")
st.caption("Solusi Kimia dalam Genggaman")

uploaded_file = st.file_uploader("Unggah foto soal kimia...", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    img = Image.open(uploaded_file)
    
    # --- OPTIMASI MOBILE: Resize Gambar ---
    # Kita gunakan 450px sebagai standar lebar maksimal agar pas di layar HP
    max_width_mobile = 450 
    if img.width > max_width_mobile:
        ratio = max_width_mobile / float(img.width)
        new_height = int(float(img.height) * float(ratio))
        img = img.resize((max_width_mobile, new_height), Image.Resampling.LANCZOS)

    # --- TAMPILAN 1: AREA CROP ---
    st.markdown("### 1. Pilih Bagian Soal")
    
    # canvas_width diatur ke max_width_mobile agar tidak overflow
    cropped_img = st_cropper(
        img, 
        realtime_update=True, 
        box_color='#FF4B4B', # Warna merah agar lebih kontras
        aspect_ratio=None,
        canvas_width=max_width_mobile 
    )
    
    st.write("")
    hitung_btn = st.button("🚀 Lakukan Perhitungan", use_container_width=True)
    st.divider()

    # --- TAMPILAN 2: HASIL ANALISIS ---
    if hitung_btn:
        if cropped_img:
            st.markdown("### 2. Analisis & Solusi")
            with st.spinner("Gemini 2.5 Flash sedang memproses..."):
                # Kita kirim gambar yang sudah di-crop ke Gemini
                prompt = (
                    "Kamu adalah asisten ahli kimia. Analisis gambar soal ini: "
                    "1. Identifikasi teks soal. "
                    "2. Jelaskan konsep kimianya secara singkat. "
                    "3. Tuliskan rumus dalam LaTeX. "
                    "4. Berikan langkah pengerjaan dan jawaban akhir yang akurat."
                )
                
                try:
                    response = model.generate_content([prompt, cropped_img])
                    st.success("Analisis Selesai!")
                    st.markdown(response.text)
                    
                    with st.expander("Lihat Referensi Gambar"):
                        st.image(cropped_img, caption="Area yang dihitung", use_container_width=True)
                except Exception as e:
                    st.error(f"Terjadi kesalahan: {e}")
        else:
            st.warning("Silakan pilih area soal terlebih dahulu.")
