def run_inference(clf, text):
    """
    Runs inference using a Hugging Face pipeline (clf) on the given text.
    Returns (outputs, error):
      - outputs: list of dicts with 'label' and 'score' keys
      - error: None if successful, or error message string
    """
    try:
        results = clf(text)
        # If pipeline returns a list of lists, flatten
        if results and isinstance(results[0], list):
            results = results[0]
        outputs = [
            {"label": r["label"], "score": r["score"]}
            for r in results
        ]
        return outputs, None
    except Exception as e:
        return None, str(e)
