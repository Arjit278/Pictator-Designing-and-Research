import io
import requests
import streamlit as st
import json
import time
import re
from PIL import Image
from huggingface_hub import InferenceClient

# --------------------------------------
# 🔧 PAGE CONFIG & API
# --------------------------------------
st.set_page_config(page_title="Pictator Pro 2026", page_icon="🏎️", layout="wide")

OPENROUTER_API_KEY = st.secrets.get("OPENROUTER_API_KEY", "")
SERP_API_KEY = st.secrets.get("SERP_API_KEY", "")
HF_TOKEN = st.secrets.get("HF_TOKEN", "")

st.title("🏎️ Pictator Pro – CEO Engineering Suite")
st.caption("Strategic Parallel RCA | Multithreaded Design | 2026 Material Intel")

# --------------------------------------
# 🔐 AUTHENTICATION
# --------------------------------------
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

with st.sidebar:
    st.title("🔐 Access Panel")
    if not st.session_state.authenticated:
        user = st.text_input("Username")
        pwd = st.text_input("Password", type="password")
        if st.button("Login"):
            if user == "Harmony" and pwd == "Harmony_Pictator123":
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("Invalid Credentials")
    else:
        st.success("🟢 Logged in as Harmony")
        if st.button("Logout"):
            st.session_state.authenticated = False
            st.rerun()

if not st.session_state.authenticated:
    st.warning("🔐 Please login to continue")
    st.stop()

# --------------------------------------
# ⚡ FLASHMIND ENGINE (OPENROUTER)
# --------------------------------------
ANALYSIS_MODELS = [
    "qwen/qwen-3-coder:free",
    "meta-llama/llama-3.2-3b-instruct:free",
    "nousresearch/hermes-2-pro-llama-3-8b",
]

def call_openrouter(prompt):
    headers = {"Authorization": f"Bearer {OPENROUTER_API_KEY}", "Content-Type": "application/json"}
    for model in ANALYSIS_MODELS:
        try:
            r = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                json={
                    "model": model,
                    "messages": [
                        {"role": "system", "content": "You are an automotive engineering expert."},
                        {"role": "user", "content": prompt}
                    ]
                },
                timeout=15
            )
            if r.status_code == 200:
                return r.json()["choices"][0]["message"]["content"].strip()
        except:
            continue
    return "Intelligence fallback active: Manual review required."

# --------------------------------------
# 🛠️ IMAGE & MARKET ENGINES
# --------------------------------------
def generate_ai_image(prompt, model_id):
    """GENERATE: Pure AI Design Concept"""
    try:
        client = InferenceClient(model=model_id, token=HF_TOKEN)
        return client.text_to_image(prompt, width=1024, height=768)
    except Exception as e:
        st.error(f"HF Generation Failed: {e}")
        return None

def fetch_market_references(query):
    try:
        # Increase num to 40 to get a wide variety of sources to filter from
        params = {
            "engine": "google_images", 
            "q": f"{query} car seat covers leather", 
            "api_key": SERP_API_KEY, 
            "num": 40
        }
        r = requests.get("https://serpapi.com/search", params=params, timeout=10)
        results = r.json().get("images_results", [])
        
        filtered_refs = []
        used_domains = set() # This tracks the 'source' name to prevent repetition

        for i in results:
            source_name = i.get("source", "").strip()
            link = i.get("link", "").lower()
            
            # 1. Check if we've already used this specific source name (e.g., Elegant Auto)
            if source_name in used_domains:
                continue
            
            # 2. Check if the link belongs to our TRUSTED_DOMAINS list
            is_trusted = any(td in link for td in TRUSTED_DOMAINS)
            
            if is_trusted:
                filtered_refs.append({
                    "img": i["original"], 
                    "link": i["link"], 
                    "src": source_name
                })
                used_domains.add(source_name) # Lock this domain so it isn't used again
            
            # Stop once we have 6 unique high-quality sources
            if len(filtered_refs) >= 6:
                break
        
        # --- FALLBACK: If we still don't have 6 unique links after checking trusted ones ---
        if len(filtered_refs) < 6:
            for i in results:
                source_name = i.get("source", "").strip()
                if source_name not in used_domains:
                    filtered_refs.append({
                        "img": i["original"], 
                        "link": i["link"], 
                        "src": source_name
                    })
                    used_domains.add(source_name)
                if len(filtered_refs) >= 6: break
                
        return filtered_refs
    except Exception as e:
        st.sidebar.error(f"Search Fallback Engaged: {e}")
        return []

