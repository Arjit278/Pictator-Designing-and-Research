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

if not HF_TOKEN:
    st.error("❌ HF_TOKEN missing - add in Streamlit secrets")

# --------------------------------------
# 🌐 WEBSITE FETCH
# --------------------------------------
def fetch_real_website(brand, part="automotive"):
    try:
        # 🎯 Build smart query based on part
        if part == "seat":
            query = f"{brand} seat cover collection leather car seat cover product page"
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
            if any(domain in link for domain in TRUSTED_DOMAINS):
                if any(k in link.lower() for k in [
                    "seat-cover", "seat-covers", "car-seat-cover",
                    "collection", "custom-seat", "products"
                ]):
                    return link

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

def get_clean_images(query):
    try:
        r = requests.get(
            "https://serpapi.com/search",
            params={
                "engine": "google_images",
                "q": query + " car seat cover leather premium",
                "api_key": SERP_API_KEY
            },
            timeout=10
        )

        results = r.json().get("images_results", [])

        clean = []
        for img in results:
            url = img.get("original")

            if url and any(k in url.lower() for k in ["seat", "cover", "leather"]):
                clean.append(url)

        return clean[:3]

    except:
        return []
        
def generate_design_blocks(prompt):
    p = prompt.lower()

    blocks = []

    # --------------------------------------
    # 🎯 DETECT DESIGN INTENT FROM PROMPT
    # --------------------------------------
    if "quilt" in p:
        blocks.append({
            "title": "🔷 Diamond Quilted (Luxury)",
            "score": "9/10",
            "desc": "Premium cushioned design with strong visual appeal.",
            "elements": [
                "Diamond stitching",
                "Dual tone contrast",
                "Soft foam padding"
            ],
            "best_for": "Luxury builds",
            "keyword": "diamond quilted seat cover leather"
        })

    if "sport" in p or "racing" in p:
        blocks.append({
            "title": "🔷 Sport Racing Design",
            "score": "8/10",
            "desc": "Aggressive sporty styling for performance interiors.",
            "elements": [
                "Side bolsters",
                "Contrast stripes",
                "Firm foam support"
            ],
            "best_for": "Sporty cars",
            "keyword": "sport racing seat cover red black"
        })

    if "minimal" in p or "clean" in p:
        blocks.append({
            "title": "🔶 Minimal Flat Design",
            "score": "7/10",
            "desc": "Clean and modern flat surface styling.",
            "elements": [
                "Straight stitching",
                "Matte finish",
                "Low padding"
            ],
            "best_for": "Budget + clean builds",
            "keyword": "minimal seat cover flat design"
        })

    if "puff" in p or "cushion" in p:
        blocks.append({
            "title": "🔷 Puffy Cushion Design",
            "score": "8/10",
            "desc": "Highly padded comfort-focused seat design.",
            "elements": [
                "Extra foam layering",
                "Soft touch finish",
                "Bulky stitched panels"
            ],
            "best_for": "Long drives comfort",
            "keyword": "puffy seat cover cushion thick"
        })

    # --------------------------------------
    # 🔥 FALLBACK (AUTO GENERATE IF NOTHING MATCHED)
    # --------------------------------------
    if not blocks:
        blocks = [
            {
                "title": "🔷 Premium Leather Pattern",
                "score": "8/10",
                "desc": "Balanced premium design based on current market trends.",
                "elements": [
                    "Contrast stitching",
                    "Ergonomic contour",
                    "Dual tone finish"
                ],
                "best_for": "All segment cars",
                "keyword": f"{prompt} seat cover design"
            },
            {
                "title": "🔶 Comfort-Oriented Build",
                "score": "7/10",
                "desc": "Focus on comfort + usability.",
                "elements": [
                    "Soft padding",
                    "Breathable fabric",
                    "Flat structure"
                ],
                "best_for": "Wagon R, Swift",
                "keyword": f"{prompt} comfortable seat cover"
            }
        ]

    return blocks
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

