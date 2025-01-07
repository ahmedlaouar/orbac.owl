from rdflib import Graph

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
