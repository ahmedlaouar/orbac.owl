from rdflib import Graph, Namespace, URIRef, Literal
from rdflib.namespace import RDF, RDFS, OWL
from urllib.parse import urlparse
from simplenlg.framework import NLGFactory, Lexicon
from simplenlg.realiser.english import Realiser
import textstat
import nltk
from nltk.stem import WordNetLemmatizer
import numpy as np
from acceptance import *
#from util import *

# Initialize the lexicon, factory, and realiser
lexicon = Lexicon.getDefaultLexicon()
nlgFactory = NLGFactory(lexicon)
realiser = Realiser(lexicon) 

# ------------------------------------------ begin classes ------------------------------------------ #
class ResultWithExplanations:
    def __init__(self, graph, example_uri, subject, action, obj):
        self.subject = subject
        self.action = action
        self.obj = obj
        self.results = []
        self.accesses = []
        self.text =""
        self.perm_supports = compute_supports(graph, example_uri, subject, action, obj, 0)       
        self.proh_supports = compute_supports(graph, example_uri, subject, action, obj, 1)     
        self.graph = graph
        self.example_uri = example_uri

    def __str__(self): 
        return self.text

    def getAccessResultArray(self):
        resultsStr = []
        for result in self.results:
            resultsStr.append("Access("+self.subject+","+self.action+","+self.obj+") = "+result)
        return resultsStr
    
    def getPermissionAccesses(self):
        permissions = []
        for access in self.accesses:
            if access.accessType == "Permission":
                permissions.append(access)
        return permissions

    def getProhibitionAccesses(self):
        prohibitions = []
        for access in self.accesses:
            if access.accessType == "Prohibition":
                prohibitions.append(access)
        return prohibitions

    def getAccessResultText(self):
        output = ""
        for str in self.getAccessResultArray():
            output += str+"\n"
        return output
    
    def getLogicBasedSupports(self):
        text= "Supports\n"
        text_perm = "S_perm = {"
        for perm_support in self.perm_supports:
            for value in perm_support:
                text_perm += value.fragment+", "
        if (text_perm.endswith(", ")):
            text_perm = text_perm[0:len(text_perm)-2]        
        text_perm+="}\n"

        text_proh = "S_proh = {"
        for proh_support in self.proh_supports:
            for value in proh_support:
                text_proh += value.fragment+", "
        if (text_proh.endswith(", ")):
            text_proh = text_proh[0:len(text_proh)-2]        
        text_proh+="}\n"

        return text + text_perm + text_proh
    

    def getContrastiveExplanation(self): # needs to be well formulated in the future 
        # [This should be based on the notion of supports not on a bare comparison between the permission and the prohibition.]
        
        text = ""

        for access in self.accesses:
            if access.accessType == "Prohibition": # no need to separate but it was just like that before
                text += access.getLogicalExplanationDetailsStr()+"\n"
                
            if access.accessType == "Permission": # no need to separate but it was just like that before
                text += access.getLogicalExplanationDetailsStr()+"\n"
                
        text+= self.getLogicBasedSupports()
        diff_supports = difference_supports(self.graph, self.example_uri, self.subject, self.action, self.obj)
        text_supports_logic_based = get_diff_supports_logic_based(diff_supports) 
        text += text_supports_logic_based+"\n"
       
        return text
    
    def is_strictly_preferred_with_details(self, example_uri, member1, member2):
        dominance_query_path = "queries.sparql/dominance_query.sparql"
        with open(dominance_query_path, 'r') as file:
            query_template = file.read()

        query = query_template.format(example_uri=example_uri, member1=member1, member2=member2)

        results = self.graph.query(query)
        try:
            first_result = next(iter(results))
            if first_result:
                detail = member1+">"+member2
                return (True,detail)
            else: 
                detail = member2+">"+member1
                return (False,detail)
        except StopIteration:
            # print("No query results found.")
            return (False,None)

    def check_dominance_with_details(self, example_uri, subset1, subset2):
        preference = (False,[])
        detail_list = []
        for member1 in subset1:
            dominates_at_least_one = False
            for member2 in subset2:   
                pref = self.is_strictly_preferred_with_details(example_uri, member1, member2)
                if pref[0]:
                    detail_list.append(pref[1])
                    preference = (pref[0], detail_list)
                    dominates_at_least_one = True                
                    break 
            if not dominates_at_least_one:
                return (False,[])
        return preference

    def check_acceptance_with_details(self, example_uri):
        permission_supports = self.perm_supports
        prohibition_supports = self.proh_supports
        
        stripped_prohibition_supports = []
        for proh_support in prohibition_supports:
            stripped_prohibition_supports.append(tuple(strip_prefix(str(uri)) for uri in proh_support))
        stripped_prohibition_supports = list(set(stripped_prohibition_supports))
        stripped_permission_supports = []
        for perm_support in permission_supports:
            stripped_permission_supports.append(tuple(strip_prefix(str(uri)) for uri in perm_support))
        stripped_permission_supports = list(set(stripped_permission_supports))

        accepted = True
        detail = []
        for proh_support in stripped_prohibition_supports:
            conflict_supported = False
            for perm_support in stripped_permission_supports:
                dominance = self.check_dominance_with_details(example_uri, perm_support, proh_support)
                if dominance[0]:
                    conflict_supported = True
                    detail = dominance[1]
                    break
            if not conflict_supported:
                return (False,[])
        return (accepted,detail)

    def getOutcomeConflict(self):
        text = "Outcome\n"
        outcome = self.check_acceptance_with_details(self.example_uri)                

        if outcome[0]:
            outcome_logic_list = outcome[1]
            if len(outcome_logic_list) == 0:
                outcome_logic = "there is no support for prohibition."
            else:
                outcome_logic = []
                for outcome_logic_raw in outcome_logic_list:
                    outcome_logic.append(self.getLogicExplanationPreferance(outcome_logic_raw)) # orbac form

                text+="Is-permitted("+self.subject+","+self.action+","+self.obj+") because " #+outcome_logic+"\n"
                for outcome_logic_element in outcome_logic:
                    text+= outcome_logic_element+", and "
                text = text[:-6] + "\n"

            #outcome_logic_raw = outcome[1] # X>Y
            #if outcome_logic_raw == None:
            #    outcome_logic = "there is no support for prohibition."
            #else:
            #    outcome_logic = self.getLogicExplanationPreferance(outcome_logic_raw) # orbac form

            #text+="Is-permitted("+self.subject+","+self.action+","+self.obj+") because "+outcome_logic+"\n"
            # if outcome_logic_raw != None: # This was just a test if verbalisation related the preference works well
            #     text+=self.getNaturalLanguagePreference( outcome_logic_raw)

        else:
            text+="Is-prohibited("+self.subject+","+self.action+","+self.obj+")"
        return text
    
    def getLogicExplanationPreferance(self, preference):
        # print(preference)
        variables = preference.split(sep='>')
        return "<"+variables[0]+", orbac:isPreferredTo, "+variables[1]+">"
    
    def getNaturalLanguagePreference(self, preference):
        variables = preference.split(sep='>')
        text = "'"+variable_verbalisation(self.graph, self.example_uri, variables[0])+"' is preferred to '"+variable_verbalisation(self.graph, self.example_uri, variables[1])+"'"
        return text
        
