import streamlit as st
import streamlit_shadcn_ui as ui
from rdflib import Graph
import pandas as pd
from acceptance import *
from explanation import *
from AccessRight import AccessRight
from htbuilder import HtmlElement, div, ul, li, br, hr, a, p, img, styles, classes, fonts
from htbuilder.units import percent, px
from htbuilder.funcs import rgba, rgb
from os import listdir
from os.path import isfile, join
#st.set_page_config(layout='centered')
st.set_page_config(layout="centered", page_title="OrBAC ontology", page_icon="🧊", initial_sidebar_state="expanded", menu_items={'Get help':'https://orbac-owl.streamlit.app/contact','About':'## This is the official OrBAC ontology demo app!'})

# Load the ontology graph
def load_policy(policy_name):
    graph = Graph()
    # Paths to the base ontology and the instance file
    base_ontology_path = "ontology/orbac.owl"
    
    # Parse the base ontology into the graph
    graph.parse(base_ontology_path, format="xml")

    instance_file_path = "ontology/examples/"+policy_name
    # Parse the instance file into the same graph
    graph.parse(instance_file_path, format="xml")

    for s, p, o in graph.triples((None, RDF.type, OWL.Ontology)):
        base_uri = s
        #break  # Assuming there is only one owl:Ontology

    if base_uri:
        example_uri = base_uri
    else:
        print("Base URI not found in the graph.")

    if example_uri[-1] != "#":
        example_uri += "#"

    return graph, example_uri

def generate_explanation(graph, example_uri, subject, action, obj, lemmatizer):
    accessesPermission = computeAccess(graph, example_uri, "Permission", subject, action, obj)
    accessesProhibition = computeAccess(graph, example_uri, "Prohibition", subject, action, obj)

    explanations  = Explanations(graph, example_uri, accessesPermission, accessesProhibition, lemmatizer)
    
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

def get_concrete_concepts(graph):
    query = """PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            PREFIX : <https://raw.githubusercontent.com/ahmedlaouar/orbac.owl/refs/heads/main/ontology/orbac.owl#> # Adjust the base URI as necessary

            SELECT ?s ?alpha ?o {{
                ?relation rdf:type :Define .
                ?relation :definesSubject ?s .
                ?relation :definesAction ?alpha .
                ?relation :definesObject ?o .
            }}"""
    
    results = graph.query(query)

    return results

