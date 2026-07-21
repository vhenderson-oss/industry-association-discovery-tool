import streamlit as st
from google import genai
import pandas as pd
import re
from datetime import datetime

import streamlit as st

api_key = st.secrets["GEMINI_API_KEY"]
st.write("Secret loaded successfully!")

# ---------------------------
# Page configuration
# ---------------------------
st.set_page_config(
    page_title="Industry Association Discovery Tool",
    page_icon="🏢",
    layout="centered"
)

# ---------------------------
# Title and instructions
# ---------------------------
st.title("🏢 Industry Association Discovery Tool")

st.markdown(
    """
Generate a list of organizations, associations, publications, and media outlets
for a chosen industry and location using **Google Gemini AI**.

### What you need
- A free Google account
- A free Gemini API key from https://aistudio.google.com/
"""
)

# ---------------------------
# User inputs
# ---------------------------
api_key = st.text_input(
    "🔑 Gemini API Key",
    type="password",
    placeholder="Paste your API key here"
)

industry = st.text_input(
    "Industry",
    placeholder="e.g., Construction, Law, Healthcare, Manufacturing"
)

location = st.text_input(
    "Location",
    placeholder="e.g., Los Angeles, Hawaii, Phoenix, Arizona"
)

# ---------------------------
# Generate button
# ---------------------------
if st.button("🚀 Generate Organizations", type="primary"):

    if not api_key or not industry or not location:
        st.error("Please enter your API key, industry, and location.")
        st.stop()

    try:
        # Initialize Gemini client
        client = genai.Client(api_key=api_key)

        # Build prompt
        prompt = f"""
You are conducting business research.

Generate a comprehensive list of REAL organizations, publications, and media outlets related to the following industry and location.

Industry:
{industry}

Location:
{location}

Include entities such as:
- Trade associations
- Professional societies
- Chambers of commerce
- Nonprofit organizations
- Councils
- Alliances
- Institutes
- Industry publications
- Industry magazines
- Industry media outlets

Include organizations that are:
- Local
- Regional
- Statewide
- National organizations with an active presence in this location

Only include organizations that currently exist or have an active chapter or office serving this location.

If you are uncertain whether an organization exists, DO NOT include it.

Return between 30 and 75 organizations whenever possible.

Return ONLY the organization names.

One organization per line.

Do not number them.

Do not include websites.

Do not include explanations.

Do not include blank lines.
"""

        # Call Gemini
        with st.spinner("Generating organizations..."):
            response = client.models.generate_content(
                model="gemini-flash-lite-latest",
                contents=prompt,
            )

        # Process results
        organizations = sorted(list(set([
            line.strip()
            for line in response.text.split("\\n")
            if line.strip()
        ])))

        # Create dataframe
        df = pd.DataFrame({
            "Organization Name": organizations
        })

        # Display results
        st.success(f"Found {len(df)} organizations")
        st.dataframe(df, use_container_width=True)

        # Create filename
        industry_clean = re.sub(r'[^a-zA-Z0-9]+', '_', industry.strip()).lower()
        location_clean = re.sub(r'[^a-zA-Z0-9]+', '_', location.strip()).lower()
        today = datetime.now().strftime("%Y-%m-%d")

        filename = f"{industry_clean}_{location_clean}_associations_{today}.csv"

        # Download button
        csv = df.to_csv(index=False).encode('utf-8')

        st.download_button(
            label="📥 Download CSV",
            data=csv,
            file_name=filename,
            mime="text/csv"
        )

    except Exception as e:
        st.error(f"Error: {str(e)}")

# ---------------------------
# Footer
# ---------------------------
st.markdown("---")
st.markdown(
    "Built with **Streamlit + Google Gemini AI** • Free for light research use"
)
