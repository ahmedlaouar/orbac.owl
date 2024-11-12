from rdflib import Graph, Namespace, URIRef, Literal
from rdflib.namespace import RDF, RDFS, OWL
from urllib.parse import urlparse

from simplenlg.framework import NLGFactory, Lexicon
from simplenlg.realiser.english import Realiser

import textstat
import language_tool_python

import nltk
from nltk.stem import WordNetLemmatizer

import matplotlib.pyplot as plt #pip install numpy matplotlib==3.8.3

import numpy as np

import compute_accepted as ca

tool = language_tool_python.LanguageTool('en-US')
 # Initialize the lexicon, factory, and realiser

lexicon = Lexicon.getDefaultLexicon()
nlgFactory = NLGFactory(lexicon)
realiser = Realiser(lexicon)   

def calculate_grammar_score(tool, text):
    
    matches = tool.check(text)
    num_errors = len(matches)
    
    num_words = len(text.split())
    
    if num_words == 0:
        return 1.0  # If there are no words, return the highest score
    
    score = 1 - (num_errors / num_words)
    return max(score, 0)  # Clamp the score to a minimum of 0

def evaluate(text):    
            
    # Flesch Reading Ease
    flesch_reading_ease = textstat.flesch_reading_ease(text)
    #print(f"Flesch Reading Ease: {flesch_reading_ease}")

    # Flesch-Kincaid Grade Level
    flesch_kincaid_grade = textstat.flesch_kincaid_grade(text)
    #print(f"Flesch-Kincaid Grade Level: {flesch_kincaid_grade}")

    # Gunning Fog Index
    gunning_fog = textstat.gunning_fog(text)
    #print(f"Gunning Fog Index: {gunning_fog}")

    # SMOG Index
    #smog_index = textstat.smog_index(text)
    #print(f"SMOG Index: {smog_index}")

    # Coleman-Liau Index
    coleman_liau_index = textstat.coleman_liau_index(text)
    #print(f"Coleman-Liau Index: {coleman_liau_index}")

    # Automated Readability Index
    ari = textstat.automated_readability_index(text)
    #print(f"Automated Readability Index: {ari}")

    #tool = language_tool_python.LanguageTool('en-US')
    #matches = tool.check(text)

    #print(f"Number of grammatical errors: {len(matches)}")
    #for match in matches:
    #    print(match)

    grammaticality = calculate_grammar_score(tool, text) 
    #print(f"Grammar score: {grammaticality:.2f}")

    csv = text+";"+"{:.2f}".format(flesch_reading_ease)+";"+"{:.2f}".format(flesch_kincaid_grade)+";"+"{:.2f}".format(gunning_fog)+";"+"{:.2f}".format(coleman_liau_index)+";"+"{:.2f}".format(ari)+";"+"{:.2f}".format(grammaticality)
    return csv

def getStatsResults(texts):
    data_Flesch =[]
    data_Flesch_Kincaid =[]
    data_Gunning_Fog = []
    data_Coleman_Liau = []
    data_ARI = []
    data_grammaticality =[]

    for text in texts:
        flesch_reading_ease = textstat.flesch_reading_ease(text)
        data_Flesch.append(flesch_reading_ease)
        flesch_kincaid_grade = textstat.flesch_kincaid_grade(text)
        data_Flesch_Kincaid.append(flesch_kincaid_grade)
        gunning_fog = textstat.gunning_fog(text)
        data_Gunning_Fog.append(gunning_fog)
        coleman_liau_index = textstat.coleman_liau_index(text)
        data_Coleman_Liau.append(coleman_liau_index)
        ari = textstat.automated_readability_index(text)
        data_ARI.append(ari)
        grammaticality = calculate_grammar_score(tool, text) 
        data_grammaticality.append(grammaticality)
    
    data = [data_Flesch, data_Flesch_Kincaid, data_Gunning_Fog, data_Coleman_Liau, data_ARI, data_grammaticality]   
    print("data_Flesch = ",data_Flesch) 
    print("data_Flesch_Kincaid = ",data_Flesch_Kincaid) 
    print("data_Gunning_Fog = ",data_Gunning_Fog) 
    print("data_Coleman_Liau = ",data_Coleman_Liau) 
    print("data_ARI = ",data_ARI) 
    print("data_grammaticality = ",data_grammaticality) 
    
    labels = ['Flesch', 'Flesch-Kincaid', 'Gunning Fog Index', 'Coleman-Liau', 'ARI','Grammaticality']
    results =[]
    title = "Metric;Mean;Standard deviation;Min;Max\n"
    results.append(title)
    i = 0
    for d in data:
        mean_value = np.mean(d)    
        max_value = np.max(d)        
        min_value = np.min(d)    
        # Calculate standard deviation
        std_dev = np.std(d)
        csv = labels[i]+";"+"{:.2f}".format(mean_value)+";"+"{:.2f}".format(std_dev)+";"+"{:.2f}".format(min_value)+";"+"{:.2f}".format(max_value)
        results.append(csv+"\n")
        i += 1
    return results
    
