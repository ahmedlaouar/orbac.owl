import os
import optuna
import pandas as pd
from rdflib import OWL, RDF, Graph
import requests
import torch
from AccessRight import AccessRight
import textstat
from sentence_transformers import SentenceTransformer, util
from transformers import pipeline
import language_tool_python
from time import time
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
from logzero import logger

class Evaluator:
    def __init__(self, ):
        self.use_gpu = torch.cuda.is_available()
        logger.debug('Use GPU: %r' % self.use_gpu)

        logger.debug('Ready.')

ollama_model_name = {
    "local_models/Llama-3.2-3B" : "llama3.2:latest",
    "local_models/gemma-2-2b" : "gemma2:2b", 
    "local_models/DeepSeek-R1-Distill-Llama-8B" : "deepseek-r1:8b",
    "local_models/DeepSeek-R1-Distill-Qwen-1.5B" : "deepseek-r1:1.5b",
    "local_models/DeepSeek-R1-Distill-Qwen-7B" : "deepseek-r1:7b"
}

def strip_prefix(uri):
    return uri.split('#')[-1]

def get_response(model, tokenizer, inputs, **kwargs):
    outputs = model.generate(
        **inputs,
        max_new_tokens=kwargs["max_new_tokens"],
        temperature=kwargs["temperature"],   # Control randomness: lower = deterministic, higher = more creative
        top_p=kwargs["top_p"],       # Top-p sampling (nucleus sampling)
        top_k=kwargs["top_k"],         # Top-k sampling (limits sampling to the top-k probable tokens)
        repetition_penalty=kwargs["repetition_penalty"],  # Avoid repetitive answers
        no_repeat_ngram_size=kwargs["no_repeat_ngram_size"],  # Prevent repeating n-grams
        do_sample=kwargs["do_sample"],     # Use sampling instead of greedy search
        early_stopping=kwargs["early_stopping"], 
        num_beams=kwargs["num_beams"],
    )
    answer = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return answer

def query_model(model_name, prompt_text, **kwargs): # max_new_tokens=1700, temperature=0.7, top_p=0.95, top_k=50, repetition_penalty=1.2, no_repeat_ngram_size=2, do_sample=True, early_stopping=True, num_beams=5, ):
    """"""
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForCausalLM.from_pretrained(model_name)
    # Get the answer
    inputs = tokenizer(prompt_text, return_tensors="pt")

    answer = get_response(model, tokenizer, inputs, kwargs=kwargs)
    
    return answer

def query_ollama(model, prompt, **kwargs):
    url = "http://localhost:11434/api/generate"
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {
            "max_new_tokens" : kwargs["max_new_tokens"],
            "temperature" : kwargs["temperature"],   # Control randomness: lower = deterministic, higher = more creative
            "top_p" : kwargs["top_p"],       # Top-p sampling (nucleus sampling)
            "top_k" : kwargs["top_k"],         # Top-k sampling (limits sampling to the top-k probable tokens)
            "repetition_penalty" : kwargs["repetition_penalty"],  # Avoid repetitive answers
            "no_repeat_ngram_size" : kwargs["no_repeat_ngram_size"],  # Prevent repeating n-grams
            "do_sample" : kwargs["do_sample"],     # Use sampling instead of greedy search
            "early_stopping" : kwargs["early_stopping"], 
            "num_beams" : kwargs["num_beams"],
        }
    }
    response = requests.post(url, json=payload)
    return response.json().get("response", "").strip()

def load_policy(instance_file_path):
    graph = Graph()
    # Paths to the base ontology and the instance file
    base_ontology_path = "ontology/orbac.owl"
    
    # Parse the base ontology into the graph
    graph.parse(base_ontology_path, format="xml")

    # Parse the instance file into the same graph
    graph.parse(instance_file_path, format="xml")

    for s, p, o in graph.triples((None, RDF.type, OWL.Ontology)):
        base_uri = s
        #break  # Assuming there is only one owl:Ontology

    if base_uri:
        example_uri = base_uri
    else:
        print("Base URI not found in the graph.")

    if example_uri[-1] != "#":
        example_uri += "#"

    return graph, example_uri

def get_define_rules(graph):
    query = """PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            PREFIX : <https://raw.githubusercontent.com/ahmedlaouar/orbac.owl/refs/heads/main/ontology/orbac.owl#> # Adjust the base URI as necessary

            SELECT ?s ?alpha ?o {{
                ?relation rdf:type :Define .
                ?relation :definesSubject ?s .
                ?relation :definesAction ?alpha .
                ?relation :definesObject ?o .
            }}"""
    
    results = graph.query(query)

    return results

