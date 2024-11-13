import streamlit as st
import streamlit_shadcn_ui as ui
from rdflib import Graph
import pandas as pd
from acceptance import *
from explanation import *

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

def display_app_heading():
    st.title("OrBAC ontology demo")
    #st.header("Test some functions of the OrBAC ontology")
    with st.expander("About the project",expanded=False):
        st.header("The Organisation Based Access Control (OrBAC) ontology:")
        st.write("This website serves as a demo of the OrBAC ontology and the methods around it. It mainly allows applying conflict resolution methods and explanation mechanisms on some example policies.")

# Streamlit app
display_app_heading()

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
    
    with st.expander("Visualize the policy", expanded=False):
        #st.caption("A visualization of the policy:")
        policy_tabs = st.tabs(["Abstract rules", "Connection relations", "Uncertainty"])

        with policy_tabs[0]:
            #st.caption("")
            abstract_rules = get_abstract_rules(graph)
            abstract_rules_data = pd.DataFrame(abstract_rules, columns=["Privilege name", "Privilege type", "Organisation", "Role", "Activity", "view", "Context"])
                
            abstract_rules_data = abstract_rules_data.map(strip_prefix)
            st.dataframe(abstract_rules_data, hide_index=True, use_container_width=True)

        with policy_tabs[1]:
            #st.caption("")
            connection_rules = get_connection_rules(graph)
            connection_rules_data = pd.DataFrame(connection_rules, columns=["Rule name", "Rule type", "Organisation", "Abstract", "Concrete"])
                
            connection_rules_data = connection_rules_data.map(strip_prefix)
            st.dataframe(connection_rules_data, hide_index=True, use_container_width=True)
        
    # Primary tabs for grouping
    left_co1, cent_co1, right_co1 = st.columns([0.12,0.76,0.12])
    
    with cent_co1:
        main_tabs = ui.tabs(["Check privileges", "Check consistency", "Compute supports", "Acceptance"], default_value='Check privileges')#, use_container_width=True

    with st.expander("Privilege inference and conflict resolution methods", expanded=True):
        # Create 3 columns
        col1, col2, col3 = st.columns(3)

        # Place the text inputs in the respective columns
        with col1:
            subject = st.text_input("Subject")
        with col2:
            action = st.text_input("Action")
        with col3:
            obj = st.text_input("Object")
        # 1. Checking Privileges Tab
        if main_tabs == "Check privileges":
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

        # 2. Checking Consistency & Conflicts Tab
        elif main_tabs == "Check consistency":
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

        # 3. Compute Supports Tab
        elif main_tabs == "Compute supports":
            #st.caption("Compute supports")
            
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

        # 4. Acceptance Tab
        elif main_tabs == "Acceptance":
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

def main():
    st.markdown("""
    <style>
        .center-tabs {
            display: flex;
            justify-content: center;
        }
    </style>
    """, unsafe_allow_html=True)

    sidebar_option = st.sidebar.selectbox('Choose an option:',('Use an example policy', 'Load a policy', 'Build your policy'))

    if sidebar_option == 'Use an example policy':
        display_use_part()
    elif sidebar_option == "Load a policy" or sidebar_option == "Build your policy":
        display_coming()

if __name__ == "__main__":
    main()