def createBoxPlot(texts):
    data_Flesch =[]
    data_Flesch_Kincaid =[]
    data_Gunning_Fog = []
    data_Coleman_Liau = []
    data_ARI = []
    data_grammaticality =[]

    for text in texts:
        flesch_reading_ease = textstat.flesch_reading_ease(text)
        data_Flesch.append(flesch_reading_ease)
        flesch_kincaid_grade = textstat.flesch_kincaid_grade(text)
        data_Flesch_Kincaid.append(flesch_kincaid_grade)
        gunning_fog = textstat.gunning_fog(text)
        data_Gunning_Fog.append(gunning_fog)
        coleman_liau_index = textstat.coleman_liau_index(text)
        data_Coleman_Liau.append(coleman_liau_index)
        ari = textstat.automated_readability_index(text)
        data_ARI.append(ari)
        grammaticality = calculate_grammar_score(tool, text) 
        data_grammaticality.append(grammaticality)
    
    data = [data_Flesch, data_Flesch_Kincaid, data_Gunning_Fog, data_Coleman_Liau, data_ARI, data_grammaticality]    

    # Create a box plot for all data sets
    plt.figure(figsize=(10, 6))
    plt.boxplot(data, labels=['Flesch', 'Flesch-Kincaid', 'Gunning Fog Index', 'Coleman-Liau', 'ARI','Grammaticality'])
    plt.title('Readability, understandability and grammaticality of the generated explanations')
    plt.xlabel('Data Sets')
    plt.ylabel('Values')

    # Save the plot as a PDF file
    plt.savefig('boxplot.pdf')

    # Save the plot as a PNG file (alternative)
    # plt.savefig('boxplot.png')

    plt.show()

def evaluateAll(texts):
    title = "Explanation;Flesch Reading Ease;Flesch-Kincaid Grade Level;Gunning Fog Index;Coleman-Liau Index;Automated Readability Index;Grammaticality"
    output = ""
    for text in texts:
        output += evaluate(text)+"\n"
    return title+"\n"+output

def to_gerund(verb):
    base_form = lemmatizer.lemmatize(verb, 'v')
    if base_form.endswith('e') and len(base_form) > 1:
        return base_form[:-1] + 'ing'
    elif base_form.endswith('ie'):
        return base_form[:-2] + 'ying'
    else:
        return base_form + 'ing'
    
