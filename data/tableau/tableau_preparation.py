# tableau_preparation.py
def prepare_for_tableau(df):
    """Prepare and export data for Tableau dashboard"""
    
    # Aggregate data at patient-admission level
    tableau_data = df.groupby(['patient_id', 'admission_id']).agg({
        'gender': 'first',
        'admission_age': 'first',
        'admission_date': 'first',
        'discharge_date': 'first',
        'length_of_stay': 'first',
        'diagnosis': 'first',
        'admission_type': 'first',
        'readmission_30d': 'max',
        'lab_value': ['mean', 'std', 'count']
    }).reset_index()
    
    # Flatten multi-index columns
    tableau_data.columns = ['_'.join(col).strip('_') for col in tableau_data.columns]
    
    # Calculate lab value volatility
    tableau_data['lab_value_volatility'] = tableau_data['lab_value_std'] / tableau_data['lab_value_mean']
    
    # Export to CSV for Tableau
    tableau_data.to_csv('tableau_healthcare_data.csv', index=False)
    tableau_data.to_excel('tableau_healthcare_data.xlsx', index=False)
    
    print(f"✅ Tableau data exported: {len(tableau_data)} records")
    print(f"📁 Files created: tableau_healthcare_data.csv, tableau_healthcare_data.xlsx")
    
    return tableau_data