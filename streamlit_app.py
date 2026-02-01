# app.py - UPDATED FOR STREAMLIT 1.29+
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import plotly
import sys
import os
from datetime import datetime

# ========== PAGE CONFIG (MUST BE FIRST) ==========
st.set_page_config(
    page_title="Healthcare Analytics Platform",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://docs.example.com',
        'Report a bug': 'https://github.com/yourusername/healthcare-analytics/issues',
        'About': '## 🏥 Healthcare Readmission Prediction Platform'
    }
)

# ========== MOBILE DETECTION & OPTIMIZATION ==========
def get_user_agent():
    """Try to get user agent from Streamlit context"""
    try:
        # Updated for Streamlit 1.29+
        return st.query_params.get('user_agent', [''])[0]
    except:
        return ""

def is_mobile_device():
    """Check if user is on mobile device (basic detection)"""
    user_agent = get_user_agent().lower()
    mobile_keywords = ['mobile', 'android', 'iphone', 'ipad', 'windows phone']
    
    # Also check via JavaScript injection
    return st.session_state.get('is_mobile', False)

# Store mobile detection in session state
if 'is_mobile' not in st.session_state:
    st.session_state.is_mobile = is_mobile_device()

# ========== MOBILE-OPTIMIZED CSS ==========
mobile_css = """
<style>
    /* Base responsive styles */
    @media (max-width: 768px) {
        /* Adjust container padding */
        .main .block-container {
            padding-top: 2rem;
            padding-right: 1rem;
            padding-left: 1rem;
            padding-bottom: 2rem;
        }
        
        /* Adjust titles */
        h1 {
            font-size: 1.8rem !important;
        }
        
        h2 {
            font-size: 1.5rem !important;
        }
        
        h3 {
            font-size: 1.2rem !important;
        }
        
        /* Adjust columns for mobile */
        [data-testid="column"] {
            padding: 5px !important;
        }
        
        /* Make buttons full width on mobile */
        .stButton > button {
            width: 100% !important;
            margin: 5px 0 !important;
        }
        
        /* Adjust form inputs */
        .stTextInput > div > div > input,
        .stNumberInput > div > div > input,
        .stSelectbox > div > div > select {
            font-size: 16px !important; /* Prevents iOS zoom */
        }
        
        /* Adjust dataframes */
        .stDataFrame {
            font-size: 12px !important;
        }
        
        /* Adjust charts */
        .js-plotly-plot {
            max-width: 100% !important;
        }
        
        /* Adjust sidebar */
        [data-testid="stSidebar"] {
            min-width: 200px !important;
            max-width: 250px !important;
        }
        
        /* Adjust metric cards */
        .metric-card {
            margin: 10px 0 !important;
            padding: 15px !important;
        }
        
        /* Adjust tabs */
        .stTabs [data-baseweb="tab-list"] {
            flex-wrap: wrap !important;
        }
        
        .stTabs [data-baseweb="tab"] {
            padding: 10px 15px !important;
            font-size: 14px !important;
        }
        
        /* Adjust form spacing */
        .stForm {
            margin-bottom: 20px !important;
        }
    }
    
    /* Tablet styles */
    @media (max-width: 1024px) and (min-width: 769px) {
        .main .block-container {
            padding: 2rem;
        }
        
        [data-testid="column"] {
            padding: 10px !important;
        }
    }
    
    /* Metric card styling */
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 20px;
        border-radius: 15px;
        text-align: center;
        margin: 10px 0;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        transition: transform 0.3s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-5px);
    }
    
    .metric-card h3 {
        font-size: 1rem;
        margin-bottom: 10px;
        font-weight: 500;
    }
    
    .metric-card h1 {
        font-size: 2.5rem;
        margin: 10px 0;
        font-weight: 700;
    }
    
    .metric-card p {
        font-size: 0.9rem;
        opacity: 0.9;
    }
    
    /* Mobile-specific classes */
    .mobile-hidden {
        display: none;
    }
    
    @media (min-width: 769px) {
        .mobile-hidden {
            display: block;
        }
    }
    
    /* Touch-friendly buttons */
    .touch-button {
        min-height: 44px !important;
        min-width: 44px !important;
    }
    
    /* Better form spacing for mobile */
    .stForm {
        margin-bottom: 20px;
    }
    
    /* Scrollable containers for mobile */
    .scrollable-container {
        max-height: 400px;
        overflow-y: auto;
        -webkit-overflow-scrolling: touch;
        padding: 10px;
        border: 1px solid #e0e0e0;
        border-radius: 5px;
        margin: 10px 0;
    }
    
    /* Streamlit specific fixes */
    .st-emotion-cache-1y4p8pa {
        padding: 1rem !important;
    }
    
    /* Fix for Streamlit buttons */
    button[kind="primary"] {
        background-color: #1E3A8A !important;
    }
    
    /* Fix for Streamlit selectboxes on mobile */
    .stSelectbox > div > div {
        min-height: 44px !important;
    }
</style>
"""

# Inject CSS
st.markdown(mobile_css, unsafe_allow_html=True)

