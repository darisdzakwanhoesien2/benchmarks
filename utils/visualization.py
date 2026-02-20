import streamlit as st
import base64
import io
import json


def _decode_base64_image(data_str: str):
    """
    Decode base64 image string from HuggingFace Gradio

    Supports formats like:
    data:image/png;base64,...
    data:image/webp;base64,...
    """

    try:

        # Remove header if exists
        if "," in data_str:
            base64_str = data_str.split(",", 1)[1]
        else:
            base64_str = data_str

        image_bytes = base64.b64decode(base64_str)

        return image_bytes

    except Exception as e:

        st.error(f"Failed to decode base64 image: {e}")

        return None


def _render_plotly(plot_data):
    """
    Render plotly safely
    """

    try:

        # Already figure
        st.plotly_chart(plot_data, use_container_width=True)

    except Exception:

        try:

            # If JSON string
            if isinstance(plot_data, str):
                plot_json = json.loads(plot_data)

                import plotly.io as pio

                fig = pio.from_json(json.dumps(plot_json))

                st.plotly_chart(fig, use_container_width=True)

        except Exception:

            st.warning("Unable to render Plotly chart.")
            st.write(plot_data)


def _render_matplotlib(plot_data):
    """
    Render matplotlib safely
    """

    try:

        # Case 1: base64 string (most common from HF)
        if isinstance(plot_data, str):

            image_bytes = _decode_base64_image(plot_data)

            if image_bytes is not None:
                st.image(image_bytes, use_container_width=True)
                return

        # Case 2: matplotlib figure object
        st.pyplot(plot_data)

    except Exception as e:

        st.warning(f"Matplotlib rendering failed: {e}")
        st.write(plot_data)


def _render_altair(plot_data):
    """
    Render altair safely
    """

    try:

        import altair as alt

        if isinstance(plot_data, dict):
            chart = alt.Chart.from_dict(plot_data)
            st.altair_chart(chart, use_container_width=True)
        else:
            st.altair_chart(plot_data, use_container_width=True)

    except Exception:

        st.write(plot_data)


def _render_bokeh(plot_data):
    """
    Render bokeh safely
    """

    try:

        from streamlit.components.v1 import html

        html(plot_data)

    except Exception:

        st.write(plot_data)


def render_plot(plot_dict):
    """
    Universal HuggingFace Gradio plot renderer

    Supports:
    - matplotlib (base64 + object)
    - plotly (object + JSON)
    - altair
    - bokeh
    - base64 images
    - raw fallback

    Input format:
    {
        "type": "...",
        "plot": ...
    }
    """

    if plot_dict is None:

        st.info("No visualization returned.")

        return

    if not isinstance(plot_dict, dict):

        st.warning("Invalid plot format.")
        st.write(plot_dict)

        return

    plot_type = plot_dict.get("type")
    plot_data = plot_dict.get("plot")

    if plot_data is None:

        st.info("Empty visualization.")

        return

    try:

        # Normalize type
        if plot_type:
            plot_type = plot_type.lower()

        # matplotlib
        if plot_type == "matplotlib":

            _render_matplotlib(plot_data)

        # plotly
        elif plot_type == "plotly":

            _render_plotly(plot_data)

        # altair
        elif plot_type == "altair":

            _render_altair(plot_data)

        # bokeh
        elif plot_type == "bokeh":

            _render_bokeh(plot_data)

        # fallback: detect base64 image automatically
        elif isinstance(plot_data, str) and plot_data.startswith("data:image"):

            image_bytes = _decode_base64_image(plot_data)

            if image_bytes:
                st.image(image_bytes, use_container_width=True)

        # fallback generic
        else:

            st.write(plot_data)

    except Exception as e:

        st.error("Visualization rendering failed.")
        st.exception(e)

        # debug fallback
        with st.expander("Debug visualization data"):
            st.write(plot_dict)


# import streamlit as st
# import base64
# import io


# def render_plot(plot_dict):
#     """
#     Render HuggingFace Gradio plot safely
#     Supports:
#     - plotly
#     - matplotlib (serialized)
#     - altair
#     - bokeh
#     """

#     if plot_dict is None:
#         st.warning("No plot returned.")
#         return

#     plot_type = plot_dict.get("type")
#     plot_data = plot_dict.get("plot")

#     if plot_data is None:
#         st.warning("Empty plot.")
#         return

#     try:

#         # Plotly (sometimes JSON or object)
#         if plot_type == "plotly":

#             try:
#                 st.plotly_chart(plot_data, use_container_width=True)
#             except:
#                 st.write(plot_data)

#         # Matplotlib serialized image
#         elif plot_type == "matplotlib":

#             # case 1: base64 image string
#             if isinstance(plot_data, str):

#                 try:
#                     image_bytes = base64.b64decode(plot_data)
#                     st.image(image_bytes)

#                 except:
#                     st.write("Matplotlib plot received (serialized).")

#             else:
#                 st.pyplot(plot_data)

#         elif plot_type == "altair":

#             st.write(plot_data)

#         elif plot_type == "bokeh":

#             st.write(plot_data)

#         else:

#             st.write("Unsupported plot type:", plot_type)

#     except Exception as e:

#         st.error(f"Plot rendering failed: {e}")
#         st.write(plot_dict)


# import streamlit as st


# def render_plot(plot_dict):

#     if plot_dict is None:
#         return

#     plot_type = plot_dict.get("type")

#     if plot_type == "plotly":
#         st.plotly_chart(plot_dict["plot"])

#     elif plot_type == "matplotlib":
#         st.pyplot(plot_dict["plot"])

#     else:
#         st.write("Visualization available")
