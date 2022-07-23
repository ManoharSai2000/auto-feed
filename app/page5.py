import os
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import datetime
import altair as alt
from st_aggrid import GridOptionsBuilder, AgGrid, GridUpdateMode, DataReturnMode
from modules import convert_df

def page5(customer:str):

    text = """ # Feature Requests, Difficulties and Improvements from Users"""

    st.code(text,language="python")
    st.text("")
    st.text("")

    data = st.session_state.data
    cdata = data.copy()
    cdata["createdAt"] = pd.to_datetime(data["createdAt"]).dt.date
    
    cdata = cdata[(cdata["createdAt"]>st.session_state.start_date)&(cdata["createdAt"]<st.session_state.end_date)]
    cdata = cdata[(cdata["reason"].str.contains("need",case=False))|(cdata["reason"].str.contains("want",case=False))]
    cdata = cdata[cdata["reason_sentiment"]!="Negative"]

    ccdata = cdata.copy()

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

    reasons = ["All"]
    reasons.extend(ccdata["reason"].unique().tolist())

    selected_reason = st.multiselect(
        'Filter By Reason',
        reasons,
        default = st.session_state.reason_need if st.session_state.get("reason_need",None) else ["All"],
        key="reason_need"
    )
    #st.session_state["reason_need"] = selected_reason

    if "All" not in selected_reason:
        ccdata = ccdata[ccdata["reason"].notna()]
        ccdata = ccdata[ccdata["reason"].isin(selected_reason)]
    
    ccdata = ccdata[['original_untokenised_msg']]
    ccdata = ccdata.rename({'original_untokenised_msg':"Feedback"},axis=1)

    st.download_button('Download Feedback', convert_df(ccdata), file_name='requests.csv')


    gb = GridOptionsBuilder.from_dataframe(ccdata)
    gb.configure_pagination(paginationAutoPageSize=True,paginationPageSize=20) #Add pagination
    gb.configure_side_bar() #Add a sidebar
    gb.configure_default_column(wrapText=True, autoHeight=True)
    gridOptions = gb.build()

    grid_response = AgGrid(
        ccdata,
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

    