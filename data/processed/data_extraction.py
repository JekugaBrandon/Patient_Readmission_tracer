import pandas as pd
def extract_patient_journey():
    """EXTRACT COMPREHENSIVE PATEINTS JOURNEY WITH SQL JOINS"""
    query = """
    SELECT 
        p.patient_id,
        p.gender,
        p.admission_age,
        a.admission_id,
        a.admission_date,
        a.discharge_date,
        a.diagnosis,
        DATEDIFF(a.discharge_date, a.admission_date) AS length_of_stay,
        l.item_id,
        l.valuenum as lab_value,
        l.valueuom as lab_unit,
        l.charttime as lab_time
    FROM patients p
    JOIN admissions a ON p.patient_id = a.patient_id
    LEFT JOIN lab_events l ON a.admission_id = l.admission_id
    WHERE a.discharge_date IS NOT NULL
    AND l.valuenum IS NOT NULL
    ORDER BY p.patient_id, a.admission_date, l.charttime;
    """

    engine = create_engine('mysql+mysqlconnector://root:Jekuga70$@localhost/healthcare_analytics')
    df = pd.read_sql(query, engine)
    print(f"✅ Extracted {len(df):,} records with {df.shape[1]} columns") 
    
    #initial query quality report

    print("\n🔍 DATA QUALITY REPORT:")
    print(f"Mising Values: {df.isnull().sum().sum()}")
    print(f"Duplicate Rows {df.duplicated().sum()}")

    return df