class Access:
    def __init__(self):
        self.accessType = ""

    def init(self, accessType, access, employ, use, consider, define, s, o, v, a, alpha, c, r, org, org2):
        self.accessType = accessType
        self.access = access
        self.employ = employ
        self.use = use
        self.consider = consider
        self.define = define
        self.subject = s
        self.obj = o
        self.view = v
        self.activity = a
        self.action = alpha
        self.context = c
        self.role = r
        self.org = org
        self.org2 = org2
        
        if (self.accessType == "Prohibition"):
            self.outcome = "Is-prohibited"
        else:
            self.outcome = "Is-permitted"

    def initFromCSV(self, csv):
        elements = csv.split(";")
        self.accessType = elements[0]
        self.access = elements[1]
        self.employ = elements[2]
        self.use = elements[3]
        self.consider = elements[4]
        self.define = elements[5]
        self.subject = elements[6]
        self.obj = elements[7]
        self.view = elements[8]
        self.activity = elements[9]
        self.action = elements[10]
        self.context = elements[11]
        self.role = elements[12]
        self.org = elements[13]
        org2 = elements[14]
        self.org2 = org2.split("\n")[0] #org2[:len(org2)-2] 
        if (self.accessType == "Prohibition"):
            self.outcome = "Is-prohibited"
        else:
            self.outcome = "Is-permitted"

    def logicalExplanation(self):        
        explanations=[]
        explanations.append(self.accessType+"("+self.org+","+self.role+","+self.activity+","+self.view+","+self.context+") $\\wedge$")
        explanations.append("Employ("+self.org+","+self.subject+","+self.role+") $\\wedge$")
        explanations.append("Use("+self.org+","+self.obj+","+self.view+") $\\wedge$")
        explanations.append("Consider("+self.org+","+self.action+","+self.activity+") $\\wedge$")
        explanations.append("Define("+self.org+","+self.subject+","+self.action+","+self.view+","+self.context+") $\\wedge$")
        explanations.append("SubOrganisationOf"+"("+self.org+","+self.org2+") $\\models$")
        explanations.append(self.outcome+"("+self.subject+","+self.action+","+self.obj+")")

        return explanations
    
    def logicalExplanationDetails(self):        
        explanations=[]
        explanations.append(self.accessType+"("+self.org+","+self.role+","+self.activity+","+self.view+","+self.context+") $\\wedge$")
        explanations.append(self.employ+"("+self.org+","+self.subject+","+self.role+") $\\wedge$")
        explanations.append(self.use+"("+self.org+","+self.obj+","+self.view+") $\\wedge$")
        explanations.append(self.consider+"("+self.org+","+self.action+","+self.activity+") $\\wedge$")
        explanations.append(self.define+"("+self.org+","+self.subject+","+self.action+","+self.view+","+self.context+") $\\wedge$")
        explanations.append("SubOrganisationOf"+"("+self.org+","+self.org2+") $\\models$")
        explanations.append(self.outcome+"("+self.subject+","+self.action+","+self.obj+")")

        return explanations
    
    def getCSV(self):
        csv = self.accessType+";"+ self.access+";"+ self.employ+";"+self.use+";"+self.consider+";"+self.define+";"+self.subject+";"+self.obj+";"+self.view+";"+self.activity+";"+self.action+";"+self.context+";"+self.role+";"+self.org+";"+self.org2
        return csv

    
    def __str__(self):
       return self.getLogicalExplanationDetailsStr()

    def getLogicalExplanationDetailsStr(self):
        str = ""
        for explanation in self.logicalExplanationDetails():
            str+=explanation+"\n"
        return str

