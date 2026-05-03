import streamlit as st
from _page_explanations import add_page_explanation, add_section_explanation
import json
import pandas as pd

st.title('ABSA Metrics Results Visualization')
add_page_explanation(__file__)

# Load results
def load_results(path='absa_metrics_results.json'):
    with open(path, 'r') as f:
        return json.load(f)

def is_nonzero(metrics):
    # Check if any main metric is non-zero
    return (
        metrics['accuracy'] > 0 or
        metrics['precision'] > 0 or
        metrics['recall'] > 0 or
        metrics['f1'] > 0
    )

def flatten_report(report):
    # Flatten classification report for display
    rows = []
    for label, scores in report.items():
        if isinstance(scores, dict):
            row = {'label': label}
            row.update(scores)
            rows.append(row)
    return pd.DataFrame(rows)

results = load_results()

nonzero = {k: v for k, v in results.items() if is_nonzero(v)}
zero = {k: v for k, v in results.items() if not is_nonzero(v)}

st.header('Non-zero Results')
add_section_explanation('Non-zero Results')
if nonzero:
    for model, metrics in nonzero.items():
        st.subheader(model)
        st.write(f"Accuracy: {metrics['accuracy']:.4f}")
        st.write(f"Precision: {metrics['precision']:.4f}")
        st.write(f"Recall: {metrics['recall']:.4f}")
        st.write(f"F1: {metrics['f1']:.4f}")
        st.write('Confusion Matrix:')
        st.dataframe(pd.DataFrame(metrics['confusion_matrix']))
        st.write('Classification Report:')
        st.dataframe(flatten_report(metrics['classification_report']))
else:
    st.write('No non-zero results found.')

st.header('Zero Results')
add_section_explanation('Zero Results')
if zero:
    st.write(', '.join(zero.keys()))
else:
    st.write('No zero results found.')