def select_combination(graph):
    # randomly get a subject, action and object from the used example
    define_rules = get_define_rules(graph)
    define_rules_data = pd.DataFrame(define_rules, columns=["Subject", "Action", "Object"])
    define_rules_data = define_rules_data.map(strip_prefix)
    combinations = define_rules_data[["Subject", "Action", "Object"]].drop_duplicates()
    random_row = combinations.sample(n=1)
    subject, action, obj = random_row["Subject"].values[0], random_row["Action"].values[0], random_row["Object"].values[0]
    return subject, action, obj

def get_combinations(graph):
    """retruens all the combinations of subject, action and object without duplicates"""
    define_rules = get_define_rules(graph)
    define_rules_data = pd.DataFrame(define_rules, columns=["Subject", "Action", "Object"])
    define_rules_data = define_rules_data.map(strip_prefix)
    combinations = define_rules_data[["Subject", "Action", "Object"]].drop_duplicates()
    return combinations

def get_sentence_transformers_score(fact, text):
    """"""
    model = SentenceTransformer('all-MiniLM-L6-v2')
    # Split the text into sentences (or use paragraphs, depending on the granularity you want)
    text_sentences = text.split('.')

    # Encode the fact and all text sentences
    fact_embedding = model.encode(fact, convert_to_tensor=True)
    text_embeddings = model.encode(text_sentences, convert_to_tensor=True)

    # Calculate cosine similarity between the fact and each sentence in the text
    similarity_scores = util.pytorch_cos_sim(fact_embedding, text_embeddings)

    # Find the sentence with the highest similarity score
    best_score = similarity_scores.max()

    return best_score.item()

def get_nli_score(fact, text):
    """"""
    # Load an NLI pipeline (for textual entailment)
    nli_model = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")
    
    # Split the text into sentences (or use paragraphs, depending on the granularity you want)
    text_sentences = text.split('.')

    best_result = 0
    # Perform zero-shot classification (NLI) to see if the text entails the fact
    for sentence in text_sentences:
        if sentence == '':
            continue
        result = nli_model(sentence, candidate_labels=[fact])
        best_result = max(best_result, result['scores'][0])
    
    return best_result

def get_sentence_similarity_score(fact, text):
    #return get_sentence_transformers_score(fact, text)
    return get_nli_score(fact, text)

def evaluate_answer_logic_similarity_outcome_granted(text_answer, explanations):
    """"""
    nb_logic_exp = 0
    sum_scores = 0
    sum_bests = 0
    
    for (employ_proh, define_proh), list_permissions in explanations.items():        
        nb_logic_exp += len(list_permissions)
        best_score = 0
        for employ_perm, define_perm in list_permissions:
            # option 1 evaluates against the specific roles and option 2 evaluates against the use of the roles in employ relations
            #fact_1 = f"the role {employ_perm.employesRole} is preferred to the role {employ_proh.employesRole}"
            fact_1 = f"the role {employ_perm.employesRole} in {employ_perm.employesEmployer} is preferred over the role {employ_proh.employesRole} in {employ_proh.employesEmployer}"
            score_1 = get_sentence_similarity_score(fact_1, text_answer)
            opposite_fact_1 = f"{employ_perm.employesEmployee} playing the role {employ_perm.employesRole} in {employ_perm.employesEmployer} is not preferred over {employ_proh.employesEmployee} playing the role {employ_proh.employesRole} in {employ_proh.employesEmployer}"
            opposite_score_1 = get_sentence_similarity_score(opposite_fact_1, text_answer) 
            # ideas of combination between fact score and opposite-fact score:
            # combined_score=max(fact_score,1-opposite_fact_score) OR combined_score=fact_score​/(fact_score+opposite_fact_score) OR combined_score=fact_score-λ*opposite_fact_score
            score_1 = score_1 - 0.2 * opposite_score_1

            # Similarly, option 1 evaluates against the specific contexts and option 2 evaluates against the definition of the contexts in define relations
            #fact_2 = f"the context {define_perm.definesContext} is preferred to the context {define_proh.definesContext}"
            fact_2 = f"the definition of the context {define_perm.definesContext} in {define_perm.definesOrganisation} is preferred over the definition of the context {define_proh.definesContext} in {define_proh.definesOrganisation}"
            score_2 = get_sentence_similarity_score(fact_2, text_answer)
            opposite_fact_2 = f"the definition of the context {define_perm.definesContext} in {define_perm.definesOrganisation} is not preferred over the definition of the context {define_proh.definesContext} in {define_proh.definesOrganisation}"
            opposite_score_2 = get_sentence_similarity_score(opposite_fact_2, text_answer)
            score_2 = score_2  - 0.2 * opposite_score_2
            
            score = (score_1 + score_2) / 2
            sum_scores += score
            best_score = max(best_score, score)

        sum_bests += best_score

    coverage = sum_bests / len(explanations)
    completness = sum_scores / nb_logic_exp

    return coverage, completness