class Explanations:
    def __init__(self, graph, example_uri, accessesPermission, accessesProhibition, lemmatizer):
        self.accessesPermission = accessesPermission
        self.accessesProhibition = accessesProhibition
        self.graph = graph
        self.example_uri = example_uri
        self.lemmatizer = lemmatizer

    def getAccessFor(self, subject, action, obj, accessType):
        results = []
        accesses = []
        if (accessType == "Permission"):
            accesses = self.accessesPermission
        else:
            if (accessType == "Prohibition"):
                accesses = self.accessesProhibition
            else:
                return
        for access in accesses:
            if (access.subject == subject and access.action == action and access.obj == obj):
                results.append(access)
        return results
    
    
    def renderExplanationSimple(self, access, accessType, index):
                
        ability = "can"
        decision = "permitted"

        if (accessType == "Prohibition"):
            ability = "cannot"
            decision = "prohibited"

        # Define the input values
        subject = access.subject.capitalize().replace("_"," ")
        action = access.action.lower().replace("-"," ").replace("_"," ")
        obj = access.obj.lower().replace("-"," ").replace("_"," ")

        view = access.view.lower().replace("-"," ").replace("_"," ")
        noun_phrase = nlgFactory.createNounPhrase(view)
        noun_phrase.setSpecifier("a")
        view = realiser.realise(noun_phrase).getRealisation()

        activity = access.activity.lower().replace("-"," ").replace("_"," ")        
            
        activity_ing = to_gerund(activity, self.lemmatizer)

        action_ing = to_gerund(action, self.lemmatizer)
       
        context = access.context.lower().replace("-"," ").replace("_"," ")
        noun_phrase = nlgFactory.createNounPhrase(context)
        noun_phrase.setSpecifier("a")
        context = realiser.realise(noun_phrase).getRealisation()

        role = access.role.lower().replace("-"," ").replace("_"," ")
        noun_phrase = nlgFactory.createNounPhrase(role)
        noun_phrase.setSpecifier("a")
        role = realiser.realise(noun_phrase).getRealisation()

        organisation = access.org
        organisation2 = access.org2

        # Define the template           

        # TEMPLATE 1.0 BEGIN
    #     template = (
    # "{Subject}, "+role+" at {Organisation}, part of the {Organisation2}, "+ability+" {action} the {object}. "
    # "This is because {Subject}"
    # " is "+decision+" to {activity} "+view+" in "+context+" context, where "
    # "{object} is considered as "+view+", and "+action_ing+" it is classified as a "+activity_ing+" activity."
    #     )   
        # TEMPLATE 1.0 END
        part_result = ""
        if decision =="permitted":
            part_result = "{Subject} is "+decision+" to {activity} "
        else: # prohibitted
            part_result = "{Subject} is "+decision+" from "+activity_ing+" "

        if index == 0: # It's the first time. Therefore, a little introduction seems to be needed.
            template = (
            "{Subject}, "+role+" at {Organisation}, "+ability+" {action} the {object}. "
            +part_result+view+" in "+context+" context, where "
            "{object} is considered as "+view+", "+action_ing+" it is classified as "+activity_ing+" activity, and "
            "{Organisation} is part of the {Organisation2}. "
                )
        else:
            template = (            
            part_result+view+" in "+context+" context, where "
            "{object} is considered as "+view+", "+action_ing+" it is classified as "+activity_ing+" activity, and "
            "{Organisation} is part of the {Organisation2}. "
                )

        # Fill in the template
        output = template.format(
            Subject=subject,
            action=action,
            object=obj,
            view=view,
            activity=activity,
            context=context,
            role=role,
            Organisation=organisation,
            Organisation2=organisation2, 

        )
        # Return the result        
        return output
    
    def renderExplanationConflict(self, resultWithExplanaitons: ResultWithExplanations):

        accessPermissions = resultWithExplanaitons.getPermissionAccesses()
        accessProhibitions = resultWithExplanaitons.getProhibitionAccesses()

        # Define the input values
        subject = resultWithExplanaitons.accesses[0].subject.capitalize().replace("_"," ")
        action = resultWithExplanaitons.accesses[0].action.lower().replace("-"," ").replace("_"," ")
        obj = resultWithExplanaitons.accesses[0].obj.lower().replace("-"," ").replace("_"," ")
        # We use [0] because so far it doesn't matter if it is a prohibition or a permission. subject, action and obj are always the same.
        
        # ------ SIMPLE ------ #
        template = (
    "There is a conflict in the access of {object} for {Subject}: \n\n")        

        # Fill in the template         
        simple = template.format(
            Subject=subject,
            action=action,
            object=obj
        )
        i = 0
        for permission in accessPermissions:            
            simple+= " "+self.renderExplanationSimple(permission, "Permission", i)
            i = i+1
        simple+="\n\n"
        j = 0
        for prohibition in accessProhibitions:
            simple+= " "+self.renderExplanationSimple(prohibition, "Prohibition", j)
            j= j+1

        # ------ CONTRAST ------ #
        contrast = "There are contrasts: "
        diff_supports_short = difference_supports_short(resultWithExplanaitons.graph, resultWithExplanaitons.example_uri, resultWithExplanaitons.subject, resultWithExplanaitons.action, resultWithExplanaitons.obj)
        diff_supports_text = diff_supports_verbalisation(self.graph, self.example_uri, diff_supports_short)
        contrast += diff_supports_text

        # ------ AUTOMATIC RESOLUTION ------ #
        outcome = ""
        no_support_prohibition = False
        acceptance = resultWithExplanaitons.check_acceptance_with_details(self.example_uri)
        if acceptance[0]:
            outcome = capitalize_first_letter(subject)+" can "+action+" "+obj+" because "
            if len(acceptance[1]) != 0:
                for acceptance_detail in acceptance[1]:
                    # This outcome is comparaison between two contrasts
                    outcome += resultWithExplanaitons.getNaturalLanguagePreference(acceptance_detail)+", and "
                outcome = outcome[:-6]+"."
            #if acceptance[1] != None:
            #    # This outcome is comparaison between two contrasts
            #    outcome += resultWithExplanaitons.getNaturalLanguagePreference(acceptance[1])  
            else:
                outcome += "there is no support for the prohibition."
                no_support_prohibition = True
        else:
            outcome = "Therefore, because of the conflicts, "+ capitalize_first_letter(subject)+" can "+action+" "+obj+"."
        
        # ------ OUTPUT ------ #

        if no_support_prohibition:
            output = simple + " " + outcome
        else:
            output = simple +"\n\n"+ contrast +"\n\n"+ outcome

        # Return the result  
        return output

    def getExplanationsPermissions(self): # This is full permission: It's OK (no need to change anymore)
        results = []
        i = 0
        for permission in self.accessesPermission:
            prohibitions = self.getAccessFor(permission.subject, permission.action, permission.obj, "Prohibition")
            if (len(prohibitions) == 0): 
                result = None
                for currentResult in results:
                    if (currentResult.subject == permission.subject and currentResult.action == permission.action and currentResult.obj == permission.obj):
                        result = currentResult
                if result == None:
                    result = ResultWithExplanations(self.graph, self.example_uri, permission.subject, permission.action, permission.obj)
                    results.append(result)    
                result.accesses.append(permission)
                result.results.append("Permitted")
                verbalisedExplanation = self.renderExplanationSimple(permission, "Permission", i)                
                i = i+1
                result.text = verbalisedExplanation                        
        return results
        
    def getExplanationsProhibitions(self): # This is full prohibition: It's OK (no need to change anymore)
        results = []
        i = 0
        for prohibition in self.accessesProhibition:
            permissions = self.getAccessFor(prohibition.subject, prohibition.action, prohibition.obj, "Permission")
            if (len(permissions) == 0):  
                result = None
                for currentResult in results:
                    if (currentResult.subject == prohibition.subject and currentResult.action == prohibition.action and currentResult.obj == prohibition.obj):
                        result = currentResult
                if result == None:
                    result = ResultWithExplanations(self.graph, self.example_uri, prohibition.subject, prohibition.action, prohibition.obj)
                    results.append(result) 
                result.accesses.append(prohibition)
                result.result = "Prohibited"
                result.text = self.renderExplanationSimple(prohibition, "Prohibition", i) 
                i = i+1                          
        return results
    
    #get explanations for those that have conflicts

    def getExplanationsConflicts(self): 
        # I have to change things here
        # a) present in the logic-based explanation the supports for the permission and the prohibition
        # b) contrastive is over the difference between the supports
        # c) final automatic decision based on the preference (compute_accepted?)
        results = []
        for permission in self.accessesPermission:
            prohibitions = self.getAccessFor(permission.subject, permission.action, permission.obj, "Prohibition")
            if (len(prohibitions) != 0):
                result = None
                for currentResult in results:
                    if (currentResult.subject == permission.subject and currentResult.action == permission.action and currentResult.obj == permission.obj):
                        result = currentResult
                        
                if result == None:
                    result = ResultWithExplanations(self.graph, self.example_uri, permission.subject, permission.action, permission.obj)
                    results.append(result)
                result.accesses.append(permission)
                for prohibition in prohibitions:
                    result.accesses.append(prohibition)
                result.results.append("Permitted")
                result.results.append("Prohibited")

                #print(result.getContrastiveExplanation())
                #print(result.getOutcomeConflict())

                newText = ""
                # for prohibition in prohibitions:
                newText += self.renderExplanationConflict(result)
                
                result.text = newText                                    
        return results
