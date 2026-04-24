import io
import json
import requests
import streamlit as st
import re
import threading
import time
import random
import zipfile  # NEW: For ZIP functionality
from PIL import Image

# --------------------------------------
# 🔧 PAGE CONFIG
# --------------------------------------
st.set_page_config(page_title="Pictator Pro", page_icon="🏎️", layout="wide")

st.title("🏎️ Pictator Pro – CEO Engineering Suite")
st.caption("Strategic Parallel RCA | Multithreaded Design | 2026 Material Intel")



# --------------------------------------
# 🔐 LOGIN SYSTEM (ADDED - NO REMOVAL)
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
                st.success("✅ Logged in")
                st.rerun()
            else:
                st.error("❌ Invalid credentials")
    else:
        st.success("🟢 Logged in as Harmony")
        if st.button("🚪 Logout"):
            st.session_state.authenticated = False
            st.rerun()

if not st.session_state.authenticated:
    st.warning("🔐 Please login from sidebar to continue")
    st.stop()
    
# --------------------------------------
# 🧠 ADMIN DATA STORE
# --------------------------------------
if "admin_logs" not in st.session_state:
    st.session_state.admin_logs = []

if st.sidebar.checkbox("View Raw LLM Logs"):
    for log in reversed(st.session_state.admin_logs[-10:]):
        st.sidebar.text(f"{log['timestamp']} | {log['prompt']}")
        st.sidebar.code(log["raw_output"])

# --- UPDATE THIS BLOCK ---
if "global_count" not in st.session_state:
    st.session_state.global_count = 0

# Now the sidebar metric can safely find the key
st.sidebar.markdown("---")
st.sidebar.subheader("🛠 Admin Panel")
st.sidebar.metric("🌍 Total Images (All Users)", st.session_state.global_count)


# --------------------------------------
# SESSION
# --------------------------------------
if "count" not in st.session_state:
    st.session_state.count = 0

st.sidebar.title("🔐 Control Panel")
st.sidebar.metric("🧑 Your Generated Images", st.session_state.count)
st.sidebar.markdown("---")

# --------------------------------------
# 🎨 MODEL SELECTOR (NEW PATCH)
# --------------------------------------
st.sidebar.markdown("---")
st.sidebar.subheader("🎨 Image Model Control")

MODEL_OPTIONS = {
    "⚡ Default (Fast - FLUX Schnell)": "black-forest-labs/FLUX.1-schnell",
    "🔥 Krea Dev (Ultra Realistic)": "black-forest-labs/FLUX.1-Krea-dev",
    "🧠 Qwen Image (Balanced AI)": "Qwen/Qwen-Image",
    "⚡ SDXL Lightning (Fastest)": "ByteDance/SDXL-Lightning"
}

selected_model_label = st.sidebar.selectbox(
    "Choose Generation Model",
    list(MODEL_OPTIONS.keys())
)

SELECTED_MODEL = MODEL_OPTIONS[selected_model_label]

st.sidebar.caption(f"Active Model: {SELECTED_MODEL}")

# --------------------------------------
# API CONFIG
# --------------------------------------
OPENROUTER_API_KEY = st.secrets.get("OPENROUTER_API_KEY", "")
SERP_API_KEY = st.secrets.get("SERP_API_KEY", "")
HF_TOKEN = st.secrets.get("HF_TOKEN", "")

# --------------------------------------
# 🌐 WEBSITE FETCH
# --------------------------------------
def fetch_real_website(brand, part="automotive"):
    try:
        # 🎯 Build smart query based on part
        if part == "seat":
            query = f"{brand} car seat covers india buy OR site OR collection OR custom seat covers"
        else:
            query = f"{brand} automotive official website OR products"

        r = requests.get(
            "https://serpapi.com/search",
            params={
                "engine": "google",
                "q": query,
                "api_key": SERP_API_KEY
            },
            timeout=5
        )

        results = r.json().get("organic_results", [])

        # --------------------------------------
        # 🧠 PRIORITY FILTERING
        # --------------------------------------
        for res in results:
            link = res.get("link", "").lower()

            # ✅ Prefer product / collection pages
            if any(k in link for k in [
                "seat-cover", "seat-cover", "car-seat-cover",
                "collection", "custom-seat", "products"
            ]):
                return res.get("link")

        # --------------------------------------
        # 🥈 SECOND PRIORITY: Official site
        # --------------------------------------
        for res in results:
            link = res.get("link", "").lower()

            if brand.lower().replace(" ", "") in link:
                return res.get("link")

        # --------------------------------------
        # 🥉 FALLBACK: Any valid result
        # --------------------------------------
        if results:
            return results[0].get("link")

    except:
        pass

    return None
