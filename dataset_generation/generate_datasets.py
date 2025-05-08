import argparse
import json
import random
from itertools import product
import rdflib
from rdflib.namespace import RDF, OWL

import classes

def generate_test_cases(input_individuals, nb_confs):
    output_individuals = {
        "parent_organisation": input_individuals["parent_organisation"],
        "Organisation" : [],
        "up_Role" : [],
        "down_Role" : [],
        "Role": [],
        "Activity" : [],
        "View" : [],
        "up_Context" : [],
        "down_Context" : [],
        "Context" : [],
        "Subject" : [],
        "Action" : [],
        "Object" : []
    }    
    output_individuals["Organisation"].append(input_individuals["parent_organisation"])
    generated_elements = set()
    
    # For each action type (consult, modify, validate)
    for _ in range(nb_confs):
        # choose first a random subject, action and object (activity follows by default)
        s = random.choice(input_individuals["Subject"])
        o = random.choice(input_individuals["Object"])
        act = random.choice(list(input_individuals["Action"].keys()))
        a_perm, a_proh = act, act
        a = random.choice(input_individuals["Action"][act])
        # Appending individual data
        output_individuals["Subject"].append(s)
        output_individuals["Action"].append(a)
        output_individuals["Object"].append(o) 
        
        # for a random number of times, generate a case for the same s, o, a
        concrete_n = random.randint(1,3)
        for _ in range(concrete_n):
            # this loop repeats to generate 1..4 supports for a permission
            # permission supports
            org_perm = random.choice(input_individuals["Organisation"])
            r_perm = random.choice(input_individuals["up_Role"])
            v_perm = random.choice(input_individuals["View"])
            c_perm = random.choice(input_individuals["up_Context"])
            generated_elements.add(classes.Permission(org_perm=org_perm, r_perm=r_perm, v_perm=v_perm, a_perm=a_perm, c_perm=c_perm))
            generated_elements.add(classes.Employ(org=org_perm, r=r_perm, s=s))
            generated_elements.add(classes.Use(org=org_perm, v=v_perm, o=o))
            generated_elements.add(classes.Consider(org=input_individuals["parent_organisation"], a=a_perm, alpha=a))
            generated_elements.add(classes.Define(org=org_perm, s=s, a=a, o=o, c=c_perm))
            generated_elements.add(classes.subOrganisationOf(org_1=org_perm, org_2=input_individuals["parent_organisation"]))         
            output_individuals["Organisation"].append(org_perm)
            output_individuals["up_Role"].append(r_perm)
            output_individuals["Role"].append(r_perm)
            output_individuals["View"].append(v_perm)
            output_individuals["up_Context"].append(c_perm)
            output_individuals["Context"].append(c_perm)
            output_individuals["Activity"].append(a_perm)

        concrete_n = random.randint(1,3)
        for _ in range(concrete_n):
            # this loop repeats to generate 1..4 supports for a permission
            # prohibition supports
            org_proh = random.choice(input_individuals["Organisation"])
            r_proh = random.choice(input_individuals["down_Role"])
            v_proh = random.choice(input_individuals["View"])
            c_proh = random.choice(input_individuals["down_Context"])
            generated_elements.add(classes.Prohibition(org_proh=org_proh, r_proh=r_proh, a_proh=a_proh, v_proh=v_proh, c_proh=c_proh))
            generated_elements.add(classes.Employ(org=org_proh, r=r_proh, s=s))            
            generated_elements.add(classes.Use(org=org_proh, v=v_proh, o=o))            
            generated_elements.add(classes.Consider(org=input_individuals["parent_organisation"], a=a_proh, alpha=a))            
            generated_elements.add(classes.Define(org=org_proh, s=s, a=a, o=o, c=c_proh))
            generated_elements.add(classes.subOrganisationOf(org_1=org_proh, org_2=input_individuals["parent_organisation"]))

            output_individuals["Organisation"].append(org_proh)
            output_individuals["down_Role"].append(r_proh)
            output_individuals["Role"].append(r_proh)
            output_individuals["View"].append(v_proh)
            output_individuals["down_Context"].append(c_proh)
            output_individuals["Context"].append(c_proh)
            output_individuals["Activity"].append(a_proh)                    

    return generated_elements, output_individuals

