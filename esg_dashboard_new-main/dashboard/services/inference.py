def run_inference(clf, text):
    """
    Run inference and normalize transformer pipeline outputs.
    Returns (outputs, None) or (None, error_message).
    """
    try:
        outputs = clf(text)

        if isinstance(outputs, list) and len(outputs) == 1 and isinstance(outputs[0], list):
            outputs = outputs[0]
        elif isinstance(outputs, dict):
            outputs = [outputs]

        return outputs, None
    except Exception as e:
        return None, str(e)
