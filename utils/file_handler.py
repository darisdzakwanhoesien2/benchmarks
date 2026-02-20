import streamlit as st
import base64


def render_hf_image(image_dict):

    if image_dict is None:
        return

    url = image_dict.get("url")

    if url is None:
        return

    # base64 image
    if url.startswith("data:image"):

        base64_str = url.split(",")[1]
        image_bytes = base64.b64decode(base64_str)

        st.image(image_bytes)

    else:

        st.image(url)


def render_download(filepath, label="Download File"):

    if filepath is None:
        return

    try:

        with open(filepath, "rb") as f:

            st.download_button(
                label,
                f,
                file_name=filepath.split("/")[-1]
            )

    except:
        st.write(filepath)