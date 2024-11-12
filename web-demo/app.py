import streamlit as st
from rdflib import Graph
import pandas as pd

st.set_page_config(layout="centered", page_title="OrBAC ontology", page_icon="🧊", initial_sidebar_state="expanded", menu_items={'Get help':'https://orbac-owl.streamlit.app/contact','About':'## This is the official OrBAC ontology demo app!'})

def strip_prefix(uri):
    return uri.split('#')[-1]

def ispermitted(graph, subject, action, obj):
    query_path = "queries.sparql/is-permitted.sparql"
    with open(query_path, 'r') as file:
        
        query_template = file.read()
        
        query = query_template.format(subject=subject, action=action, object=obj)
        
        results = graph.query(query)
    try:
        first_result = next(iter(results))
        if first_result:
            return True
        else: 
            return False
    except StopIteration:
        print("No query results found.")
        return False

def isprohibited(graph, subject, action, obj):
    query_path = "queries.sparql/is-prohibited.sparql"
    with open(query_path, 'r') as file:
        
        query_template = file.read()
        
        query = query_template.format(subject=subject, action=action, object=obj)
        
        results = graph.query(query)
    try:
        first_result = next(iter(results))
        if first_result:
            return True
        else: 
            return False
    except StopIteration:
        print("No query results found.")
        return False

def compute_supports(graph, subject, action, obj, accessType=0):
    # by default, support of a permission is computed when accessType=0
    # for a support of a prohibition set accessType = 1
    if accessType == 0:
        supports_query_path = "queries.sparql/permission_supports.sparql"
    elif accessType == 1:
        supports_query_path = "queries.sparql/prohibition_supports.sparql"
    else:
        print("Please enter a valid accessType.")

    with open(supports_query_path, 'r') as file:
        
        query_template = file.read()
        
        query = query_template.format(subject=subject, action=action, object=obj)
        
        results = graph.query(query)
    
    return results

def check_consistency(graph):
    consistency_checking_query_path = "queries.sparql/inconsistency_checking.sparql"
    with open(consistency_checking_query_path, 'r') as file:
        query = file.read()

    results = graph.query(query)
    try:
        first_result = next(iter(results))
        if first_result:
            return False
        else: 
            return True
    except StopIteration:
        print("No query results found.")
        return True

def compute_conflicts(graph):
    conflicts_query_path = 'queries.sparql/compute_conflicts.sparql'

    with open(conflicts_query_path, 'r') as file:
        query = file.read()

    results = graph.query(query)

    return results

def is_strictly_preferred(graph, member1, member2):
    dominance_query_path = "queries.sparql/dominance_query.sparql"
    with open(dominance_query_path, 'r') as file:
        query_template = file.read()

    query = query_template.format(member1=member1, member2=member2)

    results = graph.query(query)
    try:
        first_result = next(iter(results))
        if first_result:
            return True
        else:
            return False
    except StopIteration:
        print("No query results found.")
        return False

def check_dominance(graph, subset1, subset2):
    for member1 in subset1:
        dominates_at_least_one = False        
        for member2 in subset2:
            if is_strictly_preferred(graph, member1, member2):
                dominates_at_least_one = True
                break 
        if not dominates_at_least_one:
            return False
    return True

def check_acceptance(graph, subject, action, obj):
    if not (subject and obj and action):
        return False
    else:
        permission_supports = compute_supports(graph, subject, action, obj, 0)
        prohibition_supports = compute_supports(graph, subject, action, obj, 1)
        if len(permission_supports) == len(prohibition_supports) == 0:
            return False
        elif len(permission_supports) == 0:
            return False
        elif len(prohibition_supports) == 0:
            return True
        else:
            stripped_prohibition_supports = []
            for proh_support in prohibition_supports:
                stripped_prohibition_supports.append(tuple(strip_prefix(str(uri)) for uri in proh_support))
            stripped_prohibition_supports = list(set(stripped_prohibition_supports))
            stripped_permission_supports = []
            for perm_support in permission_supports:
                stripped_permission_supports.append(tuple(strip_prefix(str(uri)) for uri in perm_support))
            stripped_permission_supports = list(set(stripped_permission_supports))
            
            accepted = True
            for proh_support in stripped_prohibition_supports:
                conflict_supported = False
                for perm_support in stripped_permission_supports:
                    if check_dominance(graph,perm_support, proh_support):
                        conflict_supported = True
                        break
                if not conflict_supported:
                    return False
            return accepted