def add_generated_to_graph(graph, test_data, output_individuals, long_example, ORBAC):
    count = 0
    for typ, elements in output_individuals.items():
        if typ == "up_Role" or typ == "down_Role" or typ == "up_Context" or typ == "down_Context" or typ == "parent_organisation":
            continue
        for element in elements:
            graph.add((rdflib.URIRef(long_example[element]), RDF.type, rdflib.URIRef(ORBAC[typ])))
        
    for relation in test_data:
        name = str(type(relation)).split("'")[1].split(".")[-1]
        if name != "subOrganisationOf":
            graph.add((rdflib.URIRef(long_example[name+str(count)]), RDF.type, rdflib.URIRef(ORBAC[name])))
            attributes = vars(relation)
            for att_name, value in attributes.items():
                graph.add((rdflib.URIRef(long_example[name+str(count)]), rdflib.URIRef(ORBAC[att_name]), rdflib.URIRef(long_example[value])))
        #else:
            #attributes = vars(relation)
        count +=1

    for org in output_individuals["Organisation"]:
        if org != output_individuals["parent_organisation"]:
            graph.add((rdflib.URIRef(long_example[org]), rdflib.URIRef(ORBAC["subOrganisationOf"]), rdflib.URIRef(long_example[output_individuals["parent_organisation"]])))
    
    # preference between contexts
    for up_c in output_individuals["up_Context"]:
        for down_c in output_individuals["down_Context"]:
            graph.add((rdflib.URIRef(long_example[up_c]), rdflib.URIRef(ORBAC["isPreferredTo"]), rdflib.URIRef(long_example[down_c])))
    
    # preference between roles
    for up_r in output_individuals["up_Role"]:
        for down_r in output_individuals["down_Role"]:
            graph.add((rdflib.URIRef(long_example[up_r]), rdflib.URIRef(ORBAC["isPreferredTo"]), rdflib.URIRef(long_example[down_r])))

if __name__ == '__main__':
    """"""
    """Generating and Adding test examples to an rdflib graph"""    

    parser = argparse.ArgumentParser(description="Generation of RDF graphs for examples of the OrBAC ontology.")
    parser.add_argument("--file", type=str, required=True, help="Path to JSON file containing elements of an example.")
    parser.add_argument("--conflicts", type=int, required=True, help="The number of conflicts wanted in the output graph.")

    args = parser.parse_args()
    nb_confs = args.conflicts
    example_file = args.file

    with open(example_file, "r") as f:
        individuals = json.load(f)

    example_name = example_file.split("/")[-1].split(".json")[0]

    # Namespaces
    example_uri = f"http://www.semanticweb.org/bleu/ontologies/2025/0/{example_name}_{nb_confs}#"
    long_example = rdflib.Namespace(example_uri)
    ORBAC = rdflib.Namespace("https://raw.githubusercontent.com/ahmedlaouar/orbac.owl/refs/heads/main/ontology/orbac.owl#")    
    
    # Create graph and load ORBAC ontology
    graph = rdflib.Graph()
    graph.parse("ontology/orbac.owl", format="xml")
    
    graph.bind("ex", long_example)
    graph.bind("orbac", ORBAC)
    graph.bind("owl", OWL)
    # Explicitly declare this ontology's IRI
    graph.add((rdflib.URIRef(example_uri), RDF.type, OWL.Ontology))

    # Explicitly declare ORBAC as an import
    graph.add((rdflib.URIRef(example_uri), OWL.imports, rdflib.URIRef("https://raw.githubusercontent.com/ahmedlaouar/orbac.owl/refs/heads/main/ontology/orbac.owl")))

    generated_elements, output_individuals = generate_test_cases(individuals, nb_confs)
    add_generated_to_graph(graph, generated_elements, output_individuals, long_example, ORBAC)

    output_file = f"ontology/examples/{example_name}_{nb_confs}.owl"
    graph.serialize(destination=output_file,format="application/rdf+xml")