# ------------------------------------------ end classes ------------------------------------------ #

def inference_query(graph, example_uri, accessType, subject, action, obj):
    # returns a tuple of the individuals involved in deriving a privilege in the form: ?permission/?prohibition ?employ ?use ?consider ?define ?v ?a ?c ?r ?org ?org2
    if accessType == "Permission":
        inference_query = 'queries.sparql/get_all_permission_ind.sparql' #Permission
    elif accessType == "Prohibition":
        inference_query = 'queries.sparql/get_all_prohibition_ind.sparql'
    else:
        print("Please enter a valid accessType.")

    with open(inference_query, 'r') as file:
        query_template = file.read()
        
        query = query_template.format(example_uri=example_uri, subject=subject, action=action, object=obj)   
    
    results = graph.query(query)
    
    return results
    
def computeAccess(g, example_uri, accessType, subject, action, obj):

    results = inference_query(g, example_uri, accessType, subject, action, obj)

    #?permission/?prohibition ?employ ?use ?consider ?define ?v ?a ?c ?r ?org ?org2
    accesses = []
    for row in results:
        permission = row[0].fragment
        employ = row[1].fragment
        use = row[2].fragment
        consider = row[3].fragment
        define = row[4].fragment
        v = row[5].fragment
        a = row[6].fragment
        c = row[7].fragment
        r = row[8].fragment
        org = row[9].fragment
        if row[10]: org2 = row[10].fragment 
        else: org2 = row[10]         

        access = Access()
        access.init(accessType, permission, employ, use, consider, define, subject, obj, v, a, action, c, r, org, org2)

        accesses.append(access)  
        #print("-> done") 
        #print(access)
        #print("")
        #print(access.getCSV())
        #print("")
    
    return accesses

