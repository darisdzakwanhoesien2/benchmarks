import pandas as pd
from datetime import datetime

from api.climatebert_client_combined import predict_all_models
from utils.climatebert_parser import parse_climatebert_markdown


SUPPORTED_COLUMNS = [
    "sentence_norm",
    "sentence",
    "text"
]


def detect_text_column(df):

    for col in SUPPORTED_COLUMNS:
        if col in df.columns:
            return col

    raise Exception(
        f"No valid text column found. Available: {list(df.columns)}"
    )


def batch_process_core(
    csv_path,
    storage,
    batch_size=10,
    progress_callback=None
):

    df = pd.read_csv(csv_path)

    text_column = detect_text_column(df)

    existing = storage.load_results()

    processed_indices = set(
        entry["index"]
        for entry in existing
        if "index" in entry
    )

    total = len(df)
    processed_count = len(processed_indices)

    new_processed = 0

    for i, row in df.iterrows():

        if i in processed_indices:
            continue

        text = str(row[text_column])

        try:

            raw = predict_all_models(text)

            storage.save_result({

                "index": i,
                "text": text,
                "raw_markdown": raw,
                "timestamp": datetime.now().isoformat(),
                "status": "success"

            })

            parsed = parse_climatebert_markdown(raw)

            storage.save_parsed({

                "index": i,
                "text": text,
                "models": parsed["models"],
                "timestamp": parsed["timestamp"]

            })

        except Exception as e:

            storage.save_result({

                "index": i,
                "text": text,
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
                "status": "error"

            })

        processed_count += 1
        new_processed += 1

        if progress_callback:
            progress_callback(processed_count, total)

        if new_processed >= batch_size:
            break

    return new_processed, processed_count, total

# import pandas as pd
# from datetime import datetime

# from api.climatebert_client_combined import predict_all_models
# from utils.climatebert_parser import parse_climatebert_markdown


# SUPPORTED_COLUMNS = [
#     "sentence_norm",
#     "sentence",
#     "text"
# ]


# def detect_column(df):

#     for col in SUPPORTED_COLUMNS:
#         if col in df.columns:
#             return col

#     raise Exception(
#         f"No valid text column found. Available columns: {list(df.columns)}"
#     )


# def batch_process_core(
#     csv_path,
#     storage,
#     batch_size=10,
#     progress_callback=None
# ):

#     df = pd.read_csv(csv_path)

#     text_column = detect_column(df)

#     existing = storage.load_results()

#     processed_indices = set(
#         x["index"]
#         for x in existing
#         if "index" in x
#     )

#     total = len(df)
#     processed_count = len(processed_indices)

#     new_count = 0

#     for i, row in df.iterrows():

#         if i in processed_indices:
#             continue

#         text = str(row[text_column])

#         try:

#             raw = predict_all_models(text)

#             storage.save_result({

#                 "index": i,
#                 "text": text,
#                 "raw_markdown": raw,
#                 "timestamp": datetime.now().isoformat(),
#                 "status": "success"

#             })

#             parsed = parse_climatebert_markdown(raw)

#             storage.save_parsed({

#                 "index": i,
#                 "text": text,
#                 "models": parsed["models"],
#                 "timestamp": parsed["timestamp"]

#             })

#         except Exception as e:

#             storage.save_result({

#                 "index": i,
#                 "text": text,
#                 "error": str(e),
#                 "status": "error",
#                 "timestamp": datetime.now().isoformat()

#             })

#         processed_count += 1
#         new_count += 1

#         if progress_callback:
#             progress_callback(processed_count, total)

#         if new_count >= batch_size:
#             break

#     return new_count, processed_count, total