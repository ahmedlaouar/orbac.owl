from acceptance import *
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
    perm_supports = compute_supports(g, subject, action, object, 0)
    # print(" len(perm_supports)= ", len(list(perm_supports)))
    proh_supports = compute_supports(g, subject, action, object, 1)
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
    perm_supports = compute_supports(g, subject, action, object, 0)
    # print(" len(perm_supports)= ", len(list(perm_supports)))
    proh_supports = compute_supports(g, subject, action, object, 1)
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

def to_gerund(verb, lemmatizer):
    base_form = lemmatizer.lemmatize(verb, 'v')
    if base_form.endswith('e') and len(base_form) > 1:
        return base_form[:-1] + 'ing'
    elif base_form.endswith('ie'):
        return base_form[:-2] + 'ying'
    else:
        return base_form + 'ing'