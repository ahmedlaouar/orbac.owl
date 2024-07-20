from rdflib import Graph, Namespace, URIRef, Literal
from rdflib.namespace import RDF, RDFS, OWL
from urllib.parse import urlparse

def strip_prefix(uri):
    return uri.split('#')[-1]

def compute_supports(graph, subject, action, object):
    supports_query_path = "queries.sparql/supports_query.sparql"
    with open(supports_query_path, 'r') as file:
        
        query_template = file.read()
        
        query = query_template.format(subject=subject, action=action, object=object)
        
        results = graph.query(query)
    
    return results

def check_consistency(graph):
    consistency_checking_query_path = "queries.sparql/consistency_checking.sparql"
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
    conflicts_query_path = 'queries.sparql/conflicts_query.sparql'

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

def check_acceptance(graph, subject, action, object):
    supports = compute_supports(graph, subject, action, object)
    conflicts = compute_conflicts(graph)
    stripped_conflicts = []
    for conflict in conflicts:
        stripped_conflicts.append(tuple(strip_prefix(str(uri)) for uri in conflict))
    stripped_conflicts = list(set(stripped_conflicts))
    stripped_supports = []
    for support in supports:
        stripped_supports.append(tuple(strip_prefix(str(uri)) for uri in support))
    stripped_supports = list(set(stripped_supports))
    #print(stripped_supports)
    #print(stripped_conflicts)
    accepted = True
    for conflict in stripped_conflicts:
        conflict_supported = False
        for support in stripped_supports:
            if check_dominance(graph,support, conflict):
                conflict_supported = True
                break
        if not conflict_supported:
            accepted = False
    return accepted

# Load the ontology
graph = Graph()
graph.parse("ontology/orbac-STARWARS.owl", format="xml")

#subject, object, action = "Bob", "report1", "edit"
subject, object, action = 'researcher4', 'dataset5', 'select'


#if check_acceptance(graph, subject, action, object):
#    print(f"The permission for {subject} to perform the action {action} on {object} is granted")
#else:
#    print(f"The permission for {subject} to perform the action {action} on {object} is denied")




#if check_consistency(graph):
#    print("The instance is consistent")
#else:
#    print("The instance is inconsistent")

supports = compute_supports(graph, subject, action, object)
for support in supports:
    stripped_support = tuple(strip_prefix(str(uri)) for uri in support)
    print(stripped_support)

print("--------------------------------------------------------------------------")
"""
conflicts = compute_conflicts(graph)
for conflict in conflicts:
    stripped_conflict = tuple(strip_prefix(str(uri)) for uri in conflict)
    print(stripped_conflict)
"""