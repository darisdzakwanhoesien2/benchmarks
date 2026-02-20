# pages/3_ABSA_Classical.py

import streamlit as st

from api.absa_client import run_classical
from utils.dataframe import hf_to_df
from utils.visualization import render_plot


st.title("ABSA Classical ML")

text = st.text_area("Enter ESG Text")


if st.button("Run Classical ABSA"):

    if not text.strip():

        st.warning("Please enter text before running ABSA.")
        st.stop()

    with st.spinner("Running Classical ABSA..."):

        try:

            result = run_classical(text)

            if result is None:
                st.error("No result returned.")
                st.stop()

            csv = result[0]
            predictions = hf_to_df(result[1])
            plot = result[2]
            sentiment_coef = hf_to_df(result[3])
            aspect_coef = hf_to_df(result[4])

            st.subheader("Predictions")
            st.dataframe(predictions)

            st.subheader("Visualization")
            render_plot(plot)

            st.subheader("Sentiment Coefficients")
            st.dataframe(sentiment_coef)

            st.subheader("Aspect Coefficients")
            st.dataframe(aspect_coef)

            # ✅ SAFE CSV handling
            if csv is not None:

                with open(csv, "rb") as f:

                    st.download_button(
                        "Download CSV",
                        f,
                        file_name="absa_classical.csv"
                    )

            else:

                st.info("No CSV file returned by API.")

        except Exception as e:

            st.error("ABSA Classical model failed.")
            st.exception(e)


# import streamlit as st

# from api.absa_client import run_classical
# from utils.dataframe import hf_to_df
# from utils.visualization import render_plot


# st.title("ABSA Classical ML")

# text = st.text_area("Enter ESG Text")


# if st.button("Run Classical ABSA"):

#     if not text.strip():

#         st.warning("Please enter text before running ABSA.")
#         st.stop()

#     with st.spinner("Running Classical ABSA..."):

#         try:

#             result = run_classical(text)

#             csv = result[0]
#             predictions = hf_to_df(result[1])
#             plot = result[2]
#             sentiment_coef = hf_to_df(result[3])
#             aspect_coef = hf_to_df(result[4])

#             st.subheader("Predictions")
#             st.dataframe(predictions)

#             st.subheader("Visualization")
#             render_plot(plot)

#             st.subheader("Sentiment Coefficients")
#             st.dataframe(sentiment_coef)

#             st.subheader("Aspect Coefficients")
#             st.dataframe(aspect_coef)

#             st.download_button(
#                 "Download CSV",
#                 open(csv, "rb"),
#                 file_name="absa_classical.csv"
#             )

#         except Exception as e:

#             st.error("ABSA Classical model failed.")
#             st.exception(e)


# import streamlit as st

# from api.absa_client import run_classical
# from utils.dataframe import hf_to_df
# from utils.visualization import render_plot


# st.title("ABSA Classical ML")

# text = st.text_area("Enter ESG Text")

# if st.button("Run Classical ABSA"):

#     result = run_classical(text)

#     csv = result[0]
#     predictions = hf_to_df(result[1])
#     plot = result[2]
#     sentiment_coef = hf_to_df(result[3])
#     aspect_coef = hf_to_df(result[4])

#     st.dataframe(predictions)
#     render_plot(plot)

#     st.subheader("Sentiment Coefficients")
#     st.dataframe(sentiment_coef)

#     st.subheader("Aspect Coefficients")
#     st.dataframe(aspect_coef)

#     st.download_button(
#         "Download CSV",
#         open(csv, "rb"),
#         file_name="absa_classical.csv"
#     )
