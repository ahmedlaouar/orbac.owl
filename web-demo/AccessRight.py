from rdflib import RDF, URIRef

class AccessType:
    def __init__(self, name, org_perm, r_perm, a_perm, v_perm, c_perm, type):
        self.name = name
        self.accessTypeOrganisation = org_perm
        self.accessTypeRole = r_perm
        self.accessTypeActivity = a_perm
        self.accessTypeView = v_perm
        self.accessTypeContext = c_perm
        self.type = type

    def __eq__(self, __value: object) -> bool:
        if not isinstance(__value, AccessType):
            return False
        return (self.accessTypeOrganisation == __value.accessTypeOrganisation and
                self.accessTypeRole == __value.accessTypeRole and
                self.accessTypeActivity == __value.accessTypeActivity and
                self.accessTypeView == __value.accessTypeView and
                self.accessTypeContext == __value.accessTypeContext)

    def __hash__(self):
        return hash((self.accessTypeOrganisation, 
                     self.accessTypeRole, 
                     self.accessTypeActivity, 
                     self.accessTypeView, 
                     self.accessTypeContext))
    @classmethod
    def create_from_graph(cls, graph, uri, name, type):
        """"""
        accessTypeOrganisation = URIRef("https://raw.githubusercontent.com/ahmedlaouar/orbac.owl/refs/heads/main/ontology/orbac.owl#accessTypeOrganisation")
        accessTypeRole = URIRef("https://raw.githubusercontent.com/ahmedlaouar/orbac.owl/refs/heads/main/ontology/orbac.owl#accessTypeRole")
        accessTypeActivity = URIRef("https://raw.githubusercontent.com/ahmedlaouar/orbac.owl/refs/heads/main/ontology/orbac.owl#accessTypeActivity")
        accessTypeView = URIRef("https://raw.githubusercontent.com/ahmedlaouar/orbac.owl/refs/heads/main/ontology/orbac.owl#accessTypeView")
        accessTypeContext = URIRef("https://raw.githubusercontent.com/ahmedlaouar/orbac.owl/refs/heads/main/ontology/orbac.owl#accessTypeContext")
        
        for _, _, o in graph.triples((URIRef(uri+name), accessTypeOrganisation, None)):
            org = o.fragment
        for _, _, o in graph.triples((URIRef(uri+name), accessTypeRole, None)):
            role = o.fragment
        for _, _, o in graph.triples((URIRef(uri+name), accessTypeActivity, None)):
            activity = o.fragment
        for _, _, o in graph.triples((URIRef(uri+name), accessTypeView, None)):
            view = o.fragment
        for _, _, o in graph.triples((URIRef(uri+name), accessTypeContext, None)):
            context = o.fragment
        return cls(name, org, role, activity, view, context, type)
    def verbalise(self):
        """"""
        return f"The organization {self.accessTypeOrganisation} grants the role {self.accessTypeRole} the {self.type} to perform the activity {self.accessTypeActivity} on the view {self.accessTypeView} if the context {self.accessTypeContext} holds,"
    def get_predicate(self):
        return f"{self.type}({self.accessTypeOrganisation},{self.accessTypeRole},{self.accessTypeActivity},{self.accessTypeView},{self.accessTypeContext})"

class Employ:
    def __init__(self, name, org, r, s):
        self.name = name
        self.employesEmployee = s
        self.employesEmployer = org
        self.employesRole = r

    def __eq__(self, __value: object) -> bool:
        if not isinstance(__value, Employ):
            return False
        return (self.employesEmployer == __value.employesEmployer and
                self.employesRole == __value.employesRole and
                self.employesEmployee == __value.employesEmployee)

    def __hash__(self):
        return hash((self.employesEmployer, 
                     self.employesRole, 
                     self.employesEmployee))
    @classmethod
    def create_from_graph(cls, graph, uri, name, s):
        """"""
        employesEmployer = URIRef("https://raw.githubusercontent.com/ahmedlaouar/orbac.owl/refs/heads/main/ontology/orbac.owl#employesEmployer")
        employesRole = URIRef("https://raw.githubusercontent.com/ahmedlaouar/orbac.owl/refs/heads/main/ontology/orbac.owl#employesRole")
        
        for _, _, o in graph.triples((URIRef(uri+name), employesRole, None)):
            role = o.fragment
        for _, _, o in graph.triples((URIRef(uri+name), employesEmployer, None)):
            organisation = o.fragment
        return cls(name, organisation, role, s)
    def verbalise(self):
        """"""
        return f"The organisation {self.employesEmployer} employes {self.employesEmployee} in the role {self.employesRole}, "
    def get_predicate(self):
        return f"Employ({self.employesEmployer},{self.employesRole},{self.employesEmployee})"

