from scipy.stats import ttest_ind, chi2_contingency  
import pandas as pd

def perform_statistical_tests(df):
    """run statistical tests for insights"""

    # T-test: Length stay for readmission VS non-readmission

    los_readmitted = df[df['readmisson_30d'] ==1]['lenght_of_stay']
    los_non_readmitted = df[df['readmission_30d'] == 0]['lenght_of_stay']
    t_stat, p_value = ttest_ind(los_readmitted, los_non_readmitted, nan_policy='omit')

    #Chi-square test: Gender amd readmisson
    contingency_table = pd.crosstab(df['gender'], df['readmission_30d'])
    chi2, p_chi, dof, expected = chi2_contingency(contingency_table)

    print("📊 STATISTICAL TEST RESULTS")
    print("="*50)
    print(f"T-test (LOS difference): t={t_stat:.3f}, p={p_value:.4f}")
    print(f"Chi-square (gender): χ²={chi2:.3f}, p={p_chi:.4f}")

    if p_value < 0.05:
        print("✅ Significant difference in LOS between readmission and non-readmitted patients")
        if p_chi < 0.05:
            print("✅ Significanr association between gender and readmission")

            return {
                't_test': (t_stat, p_value),
                'chi_square': (chi2, p_chi)
            }