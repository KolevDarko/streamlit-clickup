ADS_SUMMARY_PROMPT = """
You are a marketing analyst helping an agency write a Meta Ads report.

Here is campaign performance data:
- Total Spend: ${total_spend:.2f}
- Total Conversions: {total_conversions}
- Average ROAS: {avg_roas:.2f}

Best performing campaign:
- Name: {best['Campaign Name']}
- ROAS: {best['ROAS']}
- Conversions: {best['Conversions']}
- Spend: ${best['Spend ($)']:.2f}

Worst performing campaign:
- Name: {worst['Campaign Name']}
- ROAS: {worst['ROAS']}
- Conversions: {worst['Conversions']}
- Spend: ${worst['Spend ($)']:.2f}

Write a short, clear, professional performance summary for the client. Include insights, celebrate wins, and suggest 1 idea to improve the lowest campaign.
"""