import os
from unicodedata import name
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import datetime
import altair as alt
from scipy.ndimage.filters import gaussian_filter1d
from modules import get_insight,convert_df
from st_aggrid import GridOptionsBuilder, AgGrid, GridUpdateMode, DataReturnMode


def page1_1(customer:str):

    st.header("Top Reasons")
    data = st.session_state.data
    cdata = data.copy()
    cdata["createdAt"] = pd.to_datetime(data["createdAt"]).dt.date
    
    cdata = cdata[(cdata["createdAt"]>st.session_state.start_date)&(cdata["createdAt"]<st.session_state.end_date)]

    #cdata["reason"] = cdata["reason"].apply(lambda x: eval(x))
    
    cdata = pd.DataFrame({'count' : cdata.groupby( [ "id", "reason"] ).size()}).reset_index()
    cdata = pd.DataFrame({'count' : cdata.groupby( ["reason"] ).size()}).reset_index()
    cdata = cdata.sort_values('count',ascending=False)

    chart = alt.Chart(cdata[:min(len(cdata),st.session_state["top_k"])],height=500).mark_text(size=10).mark_bar().encode(
        alt.X("reason",sort="-y"),
        alt.Y("count"),
        alt.Color("reason"),
        alt.Tooltip(["reason", "count"]),
    ).interactive()

    st.altair_chart(chart,use_container_width=True)

def page1_2(customer:str):
    st.header("Sentiment Distribution")
    data = st.session_state.data
    cdata = data.copy()
    cdata["createdAt"] = pd.to_datetime(data["createdAt"]).dt.date
    
    cdata = cdata[(cdata["createdAt"]>st.session_state.start_date)&(cdata["createdAt"]<st.session_state.end_date)]
    cdata = cdata.groupby(['id'])['sentiment'].agg(pd.Series.mode).reset_index()

    cdata = pd.DataFrame({'count' : cdata.groupby( ["sentiment"] ).size()}).reset_index()
    domain = ['Negative', 'Positive', 'Neutral']
    range_ = ['red', 'green', 'blue']
    chart = alt.Chart(cdata,height=500).mark_text(size=10).mark_bar().encode(
        alt.X("sentiment",sort="-y"),
        alt.Y("count"),
        alt.Color("sentiment",scale=alt.Scale(domain=domain,range=range_,scheme="accent")),
        alt.Tooltip(["sentiment", "count"]),
    ).interactive()

    st.altair_chart(chart,use_container_width=True)

def page1_3(customer:str):
    
    st.header("Top Entities")
    data = st.session_state.data
    cdata = data.copy()
    cdata["createdAt"] = pd.to_datetime(data["createdAt"]).dt.date
    
    cdata = cdata[(cdata["createdAt"]>st.session_state.start_date)&(cdata["createdAt"]<st.session_state.end_date)]
    cdata = cdata.explode("entity")
    cdata["entity"] = cdata["entity"].str.title()
    #cdata["reason"] = cdata["reason"].apply(lambda x: eval(x))
    
    cdata = pd.DataFrame({'count' : cdata.groupby( [ "id", "entity"] ).size()}).reset_index()
    cdata = pd.DataFrame({'count' : cdata.groupby( ["entity"] ).size()}).reset_index()
    cdata = cdata.sort_values('count',ascending=False)

    chart = alt.Chart(cdata[:min(len(cdata),st.session_state["top_k"])],height=500).mark_text(size=10).mark_bar().encode(
        alt.X("entity",sort="-y"),
        alt.Y("count"),
        alt.Color("entity"),
        alt.Tooltip(["entity", "count"]),
    ).interactive()

    st.altair_chart(chart,use_container_width=True)