# --------------------------------------
# RESULT CONTAINER
# --------------------------------------
class AnalysisResults:
    def __init__(self):
        self.rca_intel = None
        self.specs_raw = None
        self.market_photos = []
        self.ai_concept = None
        self.rca_status = "OK"
        self.final_images = []

# --------------------------------------
# ⚡ FLASHMIND ENGINE
# --------------------------------------
ANALYSIS_FALLBACK_MODELS = [
    "qwen/qwen3-coder:free",
    "qwen/qwen3-next-80b-a3b-instruct:free",
    "meta-llama/llama-3.2-3b-instruct:free",
    "nousresearch/hermes-2-pro-llama-3-8b",
    "qwen/qwen3-next-80b-a3b-instruct:free",
]

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

def call_openrouter_with_fallback_requests(prompt: str, api_key: str):
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}

    for model in ANALYSIS_FALLBACK_MODELS:
        try:
            r = requests.post(
                OPENROUTER_URL,
                headers=headers,
                json={
                    "model": model,
                    "messages": [
                        {"role": "system", "content": "You are an automotive engineering expert."},
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.2
                },
                timeout=60
            )

            if r.status_code == 200:
                data = r.json()
                content = data.get("choices", [{}])[0].get("message", {}).get("content")
                if content:
                    return content.strip(), "OK"

            elif r.status_code == 429:
                time.sleep(2)

        except:
            continue

    return None, "All models failed"

# --------------------------------------
# SAFE JSON
# --------------------------------------
def safe_json_extract(text):
    try:
        text = str(text)

        # Try direct JSON first
        return json.loads(text)

    except:
        pass

    try:
        # Extract JSON array safely
        match = re.search(r"\[\s*{.*?}\s*\]", text, re.DOTALL)
        if match:
            return json.loads(match.group())
    except:
        pass

    return []

# --------------------------------------
# ✅ DOMAIN BRAND FILTER
# --------------------------------------
PART_BRAND_WHITELIST = {
    "seat": [
        "Stanley", "Autoform", "autofurnish", "Elegant Auto Accessories",
        "KVD Auto", "Galaxy Auto", "Classic Auto"
    ],
    "tyre": ["MRF", "JK Tyre", "Apollo", "CEAT", "Bridgestone"],
    "battery": ["Amaron", "Exide"],
    "lighting": ["Lumax", "Philips Automotive"],
}

# --------------------------------------
# NORMALIZER
# --------------------------------------
def normalize_specs(specs, prompt=""):
    normalized = []
    seen_brands = set()

    # --------------------------------------
    # 🔍 PART DETECTION (INLINE - LIGHTWEIGHT)
    # --------------------------------------
    p = prompt.lower()

    PART_KEYWORDS = {
        "seat": ["seat", "seat cover"],
        "headlight": ["headlight", "head lamp"],
        "tail light": ["tail light", "rear light"],
        "steering": ["steering"],
        "tyre": ["tyre", "tire", "wheel"],
        "brake": ["brake", "disc brake"],
        "suspension": ["suspension", "shock absorber"],
        "battery": ["battery", "ev battery"],
        "mirror": ["mirror"],
    }

    detected_part = "automotive component"
    for part, keywords in PART_KEYWORDS.items():
        if any(k in p for k in keywords):
            detected_part = part
            break
    # ✅ Detect part from earlier logic
    allowed_brands = PART_BRAND_WHITELIST.get(detected_part, [])
    
    # --------------------------------------
    # 🧠 PART-BASED MATERIAL INTELLIGENCE
    # --------------------------------------
    PART_MATERIAL_MAP = {
        "seat": "PU Leather / Fabric / Nappa leather",
        "headlight": "Polycarbonate Lens + LED Matrix",
        "tail light": "LED + Acrylic Housing",
        "steering": "Leather Wrapped + Aluminum Core",
        "tyre": "Rubber Compound + Steel Belt",
        "brake": "Carbon Ceramic / Steel Disc",
        "suspension": "Hydraulic + Alloy Steel",
        "battery": "Lithium-ion Cells",
        "mirror": "ABS Housing + Reflective Glass",
    }

    # --------------------------------------
    # 🔄 NORMALIZATION LOOP
    # --------------------------------------
    for item in specs:
        if not isinstance(item, dict):
            continue

        brand = item.get("Brand") or item.get("vendor") or "Unknown"

        # 🚫 Skip duplicates
        if brand.lower() in seen_brands:
            continue
        seen_brands.add(brand.lower())

        # ✅ Safe vehicle extraction
        compatibility = item.get("compatibility")
        if isinstance(compatibility, list) and len(compatibility) > 0:
            vehicle = compatibility[0]
        elif isinstance(compatibility, str):
            vehicle = compatibility
        else:
            vehicle = item.get("Vehicle") or "Generic"

        # ✅ Smart material logic (part-aware + fallback detection)
        item_str = str(item).lower()

        if item.get("Material"):
            material = item.get("Material")
        elif any(x in item_str for x in ["leather", "napa", "alcantara", "pu leather", "vegan leather"]):
            material = "Premium Leather / Synthetic"
        else:
            material = PART_MATERIAL_MAP.get(detected_part, "Advanced Automotive Material")

        # ✅ Dynamic type (based on part)
        comp_type = item.get("Type") or item.get("model") or detected_part

        # ✅ Strength tuning per part
        if detected_part in ["brake", "suspension"]:
            strength = item.get("Strength") or "High Load / Safety Critical"
        elif detected_part in ["tyre"]:
            strength = item.get("Strength") or "Wear Resistant / High Grip"
        else:
            strength = item.get("Strength") or "Optimized"

        # ✅ Website logic (robust)
        website = item.get("Website")
        if not website or "http" not in website:
            safe_brand = brand if brand and brand != "Unknown" else f"{detected_part} supplier india"
            website = fetch_real_website(safe_brand, detected_part)
        
        normalized.append({
            "Brand": brand,
            "Vehicle": vehicle,
            "Type": comp_type,
            "Material": material,
            "Strength": strength,
            "Description": item.get("description") or "",
            "Website": website
        })

    return normalized

    # --------------------------------------
    # 🛡 FINAL FALLBACK (INSIDE FUNCTION)
    # --------------------------------------
    if not normalized or all(d.get("Brand") == "Unknown" for d in normalized):
    
        if detected_part == "seat":
            normalized = [
                {
                    "Brand": "Autoform",
                    "Vehicle": "Passenger Car",
                    "Type": "Seat Cover",
                    "Material": "PU Leather",
                    "Strength": "Premium Finish",
                    "Description": "India leader in custom seat covers",
                    "Website": "https://autoform.in"
                },
                {
                    "Brand": "Stanley",
                    "Vehicle": "Premium Cars",
                    "Type": "Seat Cover",
                    "Material": "Nappa Leather",
                    "Strength": "Luxury Grade",
                    "Description": "High-end automotive interiors",
                    "Website": reviews.oneclearwinner.com/product/custom-made-car-seat-covers
                },
                {
                    "Brand": "Elegant Auto Accessories",
                    "Vehicle": "Universal Fit",
                    "Type": "Seat Cover",
                    "Material": "Synthetic Leather",
                    "Strength": "Durable",
                    "Description": "Mass market seat cover supplier",
                    "Website": "https://www.autofurnish.com/collections/oem-style-factory-fitted-seat-covers"
                }
            ]
        else:
            normalized = [
                {
                    "Brand": "Bosch India",
                    "Vehicle": "Passenger Car",
                    "Type": "Automotive Component",
                    "Material": "Advanced Automotive Material",
                    "Strength": "High Reliability",
                    "Description": "Leading OEM supplier in India",
                    "Website": "https://www.bosch.in"
                },
                {
                    "Brand": "Uno Minda",
                    "Vehicle": "2W/4W",
                    "Type": "Automotive Component",
                    "Material": "Engineered Materials",
                    "Strength": "Durable",
                    "Description": "Major Indian auto component manufacturer",
                    "Website": "https://www.unominda.com"
                },
                {
                    "Brand": "Lumax",
                    "Vehicle": "Passenger Car",
                    "Type": "Lighting & Components",
                    "Material": "Polycarbonate / Electronics",
                    "Strength": "OEM Grade",
                    "Description": "Leading automotive lighting player",
                    "Website": "https://www.lumaxworld.in"
                }
            ]
    
    return normalized[:3]
# --------------------------------------
# IMAGE ENGINE (HF)
# --------------------------------------

def hf_gen_image(prompt):
    try:
        model_url = f"https://router.huggingface.co/hf-inference/models/{SELECTED_MODEL}"

        headers = {
            "Authorization": f"Bearer {HF_TOKEN}",
            "Content-Type": "application/json"
        }

        payload = {
            "inputs": prompt,
            "parameters": {
                "guidance_scale": 7.5,
                "num_inference_steps": 28
            }
        }

        # ⚡ Speed optimization per model
        if "Lightning" in SELECTED_MODEL:
            payload["parameters"]["num_inference_steps"] = 8

        if "Krea" in SELECTED_MODEL:
            payload["parameters"]["guidance_scale"] = 8.5

        r = requests.post(model_url, headers=headers, json=payload, timeout=60)

        if r.status_code == 200:
            return Image.open(io.BytesIO(r.content)).convert("RGB")

        else:
            return None

    except Exception as e:
        print(f"HF ERROR: {e}")
        return None

def enhance_prompt(prompt):
    if "Krea" in SELECTED_MODEL:
        return f"{prompt}, ultra realistic, cinematic lighting, hyper-detailed textures, 8k, studio quality"

    elif "Qwen" in SELECTED_MODEL:
        return f"{prompt}, highly structured design, clean composition, modern industrial design"

    elif "Lightning" in SELECTED_MODEL:
        return f"{prompt}, sharp, fast render, high contrast, clean output"

    return prompt
# --------------------------------------
# THREADS
# --------------------------------------
def thread_rca(res, prompt):
    res.rca_intel, res.rca_status = call_openrouter_with_fallback_requests(
        f"Generate automotive trends: {prompt}", OPENROUTER_API_KEY
    )

def thread_meta(res, prompt):
    res.specs_raw, _ = call_openrouter_with_fallback_requests(
        f"""
        Return ONLY VALID JSON. No explanation. No text.
    
        Generate EXACTLY 3 REAL automotive vendors for: {prompt}
        
        STRICT RULES:
        - If part = seat cover → ONLY seat cover manufacturers
        - DO NOT return tyre, battery, or unrelated brands
        - Prefer Indian aftermarket interior brands with weblinks
        - Include latest trends 2026 like Ultra-Quilt (Diamond), Carbon Fiber Texture, Minimalist "Flat" Grain, "GSM" (Grams per Square Meter) of the material
        - Display direct Website like https://www.autofurnish.com/collections/oem-style-factory-fitted-seat-covers, autofurnish.com/collections/oem-style-factory-fitted-seat-covers
        - Also show trends in world in europe with websites working properly
    
        FORMAT:
        [
            {{
                "Brand": "Bosch",
                "Vehicle": "Passenger Car",
                "Type": "",
                "Material": "",
                "Strength": "",
                "Description": "",
                "Website": "https://example.com"
            }}
        ]
    
        IMPORTANT:
        - Output MUST start with [ and end with ]
        - No markdown
        - No text before or after
        """,
        OPENROUTER_API_KEY
    )

def thread_assets(res, prompt):
    try:
        r = requests.get(
            "https://serpapi.com/search",
            params={"engine": "google_images", "q": prompt, "api_key": SERP_API_KEY},
            timeout=10
        )
        res.market_photos = r.json().get("images_results", [])[:3]
    except:
        res.market_photos = []
    res.ai_concept = hf_gen_image(prompt)

# --------------------------------------
# UI
# --------------------------------------
prompt = st.text_area("Enter Topic")

col1, col2 = st.columns(2)

if col1.button("🚀 EXECUTE"):
    res = AnalysisResults()

    with st.status("🚀 Engineering Data...", expanded=True) as status:
        t1 = threading.Thread(target=thread_rca, args=(res, prompt))
        t2 = threading.Thread(target=thread_meta, args=(res, prompt))
        t3 = threading.Thread(target=thread_assets, args=(res, prompt))

        t1.start(); t2.start(); t3.start()
        t1.join(); t2.join(); t3.join()
        status.update(label="✅ Analysis Complete", state="complete")

    # --------------------------------------
    # 🔥 FINAL IMAGE PIPELINE (FIXED)
    # --------------------------------------
    final_images = []
    if res.market_photos:
        for img_data in res.market_photos:
            url = img_data.get("thumbnail") or img_data.get("original")
            if url:
                final_images.append(url)

    while len(final_images) < 3:
        dynamic_prompt = f"""
        {prompt}, {random.choice(TREND_KEYWORDS)},
        ultra modern automotive seat, india market, 2026 design,
        premium materials, realistic lighting, 8k
        """
        ai_img = hf_gen_image(enhance_prompt(dynamic_prompt))
    
        if ai_img:
            final_images.append(ai_img)
        else:
            break
    # 3️⃣ FALLBACK (STILL DYNAMIC — NOT FIXED)
    while len(final_images) < 3:
        fallback_query = f"https://source.unsplash.com/600x400/?{prompt},{random.choice(TREND_KEYWORDS)}"
        final_images.append(fallback_query)
    
    res.final_images = final_images
    # ✅ Count generated images
    generated_count = len(res.final_images)
    
    st.session_state.count += generated_count
    st.session_state.global_count += generated_count
    
    if not res.final_images:
        st.warning("No images generated")
    # --------------------------------------
    # 📦 DOWNLOAD ALL LOGIC (ZIP)
    # --------------------------------------
    zip_buf = io.BytesIO()
    with zipfile.ZipFile(zip_buf, "w") as zf:
        # Report
        report = f"TOPIC: {prompt}\n\nTRENDS:\n{res.rca_intel}\n\nSPECS:\n{res.specs_raw}"
        zf.writestr("full_report.txt", report)
        # Images
        # --- UPDATE THIS SUB-BLOCK ---
        if res.ai_concept:
            try:
                img_byte = io.BytesIO()
                res.ai_concept.save(img_byte, format="PNG")
                zf.writestr("concept_design.png", img_byte.getvalue())
            except Exception as e:
                st.error(f"Error saving ZIP image: {e}")
        for idx, img_obj in enumerate(res.final_images):
            if isinstance(img_obj, Image.Image):
                img_byte = io.BytesIO()
                img_obj.save(img_byte, format="PNG")
                zf.writestr(f"spec_image_{idx}.png", img_byte.getvalue())
    
    st.sidebar.download_button("📦 Download All Files (ZIP)", zip_buf.getvalue(), "Pictator_Package.zip", "application/zip")

    # --------------------------------------
    # DISPLAY
    # --------------------------------------
    st.subheader("📊 Current Trends")
    st.write(res.rca_intel)

    if res.ai_concept:
        st.image(res.ai_concept)
        # --- PATCH: DOWNLOAD CONCEPT ---
        buf_concept = io.BytesIO()
        res.ai_concept.save(buf_concept, format="PNG")
        st.download_button("💾 Save Concept Image", buf_concept.getvalue(), "concept.png", "image/png")

    raw_specs = safe_json_extract(res.specs_raw)
    # 🔐 Store raw LLM output for admin
    st.session_state.admin_logs.append({
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "prompt": prompt,
        "raw_output": res.specs_raw
    })
    specs = normalize_specs(raw_specs, prompt)

         
    # --- PATCH: DOWNLOAD TEXT REPORT ---
    report_text = f"ANALYSIS: {prompt}\n\nTRENDS:\n{res.rca_intel}\n\nSPECS:\n{json.dumps(specs, indent=2)}"
    st.sidebar.download_button("📄 Download Full Report", report_text, f"report_{prompt[:10]}.txt", "text/plain")

    st.subheader("🔍 Technical Specs")

    cols = st.columns(3)
    for i, col in enumerate(cols):
        d = specs[i % len(specs)] if specs else {}
        with col:
            brand = d.get("Brand") or f"auto-seat-{i}"
            st.markdown(f"### {brand}")
            st.write(f"**Vehicle:** {d.get('Vehicle')}")
            for k, v in d.items():
                if k not in ["Vehicle", "Website"]:
                    st.write(f"**{k}:** {v}")
            
            if d.get("Description"):
                st.caption(d.get("Description"))

            website = d.get("Website") or fetch_real_website(brand)
            if website:
                st.link_button("🌐 Visit Website", website + f"?ref={i}")

            if i < len(res.final_images):
                img_src = res.final_images[i]
                st.image(img_src)
                # --- PATCH: DOWNLOAD SPEC IMAGE ---
                if isinstance(img_src, Image.Image):
                    buf_spec = io.BytesIO()
                    img_src.save(buf_spec, format="PNG")
                    st.download_button(f"📥 Save {brand} Image", buf_spec.getvalue(), f"{brand}.png", "image/png", key=f"dl_{i}")

# --------------------------------------
# RENDER (FAST STREAMING STYLE)
# --------------------------------------
if col2.button("🎨 RENDER"):
    with st.spinner("🎨 Fast Rendering 8K Intel..."):
        img_render = hf_gen_image(enhance_prompt(f"{prompt}, ultra realistic, 8k, Seat Cover interior Desgins, photorealistic automotive engineering")) 
        if img_render:
            st.image(img_render)
            st.session_state.count += 1
            st.session_state.global_count += 1
            # --- PATCH: DOWNLOAD RENDER ---
            buf_render = io.BytesIO()
            img_render.save(buf_render, format="PNG")
            st.download_button("🖼️ Save 8K Render", buf_render.getvalue(), "render_8k.png", "image/png")