TRUSTED_DOMAINS = [
    "autofurnish.com",
    "autofit.in",
    "autotextile.com",
    "cncstitching.com",
    "seatcoversunlimited.com",
    "foamvilla.com",
    "sa.made-in-china.com",
    "autoclint.com",
    "autoform.in",
    "coverking.com",
    "katzkin.com",
    "amazon.in",
    "cardekho.com",
]
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
    seen = set()

    p = prompt.lower()

    # --------------------------------------
    # 🔍 DETECT PART
    # --------------------------------------
    detected_part = "seat" if "seat" in p else "automotive"

    # --------------------------------------
    # 🧠 MATERIAL MAP
    # --------------------------------------
    PART_MATERIAL_MAP = {
        "seat": "PU Leather / Nappa / Fabric",
    }

    # --------------------------------------
    # 🔥 STRICT DOMAIN FILTER
    # --------------------------------------
    def is_trusted(url):
        if not url:
            return False
        return any(domain in url for domain in TRUSTED_DOMAINS)

    # --------------------------------------
    # 🔄 MAIN LOOP
    # --------------------------------------
    for item in specs:
        if not isinstance(item, dict):
            continue

        brand = (item.get("Brand") or "").strip()

        if not brand:
            continue

        # 🔥 NORMALIZE BRAND NAME (REMOVE DUPLICATE VARIANTS)
        brand_key = brand.lower().replace(" ", "").replace("-", "")

        if brand_key in seen:
            continue
        seen.add(brand_key)

        # --------------------------------------
        # 🌐 WEBSITE (STRICT CONTROL)
        # --------------------------------------
        website = item.get("Website")

        if not is_trusted(website):
            website = fetch_real_website(brand, detected_part)

        # 🔥 FINAL CHECK — ONLY TRUSTED DOMAINS ALLOWED
        if not is_trusted(website):
            continue  # ❌ skip completely

        # --------------------------------------
        # 🧠 MATERIAL
        # --------------------------------------
        material = item.get("Material") or PART_MATERIAL_MAP.get(detected_part)

        # --------------------------------------
        # 📦 BUILD CLEAN OBJECT
        # --------------------------------------
        normalized.append({
            "Brand": brand,
            "Vehicle": item.get("Vehicle", "Passenger Car"),
            "Type": item.get("Type", detected_part),
            "Material": material,
            "Strength": item.get("Strength", "Optimized"),
            "Description": item.get("description", ""),
            "Website": website
        })

    if not normalized:
    st.warning("⚠️ No trusted suppliers found.")

    return normalized
    
# --------------------------------------
# 🎯 TREND KEYWORDS (NEW FIX)
# --------------------------------------
TREND_KEYWORDS = [
    "diamond quilted",
    "carbon fiber texture",
    "minimalist flat design",
    "luxury napa leather",
    "sport racing style",
    "perforated leather",
    "premium stitching",
    "futuristic interior",
    "ergonomic contour",
    "high contrast dual tone",
    "matte finish",
    "3D embossed pattern"
]

# --------------------------------------
# IMAGE ENGINE (HF)
# --------------------------------------

def hf_gen_image(prompt):
    try:
        model = SELECTED_MODEL
        model_url = f"https://router.huggingface.co/hf-inference/models/{model}"

        headers = {
            "Authorization": f"Bearer {HF_TOKEN}",
            "Content-Type": "application/json"
        }

        payload = {
            "inputs": prompt,
            "parameters": {
                "guidance_scale": 7.5,
                "num_inference_steps": 28,
                "width": 1024,
                "height": 1024
            }
        }

        # --------------------------------------
        # 🎯 MODEL-SPECIFIC TUNING
        # --------------------------------------
        if "Lightning" in model:
            payload["parameters"].update({
                "num_inference_steps": 8,
                "width": 768,
                "height": 768
            })

        if "Krea" in model:
            payload["parameters"].update({
                "guidance_scale": 8.5,
                "num_inference_steps": 30
            })

        # --------------------------------------
        # 🚀 PRIMARY REQUEST
        # --------------------------------------
        r = requests.post(model_url, headers=headers, json=payload, timeout=60)

        # --------------------------------------
        # ✅ HANDLE SUCCESS
        # --------------------------------------
        if r.status_code == 200:
            try:
                return Image.open(io.BytesIO(r.content)).convert("RGB")
            except:
                print("⚠️ Response not a valid image")
                print("CONTENT-TYPE:", r.headers.get("content-type"))

        # --------------------------------------
        # 🔍 DEBUG (IMPORTANT)
        # --------------------------------------
        print(f"❌ HF PRIMARY FAILED | Model: {model}")
        print("STATUS:", r.status_code)
        print("RESPONSE:", r.text[:200])

        if r.status_code == 401:
            print("🔐 Invalid or missing HF token")

        if r.status_code == 429:
            print("⚠️ Rate limit hit")

        # --------------------------------------
        # 🔥 FALLBACK MODEL
        # --------------------------------------
        fallback = "black-forest-labs/FLUX.1-schnell"
        fallback_url = f"https://router.huggingface.co/hf-inference/models/{fallback}"

        print("⚡ Switching to fallback:", fallback)

        r2 = requests.post(
            fallback_url,
            headers=headers,
            json={
                "inputs": prompt,
                "parameters": {
                    "width": 1024,
                    "height": 1024
                }
            },
            timeout=60
        )

        if r2.status_code == 200:
            try:
                return Image.open(io.BytesIO(r2.content)).convert("RGB")
            except:
                print("⚠️ Fallback response not image")

        print("❌ FALLBACK FAILED")
        print("STATUS:", r2.status_code)
        print("RESPONSE:", r2.text[:200])

        return None

    except Exception as e:
        print("🔥 HF ERROR:", e)
        return None

