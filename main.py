import streamlit as st
import requests
import base64
import io
from PIL import Image

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="Chronos: Time Machine", page_icon="⌛", layout="centered")

# --- 2. CSS STYLING ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&display=swap');
    .stApp {
        background-image: url("https://images.unsplash.com/photo-1451187580459-43490279c0fa?q=80&w=2072&auto=format&fit=crop");
        background-size: cover;
        background-attachment: fixed;
    }
    .stBlock, div[data-testid="stVerticalBlock"] {
        background-color: rgba(0, 0, 0, 0.8);
        border-radius: 15px;
        padding: 20px;
        border: 1px solid #00e5ff;
    }
    h1 { font-family: 'Orbitron', sans-serif; color: #00e5ff; text-align: center; }
    h3, p, label { color: #ffffff !important; font-family: 'Courier New', monospace; }
    .stButton>button {
        background-color: #00e5ff; color: black; font-family: 'Orbitron', sans-serif;
        border: none; width: 100%; transition: 0.3s;
    }
    .stButton>button:hover { background-color: #ffffff; }
    </style>
    """, unsafe_allow_html=True)

st.title("CHRONOS V10 (DEBUGGER)")
st.markdown("<h3 style='text-align: center;'>Temporal Displacement Unit</h3>", unsafe_allow_html=True)

# --- 3. AUTH ---
if "HF_TOKEN" in st.secrets:
    api_key = st.secrets["HF_TOKEN"]
else:
    api_key = st.sidebar.text_input("ENTER ACCESS TOKEN", type="password")

# --- 4. HELPER FUNCTIONS ---
def image_to_base64(image):
    buffered = io.BytesIO()
    image.save(buffered, format="JPEG")
    return base64.b64encode(buffered.getvalue()).decode('utf-8')

# --- 5. MAIN LOGIC ---
if api_key:
    st.write("### 1. ACQUIRE BIOMETRIC DATA")
    input_method = st.radio("Select Input Source:", ["Activate Camera", "Upload File"])

    image_input = None
    if input_method == "Activate Camera":
        image_input = st.camera_input("Scanning Face...")
    else:
        image_input = st.file_uploader("Upload Image Data", type=["jpg", "png", "jpeg"])

    if image_input:
        # Load and Resize (CRITICAL for free tier)
        original_image = Image.open(image_input)
        original_image = original_image.resize((512, 512)) # Force small size
        
        st.image(original_image, caption="SUBJECT: PRESENT DAY (512x512)", width=300)

        st.write("---")
        st.write("### 2. SET TEMPORAL COORDINATES")
        years = st.select_slider("Warp Forward By:", options=["10 Years", "30 Years", "50 Years", "80 Years"])

        prompts = {
            "10 Years": "photo of a person, slightly older, 10 years later, realistic, 8k",
            "30 Years": "photo of a person, middle aged, 50 years old, grey hair, wrinkles, realistic",
            "50 Years": "photo of a person, 70 years old, grandmother grandfather, white hair, elderly, detailed",
            "80 Years": "photo of a person, 100 years old, ancient, deep wrinkles, very old, detailed portrait"
        }

        if st.button("INITIATE TIME WARP"):
            with st.spinner("⚡ CONTACTING SERVER..."):
                try:
                    # MANUAL API CALL (No Client Library)
                    API_URL = "https://api-inference.huggingface.co/models/runwayml/stable-diffusion-v1-5"
                    headers = {"Authorization": f"Bearer {api_key}"}
                    
                    # This specific model expects inputs + image in a specific way
                    # But for img2img on the API, we can sometimes just use text-to-image with init_image
                    # Let's try the standard payload
                    payload = {
                        "inputs": prompts[years],
                        "parameters": {
                            "image": image_to_base64(original_image), # Sending image as base64 parameter
                            "strength": 0.5,
                            "guidance_scale": 7.5
                        }
                    }
                    
                    response = requests.post(API_URL, headers=headers, json=payload)
                    
                    # --- THE DEBUGGING BLOCK ---
                    if response.status_code == 200:
                        # Success!
                        edited_image = Image.open(io.BytesIO(response.content))
                        st.success("✔ TEMPORAL JUMP COMPLETE")
                        st.image(edited_image, caption=f"SUBJECT: +{years}")
                    else:
                        # FAILURE - PRINT EVERYTHING
                        st.error(f"⚠️ SERVER ERROR: {response.status_code}")
                        st.write("Raw Server Message:")
                        st.code(response.text) # This will show us the REAL error
                        
                        if "loading" in response.text.lower():
                            st.info("💡 Solution: The model is loading. Click the button again in 30 seconds.")
                        elif "too large" in response.text.lower():
                            st.info("💡 Solution: The image is too big. We resized it, but try a smaller file.")

                except Exception as e:
                    st.error("⚠️ SYSTEM CRASH")
                    st.write(f"Python Error: {e}")

else:
    st.warning("⚠️ ACCESS DENIED. PLEASE ENTER TOKEN.")
