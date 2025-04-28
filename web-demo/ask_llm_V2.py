import os
import logzero
import pandas as pd
from AccessRight import AccessRight
from time import time
from logzero import logger
from Evaluator import Evaluator
from Policy import Policy
from Explainer import Explainer

ollama_name = {
    "Llama-3.2-3B" : "llama3.2:latest",
    "gemma-2-2b" : "gemma2:2b", 
    "DeepSeek-R1-Distill-Llama-8B" : "deepseek-r1:8b",
    "DeepSeek-R1-Distill-Qwen-1.5B" : "deepseek-r1:1.5b",
    "DeepSeek-R1-Distill-Qwen-7B" : "deepseek-r1:7b"
}

models_list = [
    "deepseek-ai/DeepSeek-R1-Distill-Qwen-7B", 
    "google/gemma-2-2b", 
    "meta-llama/Llama-3.2-3B-Instruct", 
    "google/gemma-2-2b-it", 
    "deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B", 
    "EleutherAI/llemma_7b"
]

policies_list = [
    "ontology/examples/supports_1to3_example_50.owl", 
    "ontology/examples/diff_supp_example_20.owl", 
    "ontology/examples/hospital_example_25.owl", 
    "ontology/examples/secondee-example.owl"
]

def ask_model(new_access, explainer, **kwargs):
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
    answer, prompt_size, answer_size = explainer.query_model(prompt, **kwargs)
    output["prompt_size"] = prompt_size
    output["answer_size"] = answer_size
    output["answer"] = answer    
    # Get the evaluation scores
    evaluator = Evaluator()
    metrics = evaluator.run_evaluations(new_access, answer, explanations)
    combined_score = (metrics['coverage'] + metrics['completness'] + metrics['correctness'] + metrics['clarity'] + (1 - metrics["hallucination"])) / 5.0
    output["combined_score"] = combined_score
    for metric, score in metrics.items():
        output[metric] = score
    return output

def experiments(model_name, instance_file_path):
    """"""
    start_time = time()
    n_trials = 1
    use_ollama = True
    # init policy
    policy = Policy(instance_file_path)
    use_ollama = True
    # load explainer
    explainer = Explainer(model_name, use_ollama, ollama_model_name=ollama_name[model_name.split("/")[-1]], load_json_params=True)
    best_trial = explainer.optimize_model(n_trials, policy)
    with (open("results/best_trial.txt", "a")) as f:
        f.write(f"--------------------------------- Using Ollama = {use_ollama} ------------------------------------------------------\n")
        f.write(f"Used model: {model_name.split("/")[-1]}, Executed example: {instance_file_path}:\n")
        f.write(f"Best hyperparameters: {best_trial.params}\n")
        f.write(f"Best combined score: {best_trial.value}\n")
        f.write(f"Best trial metrics: {best_trial.user_attrs['metrics']}\n")
    end_time = time()
    logger.debug(f"Optimization done in: {end_time - start_time:.2f} seconds.")
    logger.debug('Done.')

if __name__ == "__main__":
    # Set a logfile (all future log messages are also saved there)
    logzero.logfile("web-demo/tmp/logfile.log")
    logger.debug('Starting...')
    for model_name in models_list:
        for instance_file_path in policies_list:
            experiments(model_name, instance_file_path)
    """    
    model_name = "local_models/Llama-3.2-3B"
    instance_file_path = "ontology/examples/supports_1to3_example_50.owl"
    # TODO : consider training with the dominance relation (why S_1 dominates S_2: because each element is preferred s.t. > , > , ...), (why S_1 does not dominate S_2: because this element is not preferred: incomparable, less preferred, equal....)
    # model params
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
    # init policy
    policy = Policy(instance_file_path)
    use_ollama = True
    # load explainer
    explainer = Explainer(model_name, use_ollama, ollama_model_name=ollama_name[model_name.split("/")[-1]], load_json_params=True)
    combinations = policy.get_combinations()
    total_rows = len(combinations)
    for idx, row in enumerate(combinations.itertuples(), 1):
        start_time = time()
        subject, action, obj = row.Subject, row.Action, row.Object
        new_access = AccessRight(subject, action, obj, policy.graph, policy.example_uri)    
        output = ask_model(new_access, explainer)#, **deepseek_7B_params
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
        logger.debug(f"Progress: {progress:.2f}%, time spent: {end_time - start_time:.2f} seconds.")    
    logger.debug('Done.')
    """
    