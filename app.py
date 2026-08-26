import streamlit as st
from PIL import Image
from google import genai
from gtts import gTTS

# 1. Page Configuration
st.set_page_config(
    page_title="Medicine Safety & Voice Assistant", 
    page_icon="💊",
    layout="centered"
)

# 2. App Header
st.title("💊 Household Medicine Safety Assistant")
st.write("Upload or snap an image of a medicine container to analyze usage guidelines, check expiration dates, and hear instructions read aloud.")

# 3. Sidebar Configuration (Language Selection)
st.sidebar.title("Configuration")
language = st.sidebar.selectbox("Choose Output Language:", ["English", "Hindi"])
lang_code = "hi" if language == "Hindi" else "en"

# Load API Key automatically from Streamlit Secrets
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    client = genai.Client(api_key=api_key)
    
    # 4. Input Method: Camera or File Upload
    input_method = st.radio("Choose input method:", ["Take a Photo (Camera)", "Upload from Gallery"])
    
    uploaded_file = None
    if input_method == "Take a Photo (Camera)":
        uploaded_file = st.camera_input("Snap a picture of the medicine packaging")
    else:
        uploaded_file = st.file_uploader("Choose an image from your device:", type=["jpg", "jpeg", "png"])
    
    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded Medicine Packaging", use_container_width=True)
        
        if st.button("Scan Label & Speak"):
            with st.spinner("Analyzing text and generating audio..."):
                try:
                    prompt = f"""
                    You are an assistant helping people understand medicine packaging clearly. 
                    Analyze the uploaded image and extract the following in {language}:
                    
                    1. **Medicine Name**: Specify the Brand Name and Generic Name if visible.
                    2. **Expiration Date**: State the Expiry Date or Best-Before date if visible (or state 'Not visible on label').
                    3. **Simple Purpose**: Explain what condition this treats in 1-2 plain, simple sentences suitable for a general user.
                    4. **Dosage & Instructions**: Provide simple, clear directions on how to take it safely.
                    5. **Key Safety Warnings**: List any important side effects or precautions.
                    
                    Keep the phrasing very concise, direct, and accessible. Write the entire output in {language}.
                    """
                    
                    response = client.models.generate_content(
                        model="gemini-2.0-flash",
                        contents=[image, prompt]
                    )
                    
                    st.success("Analysis Complete!")
                    st.markdown(response.text)
                    
                    clean_text = response.text.replace("*", "").replace("#", "")
                    tts = gTTS(text=clean_text, lang=lang_code)
                    audio_file_path = "medicine_summary.mp3"
                    tts.save(audio_file_path)
                    
                    # Standard manual audio player (voice-note style)
                    st.audio(audio_file_path, format="audio/mp3")
                    
                    st.caption("⚠️ Disclaimer: This is an AI-generated educational project. Always verify medicine details with a certified healthcare professional.")
                    
                except Exception as e:
                    st.error(f"Error analyzing image: {e}")
                    
except Exception:
    st.error("⚠️ Gemini API Key not found. Please configure `GEMINI_API_KEY` in your Streamlit Cloud Secrets settings.")