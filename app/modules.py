import calendar
import pandas as pd
from collections import Counter
import streamlit as st
@st.cache
def convert_df(df):
    # IMPORTANT: Cache the conversion to prevent computation on every rerun
    return df.to_csv().encode('utf-8')


def get_insight(df, reason):
    counts = pd.DatetimeIndex(df[df.reason == reason].createdAt).month
    trend = pd.DataFrame(Counter(counts).most_common(), columns=["month", "count"]).sort_values("month")
    trend['month'] = trend['month'].apply(lambda x: calendar.month_abbr[x])

    if len(trend) >1:
        start_month, end_month = trend.iloc[0]["month"], trend.iloc[-1]["month"]
        start_value = trend.iloc[0]["count"]
        percent_change = int((trend.iloc[-1]["count"] - trend.iloc[0]["count"])/trend.iloc[0]["count"]*100)
        if percent_change<0:
            insight = f"Occurances have decreased by {abs(percent_change)}% from {start_month} to {end_month}"
        elif percent_change>0:
            insight = f"Occurances have increased by {abs(percent_change)}% from {start_month} to {end_month}"
        elif percent_change==0:
            insight = f"Occurances have remained same at {start_value} from {start_month} to {end_month}"
    else:
        start_month = end_month = trend.iloc[0]["month"]
        percent_change = 0
        count = trend.iloc[0]["month"]
        insight = f"Occurances have been {count} in the month of {start_month}"

    return pd.Series([start_month, end_month, percent_change, insight])
