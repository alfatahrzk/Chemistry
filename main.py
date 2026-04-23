import streamlit as st
import google.generativeai as genai
from PIL import Image
from streamlit_cropper import st_cropper

# 1. KONFIGURASI KUNCI API GEMINI
# Pastikan sudah setting GEMINI_API_KEY di Streamlit Cloud Secrets
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

# Inisialisasi Model Gemini (Menggunakan gemini-1.5-flash untuk kecepatan dan dukungan visi)
model = genai.GenerativeModel('gemini-1.5-flash')

# 2. PENGATURAN LAYOUT STREAMLIT
st.set_page_config(layout="wide", page_title="ChemCompute Pro")
st.title("🧪 ChemCompute Pro: Asisten Kimia AI")
st.write("Unggah foto soal kimia Anda dan pilih bagian yang ingin diselesaikan.")

# 3. FITUR UNGGAH GAMBAR
uploaded_file = st.file_uploader("Unggah foto soal kimia...", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    img = Image.open(uploaded_file)
    
    col1, col2 = st.columns([1, 1]) # Membuat dua kolom agar tampilan seimbang
    
    with col1:
        st.subheader("Pilih Bagian Soal (Crop)")
        # 4. FITUR CROP INTERAKTIF
        # realtime_update=True memungkinkan hasil crop langsung berubah saat kotak digeser
        cropped_img = st_cropper(img, realtime_update=True, box_color='#007bff', aspect_ratio=None)
        
        # Tombol untuk memicu perhitungan
        hitung_btn = st.button("Lakukan Perhitungan", use_container_width=True)

    with col2:
        st.subheader("Analisis & Solusi AI")
        
        if hitung_btn:
            if cropped_img:
                with st.spinner("Gemini sedang menganalisis soal..."):
                    # 5. MENGIRIM GAMBAR KE GEMINI
                    prompt = (
                        "Analisis gambar soal kimia ini. Pertama, tulis ulang teks soalnya. "
                        "Kemudian, berikan penjelasan konsep kimia yang relevan, tuliskan rumus yang digunakan dalam format LaTeX, "
                        "tunjukkan langkah-langkah perhitungan secara rinci beserta unitnya, dan berikan jawaban akhir yang jelas."
                    )
                    
                    # Memanggil Gemini dengan input gambar yang di-crop
                    response = model.generate_content([prompt, cropped_img])
                    
                    # 6. MENAMPILKAN HASIL DARI AI
                    st.markdown("### Hasil Perhitungan")
                    st.markdown(response.text)
                    
                    # Menampilkan preview kecil hasil crop sebagai referensi
                    st.image(cropped_img, caption="Area yang dianalisis", width=200)
            else:
                st.error("Silakan tentukan bagian gambar yang ingin dihitung.")