class Use:
    def __init__(self, name, org, v, o):
        self.name = name
        self.usesEmployer = org
        self.usesObject = o
        self.usesView = v

    def __eq__(self, __value: object) -> bool:
        if not isinstance(__value, Use):
            return False
        return (self.usesEmployer == __value.usesEmployer and
                self.usesObject == __value.usesObject and
                self.usesView == __value.usesView)

    def __hash__(self):
        return hash((self.usesEmployer, 
                     self.usesObject, 
                     self.usesView))
    @classmethod
    def create_from_graph(cls, graph, uri, name, s):
        """"""
        usesEmployer = URIRef("https://raw.githubusercontent.com/ahmedlaouar/orbac.owl/refs/heads/main/ontology/orbac.owl#usesEmployer")
        usesView = URIRef("https://raw.githubusercontent.com/ahmedlaouar/orbac.owl/refs/heads/main/ontology/orbac.owl#usesView")
        
        for _, _, o in graph.triples((URIRef(uri+name), usesView, None)):
            view = o.fragment
        for _, _, o in graph.triples((URIRef(uri+name), usesEmployer, None)):
            org = o.fragment
        return cls(name, org, view, s)
    def verbalise(self):
        """"""
        return f"The organisation {self.usesEmployer} uses {self.usesObject} in the view {self.usesView}, "
    def get_predicate(self):
        return f"Use({self.usesEmployer},{self.usesView},{self.usesObject})"

class Consider:
    def __init__(self, name, org, a, alpha):
        self.name = name
        self.considersOrganisation = org
        self.considersAction = alpha
        self.considersActivity = a

    def __eq__(self, __value: object) -> bool:
        if not isinstance(__value, Consider):
            return False
        return (self.considersOrganisation == __value.considersOrganisation and
                self.considersAction == __value.considersAction and
                self.considersActivity == __value.considersActivity)

    def __hash__(self):
        return hash((self.considersOrganisation, 
                     self.considersAction, 
                     self.considersActivity))
    @classmethod
    def create_from_graph(cls, graph, uri, name, s):
        """"""
        considersOrganisation = URIRef("https://raw.githubusercontent.com/ahmedlaouar/orbac.owl/refs/heads/main/ontology/orbac.owl#considersOrganisation")
        considersActivity = URIRef("https://raw.githubusercontent.com/ahmedlaouar/orbac.owl/refs/heads/main/ontology/orbac.owl#considersActivity")
        
        for _, _, o in graph.triples((URIRef(uri+name), considersActivity, None)):
            activity = o.fragment
        for _, _, o in graph.triples((URIRef(uri+name), considersOrganisation, None)):
            org = o.fragment
        return cls(name, org, activity, s)
    def verbalise(self):
        """"""
        return f"The organisation {self.considersOrganisation} considers {self.considersAction} as a {self.considersActivity} activity, "
    def get_predicate(self):
        return f"Consider({self.considersOrganisation},{self.considersActivity},{self.considersAction})"