def no_prohibition_case(resultsPermissions):
    textExplanations = []
    index = 0
    for result in resultsPermissions:
        index=index + 1
        access = str(index)+" - "+result.getAccessResultText()
        print(access)
        print("")
        for access in result.accesses:
            print(access)
        print("")
        print(result.text)
        textExplanations.append(result.text)
        print("---------------------------------------------------------------")
        print("")

def no_permission_case(resultsProhibitions):
    textExplanations = []
    index = 0
    for result in resultsProhibitions:
        index+=1
        print(str(index)+" - "+result.getAccessResultText())
        print("")
        for access in result.accesses:
            print(access)
        print("")
        print(result.text)
        textExplanations.append(result.text)
        print("---------------------------------------------------------------")
        print("")

def conflict_case(resultsConflicts):
    textExplanations = []
    index = 0
    for result in resultsConflicts:
        index+=1
        #print(str(index)+" - "+result.getAccessResultText())
        #print("")
        #for access in result.accesses:
        #    print(access)
        #    print("")
        #print("")
        # Contrastive Explanation
        #print(result.getContrastiveExplanation())
        #print("Outcome_issues")
        #print(result.getOutcomeConflict())
        #print("")
        print(result.text)
        textExplanations.append(result.text)
        print("---------------------------------------------------------------")
        print("")

