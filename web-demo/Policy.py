from logzero import logger
from rdflib import OWL, RDF, Graph

class Policy:
    def __init__(self, instance_file_path):
        logger.debug('Loading Policy.')
        self.graph = Graph()
        # Paths to the base ontology and the instance file
        base_ontology_path = "ontology/orbac.owl"        
        # Parse the base ontology into the graph
        self.graph.parse(base_ontology_path, format="xml")
        # Parse the instance file into the same graph
        self.graph.parse(instance_file_path, format="xml")
        for s, p, o in self.graph.triples((None, RDF.type, OWL.Ontology)):
            base_uri = s
            #break  # Assuming there is only one owl:Ontology
        if base_uri:
            self.example_uri = base_uri
        else:
            logger.debug("Base URI not found in the graph.")
        if self.example_uri[-1] != "#":
            self.example_uri += "#"
        logger.debug('Ready.')

    def strip_prefix(self, uri):
        return uri.split('#')[-1]
    
    def get_concrete_concepts(self):
        query = """PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                PREFIX : <https://raw.githubusercontent.com/ahmedlaouar/orbac.owl/refs/heads/main/ontology/orbac.owl#> # Adjust the base URI as necessary

                SELECT ?s ?alpha ?o {{
                    ?relation rdf:type :Define .
                    ?relation :definesSubject ?s .
                    ?relation :definesAction ?alpha .
                    ?relation :definesObject ?o .
                }}"""        
        results = self.graph.query(query)
        return results
    
    def select_combination(self):
        # randomly get a subject, action and object from the used example
        define_rules = self.get_concrete_concepts()
        define_rules_data = [
            {"Subject": self.strip_prefix(row[0]), 
            "Action": self.strip_prefix(row[1]), 
            "Object": self.strip_prefix(row[2])}
            for row in define_rules
        ]

        # Remove duplicates
        combinations = {tuple(d.values()) for d in define_rules_data}
        combinations = [dict(zip(["Subject", "Action", "Object"], comb)) for comb in combinations]        
        random_row = combinations.sample(n=1)
        subject, action, obj = random_row["Subject"].values[0], random_row["Action"].values[0], random_row["Object"].values[0]
        return subject, action, obj
    
    def get_combinations(self):
        """retruens all the combinations of subject, action and object without duplicates"""
        # Convert to list of dictionaries and apply strip_prefix
        define_rules = self.get_concrete_concepts()
        define_rules_data = [
            {"Subject": self.strip_prefix(row[0]), 
            "Action": self.strip_prefix(row[1]), 
            "Object": self.strip_prefix(row[2])}
            for row in define_rules
        ]

        # Remove duplicates
        combinations = {tuple(d.values()) for d in define_rules_data}
        combinations = [dict(zip(["Subject", "Action", "Object"], comb)) for comb in combinations]
        return combinations
    
    def get_abstract_rules(self):
        abstract_rules_query_path = 'queries.sparql/get_access_types.sparql'

        with open(abstract_rules_query_path, 'r') as file:
            query = file.read()
        
        results = self.graph.query(query)

        return results

    def get_connection_rules(self):
        connection_rules_query_path = 'queries.sparql/get_connection_rules.sparql'

        with open(connection_rules_query_path, 'r') as file:
            query = file.read()
        
        results = self.graph.query(query)

        return results

    def get_define_rules(self):
        connection_rules_query_path = 'queries.sparql/get_define_rules.sparql'

        with open(connection_rules_query_path, 'r') as file:
            query = file.read()
        
        results = self.graph.query(query)

        return results
    
    def check_consistency(self):
        consistency_checking_query_path = "queries.sparql/inconsistency_checking.sparql"
        with open(consistency_checking_query_path, 'r') as file:
            query = file.read()

        results = self.graph.query(query)
        try:
            first_result = next(iter(results))
            if first_result:
                return False
            else: 
                return True
        except StopIteration:
            print("No query results found.")
            return True

    def compute_conflicts(self):
        conflicts_query_path = 'queries.sparql/compute_conflicts.sparql'

        with open(conflicts_query_path, 'r') as file:
            query = file.read()

        results = self.graph.query(query)

        return results