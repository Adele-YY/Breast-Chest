# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

import streamlit as st
import plotly.express as px
import pandas as pd
import re

st.set_page_config(page_title="", page_icon="🎀", layout="wide")

@st.cache_data
def load_data():
     return pd.read_csv("/Users/14708034428139.com/Desktop/cleaned_breast_cancer.csv")

bc = load_data()
data = pd.read_csv('/Users/14708034428139.com/Desktop/cleaned_bc_population.csv')
time = pd.read_csv('/Users/14708034428139.com/Desktop/cleaned_bc_time.csv')

st.title("Breast Cancer")

# color
st.markdown("""
    <style>
    body {
        background: linear-gradient(135deg, #fff5fb, #ffeaf4, #ffddee);
        background-attachment: fixed;
    }

    .stApp {
        background: transparent;
    }

    section[data-testid="stSidebar"] {
        background-color: #e6e0f8 !important; 
        border-top-right-radius: 20px;
        border-bottom-right-radius: 20px;
        padding: 1rem;
    }

    .stSidebar > div {
        color: #5a3e99; 
    }
    </style>
""", unsafe_allow_html=True)

# pictures
col1, col2 = st.columns(2)

with col1:
    st.image("https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSswOO8qnGkTmgvITqd0p1PrfF10cjUPHclUg&s", width=280)

with col2:
    st.image("https://my.clevelandclinic.org/-/scassets/Images/org/health/articles/3986-breast-cancer", width=150)

st.subheader("the most common cancer in women")

# text

st.markdown(
    """
    <p style="font-size:16px; line-height:1.6;">
    Breast cancer is the <strong>most common cancer</strong> amongst women worldwide.<br><br>
    It starts when cells in the breast begin to grow out of control.<br>
    These cells usually form tumors that can be seen via X-ray or felt as lumps in the breast area.<br><br>
    The key challenge in detection is how to classify tumors into <span style="color:#e63946;"><strong>malignant (cancerous)</strong></span> or <span style="color:#1d3557;"><strong>benign (non-cancerous)</strong></span>.
    </p>
    """, 
    unsafe_allow_html=True
)

# donut chart

show_chart = st.checkbox("Want to know malignancy rate?", value=False)  # default

if show_chart:
    diagnosis_counts = bc['diagnosis'].value_counts().reset_index()
    diagnosis_counts.columns = ['diagnosis', 'count']
    
    fig = px.pie(
        diagnosis_counts,
        values='count',
        names='diagnosis',
        hole=0.4,
        title="Malignancy Rate", 
        color_discrete_sequence=["rgb(10,255,134)", "rgb(255, 130, 130)"]
    )
    
    st.plotly_chart(fig)

# population around the world

st.markdown("<h3>Population Around the World</h3>", unsafe_allow_html=True)

fig = px.choropleth(
    data_frame=data,
    locations='Alpha‑3 code',
    color='ASR (World) per 100 000',
    hover_name='Alpha‑3 code',
    color_continuous_scale='Reds',
    labels='ASR (World) per 100 000',
    title='Global Breast Cancer Cases Heatmap'
)

st.plotly_chart(fig, use_container_width=True)

# Over time
st.markdown("<h3>Cancer Incidence Rate Over Time</h3>", unsafe_allow_html=True)
st.sidebar.header("Explore Countries & Rates📈")

all_countries = sorted(time['country'].dropna().unique())
default_country = "Germany" if "Germany" in all_countries else all_countries[0]

selected_countries = st.sidebar.multiselect(
    "Select Country/Countries", 
    options=all_countries, 
    default=[default_country]
)

rate_type = st.sidebar.selectbox("Select Rate Type", ["crude_rate", "ASR (World)"])

filtered_data = time[time['country'].isin(selected_countries)]

## create figure
fig = px.line(
    filtered_data,
    x="year",
    y=rate_type,
    color="country",
    markers=True,
    title=f"{rate_type.replace('_', ' ').title()} Over Time"
)

fig.update_layout(
    xaxis_title="Year",
    yaxis_title=rate_type.replace('_', ' ').title(),
    template="plotly_white"
)

st.plotly_chart(fig)


# distribution of each feature

## sidebar
st.sidebar.header("Filter Tumors 🔍")

st.markdown("<h3>Tumor Features</h3>", unsafe_allow_html=True)

all_cols = [col for col in bc.columns if col != "diagnosis"]

## grouping
pattern = re.compile(r"^(.*?)(_mean|_se|_worst)$")

base_features = set()
suffixes = set()

for col in all_cols:
    m = pattern.match(col)
    if m:
        base_features.add(m.group(1))
        suffixes.add(m.group(2))

base_features = sorted(base_features)
suffixes = sorted(suffixes)

suffixes = sorted(suffixes)
if '_se' in suffixes:
    suffixes.remove('_se')
    suffixes.append('_se')

def beautify(s):
    if s.lower() == '_se':
        return 'Standard Error'
    else:
        return s.replace('_', ' ').title()

base_features_display = [beautify(f) for f in base_features]
suffixes_display = [beautify(s) for s in suffixes]

selected_base_display = st.sidebar.selectbox("Select feature", base_features_display)
selected_suffix_display = st.sidebar.selectbox("Select specific data", suffixes_display)

selected_base = base_features[base_features_display.index(selected_base_display)]
selected_suffix = suffixes[suffixes_display.index(selected_suffix_display)]

selected_feature = selected_base + selected_suffix

if selected_feature not in bc.columns:
    st.error(f"Feature '{selected_feature}' not found in dataset.")
else:
    fig_hist = px.histogram(
        bc,
        x=selected_feature,
        color='diagnosis',
        nbins=30,
        opacity=0.7,
        marginal='rug',
        barmode='overlay',
        title=f"Distribution of {selected_feature}"
    )

    fig_hist.update_layout(
        xaxis_title=selected_feature,
        yaxis_title="Count",
        bargap=0.05
    )

    st.plotly_chart(fig_hist)
    
# find correlation

st.markdown("<h3>Is there any relationship?</h4>", unsafe_allow_html=True)

st.sidebar.header("Find Relationship 🔗")

numeric_cols = [col for col in bc.columns if col != "diagnosis"]

col_x = st.sidebar.selectbox("Select X", numeric_cols, key="x_axis")
col_y_options = [col for col in numeric_cols if col != col_x]
col_y = st.sidebar.selectbox("Select Y", col_y_options, key="y_axis")

fig_scatter = px.scatter(
    bc,
    x=col_x,
    y=col_y,
    opacity=0.7,
    trendline="ols",
    title=f"Relationship between {col_x} & {col_y}"
)

fig_scatter.update_layout(
    xaxis_title=col_x,
    yaxis_title=col_y,
)

st.plotly_chart(fig_scatter)


# raw data
st.markdown("<h3>Sample of Raw Data</h3>", unsafe_allow_html=True)
st.dataframe(bc.head())
st.dataframe(data.head())
st.dataframe(time.head())






