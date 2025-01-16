from owlready2 import *

def print_swrl_rules():
    
    onto = get_ontology("ontology/orbac.owl").load()
    example_onto = get_ontology("ontology/examples/secondee-example.owl").load()

    # Access SWRL rules
    print("Ontology IRI:", onto.base_iri)
    print(type(onto.rules()))

    #print("Classes:", list(onto.classes()))
    #print("Properties:", list(onto.properties()))
    #print("Individuals:", list(onto.individuals()))
    if onto.rules():
        for rule in onto.rules():
            print(rule,"\n")
    else:
        print("No SWRL rules found in the ontology.")