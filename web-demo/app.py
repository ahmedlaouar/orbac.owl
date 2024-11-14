import streamlit as st
import streamlit_shadcn_ui as ui
from rdflib import Graph
import pandas as pd
from acceptance import *
from explanation import *
from htbuilder import HtmlElement, div, ul, li, br, hr, a, p, img, styles, classes, fonts
from htbuilder.units import percent, px
from htbuilder.funcs import rgba, rgb

st.set_page_config(layout="centered", page_title="OrBAC ontology", page_icon="🧊", initial_sidebar_state="expanded", menu_items={'Get help':'https://orbac-owl.streamlit.app/contact','About':'## This is the official OrBAC ontology demo app!'})

# Load the ontology graph
def load_starwars_policy():
    graph = Graph()
    graph.parse("ontology/orbac-STARWARS.owl", format="xml")
    return graph

def generate_explanation(graph, subject, action, obj, lemmatizer):
    accessesPermission = computeAccess(graph, "Permission", subject, action, obj)
    accessesProhibition = computeAccess(graph, "Prohibition", subject, action, obj)

    explanations  = Explanations(graph, accessesPermission, accessesProhibition, lemmatizer)

    if len(accessesProhibition) == len(accessesPermission) == 0:
        explanations = []
        explanations.append(f"There is no permission or prohibition inferred for {subject} to perform {action} on {obj}")
        return explanations
    elif len(accessesProhibition) == 0:
        return explanations.getExplanationsPermissions()
    elif len(accessesPermission) == 0:
        return explanations.getExplanationsProhibitions()
    else:
        return explanations.getExplanationsConflicts()

def display_coming():
    st.write("Coming soon")