class Define:
    def __init__(self, name, org, s, a, o, c):
        self.name = name
        self.definesOrganisation = org
        self.definesSubject = s
        self.definesAction = a
        self.definesObject = o
        self.definesContext = c

    def __eq__(self, __value: object) -> bool:
        if not isinstance(__value, Define):
            return False
        return (self.definesOrganisation == __value.definesOrganisation and
                self.definesSubject == __value.definesSubject and
                self.definesAction == __value.definesAction and
                self.definesObject == __value.definesObject and
                self.definesContext == __value.definesContext)

    def __hash__(self):
        return hash((self.definesOrganisation, 
                     self.definesSubject, 
                     self.definesAction, 
                     self.definesObject, 
                     self.definesContext))
    @classmethod
    def create_from_graph(cls, graph, uri, name, subject, action, obj):
        """"""
        definesOrganisation = URIRef("https://raw.githubusercontent.com/ahmedlaouar/orbac.owl/refs/heads/main/ontology/orbac.owl#definesOrganisation")
        definesContext = URIRef("https://raw.githubusercontent.com/ahmedlaouar/orbac.owl/refs/heads/main/ontology/orbac.owl#definesContext")
        
        for _, _, o in graph.triples((URIRef(uri+name), definesContext, None)):
            context = o.fragment
        for _, _, o in graph.triples((URIRef(uri+name), definesOrganisation, None)):
            org = o.fragment
        return cls(name, org, subject, action , obj, context)
    def verbalise(self):
        """"""
        return f"The context {self.definesContext} holds between {self.definesSubject}, {self.definesAction}, and {self.definesObject} in the organisation {self.definesOrganisation}, "
    def get_predicate(self):
        return f"Define({self.definesOrganisation},{self.definesSubject},{self.definesAction},{self.definesObject},{self.definesContext})"

class subOrganisationOf:
    def __init__(self, org_1, org_2):
        self.org_1 = org_1
        self.org_2 = org_2

    def __eq__(self, __value: object) -> bool:
        if not isinstance(__value, subOrganisationOf):
            return False
        return (self.org_1 == __value.org_1 and
                self.org_2 == __value.org_2)
    
    def __hash__(self):
        return hash((self.org_1, self.org_2))
    