def generate_explanations(g, example_uri, subject, action, obj, lemmatizer):

    accessesPermission = computeAccess(g, example_uri, "Permission", subject, action, obj)
    accessesProhibition = computeAccess(g, example_uri, "Prohibition", subject, action, obj)

    explanations  = Explanations(g, accessesPermission, accessesProhibition, lemmatizer)
    
    # test here if there is no prohibition fir subject, action, object
    resultsPermissions = explanations.getExplanationsPermissions()
    no_prohibition_case(resultsPermissions)
    print("")
    print("###############################################################")
    print("###############################################################")
    print("")

    # test here if there is no permission for subject, action, object
    resultsProhibitions = explanations.getExplanationsProhibitions()
    no_permission_case(resultsProhibitions)
    print("")
    print("###############################################################")
    print("###############################################################")
    print("")

    # if there are both permission and prohibition for subject, action, object (conflict)
    resultsConflicts = explanations.getExplanationsConflicts()
    conflict_case(resultsConflicts)

# Download WordNet data
#nltk.download('wordnet')
#lemmatizer = WordNetLemmatizer()

#graph = Graph()
#graph.parse("ontology/orbac-STARWARS.owl", format="xml")
#
#generate_explanations(graph, "Bob", "edit", "report1", lemmatizer)

#computeAccess(graph, "Permission", "Bob", "edit", "report1")
#computeAccess(graph, "Prohibition", "Bob", "edit", "report1")

def capitalize_first_letter(s):
    # Capitalize the first letter of the string
    return s[0].upper() + s[1:]

def remove_special_char(s):
    return s.replace("-"," ").replace("_"," ")

def noun_with_article_a(noun):
    noun = noun.lower().replace("-"," ").replace("_"," ")
    noun_phrase = nlgFactory.createNounPhrase(noun)
    noun_phrase.setSpecifier("a")
    noun = realiser.realise(noun_phrase).getRealisation()
    return noun

def employ_verbalisation(graph, example_uri, employ):        
    employ_query_path = "queries.sparql/employ_query.sparql"
    with open(employ_query_path, 'r') as file:        
        query_template = file.read()              
        query = query_template.format(example_uri=example_uri, employ=employ)   
        
    results = list(graph.query(query))
    row = results[0]    
    role = noun_with_article_a(row[1].fragment)
    subject = remove_special_char(row[0].fragment)
    org = remove_special_char(row[2].fragment)
    text = subject+ " is "+role+" at "+org
    return text

