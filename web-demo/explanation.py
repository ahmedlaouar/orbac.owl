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
from util import *

# Initialize the lexicon, factory, and realiser
lexicon = Lexicon.getDefaultLexicon()
nlgFactory = NLGFactory(lexicon)
realiser = Realiser(lexicon) 

# ------------------------------------------ begin classes ------------------------------------------ #
class ResultWithExplanations:
    def __init__(self, graph, subject, action, obj):
        self.subject = subject
        self.action = action
        self.obj = obj
        self.results = []
        self.accesses = []
        self.text =""
        self.perm_supports = compute_supports(graph, subject, action, obj, 0)       
        self.proh_supports = compute_supports(graph, subject, action, obj, 1)     
        self.graph = graph

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
        diff_supports = difference_supports(self.graph, self.subject, self.action, self.obj)
        text_supports_logic_based = get_diff_supports_logic_based(diff_supports) 
        text += text_supports_logic_based+"\n"
       
        return text
    
    def is_strictly_preferred_with_details(self, member1, member2):
        dominance_query_path = "queries.sparql/dominance_query.sparql"
        with open(dominance_query_path, 'r') as file:
            query_template = file.read()

        query = query_template.format(member1=member1, member2=member2)

        results = self.graph.query(query)
        try:
            first_result = next(iter(results))
            if first_result:
                detail = member1+">"+member2
                return (True,detail)
            else: 
                detail = member1+"<"+member2
                return (False,detail)
        except StopIteration:
            # print("No query results found.")
            return (False,None)

    def check_dominance_with_details(self, subset1, subset2):
        preference = (False,None)
        for member1 in subset1:
            dominates_at_least_one = False
            for member2 in subset2:   
                preference = self.is_strictly_preferred_with_details(member1, member2)         
                if preference[0]:
                    dominates_at_least_one = True                
                    break 
            if not dominates_at_least_one:
                return (False,None)
        return preference

    def check_acceptance_with_details(self):
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
        detail = None
        for proh_support in stripped_prohibition_supports:
            conflict_supported = False
            for perm_support in stripped_permission_supports:
                dominance = self.check_dominance_with_details(perm_support, proh_support)
                if dominance[0]:
                    conflict_supported = True
                    detail = dominance[1]
                    break
            if not conflict_supported:
                return (False,None)
        return (accepted,detail)

    def getOutcomeConflict(self):
        text = "Outcome\n"
        outcome = self.check_acceptance_with_details()                

        if outcome[0]:
            outcome_logic_raw = outcome[1] # X>Y
            if outcome_logic_raw == None:
                outcome_logic = "there is no support for prohibition."
            else:
                outcome_logic = self.getLogicExplanationPreferance(outcome_logic_raw) # orbac form

            text+="Is-permitted("+self.subject+","+self.action+","+self.obj+") because "+outcome_logic+"\n"
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
        text = "'"+variable_verbalisation(self.graph, variables[0])+"' is preferred to '"+variable_verbalisation(self.graph, variables[1])+"'."
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
        explanations.append(self.accessType+"("+self.org+","+self.role+","+self.activity+","+self.view+","+self.context+") $\wedge$")
        explanations.append("Employ("+self.org+","+self.subject+","+self.role+") $\wedge$")
        explanations.append("Use("+self.org+","+self.obj+","+self.view+") $\wedge$")
        explanations.append("Consider("+self.org+","+self.action+","+self.activity+") $\wedge$")
        explanations.append("Define("+self.org+","+self.subject+","+self.action+","+self.view+","+self.context+") $\wedge$")
        explanations.append("SubOrganisationOf"+"("+self.org+","+self.org2+") $\models$")
        explanations.append(self.outcome+"("+self.subject+","+self.action+","+self.obj+")")

        return explanations
    
    def logicalExplanationDetails(self):        
        explanations=[]
        explanations.append(self.accessType+"("+self.org+","+self.role+","+self.activity+","+self.view+","+self.context+") $\wedge$")
        explanations.append(self.employ+"("+self.org+","+self.subject+","+self.role+") $\wedge$")
        explanations.append(self.use+"("+self.org+","+self.obj+","+self.view+") $\wedge$")
        explanations.append(self.consider+"("+self.org+","+self.action+","+self.activity+") $\wedge$")
        explanations.append(self.define+"("+self.org+","+self.subject+","+self.action+","+self.view+","+self.context+") $\wedge$")
        explanations.append("SubOrganisationOf"+"("+self.org+","+self.org2+") $\models$")
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
    def __init__(self, graph, accessesPermission, accessesProhibition, lemmatizer):
        self.accessesPermission = accessesPermission
        self.accessesProhibition = accessesProhibition
        self.graph = graph
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
            "{Organisation} is part of the {Organisation2}."
                )
        else:
            template = (            
            part_result+view+" in "+context+" context, where "
            "{object} is considered as "+view+", "+action_ing+" it is classified as "+activity_ing+" activity, and "
            "{Organisation} is part of the {Organisation2}."
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
    "There is a conflict in the access of {object} for {Subject}.")        

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
        j = 0
        for prohibition in accessProhibitions:
            simple+= " "+self.renderExplanationSimple(prohibition, "Prohibition", j)
            j= j+1

        # ------ CONTRAST ------ #
        contrast = " There are contrasts. "
        diff_supports_short = difference_supports_short(resultWithExplanaitons.graph, resultWithExplanaitons.subject, resultWithExplanaitons.action, resultWithExplanaitons.obj)        
        diff_supports_text = diff_supports_verbalisation(self.graph, diff_supports_short)
        contrast += diff_supports_text

        # ------ AUTOMATIC RESOLUTION ------ #
        outcome = ""
        no_support_prohibition = False
        acceptance = resultWithExplanaitons.check_acceptance_with_details()
        if acceptance[0]:
            outcome = capitalize_first_letter(subject)+" can "+action+" "+obj+" because "
            if acceptance[1] != None:
                outcome += resultWithExplanaitons.getNaturalLanguagePreference(acceptance[1]) 
            else:
                outcome += "there is no support for the prohibition."
                no_support_prohibition = True
        else:
            outcome = "Therefore, because of the conflicts, "+ capitalize_first_letter(subject)+" can "+action+" "+obj+"."
        
        # ------ OUTPUT ------ #

        if no_support_prohibition:
            output = simple + " "+outcome
        else:
            output = simple + contrast + outcome

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
                    result = ResultWithExplanations(self.graph, permission.subject, permission.action, permission.obj)
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
                    result = ResultWithExplanations(self.graph, prohibition.subject, prohibition.action, prohibition.obj)
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
                    result = ResultWithExplanations(self.graph, permission.subject, permission.action, permission.obj)
                    results.append(result)
                result.accesses.append(permission)
                for prohibition in prohibitions:
                    result.accesses.append(prohibition)
                result.results.append("Permitted")
                result.results.append("Prohibited")

                newText = ""
                # for prohibition in prohibitions:
                newText += self.renderExplanationConflict(result) 
                result.text = newText                                     
        return results
