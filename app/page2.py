import os
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import datetime
import altair as alt
from st_aggrid import GridOptionsBuilder, AgGrid, GridUpdateMode, DataReturnMode
from modules import convert_df

def page2(customer:str):
    text = """ # The feedback from the customers who like the app but have problems"""

    st.code(text,language="python")
    st.text("")
    st.text("")

    data = st.session_state.data
    cdata = data.copy()
    cdata["createdAt"] = pd.to_datetime(data["createdAt"]).dt.date
    
    cdata = cdata[(cdata["createdAt"]>st.session_state.start_date)&(cdata["createdAt"]<st.session_state.end_date)]

    neg_data = cdata[(cdata["reason_sentiment"]=="Negative")]
    neg_data = neg_data[(neg_data["rating"]>3)]
    
    cdata = neg_data.copy()

    neg_data = pd.DataFrame({'count' : neg_data.groupby( [ "id", "reason"] ).size()}).reset_index()
    neg_data = pd.DataFrame({'count' : neg_data.groupby( ["reason"] ).size()}).reset_index()
    neg_data = neg_data.sort_values('count',ascending=False)
    chart = alt.Chart(neg_data[:min(len(neg_data),st.session_state["top_k"])],height=500).mark_text(size=10).mark_bar().encode(
        alt.X("reason",sort="-y"),
        alt.Y("count"),
        alt.Color("reason"),
        alt.Tooltip(["reason", "count"]),
    ).interactive()

    st.altair_chart(chart,use_container_width=True)

    reasons = ["All"]
    reasons.extend(cdata["reason"].unique().tolist())

    selected_reason = st.multiselect(
        'Filter By Reason',
        reasons,
        default = st.session_state.reason_happy if st.session_state.get("reason_happy",None) else ["All"],
        key="reason_happy"
    )
    
    if "All" not in selected_reason:
        cdata = cdata[cdata["reason"].notna()]
        cdata = cdata[cdata["reason"].isin(selected_reason)]
    
    cdata = cdata[['original_untokenised_msg']]
    cdata = cdata.rename({'original_untokenised_msg':"Feedback"},axis=1)

    st.download_button('Download Feedback', convert_df(cdata), file_name='happy_feedback.csv')

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


def page3(customer:str):

    text = """ # The feedback from the customers who do not like the app"""

    st.code(text,language="python")
    st.text("")
    st.text("")

    data = st.session_state.data
    cdata = data.copy()
    cdata["createdAt"] = pd.to_datetime(data["createdAt"]).dt.date
    
    cdata = cdata[(cdata["createdAt"]>st.session_state.start_date)&(cdata["createdAt"]<st.session_state.end_date)]

    neg_data = cdata[(cdata["reason_sentiment"]=="Negative")]
    neg_data = neg_data[(neg_data["rating"]<3)]
    
    cdata = neg_data.copy()

    neg_data = pd.DataFrame({'count' : neg_data.groupby( [ "id", "reason"] ).size()}).reset_index()
    neg_data = pd.DataFrame({'count' : neg_data.groupby( ["reason"] ).size()}).reset_index()
    neg_data = neg_data.sort_values('count',ascending=False)
    
    chart = alt.Chart(neg_data[:min(len(neg_data),st.session_state["top_k"])],height=500).mark_text(size=10).mark_bar().encode(
        alt.X("reason",sort="-y"),
        alt.Y("count"),
        alt.Color("reason"),
        alt.Tooltip(["reason", "count"]),
    ).interactive()

    st.altair_chart(chart,use_container_width=True)


    reasons = ["All"]
    reasons.extend(cdata["reason"].unique().tolist())

    selected_reason = st.multiselect(
        'Filter By Reason',
        reasons,
        default = st.session_state.reason_unhappy if st.session_state.get("reason_unhappy",None) else ["All"],
        key="reason_unhappy"
    )
    
    if "All" not in selected_reason:
        cdata = cdata[cdata["reason"].notna()]
        cdata = cdata[cdata["reason"].isin(selected_reason)]
    
    cdata = cdata[['original_untokenised_msg']]
    cdata = cdata.rename({'original_untokenised_msg':"Feedback"},axis=1)
    
    st.download_button('Download Feedback', convert_df(cdata), file_name='unhappy_feedback.csv')

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

   