from rdflib import Graph, Namespace, URIRef, Literal
from rdflib.namespace import RDF, RDFS, OWL
from urllib.parse import urlparse

def strip_prefix(uri):
    return uri.split('#')[-1]

def check_permission(graph, subject, action, object):
    query = """
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
PREFIX : <http://www.co-ode.org/ontologies/ont.owl#> # Adjust the base URI as necessary

# Permission, Prohibition, Obligation

SELECT ?permission ?employ ?use ?consider ?define
#SELECT ?permission ?org ?r ?r2 ?a ?v ?c ?s ?alpha ?o
WHERE {
    ?employ rdf:type :Employ .
    ?employ :employesEmployee :"""+subject+""" .
    
    ?use rdf:type :Use .
    ?use :usesObject :"""+object+""".
    ?use :usesView ?v .
   
    ?consider rdf:type :Consider .
    ?consider :considersAction :"""+action+""" .
    ?consider :considersActivity ?a .
    
    ?define rdf:type :Define .
    ?define :definesSubject :"""+subject+""" .
    ?define :definesAction :"""+action+""" .
    ?define :definesObject :"""+object+""".
    ?define :definesContext ?c .

    ?permission rdf:type :Permission .
    ?permission :accessTypeRole ?r .
    ?permission :accessTypeActivity ?a .
    ?permission :accessTypeView ?v .
    ?permission :accessTypeContext ?c .

    {
    ?employ :employesEmployer ?org .
    } UNION    {
    ?employ :employesEmployer ?org2 .
    ?org :subOrganisationOf* ?org2 . 
    }
    {
    ?use :usesEmployer ?org .
    } UNION    {
    ?use :usesEmployer ?org2 .
    ?org :subOrganisationOf* ?org2 . 
    }
    {
    ?consider :considersOrganisation ?org .
    } UNION    {
    ?consider :considersOrganisation ?org2 .
    ?org :subOrganisationOf* ?org2 . 
    }
    {
    ?define :definesOrganisation ?org .
    } UNION    {
    ?define :definesOrganisation ?org2 .
    ?org :subOrganisationOf* ?org2 . 
    }
    {
    ?permission :accessTypeOrganisation ?org .
    } UNION    {
    ?permission :accessTypeOrganisation ?org2 .
    ?org :subOrganisationOf* ?org2 . 
    }
    {
    ?employ :employesRole ?r .
    } UNION {
    ?employ :employesRole ?r2 .
    {?r2 rdf:type :SubRole .} UNION {?r2 rdf:type :SeniorRole .}
    ?r2 :hasParent+ ?r .
    ?r2 :subRoleOrganisation ?org .
    }
    }
"""
    results = graph.query(query)

    
    for result in results:
        stripped_result = tuple(strip_prefix(str(uri)) for uri in result)
        print(stripped_result)
    
    return len(results) > 0

subject = "researcher4"
object = "dataset1"
action = "read"

# Load the ontology
graph = Graph()
graph.parse("ontology/orbac-STARWARS.owl", format="xml")

print(check_permission(graph, subject, action, object))
