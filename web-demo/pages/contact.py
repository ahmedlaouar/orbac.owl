import streamlit as st
import streamlit_shadcn_ui as ui
from rdflib import Graph
import pandas as pd
from htbuilder import HtmlElement, div, ul, li, br, hr, a, p, img, styles, classes, fonts
from htbuilder.units import percent, px
from htbuilder.funcs import rgba, rgb

st.set_page_config(layout="centered", page_title="OrBAC ontology", page_icon="🧊", initial_sidebar_state="expanded", menu_items={'Get help':'https://orbac-owl.streamlit.app/contact','About':'## This is the official OrBAC ontology demo app!'})

def link(link, text, **style):
    return a(_href=link, _target="_blank", style=styles(textDecoration="none", **style))(text)

def link2(link, text, **style):
    return a(_href=link, _target="_blank", style=styles(**style))(text)
def layout(*args):

    style = """
    <style>
      # MainMenu {visibility: hidden;}
      footer {visibility: hidden;}
    </style>
    """

    style_div = styles(
        left=0,
        bottom=0,
        margin=px(0, 0, 0, 0),
        width=percent(100),
        text_align="center",
        height="100px",
        # opacity=0.9
    )

    style_hr = styles(
    )

    body = p()
    foot = div(style=style_div)(hr(style=style_hr), body)

    st.markdown(style, unsafe_allow_html=True)

    for arg in args:
        if isinstance(arg, str):
            body(arg)
        elif isinstance(arg, HtmlElement):
            body(arg)

    st.markdown(str(foot), unsafe_allow_html=True)

def footer():
    myargs = [
        " Copyright © 2025, Created by ",
        link("ABCD", "ABCD"),
        ", ",
        link("ABCD", "ABCD"),
        ", ",
        link("ABCD", "ABCD"),
        br(),
        "Funded by the XYZ: ",
        link2("XYZ", "XYZ"),
    ]
    layout(*myargs)

def main():
    st.markdown("""
    <style>
        .center-tabs {
            display: flex;
            justify-content: center;
        }
    </style>
    """, unsafe_allow_html=True)

    st.sidebar.title("OrBAC ontology")

    st.sidebar.page_link("app.py", label='Demo')
    st.sidebar.page_link("pages/overview.py", label='About the project')
    st.sidebar.page_link("pages/contact.py", label='Contact us')
    #st.sidebar.page_link("pages/contact.py", label='COntact us')

    # Streamlit app
    st.title("OrBAC ontology demo")

    footer()

if __name__ == "__main__":
    main()