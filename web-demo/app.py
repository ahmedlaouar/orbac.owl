import streamlit as st
from rdflib import Graph
import pandas as pd

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

# Load the ontology graph
def load_starwars_policy():
    graph = Graph()
    graph.parse("ontology/orbac-STARWARS.owl", format="xml")
    return graph

# Streamlit app
st.title = "OrBAC ontology demo"
st.header = "Test some functions of the OrBAC ontology"

# Policy selection options
policy_option = st.selectbox("Choose an option:", ["Load a policy", "Build a policy", "Load an example policy"])



# Display options or load STARWARS policy
if policy_option == "Load a policy" or policy_option == "Build a policy":
    st.write("Coming soon")
elif policy_option == "Load an example policy":
    example_option = st.selectbox("Choose an example policy:", ["Starwars", "Policy 2"])
    if example_option == "Starwars":
        st.write("Loading STARWARS policy...")
        graph = load_starwars_policy()
        st.write("STARWARS policy loaded successfully!")
    elif example_option == "Policy 2":
        st.write("Loading Policy 2...")
        graph = load_starwars_policy()
        st.write("Policy 2 loaded successfully!")
    
    with st.expander("Visualize the policy", expanded=True):
        st.caption("A visualization of the policy:")


    with st.expander("Privilege inference and conflict resolution", expanded=True):
        # Create 3 columns
        col1, col2, col3 = st.columns(3)

        # Place the text inputs in the respective columns
        with col1:
            subject = st.text_input("Subject")

        with col2:
            obj = st.text_input("Object")

        with col3:
            action = st.text_input("Action")

        # Primary tabs for grouping
        main_tabs = st.tabs(["Check Privileges", "Check Consistency", "Compute Supports", "Acceptance"])

        # 1. Checking Privileges Tab
        with main_tabs[0]:
            st.caption("Checking the existence of a privilege")

            # Nested tabs for permission and prohibition
            #privilege_tabs = st.tabs(["Check Permission", "Check Prohibition"])
            
            col1, col2 = st.columns(2)
            #with privilege_tabs[0]:  # Check Permission
            with col1:
                if st.button("Check Permission"):
                    if not (subject and obj and action):
                        st.write("Please enter a valid subject, action and object!")
                    elif ispermitted(graph, subject, action, obj):
                        st.write(f"{subject} is permitted to perform {action} on {obj}")
                    else:
                        st.write(f"{subject} is not permitted to perform {action} on {obj}")
            with col2:
                #with privilege_tabs[1]:  # Check Prohibition
                if st.button("Check Prohibition"):
                    if not (subject and obj and action):
                        st.write("Please enter a valid subject, action and object!")
                    elif isprohibited(graph, subject, action, obj):
                        st.write(f"{subject} is prohibited from performing {action} on {obj}")
                    else:
                        st.write(f"{subject} is not prohibited from performing {action} on {obj}")

        # 2. Checking Consistency & Conflicts Tab
        with main_tabs[1]:
            st.caption("Checking consistency & computing the conflicts")

            if st.button("Check consistency"):
                consistency = check_consistency(graph)
                if consistency:
                    st.write("The instance is consistent")
                else:
                    st.write("The instance is inconsistent")
            # Only show Compute Conflicts if inconsistent
            if st.button("Compute conflicts"):
                compute_conflicts(graph)
                # Placeholder output for conflicts
                conflicts = compute_conflicts(graph)
                conflict_data = pd.DataFrame(conflicts, columns=["Employ relation", "Use relation", "Define relation", "Employ relation", "Use relation", "Define relation"])
                st.table(conflict_data)

        # 3. Compute Supports Tab
        with main_tabs[2]:
            st.caption("Compute supports")
            
            # Nested tabs for permission and prohibition supports
            support_tabs = st.tabs(["Permission supports", "Prohibition supports"])
            
            with support_tabs[0]:  # Permission Supports
                if st.button("Compute permission supports"):
                    compute_supports(graph, subject, action, obj, 0)
                    # Placeholder output for permission supports

            with support_tabs[1]:  # Prohibition Supports
                if st.button("Compute prohibition supports"):
                    compute_supports(graph, subject, action, obj, 1)
                    # Placeholder output for prohibition supports

        # 4. Acceptance Tab
        with main_tabs[3]:
            st.caption("Checking acceptance")
            if st.button("Check acceptance"):
                if not (subject and obj and action):
                    st.write("Please enter a valid subject, action and object!")
                else:
                    if check_acceptance(graph, subject, action, obj):
                        st.write(f"The permission for {subject} to perform {action} on {obj} is granted")
                    else:
                        st.write(f"The permission for {subject} to perform {action} on {obj} is denied")
                #if st.button("Explain"):
                #    st.write("")


