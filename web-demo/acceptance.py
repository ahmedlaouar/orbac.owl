from rdflib import RDF, Graph, URIRef

def strip_prefix(uri):
    return uri.split('#')[-1]

def ispermitted(graph, example_uri, subject, action, obj):
    query_path = "queries.sparql/is-permitted.sparql"
    with open(query_path, 'r') as file:
        
        query_template = file.read()
        
        query = query_template.format(example_uri=example_uri, subject=subject, action=action, object=obj)
        
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

def isprohibited(graph, example_uri, subject, action, obj):
    query_path = "queries.sparql/is-prohibited.sparql"
    with open(query_path, 'r') as file:
        
        query_template = file.read()
        
        query = query_template.format(example_uri=example_uri, subject=subject, action=action, object=obj)
        
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

def compute_supports(graph, example_uri, subject, action, obj, accessType=0):
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
        
        query = query_template.format(example_uri=example_uri, subject=subject, action=action, object=obj)
        
        results = graph.query(query)
    
    return results

def compute_raw_supports(graph, example_uri, subject, action, obj, accessType=0):
    # by default, support of a permission is computed when accessType=0
    # for a support of a prohibition set accessType = 1
    if accessType == 0:
        supports_query_path = "queries.sparql/permission_raw_supports.sparql"
    elif accessType == 1:
        supports_query_path = "queries.sparql/prohibition_raw_supports.sparql"
    else:
        print("Please enter a valid accessType.")

    with open(supports_query_path, 'r') as file:
        
        query_template = file.read()
        
        query = query_template.format(example_uri= example_uri, subject=subject, action=action, object=obj)
        
        results = graph.query(query)
    
    return results

def compute_hierarchy_supports(graph, example_uri, subject, action, obj, accessType=0):
    # by default, support of a permission is computed when accessType=0
    # for a support of a prohibition set accessType = 1
    if accessType == 0:
        supports_query_path = "queries.sparql/permission_hierarchy_supports.sparql"
    elif accessType == 1:
        supports_query_path = "queries.sparql/prohibition_hierarchy_supports.sparql"
    else:
        print("Please enter a valid accessType.")

    with open(supports_query_path, 'r') as file:
        
        query_template = file.read()
        
        query = query_template.format(example_uri= example_uri, subject=subject, action=action, object=obj)
        
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

def is_strictly_preferred(graph, example_uri, member1, member2):
    dominance_query_path = "queries.sparql/dominance_query.sparql"
    with open(dominance_query_path, 'r') as file:
        query_template = file.read()

    query = query_template.format(example_uri=example_uri, member1=member1, member2=member2)

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

def check_dominance(graph, example_uri, subset1, subset2):
    for member1 in subset1:
        dominates_at_least_one = False        
        for member2 in subset2:
            if is_strictly_preferred(graph, example_uri, member1, member2):
                dominates_at_least_one = True
                break 
        if not dominates_at_least_one:
            return False
    return True

def check_acceptance(graph, example_uri, subject, action, obj):
    if not (subject and obj and action):
        return False
    else:
        permission_supports = compute_supports(graph, example_uri, subject, action, obj, 0)
        prohibition_supports = compute_supports(graph, example_uri, subject, action, obj, 1)
        
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
                    if check_dominance(graph, example_uri, perm_support, proh_support):
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

# Toky's code [begin]
def is_strictly_preferred_with_details_original(graph, example_uri, member1, member2):
    dominance_query_path = "queries.sparql/dominance_query.sparql"
    with open(dominance_query_path, 'r') as file:
        query_template = file.read()

    query = query_template.format(example_uri=example_uri, member1=member1, member2=member2)

    results = graph.query(query)
    try:
        first_result = next(iter(results))
        if first_result:
            detail = member1+" > "+member2
            return (True,detail)
        else: 
            detail = member1+" < "+member2
            return (False,detail)
    except StopIteration:
        print("No query results found.")
        return (False,None)

