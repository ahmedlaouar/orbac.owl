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


tool = language_tool_python.LanguageTool('en-US')
import numpy as np


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

class ResultWithExplanations:
    def __init__(self, subject, action, object):
        self.subject = subject
        self.action = action
        self.object = object
        self.results = []
        self.accesses = []
        self.text =""
    
    def getAccessResultArray(self):
        resultsStr = []
        for result in self.results:
            resultsStr.append("Access("+self.subject+","+self.action+","+self.object+") = "+result)
        return resultsStr
    
    def getAccessResultText(self):
        output = ""
        for str in self.getAccessResultArray():
            output += str+"\n"
        return output
    def getContrastiveExplanation(self): # needs to be well formulated in the future
        text = ""
        prohibition = Access()
        permission = Access()
        #print(len(self.accesses))
        for access in self.accesses:
            if access.accessType == "Prohibition":
                prohibition = access
                #print(prohibition)
            if access.accessType == "Permission":
                permission = access
                #print(permission)        
        
        explanationsPermission = permission.logicalExplanation()
        explanationsProhibition = prohibition.logicalExplanation()

        similars = []
        contrastsB = []
        contrastsNotB = []
        
        i = 0
        while i < len(explanationsPermission) - 1:
            if (explanationsPermission[i] == explanationsProhibition[i]):
                similars.append(explanationsPermission[i])
            else:
                contrastsB.append(explanationsPermission[i])
                contrastsNotB.append(explanationsProhibition[i])
            i += 1

        text = "Contrast(X, Y, Z) represents the change in the truth value of X when the variable Y is changed to Z, where: \n"
        X = "X = "
        for similar in similars:
            X += similar+" "
        X = X[:len(X) - 10]+"\n"
        
        text+= X
        Y = "Y = "
        for constrastB in contrastsB:
            Y += constrastB+" "
        Y = Y[:len(Y) - 10]+"\n"
        text+= Y

        Z = "Z = "
        for constrastNotB in contrastsNotB:
            Z += constrastNotB+" "
        Z = Z[:len(Z) - 10]+"\n"
        text+= Z

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
        str = ""
        for explanation in self.logicalExplanation():
            str+=explanation+"\n"
        return str

