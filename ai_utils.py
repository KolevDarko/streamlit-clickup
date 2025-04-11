from openai import OpenAI
import os


# Initialize the client with the API key from environment variable
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def generate_summary(df):
    # Aggregate KPIs
    total_spend = df['Spend ($)'].sum()
    total_conversions = df['Conversions'].sum()
    avg_roas = df['ROAS'].mean()

    # Build campaign-level stats
    df['Revenue'] = df['ROAS'] * df['Spend ($)']
    campaign_stats = df.groupby("Campaign Name").agg({
        "Spend ($)": "sum",
        "Conversions": "sum",
        "ROAS": "mean",
        "Revenue": "sum"
    }).reset_index()
    campaign_stats["AOV"] = campaign_stats["Revenue"] / campaign_stats["Conversions"]

    # Build input string
    campaign_text = ""
    for _, row in campaign_stats.iterrows():
        campaign_text += f"""
            Campaign: {row['Campaign Name']}
            - Total Spend: ${row['Spend ($)']:.2f}
            - Total Conversions: {int(row['Conversions'])}
            - Avg ROAS: {row['ROAS']:.2f}
            - Revenue: ${row['Revenue']:.2f}
            - AOV: ${row['AOV']:.2f}
        """

    prompt = f"""
        You are a marketing analyst reviewing Meta Ads campaign performance.

        Here is the account-level performance:
        - Total Spend: ${total_spend:.2f}
        - Total Conversions: {int(total_conversions)}
        - Average ROAS: {avg_roas:.2f}

        Here is the performance of each campaign:
        {campaign_text}

        Please write a professional and insightful performance summary. 
        - Compare campaign performance
        - Highlight the best and worst campaigns
        - Discuss differences in conversion volume and AOV
        - Recommend 1-2 next steps to improve underperforming campaigns
    """

    # GPT call
    response = client.chat.completions.create(
        model="gpt-4-turbo-preview",
        messages=[
            {"role": "system", "content": "You are a performance marketing analyst writing client reports."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7
    )

    return response.choices[0].message.content.strip()