def get_abstract_rules(graph):
    abstract_rules_query_path = 'queries.sparql/get_access_types.sparql'

    with open(abstract_rules_query_path, 'r') as file:
        query = file.read()
    
    results = graph.query(query)

    return results

def get_connection_rules(graph):
    connection_rules_query_path = 'queries.sparql/get_connection_rules.sparql'

    with open(connection_rules_query_path, 'r') as file:
        query = file.read()
    
    results = graph.query(query)

    return results

# Load the ontology graph
def load_starwars_policy():
    graph = Graph()
    graph.parse("ontology/orbac-STARWARS.owl", format="xml")
    return graph

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

#if button_load or button_build:
#    st.write("Coming soon")

#if button_use:
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

        # Primary tabs for grouping
        main_tabs = st.tabs(["Check Privileges", "Check Consistency", "Compute Supports", "Acceptance"])

        # 1. Checking Privileges Tab
        with main_tabs[0]:
            st.caption("Checking the inference of a privilege")

            # Nested tabs for permission and prohibition
            #privilege_tabs = st.tabs(["Check Permission", "Check Prohibition"])
            
            col1, col2 = st.columns(2)
            #with privilege_tabs[0]:  # Check Permission
            with col1:
                if st.button("Check Permission", use_container_width=True):
                    if not (subject and obj and action):
                        st.write("Please enter a valid subject, action and object!")
                    elif ispermitted(graph, subject, action, obj):
                        st.write(f"{subject} is permitted to perform {action} on {obj}")
                    else:
                        st.write(f"{subject} is not permitted to perform {action} on {obj}")
            with col2:
                #with privilege_tabs[1]:  # Check Prohibition
                if st.button("Check Prohibition", use_container_width=True):
                    if not (subject and obj and action):
                        st.write("Please enter a valid subject, action and object!")
                    elif isprohibited(graph, subject, action, obj):
                        st.write(f"{subject} is prohibited from performing {action} on {obj}")
                    else:
                        st.write(f"{subject} is not prohibited from performing {action} on {obj}")

        # 2. Checking Consistency & Conflicts Tab
        with main_tabs[1]:
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
        with main_tabs[2]:
            #st.caption("Compute supports")
            
            # Nested tabs for permission and prohibition supports
            support_tabs = st.tabs(["Permission supports", "Prohibition supports"])
            
            with support_tabs[0]:  # Permission Supports
                if st.button("Compute permission supports", use_container_width=True):
                    supports = compute_supports(graph, subject, action, obj, 0)
                    supports_data = pd.DataFrame(supports, columns=["Employ relation", "Use relation", "Define relation"])
                    supports_data = supports_data.map(strip_prefix)
                    st.dataframe(supports_data,hide_index=True, use_container_width=True)

            with support_tabs[1]:  # Prohibition Supports
                if st.button("Compute prohibition supports", use_container_width=True):
                    supports = compute_supports(graph, subject, action, obj, 1)
                    supports_data = pd.DataFrame(supports, columns=["Employ relation", "Use relation", "Define relation"])
                    supports_data = supports_data.map(strip_prefix)
                    st.dataframe(supports_data, hide_index=True, use_container_width=True)

        # 4. Acceptance Tab
        with main_tabs[3]:
            #st.caption("Checking acceptance")
            if st.button("Check acceptance", use_container_width=True):
                if not (subject and obj and action):
                    st.write("Please enter a valid subject, action and object!")
                else:
                    if check_acceptance(graph, subject, action, obj):
                        st.write(f"The permission for {subject} to perform {action} on {obj} is granted")
                    else:
                        st.write(f"The permission for {subject} to perform {action} on {obj} is denied")
                #if st.button("Explain"):
                #    st.write("")

#    button_use = st.button('Use an example policy', use_container_width=True, type='primary', on_click=display_use_part)

sidebar_option = st.sidebar.selectbox('Choose an option:',('Use an example policy', 'Load a policy', 'Build your policy'))

if sidebar_option == 'Use an example policy':
    display_use_part()
elif sidebar_option == "Load a policy" or sidebar_option == "Build your policy":
    display_coming()