class ResultWithExplanations:
    def __init__(self, graph, subject, action, object):
        self.subject = subject
        self.action = action
        self.object = object
        self.results = []
        self.accesses = []
        self.text =""
        self.perm_supports = ca.compute_supports(graph, subject, action, object, 0)       
        self.proh_supports = ca.compute_supports(graph, subject, action, object, 1)     
        self.graph = graph
    
    def getAccessResultArray(self):
        resultsStr = []
        for result in self.results:
            resultsStr.append("Access("+self.subject+","+self.action+","+self.object+") = "+result)
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
        diff_supports = difference_supports(self.graph, self.subject, self.action, self.object)
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
            stripped_prohibition_supports.append(tuple(ca.strip_prefix(str(uri)) for uri in proh_support))
        stripped_prohibition_supports = list(set(stripped_prohibition_supports))
        stripped_permission_supports = []
        for perm_support in permission_supports:
            stripped_permission_supports.append(tuple(ca.strip_prefix(str(uri)) for uri in perm_support))
        stripped_permission_supports = list(set(stripped_permission_supports))

        # checking if the supports are in line with my supports 
        #print(stripped_permission_supports)
        #print(stripped_prohibition_supports)

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

            text+="Is-permitted("+self.subject+","+self.action+","+self.object+") because "+outcome_logic+"\n"
            # if outcome_logic_raw != None: # This was just a test if verbalisation related the preference works well
            #     text+=self.getNaturalLanguagePreference( outcome_logic_raw)

        else:
            text+="Is-prohibited("+self.subject+","+self.action+","+self.object+")"
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
        self.object = o
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
        self.object = elements[7]
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
        explanations.append("Use("+self.org+","+self.object+","+self.view+") $\wedge$")
        explanations.append("Consider("+self.org+","+self.action+","+self.activity+") $\wedge$")
        explanations.append("Define("+self.org+","+self.subject+","+self.action+","+self.view+","+self.context+") $\wedge$")
        explanations.append("SubOrganisationOf"+"("+self.org+","+self.org2+") $\models$")
        explanations.append(self.outcome+"("+self.subject+","+self.action+","+self.object+")")

        return explanations
    
    def logicalExplanationDetails(self):        
        explanations=[]
        explanations.append(self.accessType+"("+self.org+","+self.role+","+self.activity+","+self.view+","+self.context+") $\wedge$")
        explanations.append(self.employ+"("+self.org+","+self.subject+","+self.role+") $\wedge$")
        explanations.append(self.use+"("+self.org+","+self.object+","+self.view+") $\wedge$")
        explanations.append(self.consider+"("+self.org+","+self.action+","+self.activity+") $\wedge$")
        explanations.append(self.define+"("+self.org+","+self.subject+","+self.action+","+self.view+","+self.context+") $\wedge$")
        explanations.append("SubOrganisationOf"+"("+self.org+","+self.org2+") $\models$")
        explanations.append(self.outcome+"("+self.subject+","+self.action+","+self.object+")")

        return explanations
    
    def getCSV(self):
        csv = self.accessType+";"+ self.access+";"+ self.employ+";"+self.use+";"+self.consider+";"+self.define+";"+self.subject+";"+self.object+";"+self.view+";"+self.activity+";"+self.action+";"+self.context+";"+self.role+";"+self.org+";"+self.org2
        return csv

    
    def __str__(self):
       return self.getLogicalExplanationDetailsStr()

    def getLogicalExplanationDetailsStr(self):
        str = ""
        for explanation in self.logicalExplanationDetails():
            str+=explanation+"\n"
        return str
    
class Salphao: # s (subject), alpha (action), o (object)
    subject = ""
    action = ""
    object = ""