# ========== HELPER FUNCTIONS ==========
def initialize_session_state():
    """Initialize session state variables"""
    if 'data' not in st.session_state:
        # Create sample healthcare data
        np.random.seed(42)
        n_patients = 1000
        
        dates = pd.date_range('2023-01-01', '2023-12-31', freq='D')
        
        st.session_state.data = pd.DataFrame({
            'patient_id': range(1000, 1000 + n_patients),
            'admission_date': np.random.choice(dates, n_patients),
            'age': np.random.randint(18, 90, n_patients),
            'gender': np.random.choice(['Male', 'Female', 'Other'], n_patients, p=[0.48, 0.48, 0.04]),
            'length_of_stay': np.random.exponential(7, n_patients).astype(int) + 1,
            'blood_pressure_sys': np.random.normal(120, 20, n_patients).astype(int),
            'blood_pressure_dia': np.random.normal(80, 10, n_patients).astype(int),
            'cholesterol': np.random.normal(200, 40, n_patients).astype(int),
            'bmi': np.random.normal(25, 5, n_patients),
            'diabetes': np.random.choice([0, 1], n_patients, p=[0.7, 0.3]),
            'hypertension': np.random.choice([0, 1], n_patients, p=[0.6, 0.4]),
            'previous_admissions': np.random.poisson(1.5, n_patients),
            'lab_result': np.random.normal(100, 20, n_patients)
        })
        
        # Calculate readmission (target variable) based on risk factors
        risk_score = (
            (st.session_state.data['age'] - 30) / 60 * 0.3 +
            (st.session_state.data['length_of_stay'] > 10) * 0.2 +
            (st.session_state.data['diabetes'] == 1) * 0.15 +
            (st.session_state.data['hypertension'] == 1) * 0.1 +
            (st.session_state.data['cholesterol'] > 240) * 0.1 +
            (st.session_state.data['previous_admissions'] > 2) * 0.15 +
            np.random.normal(0, 0.1, n_patients)
        )
        
        # Convert risk score to binary outcome (0 = no readmission, 1 = readmission)
        st.session_state.data['readmission_30d'] = (risk_score > 0.5).astype(int)
        
        # Add some time-based features
        st.session_state.data['admission_date'] = pd.to_datetime(st.session_state.data['admission_date'])
        st.session_state.data['admission_month'] = st.session_state.data['admission_date'].dt.month
        st.session_state.data['admission_day'] = st.session_state.data['admission_date'].dt.day
        st.session_state.data['discharge_date'] = st.session_state.data['admission_date'] + pd.to_timedelta(st.session_state.data['length_of_stay'], unit='d')
        
        # Calculate additional metrics
        st.session_state.metrics = {
            'total_patients': n_patients,
            'readmission_rate': st.session_state.data['readmission_30d'].mean() * 100,
            'avg_age': st.session_state.data['age'].mean(),
            'avg_stay': st.session_state.data['length_of_stay'].mean(),
            'avg_bmi': st.session_state.data['bmi'].mean()
        }
    
    # Initialize filters
    if 'filters' not in st.session_state:
        st.session_state.filters = {
            'gender': ['Male', 'Female', 'Other'],
            'age_range': (18, 90),
            'readmission_status': [0, 1]
        }
    
    # Initialize analytics
    if 'analytics' not in st.session_state:
        st.session_state.analytics = {
            'page_views': 0,
            'predictions_made': 0,
            'data_exports': 0,
            'session_start': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    
    # Track page view
    st.session_state.analytics['page_views'] += 1

def create_metric_card(title, value, subtitle, icon="📊"):
    """Create a responsive metric card"""
    card_html = f"""
    <div class="metric-card">
        <div style="font-size: 2rem; margin-bottom: 10px;">{icon}</div>
        <h3>{title}</h3>
        <h1>{value}</h1>
        <p>{subtitle}</p>
    </div>
    """
    return card_html

# ========== PAGE FUNCTIONS ==========
def show_dashboard():
    """Dashboard page"""
    st.markdown('<h1 style="font-size: 2.5rem; color: #1E3A8A; text-align: center; margin-bottom: 2rem;">📊 Healthcare Analytics Dashboard</h1>', unsafe_allow_html=True)
    
    # Mobile notification
    if st.session_state.is_mobile:
        st.info("📱 You're viewing the mobile-optimized version. For best experience, rotate your device horizontally.")
    
    # Apply filters
    filtered_data = st.session_state.data[
        (st.session_state.data['gender'].isin(st.session_state.filters['gender'])) &
        (st.session_state.data['age'].between(
            st.session_state.filters['age_range'][0],
            st.session_state.filters['age_range'][1]
        )) &
        (st.session_state.data['readmission_30d'].isin(st.session_state.filters['readmission_status']))
    ]
    
    # KPI Metrics - Responsive layout
    if st.session_state.is_mobile:
        # Stack metrics vertically on mobile
        for title, value, subtitle in [
            ("Total Patients", f"{len(filtered_data):,}", "Registered patients"),
            ("Readmission Rate", f"{filtered_data['readmission_30d'].mean()*100:.1f}%", "Within 30 days"),
            ("Avg Stay", f"{filtered_data['length_of_stay'].mean():.1f} days", "Hospitalization duration"),
            ("Avg Age", f"{filtered_data['age'].mean():.1f} years", "Patient demographics")
        ]:
            st.markdown(create_metric_card(title, value, subtitle), unsafe_allow_html=True)
    else:
        # Desktop layout
        cols = st.columns(4)
        metrics = [
            ("Total Patients", f"{len(filtered_data):,}", "Registered patients"),
            ("Readmission Rate", f"{filtered_data['readmission_30d'].mean()*100:.1f}%", "Within 30 days"),
            ("Avg Stay", f"{filtered_data['length_of_stay'].mean():.1f} days", "Hospitalization duration"),
            ("Avg Age", f"{filtered_data['age'].mean():.1f} years", "Patient demographics")
        ]
        
        for i, (title, value, subtitle) in enumerate(metrics):
            with cols[i]:
                st.markdown(create_metric_card(title, value, subtitle), unsafe_allow_html=True)
    
    # Charts section with responsive layout
    st.markdown("---")
    st.header("📈 Visual Analytics")
    
    if st.session_state.is_mobile:
        # Stack charts vertically on mobile
        # Chart 1: Readmission by Age Group
        st.subheader("Readmission by Age Group")
        
        # Create age groups
        filtered_data['age_group'] = pd.cut(
            filtered_data['age'],
            bins=[0, 30, 50, 65, 80, 100],
            labels=['0-30', '31-50', '51-65', '66-80', '81+']
        )
        
        age_group_stats = filtered_data.groupby('age_group')['readmission_30d'].agg(['mean', 'count']).reset_index()
        
        fig1 = px.bar(
            age_group_stats,
            x='age_group',
            y='mean',
            color='mean',
            color_continuous_scale='RdYlGn_r',
            labels={'mean': 'Readmission Rate', 'age_group': 'Age Group'},
            title="Readmission Rate by Age Group"
        )
        
        # Add count annotations
        for i, row in age_group_stats.iterrows():
            fig1.add_annotation(
                x=row['age_group'],
                y=row['mean'] + 0.02,
                text=f"n={int(row['count'])}",
                showarrow=False,
                font=dict(size=10)
            )
        
        fig1.update_layout(height=400)
        st.plotly_chart(fig1, use_container_width=True)
        
        # Chart 2: Length of Stay Distribution
        st.subheader("Length of Stay Distribution")
        
        fig2 = px.box(
            filtered_data,
            y='length_of_stay',
            x='gender',
            color='gender',
            points='all',
            title="Length of Stay by Gender",
            labels={'length_of_stay': 'Days', 'gender': 'Gender'}
        )
        
        fig2.update_layout(height=400)
        st.plotly_chart(fig2, use_container_width=True)
    else:
        # Desktop layout
        chart_cols = st.columns(2)
        
        with chart_cols[0]:
            st.subheader("Readmission by Age Group")
            
            # Create age groups
            filtered_data['age_group'] = pd.cut(
                filtered_data['age'],
                bins=[0, 30, 50, 65, 80, 100],
                labels=['0-30', '31-50', '51-65', '66-80', '81+']
            )
            
            age_group_stats = filtered_data.groupby('age_group')['readmission_30d'].agg(['mean', 'count']).reset_index()
            
            fig1 = px.bar(
                age_group_stats,
                x='age_group',
                y='mean',
                color='mean',
                color_continuous_scale='RdYlGn_r',
                labels={'mean': 'Readmission Rate', 'age_group': 'Age Group'},
                title="Readmission Rate by Age Group"
            )
            
            # Add count annotations
            for i, row in age_group_stats.iterrows():
                fig1.add_annotation(
                    x=row['age_group'],
                    y=row['mean'] + 0.02,
                    text=f"n={int(row['count'])}",
                    showarrow=False,
                    font=dict(size=10)
                )
            
            fig1.update_layout(height=400)
            st.plotly_chart(fig1, use_container_width=True)
        
        with chart_cols[1]:
            st.subheader("Length of Stay Distribution")
            
            fig2 = px.box(
                filtered_data,
                y='length_of_stay',
                x='gender',
                color='gender',
                points='all',
                title="Length of Stay by Gender",
                labels={'length_of_stay': 'Days', 'gender': 'Gender'}
            )
            
            fig2.update_layout(height=400)
            st.plotly_chart(fig2, use_container_width=True)
        
        # Additional desktop charts
        st.subheader("📊 Detailed Analysis")
        
        detailed_cols = st.columns(2)
        
        with detailed_cols[0]:
            # Blood pressure vs readmission
            sample_data = filtered_data.sample(min(200, len(filtered_data)))
            fig3 = px.scatter(
                sample_data,
                x='blood_pressure_sys',
                y='blood_pressure_dia',
                color='readmission_30d',
                size='bmi',
                hover_data=['age', 'gender'],
                title="Blood Pressure vs Readmission",
                labels={'readmission_30d': 'Readmitted'}
            )
            st.plotly_chart(fig3, use_container_width=True)
        
        with detailed_cols[1]:
            # Monthly trends
            monthly_trend = filtered_data.groupby('admission_month')['readmission_30d'].mean().reset_index()
            
            fig4 = px.line(
                monthly_trend,
                x='admission_month',
                y='readmission_30d',
                markers=True,
                title="Monthly Readmission Trend",
                labels={'readmission_30d': 'Readmission Rate', 'admission_month': 'Month'}
            )
            fig4.update_traces(line=dict(width=3))
            st.plotly_chart(fig4, use_container_width=True)
    
    # Data preview with mobile optimization
    st.markdown("---")
    st.header("📋 Patient Data Preview")
    
    with st.expander("View Filtered Data", expanded=False):
        # Show limited data on mobile
        display_count = 5 if st.session_state.is_mobile else 10
        
        if st.session_state.is_mobile:
            st.markdown('<div class="scrollable-container">', unsafe_allow_html=True)
        
        st.dataframe(
            filtered_data[['patient_id', 'age', 'gender', 'length_of_stay', 'readmission_30d', 'bmi']].head(display_count),
            use_container_width=True,
            hide_index=True
        )
        
        if st.session_state.is_mobile:
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Download options
        csv = filtered_data.to_csv(index=False)
        
        if st.session_state.is_mobile:
            st.download_button(
                label="📥 Download as CSV",
                data=csv,
                file_name="patient_data.csv",
                mime="text/csv",
                use_container_width=True
            )
        else:
            col1, col2 = st.columns(2)
            with col1:
                st.download_button(
                    label="📥 Download as CSV",
                    data=csv,
                    file_name="patient_data.csv",
                    mime="text/csv",
                    use_container_width=True
                )
            
            with col2:
                # Show additional options on desktop
                json_data = filtered_data.to_json(orient='records')
                st.download_button(
                    label="📥 Download as JSON",
                    data=json_data,
                    file_name="patient_data.json",
                    mime="application/json",
                    use_container_width=True
                )

def show_predictions():
    """Predictions page"""
    st.header("🤖 Readmission Risk Predictor")
    
    # Mobile-friendly info
    if st.session_state.is_mobile:
        st.info("📱 Fill in the form below to predict readmission risk. Scroll to see all fields.")
    
    # Create form
    with st.form("prediction_form"):
        # Responsive form layout
        if st.session_state.is_mobile:
            # Stack form fields vertically on mobile
            st.subheader("👤 Patient Info")
            age = st.number_input(
                "Age",
                min_value=18,
                max_value=120,
                value=45,
                help="Patient's age in years"
            )
            gender = st.selectbox(
                "Gender",
                ["Male", "Female", "Other"]
            )
            bmi = st.slider(
                "BMI",
                min_value=15.0,
                max_value=50.0,
                value=25.0,
                step=0.1,
                help="Body Mass Index"
            )
            
            st.subheader("🏥 Medical History")
            diabetes = st.selectbox(
                "Diabetes",
                ["No", "Yes"]
            )
            hypertension = st.selectbox(
                "Hypertension",
                ["No", "Yes"]
            )
            previous_admissions = st.number_input(
                "Previous Admissions",
                min_value=0,
                max_value=20,
                value=1
            )
            
            st.subheader("🔬 Current Status")
            length_of_stay = st.number_input(
                "Current Stay (days)",
                min_value=1,
                max_value=365,
                value=7
            )
            blood_pressure = st.slider(
                "Systolic BP",
                min_value=80,
                max_value=200,
                value=120
            )
            cholesterol = st.number_input(
                "Cholesterol (mg/dL)",
                min_value=100,
                max_value=400,
                value=200
            )
        else:
            # Desktop form layout
            form_cols = st.columns(3)
            
            with form_cols[0]:
                st.subheader("👤 Patient Info")
                age = st.number_input(
                    "Age",
                    min_value=18,
                    max_value=120,
                    value=45,
                    help="Patient's age in years",
                    key="pred_age"
                )
                gender = st.selectbox(
                    "Gender",
                    ["Male", "Female", "Other"],
                    key="pred_gender"
                )
                bmi = st.slider(
                    "BMI",
                    min_value=15.0,
                    max_value=50.0,
                    value=25.0,
                    step=0.1,
                    help="Body Mass Index",
                    key="pred_bmi"
                )
            
            with form_cols[1]:
                st.subheader("🏥 Medical History")
                diabetes = st.selectbox(
                    "Diabetes",
                    ["No", "Yes"],
                    key="pred_diabetes"
                )
                hypertension = st.selectbox(
                    "Hypertension",
                    ["No", "Yes"],
                    key="pred_hypertension"
                )
                previous_admissions = st.number_input(
                    "Previous Admissions",
                    min_value=0,
                    max_value=20,
                    value=1,
                    key="pred_prev_adm"
                )
            
            with form_cols[2]:
                st.subheader("🔬 Current Status")
                length_of_stay = st.number_input(
                    "Current Stay (days)",
                    min_value=1,
                    max_value=365,
                    value=7,
                    key="pred_los"
                )
                blood_pressure = st.slider(
                    "Systolic BP",
                    min_value=80,
                    max_value=200,
                    value=120,
                    key="pred_bp"
                )
                cholesterol = st.number_input(
                    "Cholesterol (mg/dL)",
                    min_value=100,
                    max_value=400,
                    value=200,
                    key="pred_chol"
                )
        
        # Submit button with mobile optimization
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            submitted = st.form_submit_button(
                "🚀 Calculate Risk",
                type="primary",
                use_container_width=True
            )
    
    if submitted:
        # Track prediction
        st.session_state.analytics['predictions_made'] += 1
        
        with st.spinner("🔍 Analyzing patient data..."):
            # Simulate processing time
            import time
            progress_bar = st.progress(0)
            
            for i in range(100):
                time.sleep(0.01)
                progress_bar.progress(i + 1)
            
            # Calculate risk score (simplified model)
            risk_factors = {
                'age': min(0.25, (age - 30) / 90),
                'bmi_risk': min(0.15, abs(25 - bmi) / 25),
                'diabetes': 0.15 if diabetes == "Yes" else 0,
                'hypertension': 0.10 if hypertension == "Yes" else 0,
                'previous_admissions': min(0.20, previous_admissions / 10),
                'length_of_stay': min(0.15, length_of_stay / 30),
                'blood_pressure': min(0.10, max(0, (blood_pressure - 120) / 80))
            }
            
            base_risk = 0.10
            risk_score = base_risk + sum(risk_factors.values())
            risk_score = min(0.95, max(0.05, risk_score))
        
        # Display results
        st.markdown("---")
        st.header("📊 Prediction Results")
        
        # Responsive results layout
        if st.session_state.is_mobile:
            # Mobile layout
            # Risk gauge
            fig = go.Figure(go.Indicator(
                mode="gauge+number",
                value=risk_score * 100,
                domain={'x': [0, 1], 'y': [0, 1]},
                title={'text': "Readmission Risk Score"},
                gauge={
                    'axis': {'range': [0, 100]},
                    'bar': {'color': "darkblue"},
                    'steps': [
                        {'range': [0, 30], 'color': "green"},
                        {'range': [30, 70], 'color': "yellow"},
                        {'range': [70, 100], 'color': "red"}
                    ],
                    'threshold': {
                        'line': {'color': "black", 'width': 4},
                        'thickness': 0.75,
                        'value': risk_score * 100
                    }
                }
            ))
            
            fig.update_layout(height=300)
            st.plotly_chart(fig, use_container_width=True)
            
            # Risk level
            if risk_score < 0.3:
                risk_level = "🟢 LOW RISK"
                recommendations = [
                    "Standard discharge protocol",
                    "Follow-up in 30 days",
                    "General patient education"
                ]
            elif risk_score < 0.7:
                risk_level = "🟡 MEDIUM RISK"
                recommendations = [
                    "Schedule follow-up within 14 days",
                    "Assign care coordinator",
                    "Monitor vital signs"
                ]
            else:
                risk_level = "🔴 HIGH RISK"
                recommendations = [
                    "Immediate care coordination",
                    "7-day follow-up required",
                    "Home health assessment",
                    "Medication management"
                ]
            
            st.markdown(f"### {risk_level}")
            st.markdown(f"**Probability:** {risk_score:.1%}")
            
            st.subheader("📋 Recommendations")
            for rec in recommendations:
                st.markdown(f"✓ {rec}")
            
            # Risk factors table
            st.markdown("---")
            st.subheader("🔍 Risk Factors")
            
            risk_df = pd.DataFrame({
                'Factor': [f.replace('_', ' ').title() for f in risk_factors.keys()],
                'Contribution': [f"{v*100:.1f}%" for v in risk_factors.values()]
            })
            
            st.table(risk_df)
        else:
            # Desktop layout
            results_cols = st.columns([2, 1])
            
            with results_cols[0]:
                # Risk gauge
                fig = go.Figure(go.Indicator(
                    mode="gauge+number",
                    value=risk_score * 100,
                    domain={'x': [0, 1], 'y': [0, 1]},
                    title={'text': "Readmission Risk Score"},
                    gauge={
                        'axis': {'range': [0, 100]},
                        'bar': {'color': "darkblue"},
                        'steps': [
                            {'range': [0, 30], 'color': "green"},
                            {'range': [30, 70], 'color': "yellow"},
                            {'range': [70, 100], 'color': "red"}
                        ],
                        'threshold': {
                            'line': {'color': "black", 'width': 4},
                            'thickness': 0.75,
                            'value': risk_score * 100
                        }
                    }
                ))
                
                fig.update_layout(height=300)
                st.plotly_chart(fig, use_container_width=True)
            
            with results_cols[1]:
                # Risk level and recommendations
                if risk_score < 0.3:
                    risk_level = "🟢 LOW RISK"
                    recommendations = [
                        "Standard discharge protocol",
                        "Follow-up in 30 days",
                        "General patient education"
                    ]
                elif risk_score < 0.7:
                    risk_level = "🟡 MEDIUM RISK"
                    recommendations = [
                        "Schedule follow-up within 14 days",
                        "Assign care coordinator",
                        "Monitor vital signs"
                    ]
                else:
                    risk_level = "🔴 HIGH RISK"
                    recommendations = [
                        "Immediate care coordination",
                        "7-day follow-up required",
                        "Home health assessment",
                        "Medication management"
                    ]
                
                st.markdown(f"### {risk_level}")
                st.markdown(f"**Probability:** {risk_score:.1%}")
                
                st.subheader("📋 Recommendations")
                for rec in recommendations:
                    st.markdown(f"✓ {rec}")
            
            # Risk factors breakdown
            st.markdown("---")
            st.subheader("🔍 Risk Factors Breakdown")
            
            risk_df = pd.DataFrame({
                'Factor': [f.replace('_', ' ').title() for f in risk_factors.keys()],
                'Contribution': [v * 100 for v in risk_factors.values()]
            })
            
            fig_risk = px.bar(
                risk_df,
                x='Contribution',
                y='Factor',
                orientation='h',
                color='Contribution',
                color_continuous_scale='RdYlGn_r',
                text='Contribution'
            )
            fig_risk.update_layout(height=300, yaxis={'categoryorder': 'total ascending'})
            st.plotly_chart(fig_risk, use_container_width=True)
        
        # Generate report
        st.markdown("---")
        st.subheader("📄 Generate Report")
        
        report_content = f"""
        HEALTHCARE READMISSION RISK ASSESSMENT
        =======================================
        
        Patient Assessment
        ------------------
        Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}
        Age: {age} years
        Gender: {gender}
        BMI: {bmi}
        
        Medical History
        ---------------
        Diabetes: {diabetes}
        Hypertension: {hypertension}
        Previous Admissions: {previous_admissions}
        
        Current Status
        --------------
        Length of Stay: {length_of_stay} days
        Blood Pressure: {blood_pressure} mmHg
        Cholesterol: {cholesterol} mg/dL
        
        Assessment Results
        ------------------
        Readmission Risk: {risk_score:.1%}
        Risk Level: {risk_level}
        
        Key Risk Factors
        ----------------
        """
        
        for factor, value in risk_factors.items():
            report_content += f"- {factor.replace('_', ' ').title()}: {value*100:.1f}%\n"
        
        report_content += f"""
        
        Recommendations
        ---------------
        """
        
        for i, rec in enumerate(recommendations, 1):
            report_content += f"{i}. {rec}\n"
        
        # Download button
        st.download_button(
            label="📥 Download Full Report",
            data=report_content,
            file_name=f"readmission_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
            mime="text/plain",
            use_container_width=True
        )

def show_data_explorer():
    """Data Explorer page"""
    st.header("🔍 Interactive Data Explorer")
    
    # Mobile info
    if st.session_state.is_mobile:
        st.info("📱 Use filters below to explore patient data. Charts will adapt to your screen size.")
    
    # Filters in expander for mobile
    with st.expander("🔧 Data Filters", expanded=not st.session_state.is_mobile):
        if st.session_state.is_mobile:
            # Stack filters vertically on mobile
            gender_filter = st.multiselect(
                "Gender",
                options=st.session_state.data['gender'].unique(),
                default=st.session_state.data['gender'].unique()
            )
            
            readmission_filter = st.multiselect(
                "Readmission Status",
                options=[0, 1],
                default=[0, 1],
                format_func=lambda x: "Readmitted" if x == 1 else "Not Readmitted"
            )
            
            age_filter = st.slider(
                "Age Range",
                int(st.session_state.data['age'].min()),
                int(st.session_state.data['age'].max()),
                (30, 70)
            )
            
            los_filter = st.slider(
                "Length of Stay",
                int(st.session_state.data['length_of_stay'].min()),
                int(st.session_state.data['length_of_stay'].max()),
                (1, 14)
            )
            
            bmi_filter = st.slider(
                "BMI Range",
                float(st.session_state.data['bmi'].min()),
                float(st.session_state.data['bmi'].max()),
                (18.5, 30.0)
            )
            
            sample_size = st.slider(
                "Sample Size",
                10, 1000, 200
            )
        else:
            # Desktop filters
            filter_cols = st.columns(3)
            
            with filter_cols[0]:
                gender_filter = st.multiselect(
                    "Gender",
                    options=st.session_state.data['gender'].unique(),
                    default=st.session_state.data['gender'].unique()
                )
                
                readmission_filter = st.multiselect(
                    "Readmission Status",
                    options=[0, 1],
                    default=[0, 1],
                    format_func=lambda x: "Readmitted" if x == 1 else "Not Readmitted"
                )
            
            with filter_cols[1]:
                age_filter = st.slider(
                    "Age Range",
                    int(st.session_state.data['age'].min()),
                    int(st.session_state.data['age'].max()),
                    (30, 70)
                )
                
                los_filter = st.slider(
                    "Length of Stay",
                    int(st.session_state.data['length_of_stay'].min()),
                    int(st.session_state.data['length_of_stay'].max()),
                    (1, 14)
                )
            
            with filter_cols[2]:
                bmi_filter = st.slider(
                    "BMI Range",
                    float(st.session_state.data['bmi'].min()),
                    float(st.session_state.data['bmi'].max()),
                    (18.5, 30.0)
                )
                
                sample_size = st.slider(
                    "Sample Size",
                    10, 1000, 200
                )
    
    # Apply filters
    filtered_data = st.session_state.data[
        (st.session_state.data['gender'].isin(gender_filter)) &
        (st.session_state.data['readmission_30d'].isin(readmission_filter)) &
        (st.session_state.data['age'].between(age_filter[0], age_filter[1])) &
        (st.session_state.data['length_of_stay'].between(los_filter[0], los_filter[1])) &
        (st.session_state.data['bmi'].between(bmi_filter[0], bmi_filter[1]))
    ].sample(min(sample_size, len(st.session_state.data)))
    
    st.success(f"✅ Showing {len(filtered_data)} records")
    
    # Visualization tools
    st.subheader("📊 Visualization Tools")
    
    # Chart type selection
    chart_options = ["Scatter Plot", "Histogram", "Box Plot", "Violin Plot", "Correlation Matrix"]
    
    if st.session_state.is_mobile:
        chart_type = st.selectbox("Chart Type", chart_options)
        
        if chart_type == "Scatter Plot":
            x_axis = st.selectbox("X-axis", filtered_data.columns, index=2)
            y_axis = st.selectbox("Y-axis", filtered_data.columns, index=5)
            
            fig = px.scatter(
                filtered_data,
                x=x_axis,
                y=y_axis,
                color='readmission_30d',
                hover_data=['patient_id', 'gender', 'age'],
                title=f"{y_axis} vs {x_axis}"
            )
            st.plotly_chart(fig, use_container_width=True)
        
        elif chart_type == "Histogram":
            column = st.selectbox("Select Column", filtered_data.select_dtypes(include=[np.number]).columns)
            
            fig = px.histogram(
                filtered_data,
                x=column,
                nbins=30,
                color='gender',
                barmode='overlay',
                title=f"Distribution of {column}"
            )
            st.plotly_chart(fig, use_container_width=True)
        
        elif chart_type == "Box Plot":
            column = st.selectbox("Value Column", ['age', 'length_of_stay', 'bmi', 'cholesterol'])
            group_by = st.selectbox("Group By", ['gender', 'readmission_30d', 'diabetes'])
            
            fig = px.box(
                filtered_data,
                y=column,
                x=group_by,
                color=group_by,
                title=f"{column} by {group_by}"
            )
            st.plotly_chart(fig, use_container_width=True)
        
        elif chart_type == "Violin Plot":
            column = st.selectbox("Value Column", ['age', 'length_of_stay', 'bmi'])
            group_by = st.selectbox("Group By", ['gender', 'readmission_30d'])
            
            fig = px.violin(
                filtered_data,
                y=column,
                x=group_by,
                color=group_by,
                box=True,
                points="all",
                title=f"{column} Distribution by {group_by}"
            )
            st.plotly_chart(fig, use_container_width=True)
        
        elif chart_type == "Correlation Matrix":
            numeric_data = filtered_data.select_dtypes(include=[np.number])
            
            if len(numeric_data.columns) > 1:
                corr_matrix = numeric_data.corr()
                
                fig = px.imshow(
                    corr_matrix,
                    text_auto='.2f',
                    color_continuous_scale='RdBu',
                    title="Correlation Matrix"
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("Need more numeric columns for correlation matrix")
    else:
        # Desktop layout
        viz_cols = st.columns([1, 3])
        
        with viz_cols[0]:
            chart_type = st.selectbox("Chart Type", chart_options)
        
        with viz_cols[1]:
            if chart_type == "Scatter Plot":
                col1, col2 = st.columns(2)
                with col1:
                    x_axis = st.selectbox("X-axis", filtered_data.columns, index=2)
                with col2:
                    y_axis = st.selectbox("Y-axis", filtered_data.columns, index=5)
                
                fig = px.scatter(
                    filtered_data,
                    x=x_axis,
                    y=y_axis,
                    color='readmission_30d',
                    hover_data=['patient_id', 'gender', 'age'],
                    title=f"{y_axis} vs {x_axis}"
                )
                st.plotly_chart(fig, use_container_width=True)
            
            elif chart_type == "Histogram":
                column = st.selectbox("Select Column", filtered_data.select_dtypes(include=[np.number]).columns)
                
                fig = px.histogram(
                    filtered_data,
                    x=column,
                    nbins=30,
                    color='gender',
                    barmode='overlay',
                    title=f"Distribution of {column}"
                )
                st.plotly_chart(fig, use_container_width=True)
            
            elif chart_type == "Box Plot":
                column = st.selectbox("Value Column", ['age', 'length_of_stay', 'bmi', 'cholesterol'])
                group_by = st.selectbox("Group By", ['gender', 'readmission_30d', 'diabetes'])
                
                fig = px.box(
                    filtered_data,
                    y=column,
                    x=group_by,
                    color=group_by,
                    title=f"{column} by {group_by}"
                )
                st.plotly_chart(fig, use_container_width=True)
            
            elif chart_type == "Violin Plot":
                column = st.selectbox("Value Column", ['age', 'length_of_stay', 'bmi'])
                group_by = st.selectbox("Group By", ['gender', 'readmission_30d'])
                
                fig = px.violin(
                    filtered_data,
                    y=column,
                    x=group_by,
                    color=group_by,
                    box=True,
                    points="all",
                    title=f"{column} Distribution by {group_by}"
                )
                st.plotly_chart(fig, use_container_width=True)
            
            elif chart_type == "Correlation Matrix":
                numeric_data = filtered_data.select_dtypes(include=[np.number])
                
                if len(numeric_data.columns) > 1:
                    corr_matrix = numeric_data.corr()
                    
                    fig = px.imshow(
                        corr_matrix,
                        text_auto='.2f',
                        color_continuous_scale='RdBu',
                        title="Correlation Matrix"
                    )
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.warning("Need more numeric columns for correlation matrix")
    
    # Data table
    st.subheader("📋 Data Table")
    
    with st.expander("View Data", expanded=False):
        # Show scrollable table on mobile
        if st.session_state.is_mobile:
            st.markdown('<div class="scrollable-container">', unsafe_allow_html=True)
        
        st.dataframe(
            filtered_data,
            use_container_width=True,
            hide_index=True,
            height=300 if st.session_state.is_mobile else 400
        )
        
        if st.session_state.is_mobile:
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Statistics
        st.subheader("📈 Summary Statistics")
        st.write(filtered_data.describe())
        
        # Export buttons
        csv = filtered_data.to_csv(index=False)
        
        if st.session_state.is_mobile:
            st.download_button(
                label="📥 Export as CSV",
                data=csv,
                file_name="healthcare_data.csv",
                mime="text/csv",
                use_container_width=True
            )
        else:
            col1, col2 = st.columns(2)
            
            with col1:
                st.download_button(
                    label="📥 Export as CSV",
                    data=csv,
                    file_name="healthcare_data.csv",
                    mime="text/csv",
                    use_container_width=True
                )
            
            with col2:
                # Excel export (desktop only)
                import io
                buffer = io.BytesIO()
                with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                    filtered_data.to_excel(writer, index=False, sheet_name='Data')
                    writer.close()
                
                st.download_button(
                    label="📥 Export as Excel",
                    data=buffer.getvalue(),
                    file_name="healthcare_data.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True
                )

def show_settings():
    """Settings page"""
    st.header("⚙️ Settings & Configuration")
    
    # App info
    with st.expander("ℹ️ About This App", expanded=True):
        st.markdown("""
        ## 🏥 Healthcare Readmission Analytics
        
        **Version:** 1.3.0
        **Last Updated:** 2024
        
        ### Overview
        This platform uses predictive analytics to identify patients at risk of hospital readmission within 30 days.
        
        ### Features
        - Real-time risk prediction
        - Interactive data visualization
        - Mobile-responsive design
        - Data export capabilities
        
        ### Privacy
        All data is anonymized and complies with healthcare privacy regulations.
        """)
    
    # Mobile settings
    with st.expander("📱 Mobile Settings", expanded=True):
        st.markdown(f"**Mobile Mode Detected:** {'Yes' if st.session_state.is_mobile else 'No'}")
        
        # Force mobile view for testing
        if st.button("Test Mobile View", help="Simulate mobile view for testing", use_container_width=st.session_state.is_mobile):
            st.session_state.is_mobile = True
            st.rerun()
        
        if st.button("Test Desktop View", help="Simulate desktop view for testing", use_container_width=st.session_state.is_mobile):
            st.session_state.is_mobile = False
            st.rerun()
    
    # Data management
    with st.expander("🗃️ Data Management", expanded=False):
        st.subheader("Upload New Data")
        
        uploaded_file = st.file_uploader(
            "Upload CSV file",
            type=['csv'],
            help="Upload patient data in CSV format"
        )
        
        if uploaded_file:
            try:
                new_data = pd.read_csv(uploaded_file)
                required_cols = ['age', 'gender', 'length_of_stay', 'readmission_30d']
                
                if all(col in new_data.columns for col in required_cols):
                    st.session_state.data = new_data
                    st.success(f"✅ Loaded {len(new_data)} records")
                else:
                    st.error(f"❌ Missing required columns: {required_cols}")
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
        
        st.subheader("Reset to Sample Data")
        if st.button("🔄 Reset Data", use_container_width=True):
            initialize_session_state()
            st.success("✅ Data reset complete!")
            st.rerun()
    
    # System info
    with st.expander("💻 System Information", expanded=False):
        st.subheader("Environment Details")
        
        info_data = {
            "Component": ["Python", "Streamlit", "Pandas", "NumPy", "Plotly", "OS"],
            "Version": [
                sys.version.split()[0],
                st.__version__,
                pd.__version__,
                np.__version__,
                plotly.__version__,
                f"{sys.platform} {os.name}"
            ]
        }
        
        info_df = pd.DataFrame(info_data)
        st.table(info_df)
        
        # Analytics
        st.subheader("📊 Usage Analytics")
        st.write(f"**Page Views:** {st.session_state.analytics.get('page_views', 0)}")
        st.write(f"**Predictions Made:** {st.session_state.analytics.get('predictions_made', 0)}")
        st.write(f"**Data Exports:** {st.session_state.analytics.get('data_exports', 0)}")
        st.write(f"**Session Started:** {st.session_state.analytics.get('session_start', 'N/A')}")
    
    # Help section
    with st.expander("❓ Help & Support", expanded=False):
        st.markdown("""
        ### Getting Help
        - **Documentation:** [docs.healthcare-analytics.com](https://docs.example.com)
        - **Support Email:** support@healthcare-analytics.com
        - **GitHub Issues:** [Report a bug](https://github.com/yourusername/healthcare-analytics/issues)
        
        ### Mobile Tips
        1. Rotate your device horizontally for better charts
        2. Use the hamburger menu (☰) to navigate
        3. Tap and hold on charts for tooltips
        """)
        
        # Feedback form
        st.subheader("💬 Feedback")
        feedback = st.text_area("Your feedback helps us improve:", height=100)
        
        if st.button("Submit Feedback", use_container_width=True):
            st.success("✅ Thank you for your feedback!")

# ========== SIDEBAR NAVIGATION ==========
def render_sidebar():
    """Render responsive sidebar"""
    with st.sidebar:
        # App logo/title
        st.markdown("""
        <div style="text-align: center; margin-bottom: 20px;">
            <h1 style="font-size: 1.5rem; color: #1E3A8A;">🏥 Healthcare Analytics</h1>
            <p style="color: #666; font-size: 0.9rem;">Predict • Analyze • Optimize</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Navigation
        st.markdown("### 📋 Navigation")
        
        # Mobile-friendly navigation
        if st.session_state.is_mobile:
            page_options = ["📊 Dashboard", "🤖 Predict", "🔍 Explore", "⚙️ Settings"]
            selected_page = st.radio(
                "Select Page",
                page_options,
                label_visibility="collapsed"
            )
        else:
            # Desktop navigation
            selected_page = st.radio(
                "Select Page",
                ["📊 Dashboard", "🤖 Predictions", "🔍 Data Explorer", "⚙️ Settings"],
                label_visibility="collapsed"
            )
        
        st.markdown("---")
        
        # Quick filters (collapsed on mobile)
        if not st.session_state.is_mobile or st.checkbox("Show Filters", value=False):
            st.markdown("### 🔍 Quick Filters")
            
            gender_options = st.multiselect(
                "Gender",
                options=st.session_state.data['gender'].unique(),
                default=st.session_state.filters['gender']
            )
            
            age_range = st.slider(
                "Age Range",
                min_value=18,
                max_value=90,
                value=st.session_state.filters['age_range']
            )
            
            readmission_status = st.multiselect(
                "Readmission Status",
                options=[0, 1],
                default=st.session_state.filters['readmission_status'],
                format_func=lambda x: "Readmitted" if x == 1 else "Not Readmitted"
            )
            
            # Update filters
            st.session_state.filters.update({
                'gender': gender_options,
                'age_range': age_range,
                'readmission_status': readmission_status
            })
        
        st.markdown("---")
        
        # Quick actions
        st.markdown("### ⚡ Quick Actions")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🔄 Refresh", use_container_width=True):
                st.rerun()
        
        with col2:
            if st.button("📊 Stats", use_container_width=True):
                st.session_state.show_stats = True
        
        # Mobile info
        if st.session_state.is_mobile:
            st.markdown("---")
            st.info("📱 Mobile mode active")
        
        # Footer
        st.markdown("---")
        st.markdown("""
        <div style="text-align: center; color: #666; font-size: 0.8rem; padding: 10px;">
            <p>Healthcare Analytics v1.3</p>
            <p>© 2024 All rights reserved</p>
        </div>
        """, unsafe_allow_html=True)
    
    return selected_page

# ========== MAIN APP FUNCTION ==========
def main():
    """Main application function"""
    # Initialize session state
    initialize_session_state()
    
    # Detect mobile from query params - UPDATED FOR STREAMLIT 1.29+
    query_params = st.query_params
    if 'mobile' in query_params:
        st.session_state.is_mobile = query_params['mobile'][0].lower() == 'true'
    
    # Get selected page from sidebar
    selected_page = render_sidebar()
    
    # Route to selected page
    if "Dashboard" in selected_page:
        show_dashboard()
    elif "Predict" in selected_page or "Predictions" in selected_page:
        show_predictions()
    elif "Explore" in selected_page or "Data Explorer" in selected_page:
        show_data_explorer()
    elif "Settings" in selected_page:
        show_settings()
    
    # Add mobile optimization note at bottom
    if st.session_state.is_mobile:
        st.markdown("---")
        st.caption("📱 Optimized for mobile viewing • Rotate device for better experience")

# ========== RUN THE APP ==========
if __name__ == "__main__":
    main()