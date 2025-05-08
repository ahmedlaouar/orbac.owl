import random
import rdflib
from rdflib.namespace import RDF, OWL
from dataset_generation import classes

"""individuals = {
    "Organisation" : ["Consortium", "Institute1", "Institute2", "Institute3", "University1", "University2", "University3"],
    "Role" : ["associate_professor", "coordinator", "dean", "director", "employee", "engineer", "full_professor", "PhD_student", "post_doc", "professor", "project_officer", "researcher", "secondee", "staff_member", "team_leader", "wp_leader"],
    "Activity" : ["consult", "execute", "full_access", "modify", "validate"],
    "View" : ["administration", "confidential_data", "contracts", "data", "deliverables", "internal_data", "public_data", "reports", "secondment_agreement", "secondment_report", "WP1", "WP2", "WP3", "WP4", "WP5"],
    "Context" : ["audit", "collaboration", "default", "management", "secondment"],
    "Subject" : ["bob", "engineer1", "engineer2", "engineer3", "engineer4", "engineer5", "engineer6", "officer", "phdStudent1", "phdStudent2", "phdStudent3", "phdStudent4", "phdStudent5", "phdStudent6", "phdStudent7", "phdStudent8", "postDoc1", "postDoc2", "professor1", "professor2", "professor3", "professor4", "professor5", "professor6", "projectCoordinator", "researcher1", "researcher2", "researcher3", "researcher4", "researcher5", "researcher6"],
    "Subject" : ["Alice_Johnson", "Bob_Smith", "Charlie_Brown", "David_Williams", "Eva_Clark", "Frank_Harris", "Grace_Davis", "Henry_Lee", "Isla_Martin", "James_Wilson", "Katherine_Moore", "Liam_Taylor", "Mia_Anderson", "Nathan_White", "Olivia_Scott", "Paul_Harris", "Quinn_Thomas", "Rachel_Baker", "Samuel_Evans", "Tina_Allen", "Ursula_Carter", "Victor_Turner", "Wendy_Mitchell", "Xander_Rodriguez", "Yara_Lee", "Zane_Gonzalez", "Amelia_King", "Ben_Foster", "Chloe_Walker", "Dylan_Nelson"],
    "Action" : ["add", "ask", "cat", "copy", "create", "delete", "describe", "drop", "edit", "grep", "insert", "list", "Modify", "move", "read", "select", "sign"],
    "Object" : ["agreement1", "agreement2", "agreement3", "agreement4", "agreement5", "agreement6", "dataset1", "dataset10", "dataset2", "dataset3", "dataset4", "dataset5", "dataset6", "dataset7", "dataset8", "dataset9", "deliverable1", "deliverable2", "report1", "report2", "report3", "report4", "report5", "report6", "report7"]
}"""
individuals = {
    "Organisation" : [],
    "Role" : [],
    "Activity" : [],
    "View" : [],
    "Context" : [],
    "Subject" : [],
    "Action" : [],
    "Object" : []
}
def generate_single_test_case(s, a, o, org_perm, org_proh, r_perm, r_proh, v_perm, v_proh, c_perm, c_proh, a_perm, a_proh):
    return {
        "Permission": {
            "accessTypeOrganisation": org_perm,
            "accessTypeRole": r_perm,
            "accessTypeActivity": a_perm,
            "accessTypeView": v_perm,
            "accessTypeContext": c_perm
        },
        "Prohibition": {
            "accessTypeOrganisation": org_proh,
            "accessTypeRole": r_proh,
            "accessTypeActivity": a_proh,
            "accessTypeView": v_proh,
            "accessTypeContext": c_proh
        },
        "Employ": [{
            "employesEmployer": org_perm,
            "employesRole": r_perm,
            "employesEmployee": s
        }, {
            "employesEmployer": org_proh,
            "employesRole": r_proh,
            "employesEmployee": s
        }],
        "Use": [{
            "usesEmployer": org_perm,
            "usesObject": o,
            "usesView": v_perm
        }, {
            "usesEmployer": org_proh,
            "usesObject": o,
            "usesView": v_proh
        }],
        "Consider": [{
            "considersOrganisation": org_perm,
            "considersAction": a,
            "considersActivity": a_perm
        }, {
            "considersOrganisation": org_proh,
            "considersAction": a,
            "considersActivity": a_proh
        }],
        "Define": [{
            "definesOrganisation": org_perm,
            "definesSubject": s,
            "definesAction": a,
            "definesObject": o,
            "definesContext": c_perm
        }, {
            "definesOrganisation": org_proh,
            "definesSubject": s,
            "definesAction": a,
            "definesObject": o,
            "definesContext": c_proh
        }],
        "subOrganisationOf": [(org_perm, "Consortium"), (org_proh, "Consortium")],
        "Expected": "Is-permitted and Is-prohibited hold for (s={}, a={}, o={})".format(s, a, o)
    }