def enhance_prompt(prompt):
    base = f"{prompt}, automotive interior, ultra detailed, 8k, professional lighting"

    if "Krea" in SELECTED_MODEL:
        return base + ", cinematic, photorealistic, leather texture, luxury finish"

    elif "Qwen" in SELECTED_MODEL:
        return base + ", clean composition, structured design, product render"

    elif "Lightning" in SELECTED_MODEL:
        return base + ", sharp, high contrast, fast render"

    return base
    
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
        - Share European and international market designs with weblinks 
        - Prefer Indian aftermarket interior brands with weblinks
        - Include latest trends 2026 like Ultra-Quilt (Diamond), Carbon Fiber Texture, Minimalist "Flat" Grain, "GSM" (Grams per Square Meter) of the material
        - Display direct Website like https://www.autofurnish.com/collections/oem-style-factory-fitted-seat-covers, autofurnish.com/collections/oem-style-factory-fitted-seat-covers
        - Also show trends in world in europe with websites and links with URL working properly
    
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
    res.ai_concept = hf_gen_image(enhance_prompt(prompt))
    
# --------------------------------------
# UI
# --------------------------------------
prompt = st.text_area("Enter Topic")

# --------------------------------------
# 🎯 STRUCTURED PROMPT BUILDER (NEW)
# --------------------------------------
st.subheader("🧠 Smart Design Builder")

colA, colB, colC = st.columns(3)

with colA:
    car_model = st.text_input("Car Model", "Wagon-R, Grand Vitara")
    seat_shape = st.selectbox("Seat Shape", ["bucket", "flat", "hybrid"])

with colB:
    material = st.selectbox("Material", ["PU leather", "Nappa leather", "synthetic", "fabric"])
    stitching = st.selectbox("Stitching", ["diamond", "hex", "straight"])

with colC:
    color = st.text_input("Color Combo", "black + tan")
    use_case = st.selectbox("Use Case", ["luxury", "budget", "sporty"])

lighting = st.selectbox("Lighting", ["studio", "ambient", "showroom", "blueprint"])
quality = "8k photorealistic"

# --------------------------------------
# 🔥 FINAL PROMPT (AUTO GENERATED)
# --------------------------------------
structured_prompt = f"""
Automotive seat cover design for {car_model},
{seat_shape} seats, {material},
{stitching} stitching pattern,
{color} color combination,
{use_case} design style,
{lighting} lighting,
ultra detailed textures, {quality}
"""

# 👉 Combine with user input (VERY IMPORTANT)
final_prompt = f"{prompt}, {structured_prompt}"
col1, col2 = st.columns(2)