def check_dominance_with_details_original(graph, example_uri, subset1, subset2):
    preference = (False,None)
    for member1 in subset1:
        dominates_at_least_one = False
        for member2 in subset2:   
            preference = is_strictly_preferred_with_details_original(graph, example_uri, member1, member2)         
            if preference[0]:
                dominates_at_least_one = True                
                break 
        if not dominates_at_least_one:
            return (False,None)
    return preference

def check_acceptance_with_details_original(graph, example_uri, subject, action, obj):
    if not (subject and obj and action):
        return False
    else:
        permission_supports = compute_supports(graph, example_uri, subject, action, obj, 0)
        prohibition_supports = compute_supports(graph, example_uri, subject, action, obj, 1)
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
            detail = None
            for proh_support in stripped_prohibition_supports:
                conflict_supported = False
                for perm_support in stripped_permission_supports:
                    dominance = check_dominance_with_details_original(graph, example_uri, perm_support, proh_support)
                    if dominance[0]:
                        conflict_supported = True
                        detail = dominance[1]
                        break
                if not conflict_supported:
                    return False
            return (accepted,detail)


def check_if_role_from_hierarchy(graph, example_uri, access_type_relation, employ_relation):
    # Test if some roles are inferred from hierarchy
    # amounts to checking if an employ relation exists and connects subject to role
    # return True if the role is inferred from a hierarchy, False instead. The negation of the result of the query
    verif_query= """PREFIX orbac-owl: <https://raw.githubusercontent.com/ahmedlaouar/orbac.owl/refs/heads/main/ontology/orbac.owl#>
    PREFIX : <{example_uri}>
    ASK {{
    :{access_type_relation} orbac-owl:accessTypeRole ?role .
    :{employ_relation} orbac-owl:employesRole ?role .
    }}
    """
    query = verif_query.format(example_uri=example_uri, access_type_relation=access_type_relation, employ_relation=employ_relation)
    results = graph.query(query)
    return not(next(iter(results)))

def add_new_employ(graph, example_uri, access_type_relation, subject):
    accessTypeRole = URIRef("https://raw.githubusercontent.com/ahmedlaouar/orbac.owl/refs/heads/main/ontology/orbac.owl#accessTypeRole")
    accessTypeOrganisation = URIRef("https://raw.githubusercontent.com/ahmedlaouar/orbac.owl/refs/heads/main/ontology/orbac.owl#accessTypeOrganisation")
    Employ = URIRef("https://raw.githubusercontent.com/ahmedlaouar/orbac.owl/refs/heads/main/ontology/orbac.owl#Employ")
    employesEmployer = URIRef("https://raw.githubusercontent.com/ahmedlaouar/orbac.owl/refs/heads/main/ontology/orbac.owl#employesEmployer")
    employesEmploee = URIRef("https://raw.githubusercontent.com/ahmedlaouar/orbac.owl/refs/heads/main/ontology/orbac.owl#employesEmployee")
    employesRole = URIRef("https://raw.githubusercontent.com/ahmedlaouar/orbac.owl/refs/heads/main/ontology/orbac.owl#employesRole")
    isPreferredTo = URIRef("https://raw.githubusercontent.com/ahmedlaouar/orbac.owl/refs/heads/main/ontology/orbac.owl#isPreferredTo")
    
    for _, _, o in graph.triples((URIRef(example_uri+access_type_relation), accessTypeRole, None)):
        role = o
    for _, _, o in graph.triples((URIRef(example_uri+access_type_relation), accessTypeOrganisation, None)):
        organisation = o    

    s = URIRef(example_uri+subject)
    org = organisation
    rel_name = URIRef(example_uri+"employ_"+subject+"_"+role.fragment)

    graph.add((rel_name, RDF.type, Employ))
    graph.add((rel_name, employesEmployer, org))
    graph.add((rel_name, employesRole, role))
    graph.add((rel_name, employesEmploee, s))

    for _, _, role2 in graph.triples((role, isPreferredTo, None)):
        for employ2, _, _ in graph.triples((None, employesRole, role2)):
            graph.add((rel_name, isPreferredTo, employ2))

    for role2, _, _ in graph.triples((None, isPreferredTo, role)):
        for employ2, _, _ in graph.triples((None, employesRole, role2)):
            graph.add((employ2, isPreferredTo, rel_name))

    return graph