# ------------------------------------------ end classes ------------------------------------------ #

def inference_query(graph, accessType, subject, action, obj):
    # returns a tuple of the individuals involved in deriving a privilege in the form: ?permission/?prohibition ?employ ?use ?consider ?define ?v ?a ?c ?r ?org ?org2
    if accessType == "Permission":
        inference_query = 'queries.sparql/get_all_permission_ind.sparql' #Permission
    elif accessType == "Prohibition":
        inference_query = 'queries.sparql/get_all_prohibition_ind.sparql'
    else:
        print("Please enter a valid accessType.")

    with open(inference_query, 'r') as file:
        query_template = file.read()
        
        query = query_template.format(subject=subject, action=action, object=obj)   
    
    results = graph.query(query)
    
    return results
    
def computeAccess(g, accessType, subject, action, obj):

    results = inference_query(g, accessType, subject, action, obj)

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
        org2 = row[10].fragment        

        access = Access()
        access.init(accessType, permission, employ, use, consider, define, subject, obj, v, a, action, c, r, org, org2)

        accesses.append(access)  
        #print("-> done") 
        #print(access)
        print("")
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

def generate_explanations(g, subject, action, obj, lemmatizer):

    accessesPermission = computeAccess(g, "Permission", subject, action, obj)
    accessesProhibition = computeAccess(g, "Prohibition", subject, action, obj)

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