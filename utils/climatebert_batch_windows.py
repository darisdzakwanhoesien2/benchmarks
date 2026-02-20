from utils.climatebert_batch_core import batch_process_core
import utils.climatebert_groundtruth_storage_windows as storage


def batch_process_csv_windows(
    csv_path,
    batch_size=10,
    progress_callback=None
):

    return batch_process_core(
        csv_path,
        storage,
        batch_size,
        progress_callback
    )

# import pandas as pd
# from datetime import datetime

# from api.climatebert_client_combined import predict_all_models
# from utils.climatebert_parser import parse_climatebert_markdown

# from utils.climatebert_groundtruth_storage_windows import (
#     save_result,
#     save_parsed,
#     load_results
# )


# SUPPORTED_COLUMNS = [
#     "sentence_norm",
#     "sentence",
#     "text"
# ]


# def detect_column(df):

#     for col in SUPPORTED_COLUMNS:
#         if col in df.columns:
#             return col

#     raise Exception("No valid text column found")


# def batch_process_csv(
#     csv_path,
#     batch_size=10,
#     progress_callback=None
# ):

#     df = pd.read_csv(csv_path)

#     text_col = detect_column(df)

#     existing = load_results()

#     done_indices = set(
#         x["index"]
#         for x in existing
#         if "index" in x
#     )

#     total = len(df)

#     processed = len(done_indices)

#     new_count = 0

#     for i, row in df.iterrows():

#         if i in done_indices:
#             continue

#         text = str(row[text_col])

#         try:

#             raw = predict_all_models(text)

#             save_result({

#                 "index": i,
#                 "text": text,
#                 "raw_markdown": raw,
#                 "timestamp": datetime.now().isoformat(),
#                 "status": "success"

#             })

#             parsed = parse_climatebert_markdown(raw)

#             save_parsed({

#                 "index": i,
#                 "text": text,
#                 "models": parsed["models"],
#                 "timestamp": parsed["timestamp"]

#             })

#         except Exception as e:

#             save_result({

#                 "index": i,
#                 "text": text,
#                 "error": str(e),
#                 "status": "error"

#             })

#         processed += 1
#         new_count += 1

#         if progress_callback:
#             progress_callback(processed, total)

#         if new_count >= batch_size:
#             break

#     return new_count, processed, total