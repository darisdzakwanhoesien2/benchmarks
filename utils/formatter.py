def format_result(result):
    """
    Normalize ESG model output into clean dictionary
    """

    if isinstance(result, dict):
        return result

    if isinstance(result, list):
        return {"output": result}

    return {"value": result}
