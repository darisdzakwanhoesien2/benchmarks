import streamlit as st
from _shared.page_explanations import add_page_explanation, add_section_explanation
import pandas as pd
import matplotlib.pyplot as plt
from code.rule_based import run_rule_based
from code.classical_ml import run_classical_ml
from code.deep_model import run_deep_learning
from code.hybrid_model import run_hierarchical_hybrid
from code.explainability import compare_explain, explain_sentence_across_models
from code.app_state import app_state

st.title("ESG ABSA Model Tester")
add_page_explanation(__file__)

st.markdown("Enter ESG report text below and run the models to see predictions.")

text_input = st.text_area("ESG Report Text", height=200, value="""
## KINERJA EKONOMI
Kami telah meningkatkan efisiensi operasional dengan digitalisasi. Tantangan utama adalah risiko pasokan.

## KINERJA LINGKUNGAN
Kami berkomitmen untuk mengurangi emisi gas rumah kaca. Telah berhasil menerapkan energi terbarukan.

## KINERJA SOSIAL
Melakukan program pendidikan untuk masyarakat lokal. Mencapai target kesejahteraan pekerja.
""")

if st.button("Run Rule-Based Model"):
    if text_input.strip():
        with st.spinner("Running Rule-Based Model..."):
            csv_path, df, fig = run_rule_based(text_input)
        st.success("Rule-Based Model completed!")
        st.dataframe(df)
        st.pyplot(fig)
        st.download_button("Download CSV", df.to_csv(index=False), "rule_based_results.csv", "text/csv")
    else:
        st.error("Please enter some text.")

if st.button("Run Classical ML Model"):
    if text_input.strip():
        with st.spinner("Running Classical ML Model..."):
            csv_path, df, fig, coef_sent, coef_aspect = run_classical_ml(text_input)
        st.success("Classical ML Model completed!")
        st.dataframe(df)
        st.pyplot(fig)
        if not coef_sent.empty:
            st.subheader("Sentiment Coefficients")
            add_section_explanation("Sentiment Coefficients")
            st.dataframe(coef_sent)
        if not coef_aspect.empty:
            st.subheader("Aspect Coefficients")
            add_section_explanation("Aspect Coefficients")
            st.dataframe(coef_aspect)
        st.download_button("Download CSV", df.to_csv(index=False), "classical_ml_results.csv", "text/csv")
    else:
        st.error("Please enter some text.")

if st.button("Run Deep Learning Model"):
    if text_input.strip():
        with st.spinner("Running Deep Learning Model..."):
            csv_path, df, fig, interp_df = run_deep_learning(text_input)
        st.success("Deep Learning Model completed!")
        st.dataframe(df)
        st.pyplot(fig)
        if not interp_df.empty:
            st.subheader("Interpretability")
            add_section_explanation("Interpretability")
            st.dataframe(interp_df)
        st.download_button("Download CSV", df.to_csv(index=False), "deep_learning_results.csv", "text/csv")
    else:
        st.error("Please enter some text.")

if st.button("Run Hybrid Model"):
    if text_input.strip():
        with st.spinner("Running Hybrid Model..."):
            csv_path, df, fig1, fig2, fig3, metrics = run_hierarchical_hybrid(text_input)
        st.success("Hybrid Model completed!")
        st.dataframe(df)
        col1, col2, col3 = st.columns(3)
        with col1:
            st.pyplot(fig1)
        with col2:
            st.pyplot(fig2)
        with col3:
            st.pyplot(fig3)
        st.subheader("Metrics")
        add_section_explanation("Metrics")
        st.dataframe(metrics)
        st.download_button("Download CSV", df.to_csv(index=False), "hybrid_results.csv", "text/csv")
    else:
        st.error("Please enter some text.")

if st.button("Compare Models"):
    if any(app_state.get(k) for k in ["rule", "classical", "deep", "hybrid"]):
        with st.spinner("Comparing Models..."):
            merged, fig, plotly_scatter = compare_explain()
        st.success("Model Comparison completed!")
        st.dataframe(merged)
        st.pyplot(fig)
        if plotly_scatter:
            st.plotly_chart(plotly_scatter)
    else:
        st.error("Run at least one model first.")

st.header("Explain Sentence")
add_section_explanation("Explain Sentence")
sentence_input = st.text_input("Enter a sentence to explain across models")
if st.button("Explain Sentence"):
    if sentence_input.strip():
        with st.spinner("Explaining sentence..."):
            explanations = explain_sentence_across_models(sentence_input)
        st.json(explanations)
    else:
        st.error("Please enter a sentence.")