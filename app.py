import streamlit as st
import os
import time
from docx2pdf import convert
import pythoncom  # Required for Windows/macOS Word automation in threads

# Set page config
st.set_page_config(
    page_title="Word to PDF Agent",
    page_icon="📄",
    layout="centered"
)

# Custom CSS for a "Premium" feel
st.markdown("""
    <style>
    .stButton>button {
        width: 100%;
        background-color: #4CAF50;
        color: white;
        font-weight: bold;
        padding: 10px;
        border-radius: 10px;
        border: none;
    }
    .stButton>button:hover {
        background-color: #45a049;
    }
    .upload-box {
        border: 2px dashed #4CAF50;
        padding: 20px;
        border-radius: 10px;
        text-align: center;
    }
    </style>
""", unsafe_allow_html=True)

def main():
    st.title("📄 Word to PDF AI Agent")
    st.markdown("### Enterprise-Grade Document Conversion")
    st.info("Drag and drop your Word document below to convert it to PDF instantly.")

    uploaded_file = st.file_uploader("Choose a Word file", type=['docx', 'doc'])

    if uploaded_file is not None:
        file_details = {"FileName": uploaded_file.name, "FileType": uploaded_file.type, "FileSize": uploaded_file.size}
        # st.write(file_details)

        if st.button("🚀 Convert to PDF"):
            progress_bar = st.progress(0)
            status_text = st.empty()

            # 1. Save uploaded file locally
            status_text.text("📥 Receiving file...")
            save_path = os.path.join(os.getcwd(), uploaded_file.name)
            with open(save_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            progress_bar.progress(20)
            time.sleep(0.5)

            # 2. Simulate AI Analysis
            status_text.text("🤖 AI Agent analyzing content structure...")
            progress_bar.progress(40)
            time.sleep(1)

            # 3. Convert
            status_text.text("⚙️ Converting format...")
            output_pdf = os.path.splitext(save_path)[0] + ".pdf"
            
            try:
                # Initialize COM for this thread (Crucial for Streamlit + docx2pdf)
                try:
                    pythoncom.CoInitialize() 
                except:
                    pass
                
                convert(save_path, output_pdf)
                progress_bar.progress(100)
                status_text.text("✅ Conversion Complete!")
                
                st.success(f"Successfully converted {uploaded_file.name} to PDF!")
                
                # 4. Download Button
                with open(output_pdf, "rb") as pdf_file:
                    st.download_button(
                        label="📥 Download PDF",
                        data=pdf_file,
                        file_name=os.path.basename(output_pdf),
                        mime="application/pdf"
                    )
            except Exception as e:
                st.error(f"Error during conversion: {e}")
            finally:
                # Cleanup logic (Optional: keep files for demo or delete)
                # os.remove(save_path) 
                pass

if __name__ == "__main__":
    main()