def evaluate_answer_logic_similarity_outcome_denied(text_answer, explanations):
    """"""
    sum_scores = 0
    
    for (employ_proh, define_proh), list_permissions in explanations.items():
        best_score = 0
        sum_one_scores = 0
        for employ_perm, define_perm in list_permissions:
            fact_1 = f"the role {employ_perm.employesRole} is not preferred to the role {employ_proh.employesRole}"
            score_1 = get_sentence_similarity_score(fact_1, text_answer)
            # TODO add full relation verification and penalise with the opposite
            fact_2 = f"the context {define_perm.definesContext} is not preferred to the context {define_proh.definesContext}"
            score_2 = get_sentence_similarity_score(fact_2, text_answer) 

            score = max(score_1,score_2)
            sum_one_scores += score

        one_exp_score = sum_one_scores / len(list_permissions)
        best_score = max(best_score, one_exp_score)
        sum_scores += one_exp_score

    coverage = best_score
    completness = sum_scores / len(explanations)

    return coverage, completness

def evaluate_answer_ask_LLM(model_name, text_answer, explanations):
    """"""
    evaluation = {}
    question = "Does the provided text state the following fact? Please only provide Yes or No as an answer."
    nb_suff = 0
    nb_yes = 0
    Nb_logic_exp = 0
    for (role_proh, context_proh), list_permissions in explanations.items():        
        Nb_logic_exp += len(list_permissions)
        at_least_one_exp = 0
        for role_perm, context_perm in list_permissions:
            prompt = ""
            fact_1 = f"The fact: {role_perm} is preferred to {role_proh}"
            prompt += question + "\n" + fact_1 + "\n" + "The text: " + text_answer
            response_1 = query_ollama(model_name, prompt)
            response_1 = response_1.split("</think>")[1].strip()
            
            fact_2 = f"The fact: {context_perm} is preferred to {context_proh}"
            prompt += question + "\n" + fact_2 + "\n" + "The text: " + text_answer
            response_2 = query_ollama(model_name, prompt)
            response_2 = response_2.split("</think>")[1].strip()
            fact = fact_1 + " and " + fact_2
            evaluation[fact] = response_1 + " and " + response_2

            if "Yes" in response_1 and "Yes" in response_2:
                at_least_one_exp = 1
                nb_yes += 1
            elif "Yes" in response_1 or "Yes" in response_2:
                at_least_one_exp = 0.5
                nb_yes += 0.5
        nb_suff += at_least_one_exp

    sufficiency_score = nb_suff / len(explanations)
    all_exp_score = nb_yes / Nb_logic_exp

    return evaluation, sufficiency_score, all_exp_score

def evaluate_grammaticality(tool, text):
    
    matches = tool.check(text)
    num_errors = len(matches)
    
    num_words = len(text.split())
    
    if num_words == 0:
        return 1.0  # If there are no words, return the highest score
    
    score = 1 - (num_errors / num_words)
    return max(score, 0)  # Clamp the score to a minimum of 0

def evaluate_readability(text):
    readability_scores = {}
    # Flesch Reading Ease
    readability_scores["flesch_reading_ease"] = textstat.flesch_reading_ease(text)

    # Flesch-Kincaid Grade Level
    readability_scores["flesch_kincaid_grade"] = textstat.flesch_kincaid_grade(text)

    # Gunning Fog Index
    readability_scores["gunning_fog"] = textstat.gunning_fog(text)

    # SMOG Index
    readability_scores["smog_index"] = textstat.smog_index(text)

    # Coleman-Liau Index
    readability_scores["coleman_liau_index"] = textstat.coleman_liau_index(text)

    # Automated Readability Index
    readability_scores["ari"] = textstat.automated_readability_index(text)

    return readability_scores

