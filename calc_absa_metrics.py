import pandas as pd
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score, precision_score, recall_score, f1_score

# Load the CSV
df = pd.read_csv('data/absa_integration.csv')

# Define ground truth column (change as needed)
ground_truth_col = 'majority_sentiment'  # You can change this to any ground truth column

# Identify all model prediction columns (ending with '_label')
prediction_cols = [col for col in df.columns if col.endswith('_label')]

# Drop rows where ground truth is missing
filtered_df = df.dropna(subset=[ground_truth_col])

def safe_report(y_true, y_pred, labels):
    try:
        return classification_report(y_true, y_pred, labels=labels, zero_division=0, output_dict=True)
    except Exception as e:
        return str(e)

results = {}
labels = filtered_df[ground_truth_col].dropna().unique().tolist()

for pred_col in prediction_cols:
    # Drop rows where prediction is missing
    valid = filtered_df.dropna(subset=[pred_col])
    y_true = valid[ground_truth_col].astype(str)
    y_pred = valid[pred_col].astype(str)
    report = safe_report(y_true, y_pred, labels)
    cm = confusion_matrix(y_true, y_pred, labels=labels)
    acc = accuracy_score(y_true, y_pred)
    results[pred_col] = {
        'classification_report': report,
        'confusion_matrix': cm.tolist(),
        'accuracy': acc,
        'precision': precision_score(y_true, y_pred, average='weighted', zero_division=0),
        'recall': recall_score(y_true, y_pred, average='weighted', zero_division=0),
        'f1': f1_score(y_true, y_pred, average='weighted', zero_division=0),
        'support': len(y_true)
    }

# Save results to a file
import json
with open('absa_metrics_results.json', 'w') as f:
    json.dump(results, f, indent=2)

print('Metrics calculated for all model columns against ground truth:', ground_truth_col)
print('Results saved to absa_metrics_results.json')