def display_use_part():
    
    with st.container():
        # Primary tabs for grouping
        _, cent_co1, _ = st.columns([0.25,0.51,0.25])
        with cent_co1:
            main_tabs = ui.tabs(["Home", "Policy Viewer", "More on Explanations"], default_value='Home')
            
        _, cent_co1, _ = st.columns([0.15,0.7,0.15])
        with cent_co1:
            option = st.selectbox('Choose an option:',('Use an example policy', 'Load a policy', 'Build your policy'))

    if option == 'Use an example policy':
        examples_path = "ontology/examples"
        onlyfiles = [f for f in sorted(listdir(examples_path)) if isfile(join(examples_path, f))]
        _, cent_co1, _ = st.columns([0.1,0.8,0.1])
        with cent_co1:
            example_option = st.selectbox("Choose an example policy:", onlyfiles)
            for e in onlyfiles:
                if example_option == e:
                    st.caption("Loading "+e+" policy...")
                    policy_name = e #"secondee-example.owl"
                    graph, example_uri = load_policy(policy_name)
                    st.caption(e + " policy loaded successfully!")

        with st.container(border=True):
            st.caption("Conflict resolution and explanation of OrBAC Access Control Decisions")
            
            _, main_col, _ = st.columns([0.1,2,0.1])
            with main_col:
                st.caption("Introduction")
                
                # 1. Home tab
                # TODO : in preference create a Policy class, it should contain a graph, uri and list of all combinations of (subject, action, object), it should have methods to return rules and relations of the following tab
                # the goal is also to avoid unnecessary IO operations from system files since app is hosted in github
                if main_tabs == "Home":
                    # Create 3 columns
                    _, col2, _ = st.columns([0.05,0.9,0.05])
                    with col2:
                        define_rules = get_concrete_concepts(graph)
                        define_rules_data = pd.DataFrame(define_rules, columns=["Subject", "Action", "Object"])
                        define_rules_data = define_rules_data.map(strip_prefix)
                        combinations = define_rules_data[["Subject", "Action", "Object"]].drop_duplicates()
                        combinations['Combination'] = combinations.apply(lambda row: f"Is-permitted({row['Subject']}, {row['Action']}, {row['Object']})?", axis=1)
                        selected_combination_str = st.selectbox("Select a combination of subject, action and object", combinations['Combination'].values)
                        # Extract the selected combination (Subject, Action, Object)
                        selected_combination = combinations[combinations['Combination'] == selected_combination_str].iloc[0]
                        subject = selected_combination['Subject']
                        action = selected_combination['Action']
                        obj = selected_combination['Object']
                
                    new_access = AccessRight(subject, action, obj, graph, example_uri)

                    with st.expander("Permission and Prohibition supports", expanded=False):
                        # Permission supports
                        st.caption("Permission supports")
                        if not (subject and obj and action):
                            st.write("Please enter a valid subject, action and object!")
                        elif len(new_access.permission_supports) != 0:
                            st.write(f"{subject} is permitted to perform {action} on {obj}")
                        else:
                            st.write(f"{subject} is not permitted to perform {action} on {obj}")
                        supports = new_access.permission_supports
                        supports_data = pd.DataFrame(supports,).map(lambda x: x.get_predicate())
                        st.dataframe(supports_data,hide_index=True, use_container_width=True)
                        # Prohibition supports
                        st.caption("Prohibition supports")
                        if not (subject and obj and action):
                            st.write("Please enter a valid subject, action and object!")
                        elif len(new_access.prohibition_supports) != 0:
                            st.write(f"{subject} is prohibited from performing {action} on {obj}")
                        else:
                            st.write(f"{subject} is not prohibited from performing {action} on {obj}")
                        supports = new_access.prohibition_supports                    
                        supports_data = pd.DataFrame(supports,).map(lambda x: x.get_predicate())
                        st.dataframe(supports_data, hide_index=True, use_container_width=True)

                    # Acceptance decision:
                    with st.expander("Conflict resolution using the acceptance method", expanded=False):
                        st.caption("Description of the used method")
                        
                        st.caption("Used supports:")
                        supports_text = ""
                        if len(new_access.permission_supports) != 0 and len(new_access.prohibition_supports) != 0:
                            supports_text += f"There is a conflict in the access of ``{subject}`` to ``{action}`` the object ``{obj}``, namely, it has "
                        else:
                            supports_text += f"The access of ``{subject}`` to ``{action}`` the object ``{obj}`` has " 
                        if len(new_access.permission_supports) == 1:
                            supports_text += "``1`` permission support " 
                        else:
                            supports_text += f"``{len(new_access.permission_supports)}`` permission supports "
                        if len(new_access.prohibition_supports) == 1:
                            supports_text += "and ``1`` prohibition support."
                        else:
                            supports_text += f"and ``{len(new_access.prohibition_supports)}`` prohibition supports."
                        st.write(supports_text)
                        st.caption("The outcome decision:")
                        if new_access.outcome:
                            st.write(f"The permission for ``{subject}`` to perform ``{action}`` on ``{obj}`` is accepted")
                        else:
                            st.write(f"The permission for ``{subject}`` to perform ``{action}`` on ``{obj}`` is rejected")

                    #with st.expander("Logical explanations of the decision", expanded=False):
                    #    # TODO here present all logical explanations as computed by AccessRight.get_support_logic_explanations()
                    #    """"""

                    with st.expander("Natural Language Explanations", expanded=False):
                        # TODO replace the template-based approach with the new approach (ongoing):
                        """"""
                        st.caption("Template-based textual explanations:")
                        if st.button("Explain the desicion", use_container_width=True):
                            nltk.download('wordnet')
                            lemmatizer = WordNetLemmatizer()
                            explanations = generate_explanation(graph, example_uri, subject, action, obj, lemmatizer)
                            for explanation in explanations:                                
                                st.markdown(explanation)#.__str__()
                                #st.caption("Logic-based explanations:")
                                #st.write(explanation.getContrastiveExplanation())
                                #st.write(explanation.getOutcomeConflict())

                # 2. Visualise the full policy 
                elif main_tabs == "Policy Viewer":
                    with st.container(border=True):
                        _, c_col, _ = st.columns([0.05,1,0.05], gap="small")
                        with c_col:
                            with st.container():
                                policy_tabs = ui.tabs(["Abstract rules", "Connection relations", "Uncertainty", "Access Conflicts"], default_value='Abstract rules')

                        if policy_tabs == "Abstract rules":
                            abstract_rules = get_abstract_rules(graph)
                            abstract_rules_data = pd.DataFrame(abstract_rules, columns=["Privilege name", "Privilege type", "Organisation", "Role", "Activity", "view", "Context"])
                                
                            abstract_rules_data = abstract_rules_data.map(strip_prefix)
                            st.dataframe(abstract_rules_data, hide_index=True, use_container_width=True)

                        elif policy_tabs == "Connection relations":
                            connection_rules = get_connection_rules(graph)
                            connection_rules_data = pd.DataFrame(connection_rules, columns=["Rule name", "Rule type", "Organisation", "Abstract", "Concrete"])
                                
                            connection_rules_data = connection_rules_data.map(strip_prefix)
                            st.dataframe(connection_rules_data, hide_index=True, use_container_width=True)
                            st.caption("Define relations:")
                            define_rules = get_define_rules(graph)
                            define_rules_data = pd.DataFrame(define_rules, columns=["Rule name", "Organisation", "Subject", "Action", "Object", "Context"])
                            define_rules_data = define_rules_data.map(strip_prefix)
                            st.dataframe(define_rules_data, hide_index=True, use_container_width=True)
                    
                        # Checking Consistency & Conflicts Tab
                        elif policy_tabs == "Access Conflicts":
                            st.caption("Checking consistency & computing the conflicts")

                            if st.button("Check consistency", use_container_width=True):
                                consistency = check_consistency(graph)
                                if consistency:
                                    st.write("The instance is consistent")
                                else:
                                    st.write("The instance is inconsistent")
                            # Only show Compute Conflicts if inconsistent
                            if st.button("Compute conflicts", use_container_width=True):
                                # Compute and display conflicts
                                conflicts = compute_conflicts(graph)
                                conflict_data = pd.DataFrame(conflicts, columns=["Employ relation1", "Use relation1", "Define relation1", "Employ relation2", "Use relation2", "Define relation2"])
                                conflict_data = conflict_data.map(strip_prefix)
                                st.dataframe(conflict_data, hide_index=True, use_container_width=True)

                    st.caption("Quick Links")

    elif option == "Load a policy" or option == "Build your policy":
        with st.container(border=True):
            display_coming()
                

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
        link("https://ahmedlaouar.me", "Ahmed Laouar"),
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
        .css-1cxcynr { /* This class corresponds to the selectbox container */
            width: 100px; /* Adjust this value to the desired width */
            margin-left: auto;
            margin-right: auto;
        }
    </style>
    """, unsafe_allow_html=True)

    st.title("OrBAC ontology demo")

    st.sidebar.title("OrBAC ontology")

    st.sidebar.page_link("app.py", label='Demo')
    st.sidebar.page_link("pages/overview.py", label='About the project')
    st.sidebar.page_link("pages/contact.py", label='Contact us')

    display_use_part()

    footer()

if __name__ == "__main__":
    main()