if col1.button("🚀 EXECUTE"):
    res = AnalysisResults()

    with st.status("🚀 Engineering Data...", expanded=True) as status:

        # --------------------------------------
        # 🧠 LLM TREND ANALYSIS
        # --------------------------------------
        res.rca_intel, res.rca_status = call_openrouter_with_fallback_requests(
            f"Generate automotive trends: {prompt}", OPENROUTER_API_KEY
        )

        # --------------------------------------
        # 📦 SUPPLIER DATA
        # --------------------------------------
        res.specs_raw, _ = call_openrouter_with_fallback_requests(
            f"""
            Return ONLY VALID JSON.

            Generate EXACTLY 3 REAL seat cover vendors for: {prompt}

            Include:
            - Brand
            - Material
            - Description
            - Website (working product/collection page)

            Output format:
            [
                {{
                    "Brand": "",
                    "Material": "",
                    "Description": "",
                    "Website": ""
                }}
            ]
            """,
            OPENROUTER_API_KEY
        )

        # --------------------------------------
        # 🎨 IMAGE GENERATION (MAIN FIX)
        # --------------------------------------
        clean_prompt = f"{car_model} car seat cover {material} {stitching} {color} {use_case}"

        res.ai_concept = hf_gen_image(enhance_prompt(clean_prompt))

        status.update(label="✅ Analysis Complete", state="complete")

     # --------------------------------------
    # 🔧 PREPARE SPECS (ONLY ONCE - IMPORTANT)
    # --------------------------------------
    raw_specs = safe_json_extract(res.specs_raw)
    
    # 🔐 Store raw LLM output for admin
    st.session_state.admin_logs.append({
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "prompt": prompt,
        "raw_output": res.specs_raw
    })
    
    specs = normalize_specs(raw_specs, prompt)
             
     # --------------------------------------
    # 📦 DOWNLOAD ALL (ZIP - UPDATED)
    # --------------------------------------
    zip_buf = io.BytesIO()
    
    with zipfile.ZipFile(zip_buf, "w") as zf:
    
        # --------------------------------------
        # 📄 REPORT
        # --------------------------------------
        report = f"""
    TOPIC: {prompt}
    
    TRENDS:
    {res.rca_intel}
    
    SPECS:
    {json.dumps(specs, indent=2)}
    """
        zf.writestr("full_report.txt", report)
    
        # --------------------------------------
        # 🎨 MAIN IMAGE (NEW SYSTEM)
        # --------------------------------------
        if 'main_img' in locals():
    
            try:
                if isinstance(main_img, Image.Image):
                    img_byte = io.BytesIO()
                    main_img.save(img_byte, format="PNG")
                    zf.writestr("concept_design.png", img_byte.getvalue())
    
                elif isinstance(main_img, str):
                    # download image from URL
                    r = requests.get(main_img, timeout=10)
                    if r.status_code == 200:
                        zf.writestr("concept_design.png", r.content)
    
            except Exception as e:
                st.error(f"Error saving main image: {e}")
    
    # --------------------------------------
    # 📥 DOWNLOAD BUTTON
    # --------------------------------------
    st.sidebar.download_button(
        "📦 Download All Files (ZIP)",
        zip_buf.getvalue(),
        "Pictator_Package.zip",
        "application/zip"
    )
        
    # --------------------------------------
    # DISPLAY
    # --------------------------------------
    st.subheader("📊 Current Trends")
    
    if res.rca_intel and str(res.rca_intel).strip().lower() != "none":
        st.markdown(res.rca_intel)
    else:
        st.info("⚠️ No trend data available. Try refining your prompt or check API keys.")
    
        # --- PATCH: DOWNLOAD CONCEPT ---
        buf_concept = io.BytesIO()
        res.ai_concept.save(buf_concept, format="PNG")
        st.download_button("💾 Save Concept Image", buf_concept.getvalue(), "concept.png", "image/png")

   
    # --------------------------------------
# 🎨 HERO DESIGN IMAGE (FINAL FIX)
# --------------------------------------
st.subheader("🎨 Featured Design Concept")

def generate_main_image(prompt):
    strong_prompt = f"""
    {prompt},
    car seat cover interior,
    {material}, {stitching} stitching,
    {color} color,
    premium automotive interior,
    no logo, no watermark,
    ultra realistic, 8k
    """

    # 1️⃣ AI
    img = hf_gen_image(enhance_prompt(strong_prompt))
    if img:
        return img

    # 2️⃣ SERP fallback
    try:
        r = requests.get(
            "https://serpapi.com/search",
            params={
                "engine": "google_images",
                "q": strong_prompt,
                "api_key": SERP_API_KEY
            },
            timeout=10
        )

        imgs = r.json().get("images_results", [])

        clean = []
        for im in imgs:
            url = im.get("original")
            if url and all(x not in url.lower() for x in ["logo", "icon", "svg"]):
                clean.append(url)

        return clean[0] if clean else None

    except:
        return None


clean_prompt = f"{car_model} {material} {stitching} seat cover {color} {use_case}"
main_img = generate_main_image(clean_prompt)

# --------------------------------------
# ✅ FIXED DISPLAY (NO CRASH)
# --------------------------------------
if isinstance(main_img, Image.Image):
    st.image(main_img)

elif isinstance(main_img, str) and main_img.startswith("http"):
    st.image(main_img)

