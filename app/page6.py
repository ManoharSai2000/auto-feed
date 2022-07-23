import os
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import datetime
import numpy as np
import altair as alt
import textwrap
from st_aggrid import GridOptionsBuilder, AgGrid, GridUpdateMode, DataReturnMode
from modules import convert_df

def page6(customer:str):

    text = """ # Explore the Feedback Using Various Filters To Get More Insights"""

    st.code(text,language="python")
    st.text("")
    st.text("")

    col1,col2,col3 = st.columns(3)

    data = st.session_state.data
    cdata = data.copy()
    cdata["createdAt"] = pd.to_datetime(data["createdAt"]).dt.date
    
    cdata = cdata[(cdata["createdAt"]>st.session_state.start_date)&(cdata["createdAt"]<st.session_state.end_date)]
    
    sources = ["All","Playstore","Appstore"]
    ratings = ["All",1,2,3,4,5]
    sentiments = ["All","Negative","Positive","Neutral"]
    reasons = ["All"]
    reasons.extend(cdata["reason"].unique().tolist())
    entities = ["All"]
    entities.extend(cdata.explode('entity')["entity"].unique().tolist())

    with col1:
        selected_source = st.selectbox(
            'Filter By Source',
            sources,
            index = sources.index(st.session_state.source) if st.session_state.get("source",None) else 0,
            key="source"
        )
    
    if "All" not in selected_source:
        cdata = cdata[cdata["source"]==selected_source]
    
    with col2:
            selected_rating = st.multiselect(
            'Filter By Rating',
            ratings,
            default = st.session_state.rating if st.session_state.get("rating",None) else ["All"],
            key="rating"
        )
    if "All" not in selected_rating:
        cdata = cdata[cdata["rating"].isin(selected_rating)]
    
    with col3:
        selected_sentiment = st.multiselect(
            'Filter By Sentiment',
            sentiments,
            default = st.session_state.sentiment if st.session_state.get("sentiment",None) else ["All"],
            key="sentiment"
        )

    if "All" not in selected_sentiment:
        cdata = cdata[cdata["sentiment"].notna()]
        cdata = cdata[cdata["sentiment"].isin(selected_sentiment)]

    
    with col1:
        selected_reason = st.multiselect(
            'Filter By Reason',
            reasons,
            default = st.session_state.reason if st.session_state.get("reason",None) else ["All"],
            key="reason"
        )

    if "All" not in selected_reason:
        cdata = cdata[cdata["reason"].notna()]
        cdata = cdata[cdata["reason"].isin(selected_reason)]
    
    with col2:
        selected_entity = st.multiselect(
            'Filter By Entity',
            entities,
            default = st.session_state.entity if st.session_state.get("entity",None) else ["All"],
            key="entity"
        )

    if "All" not in selected_entity:
        cdata = cdata[cdata["entity"].notna()]
        cdata = cdata[cdata['entity'].apply(lambda x: any([entity in x for entity in selected_entity]))]
    
    if not len(data):
        st.header("No Feedback Found")
        return

    
    rdata = cdata.copy()

    cdata = cdata[['original_untokenised_msg']]
    cdata = cdata.rename({'original_untokenised_msg':"Feedback"},axis=1)
    cdata["Feedback"] = cdata["Feedback"].apply(lambda x: textwrap.fill(x,80))  

    ddata = pd.DataFrame({'count' : rdata.groupby( [ "id", "reason"] ).size()}).reset_index()
    ddata = pd.DataFrame({'count' : ddata.groupby( ["reason"] ).size()}).reset_index()
    ddata = ddata.sort_values('count',ascending=False)

    chart = alt.Chart(ddata[:min(len(ddata),st.session_state["top_k"])],height=500).mark_text(size=10).mark_bar().encode(
        alt.X("reason",sort="-y"),
        alt.Y("count"),
        alt.Color("reason"),
        alt.Tooltip(["reason", "count"]),
    ).interactive()

    st.altair_chart(chart,use_container_width=True)
    
    edata = rdata.explode("entity")
    edata["entity"] = edata["entity"].str.title()
    edata = pd.DataFrame({'count' : edata.groupby( [ "id", "entity"] ).size()}).reset_index()
    edata = pd.DataFrame({'count' : edata.groupby( ["entity"] ).size()}).reset_index()
    edata = edata.sort_values('count',ascending=False)

    chart = alt.Chart(edata[:min(len(edata),st.session_state["top_k"])],height=500).mark_text(size=10).mark_bar().encode(
        alt.X("entity",sort="-y"),
        alt.Y("count"),
        alt.Color("entity"),
        alt.Tooltip(["entity", "count"]),
    ).interactive()

    st.altair_chart(chart,use_container_width=True)

    st.download_button('Download Feedback', convert_df(cdata), file_name='filtered_feedback.csv')


    gb = GridOptionsBuilder.from_dataframe(cdata)
    gb.configure_pagination(paginationAutoPageSize=True,paginationPageSize=20) #Add pagination
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
        height=1000, 
        width='100%',
        reload_data=True
    )

    
    