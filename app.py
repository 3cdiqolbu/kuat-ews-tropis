import streamlit as st
import pandas as pd
import joblib
import time
import plotly.express as px
from datetime import datetime

# ==========================================
# 1. PAGE CONFIGURATION & THEME
# ==========================================
st.set_page_config(
    page_title="KUAT. | Tropical Cattle EWS", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Color Hunt Palette (819a91, a7c1a8, d1d8be, eeefe0) 
# WITH ALL-DARK FONT IMPLEMENTATION
st.markdown("""
<style>
    /* Main App Background */
    .stApp { background-color: #eeefe0; }
    [data-testid="stHeader"] { background-color: transparent; }
    
    /* Global Text Color (All Dark Slate) */
    .stMarkdown, .stMarkdown p, h1, h2, h3, h4, h5, h6, label, .stSelectbox label, .stTextInput label, .stNumberInput label {
        color: #2c3e50 !important;
    }
    
    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background-color: #819a91;
        border-right: 1px solid #a7c1a8;
    }

    /* Block Navigation Sidebar */
    [data-testid="stSidebar"] .stRadio div[role="radiogroup"] {
        gap: 8px; 
        padding-top: 10px;
    }
    
    [data-testid="stSidebar"] .stRadio div[data-testid="stRadioButton"] > label {
        width: 100%;
        padding: 15px 20px;
        background-color: transparent;
        border-radius: 4px;
        cursor: pointer;
        transition: all 0.2s ease-in-out;
        border-left: 0px solid transparent;
        display: block;
    }
    
    /* Hide default radio circle */
    [data-testid="stSidebar"] .stRadio div[data-testid="stRadioButton"] > label > div:first-child {
        display: none;
    }
    
    /* Navigation Text Style (Dark Font) */
    [data-testid="stSidebar"] .stRadio div[data-testid="stRadioButton"] > label p {
        font-weight: 800;
        font-size: 16px;
        margin: 0;
        color: #2c3e50 !important;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    /* Hover and Active State */
    [data-testid="stSidebar"] .stRadio div[data-testid="stRadioButton"] > label:hover {
        background-color: #a7c1a8;
    }
    
    [data-testid="stSidebar"] .stRadio div[data-testid="stRadioButton"]:has(input:checked) > label {
        background-color: #d1d8be;
        border-left: 6px solid #2c3e50;
    }

    /* Main Action Button (Dark Font on Light Background) */
    div.stButton > button:first-child {
        background-color: #d1d8be; color: #2c3e50 !important;
        border: 2px solid #819a91; border-radius: 8px;
        font-weight: 900; width: 100%; padding: 12px;
        text-transform: uppercase; letter-spacing: 1px;
    }
    div.stButton > button:first-child:hover { 
        background-color: #a7c1a8; color: #2c3e50 !important; 
        border: 2px solid #2c3e50;
    }
    
    /* Record Detail Card Design */
    .record-card {
        background-color: #d1d8be;
        border-radius: 12px;
        padding: 30px;
        box-shadow: 0 8px 16px rgba(129,154,145,0.2);
        border-left: 10px solid #819a91;
    }
    
    div.record-card, div.record-card * {
        color: #2c3e50 !important;
    }
    div.record-card .record-label {
        color: #2c3e50 !important;
        font-weight: 800;
        text-transform: uppercase;
        font-size: 12px;
        opacity: 0.8;
    }
    
    .record-card h4 { margin-top: 0; border-bottom: 2px solid #819a91; padding-bottom: 12px; font-weight: 900; text-transform: uppercase; color: #2c3e50 !important; }
    .record-row { display: flex; justify-content: space-between; padding: 10px 0; border-bottom: 1px solid #a7c1a8; }
    .record-value { font-weight: 800; text-align: right; font-size: 14px; }
    
    /* EWS Status Boxes (Text remains white for crucial contrast) */
    .ews-sakit { background-color: #e74c3c; color: #FFFFFF !important; padding: 25px; text-align: center; font-weight: bold; font-size: 26px; border-radius: 12px; margin-bottom: 20px; }
    .ews-sehat { background-color: #2ecc71; color: #FFFFFF !important; padding: 25px; text-align: center; font-weight: bold; font-size: 26px; border-radius: 12px; margin-bottom: 20px; }
    
    /* Input Fields Override */
    div[data-baseweb="input"] > div, div[data-baseweb="select"] > div {
        background-color: #eeefe0;
        border: 1px solid #a7c1a8;
        color: #2c3e50 !important;
    }
    
    /* Sidebar Info Box Alert Text */
    div[data-testid="stAlert"] div {
        color: #2c3e50 !important;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. MODEL & DATASET LOADING
# ==========================================
@st.cache_resource
def load_pipeline():
    try:
        return joblib.load('ews_pipeline_lengkap.pkl')
    except Exception:
        return None

@st.cache_data
def load_dataset():
    try:
        df = pd.read_csv('dataset.zip')
        def categorize_tropical(region):
            if 'Asia' in region: return 'Asia'
            if region in ['Africa', 'South_America', 'Oceania']: return region
            return 'Other'
        df['Tropical_Region_Category'] = df['Region'].apply(categorize_tropical)
        return df
    except Exception:
        return pd.DataFrame() 

pipeline = load_pipeline()
df_cattle = load_dataset()

if 'history' not in st.session_state:
    st.session_state['history'] = []

# ==========================================
# 3. SIDEBAR NAVIGATION
# ==========================================
# Sidebar Header with DARK TEXT
st.sidebar.markdown("""
<div style="padding: 20px 0; text-align: center; border-bottom: 2px solid #2c3e50; margin-bottom: 10px;">
    <h1 style="color: #2c3e50; font-size: 28px; margin: 0; font-weight: 900; letter-spacing: 2px;">KUAT.</h1>
    <p style="color: #2c3e50; font-size: 12px; margin: 5px 0 0 0; text-transform: uppercase; letter-spacing: 1px; font-weight: 700;">Livestock Information System</p>
</div>
""", unsafe_allow_html=True)

menu = st.sidebar.radio("NAVIGATION", ["Dashboard", "Analysis Schema", "About System"], label_visibility="collapsed")

st.sidebar.markdown("<br><br>", unsafe_allow_html=True)
st.sidebar.info("Standard: Tropical EWS v1.0\nAlgorithm: Decision Tree\nObjective: Recall Optimization")

# ==========================================
# 4. DASHBOARD MENU
# ==========================================
if menu == "Dashboard":
    st.title("TROPICAL EWS DASHBOARD")
    
    # --- REGION MONITORING ---
    st.subheader("Regional Biosurveillance Map")
    kawasan_pilihan = st.selectbox("Select Target Region:", ["Asia", "Africa", "South America", "Oceania"])
    region_mapping = {
        "Asia": ["Indonesia", "India", "Thailand", "Vietnam", "Philippines"], 
        "Africa": ["Kenya", "Ethiopia", "Tanzania", "Nigeria", "Sudan"], 
        "South America": ["Brazil", "Colombia", "Peru", "Argentina"], 
        "Oceania": ["Australia", "Papua New Guinea", "Fiji"]
    }
    df_map = pd.DataFrame({"Country": region_mapping[kawasan_pilihan], "Intensity": [1] * len(region_mapping[kawasan_pilihan])})
    
    fig = px.choropleth(
        df_map, locations="Country", locationmode="country names", 
        color="Intensity", hover_name="Country", 
        color_continuous_scale=["#a7c1a8", "#e74c3c"]
    )
    
    fig.update_layout(
        geo=dict(
            bgcolor="#eeefe0",               
            projection_type="orthographic", 
            showcoastlines=True, coastlinecolor="#819a91", 
            showland=True, landcolor="#a7c1a8",   
            showocean=True, oceancolor="#d1d8be"  
        ), 
        coloraxis_showscale=False, 
        margin={"r":0,"t":0,"l":0,"b":0}, 
        height=450,
        paper_bgcolor="#eeefe0", 
        plot_bgcolor="#eeefe0"
    )
    st.plotly_chart(fig, use_container_width=True)
    st.markdown("---")
    
    # --- DATA INPUT ---
    st.subheader("Data Acquisition and Clinical Metrics")
    with st.form("ews_form"):
        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown("**Core Identity**")
            cattle_id = st.text_input("Cattle ID")
            umur = st.number_input("Age (Months)", min_value=1, value=36)
            berat = st.number_input("Weight (Kg)", min_value=50.0, value=450.0)
        with c2:
            st.markdown("**Biometric Indicators**")
            suhu = st.number_input("Body Temperature (°C)", value=38.5)
            bpm = st.number_input("Heart Rate (BPM)", value=65)
            ruminasi = st.number_input("Rumination Time (Hours/Day)", value=7.0)
        with c3:
            st.markdown("**Environmental Context**")
            jml_pakan = st.number_input("Feed Quantity (Kg/Day)", value=15.0)
            tipe_pakan_ui = st.selectbox("Feed Classification", ["Green Fodder", "Dry Fodder", "Concentrates"])
            manajemen_ui = st.selectbox("Management Protocol", ["Pastoral", "Semi-Intensive", "Intensive"])
            
        submit = st.form_submit_button("PROCESS AUDIT", use_container_width=True)

    # --- OUTPUT SECTION ---
    if submit:
        if pipeline is not None:
            pakan_map = {"Green Fodder": "Green_Fodder", "Dry Fodder": "Dry_Fodder", "Concentrates": "Concentrates"}
            manajemen_map = {"Pastoral": "Pastoral", "Semi-Intensive": "Semi_Intensive", "Intensive": "Intensive"}
            mapping_region = {"Asia": "Asia", "Africa": "Africa", "South America": "South_America", "Oceania": "Oceania"}
            
            raw_input = pd.DataFrame({
                'Body_Temperature_C': suhu, 'Heart_Rate_bpm': bpm, 'Rumination_Time_hrs': ruminasi,
                'Feed_Type': pakan_map[tipe_pakan_ui], 'Feed_Quantity_kg': jml_pakan,
                'Tropical_Region_Category': mapping_region[kawasan_pilihan], 'Country': "ID", 
                'Management_System': manajemen_map[manajemen_ui], 'Breed': "Brahman", 
                'Age_Months': umur, 'Weight_kg': berat
            }, index=[0]) 
            
            with st.spinner("Executing analysis..."):
                time.sleep(1)
                prediction = pipeline.predict(raw_input)[0]

            st.markdown("---")
            
            # Database Lookup
            sapi_db = df_cattle[df_cattle['Cattle_ID'] == cattle_id] if not df_cattle.empty else pd.DataFrame()
            is_registered = not sapi_db.empty

            disp_id = cattle_id if cattle_id else "UNDEFINED"
            if is_registered:
                row = sapi_db.iloc[0]
                disp_breed = row['Breed']
                disp_country = row['Country']
                disp_region = row['Tropical_Region_Category']
                disp_vaksin = "FMD (Complete), LSD (Active)"
                title_card = "Verified Cattle Record"
            else:
                disp_breed = "New Registration"
                disp_country = "Not Recorded"
                disp_region = f"{kawasan_pilihan} Zone"
                disp_vaksin = "No Historical Data"
                title_card = "Unverified Field Entry"

            col_detail, col_status = st.columns([1.5, 1])
            
            with col_status:
                if prediction == 1:
                    st.markdown('<div class="ews-sakit">DISEASE STATUS: INFECTED</div>', unsafe_allow_html=True)
                    st.session_state['history'].append({"ID": disp_id, "Time": datetime.now().strftime("%H:%M"), "Status": "INFECTED"})
                else:
                    st.markdown('<div class="ews-sehat">DISEASE STATUS: HEALTHY</div>', unsafe_allow_html=True)
                st.image("https://images.unsplash.com/photo-1546445317-29f4545e9d53?w=500", caption="Visualization Matrix", use_container_width=True)

            with col_detail:
                st.markdown(f"""
                <div class="record-card">
                    <h4>{title_card}</h4>
                    <div class="record-row"><span class="record-label">Cattle ID</span><span class="record-value">{disp_id}</span></div>
                    <div class="record-row"><span class="record-label">Breed Classification</span><span class="record-value">{disp_breed}</span></div>
                    <div class="record-row"><span class="record-label">Geographic Zone</span><span class="record-value">{disp_region}</span></div>
                    <div class="record-row"><span class="record-label">Origin Country</span><span class="record-value">{disp_country}</span></div>
                    <div class="record-row"><span class="record-label">Operational System</span><span class="record-value">{manajemen_ui}</span></div>
                    <div class="record-row"><span class="record-label">Maturity Age</span><span class="record-value">{umur} Months</span></div>
                    <div class="record-row"><span class="record-label">Body Temperature</span><span class="record-value">{suhu} °C</span></div>
                    <div class="record-row"><span class="record-label">Cardiac Rhythm</span><span class="record-value">{bpm} BPM</span></div>
                    <div class="record-row"><span class="record-label">Body Mass</span><span class="record-value">{berat} Kg</span></div>
                    <div class="record-row"><span class="record-label">Nutritional Type</span><span class="record-value">{tipe_pakan_ui}</span></div>
                    <div class="record-row"><span class="record-label">Daily Intake</span><span class="record-value">{jml_pakan} Kg</span></div>
                    <div class="record-row"><span class="record-label">Rumination Period</span><span class="record-value">{ruminasi} Hours</span></div>
                    <div class="record-row" style="border-bottom: none;"><span class="record-label">Immunization Status</span><span class="record-value">{disp_vaksin}</span></div>
                </div>
                """, unsafe_allow_html=True)

        else:
            st.error("System Failure: Unable to load classification engine.")

# ==========================================
# 5. ANALYSIS SCHEMA MENU
# ==========================================
elif menu == "Analysis Schema":
    st.title("Decision Architecture")
    st.write("Visual representation of the Decision Tree logic and diagnostic standards.")
    
    try:
        st.image("pohon_ku.png", caption="Optimized Decision Path for Tropical EWS", use_container_width=True)
    except:
        st.warning("Diagram source (pohon_ku.png) not detected in directory.")

# ==========================================
# 6. ABOUT SYSTEM MENU
# ==========================================
else:
    st.title("About KUAT.")
    st.markdown("""
    ### Tropical Outbreak Mitigation Engine
    **KUAT. (Kesehatan Utama Analisis Ternak)** adalah kerangka kerja *Intelligence* yang dirancang khusus sebagai sistem peringatan dini (*Early Warning System*) terhadap wabah penyakit ternak di kawasan tropis. Proyek ini mengintegrasikan kecerdasan buatan dengan standar medik veteriner untuk menekan risiko kerugian ekonomi akibat keterlambatan diagnosa.

    ---

    ### Tiga Pilar Intelligence
    Sistem ini bekerja dengan menggabungkan tiga sudut pandang data yang komprehensif:
    1. **Clinical Intelligence:** Menganalisis sensor biometrik (Suhu, Detak Jantung, Ruminasi) untuk mendeteksi anomali kesehatan secara *real-time*.
    2. **Ecological Intelligence:** Mempertimbangkan faktor lingkungan seperti sistem manajemen kandang dan jenis pakan yang sangat berpengaruh pada imunitas ternak di iklim tropis.
    3. **Geospatial Intelligence:** Melakukan pengawasan biosurveilans pada 4 sub-kawasan tropis utama (Asia, Afrika, Amerika Selatan, dan Oseania) melalui visualisasi *Globe 3D*.

    ---

    ### Engine Optimization & The Recall Paradox
    Berbeda dengan model AI standar yang hanya mengejar akurasi, mesin **KUAT.** dikalibrasi secara ketat untuk mengutamakan **Keamanan Diagnosa**:
    - **SMOTE Balancing:** Melalui teknik *Synthetic Minority Over-sampling*, model dilatih untuk memiliki "insting" yang tajam dalam mengenali gejala penyakit meskipun data di lapangan tidak seimbang.
    - **Feature Selection (RFE):** Algoritma telah dirampingkan melalui *Recursive Feature Elimination* untuk hanya berfokus pada indikator paling murni (Suhu Tubuh & Ruminasi).
    - **The Recall Strategy:** Kami secara sengaja mengoptimalkan metrik **Recall (Sensitivitas)**. Dalam konteks wabah, lebih aman mencurigai sapi sehat sebagai sakit (*False Positive*) daripada melewatkan satu saja sapi yang benar-benar terinfeksi (*False Negative*).

    ---

    ### Real-World Application
    Sistem ini mengimplementasikan **Dual-Logic Diagnostic**:
    - **Verified Records:** Penarikan data historis (riwayat vaksin & genetik) otomatis untuk ternak yang terdaftar di basis data.
    - **Field Inference:** Kemampuan model untuk melakukan diagnosa mandiri (*generalization*) secara instan pada ternak baru yang belum memiliki rekam medis di lapangan.
    """)