def generate_test_cases():
    Org = ["Institute1", "Institute2", "Institute3", "University1", "University2", "University3"] #"Consortium",
    #R = ["associate_professor", "coordinator", "dean", "director", "employee", "engineer", "full_professor", "PhD_student", "post_doc", "professor", "project_officer", "researcher", "secondee", "staff_member", "team_leader", "wp_leader"]
    V = ["administration", "confidential_data", "contracts", "data", "deliverables", "internal_data", "public_data", "reports", "secondment_agreement", "secondment_report", "WP1", "WP2", "WP3", "WP4", "WP5"]
    #C = ["audit", "collaboration", "default", "management", "secondment"]
    s_list = [
    "Alice_Johnson", "Bob_Smith", "Charlie_Brown", "David_Williams", "Eva_Clark",
    "Frank_Harris", "Grace_Davis", "Henry_Lee", "Isla_Martin", "James_Wilson",
    "Katherine_Moore", "Liam_Taylor", "Mia_Anderson", "Nathan_White", "Olivia_Scott",
    "Paul_Harris", "Quinn_Thomas", "Rachel_Baker", "Samuel_Evans", "Tina_Allen",
    "Ursula_Carter", "Victor_Turner", "Wendy_Mitchell", "Xander_Rodriguez", "Yara_Lee",
    "Zane_Gonzalez", "Amelia_King", "Ben_Foster", "Chloe_Walker", "Dylan_Nelson"]
    #["bob", "engineer1", "engineer2", "engineer3", "engineer4", "engineer5", "engineer6", "officer", "phdStudent1", "phdStudent2", "phdStudent3", "phdStudent4", "phdStudent5", "phdStudent6", "phdStudent7", "phdStudent8", "postDoc1", "postDoc2", "professor1", "professor2", "professor3", "professor4", "professor5", "professor6", "projectCoordinator", "researcher1", "researcher2", "researcher3", "researcher4", "researcher5", "researcher6"]
    o_list = ["agreement1", "agreement2", "agreement3", "agreement4", "agreement5", "agreement6", "dataset1", "dataset10", "dataset2", "dataset3", "dataset4", "dataset5", "dataset6", "dataset7", "dataset8", "dataset9", "deliverable1", "deliverable2", "report1", "report2", "report3", "report4", "report5", "report6", "report7"]
    
    up_C = ["secondment", "management", "audit"]
    down_C = ["default", "collaboration"]
    #up_R = ["full_professor", "project_officer", "team_leader", "researcher", "wp_leader", "coordinator", "dean", "director"]
    #down_R = ["employee", "staff_member", "PhD_student", "post_doc", "secondee",  "engineer", "associate_professor", "professor"]
    up_R = ["full_professor", "team_leader", "researcher", "wp_leader", "coordinator"]
    down_R = ["staff_member", "PhD_student", "post_doc", "secondee", "associate_professor"]
    actions = {
        "consult": ["ask", "cat", "describe", "grep", "list", "read", "select"],
        "modify": ["add", "copy", "create", "delete", "drop", "edit", "insert", "move"],
        "validate": ["sign"]
    }

    individuals["Organisation"].append("Consortium")
    generated_elements = set()
    
    # For each action type (consult, modify, validate)
    for _ in range(50):
        # choose first a random subject, action and object (activity follows by default)
        s = random.choice(s_list)
        o = random.choice(o_list)
        act = random.choice(list(actions.keys()))
        a_perm, a_proh = act, act
        a = random.choice(actions[act])
        # Appending individual data
        individuals["Subject"].append(s)
        individuals["Action"].append(a)
        individuals["Object"].append(o) 
        
        # for a random number of times, generate a case for the same s, o, a
        concrete_n = random.randint(1,3)
        for _ in range(concrete_n):
            # this loop repeats to generate 1..4 supports for a permission

            # permission supports
            org_perm = random.choice(Org)
            r_perm = random.choice(up_R)
            v_perm = random.choice(V)
            c_perm = random.choice(up_C)
            generated_elements.add(classes.Permission(org_perm=org_perm, r_perm=r_perm, v_perm=v_perm, a_perm=a_perm, c_perm=c_perm))
            generated_elements.add(classes.Employ(org=org_perm, r=r_perm, s=s))
            generated_elements.add(classes.Use(org=org_perm, v=v_perm, o=o))
            generated_elements.add(classes.Consider(org="Consortium", a=a_perm, alpha=a))
            generated_elements.add(classes.Define(org=org_perm, s=s, a=a, o=o, c=c_perm))
            generated_elements.add(classes.subOrganisationOf(org_1=org_perm, org_2="Consortium"))         
            individuals["Organisation"].append(org_perm)
            individuals["Role"].append(r_perm)
            individuals["View"].append(v_perm)
            individuals["Context"].append(c_perm)
            individuals["Activity"].append(a_perm)

        concrete_n = random.randint(1,3)
        for _ in range(concrete_n):
            # this loop repeats to generate 1..4 supports for a permission

            # prohibition supports
            org_proh = random.choice(Org)
            r_proh = random.choice(down_R)
            v_proh = random.choice(V)
            c_proh = random.choice(down_C)
            generated_elements.add(classes.Prohibition(org_proh=org_proh, r_proh=r_proh, a_proh=a_proh, v_proh=v_proh, c_proh=c_proh))
            generated_elements.add(classes.Employ(org=org_proh, r=r_proh, s=s))            
            generated_elements.add(classes.Use(org=org_proh, v=v_proh, o=o))            
            generated_elements.add(classes.Consider(org="Consortium", a=a_proh, alpha=a))            
            generated_elements.add(classes.Define(org=org_proh, s=s, a=a, o=o, c=c_proh))
            generated_elements.add(classes.subOrganisationOf(org_1=org_proh, org_2="Consortium"))

            individuals["Organisation"].append(org_proh)
            individuals["Role"].append(r_proh)
            individuals["View"].append(v_proh)
            individuals["Context"].append(c_proh)
            individuals["Activity"].append(a_proh)                    

    return generated_elements

