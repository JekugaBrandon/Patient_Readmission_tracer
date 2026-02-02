# streamlit_app_fixed.py
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import plotly  # Import plotly for version checking
import sys
import platform

# MUST BE FIRST STREAMLIT COMMAND
st.set_page_config(
    page_title="Healthcare Analytics",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Add custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1E3A8A;
        text-align: center;
        margin-bottom: 2rem;
    }
    .stButton>button {
        background-color: #1E3A8A;
        color: white;
        font-weight: bold;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 20px;
        border-radius: 10px;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'data' not in st.session_state:
    # Create sample data
    np.random.seed(42)
    dates = pd.date_range('2023-01-01', '2023-12-31', freq='D')
    st.session_state.data = pd.DataFrame({
        'date': np.random.choice(dates, 1000),
        'patient_id': np.random.randint(1000, 2000, 1000),
        'age': np.random.randint(18, 90, 1000),
        'gender': np.random.choice(['Male', 'Female'], 1000),
        'length_of_stay': np.random.randint(1, 30, 1000),
        'readmission': np.random.choice([0, 1], 1000, p=[0.85, 0.15]),
        'lab_value': np.random.normal(100, 20, 1000)
    })
    
    # Calculate some metrics for dashboard
    st.session_state.metrics = {
        'total_patients': len(st.session_state.data),
        'readmission_rate': st.session_state.data['readmission'].mean() * 100,
        'avg_age': st.session_state.data['age'].mean(),
        'avg_stay': st.session_state.data['length_of_stay'].mean()
    }

def main():
    # Title
    st.markdown('<h1 class="main-header">🏥 Healthcare Readmission Analytics Platform</h1>', 
                unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.title("📋 Navigation")
        page = st.radio(
            "Select Page:",
            ["📊 Dashboard", "🤖 Predictions", "🔍 Data Explorer", "⚙️ Settings"],
            index=0
        )
        
        st.markdown("---")
        st.title("🔍 Filters")
        
        # Sample filters
        gender_filter = st.multiselect(
            "Select Gender",
            options=['Male', 'Female'],
            default=['Male', 'Female']
        )
        
        age_range = st.slider(
            "Age Range",
            min_value=18,
            max_value=90,
            value=(25, 65)
        )
        
        # Add some helpful info
        st.markdown("---")
        st.caption("💡 **Tip**: Use filters to refine your analysis")
    
    # Store filters in session state
    st.session_state.filters = {
        'gender': gender_filter,
        'age_range': age_range
    }
    
    # Main content based on page selection
    if page == "📊 Dashboard":
        show_dashboard()
    elif page == "🤖 Predictions":
        show_predictions()
    elif page == "🔍 Data Explorer":
        show_data_explorer()
    elif page == "⚙️ Settings":
        show_settings()

def show_dashboard():
    st.header("📊 Dashboard Overview")
    
    # Apply filters
    filtered_data = st.session_state.data[
        (st.session_state.data['gender'].isin(st.session_state.filters['gender'])) &
        (st.session_state.data['age'].between(
            st.session_state.filters['age_range'][0],
            st.session_state.filters['age_range'][1]
        ))
    ]
    
    # KPI Metrics with better styling
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="metric-card">
            <h3>👥 Total Patients</h3>
            <h1>{:,}</h1>
            <p>Registered in system</p>
        </div>
        """.format(len(filtered_data)), unsafe_allow_html=True)
    
    with col2:
        readmission_rate = filtered_data['readmission'].mean() * 100
        st.markdown(f"""
        <div class="metric-card">
            <h3>📈 Readmission Rate</h3>
            <h1>{readmission_rate:.1f}%</h1>
            <p>Target: < 10%</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        avg_stay = filtered_data['length_of_stay'].mean()
        st.markdown(f"""
        <div class="metric-card">
            <h3>⏱️ Avg Stay</h3>
            <h1>{avg_stay:.1f} days</h1>
            <p>Length of hospitalization</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        avg_age = filtered_data['age'].mean()
        st.markdown(f"""
        <div class="metric-card">
            <h3>👴 Avg Age</h3>
            <h1>{avg_age:.1f} years</h1>
            <p>Patient demographics</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Charts Section
    st.markdown("---")
    st.header("📈 Visual Analytics")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Readmission Trend")
        
        # Monthly aggregation
        filtered_data['month'] = pd.to_datetime(filtered_data['date']).dt.to_period('M')
        monthly_data = filtered_data.groupby('month').agg({
            'readmission': 'mean',
            'patient_id': 'count'
        }).reset_index()
        monthly_data['month'] = monthly_data['month'].astype(str)
        
        fig1 = go.Figure()
        fig1.add_trace(go.Scatter(
            x=monthly_data['month'],
            y=monthly_data['readmission'] * 100,
            mode='lines+markers',
            name='Readmission Rate',
            line=dict(color='#FF6B6B', width=3)
        ))
        
        fig1.update_layout(
            height=400,
            xaxis_title="Month",
            yaxis_title="Readmission Rate (%)",
            hovermode='x unified',
            plot_bgcolor='rgba(0,0,0,0)'
        )
        st.plotly_chart(fig1, use_container_width=True)
    
    with col2:
        st.subheader("📊 Age Distribution")
        
        # Age distribution by gender
        fig2 = px.histogram(
            filtered_data,
            x='age',
            color='gender',
            nbins=20,
            title="Patient Age Distribution by Gender",
            color_discrete_map={'Male': '#36BFFA', 'Female': '#F87272'},
            barmode='overlay'
        )
        
        fig2.update_layout(
            height=400,
            xaxis_title="Age",
            yaxis_title="Number of Patients",
            legend_title="Gender",
            plot_bgcolor='rgba(0,0,0,0)'
        )
        st.plotly_chart(fig2, use_container_width=True)
    
    # Additional Charts
    col3, col4 = st.columns(2)
    
    with col3:
        st.subheader("🏥 Length of Stay Distribution")
        
        fig3 = px.box(
            filtered_data,
            x='gender',
            y='length_of_stay',
            color='gender',
            points='all'
        )
        
        fig3.update_layout(
            height=400,
            xaxis_title="Gender",
            yaxis_title="Length of Stay (days)",
            plot_bgcolor='rgba(0,0,0,0)'
        )
        st.plotly_chart(fig3, use_container_width=True)
    
    with col4:
        st.subheader("🎯 Readmission by Age Group")
        
        # Create age groups
        filtered_data['age_group'] = pd.cut(
            filtered_data['age'],
            bins=[0, 30, 50, 65, 80, 100],
            labels=['0-30', '31-50', '51-65', '66-80', '81+']
        )
        
        age_group_data = filtered_data.groupby('age_group')['readmission'].mean().reset_index()
        
        fig4 = px.bar(
            age_group_data,
            x='age_group',
            y='readmission',
            color='readmission',
            color_continuous_scale='RdYlGn_r'
        )
        
        fig4.update_layout(
            height=400,
            xaxis_title="Age Group",
            yaxis_title="Readmission Rate",
            plot_bgcolor='rgba(0,0,0,0)'
        )
        st.plotly_chart(fig4, use_container_width=True)
    
    # Data Preview
    st.markdown("---")
    st.header("📋 Data Preview")
    
    with st.expander("View Filtered Data"):
        st.dataframe(
            filtered_data.head(20),
            use_container_width=True,
            hide_index=True
        )
        
        # Download button for filtered data
        csv = filtered_data.to_csv(index=False)
        st.download_button(
            label="📥 Download Filtered Data (CSV)",
            data=csv,
            file_name="filtered_patient_data.csv",
            mime="text/csv"
        )

def show_predictions():
    st.header("🤖 Readmission Risk Predictor")
    st.info("""
    This tool predicts the probability of a patient being readmitted within 30 days.
    Enter patient details below to get a risk assessment.
    """)
    
    with st.form("prediction_form"):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.subheader("👤 Patient Info")
            age = st.number_input("Age", 18, 100, 45, help="Patient's age in years")
            gender = st.selectbox("Gender", ["Male", "Female", "Other"])
            bmi = st.number_input("BMI", 15.0, 50.0, 25.0, 0.1, help="Body Mass Index")
        
        with col2:
            st.subheader("🏥 Admission Details")
            admission_type = st.selectbox(
                "Admission Type",
                ["Emergency", "Urgent", "Elective", "Newborn"]
            )
            length_of_stay = st.number_input(
                "Length of Stay (days)", 
                1, 365, 7,
                help="Previous hospitalization duration"
            )
            comorbidities = st.slider(
                "Number of Comorbidities", 
                0, 10, 2,
                help="Existing health conditions"
            )
        
        with col3:
            st.subheader("🔬 Lab Results")
            lab_value = st.number_input(
                "Average Lab Value", 
                0.0, 500.0, 100.0, 0.1,
                help="Recent lab test results"
            )
            blood_pressure = st.slider(
                "Blood Pressure (systolic)",
                80, 200, 120,
                help="Systolic blood pressure"
            )
            cholesterol = st.number_input(
                "Cholesterol Level",
                100.0, 400.0, 200.0, 0.1
            )
        
        submitted = st.form_submit_button(
            "🚀 Calculate Readmission Risk",
            type="primary",
            use_container_width=True
        )
    
    if submitted:
        # Simulate prediction with a more sophisticated model
        with st.spinner("Analyzing patient data and predicting risk..."):
            # Simulate processing time
            import time
            time.sleep(1.5)
            
            # Calculate risk score (simulated ML model)
            risk_factors = {
                'age': min(0.3, age / 100),
                'length_of_stay': min(0.25, length_of_stay / 100),
                'comorbidities': min(0.2, comorbidities / 10),
                'lab_abnormality': abs(100 - lab_value) / 400,
                'bmi_risk': abs(25 - bmi) / 50,
                'bp_risk': max(0, (blood_pressure - 120) / 200)
            }
            
            base_risk = 0.15  # Base readmission rate
            risk_score = base_risk + sum(risk_factors.values()) / 2
            risk_score = min(0.95, max(0.05, risk_score))  # Clamp between 5% and 95%
        
        st.markdown("---")
        st.header("🔮 Prediction Results")
        
        # Results in columns
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Risk Score Gauge
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
            
            # Risk Level
            if risk_score < 0.3:
                risk_color = "🟢"
                risk_text = "LOW RISK"
                recommendations = [
                    "Standard discharge protocol",
                    "Routine follow-up in 30 days",
                    "Provide standard patient education"
                ]
            elif risk_score < 0.7:
                risk_color = "🟡"
                risk_text = "MEDIUM RISK"
                recommendations = [
                    "Schedule follow-up within 14 days",
                    "Assign to care coordinator",
                    "Monitor vital signs regularly"
                ]
            else:
                risk_color = "🔴"
                risk_text = "HIGH RISK"
                recommendations = [
                    "Immediate care coordination needed",
                    "Schedule follow-up within 7 days",
                    "Consider home health services",
                    "Medication reconciliation required"
                ]
            
            st.markdown(f"### {risk_color} {risk_text}")
            
            # Recommendations
            st.subheader("📋 Recommended Actions")
            for i, rec in enumerate(recommendations, 1):
                st.write(f"{i}. {rec}")
        
        with col2:
            st.subheader("📊 Risk Factors")
            
            # Create risk factors visualization
            risk_df = pd.DataFrame({
                'Factor': list(risk_factors.keys()),
                'Contribution': [v * 100 for v in risk_factors.values()]
            })
            
            fig_bar = px.bar(
                risk_df,
                x='Contribution',
                y='Factor',
                orientation='h',
                color='Contribution',
                color_continuous_scale='RdYlGn_r'
            )
            
            fig_bar.update_layout(
                height=400,
                xaxis_title="Contribution to Risk (%)",
                yaxis_title="",
                showlegend=False
            )
            st.plotly_chart(fig_bar, use_container_width=True)
        
        # Generate Report
        st.markdown("---")
        st.subheader("📄 Generate Report")
        
        report_text = f"""
        HEALTHCARE READMISSION RISK ASSESSMENT REPORT
        {'='*50}
        
        PATIENT INFORMATION:
        - Age: {age} years
        - Gender: {gender}
        - BMI: {bmi}
        - Blood Pressure: {blood_pressure} mmHg
        - Cholesterol: {cholesterol} mg/dL
        
        ADMISSION DETAILS:
        - Type: {admission_type}
        - Previous Length of Stay: {length_of_stay} days
        - Comorbidities: {comorbidities}
        - Lab Value: {lab_value}
        
        PREDICTION RESULTS:
        - Readmission Probability: {risk_score:.1%}
        - Risk Level: {risk_text}
        - Assessment Date: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M')}
        
        KEY RISK FACTORS:
        """
        
        for factor, value in risk_factors.items():
            report_text += f"- {factor.replace('_', ' ').title()}: {value:.1%}\n"
        
        report_text += f"""
        
        RECOMMENDATIONS:
        """
        
        for i, rec in enumerate(recommendations, 1):
            report_text += f"{i}. {rec}\n"
        
        # Download button
        st.download_button(
            label="📥 Download Complete Report",
            data=report_text,
            file_name=f"readmission_report_{age}_{gender}.txt",
            mime="text/plain"
        )

def show_data_explorer():
    st.header("🔍 Interactive Data Explorer")
    
    # Data filters in expanders
    with st.expander("🔧 Advanced Filters", expanded=False):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            gender_filter = st.multiselect(
                "Filter by Gender",
                options=st.session_state.data['gender'].unique(),
                default=st.session_state.data['gender'].unique()
            )
            
            readmission_filter = st.multiselect(
                "Readmission Status",
                options=[0, 1],
                default=[0, 1],
                format_func=lambda x: "Readmitted" if x == 1 else "Not Readmitted"
            )
        
        with col2:
            age_filter = st.slider(
                "Age Range",
                int(st.session_state.data['age'].min()),
                int(st.session_state.data['age'].max()),
                (30, 70)
            )
            
            los_filter = st.slider(
                "Length of Stay Range",
                int(st.session_state.data['length_of_stay'].min()),
                int(st.session_state.data['length_of_stay'].max()),
                (1, 14)
            )
        
        with col3:
            lab_min, lab_max = st.session_state.data['lab_value'].min(), st.session_state.data['lab_value'].max()
            lab_filter = st.slider(
                "Lab Value Range",
                float(lab_min),
                float(lab_max),
                (lab_min, lab_max)
            )
            
            sample_size = st.slider(
                "Sample Size",
                10, 1000, 200
            )
    
    # Apply filters
    filtered_data = st.session_state.data[
        (st.session_state.data['gender'].isin(gender_filter)) &
        (st.session_state.data['age'].between(age_filter[0], age_filter[1])) &
        (st.session_state.data['length_of_stay'].between(los_filter[0], los_filter[1])) &
        (st.session_state.data['lab_value'].between(lab_filter[0], lab_filter[1])) &
        (st.session_state.data['readmission'].isin(readmission_filter))
    ].sample(min(sample_size, len(st.session_state.data)))
    
    st.success(f"✅ Showing {len(filtered_data)} of {len(st.session_state.data)} records")
    
    # Visualization Options
    st.subheader("📊 Visualization Tools")
    
    viz_col1, viz_col2 = st.columns([1, 3])
    
    with viz_col1:
        chart_type = st.selectbox(
            "Chart Type",
            ["Scatter Plot", "Histogram", "Box Plot", "Violin Plot", "Density Heatmap", "3D Scatter"]
        )
        
        if chart_type == "Scatter Plot":
            x_axis = st.selectbox("X-axis", filtered_data.columns, index=2)
            y_axis = st.selectbox("Y-axis", filtered_data.columns, index=5)
            color_by = st.selectbox("Color by", ['None'] + filtered_data.columns.tolist())
        
        elif chart_type == "Histogram":
            hist_column = st.selectbox("Column", filtered_data.columns, index=2)
            split_by = st.selectbox("Split by", ['None', 'gender', 'readmission'])
        
        elif chart_type in ["Box Plot", "Violin Plot"]:
            box_column = st.selectbox("Value column", ['age', 'length_of_stay', 'lab_value'])
            group_by = st.selectbox("Group by", ['gender', 'readmission'])
    
    with viz_col2:
        if chart_type == "Scatter Plot":
            fig = px.scatter(
                filtered_data,
                x=x_axis,
                y=y_axis,
                color=None if color_by == 'None' else color_by,
                hover_data=['patient_id', 'gender', 'readmission'],
                title=f"{y_axis} vs {x_axis}",
                opacity=0.7
            )
            st.plotly_chart(fig, use_container_width=True)
        
        elif chart_type == "Histogram":
            if split_by == 'None':
                fig = px.histogram(
                    filtered_data,
                    x=hist_column,
                    nbins=30,
                    title=f"Distribution of {hist_column}"
                )
            else:
                fig = px.histogram(
                    filtered_data,
                    x=hist_column,
                    color=split_by,
                    barmode='overlay',
                    nbins=30,
                    title=f"{hist_column} by {split_by}"
                )
            st.plotly_chart(fig, use_container_width=True)
        
        elif chart_type == "Box Plot":
            fig = px.box(
                filtered_data,
                y=box_column,
                x=group_by,
                color=group_by,
                points="all",
                title=f"{box_column} Distribution by {group_by}"
            )
            st.plotly_chart(fig, use_container_width=True)
        
        elif chart_type == "Violin Plot":
            fig = px.violin(
                filtered_data,
                y=box_column,
                x=group_by,
                color=group_by,
                box=True,
                points="all",
                title=f"{box_column} Distribution by {group_by}"
            )
            st.plotly_chart(fig, use_container_width=True)
        
        elif chart_type == "Density Heatmap":
            fig = px.density_heatmap(
                filtered_data,
                x='age',
                y='length_of_stay',
                z='readmission',
                histfunc='avg',
                title="Readmission Density by Age and Length of Stay"
            )
            st.plotly_chart(fig, use_container_width=True)
        
        elif chart_type == "3D Scatter":
            fig = px.scatter_3d(
                filtered_data,
                x='age',
                y='length_of_stay',
                z='lab_value',
                color='readmission',
                title="3D View: Age vs Stay vs Lab Value"
            )
            st.plotly_chart(fig, use_container_width=True)
    
    # Data Table
    st.subheader("📋 Data Table")
    
    with st.expander("View Raw Data"):
        st.dataframe(
            filtered_data,
            use_container_width=True,
            hide_index=True
        )
        
        # Statistics
        st.subheader("📈 Summary Statistics")
        st.write(filtered_data.describe())
        
        # Download options
        col1, col2 = st.columns(2)
        with col1:
            csv = filtered_data.to_csv(index=False)
            st.download_button(
                label="📥 Download as CSV",
                data=csv,
                file_name="explorer_data.csv",
                mime="text/csv"
            )
        
        with col2:
            excel_buffer = pd.ExcelWriter('explorer_data.xlsx', engine='xlsxwriter')
            filtered_data.to_excel(excel_buffer, index=False, sheet_name='Data')
            excel_buffer.close()
            with open('explorer_data.xlsx', 'rb') as f:
                excel_data = f.read()
            st.download_button(
                label="📥 Download as Excel",
                data=excel_data,
                file_name="explorer_data.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

def show_settings():
    st.header("⚙️ Settings & Configuration")
    
    # App Information
    with st.expander("ℹ️ About This Application", expanded=True):
        st.markdown("""
        ## 🏥 Healthcare Readmission Analytics Platform
        
        **Version:** 1.0.0
        
        **Description:**
        This platform uses machine learning to predict patient readmission risk within 30 days 
        of discharge. It provides healthcare professionals with actionable insights to improve 
        patient outcomes and reduce hospital readmission rates.
        
        **Key Features:**
        - Real-time readmission risk prediction
        - Interactive data visualization
        - Patient data exploration tools
        - Customizable reporting
        - Export capabilities
        
        **Target Users:**
        - Hospital administrators
        - Clinical staff
        - Data analysts
        - Quality improvement teams
        """)
    
    # Data Management
    with st.expander("🗃️ Data Management", expanded=False):
        st.subheader("Upload New Data")
        
        uploaded_file = st.file_uploader(
            "Choose a CSV file",
            type=['csv', 'xlsx', 'xls'],
            help="Upload patient data in CSV or Excel format"
        )
        
        if uploaded_file:
            try:
                if uploaded_file.name.endswith('.csv'):
                    new_data = pd.read_csv(uploaded_file)
                else:
                    new_data = pd.read_excel(uploaded_file)
                
                st.session_state.data = new_data
                st.success(f"✅ Successfully loaded {len(new_data)} records")
                
                # Show preview
                st.write("**Data Preview:**")
                st.dataframe(new_data.head(), use_container_width=True)
                
            except Exception as e:
                st.error(f"❌ Error loading file: {str(e)}")
        
        st.subheader("Reset to Sample Data")
        if st.button("🔄 Reset to Sample Data", type="secondary"):
            # Reinitialize sample data
            np.random.seed(42)
            dates = pd.date_range('2023-01-01', '2023-12-31', freq='D')
            st.session_state.data = pd.DataFrame({
                'date': np.random.choice(dates, 1000),
                'patient_id': np.random.randint(1000, 2000, 1000),
                'age': np.random.randint(18, 90, 1000),
                'gender': np.random.choice(['Male', 'Female'], 1000),
                'length_of_stay': np.random.randint(1, 30, 1000),
                'readmission': np.random.choice([0, 1], 1000, p=[0.85, 0.15]),
                'lab_value': np.random.normal(100, 20, 1000)
            })
            st.success("✅ Reset to sample data completed!")
            st.rerun()
    
    # System Information
    with st.expander("💻 System Information", expanded=False):
        st.subheader("Environment Details")
        
        # Create a table of package versions
        versions_data = {
            "Package": ["Streamlit", "Pandas", "NumPy", "Plotly", "Python"],
            "Version": [
                st.__version__,
                pd.__version__,
                np.__version__,
                plotly.__version__,  # CORRECT: Using plotly.__version__
                sys.version.split()[0]
            ]
        }
        
        versions_df = pd.DataFrame(versions_data)
        st.table(versions_df)
        
        # System info
        st.subheader("System Details")
        col1, col2 = st.columns(2)
        
        with col1:
            st.write(f"**Platform:** {sys.platform}")
            st.write(f"**Machine:** {platform.machine()}")
        
        with col2:
            st.write(f"**Processor:** {platform.processor()}")
            st.write(f"**System:** {platform.system()} {platform.release()}")
    
    # Configuration
    with st.expander("⚙️ Application Configuration", expanded=False):
        st.subheader("Display Settings")
        
        col1, col2 = st.columns(2)
        
        with col1:
            theme = st.selectbox(
                "Theme Preference",
                ["Light", "Dark", "System Default"]
            )
            
            default_page = st.selectbox(
                "Default Page",
                ["Dashboard", "Predictions", "Data Explorer", "Settings"]
            )
        
        with col2:
            results_per_page = st.slider(
                "Results per page",
                10, 100, 20
            )
            
            auto_refresh = st.checkbox(
                "Enable auto-refresh",
                value=False
            )
        
        if st.button("💾 Save Configuration", type="primary"):
            st.success("✅ Configuration saved! (Note: This is a demo - settings are not persisted)")
    
    # Help & Support
    with st.expander("❓ Help & Support", expanded=False):
        st.subheader("Getting Help")
        
        st.markdown("""
        **Documentation:**
        - [User Guide](https://docs.example.com)
        - [API Reference](https://api.example.com)
        - [Tutorials](https://learn.example.com)
        
        **Support:**
        - Email: support@healthcare-analytics.com
        - Phone: +1-800-HEALTH-AI
        - Hours: Mon-Fri, 9AM-5PM EST
        
        **Troubleshooting:**
        1. Clear browser cache if experiencing display issues
        2. Ensure you have the latest browser version
        3. Check your internet connection
        4. Contact support for persistent issues
        """)
        
        # Debug information
        if st.checkbox("Show Debug Information"):
            st.code(f"""
            Session State Keys: {list(st.session_state.keys())}
            Data Shape: {st.session_state.data.shape if 'data' in st.session_state else 'N/A'}
            Memory Usage: {st.session_state.data.memory_usage().sum() / 1024 / 1024:.2f} MB
            """)

if __name__ == "__main__":
    main()