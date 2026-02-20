import pandas as pd
from datetime import datetime

from api.climatebert_client_combined import predict_all_models

from utils.climatebert_parser import parse_climatebert_markdown
from utils.climatebert_groundtruth_storage import (
    save_result,
    save_parsed,
    load_results
)


def batch_process_csv(
    csv_path,
    text_column="sentence_norm",
    batch_size=1,
    progress_callback=None
):

    df = pd.read_csv(csv_path)

    existing = load_results()

    processed_indices = set(
        entry.get("index")
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

            raw_result = predict_all_models(text)

            result_entry = {

                "timestamp": datetime.now().isoformat(),
                "index": int(i),
                "text": text,
                "raw_markdown": raw_result,
                "status": "success"

            }

            # SAVE IMMEDIATELY
            save_result(result_entry)

            parsed = parse_climatebert_markdown(raw_result)

            parsed_entry = {

                "timestamp": parsed["timestamp"],
                "index": int(i),
                "text": text,
                "models": parsed["models"]

            }

            # SAVE IMMEDIATELY
            save_parsed(parsed_entry)

        except Exception as e:

            error_entry = {

                "timestamp": datetime.now().isoformat(),
                "index": int(i),
                "text": text,
                "error": str(e),
                "status": "error"

            }

            save_result(error_entry)

        new_processed += 1
        processed_count += 1

        # update progress
        if progress_callback:
            progress_callback(processed_count, total)

        # batch control
        if batch_size and new_processed >= batch_size:
            break

    return new_processed, processed_count, total

# import pandas as pd
# from datetime import datetime

# from api.climatebert_client_combined import predict_all_models

# from utils.climatebert_parser import parse_climatebert_markdown
# from utils.climatebert_groundtruth_storage import (
#     save_result,
#     save_parsed,
#     load_results
# )


# def batch_process_csv(csv_path, text_column="sentence_norm"):

#     df = pd.read_csv(csv_path)

#     existing = load_results()

#     existing_texts = set(x["text"] for x in existing)

#     results = []
#     parsed_results = []

#     for i, row in df.iterrows():

#         text = str(row[text_column])

#         if text in existing_texts:
#             continue

#         try:

#             raw_result = predict_all_models(text)

#             result_entry = {

#                 "timestamp": datetime.now().isoformat(),
#                 "index": int(i),
#                 "text": text,
#                 "raw_markdown": raw_result

#             }

#             save_result(result_entry)

#             parsed = parse_climatebert_markdown(raw_result)

#             parsed_entry = {

#                 "timestamp": parsed["timestamp"],
#                 "index": int(i),
#                 "text": text,
#                 "models": parsed["models"]

#             }

#             save_parsed(parsed_entry)

#             results.append(result_entry)
#             parsed_results.append(parsed_entry)

#         except Exception as e:

#             error_entry = {

#                 "timestamp": datetime.now().isoformat(),
#                 "index": int(i),
#                 "text": text,
#                 "error": str(e)

#             }

#             save_result(error_entry)

#     return results, parsed_results