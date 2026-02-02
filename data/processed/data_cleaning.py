import numpy as np 
import pandas as pd 
from datetime import datetime, timedelta

class HealthcareDataCleaner:
    def __init__(self, df):
        self.df = df.copy()
        self.cleaning_log=[]

    def handle_missing_values(self):
        """Misiing values imputation"""
        original_rows = len(self)

        #REMOVE ROWS WITH CRITICAL MISSING VALUES

        self.df = self.df.dropna(subset=['admission_date', 'discharge_date'])
        
        #Impute missing lab values with group medians
        if 'lab_value' in self.df.columns:
            self.df['lab_value'] = self.df.groupby('item_id')['lab_value']\
                .transform(lambda x: x.fillna(x.median()))
            
            self.cleaning_log.append(f"Remove {original_rows - len(self.df)}rows with critical missing values")
            return self
        def detect_outliers_iqr(self, column):
            """DETECT OUTLIERS USING IQR METHOD"""
            Q1 = self.df[column].quantile(0.25)
            Q3 = self.df[column].quantilw(0.75)
            IQR = Q3 - Q1 
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR 

            outliers = self.df[(self.df[column] < lower_bound) | (self.df[column] > upper_bound)]
            return outliers, lower_bound, upper_bound
        
        def create_feature(self):
            """FEATURE ENGINEERING FOR MODEL PREDICTION"""
            #CALCULATING READMISSION FLAG(TARGETV VARIABLE)

            self.df['admission_date'] = pd.to_datetime(self.df['admission_date'])
            self.df['discharge_date'] = pd.to_datetime(self.df['dsicharge_date'])

            #Sort by patient admission date
            self.df = self.df.sort_values(['patient_id', 'admission_date'])

            # Calculate days to next admission(readmission within 30 days)
            self.df['next_admission_date'] = self.df.groupby('patient_id')
            ['admission_date'].shift(-1)
            self.df['days_to_readmit'] = (self.df['next_admission_date'] -self.df['discharge_date']).dt.days

            #Creating target variable: readmission within 30 days
            self.df['readmission_30d'] = (self.df['days_to_readmit'] <= 30).astype(int)

            #Create temporal features
            self.df['admission_month'] = self.df['admission_date'].dt.month
            self.df['admission_dayofweek'] = self.df['admission_date'].dt.dayofweek
            self.df['admission_hour'] = self.df['admission_date'].dt.hour
            self.cleaning_log.append("Created temporal features and readmission target")
            return self
        
        def get_cleaning_report(self):
            """Generate Comprehensive cleaning report"""
            report = "🧹 DATA CLEANING REPORT\n" + "="*50 + "\n"
            for log_entry in self.cleaning_log:
                report += f" {log_entry}\n"
            report += f"\n📊 Final Dataset Shape: {self.df.shape}"
            report += f"\n✅ Columns: {list(self.df.columns)}"
            return report
        