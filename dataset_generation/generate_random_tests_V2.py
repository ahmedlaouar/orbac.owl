import random
from itertools import product
import rdflib
from rdflib.namespace import RDF, OWL

from dataset_generation import classes

def generate_test_cases(input_individuals):
    output_individuals = {
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
    output_individuals["Organisation"].append("central_hospital")
    generated_elements = set()
    
    # For each action type (consult, modify, validate)
    for _ in range(50):
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
            generated_elements.add(classes.Consider(org="central_hospital", a=a_perm, alpha=a))
            generated_elements.add(classes.Define(org=org_perm, s=s, a=a, o=o, c=c_perm))
            generated_elements.add(classes.subOrganisationOf(org_1=org_perm, org_2="central_hospital"))         
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
            generated_elements.add(classes.Consider(org="central_hospital", a=a_proh, alpha=a))            
            generated_elements.add(classes.Define(org=org_proh, s=s, a=a, o=o, c=c_proh))
            generated_elements.add(classes.subOrganisationOf(org_1=org_proh, org_2="central_hospital"))

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
        if typ == "up_Role" or typ == "down_Role" or typ == "up_Context" or typ == "down_Context":
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
        if org != "central_hospital":
            graph.add((rdflib.URIRef(long_example[org]), rdflib.URIRef(ORBAC["subOrganisationOf"]), rdflib.URIRef(long_example["central_hospital"])))
    
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
    # xmlns="http://www.semanticweb.org/laouar/ontologies/2025/0/hospital_example_25#"
    long_example = rdflib.Namespace("http://www.semanticweb.org/laouar/ontologies/2025/0/hospital_example_25#")
    ORBAC = rdflib.Namespace("https://raw.githubusercontent.com/ahmedlaouar/orbac.owl/refs/heads/main/ontology/orbac.owl#")    
    
    graph = rdflib.Graph()
    base_ontology_path = "ontology/orbac.owl"
    graph.parse(base_ontology_path, format="xml")
    graph.bind("orbac-owl", ORBAC)
    graph.bind("",long_example)
    graph.add((rdflib.URIRef(long_example), RDF.type, OWL.Ontology))

    individuals = {
        "Organisation" : ["west_hospital", "east_hospital", "south_hospital", "north_hospital"],
        "up_Role" : ["anesthetist", "hospital_doctor", "intern", "surgeon", "liberal_doctor", "doctor", "specialist", "nurse"],
        "down_Role" : ["patient", "medical_secretary", "student", "extern"],
        "View" : ["medical_file", "sample", "medical_data", "personal_data", "admin_data", "prescribtion_data"],
        "up_Context" : ["intern_presc_hour", "referent_doctor", "anesthesic_patient", "emergency"],
        "down_Context" : ["afternoon", "sample_analysis", "morning", "no_anesthesia"],
        "Subject" : ["Alice_Johnson", "Bob_Smith", "Charlie_Brown", "David_Williams", "Eva_Clark", "Frank_Harris", "Grace_Davis", "Henry_Lee", "Isla_Martin", "James_Wilson", "Katherine_Moore", "Liam_Taylor", "Mia_Anderson", "Nathan_White", "Olivia_Scott", "Paul_Harris", "Quinn_Thomas", "Rachel_Baker", "Samuel_Evans", "Tina_Allen", "Ursula_Carter", "Victor_Turner", "Wendy_Mitchell", "Xander_Rodriguez", "Yara_Lee", "Zane_Gonzalez", "Amelia_King", "Ben_Foster", "Chloe_Walker", "Dylan_Nelson"],
        "Action" : {
            "prescribe" : ["transfer", "prescribe_appointment", "manage", "prescribe_prescription", "prescribe_medecine"],
            "consult" : ["read_db", "ask", "cat", "describe", "grep", "list", "read", "select"],
            "prepare_operation" : ["anaesthetize"],
            "operate" : ["aOperate"],
            "analyze" : ["blood_analysis", "cancer_analysis", "biopsy"],
            "handle" : ["handle_db", "delegate"],
            "modify": ["add", "copy", "create", "delete", "drop", "edit", "insert", "move", "write", "write_db", "revoke"],
            "validate": ["sign"]
        },
        "Object" : ["prescription_1", "prescription_2", "prescription_3", "prescription_4", "prescription_5", 
                    "sample_1", "sample_2", "sample_3", "sample_4", "sample_5", 
                    "patinet_medical_data_1", "patinet_medical_data_2", "patinet_medical_data_3", "patinet_medical_data_4", "patinet_medical_data_5",
                    "patinet_admin_data_1", "patinet_admin_data_2", "patinet_admin_data_3", "patinet_admin_data_4", "patinet_admin_data_5"]
    }

    generated_elements, output_individuals = generate_test_cases(individuals)
    add_generated_to_graph(graph, generated_elements, output_individuals, long_example, ORBAC)

    output_file = "ontology/examples/hospital_example_25.owl"
    graph.serialize(destination=output_file,format="application/rdf+xml")
