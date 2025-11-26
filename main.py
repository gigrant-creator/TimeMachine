import streamlit as st
from huggingface_hub import InferenceClient
from PIL import Image
import time

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(page_title="Chronos: Time Machine", page_icon="⌛", layout="centered")

# --- 2. CSS STYLING (Sci-Fi Look) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&display=swap');
    
    .stApp {
        background-image: url("https://images.unsplash.com/photo-1451187580459-43490279c0fa?q=80&w=2072&auto=format&fit=crop");
        background-size: cover;
        background-repeat: no-repeat;
        background-attachment: fixed;
    }
    
    .stBlock, div[data-testid="stVerticalBlock"] {
        background-color: rgba(0, 0, 0, 0.8);
        border-radius: 15px;
        padding: 20px;
        border: 1px solid #00e5ff;
    }

    h1 {
        font-family: 'Orbitron', sans-serif;
        color: #00e5ff;
        text-shadow: 0 0 10px #00e5ff;
        text-align: center;
    }
    h3, p, label, .stRadio label {
        color: #ffffff !important;
        font-family: 'Courier New', monospace;
    }

    /* Button Styling */
    .stButton>button {
        background-color: #00e5ff;
        color: black;
        font-family: 'Orbitron', sans-serif;
        font-weight: bold;
        border: none;
        border-radius: 5px;
        width: 100%;
        transition: 0.3s;
    }
    .stButton>button:hover {
        background-color: #ffffff;
        box-shadow: 0 0 15px #ffffff;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. APP HEADER ---
st.title("CHRONOS V2.0")
st.markdown("<h3 style='text-align: center;'>Temporal Displacement Unit</h3>", unsafe_allow_html=True)

# --- 4. AUTHENTICATION ---
if "HF_TOKEN" in st.secrets:
    api_key = st.secrets["HF_TOKEN"]
else:
    api_key = st.sidebar.text_input("ENTER ACCESS TOKEN", type="password")

# --- 5. MAIN LOGIC ---
if api_key:
    # Initialize Client WITH the model name to prevent confusion
    client = InferenceClient(model="timbrooks/instruct-pix2pix", token=api_key)

    st.write("### 1. ACQUIRE BIOMETRIC DATA")
    input_method = st.radio("Select Input Source:", ["Activate Camera", "Upload File"])

    image_input = None
    if input_method == "Activate Camera":
        image_input = st.camera_input("Scanning Face...")
    else:
        image_input = st.file_uploader("Upload Image Data", type=["jpg", "png", "jpeg"])

    if image_input:
        st.image(image_input, caption="SUBJECT: PRESENT DAY", width=300)
        original_image = Image.open(image_input)

        st.write("---")
        st.write("### 2. SET TEMPORAL COORDINATES")
        
        years = st.select_slider(
            "Warp Forward By:",
            options=["10 Years", "30 Years", "50 Years", "80 Years"]
        )

        prompts = {
            "10 Years": "make them look 10 years older, slight skin texture",
            "30 Years": "make them look 40 years older, grey hair, visible wrinkles",
            "50 Years": "make them look 70 years old, elderly, white hair, deep wrinkles",
            "80 Years": "make them look 100 years old, ancient, very old, detailed texture"
        }

        if st.button("INITIATE TIME WARP"):
            status_box = st.empty() # Create a placeholder for status updates
            
            try:
                # --- THE RETRY LOOP ---
                # This tries 3 times if the server says "I'm busy"
                for attempt in range(3):
                    try:
                        status_box.info(f"⚡ Attempt {attempt+1}/3: Establishing Neural Link...")
                        
                        # The Correct Call
                        edited_image = client.image_to_image(
                            image=original_image,
                            prompt=prompts[years],
                            image_guidance_scale=1.5,
                            guidance_scale=8.5
                        )
                        
                        # If successful:
                        status_box.success("✔ TEMPORAL JUMP COMPLETE")
                        st.image(edited_image, caption=f"SUBJECT: +{years}")
                        break # Exit the loop!
                        
                    except Exception as inner_e:
                        # Check if it's a "Loading" error (503)
                        error_msg = str(inner_e)
                        if "503" in error_msg or "loading" in error_msg.lower():
                            status_box.warning(f"⚠ Server Waking Up... Waiting 10 seconds...")
                            time.sleep(10) # Wait for server to load
                        else:
                            raise inner_e # If it's a real error, crash.

            except Exception as e:
                st.error("⚠️ SYSTEM FAILURE")
                st.code(f"Error Details: {e}") # This prints the REAL error code

else:
    st.warning("⚠️ ACCESS DENIED. PLEASE ENTER TOKEN.")