class Explanations:
    def __init__(self, graph, accessesPermission, accessesProhibition):
        self.accessesPermission = accessesPermission
        self.accessesProhibition = accessesProhibition
        self.graph = graph

    def getAccessFor(self, subject, action, object, accessType):
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
            if (access.subject == subject and access.action == action and access.object == object):
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
        object = access.object.lower().replace("-"," ").replace("_"," ")

        view = access.view.lower().replace("-"," ").replace("_"," ")
        noun_phrase = nlgFactory.createNounPhrase(view)
        noun_phrase.setSpecifier("a")
        view = realiser.realise(noun_phrase).getRealisation()

        activity = access.activity.lower().replace("-"," ").replace("_"," ")        
            
        activity_ing = to_gerund(activity)

        action_ing = to_gerund(action)
       
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
            object=object,
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
        object = resultWithExplanaitons.accesses[0].object.lower().replace("-"," ").replace("_"," ")
        # We use [0] because so far it doesn't matter if it is a prohibition or a permission. subject, action and object are always the same.
        
        # ------ SIMPLE ------ #
        template = (
    "There is a conflict in the access of {object} for {Subject}.")        

        # Fill in the template         
        simple = template.format(
            Subject=subject,
            action=action,
            object=object
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
        diff_supports_short = difference_supports_short(resultWithExplanaitons.graph, resultWithExplanaitons.subject, resultWithExplanaitons.action, resultWithExplanaitons.object)        
        diff_supports_text = diff_supports_verbalisation(g, diff_supports_short)
        contrast += diff_supports_text

        # ------ AUTOMATIC RESOLUTION ------ #
        outcome = ""
        no_support_prohibition = False
        acceptance = resultWithExplanaitons.check_acceptance_with_details()
        if acceptance[0]:
            outcome = capitalize_first_letter(subject)+" can "+action+" "+object+" because "
            if acceptance[1] != None:
                outcome += resultWithExplanaitons.getNaturalLanguagePreference(acceptance[1]) 
            else:
                outcome += "there is no support for the prohibition."
                no_support_prohibition = True
        else:
            outcome = "Therefore, because of the conflicts, "+ capitalize_first_letter(subject)+" can "+action+" "+object+"."
        
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
            prohibitions = self.getAccessFor(permission.subject, permission.action, permission.object, "Prohibition")
            if (len(prohibitions) == 0): 
                result = None
                for currentResult in results:
                    if (currentResult.subject == permission.subject and currentResult.action == permission.action and currentResult.object == permission.object):
                        result = currentResult
                if result == None:
                    result = ResultWithExplanations(self.graph, permission.subject, permission.action, permission.object)
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
            permissions = self.getAccessFor(prohibition.subject, prohibition.action, prohibition.object, "Permission")
            if (len(permissions) == 0):  
                result = None
                for currentResult in results:
                    if (currentResult.subject == prohibition.subject and currentResult.action == prohibition.action and currentResult.object == prohibition.object):
                        result = currentResult
                if result == None:
                    result = ResultWithExplanations(self.graph, prohibition.subject, prohibition.action, prohibition.object)
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
            prohibitions = self.getAccessFor(permission.subject, permission.action, permission.object, "Prohibition")
            if (len(prohibitions) != 0): 
                result = None
                for currentResult in results:
                    if (currentResult.subject == permission.subject and currentResult.action == permission.action and currentResult.object == permission.object):
                        result = currentResult
                if result == None:
                    result = ResultWithExplanations(self.graph, permission.subject, permission.action, permission.object)
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
    
    # def getMergedExplanationsConflicts(self):
    #     results = self.getExplanationsConflicts()
    #     mergedResults = []
    #     for result in results:
    #         subject = result.subject
    #         action = result.action
    #         object = result.object



    # def getSalphaoPermission(self):
    #     results = self.getExplanationsPermissions(self)
    #     salphaos = []
    #     for result in results:
    #         salphao = Salphao()
    #         salphao.subject = result.
    #     return salphaos
# ------------------------------------------ end classes ------------------------------------------ #

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

def employ_verbalisation(graph, employ):        
    employ_query_path = "queries.sparql/employ_query.sparql"
    with open(employ_query_path, 'r') as file:        
        query_template = file.read()              
        query = query_template.replace("{employ}",employ)   
        
    results = list(graph.query(query))    
    row = results[0]    
    role = noun_with_article_a(row[1].fragment)
    subject = remove_special_char(row[0].fragment)
    org = remove_special_char(row[2].fragment)
    text = subject+ " is "+role+" at "+org
    return text

def define_verbalisation(graph, define):    
    define_query_path = "queries.sparql/define_query.sparql"
    with open(define_query_path, 'r') as file:        
        query_template = file.read()              
        query = query_template.replace("{define}", define)   

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

def defines_verbalisation(graph, defines):
    text = ""    
    if (len(defines) > 0):
        text += capitalize_first_letter(define_verbalisation(graph, defines[0]))
        for i in range(1,len(defines)-1):
            text+=", "+define_verbalisation(graph, defines[i])
        if (len(defines) > 1):
            text += ", and "+define_verbalisation(graph, defines[len(defines)-1])
        return text
    else:
        return text

def employs_verbalisation(graph, employs):
    text = ""    
    if (len(employs) > 0):
        text += capitalize_first_letter(employ_verbalisation(graph, employs[0]))
        for i in range(1,len(employs)-1):
            text+=", "+employ_verbalisation(graph, employs[i])
        if (len(employs) > 1):
            text += ", and "+employ_verbalisation(graph, employs[len(employs)-1])
        return text
    else:
        return text
    
def uses_verbalisation(graph, uses):
    text = ""    
    if (len(uses) > 0):
        text += capitalize_first_letter(use_verbalisation(graph, uses[0]))
        for i in range(1,len(uses)-1):
            text+=", "+use_verbalisation(graph, uses[i])
        if (len(uses) > 1):
            text += ", and "+use_verbalisation(graph, uses[len(uses)-1])
        return text
    else:
        return text
    
def use_verbalisation(graph, use):
    use_query_path = "queries.sparql/use_query.sparql"
    with open(use_query_path, 'r') as file:        
        query_template = file.read()              
        query = query_template.replace("{use}", use)

    results = list(graph.query(query))    
    row = results[0]    
    object = remove_special_char(row[0].fragment)
    view = remove_special_char(row[1].fragment)
    org = remove_special_char(row[2].fragment)
    text = "the "+object+" is used in the view "+view.lower()+" within "+org+""
    return text

def variable_verbalisation(graph, variable):
    if check_variable_type(graph, variable, "Employ"):
        return employ_verbalisation(graph, variable)
    if check_variable_type(graph, variable, "Use"):
        return use_verbalisation(graph, variable)
    if check_variable_type(graph, variable, "Define"):
        return define_verbalisation(graph, variable)
    return "The type of the variable "+variable+" is not found."

def set_difference(list1, list2): # This is useful to compute the difference between the 2 supports (permission and prohibition)
    return list(set(list1).symmetric_difference(set(list2)))

def difference_supports(g, subject, action, object):
    perm_supports = ca.compute_supports(g, subject, action, object, 0)
    # print(" len(perm_supports)= ", len(list(perm_supports)))
    proh_supports = ca.compute_supports(g, subject, action, object, 1)
    # print(" len(proh_supports)= ", len(list(proh_supports)))

    employs_perm = []
    uses_perm = []
    defines_perm = []
    for  perm_support in perm_supports:        
        # print("Permission support")
        # print(perm_support)
        employs_perm.append(perm_support[0].fragment)
        uses_perm.append(perm_support[1].fragment)                
        defines_perm.append(perm_support[2].fragment)

    employs_proh = []
    uses_proh = []
    defines_proh = []
    for proh_support in proh_supports:   
        employs_proh.append(proh_support[0].fragment)
        uses_proh.append(proh_support[1].fragment)
        defines_proh.append(proh_support[2].fragment)

    employs_diff, uses_diff, defines_diff= "", "", ""
  
    employs_diff = set_difference(employs_perm, employs_proh)
    uses_diff = set_difference(uses_perm, uses_proh)
    defines_diff = set_difference(defines_proh, defines_perm)
    
    return (employs_diff, uses_diff, defines_diff)

def difference_supports_short(g, subject, action, object):
    perm_supports = ca.compute_supports(g, subject, action, object, 0)
    # print(" len(perm_supports)= ", len(list(perm_supports)))
    proh_supports = ca.compute_supports(g, subject, action, object, 1)
    # print(" len(proh_supports)= ", len(list(proh_supports)))

    employs_perm = []
    uses_perm = []
    defines_perm = []
    for  perm_support in perm_supports:        
        # print("Permission support")
        # print(perm_support)
        employs_perm.append(perm_support[0].fragment)
        uses_perm.append(perm_support[1].fragment)                
        defines_perm.append(perm_support[2].fragment)

    employs_proh = []
    uses_proh = []
    defines_proh = []
    for proh_support in proh_supports:   
        # print("Prohibition support")
        # print(proh_support)     
        employs_proh.append(proh_support[0].fragment)
        uses_proh.append(proh_support[1].fragment)
        defines_proh.append(proh_support[2].fragment)

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

    employs_diff, uses_diff, defines_diff= "", "",""

    if len(employs_perm)>0 and len(employs_proh)>0:
        employs_diff = set_difference(employs_perm, employs_proh)

    if len(uses_perm)>0 and len(uses_proh)>0:
        uses_diff = set_difference(uses_perm, uses_proh)
    
    if len(defines_proh)>0 and len(defines_perm)>0:
        defines_diff = set_difference(defines_proh, defines_perm)

    # print("")
    # print("Defines diff")
    # print(defines_diff)
    # print("")
    
    return (employs_diff, uses_diff, defines_diff)


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

def diff_supports_verbalisation(graph, diff_supports):
    text = ""
    puces = ("a) ","b) ","c) ","d) ","e) ")
    i = 0
    if (len(diff_supports[0])>0):
        text += puces[i]+employs_verbalisation(graph, diff_supports[0])+". "
        i+=1

    if (len(diff_supports[1])>0):
        text += puces[i]+uses_verbalisation(graph, diff_supports[1])+". "
        i+=1

    if (len(diff_supports[2])>0):
        text += puces[i]+defines_verbalisation(graph, diff_supports[2])+". "
        i+=1

    return text

def check_variable_type(graph, variable, type):
    variable_type_checking_query_path = "queries.sparql/variable_type_checking.sparql"
    with open(variable_type_checking_query_path, 'r') as file:
        query_template = file.read()
    query = query_template.replace("{variable}",variable)
    query = query.replace("{type}",type)

    # print(query)

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


def inference_query(graph, accessType):
    inference_query = 'queries.sparql/inference_query_perm.sparql' #Permission
    if accessType=="Prohibition":
        inference_query = 'queries.sparql/inference_query_proh.sparql'
    with open(inference_query, 'r') as file:
        query = file.read()    
    results = graph.query(query)
    return results
    
def computeAccess(g, accessType):

    results = inference_query(g, accessType)

    accesses = []
    for row in results:
        permission = row[0].fragment
        employ = row[1].fragment
        use = row[2].fragment
        consider = row[3].fragment
        define = row[4].fragment
        s = row[5].fragment
        o = row[6].fragment
        v = row[7].fragment
        a = row[8].fragment
        alpha = row[9].fragment
        c = row[10].fragment
        r = row[11].fragment
        org = row[12].fragment
        org2 = row[13].fragment        

        access = Access()
        access.init(accessType, permission, employ, use, consider, define, s, o, v, a, alpha, c, r, org, org2)

        accesses.append(access)  
        print(s, "-> done") 
        print(access)
        print("")
        print(access.getCSV())
        print("")

    print ("query done, go to return!")     
    return accesses

def computeAndSaveAllAccesses(g):
    # [Permission]
    accessesPermission = computeAccess(g, "Permission")

    csvLinesAccessPermission= []
    print("Access permission:")
    for accessPermission in accessesPermission:
        print(accessPermission)
        print("")
        csvLinesAccessPermission.append(accessPermission.getCSV()+"\n")
        
    with open("explain_results/Permission-computed.csv", "w") as file:            
        file.writelines(csvLinesAccessPermission)

    # [Prohibition]
    accessesProhibition = computeAccess(g, "Prohibition")

    csvLinesAccessProhibition= []
    print("Access Prohibition:")
    for accessProhibition in accessesProhibition:
        print(accessProhibition)
        print("")
        csvLinesAccessProhibition.append(accessProhibition.getCSV()+"\n")
        
    with open("explain_results/Prohibition-computed.csv", "w") as file:            
        file.writelines(csvLinesAccessProhibition)

def loadAccesses(filename):
    accesses = []
    text_file = open(filename, "r")    
    lines = text_file.readlines()
    for line in lines:
        access = Access()
        access.initFromCSV(line)
        accesses.append(access)
    text_file.close()
    return accesses


#def generate_explanation():
   # conflit = compute_accepted.
########################################################################################
#                                       Main                                           #
########################################################################################

# Download WordNet data
nltk.download('wordnet')
lemmatizer = WordNetLemmatizer()

g = Graph()
g.parse("ontology/orbac-STARWARS.owl")
#g.parse("orbac-ttl-3.ttl", format="ttl")

EX = Namespace("http://www.co-ode.org/ontologies/ont.owl#")

# Compute accesses

# computeAndSaveAllAccesses(g)

# generate explanations from existing dataset

accessesPermission = loadAccesses("explain_results/Permission-computed.csv")
accessesProhibition = loadAccesses("explain_results/Prohibition-computed.csv")

# print(len(accessesPermission))
# print(len(accessesProhibition))

explanations  = Explanations(g, accessesPermission, accessesProhibition)
textExplanations = []

resultsPermissions = explanations.getExplanationsPermissions() # Here there is no prohibition for (a, alpha, o)

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


print("")
print("###############################################################")
print("###############################################################")
print("")

resultsProhibitions = explanations.getExplanationsProhibitions() # Here there is no permission for (a, alpha, o)


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

print("")
print("###############################################################")
print("###############################################################")
print("")

resultsConflicts = explanations.getExplanationsConflicts()

index = 0
for result in resultsConflicts:
    index+=1
    print(str(index)+" - "+result.getAccessResultText())
    print("")
    for access in result.accesses:
        print(access)
        print("")
    print("")
    print(result.getContrastiveExplanation())
    print("Outcome_issues")
    print(result.getOutcomeConflict())
    print("")
    print(result.text)
    textExplanations.append(result.text)
    print("---------------------------------------------------------------")
    print("")

# ----------------------- [BEGIN] EVALUATION PART -----------------------
explanationsResultsCSV = evaluateAll(textExplanations)

fileExplanationsResultsCSV = open("explain_results/resultsExplanations.csv", "w")

fileExplanationsResultsCSV.write(explanationsResultsCSV)

fileExplanationsResultsCSV.close()

csvText = getStatsResults(textExplanations)
with open("explain_results/finalResult.csv", "w") as file:          
    file.writelines(csvText)
# ----------------------- [END] EVALUATION PART -----------------------

# print("")
# employ_ref = "employ_Researcher_I1"
# employ_text = employ_verbalisation(g, employ_ref)
# print(employ_ref+" --> "+employ_text)
# print(capitalize_first_letter(employ_text))
# print("")

# define_ref = "Define_sign_agreement5"
# define_text = define_verbalisation(g, define_ref)
# print(define_ref+" --> "+define_text)
# print(capitalize_first_letter(define_text))
# print("")

# use_ref = "use_as_secondmentReport"
# use_text = use_verbalisation(g, use_ref)
# print(use_ref+" --> "+use_text)
# print(capitalize_first_letter(use_text))
# print("")

# subject, object, action = "Bob", "report1", "edit"

# diff_supports = difference_supports(g, subject, action, object)
# print_diff_supports(diff_supports)
# diff_supports_text = diff_supports_verbalisation(g, diff_supports)
# print(diff_supports_text)
# print("")
# print("Done!")


# createBoxPlot(textExplanations) [NOT TO MUCH IMPORTANT FOR OUR RESULT]

print("All done")