def define_verbalisation(graph, example_uri, define):    
    define_query_path = "queries.sparql/define_query.sparql"
    with open(define_query_path, 'r') as file:        
        query_template = file.read()              
        query = query_template.format(example_uri=example_uri, define=define)   

    results = list(graph.query(query))    
    row = results[0]    
    org = remove_special_char(row[0].fragment)
    subject = remove_special_char(row[1].fragment)
    action = remove_special_char(row[2].fragment)
    object = remove_special_char(row[3].fragment)
    context = remove_special_char(row[4].fragment)
    text = ""
    text = "in "+ org +", the "+context.lower()+" context holds between "+subject+", "+object+" and "+action+""
    return text  

def defines_verbalisation(graph, example_uri, defines):
    text = ""    
    if (len(defines) > 0):
        text += capitalize_first_letter(define_verbalisation(graph, example_uri, defines[0]))
        for i in range(1,len(defines)-1):
            text+=", "+define_verbalisation(graph, example_uri, defines[i])
        if (len(defines) > 1):
            text += ", and "+define_verbalisation(graph, example_uri, defines[len(defines)-1])
        return text
    else:
        return text

def employs_verbalisation(graph, example_uri, employs):
    text = ""    
    if (len(employs) > 0):
        text += capitalize_first_letter(employ_verbalisation(graph, example_uri, employs[0]))
        for i in range(1,len(employs)-1):
            text+=", "+employ_verbalisation(graph, example_uri, employs[i])
        if (len(employs) > 1):
            text += ", and "+employ_verbalisation(graph, example_uri, employs[len(employs)-1])
        return text
    else:
        return text
    
def uses_verbalisation(graph, example_uri, uses):
    text = ""    
    if (len(uses) > 0):
        text += capitalize_first_letter(use_verbalisation(graph, example_uri, uses[0]))
        for i in range(1,len(uses)-1):
            text+=", "+use_verbalisation(graph, example_uri, uses[i])
        if (len(uses) > 1):
            text += ", and "+use_verbalisation(graph, example_uri, uses[len(uses)-1])
        return text
    else:
        return text
    
def use_verbalisation(graph, example_uri, use):
    use_query_path = "queries.sparql/use_query.sparql"
    with open(use_query_path, 'r') as file:        
        query_template = file.read()              
        query = query_template.format(example_uri=example_uri, use=use)

    results = list(graph.query(query))    
    row = results[0]    
    object = remove_special_char(row[0].fragment)
    view = remove_special_char(row[1].fragment)
    org = remove_special_char(row[2].fragment)
    text = "the "+object+" is used in the view "+view.lower()+" within "+org+""
    return text

def variable_verbalisation(graph, example_uri, variable):
    if check_variable_type(graph, example_uri, variable, "Employ"):
        return employ_verbalisation(graph, example_uri, variable)
    if check_variable_type(graph, example_uri, variable, "Use"):
        return use_verbalisation(graph, example_uri, variable)
    if check_variable_type(graph, example_uri, variable, "Define"):
        return define_verbalisation(graph, example_uri, variable)
    return "The type of the variable "+variable+" is not found."

def set_difference(list1, list2): # This is useful to compute the difference between the 2 supports (permission and prohibition)
    return list(set(list1).symmetric_difference(set(list2)))

def difference_supports(g, example_uri, subject, action, object):
    perm_supports = compute_supports(g, example_uri, subject, action, object, 0)
    # print(" len(perm_supports)= ", len(list(perm_supports)))
    proh_supports = compute_supports(g, example_uri, subject, action, object, 1)
    # print(" len(proh_supports)= ", len(list(proh_supports)))

    employs_perm = []
    #uses_perm = []
    defines_perm = []
    for  perm_support in perm_supports:        
        # print("Permission support")
        # print(perm_support)
        employs_perm.append(perm_support[0].fragment)
        #uses_perm.append(perm_support[1].fragment)                
        defines_perm.append(perm_support[1].fragment)

    employs_proh = []
    #uses_proh = []
    defines_proh = []
    for proh_support in proh_supports:   
        employs_proh.append(proh_support[0].fragment)
        #uses_proh.append(proh_support[1].fragment)
        defines_proh.append(proh_support[1].fragment)

    employs_diff, uses_diff, defines_diff= "", "", ""
  
    employs_diff = set_difference(employs_perm, employs_proh)
    #uses_diff = set_difference(uses_perm, uses_proh)
    defines_diff = set_difference(defines_proh, defines_perm)
    
    return (employs_diff, uses_diff, defines_diff)

