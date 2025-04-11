import streamlit as st
import pandas as pd
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from ai_utils import generate_summary

# Page config
st.set_page_config(page_title="Meta Ads Client Report", layout="centered")

st.title("📊 Meta Ads Client Report Generator")
st.markdown(
    "Upload your exported Meta Ads data (CSV) to generate a client-ready report."
)

# Upload CSV
uploaded_file = st.file_uploader("Upload Meta Ads CSV", type=["csv"])

import matplotlib.pyplot as plt

def plot_spend_by_campaign(df):
    df['Date'] = pd.to_datetime(df['Date'])
    pivot = df.pivot_table(index='Date', columns='Campaign Name', values='Spend ($)', aggfunc='sum')

    st.subheader("💸 Daily Spend by Campaign")
    fig, ax = plt.subplots()
    pivot.plot(ax=ax, marker='o')
    ax.set_ylabel("Spend ($)")
    ax.set_xlabel("Date")
    ax.set_title("Spend Over Time")
    st.pyplot(fig)

def plot_avg_roas(df):
    roas_avg = df.groupby("Campaign Name")["ROAS"].mean().sort_values()

    st.subheader("📈 Average ROAS by Campaign")
    fig, ax = plt.subplots()
    roas_avg.plot(kind='barh', color='skyblue', ax=ax)
    ax.set_xlabel("ROAS")
    ax.set_title("Avg ROAS per Campaign")
    st.pyplot(fig)

def plot_conversions_vs_spend(df):
    st.subheader("🎯 Conversions vs Spend")
    fig, ax = plt.subplots()
    for name, group in df.groupby("Campaign Name"):
        ax.scatter(group["Spend ($)"], group["Conversions"], label=name)

    ax.set_xlabel("Spend ($)")
    ax.set_ylabel("Conversions")
    ax.set_title("Spend vs Conversions")
    ax.legend()
    st.pyplot(fig)        

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    st.success("✅ Data uploaded successfully!")

    # Preview data
    with st.expander("📄 Preview Raw Data"):
        st.dataframe(df.head())

    # Generate report button
    if st.button("🔍 Generate AI-Powered Report"):
        with st.spinner("Analyzing your campaigns..."):
            st.subheader("📈 Performance Summary")
            summary = generate_summary(df)
            st.write(summary)
            plot_spend_by_campaign(df)
            plot_avg_roas(df)
            plot_conversions_vs_spend(df)


else:
    st.warning("👆 Please upload a CSV to get started.")
