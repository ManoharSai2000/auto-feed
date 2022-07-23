import os
from unicodedata import name
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import datetime
import altair as alt
import textwrap
from st_aggrid import GridOptionsBuilder, AgGrid, GridUpdateMode, DataReturnMode


def page4(customer:str):
    
    st.subheader("Feature Requests, Improvements and Suggestions and ")

    comp_data = pd.read_pickle(f"./data/{customer}/competitor.pkl")
    comp_data = comp_data[comp_data["competitor_mention"]==True]
    cdata = comp_data[['original_untokenised_msg']]
    cdata = cdata.rename({'original_untokenised_msg':"Feedback"},axis=1)
    cdata["Feedback"] = cdata["Feedback"].apply(lambda x: textwrap.fill(x,80))  
    
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
        width='100%',
        reload_data=True
    )