def add_generated_to_graph(graph, test_data):
    """Adding generated test examples to an rdflib graph"""
    long_example = rdflib.Namespace("http://www.semanticweb.org/bleu/ontologies/2025/0/supports_1to3_example_50#")
    ORBAC = rdflib.Namespace("https://raw.githubusercontent.com/ahmedlaouar/orbac.owl/refs/heads/main/ontology/orbac.owl#")    
    
    graph.bind("orbac-owl", ORBAC)
    graph.bind("",long_example)
    graph.add((rdflib.URIRef(long_example), RDF.type, OWL.Ontology))
    count = 0
    for typ, elements in individuals.items():
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

    for org in individuals["Organisation"]:
        if org != "Consortium":
            graph.add((rdflib.URIRef(long_example[org]), rdflib.URIRef(ORBAC["subOrganisationOf"]), rdflib.URIRef(long_example["Consortium"])))
    
    # preference between contexts 
    graph.add((rdflib.URIRef(long_example["collaboration"]), rdflib.URIRef(ORBAC["isPreferredTo"]), rdflib.URIRef(long_example["default"])))
    graph.add((rdflib.URIRef(long_example["secondment"]), rdflib.URIRef(ORBAC["isPreferredTo"]), rdflib.URIRef(long_example["default"])))
    graph.add((rdflib.URIRef(long_example["secondment"]), rdflib.URIRef(ORBAC["isPreferredTo"]), rdflib.URIRef(long_example["collaboration"])))
    graph.add((rdflib.URIRef(long_example["management"]), rdflib.URIRef(ORBAC["isPreferredTo"]), rdflib.URIRef(long_example["default"])))
    graph.add((rdflib.URIRef(long_example["management"]), rdflib.URIRef(ORBAC["isPreferredTo"]), rdflib.URIRef(long_example["secondment"])))
    graph.add((rdflib.URIRef(long_example["management"]), rdflib.URIRef(ORBAC["isPreferredTo"]), rdflib.URIRef(long_example["collaboration"])))
    graph.add((rdflib.URIRef(long_example["audit"]), rdflib.URIRef(ORBAC["isPreferredTo"]), rdflib.URIRef(long_example["management"])))
    graph.add((rdflib.URIRef(long_example["audit"]), rdflib.URIRef(ORBAC["isPreferredTo"]), rdflib.URIRef(long_example["default"])))
    graph.add((rdflib.URIRef(long_example["audit"]), rdflib.URIRef(ORBAC["isPreferredTo"]), rdflib.URIRef(long_example["collaboration"])))  
    
    # preference between roles
    up_R = ["full_professor", "team_leader", "researcher", "wp_leader", "coordinator"]
    down_R = ["staff_member", "PhD_student", "post_doc", "secondee", "associate_professor"]
    for up_r in up_R:
        for down_r in down_R:
            graph.add((rdflib.URIRef(long_example[up_r]), rdflib.URIRef(ORBAC["isPreferredTo"]), rdflib.URIRef(long_example[down_r])))
    """        
    graph.add((rdflib.URIRef(long_example["employee"]), rdflib.URIRef(ORBAC["isPreferredTo"]), rdflib.URIRef(long_example["staff_member"])))
    graph.add((rdflib.URIRef(long_example["professor"]), rdflib.URIRef(ORBAC["isPreferredTo"]), rdflib.URIRef(long_example["employee"])))
    graph.add((rdflib.URIRef(long_example["director"]), rdflib.URIRef(ORBAC["isPreferredTo"]), rdflib.URIRef(long_example["employee"])))
    graph.add((rdflib.URIRef(long_example["engineer"]), rdflib.URIRef(ORBAC["isPreferredTo"]), rdflib.URIRef(long_example["employee"])))
    graph.add((rdflib.URIRef(long_example["post_doc"]), rdflib.URIRef(ORBAC["isPreferredTo"]), rdflib.URIRef(long_example["employee"])))
    graph.add((rdflib.URIRef(long_example["professor"]), rdflib.URIRef(ORBAC["isPreferredTo"]), rdflib.URIRef(long_example["post_doc"])))
    graph.add((rdflib.URIRef(long_example["professor"]), rdflib.URIRef(ORBAC["isPreferredTo"]), rdflib.URIRef(long_example["PhD_student"])))
    graph.add((rdflib.URIRef(long_example["full_professor"]), rdflib.URIRef(ORBAC["isPreferredTo"]), rdflib.URIRef(long_example["professor"])))
    graph.add((rdflib.URIRef(long_example["associate_professor"]), rdflib.URIRef(ORBAC["isPreferredTo"]), rdflib.URIRef(long_example["professor"])))
    graph.add((rdflib.URIRef(long_example["secondee"]), rdflib.URIRef(ORBAC["isPreferredTo"]), rdflib.URIRef(long_example["employee"])))
    graph.add((rdflib.URIRef(long_example["dean"]), rdflib.URIRef(ORBAC["isPreferredTo"]), rdflib.URIRef(long_example["employee"])))
    graph.add((rdflib.URIRef(long_example["researcher"]), rdflib.URIRef(ORBAC["isPreferredTo"]), rdflib.URIRef(long_example["employee"])))
    graph.add((rdflib.URIRef(long_example["PhD_student"]), rdflib.URIRef(ORBAC["isPreferredTo"]), rdflib.URIRef(long_example["employee"])))
    graph.add((rdflib.URIRef(long_example["wp_leader"]), rdflib.URIRef(ORBAC["isPreferredTo"]), rdflib.URIRef(long_example["secondee"])))
    graph.add((rdflib.URIRef(long_example["team_leader"]), rdflib.URIRef(ORBAC["isPreferredTo"]), rdflib.URIRef(long_example["wp_leader"])))
    graph.add((rdflib.URIRef(long_example["coordinator"]), rdflib.URIRef(ORBAC["isPreferredTo"]), rdflib.URIRef(long_example["team_leader"])))
    graph.add((rdflib.URIRef(long_example["project_officer"]), rdflib.URIRef(ORBAC["isPreferredTo"]), rdflib.URIRef(long_example["team_leader"])))
    """

test_data = generate_test_cases()
print(f"Generated {len(test_data)} example test cases.")

graph = rdflib.Graph()
base_ontology_path = "ontology/orbac.owl"
graph.parse(base_ontology_path, format="xml")

#example_path = "ontology/examples/secondee-example02.owl"
#graph.parse(example_path, format='application/rdf+xml')
add_generated_to_graph(graph, test_data)
graph.serialize(destination="ontology/examples/supports_1to3_example_50.owl",format="application/rdf+xml")

"""V1:
The combination phdStudent6, edit, report7 should return True.
The combination professor5, create, report6 should return True.
V3:ALL"""