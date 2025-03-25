import streamlit as st
import streamlit_shadcn_ui as ui
from rdflib import Graph
import pandas as pd
from acceptance import *
from explanation import *
from htbuilder import HtmlElement, div, ul, li, br, hr, a, p, img, styles, classes, fonts
from htbuilder.units import percent, px
from htbuilder.funcs import rgba, rgb

st.set_page_config(layout="wide", page_title="OrBAC ontology", page_icon="🧊", initial_sidebar_state="expanded", menu_items={'Get help':'https://orbac-owl.streamlit.app/contact','About':'## This is the official OrBAC ontology demo app!'})

def display_app_heading():
    st.title("OrBAC ontology demo")
    #st.header("Test some functions of the OrBAC ontology")
    
    st.image("web-demo/content/static/images/https___raw.githubusercontent.com_ahmedlaouar_orbac.owl_refs_heads_main_ontology_orbac.owl.svg",use_container_width=True,caption="")
    st.markdown("<p style='text-align: center;color:grey;'><small>The OrBAC ontology graph: Created with <a href='http://vowl.visualdataweb.org'>WebVOWL</a> (version 1.1.7)</small></p>", unsafe_allow_html=True)

    with st.expander("The OrBAC ontology",expanded=False):
        #st.header("The Organisation Based Access Control (OrBAC) ontology:")
        #st.write("This website serves as a demo of the OrBAC ontology and the methods around it. It mainly allows applying conflict resolution methods and explanation mechanisms on some example policies.")

        # Path to markdown file
        markdown_file = "web-demo/content/orbac-ontology.md"
        # Read and display the markdown content
        with open(markdown_file, "r") as file:
            orbac_summary = file.read()
        # Display markdown content at a specific location in your Streamlit app
        st.markdown(orbac_summary, unsafe_allow_html=True)


    with st.expander("Overview of the OrBAC Model",expanded=False):
        #st.header("The Organisation Based Access Control (OrBAC) ontology:")
        #st.write("This website serves as a demo of the OrBAC ontology and the methods around it. It mainly allows applying conflict resolution methods and explanation mechanisms on some example policies.")

        # Path to markdown file
        markdown_file = "web-demo/content/orbac.md"
        # Read and display the markdown content
        with open(markdown_file, "r") as file:
            orbac_summary = file.read()
        # Display markdown content at a specific location in your Streamlit app
        st.markdown(orbac_summary, unsafe_allow_html=True)

    
    
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
        " Copyright © 2024, Created by ",
        link("http://ahmedlaouar.me", "Ahmed Laouar"),
        ", ",
        link("https://www.tokyraboanary.org/", "Toky Raboanary"),
        ", ",
        link("https://scholar.google.fr/citations?user=-3kO5x0AAAAJ&hl=fr", "Salem Benferhat"),
        br(),
        "Funded by the STARWARS-project: ",
        link2("https://sites.google.com/view/horizoneurope2020-starwars/", "Horizon Europe 2020"),
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
    display_app_heading()

    footer()

if __name__ == "__main__":
    main()