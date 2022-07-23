import os

from traitlets import default
import streamlit as st
from streamlit_option_menu import option_menu
import pandas as pd
import datetime

from page1 import page1_1,page1_2,page1_3,page1_4,page1_5
from page2 import page2,page3
from page4 import page4
from page5 import page5
from page6 import page6


st.set_page_config(layout='wide',
                    page_title="auto-feed",
                    page_icon="💁🏻")

st.markdown("<h1 style='text-align: center; color: white;'> Auto Feed </h1>", unsafe_allow_html=True)

st.markdown(
            f"""
                    <style> .appview-container .main .block-container{{ padding-top: 1rem; }} </style>
            """,
            unsafe_allow_html=True,
        )

all_tabs = ["Quick Insights","Happy Customer's Issues","Unhappy Customer`s Issues","User Requests","Explore"]

def ack_customer():

    customers = os.listdir("app/data/")
    customers = [customer for customer in customers if customer[0]!='.']
    
    add_selectbox = st.sidebar.selectbox(
        'Select The Customer',
        customers,
        index = customers.index(st.session_state.customer) if st.session_state.get("customer",None) else 0,
        key="customer",
    )

def ack_tab():
    tab = option_menu(
        menu_title="",
        options = all_tabs,
        orientation="horizontal",
        default_index = all_tabs.index(st.session_state.tab) if st.session_state.get("tab",None) else 0,
        key="tab1",
        icons = [":eyes:",":disappointed:",":tired_face:",":innocent:",":mag:"],

        # styles= {
        #     "icon": {"color": "orange", "font-size": "20px"}, 
        # }
    )
    st.session_state["tab"] = tab

def set_date_range():

    today = datetime.date.today()
    
    if st.session_state.get("start_date",None):
        default = st.session_state.get("start_date")
    else:
        default = datetime.datetime(2022, 3, 1)

    
    start_date = st.sidebar.date_input('Start date',default,key="start_date")

    if st.session_state.get("end_date",None):
        default = st.session_state.get("end_date")
    else:
        default = datetime.datetime(2022, 6, 30)

    end_date = st.sidebar.date_input('End date', default,key="end_date",)

def top_k():

    k = st.sidebar.number_input(
        "View Top-k",
        min_value = 1,
        max_value=50,
        value= st.session_state.top_k if st.session_state.get(top_k,None) else 15,
        key = "topk"
    )
    st.session_state["top_k"] = k

@st.cache
def read_data(customer:str):
    data = pd.read_pickle(f"app/data/{customer}/df.pkl")
    data["reason"] = data["reason"].str.title()
    return data


ack_tab()
ack_customer()
set_date_range()
top_k()
st.session_state.data = read_data(st.session_state.customer)

if st.session_state.tab == all_tabs[0]:
    page1_5(st.session_state.customer)
    page1_1(st.session_state.customer)
    page1_3(st.session_state.customer)
    page1_4(st.session_state.customer)
    page1_2(st.session_state.customer)
    
if st.session_state.tab == all_tabs[1]:
    page2(st.session_state.customer)

if st.session_state.tab == all_tabs[2]:
    page3(st.session_state.customer)

# if st.session_state.tab == all_tabs[2]:
#     page4(st.session_state.customer)

if st.session_state.tab == all_tabs[3]:
    page5(st.session_state.customer)

if st.session_state.tab == all_tabs[4]:
    page6(st.session_state.customer)