class AccessRight:
    def __init__(self, subject, action, obj, graph, uri):
        self.subject = subject
        self.action = action
        self.obj = obj
        self.graph = graph
        self.uri = uri
        self.get_hierarchical_relations()
        self.permission_supports = [] # a list of dicts, each dict represents the elements of a support according to their classes
        self.prohibition_supports = [] # a list of dicts, each dict represents the elements of a support according to their classes
        self.get_supports(0)
        self.get_supports(1)
        self.outcome = self.check_acceptance()

    def get_supports(self, accessType=0):
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
            query = query_template.format(example_uri=self.uri, subject=self.subject, action=self.action, object=self.obj)            
            results = self.graph.query(query)

        for row in results: #?permission ?employ ?consider ?use ?define
            current_support = {}
            access_type_name = row[0].fragment
            employ_name = row[1].fragment
            consider_name = row[2].fragment
            use_name = row[3].fragment
            define_name = row[4].fragment
            
            if accessType == 0:
                access_type = AccessType.create_from_graph(self.graph, self.uri, access_type_name, "Permission")
            else:
                access_type = AccessType.create_from_graph(self.graph, self.uri, access_type_name, "Prohibition")
            employ = Employ.create_from_graph(self.graph, self.uri, employ_name, self.subject)
            consider = Consider.create_from_graph(self.graph, self.uri, consider_name, self.action)
            use = Use.create_from_graph(self.graph, self.uri, use_name, self.obj)
            define = Define.create_from_graph(self.graph, self.uri, define_name, self.subject, self.action, self.obj)
            current_support['access_type'] = access_type
            current_support['employ'] = employ
            current_support['consider'] = consider
            current_support['use'] = use
            current_support['define'] = define
            
            if accessType == 0: 
                self.permission_supports.append(current_support.copy())
            else:
                self.prohibition_supports.append(current_support.copy())
        
        return

    def verbalise_support(self, support):
        """"""
        text = ""
        for element in support.values():
            text += element.verbalise()
        return text

    def verbalise_supports(self):
        """"""
        text = """2. **Supports of Permission:** List of the elements that compose the permission supports: """
        i = 1
        for support in self.permission_supports:
            text += "(support "+str(i)+"): " + self.verbalise_support(support)
            i += 1
        text += """3. **Supports of Prohibition:** List of the elements composing the prohibition support: """
        i = 1
        for support in self.prohibition_supports:
            text += "(support "+str(i)+"): " + self.verbalise_support(support)
            i += 1
        return text
        
    def verbalise_preferences(self):
        """"""
        preference_text = "4. **Preferences Between the Elements:**"
        reduced_permission_supports = [(support["employ"], support["define"]) for support in self.permission_supports]
        reduced_prohibition_supports = [(support["employ"], support["define"]) for support in self.prohibition_supports]
        for perm_employ, perm_define in reduced_permission_supports:
            for proh_employ, proh_define in reduced_prohibition_supports:
                if self.is_strictly_preferred(perm_employ.name, proh_employ.name):
                    preference_text += f"The relation ``{perm_employ.verbalise()}`` is preferred to ``{proh_employ.verbalise()}`` because: {perm_employ.employesRole} is preferred to {proh_employ.employesRole}. "
                else:
                    preference_text += f"The relation ``{perm_employ.verbalise()}`` is not preferred to ``{proh_employ.verbalise()}`` because: {perm_employ.employesRole} is not preferred to {proh_employ.employesRole}. "
                if self.is_strictly_preferred(perm_define.name, proh_define.name):
                    preference_text += f"The relation ``{perm_define.verbalise()}`` is preferred to ``{proh_define.verbalise()}`` because: {perm_define.definesContext} is preferred to {proh_define.definesContext}. "
                else:
                    preference_text += f"The relation ``{perm_define.verbalise()}`` is not preferred to ``{proh_define.verbalise()}`` because: {perm_define.definesContext} is not preferred to {proh_define.definesContext}. "
        
        return preference_text

    def get_logic_explanations(self, root=False):
        return self.get_support_logic_explanations()
    
    def get_root_logic_explanations(self):
        """"""
        explanations = {}
        if self.outcome :
            for prohibition_support in self.prohibition_supports:
                if (prohibition_support['employ'].employesRole,prohibition_support['define'].definesContext) not in explanations:
                    explanations[(prohibition_support['employ'].employesRole,prohibition_support['define'].definesContext)] = []
                for permission_support in self.permission_supports:
                    if self.is_strictly_preferred(permission_support['employ'].name, prohibition_support['employ'].name) and self.is_strictly_preferred(permission_support['define'].name, prohibition_support['define'].name):
                        explanations[(prohibition_support['employ'].employesRole,prohibition_support['define'].definesContext)].append((permission_support['employ'].employesRole,permission_support['define'].definesContext))
            return explanations
        else:
            for prohibition_support in self.prohibition_supports:
                if (prohibition_support['employ'].employesRole,prohibition_support['define'].definesContext) not in explanations:
                    explanations[(prohibition_support['employ'].employesRole,prohibition_support['define'].definesContext)] = []
                dominated = False
                for permission_support in self.permission_supports:
                    if self.is_strictly_preferred(permission_support['employ'].name, prohibition_support['employ'].name) and self.is_strictly_preferred(permission_support['define'].name, prohibition_support['define'].name):
                        dominated = True
                        break
                    else:
                        explanations[(prohibition_support['employ'].employesRole,prohibition_support['define'].definesContext)].append((permission_support['employ'].employesRole,permission_support['define'].definesContext))
                if dominated:
                    explanations.pop((prohibition_support['employ'].employesRole,prohibition_support['define'].definesContext), None)
            return explanations
    
    def get_support_logic_explanations(self):
        """"""
        explanations = {}
        if self.outcome :
            for prohibition_support in self.prohibition_supports:
                if (prohibition_support['employ'],prohibition_support['define']) not in explanations:
                    explanations[(prohibition_support['employ'],prohibition_support['define'])] = []
                for permission_support in self.permission_supports:
                    if self.is_strictly_preferred(permission_support['employ'].name, prohibition_support['employ'].name) and self.is_strictly_preferred(permission_support['define'].name, prohibition_support['define'].name):
                        explanations[(prohibition_support['employ'],prohibition_support['define'])].append((permission_support['employ'],permission_support['define']))
            return explanations
        else:
            for prohibition_support in self.prohibition_supports:
                if (prohibition_support['employ'],prohibition_support['define']) not in explanations:
                    explanations[(prohibition_support['employ'],prohibition_support['define'])] = []
                dominated = False
                for permission_support in self.permission_supports:
                    if self.is_strictly_preferred(permission_support['employ'].name, prohibition_support['employ'].name) and self.is_strictly_preferred(permission_support['define'].name, prohibition_support['define'].name):
                        dominated = True
                        break
                    else:
                        explanations[(prohibition_support['employ'],prohibition_support['define'])].append((permission_support['employ'],permission_support['define']))
                if dominated:
                    explanations.pop((prohibition_support['employ'],prohibition_support['define']), None)
            return explanations
        
    def verbalise_logic_explanations(self, explanations):
        logical_explanations = ""
        for prohibition, list_permissions in explanations.items():
            for permission in list_permissions:
                employ_proh, define_proh = prohibition
                employ_perm, define_perm = permission
                if self.outcome:
                    logical_explanations += f"({employ_perm.employesRole}, {define_perm.definesContext}) > ({employ_proh.employesRole}, {define_proh.definesContext}), "
                else:
                    logical_explanations += f"({employ_perm.employesRole}, {define_perm.definesContext}) !> ({employ_proh.employesRole}, {define_proh.definesContext}), "
        return logical_explanations

    def is_strictly_preferred(self, member1, member2):
        
        query_template = """PREFIX orbac-owl: <https://raw.githubusercontent.com/ahmedlaouar/orbac.owl/refs/heads/main/ontology/orbac.owl#>
        PREFIX : <{example_uri}>
        # query to check dominance of member1 over member2
        ASK {{
        :{member1} orbac-owl:isPreferredTo :{member2} .
        FILTER NOT EXISTS {{
            :{member2} orbac-owl:isPreferredTo :{member1} .
        }}
        }}"""

        query = query_template.format(example_uri=self.uri, member1=member1, member2=member2)

        results = self.graph.query(query)
        try:
            first_result = next(iter(results))
            if first_result:
                return True
            else:
                return False
        except StopIteration:
            print("No query results found.")
            return False
        
    def check_dominance(self, subset1, subset2):
        for member1 in subset1:
            dominates_at_least_one = False        
            for member2 in subset2:
                if self.is_strictly_preferred(member1, member2):
                    dominates_at_least_one = True
                    break 
            if not dominates_at_least_one:
                return False
        return True

    def check_acceptance(self):
        permission_supports = self.permission_supports
        prohibition_supports = self.prohibition_supports
        
        if len(permission_supports) == len(prohibition_supports) == 0:
            return False
        elif len(permission_supports) == 0:
            return False
        elif len(prohibition_supports) == 0:
            return True
        else:
            reduced_permission_supports = [[support["employ"].name, support["define"].name] for support in permission_supports]
            reduced_prohibition_supports = [[support["employ"].name, support["define"].name] for support in prohibition_supports]
            accepted = True
            for proh_support in reduced_prohibition_supports:
                conflict_supported = False
                for perm_support in reduced_permission_supports:
                    if self.check_dominance(perm_support, proh_support):
                        conflict_supported = True
                        break
                if not conflict_supported:
                    return False
            return accepted
        
    def verbalise_outcome(self):
        """"""
        decision = "**The Decision:** The outcome of the logical inference is that: "
        if self.outcome :
            decision += f"the permission for {self.subject} to perform {self.action} on {self.obj} is granted."
        else:
            decision += f"the permission for {self.subject} to perform {self.action} on {self.obj} is denied."
        return decision

    def get_hierarchical_relations(self):
        supps = list(self.compute_hierarchy_supports(0)) + list(self.compute_hierarchy_supports(1))
        for support in supps:
            if self.check_if_role_from_hierarchy(support[0].fragment, support[1].fragment):
                self.add_new_employ(support[0].fragment)
                # check if the modification is safely made on the graph overall, and thus no need to return it!

    def compute_hierarchy_supports(self, accessType = 0):
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
            query = query_template.format(example_uri= self.uri, subject=self.subject, action=self.action, object=self.obj)
            results = self.graph.query(query)
        
        return results
    
    def check_if_role_from_hierarchy(self, access_type_relation, employ_relation):
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
        query = verif_query.format(example_uri=self.uri, access_type_relation=access_type_relation, employ_relation=employ_relation)
        results = self.graph.query(query)
        return not(next(iter(results)))

    def add_new_employ(self, access_type_relation):
        accessTypeRole = URIRef("https://raw.githubusercontent.com/ahmedlaouar/orbac.owl/refs/heads/main/ontology/orbac.owl#accessTypeRole")
        accessTypeOrganisation = URIRef("https://raw.githubusercontent.com/ahmedlaouar/orbac.owl/refs/heads/main/ontology/orbac.owl#accessTypeOrganisation")
        Employ = URIRef("https://raw.githubusercontent.com/ahmedlaouar/orbac.owl/refs/heads/main/ontology/orbac.owl#Employ")
        employesEmployer = URIRef("https://raw.githubusercontent.com/ahmedlaouar/orbac.owl/refs/heads/main/ontology/orbac.owl#employesEmployer")
        employesEmploee = URIRef("https://raw.githubusercontent.com/ahmedlaouar/orbac.owl/refs/heads/main/ontology/orbac.owl#employesEmployee")
        employesRole = URIRef("https://raw.githubusercontent.com/ahmedlaouar/orbac.owl/refs/heads/main/ontology/orbac.owl#employesRole")
        isPreferredTo = URIRef("https://raw.githubusercontent.com/ahmedlaouar/orbac.owl/refs/heads/main/ontology/orbac.owl#isPreferredTo")
        
        for _, _, o in self.graph.triples((URIRef(self.uri+access_type_relation), accessTypeRole, None)):
            role = o
        for _, _, o in self.graph.triples((URIRef(self.uri+access_type_relation), accessTypeOrganisation, None)):
            organisation = o

        s = URIRef(self.uri+self.subject)
        org = organisation
        rel_name = URIRef(self.uri+"employ_"+self.subject+"_"+role.fragment)

        self.graph.add((rel_name, RDF.type, Employ))
        self.graph.add((rel_name, employesEmployer, org))
        self.graph.add((rel_name, employesRole, role))
        self.graph.add((rel_name, employesEmploee, s))

        for _, _, role2 in self.graph.triples((role, isPreferredTo, None)):
            for employ2, _, _ in self.graph.triples((None, employesRole, role2)):
                self.graph.add((rel_name, isPreferredTo, employ2))

        for role2, _, _ in self.graph.triples((None, isPreferredTo, role)):
            for employ2, _, _ in self.graph.triples((None, employesRole, role2)):
                self.graph.add((employ2, isPreferredTo, rel_name))

        return self.graph
    
    def generate_prompt(self):
        """"""
        overall_logic = """1. **Overall Logic:** Explain the condition under which access is granted. An access is granted if and only if, \
        for each support of a prohibition, there exists a corresponding support for a permission where the permission's support dominates the prohibition's. \
        Dominance means that: each element of the support of the permission is strictly preferred to at least one element of the support of the prohibition. \
        Here are the different elements which compose the decision: """
        request = "**Request for Explanation:** Using the provided logic, supports, and preferences, please explain why the decision was made to grant or deny access in this specific case.\
             The explanation must contain the following elements: the used decision rule, the outcome decision, and the different relations and preferences leading to the decision. "
        text = overall_logic
        text += self.verbalise_supports()
        text += self.verbalise_preferences()
        text += self.verbalise_outcome()
        text += request
        return text