def run_evaluations(access, answer, explanations):
    """"""
    # here call a function to evaluate an answer, while providing logical explanations
    # model_name = "deepseek-r1:1.5b" # "deepseek-r1:7b" # "deepseek-r1:8b" # 
    #evaluation, coverage, completness = evaluate_answer_ask_LLM(model_name, answer, explanations)

    # coverage: a score for identifying at least one explanation per support of prohibition 
    # completness: a score for identifying all explanations
    metrics = {}
    if access.outcome and len(explanations) != 0:
        metrics["coverage"], metrics["completness"] = evaluate_answer_logic_similarity_outcome_granted(answer, explanations)
        
    elif access.outcome and len(explanations) == 0:
        fact = "There is no support for a prohibition."
        metrics["coverage"] = get_sentence_similarity_score(fact,answer)
        metrics["completness"] = metrics["coverage"]
        
    elif not access.outcome and len(explanations) != 0 and len(access.permission_supports) != 0:
        metrics["coverage"], metrics["completness"] = evaluate_answer_logic_similarity_outcome_denied(answer, explanations)

    elif not access.outcome and len(explanations) != 0 and len(access.permission_supports) == 0:
        fact = "There is no support for a permission."
        metrics["coverage"] = get_sentence_similarity_score(fact,answer)
        metrics["completness"] = metrics["coverage"]
                    
    elif not access.outcome and len(explanations) == 0:
        fact = "There is no support for a permission and there is no support for a prohibition."
        metrics["coverage"] = get_sentence_similarity_score(fact,answer) 
        metrics["completness"] = metrics["coverage"]            
    
    # corectness: a score for identifying the elements of the supports and the decision outcome (cuurent version only evaluates outcome)
    fact_1 = f"The access of {access.subject} with {access.action} to {access.obj} was granted"
    score_1 = get_sentence_similarity_score(fact_1,answer)
    fact_2 = f"The access of {access.subject} with {access.action} to {access.obj} was denied"
    score_2 = get_sentence_similarity_score(fact_2,answer)
    if access.outcome:
        score = score_1 - 0.2 * score_2
    else:
        score = score_2 - 0.2 * score_1
    metrics["correctness"] = score
        
    # clarity: a score for explaining how dominance works
    fact = """An access is granted if and only if, for each support of a prohibition, there exists a corresponding support for a permission where the permission's support dominates the prohibition's."""
    #Dominance means that: each element of the support of the permission is strictly preferred to at least one element of the support of the prohibition.
    metrics["clarity"] = get_sentence_similarity_score(fact, answer)

    # Grammar score
    tool = language_tool_python.LanguageTool('en-GB')
    metrics["grammar_score"] = evaluate_grammaticality(tool, answer)
    
    # readability scores:
    readability_scores = evaluate_readability(answer)
    
    # precision: a score for correctly identified relations / all mentioned relations
    # structure: a score for how the explanation is ordered (decision rule -> supports -> dominance: for each s_proh to a dominant s_perm -> outcome) 
    # terminilogy: a score for using the right terminology

    # TODO : score useful vs useless text (using hallucination method)
    # TODO : check supports (mainly permission and prohibition elements).
    
    return metrics, readability_scores # coverage, completness, correctness, clarity, grammar_score, readability_scores

