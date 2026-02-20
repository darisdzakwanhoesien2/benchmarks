import pandas as pd


def hf_to_df(hf_dict):

    if hf_dict is None:
        return pd.DataFrame()

    headers = hf_dict.get("headers", [])
    data = hf_dict.get("data", [])

    return pd.DataFrame(data, columns=headers)
