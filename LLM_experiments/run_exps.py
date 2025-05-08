import logzero
from time import time
from logzero import logger
from huggingface_hub import login
import os
from dotenv import load_dotenv
import argparse
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from core.Policy import Policy
from core.Explainer import Explainer
from core.Evaluator import Evaluator
from core.AccessRight import AccessRight

load_dotenv()

models_list = [
    "deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B",
    "deepseek-ai/DeepSeek-R1-Distill-Qwen-7B",
    "meta-llama/Llama-3.2-3B",
    "meta-llama/Llama-3.2-3B-Instruct",
    "google/gemma-2-9b",
    "google/gemma-2-9b-it"
]
policies_list = [
    "ontology/examples/supports_1to3_example_50.owl", 
    "ontology/examples/diff_supp_example_20.owl", 
    "ontology/examples/hospital_example_25.owl", 
    "ontology/examples/secondee-example.owl"
]

def parameters_fine_tuning(model_name, instance_file_path):
    logger.info(f"Parameters selection for the model: {model_name}.")
    start_time = time()
    n_trials = 30
    use_ollama = False
    # init policy
    policy = Policy(instance_file_path)
    # load explainer
    explainer = Explainer(model_name, use_ollama, ollama_model_name="", load_json_params=False)
    best_trial = explainer.optimize_model(n_trials, policy)
    with (open("LLM_experiments/tmp/best_trial.txt", "a")) as f:
        f.write(f"--------------------------------- Using Ollama = {use_ollama} ------------------------------------------------------\n")
        f.write(f"Used model: {model_name}, Executed example: {instance_file_path}:\n")
        f.write(f"Best hyperparameters: {best_trial.params}\n")
        f.write(f"Best combined score: {best_trial.value}\n")
        f.write(f"Best trial metrics: {best_trial.user_attrs['metrics']}\n")
    end_time = time()
    logger.debug(f"Optimization done in: {end_time - start_time:.2f} seconds.")

def interactive_exps(model_name, instance_file_path, iterations=1):
    logger.info(f"Interactive expermients for the model: {model_name}.")
    use_ollama = False
    # init policy
    logger.debug('Init policy')
    policy = Policy(instance_file_path)
    logger.info('Going through all access elements in the policy, and not randomly selecting elements.')
    combinations = policy.get_combinations()
    total_rows = len(combinations)
    for idx, row in enumerate(combinations, 1):
        start_time = time()
        subject, action, obj = row["Subject"], row["Action"], row["Object"]
        access = AccessRight(subject, action, obj, policy.graph, policy.example_uri)
        logger.debug('Init evaluator and explainer')
        # load evaluator and explainer
        evaluator = Evaluator()
        explainer = Explainer(model_name, use_ollama, ollama_model_name="", load_json_params=False)
        explainer.interactive_prompting(evaluator, access, iterations)
        logger.info('The explainer.interactive_prompting does not return any values, everything is stored in csv.')
        end_time = time()
        # Calculate and print progress
        progress = (idx / total_rows) * 100
        logger.debug(f"Progress: {progress:.2f}%, time spent: {end_time - start_time:.2f} seconds.")
    logger.debug('Done.')

def run_few_shot(model_name, instance_file_path):
    logger.info(f"Few-shot prompting expermients for the model: {model_name}.")
    use_ollama = False
    # init policy
    logger.debug('Init policy')
    policy = Policy(instance_file_path)
    logger.info('Going through all access elements in the policy, and not randomly selecting elements.')
    combinations = policy.get_combinations()
    total_rows = len(combinations)
    for idx, row in enumerate(combinations, 1):
        start_time = time()
        subject, action, obj = row["Subject"], row["Action"], row["Object"]
        access = AccessRight(subject, action, obj, policy.graph, policy.example_uri)
        logger.debug('Init evaluator and explainer')
        # load evaluator and explainer
        evaluator = Evaluator()
        explainer = Explainer(model_name, use_ollama, ollama_model_name="", load_json_params=False)
        explainer.few_shot_prompting(evaluator, access)
        logger.info('The explainer.few_shot_prompting does not return any values, everything is stored in csv.')
        end_time = time()
        # Calculate and print progress
        progress = (idx / total_rows) * 100
        logger.debug(f"Progress: {progress:.2f}%, time spent: {end_time - start_time:.2f} seconds.")
    logger.debug('Done.')

#if __name__ == "__main__":
#    hf_token = os.getenv("HF_TOKEN")
#    login(token=hf_token)
#    # Set a logfile (all future log messages are also saved there)
#    timestamp = int(time())  # Get the current time as an integer
#    log_filename = f"LLM_experiments/tmp/logfile_{timestamp}.log"  # Format filename with timestamp
#    logzero.logfile(log_filename)  # Set log file
#    # Apply custom log handler to Optuna
#    logger.debug('Starting...')
#    for model_name in models_list:
#        for instance_file_path in policies_list:
#            run_few_shot(model_name, instance_file_path) #parameters_fine_tuning(model_name, instance_file_path)
#    logger.debug('Done.')


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Choose the specific experiments to run for a given model.")
    parser.add_argument("experiment", choices=["zero_shot", "few_shot", "parameters_tuning", "interactive"], help="Which experiment type to run")
    parser.add_argument("model", help="Name of the model to use")
    args = parser.parse_args()

    hf_token = os.getenv("HF_TOKEN")
    login(token=hf_token)

    # Set a logfile
    timestamp = int(time())
    log_filename = f"LLM_experiments/tmp/logfile_{timestamp}.log"
    logzero.logfile(log_filename)
    logger.debug('Starting...')

    if args.model not in models_list:
        logger.error(f"Model {args.model} not in models_list.")
        exit(1)

    for instance_file_path in policies_list:
        if args.experiment == "few_shot":
            run_few_shot(args.model, instance_file_path)
        elif args.experiment == "parameters_tuning":
            parameters_fine_tuning(args.model, instance_file_path)
        elif args.experiment == "interactive":
            interactive_exps(args.model, instance_file_path, iterations=4)
        elif args.experiment == "zero_shot":
            interactive_exps(args.model, instance_file_path, iterations=1)

    logger.debug('Done.')