def difference_supports_short(g, example_uri, subject, action, object):
    perm_supports = compute_supports(g, example_uri, subject, action, object, 0)
    # print(" len(perm_supports)= ", len(list(perm_supports)))
    proh_supports = compute_supports(g, example_uri, subject, action, object, 1)
    # print(" len(proh_supports)= ", len(list(proh_supports)))

    employs_perm = []
    #uses_perm = []
    defines_perm = []
    for perm_support in perm_supports:        
        # print("Permission support")
        # print(perm_support)
        employs_perm.append(perm_support[0].fragment)
        #uses_perm.append(perm_support[1].fragment)                
        defines_perm.append(perm_support[1].fragment)

    employs_proh = []
    #uses_proh = []
    defines_proh = []
    for proh_support in proh_supports:   
        # print("Prohibition support")
        # print(proh_support)     
        employs_proh.append(proh_support[0].fragment)
        #uses_proh.append(proh_support[1].fragment)
        defines_proh.append(proh_support[1].fragment)

    # print("")
    # print("All permission supports")
    # print(employs_perm)
    # print(defines_perm)
    # print(uses_perm)
    # print("")
    # print("All prohibition supports")
    # print(employs_proh)
    # print(defines_proh)
    # print(uses_proh)

    employs_diff, defines_diff = "", ""

    if len(employs_perm)>0 and len(employs_proh)>0:
        employs_diff = set_difference(employs_perm, employs_proh)

    #if len(uses_perm)>0 and len(uses_proh)>0:
    #    uses_diff = set_difference(uses_perm, uses_proh)
    
    if len(defines_proh)>0 and len(defines_perm)>0:
        defines_diff = set_difference(defines_proh, defines_perm)

    # print("")
    # print("Defines diff")
    # print(defines_diff)
    # print("")
    
    return (employs_diff, defines_diff)


def print_diff_supports(diff_supports):
    employs_text = "Employs = "
    for employ in diff_supports[0]:
        employs_text+=employ+","
    print(employs_text)
    uses_text = "Uses = "
    for use in diff_supports[1]:
        uses_text+=use+","
    print(uses_text)
    defines_text = "Defines = "
    for define in diff_supports[2]:
        defines_text+=define+","
    print(defines_text)

def get_diff_supports_logic_based(diff_supports):
    text = "Delta(S_perm, S_proh) = {"
    for employ in diff_supports[0]:
        text+=employ+", "        
    for use in diff_supports[1]:
        text+=use+", "        
    for define in diff_supports[2]:
        text+=define+", "
    if text.endswith(", "):
        text = text[0:len(text)-2]
    return text+"}"

def diff_supports_verbalisation(graph, example_uri, diff_supports):
    text = ""
    puces = ("a) ","b) ","c) ","d) ","e) ")
    i = 0
    if (len(diff_supports[0])>0):
        text += puces[i]+employs_verbalisation(graph, example_uri, diff_supports[0])+". "
        i+=1

    #if (len(diff_supports[1])>0):
    #    text += puces[i]+uses_verbalisation(graph, example_uri, diff_supports[1])+". "
    #    i+=1

    if (len(diff_supports[1])>0):
        text += puces[i]+defines_verbalisation(graph, example_uri, diff_supports[1])+". "
        i+=1

    return text

def check_variable_type(graph, example_uri, variable, type):
    variable_type_checking_query_path = "queries.sparql/variable_type_checking.sparql"
    with open(variable_type_checking_query_path, 'r') as file:
        query_template = file.read()
    query = query_template.format(example_uri=example_uri, variable=variable, type=type)

    #print(query)

    results = graph.query(query)

    try:
        first_result = next(iter(results))
        if first_result:
            return True
        else: 
            return False
    except StopIteration:
        # print("No query results found.")
        return False

def to_gerund(verb, lemmatizer):
    base_form = lemmatizer.lemmatize(verb, 'v')
    if base_form.endswith('e') and len(base_form) > 1:
        return base_form[:-1] + 'ing'
    elif base_form.endswith('ie'):
        return base_form[:-2] + 'ying'
    else:
        return base_form + 'ing'