def page1_4(customer:str):
    st.header("Average Sentiment Trend")

    data = st.session_state.data
    cdata = data.copy()
    cdata["date"] = cdata["createdAt"]
    cdata["createdAt"] = pd.to_datetime(data["createdAt"]).dt.date
    
    cdata = cdata[(cdata["createdAt"]>st.session_state.start_date)&(cdata["createdAt"]<st.session_state.end_date)]
    
    cdata["sindex"] = cdata["sentiment"].apply(lambda x: 1 if x=="Positive" else 0.5 if x=="Neutral" else 0)
    cdata = cdata.groupby(['id','date'])['sindex'].agg(pd.Series.mean).reset_index()

    cdata = cdata.groupby([pd.Grouper(key='date', freq='W-MON')])['sindex'] \
       .mean() \
       .reset_index() \
       .sort_values('date')
    
    series = cdata["sindex"].values.tolist()
    series = gaussian_filter1d(series, sigma=2)

    cdata["sindex"] = series
    cdata["legend"] = "sentiment index"

    domain = ['sentiment index']
    range_ = ['red']
    chart = alt.Chart(cdata).mark_line().encode(
        x='date',
        y=alt.Y('sindex',scale=alt.Scale(zero=False)),
        color = alt.Color("legend",scale=alt.Scale(domain=domain,range=range_,scheme="accent"))
    )

    st.altair_chart(chart,use_container_width=True)


def page1_5(customer:str):
    st.header("Reason Trends")

    data = st.session_state.data
    cdata = data.copy()
    cdata["date"] = cdata["createdAt"]
    cdata["createdAt"] = pd.to_datetime(data["createdAt"]).dt.date
    cdata = cdata[(cdata["createdAt"]>st.session_state.start_date)&(cdata["createdAt"]<st.session_state.end_date)]

    rdata = cdata.copy()

    rdata = pd.DataFrame({'count' : rdata.groupby( [ "id", "reason"] ).size()}).reset_index()
    rdata = pd.DataFrame({'count' : rdata.groupby( ["reason"] ).size()}).reset_index()
    rdata = rdata.sort_values('count',ascending=False)

    
    # min_count = st.sidebar.slider(
    #     "min_reason_count",
    #     min_value = 1,
    #     max_value=1000,
    #     value = 10,
    #     key="min_r_count"
    # )
    min_count = 10
    rdata = rdata[rdata["count"]>min_count]
    reasons = rdata["reason"].values.tolist()
    counts = rdata["count"].values.tolist()

    percent_change = []
    insights = []
    for reas in reasons:
        insight = get_insight(cdata,reas)
        percent_change.append(insight[2])
        insights.append(insight[3])

    # min_per = st.sidebar.slider(
    #     "min_%_count",
    #     min_value = 1,
    #     max_value=100,
    #     value = 5,
    #     key="min_per_count"
    # )
    min_per = 5
    df = pd.DataFrame()
    df["Reason"] = reasons
    df["percentage"] = [abs(p) for p in percent_change]
    df["Insight"] = insights
    df["Total Counts"] = counts

    df = df[df["percentage"]>min_per]
    cdata = df[['Reason','Insight',"Total Counts"]]
    
    st.download_button('Download Insights', convert_df(cdata), file_name='insights.csv')


    gb = GridOptionsBuilder.from_dataframe(cdata)
    gb.configure_pagination(paginationAutoPageSize=True) #Add pagination
    gb.configure_side_bar() #Add a sidebar
    gb.configure_default_column(wrapText=True, autoHeight=True)
    gridOptions = gb.build()

    grid_response = AgGrid(
        cdata,
        gridOptions=gridOptions,
        data_return_mode='AS_INPUT',
        update_mode='MODEL_CHANGED', 
        fit_columns_on_grid_load=False,
        theme='blue', #Add theme color to the table
        enable_enterprise_modules=True,
        height=350, 
        width=50,
        reload_data=True,
    )



def page1_6(customer:str):
    st.header("Insightful Trends")

    data = st.session_state.data
    cdata = data.copy()
    cdata["date"] = cdata["createdAt"]
    cdata["createdAt"] = pd.to_datetime(data["createdAt"]).dt.date
    cdata = cdata[(cdata["createdAt"]>st.session_state.start_date)&(cdata["createdAt"]<st.session_state.end_date)]