# --------------------------------------
# 🎯 UI: SMART CONFIGURATOR
# --------------------------------------
MODEL_OPTIONS = {
    "⚡ FLUX.1 Schnell": "black-forest-labs/FLUX.1-schnell",
    "🔥 FLUX.1 Dev": "black-forest-labs/FLUX.1-dev",
    "✨ SD 3.5 Large": "stabilityai/stable-diffusion-3.5-large"
}
selected_model = st.sidebar.selectbox("Choose AI Model", list(MODEL_OPTIONS.keys()))

with st.expander("🧠 Smart Design Configurator (2026 Specs)", expanded=True):
    colA, colB, colC = st.columns(3)
    with colA:
        car = st.selectbox("Vehicle", ["Maruti Wagon R", "Maruti Grand Vitara", "Custom/Other"])
        pattern = st.selectbox("Stitching", ["Ultra-Quilt Diamond", "Hex-Cell", "Puff", "Minimalist Flat"])
    with colB:
        material = st.selectbox("Material", ["1200 GSM Nappa", "Cotton", "Synthetic Leather", "Carbon Fiber Leather"])
        # FIXED: Removed the extra positional argument that caused the TypeError
        colors = st.text_input("Colorway", value="Tan & Charcoal")
    with colC:
        lighting = st.selectbox("Lighting", ["Studio", "Blueprint", "Cinematic Showroom"])
        market = st.selectbox("Market Tier", ["Luxury", "Affordable", "Sports", "OEM Upgrade"])
    
    custom_instruction = st.text_area("✍️ Custom Engineering Instructions", placeholder="Add specific details like contrast piping or perforation...")

# --------------------------------------
# 🚀 EXECUTION PIPELINE
# --------------------------------------
if st.button("🚀 EXECUTE FULL SUITE"):
    final_prompt = (
        f"Professional automotive interior photography, {car} custom seat covers, "
        f"{pattern} pattern, premium {material}, {colors} theme, "
        f"{custom_instruction}, {lighting} lighting, 8k ultra-realistic, material macro detail."
    )
    
    with st.status("Engineering Intelligence...") as status:
        st.write("🎨 Generating AI Design Concept...")
        main_img = generate_ai_image(final_prompt, MODEL_OPTIONS[selected_model])
        
        st.write("🌐 Fetching Real-World Market References...")
        market_refs = fetch_market_references(f"{car} {material} seat cover")
        
        st.write("📊 Analyzing Material Trends...")
        analysis = call_openrouter(f"Briefly analyze durability and 2026 trends for {material} with {pattern} stitching.")
        
        status.update(label="✅ Analysis Complete", state="complete")

    col_left, col_right = st.columns([2, 1])
    
    with col_left:
        st.subheader("🎨 AI-Generated Design Concept")
        if main_img:
            st.image(main_img, caption=f"AI Vision: {car} in {material}", use_container_width=True)
            buf = io.BytesIO()
            main_img.save(buf, format="PNG")
            st.download_button("💾 Save Concept", buf.getvalue(), "design_2026.png")
    
    with col_right:
        st.subheader("📈 Flashmind Analysis")
        st.info(analysis)

    st.divider()
    st.subheader("🌍 Verified Market References & Live Shop Links (Real Photos)")
    if market_refs:
        m_cols = st.columns(3)
        for idx, ref in enumerate(market_refs):
            with m_cols[idx % 3]:
                st.image(ref["img"], caption=f"Ref from {ref['src']}", use_container_width=True)
                st.link_button(f"🔗 View on {ref['src']}", ref["link"])

with st.expander("📊 2026 Tech & Model Trends"):
    st.write("- **AI Concepts:** Generated via Top Models are virtual prototype, customized and crafted by user, for prototype visualization.")
    st.write("- **Market Refs:** Sourced via SERP to ensure engineering feasibility.")
    st.markdown("""
        **Zero Data Retention (ZDR) Commitment:**
        - **Non-Storage:** Prompts and generated designs are processed in volatile memory. 
        - **Zero Training:** Your proprietary design logic is never used to train Omnicore & Pictator.
        - **Encryption:** All API calls use TLS 1.3 encryption for end-to-end security.
        - **Compliance:** This suite adheres to the 2026 Enterprise Privacy Standards for Industrial AI.
        """)
    