else:
    st.warning("⚠️ AI image failed — loading fallback")

    fallback_imgs = get_clean_images(clean_prompt)

    if fallback_imgs:
        st.image(fallback_imgs[0])
    else:
        st.error("❌ No image available")    
            
    # --- PATCH: DOWNLOAD TEXT REPORT ---
    report_text = f"ANALYSIS: {prompt}\n\nTRENDS:\n{res.rca_intel}\n\nSPECS:\n{json.dumps(specs, indent=2)}"
    st.sidebar.download_button("📄 Download Full Report", report_text, f"report_{prompt[:10]}.txt", "text/plain")

    # --------------------------------------
    # 🌍 MARKET INTELLIGENCE (CLEAN LINKS)
    # --------------------------------------
    st.subheader("🌍 Market Intelligence & Live Sourcing")
    
    links = []
    
    # --------------------------------------
    # 🔍 COLLECT FROM SPECS
    # --------------------------------------
    for s in specs:
        brand = s.get("Brand")
        site = s.get("Website") or fetch_real_website(brand, "seat")
    
        if site and site not in links:
            links.append(site)
    
    # --------------------------------------
    # 🔁 FILL UP TO 6 LINKS
    # --------------------------------------
    tries = 0
    while len(links) < 6 and tries < 10:
        extra = fetch_real_website(prompt.split()[0], "seat")
        if extra and extra not in links:
            links.append(extra)
        tries += 1
    
    # --------------------------------------
    # 🎯 DISPLAY CLEAN LINKS
    # --------------------------------------
    for link in links[:6]:
        st.markdown(f"🔗 {link}")
    
    # --------------------------------------
    # 🧠 TEXT STYLE OUTPUT
    # --------------------------------------
    st.markdown("### 🇮🇳 Indian Market Picks")
    
    for item in indian:
        brand = item.get("Brand", "Unknown")
        desc = item.get("Description", "Automotive interior solution provider")
        material = item.get("Material", "")
        website = item.get("Website") or fetch_real_website(brand, "seat")
    
        st.markdown(f"""
    **{brand}**  
    {desc}  
    Material Focus: {material}  
    🔗 {website}
    """)
    
    st.markdown("---")
    
    st.markdown("### 🌍 International Benchmarks")
    
    for item in global_brands:
        brand = item.get("Brand", "Unknown")
        desc = item.get("Description", "Global automotive design supplier")
        material = item.get("Material", "")
        website = item.get("Website") or fetch_real_website(brand, "seat")
    
        st.markdown(f"""
    **{brand}**  
    {desc}  
    Material Focus: {material}  
    🔗 {website}
    """)
    
    # --------------------------------------
    # 🎨 DYNAMIC DESIGN PATTERNS (AI DRIVEN)
    # --------------------------------------
    dynamic_patterns = [
        "Diamond Quilted Luxury Pattern",
        "Carbon Fiber Texture Inserts",
        "Minimal Flat Surface Design",
        "Hexagonal Sport Stitching",
        "Perforated Ventilated Panels",
        "Dual Tone High Contrast Layout",
        "3D Embossed Foam Back Structure",
        "Racing Stripe Accent Design",
    ]
    
    random.shuffle(dynamic_patterns)
    
    st.markdown("---")
    
    # --------------------------------------
    # 🎯 DESIGN STORY BLOCKS (LIKE YOUR FORMAT)
    # --------------------------------------
    st.subheader("🎨 Seat Cover Design Directions")
    
    designs = generate_design_blocks(prompt)
    
    for d in designs:
        st.markdown(f"""
    ### {d['title']}
    🔥 {d['score']}
    
    {d['desc']}
    
    **Design Elements:**
    """)
    
        for e in d["elements"]:
            st.markdown(f"- {e}")
    
        st.markdown(f"""
    **Best For:** {d['best_for']}
    """)
    
        # 🔗 Get REAL website
        brand = specs[0]["Brand"] if specs else d["keyword"]
        site = fetch_real_website(brand, "seat")
    
        if site:
            st.link_button("🌐 View Real Collection", site)
    
            # 🔥 REAL IMAGES FROM SAME WEBSITE
            query = f"{d['keyword']} {material} {color} car interior {random.randint(1,9999)}"
            imgs = get_clean_images(query)
    
            if imgs:
                cols = st.columns(len(imgs))
                for i, im in enumerate(imgs):
                    cols[i].image(im)
            else:
                st.info("No clean images found, try another source")
    
        st.markdown("---")
    # --------------------------------------
    # 🧠 MATERIAL INTELLIGENCE (DYNAMIC)
    # --------------------------------------
    materials_dynamic = [
        "Nappa Leather (Luxury Builds)",
        "PU Synthetic Leather (Affordable + Durable)",
        "Alcantara Suede (Sport Segment)",
        "High GSM Breathable Fabric",
        "Hybrid Leather + Mesh Structures"
    ]
    
    random.shuffle(materials_dynamic)
    
    st.markdown("""
    ### 🧠 Material & Engineering Insight
    """)
    
    for m in materials_dynamic[:3]:
        st.markdown(f"- {m}")
    
    st.markdown("""
    Modern seat engineering is shifting toward:
    - Thermal comfort zones
    - Pressure-distribution foam layers
    - Stitch-density optimization
    - Modular replaceable panels
    """)
    
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
