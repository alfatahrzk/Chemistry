import streamlit as st
import google.generativeai as genai
from PIL import Image
from streamlit_cropper import st_cropper

# 1. KONFIGURASI KUNCI API GEMINI (Tetap sesuai permintaan)
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
model = genai.GenerativeModel('gemini-2.5-flash')

# 2. PENGATURAN LAYOUT
st.set_page_config(layout="wide", page_title="ChemCompute Pro")

st.markdown("""
    <style>
    .main .block-container {
        padding: 2rem 1rem;
    }
    .stButton button {
        height: 3.5em;
        font-weight: bold;
        background-color: #FF4B4B;
        color: white;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🧪 ChemCompute Pro")
st.caption("Asisten Kimia AI - Mobile Friendly")

uploaded_file = st.file_uploader("Unggah foto soal kimia...", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    img = Image.open(uploaded_file)
    
    # --- RESIZE ADALAH KUNCI ---
    # Kita batasi lebar gambar di sini agar kanvas cropper otomatis mengecil
    max_width_mobile = 400 # Sedikit lebih kecil agar lebih aman di semua HP
    if img.width > max_width_mobile:
        ratio = max_width_mobile / float(img.width)
        new_height = int(float(img.height) * float(ratio))
        img = img.resize((max_width_mobile, new_height), Image.Resampling.LANCZOS)

    # --- TAMPILAN 1: AREA CROP (Hanya parameter basic) ---
    st.markdown("### 1. Pilih Bagian Soal")
    
    # Kita hapus 'width' atau 'canvas_width' karena menyebabkan error
    # Cropper akan otomatis mengikuti ukuran 'img' yang sudah di-resize di atas
    cropped_img = st_cropper(
        img, 
        realtime_update=True, 
        box_color='#FF4B4B', 
        aspect_ratio=None 
    )
    
    st.write("")
    hitung_btn = st.button("🚀 Lakukan Perhitungan", use_container_width=True)
    st.divider()

    # --- TAMPILAN 2: HASIL ANALISIS ---
    if hitung_btn:
        if cropped_img:
            st.markdown("### 2. Analisis & Solusi")
            with st.spinner("Gemini sedang bekerja..."):
                prompt = (
                    "Bertindaklah sebagai mentor Olimpiade Kimia (OSN) bernama Fatah. Target audiensmu adalah siswa SMA bernama Faura"
                    "yang cerdas, analitis, dan terbiasa dengan soal-soal tingkat lanjut. "
                    "Analisis gambar soal kimia ini dan berikan penyelesaian yang taktis, efisien, dan presisi secara ilmiah. "
                    "DILARANG KERAS menggunakan sapaan kekanak-kanakan (seperti 'halo murid-murid', 'mari kita hitung bareng'). "
                    "Gunakan gaya bahasa akademik profesional namun tetap *engaging*. "
                    "Struktur jawaban: "
                    "1. Tulis intisari parameter soal. "
                    "2. Tuliskan reaksi setengah sel yang relevan (gunakan LaTeX). "
                    "3. Tunjukkan langkah stoikiometri secara terstruktur dan logis. "
                    "4. Berikan jawaban akhir yang jelas. "
                    "Opsional: Berikan satu tips cepat atau 'insight' singkat terkait efisiensi perhitungan untuk tipe soal ini."
                )
                try:
                    # Mengirim konten ke model (Jangan diubah sesuai permintaan)
                    response = model.generate_content([prompt, cropped_img])
                    st.success("Selesai!")
                    st.markdown(response.text)
                except Exception as e:
                    st.error(f"Gagal memproses gambar: {e}")
