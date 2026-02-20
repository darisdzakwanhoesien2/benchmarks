import streamlit as st
import pandas as pd

from utils.climatebert_batch import batch_process_csv
from utils.climatebert_groundtruth_storage import load_results


CSV = "data/ground_truth/absa_mapping.csv"

st.title("ClimateBERT Batch Processor (Linux)")

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

if st.button("Run Linux Batch"):

    new, proc, total = batch_process_csv(
        CSV,
        batch_size,
        update
    )

    st.success(f"{new} processed")

    st.rerun()

# import streamlit as st
# import pandas as pd

# from utils.climatebert_batch import batch_process_csv
# from utils.climatebert_groundtruth_storage_windows import load_results


# st.title("ClimateBERT Batch Processor")

# CSV = "data/ground_truth_windows/absa_mapping.csv"

# df = pd.read_csv(CSV)

# total = len(df)

# results = load_results()

# processed = len(set(r["index"] for r in results if "index" in r))

# remaining = total - processed

# st.metric("Total", total)
# st.metric("Processed", processed)
# st.metric("Remaining", remaining)

# progress = st.progress(processed / total if total else 0)

# status = st.empty()


# def update(current, total):

#     progress.progress(current / total)

#     status.text(f"{current}/{total}")


# batch = st.number_input("Batch size", 1, 1000, 10)

# if st.button("Run Batch"):

#     new, proc, tot = batch_process_csv(

#         CSV,
#         batch_size=batch,
#         progress_callback=update

#     )

#     st.success(f"{new} processed")

#     st.rerun()