def display_use_part():
    example_option = st.selectbox("Choose an example policy:", ["Starwars", "Policy 2"])
    if example_option == "Starwars":
        st.write("Loading STARWARS policy...")
        graph = load_starwars_policy()
        st.write("STARWARS policy loaded successfully!")
    elif example_option == "Policy 2":
        st.write("Loading Policy 2...")
        graph = load_starwars_policy()
        st.write("Policy 2 loaded successfully!")
        
    # Primary tabs for grouping
    left_co1, cent_co1, right_co1 = st.columns([0.02,0.95,0.01])
    
    with cent_co1:
        main_tabs = ui.tabs(["Visualize policy", "Privileges & supports", "Consistency & conflicts", "Acceptance & explainability"], default_value='Visualize policy')#, use_container_width=True

    with st.expander("Privilege inference and text-based explanation methods", expanded=True):
        # Create 3 columns
        col1, col2, col3 = st.columns(3)

        # Place the text inputs in the respective columns
        with col1:
            subject = st.text_input("Subject")
        with col2:
            action = st.text_input("Action")
        with col3:
            obj = st.text_input("Object")
        # 1. Visualize the policy
        if main_tabs == "Visualize policy":
            #st.caption("A visualization of the policy:")
            policy_tabs = ui.tabs(["Abstract rules", "Connection relations", "Uncertainty"], default_value='Abstract rules')

            if policy_tabs == "Abstract rules":
                #st.caption("")
                abstract_rules = get_abstract_rules(graph)
                abstract_rules_data = pd.DataFrame(abstract_rules, columns=["Privilege name", "Privilege type", "Organisation", "Role", "Activity", "view", "Context"])
                    
                abstract_rules_data = abstract_rules_data.map(strip_prefix)
                st.dataframe(abstract_rules_data, hide_index=True, use_container_width=True)

            if policy_tabs == "Connection relations":
                #st.caption("")
                connection_rules = get_connection_rules(graph)
                connection_rules_data = pd.DataFrame(connection_rules, columns=["Rule name", "Rule type", "Organisation", "Abstract", "Concrete"])
                    
                connection_rules_data = connection_rules_data.map(strip_prefix)
                st.dataframe(connection_rules_data, hide_index=True, use_container_width=True)
        
        # 2. Checking Privileges Tab        
        if main_tabs == "Privileges & supports":
            st.caption("Checking the inference of a privilege")

            # Nested tabs for permission and prohibition
            #privilege_tabs = st.tabs(["Check Permission", "Check Prohibition"])
            
            col1, col2 = st.columns(2)
            with col1:
                perm_button = st.button("Check Permission", use_container_width=True)
            with col2:
                proh_button = st.button("Check Prohibition", use_container_width=True)
            
            if perm_button:
                if not (subject and obj and action):
                    st.write("Please enter a valid subject, action and object!")
                elif ispermitted(graph, subject, action, obj):
                    st.write(f"{subject} is permitted to perform {action} on {obj}")
                else:
                    st.write(f"{subject} is not permitted to perform {action} on {obj}")
            if proh_button:
                if not (subject and obj and action):
                    st.write("Please enter a valid subject, action and object!")
                elif isprohibited(graph, subject, action, obj):
                    st.write(f"{subject} is prohibited from performing {action} on {obj}")
                else:
                    st.write(f"{subject} is not prohibited from performing {action} on {obj}")

            # Nested tabs for permission and prohibition supports
            support_tabs = st.tabs(["Permission supports", "Prohibition supports"])
            
            with support_tabs[0]:  # Permission Supports
                if st.button("Compute permission supports", use_container_width=True):
                    supports = compute_raw_supports(graph, subject, action, obj, 0)
                    supports_data = pd.DataFrame(supports, columns=["Access type", "Employ relation", "Consider relation", "Use relation", "Define relation"])
                    supports_data = supports_data.map(strip_prefix)
                    st.dataframe(supports_data,hide_index=True, use_container_width=True)

            with support_tabs[1]:  # Prohibition Supports
                if st.button("Compute prohibition supports", use_container_width=True):
                    supports = compute_raw_supports(graph, subject, action, obj, 1)
                    supports_data = pd.DataFrame(supports, columns=["Access type", "Employ relation", "Consider relation", "Use relation", "Define relation"])
                    supports_data = supports_data.map(strip_prefix)
                    st.dataframe(supports_data, hide_index=True, use_container_width=True)

        # 3. Checking Consistency & Conflicts Tab
        elif main_tabs == "Consistency & conflicts":
            st.caption("Checking consistency & computing the conflicts")

            if st.button("Check consistency", use_container_width=True):
                consistency = check_consistency(graph)
                if consistency:
                    st.write("The instance is consistent")
                else:
                    st.write("The instance is inconsistent")
            # Only show Compute Conflicts if inconsistent
            if st.button("Compute conflicts", use_container_width=True):
                compute_conflicts(graph)
                # Placeholder output for conflicts
                conflicts = compute_conflicts(graph)
                conflict_data = pd.DataFrame(conflicts, columns=["Employ relation1", "Use relation1", "Define relation1", "Employ relation2", "Use relation2", "Define relation2"])
                
                conflict_data = conflict_data.map(strip_prefix)
                st.dataframe(conflict_data, hide_index=True, use_container_width=True)

        # 4. Acceptance Tab
        elif main_tabs == "Acceptance & explainability":
            #st.caption("Checking acceptance")
            if st.button("Check acceptance", use_container_width=True):
                if not (subject and obj and action):
                    st.write("Please enter a valid subject, action and object!")
                else:
                    if check_acceptance(graph, subject, action, obj):
                        st.write(f"The permission for {subject} to perform {action} on {obj} is granted")
                    else:
                        st.write(f"The permission for {subject} to perform {action} on {obj} is denied")
            st.header('Explain the desicion')
            st.caption("Generate text-based explanations.")
            if st.button("Explain"):
                nltk.download('wordnet')
                lemmatizer = WordNetLemmatizer()
                explanations = generate_explanation(graph, subject, action, obj, lemmatizer)
                for explanation in explanations:
                    st.write(explanation)#.__str__()

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
        link("https://github.com/ahmedlaouar", "Ahmed Laouar"),
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

    st.title("OrBAC ontology demo")

    st.sidebar.title("OrBAC ontology")

    st.sidebar.page_link("app.py", label='Demo')
    st.sidebar.page_link("pages/overview.py", label='About the project')
    st.sidebar.page_link("pages/contact.py", label='Contact us')
    #st.sidebar.page_link("pages/contact.py", label='COntact us')

    # Streamlit app
    #display_app_heading()

    option = st.selectbox('Choose an option:',('Use an example policy', 'Load a policy', 'Build your policy'))

    if option == 'Use an example policy':
        display_use_part()
    elif option == "Load a policy" or option == "Build your policy":
        display_coming()


    footer()

if __name__ == "__main__":
    main()