def objective(trial, model, tokenizer, graph, example_uri, use_ollama):
    # Define search space for hyperparameters
    params = {}
    params["temperature"] = trial.suggest_float('temperature', 0.5, 1.5)  # Values between 0.5 and 1.5
    params["top_p"] = trial.suggest_float('top_p', 0.7, 1.0)  # Values between 0.7 and 1.0
    params["top_k"] = trial.suggest_int('top_k', 60, 100)  # Values between 30 and 100
    params["max_new_tokens"] = 1800 # trial.suggest_int('max_new_tokens', 600, 1600)  # Max length of the generated text
    params["repetition_penalty"] = trial.suggest_float('repetition_penalty', 1.0, 1.8)  # Penalize repetition (1.0 to 2.0)
    params["no_repeat_ngram_size"] = trial.suggest_int('no_repeat_ngram_size', 2, 5)  # Avoid repeating n-grams (2 to 5)
    params["do_sample"] = True # trial.suggest_categorical('do_sample', [True, False])  # Whether to use sampling or greedy decoding
    params["early_stopping"] = False # trial.suggest_categorical('early_stopping', [True, False])  # Whether to stop early when all beams finish
    params["num_beams"] = trial.suggest_int('num_beams', 2, 5)  # Beam search width (1 to 5)

    # selecting a random combination of subject, action, obj
    # This way each execution is done with a different triple_query, it must allow for a better selection of parameters
    subject, action, obj = select_combination(graph) # "Zane_Gonzalez", "ask", "agreement6" #

    new_access = AccessRight(subject, action, obj, graph, example_uri)
    explanations = new_access.get_logic_explanations()

    prompt = new_access.generate_prompt()
    
    # Generate text and evaluate it
    inputs = tokenizer(prompt, return_tensors="pt")
    if use_ollama:
        generated_text = query_ollama(model, prompt, **params)
    else:
        generated_text = get_response(model, tokenizer, inputs, **params)

    if "</think>" in generated_text:
            generated_text = generated_text.split("</think>")[1]
    # Remove the prompt from the start of the generated answer
    if generated_text.startswith(prompt):
        generated_text = generated_text[len(prompt):].lstrip()

    # Get the evaluation scores
    metrics, readability_scores = run_evaluations(new_access, generated_text, explanations)

    # Combine the scores into a single objective value to maximize (you can use a weighted sum or average)
    # Example: Using equal weights for all metrics # coverage, completness, correctness, clarity, grammar_score, readability_scores
    combined_score = (metrics['coverage'] + metrics['completness'] + metrics['correctness'] + metrics['clarity']) / 4.0 # + metrics['grammar_score']) / 5.0

    # Save the metrics to the trial's user_attrs for later access
    trial.set_user_attr('metrics', metrics)
    trial.set_user_attr('readability_scores', readability_scores)
    # Return the combined score to maximize
    return combined_score

def optimize_model(model_name, instance_file_path, n_trials, use_ollama=True):
    # Initialize model and tokenizer
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    if use_ollama:
        model = ollama_model_name[model_name]
    else:
        model = AutoModelForCausalLM.from_pretrained(model_name)

    # get an example elements
    graph, example_uri = load_policy(instance_file_path)

    # Create an Optuna study to maximize the combined score
    study = optuna.create_study(direction='maximize')  # Maximize the combined score

    # Use partial to pass model and tokenizer to the objective function
    from functools import partial
    objective_with_model = partial(objective, model=model, tokenizer=tokenizer, graph=graph, example_uri=example_uri, use_ollama=use_ollama)

    # Optimize the objective function with Optuna
    study.optimize(objective_with_model, n_trials=n_trials)  # Run 'n_trials' trials of random search

    # Print the best hyperparameters and metrics from the best trial
    best_trial = study.best_trial
    return best_trial

def ask_model(model_name, new_access, params, use_ollama = True):
    
    output = {}
    
    output["subject"] = new_access.subject
    output["action"] = new_access.action
    output["obj"] = new_access.obj
        
    output["outcome"] = new_access.outcome
    decision = new_access.verbalise_outcome()
    output["decision"] = decision
    
    explanations = new_access.get_logic_explanations()

    output["logical_explanations"] = new_access.verbalise_logic_explanations(explanations)

    prompt = new_access.generate_prompt()
    
    output["prompt_text"] = prompt

    # Initialize model and tokenizer
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    inputs = tokenizer(prompt, return_tensors="pt")
    output["prompt_size"] = len(inputs['input_ids'][0])
    
    # Generate text
    if use_ollama:
        generated_text = query_ollama(ollama_model_name[model_name], prompt, **params)
    else:
        #quantization_config = BitsAndBytesConfig(load_in_4bit=True)
        model = AutoModelForCausalLM.from_pretrained(
            model_name,
            #quantization_config=quantization_config, # Apply 4-bit quantization
            #device_map="auto",  # Automatically map the model to available hardware
            #torch_dtype=torch.float32,  # Use FP16 for better performance
        )
        #print(model.config) #print(model.config.hidden_size)  # Should print 2304
        generated_text = get_response(model, tokenizer, inputs, **params)
    
    if "</think>" in generated_text:
        generated_text = generated_text.split("</think>")[1]

    # Remove the prompt from the start of the generated answer
    if generated_text.startswith(prompt):
        generated_text = generated_text[len(prompt):].lstrip()
    
    answer_tokens = tokenizer(generated_text, return_tensors="pt")

    # Get the length of the answer in tokens
    output["answer_size"] = len(answer_tokens['input_ids'][0])

    answer = generated_text.replace(";",",")
    output["answer"] = answer.replace("\n",". ")
    
    # Get the evaluation scores
    metrics, readability_scores = run_evaluations(new_access, generated_text, explanations)

    combined_score = (metrics['coverage'] + metrics['completness'] + metrics['correctness'] + metrics['clarity']) / 4.0 # + metrics['grammar_score']) / 5.0

    output["combined_score"] = combined_score
    output["coverage"] = metrics['coverage']
    output["completness"] = metrics['completness']
    output["correctness"] = metrics['correctness']
    output["clarity"] = metrics['clarity']
    output["grammar_score"] = metrics['grammar_score']

    for metric, score in readability_scores.items():
        output[metric] = score

    return output # combined_score, metrics, readability_scores

