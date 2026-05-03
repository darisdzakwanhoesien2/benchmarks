import streamlit as st
import pandas as pd

from utils.climatebert_batch_windows import batch_process_csv_windows
from utils.climatebert_groundtruth_storage_windows import load_results


CSV = "data/ground_truth_windows/absa_mapping.csv"

st.title("ClimateBERT Batch Processor (Windows)")

df = pd.read_csv(CSV)

total = len(df)

results = load_results()

processed = len(set(x["index"] for x in results if "index" in x))

st.metric("Total", total)
st.metric("Processed", processed)
st.metric("Remaining", total - processed)

progress = st.progress(processed / total if total else 0)

status = st.empty()


def update(current, total):

    progress.progress(current / total)
    status.text(f"{current}/{total}")


batch_size = st.number_input("Batch size", 1, 1000, 10)

if st.button("Run Windows Batch"):

    new, proc, total = batch_process_csv_windows(
        CSV,
        batch_size,
        update
    )

    st.success(f"{new} processed")

    st.rerun()

# import streamlit as st
# import pandas as pd

# from utils.climatebert_batch import batch_process_csv
# from utils.climatebert_groundtruth_storage_windows import (
#     load_results,
#     load_parsed
# )


# st.title("ClimateBERT Batch Processor (Fault-Tolerant)")

# CSV_PATH = "data/ground_truth_windows/absa_mapping.csv"

# df = pd.read_csv(CSV_PATH)

# total = len(df)

# results = load_results()

# processed = len(set(r["index"] for r in results if "index" in r))

# remaining = total - processed


# col1, col2, col3 = st.columns(3)

# col1.metric("Total", total)
# col2.metric("Processed", processed)
# col3.metric("Remaining", remaining)


# progress_bar = st.progress(processed / total if total > 0 else 0)


# def update_progress(current, total):

#     progress_bar.progress(current / total)

#     status_text.text(f"{current}/{total} processed")


# status_text = st.empty()


# batch_size = st.number_input(
#     "Batch size per run (safety control)",
#     min_value=1,
#     max_value=1000,
#     value=10
# )


# if st.button("Run / Resume Batch Processing"):

#     new_processed, processed_count, total_count = batch_process_csv(
#         CSV_PATH,
#         batch_size=batch_size,
#         progress_callback=update_progress
#     )

#     st.success(f"Processed {new_processed} new sentences")

#     st.rerun()


# st.divider()

# st.subheader("Parsed Results Preview")

# parsed = load_parsed()

# if parsed:

#     flat = []

#     for entry in parsed:

#         for model, data in entry["models"].items():

#             flat.append({

#                 "index": entry["index"],
#                 "model": model,
#                 "label": data["label"],
#                 "confidence": data["confidence"],
#                 "status": data["status"]

#             })

#     st.dataframe(pd.DataFrame(flat))

# import streamlit as st
# import pandas as pd

# from utils.climatebert_batch import batch_process_csv
# from utils.climatebert_groundtruth_storage import (
#     load_results,
#     load_parsed
# )


# st.title("ClimateBERT Batch Processor (Ground Truth)")

# CSV_PATH = "data/ground_truth/absa_mapping.csv"


# # preview dataset
# df = pd.read_csv(CSV_PATH)

# st.subheader("Dataset Preview")

# st.dataframe(df.head())


# total = len(df)

# st.metric("Total Sentences", total)


# # batch button
# if st.button("Run Batch ClimateBERT"):

#     progress = st.progress(0)

#     results, parsed = batch_process_csv(CSV_PATH)

#     st.success(f"Processed {len(results)} new sentences")

#     progress.progress(100)


# # show results
# st.divider()

# st.subheader("Stored Raw Results")

# results = load_results()

# if results:

#     df_results = pd.DataFrame(results)

#     st.dataframe(df_results[["index", "text"]])


# st.subheader("Stored Parsed Results")

# parsed = load_parsed()

# if parsed:

#     flat_rows = []

#     for entry in parsed:

#         for model, data in entry["models"].items():

#             flat_rows.append({

#                 "index": entry["index"],
#                 "text": entry["text"],
#                 "model": model,
#                 "status": data["status"],
#                 "label": data["label"],
#                 "confidence": data["confidence"],
#                 "error": data["error"]

#             })

#     df_parsed = pd.DataFrame(flat_rows)

#     st.dataframe(df_parsed)