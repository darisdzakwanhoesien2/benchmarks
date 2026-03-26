import streamlit as st
import pandas as pd
import plotly.express as px
import requests
from pathlib import Path
from bs4 import BeautifulSoup

st.set_page_config(page_title="ESG Score Visualization", page_icon="📊", layout="wide")
st.title("📊 ESG Score Visualization")
st.markdown("Data Source: https://sustainability.idx.co.id/esg-score")

# Path to the Excel file
excel_path = Path(__file__).resolve().parents[1] / "data" / "ESG Score.xlsx"

# Load the data
@st.cache_data
def load_esg_data(path):
    try:
        df = pd.read_excel(path)
        return df
    except Exception as e:
        st.error(f"Failed to load ESG Score.xlsx: {e}")
        return pd.DataFrame()

df = load_esg_data(excel_path)

# Path to the HTML file
html_path = Path(__file__).resolve().parents[1] / "data" / "stock_info" / "carisaham.com_emiten_sektor_bahan-baku" / "rendered.html"

# Load the HTML data
@st.cache_data
def load_html_data(path: Path):
    try:
        with open(path, "r", encoding="utf-8") as file:
            return BeautifulSoup(file, "html.parser")
    except Exception as e:
        st.error(f"Failed to load HTML data: {e}")
        return None

soup = load_html_data(html_path)

if soup:
    table = soup.find("table", class_="table")
    if table:
        headers = [th.text.strip() for th in table.find_all("th")]
        rows = []
        profile_urls = []
        for tr in table.find_all("tr")[1:]:
            tds = tr.find_all("td")
            cells = [td.get_text(separator=" ", strip=True) for td in tds]
            # find profile link in row (first /emiten/profile/ href)
            url = None
            for a in tr.find_all("a", href=True):
                href = a["href"].strip()
                if "/emiten/profile" in href:
                    if href.startswith("http"):
                        url = href
                    else:
                        url = "https://carisaham.com" + href
                    break
            # fallback: any first link
            if url is None and tds:
                a = tds[0].find("a", href=True)
                if a:
                    href = a["href"].strip()
                    url = href if href.startswith("http") else "https://carisaham.com" + href
            if cells and len(cells) == len(headers):
                rows.append(cells)
                profile_urls.append(url)
        html_df = pd.DataFrame(rows, columns=headers)
        # add Profile URL column (may contain None)
        html_df["Profile URL"] = profile_urls
    else:
        html_df = pd.DataFrame()
else:
    html_df = pd.DataFrame()

# Display ESG Score data
if not df.empty:
    st.subheader("📋 ESG Score Table")
    st.dataframe(df, use_container_width=True)

    # Select columns for visualization
    numeric_cols = df.select_dtypes(include='number').columns.tolist()
    if len(numeric_cols) >= 2:
        x_col = st.selectbox("X-axis", numeric_cols, index=0)
        y_col = st.selectbox("Y-axis", numeric_cols, index=1)
        fig = px.scatter(df, x=x_col, y=y_col, color=numeric_cols[0], title=f"{x_col} vs {y_col}")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Not enough numeric columns for scatter plot.")

# Display HTML table data with Profile URL column
if not html_df.empty:
    st.subheader("📋 Stock Info Table (from HTML)")
    st.dataframe(html_df, use_container_width=True)

    # clickable list of profile links
    links = html_df["Profile URL"].dropna().unique().tolist()
    if links:
        st.markdown("### 🔗 Profile links")
        for u in links:
            st.markdown(f"- [{u}]({u})")

        # allow user to select a row and fetch profile HTML
        sel_idx = st.number_input("Select table row index to preview profile HTML", min_value=0,
                                  max_value=len(html_df)-1, value=0, step=1)
        sel_url = html_df.loc[sel_idx, "Profile URL"]
        if sel_url:
            if st.button("Fetch selected profile HTML"):
                @st.cache_data
                def fetch_stock_profile(url: str):
                    try:
                        r = requests.get(url, timeout=15)
                        r.raise_for_status()
                        return r.text
                    except Exception as e:
                        st.error(f"Failed to fetch profile: {e}")
                        return None
                profile_html = fetch_stock_profile(sel_url)
                if profile_html:
                    import streamlit.components.v1 as components
                    components.html(profile_html, height=600, scrolling=True)
                else:
                    st.info("No HTML returned for selected profile.")
        else:
            st.info("Selected row has no profile URL.")