class Explanations:
    def __init__(self, accessesPermission, accessesProhibition):
        self.accessesPermission = accessesPermission
        self.accessesProhibition = accessesProhibition

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
    
    
    def renderExplanationSimple(self, access, accessType):
                
        ability = "can"
        decision = "permitted"

        if (accessType == "prohibition"):
            ability = "cannot"
            decision = "prohibited"

       # Initialize the lexicon, factory, and realiser
        lexicon = Lexicon.getDefaultLexicon()
        nlgFactory = NLGFactory(lexicon)
        realiser = Realiser(lexicon)     

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

        template = (
    "{Subject}, "+role+" at {Organisation}, part of the {Organisation2}, "+ability+" {action} the {object}. "
    "This is because {Subject}"
    " is "+decision+" to {activity} "+view+" in "+context+" context, where "
    "{object} is considered as "+view+", and "+action_ing+" it is classified as a "+activity_ing+" activity."
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
    
    def renderExplanationConflict(self, accessPermission, accessProhibition):
                
         

        # Initialize the lexicon, factory, and realiser
        lexicon = Lexicon.getDefaultLexicon()
        nlgFactory = NLGFactory(lexicon)
        realiser = Realiser(lexicon)     

        # Define the input values
        subject = accessPermission.subject.capitalize().replace("_"," ")
        action = accessPermission.action.lower().replace("-"," ").replace("_"," ")
        object = accessPermission.object.lower().replace("-"," ").replace("_"," ")

        view = accessPermission.view.lower().replace("-"," ").replace("_"," ")
        noun_phrase = nlgFactory.createNounPhrase(view)
        noun_phrase.setSpecifier("a")
        view = realiser.realise(noun_phrase).getRealisation()

        activity = accessPermission.activity.lower().replace("-"," ").replace("_"," ")        
            
        activity_ing = to_gerund(activity)

        action_ing = to_gerund(action)
       
        context = accessPermission.context.lower().replace("-"," ").replace("_"," ")
        noun_phrase = nlgFactory.createNounPhrase(context)
        noun_phrase.setSpecifier("a")
        context = realiser.realise(noun_phrase).getRealisation()

        role = accessPermission.role.lower().replace("-"," ").replace("_"," ")
        noun_phrase = nlgFactory.createNounPhrase(role)
        noun_phrase.setSpecifier("a")
        role = realiser.realise(noun_phrase).getRealisation()

        organisation = accessPermission.org
        organisation2 = accessPermission.org2

        subject_prohibition = accessProhibition.subject.capitalize().replace("_"," ")
        action_prohibition = accessProhibition.action.lower().replace("-"," ").replace("_"," ")
        object_prohibition = accessProhibition.object.lower().replace("-"," ").replace("_"," ")

        view_prohibition = accessProhibition.view.lower().replace("-"," ").replace("_"," ")
        noun_phrase = nlgFactory.createNounPhrase(view_prohibition)
        noun_phrase.setSpecifier("a")
        view_prohibition = realiser.realise(noun_phrase).getRealisation()

        activity_prohibition = accessProhibition.activity.lower().replace("-"," ").replace("_"," ")        
            
        activity_ing_prohibition = to_gerund(activity_prohibition)

        action_ing_prohibition = to_gerund(action_prohibition)
       
        context_prohibition = accessProhibition.context.lower().replace("-"," ").replace("_"," ")
        noun_phrase = nlgFactory.createNounPhrase(context_prohibition)
        noun_phrase.setSpecifier("a")
        context_prohibition = realiser.realise(noun_phrase).getRealisation()

        role_prohibition = accessProhibition.role.lower().replace("-"," ").replace("_"," ")
        noun_phrase = nlgFactory.createNounPhrase(role_prohibition)
        noun_phrase.setSpecifier("a")
        role_prohibition = realiser.realise(noun_phrase).getRealisation()

        organisation_prohibition = accessProhibition.org
        organisation2_prohibition = accessProhibition.org2

        # Define the template           

        contrasts = [] 

        if (role != role_prohibition):
            contrasts.append("they are considered {role_prohibition}")
        if (context != context_prohibition):
            contrasts.append("the situation is in the {context_prohibition} context")
        if (view != view_prohibition):
            contrasts.append("{object} is considered as {view_prohibition}")
        if (activity != activity_prohibition):
            contrasts.append("the action ({action}) is classified as a {activity_ing_prohibition} activity")
        if (organisation != organisation_prohibition):
            contrasts.append("{Subject} belongs to {Organisation_prohibition}")
        if (organisation2 != organisation2_prohibition):
            contrasts.append("{Subject} belongs to {Organisation2_prohibition}")

        contrastText = ""

        if (len(contrasts) == 1):
            contrastText = contrasts[0]
        else:
            i = 0
            while i < len(contrasts) - 1:
                contrastText += contrasts[i]
                i += 1
                if i < len(contrasts) - 1:
                    contrastText += ", "
                else: 
                    contrastText +=", and "
        
        template = (
    "There is a conflict in the access of {object} for {Subject}. "
    "{Subject}, "+role+" at {Organisation}, part of the {Organisation2}, can {action} the {object}. "
    "{Subject}"
    " is permitted to {activity} "+view+" in "+context+" context, where "
    "{object} is considered as "+view+", and "+action_ing+" it is classified as a "+activity_ing+" activity. "
    "In contrast, {Subject} cannot {action} it when/because "+contrastText+"."
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
            role_prohibition = role_prohibition,
            context_prohibition = context_prohibition,
            view_prohibition = view_prohibition,
            activity_ing_prohibition = activity_ing_prohibition,
            Organisation_prohibition = organisation_prohibition,
            Organisation2_prohibition = organisation2_prohibition
        )

        # Return the result        
        return output

    def getExplanationsPermissions(self):
        results = []
        for permission in self.accessesPermission:
            prohibitions = self.getAccessFor(permission.subject, permission.action, permission.object, "Prohibition")
            if (len(prohibitions) == 0): 
                result = ResultWithExplanations(permission.subject, permission.action, permission.object)
                result.accesses.append(permission)
                result.results.append("Permitted")
                verbalisedExplanation = self.renderExplanationSimple(permission, "Permission")                
                result.text = verbalisedExplanation
                results.append(result)
            
        return results
        
    def getExplanationsProhibitions(self):
        results = []
        for prohibition in self.accessesProhibition:
            permissions = self.getAccessFor(prohibition.subject, prohibition.action, prohibition.object, "Permission")
            if (len(permissions) == 0):  
                result = ResultWithExplanations(prohibition.subject, prohibition.action, prohibition.object)
                result.accesses.append(prohibition)
                result.result = "Prohibited"
                result.text = self.renderExplanationSimple(prohibition, "Prohibition")
                results.append(result)            
        return results
    
    #get explanations for those that have conflicts

    def getExplanationsConflicts(self):
        results = []
        for permission in self.accessesPermission:
            prohibitions = self.getAccessFor(permission.subject, permission.action, permission.object, "Prohibition")
            if (len(prohibitions) != 0): 
                result = ResultWithExplanations(permission.subject, permission.action, permission.object)
                result.accesses.append(permission)
                result.accesses.append(prohibitions[0])
                result.results.append("Permitted")
                result.results.append("Prohibited")

                result.text = self.renderExplanationConflict(permission, prohibitions[0])                
    
                results.append(result)
        return results
    
def computeAccess(g, accessType):

    access = accessType.lower()
    query = """
    
    # Permission

    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX owl: <http://www.w3.org/2002/07/owl#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
    PREFIX : <http://www.co-ode.org/ontologies/ont.owl#>   # Adjust the base URI as necessary

SELECT  ?"""+access+""" ?employ ?use ?consider ?define ?s ?o ?v ?a ?alpha  ?c ?r #?org ?org2 
WHERE {
    #VALUES ?org2 { :Consortium } #to be removed in the final rendering
    #VALUES ?org { :Institute1 } #to be removed in the final rendering

    ?employ rdf:type :Employ .
    ?employ :employesEmployee ?s .
    
    ?use rdf:type :Use .
    ?use :usesObject ?o .
    ?use :usesView ?v .
   
    ?consider rdf:type :Consider .
    ?consider :considersAction ?alpha .
    ?consider :considersActivity ?a .
    
    ?define rdf:type :Define .
    ?define :definesSubject ?s .
    ?define :definesAction ?alpha .
    ?define :definesObject ?o .
    ?define :definesContext ?c .

     ?"""+access+""" rdf:type :"""+accessType+""" .
     ?"""+access+""" :accessTypeRole ?r .
     ?"""+access+""" :accessTypeActivity ?a .
     ?"""+access+""" :accessTypeView ?v .
     ?"""+access+""" :accessTypeContext ?c .

    {
    ?employ :employesEmployer :Institute1 .
    } UNION    {
    ?employ :employesEmployer :Consortium .
    :Institute1 :subOrganisationOf* :Consortium . 
    }
    {
    ?use :usesEmployer :Institute1 .
    } UNION    {
    ?use :usesEmployer :Consortium .
    :Institute1 :subOrganisationOf* :Consortium . 
    }
    {
    ?consider :considersOrganisation :Institute1 .
    } UNION    {
    ?consider :considersOrganisation :Consortium .
    :Institute1 :subOrganisationOf* :Consortium . 
    }
    {
    ?define :definesOrganisation :Institute1 .
    } UNION    {
    ?define :definesOrganisation :Consortium .
    :Institute1 :subOrganisationOf* :Consortium . 
    }
}
    """
    print(query)

    results = g.query(query)

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
        org = "Institute1" #row[12].fragment
        org2 = "Consortium" #row[13].fragment        

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
        csvLinesAccessPermission.append(accessPermission.getCSV())
        
    with open("Permission-computed.csv", "w") as file:            
        file.writelines(csvLinesAccessPermission)

    # [Prohibition]
    accessesProhibition = computeAccess(g, "Prohibition")

    csvLinesAccessProhibition= []
    print("Access Prohibition:")
    for accessProhibition in accessesProhibition:
        print(accessProhibition)
        print("")
        csvLinesAccessProhibition.append(accessProhibition.getCSV())
        
    with open("Prohibition-computed.csv", "w") as file:            
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

def to_gerund(verb):
    base_form = lemmatizer.lemmatize(verb, 'v')
    if base_form.endswith('e') and len(base_form) > 1:
        return base_form[:-1] + 'ing'
    elif base_form.endswith('ie'):
        return base_form[:-2] + 'ying'
    else:
        return base_form + 'ing'

########################################################################################
#                                       Main                                           #
########################################################################################

# Download WordNet data
nltk.download('wordnet')
lemmatizer = WordNetLemmatizer()

g = Graph()
g.parse("orbac-STARWARS.owl")
#g.parse("orbac-ttl-3.ttl", format="ttl")

EX = Namespace("http://www.co-ode.org/ontologies/ont.owl#")

# Compute accesses
# computeAndSaveAllAccesses(g)

# generate explanations from existing dataset

accessesPermission = loadAccesses("Permission-computed-2.csv")
accessesProhibition = loadAccesses("Prohibition-computed-2.csv")

print(len(accessesPermission))
print(len(accessesProhibition))


explanations  = Explanations (accessesPermission, accessesProhibition)
textExplanations = []

resultsPermissions = explanations.getExplanationsPermissions()

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

resultsProhibitions = explanations.getExplanationsProhibitions()

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
    print("")
    print(result.text)
    textExplanations.append(result.text)
    print("---------------------------------------------------------------")
    print("")


explanationsResultsCSV = evaluateAll(textExplanations)

fileExplanationsResultsCSV = open("resultsExplanations.csv", "w")

fileExplanationsResultsCSV.write(explanationsResultsCSV)

fileExplanationsResultsCSV.close()

csvText = getStatsResults(textExplanations)
with open("finalResult.csv", "w") as file:          
    file.writelines(csvText)

createBoxPlot(textExplanations)

print("All done")


