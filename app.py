import streamlit as st
from PIL import Image
from google import genai
from gtts import gTTS

# 1. Page Configuration
st.set_page_config(
    page_title="AI Medicine Assistant & Voice Reader", 
    page_icon="💊",
    layout="centered"
)

# 2. App Header
st.title("💊 Elderly Medicine Helper")
st.write("Upload an image of a medicine container to analyze usage guidelines, check expiration dates, and hear instructions read aloud.")

# 3. Sidebar Configuration
st.sidebar.title("Configuration")
api_key = st.sidebar.text_input("Enter your Gemini API Key:", type="password")

# Language Selection Dropdown
language = st.sidebar.selectbox("Choose Output Language:", ["English", "Hindi"])
lang_code = "hi" if language == "Hindi" else "en"

if api_key:
    client = genai.Client(api_key=api_key)
    
    uploaded_file = st.file_uploader(
        "Upload a clear image of the medicine packaging:", 
        type=["jpg", "jpeg", "png"]
    )
    
    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded Medicine Packaging", use_container_width=True)
        
        if st.button("Scan Label & Speak"):
            with st.spinner("Analyzing text and generating audio..."):
                try:
                    # Multimodal Prompt updated with dynamic language instruction
                    prompt = f"""
                    You are an assistant helping elderly patients read medicine packaging clearly. 
                    Analyze the uploaded image and extract the following in {language}:
                    
                    1. **Medicine Name**: Specify the Brand Name and Generic Name if visible.
                    2. **Expiration Date**: State the Expiry Date or Best-Before date if visible (or state 'Not visible on label').
                    3. **Simple Purpose**: Explain what condition this treats in 1-2 plain, simple sentences suitable for a non-medical user.
                    4. **Elderly Dosage & Instructions**: Provide simple, clear directions on how to take it safely.
                    5. **Key Safety Warnings**: List any important side effects or precautions.
                    
                    Keep the phrasing very concise, direct, and accessible. Write the entire output in {language}.
                    """
                    
                    response = client.models.generate_content(
                        model="gemini-3.6-flash",
                        contents=[image, prompt]
                    )
                    
                    # Display Output
                    st.success("Analysis Complete!")
                    st.markdown(response.text)
                    
                    # Clean text and generate TTS in selected language
                    clean_text = response.text.replace("*", "").replace("#", "")
                    tts = gTTS(text=clean_text, lang=lang_code)
                    audio_file_path = "medicine_summary.mp3"
                    tts.save(audio_file_path)
                    
                    st.audio(audio_file_path, format="audio/mp3")
                    st.caption("⚠️ Disclaimer: This is an AI-generated educational project. Always verify medicine details with a certified healthcare professional.")
                    
                except Exception as e:
                    st.error(f"Error analyzing image: {e}")
else:
    st.info("👈 Please enter your Gemini API Key in the left sidebar to start using the app.")