if __name__ == "__main__":
    
    # TODO : consider training with the dominance relation (why S_1 dominates S_2: because each element is preferred s.t. > , > , ...), (why S_1 does not dominate S_2: because this element is not preferred: incomparable, less preferred, equal....)
    model_name = "local_models/Llama-3.2-3B" # "local_models/DeepSeek-R1-Distill-Qwen-1.5B" # 
    instance_file_path = "ontology/examples/supports_1to3_example_50.owl" # "ontology/examples/diff_supp_example_20.owl" # "ontology/examples/secondee-example.owl" #  
    
    # ask a model
    deepseek_1B_params = {
        'temperature': 1.2194096102839058,
        'top_p': 0.9102416214571637, 
        'top_k': 63, 
        'repetition_penalty': 1.7141859965010848, 
        'no_repeat_ngram_size': 2, 
        'num_beams': 5,
        'max_new_tokens': 1800,  
        'do_sample': True, 
        'early_stopping': False,
        }
    deepseek_7B_params = {
        'temperature': 1.158335408258468, 
        'top_p': 0.8170528801501591, 
        'top_k': 82, 
        'repetition_penalty': 1.667371695195381, 
        'no_repeat_ngram_size': 5, 
        'num_beams': 5,
        'max_new_tokens': 1800,  
        'do_sample': True, 
        'early_stopping': False, 
        }
    
    # get example elements
    graph, example_uri = load_policy(instance_file_path)
    
    #subject, action, obj = select_combination(graph) # "Wendy_Mitchell", "select", "dataset2" # "Zane_Gonzalez", "ask", "agreement6" #
    combinations = get_combinations(graph)
    total_rows = len(combinations)
    for idx, row in enumerate(combinations.itertuples(), 1):
        start_time = time()
        subject, action, obj = row.Subject, row.Action, row.Object
        new_access = AccessRight(subject, action, obj, graph, example_uri)
    
        output = ask_model(model_name, new_access, deepseek_7B_params)

        # Convert list of dictionaries to DataFrame
        outputs = [output]
        df = pd.DataFrame(outputs)

        # Define the CSV file path
        csv_file_path = "results/output_"+ model_name.split("/")[-1] + ".csv"

        # Check if the file already exists
        file_exists = os.path.isfile(csv_file_path)

        # Write DataFrame to CSV with a custom delimiter "|" and append mode
        df.to_csv(csv_file_path, sep=";", index=False, mode='a', header=not file_exists)

        end_time = time()
        # Calculate and print progress
        progress = (idx / total_rows) * 100
        print(f"Progress: {progress:.2f}%, time spent: {end_time - start_time} seconds.")    
    
    # or alternatively fine-tune parameters
    """
    n_trials = 15
    use_ollama = True
    best_trial = optimize_model(model_name, instance_file_path, n_trials, use_ollama)

    with (open("results/best_trial.txt", "a")) as f:
        f.write(f"--------------------------------- Using Ollama = {use_ollama} ------------------------------------------------------\n")
        f.write(f"Used model: {model_name.split("/")[-1]}, Executed example: {instance_file_path}:\n")
        f.write(f"Best hyperparameters: {best_trial.params}\n")
        f.write(f"Best combined score: {best_trial.value}\n")
        f.write(f"Best trial metrics: {best_trial.user_attrs['metrics']}\n")
        f.write(f"Best trial readability_scores: {best_trial.user_attrs['readability_scores']}\n")
    
    # instance_file_path = "ontology/examples/long-example-V3.owl" # "ontology/examples/long-example-V1.owl" # "ontology/examples/diff_supp_example_20.owl" # "ontology/examples/secondee-example.owl" #
    """