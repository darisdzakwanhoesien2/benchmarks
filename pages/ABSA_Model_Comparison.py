import streamlit as st
from code.classical_ml import run_classical_ml
from code.deep_model import run_deep_learning
from code.hybrid_model import run_hierarchical_hybrid
from code.rule_based import collect_aspects, polarity_basic, tone_basic
from code.explainability import compare_explain

st.set_page_config(page_title="ABSA Model Comparison", layout="wide")
st.title("ABSA Model Comparison: Input Text and Compare All Modules")

text_input = st.text_area("Enter text to process with all modules:")

if text_input:
    st.header("Rule-Based Model Output")
    aspects = collect_aspects(text_input)
    polarity = polarity_basic(text_input)
    tone = tone_basic(text_input)
    st.write(f"Aspects: {aspects}")
    st.write(f"Polarity: {polarity}")
    st.write(f"Tone: {tone}")

    st.header("Classical ML Output")
    out_csv, out_df, fig, coef_sent, coef_aspect = run_classical_ml(text_input)
    st.dataframe(out_df)
    st.write("Sentiment Coefficients:")
    st.dataframe(coef_sent)
    st.write("Aspect Coefficients:")
    st.dataframe(coef_aspect)

    st.header("Deep Model Output")
    out_csv, out_df, fig, interp_df = run_deep_learning(text_input)
    st.dataframe(out_df)
    st.write("Interpretability (Top Tokens):")
    st.dataframe(interp_df)

    st.header("Hybrid Model Output")
    _, df, fig1, _, _, metrics = run_hierarchical_hybrid(text_input)
    st.dataframe(df)
    st.write("Metrics:", metrics)

    st.header("Comparison Across Models")
    # Run all models for explainability comparison
    compare_df, compare_fig, compare_scatter = compare_explain()
    st.dataframe(compare_df)
    if compare_fig:
        st.pyplot(compare_fig)
    if compare_scatter is not None:
        st.plotly_chart(compare_scatter)
else:
    st.info("Enter text above to process and compare across all modules.")
