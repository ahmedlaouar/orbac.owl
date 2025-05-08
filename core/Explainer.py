import json
from logzero import logger
import logging
import optuna
import csv
import os
import requests
import torch
from functools import partial
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
from Evaluator import Evaluator
from AccessRight import AccessRight
from time import time
from huggingface_hub import InferenceClient

# Custom handler to redirect Optuna logs to logzero
class LogzeroHandler(logging.Handler):
    def emit(self, record):
        log_message = self.format(record)
        if record.levelno == logging.INFO:
            logger.info(log_message)
        elif record.levelno == logging.WARNING:
            logger.warning(log_message)
        elif record.levelno == logging.ERROR:
            logger.error(log_message)
        elif record.levelno == logging.DEBUG:
            logger.debug(log_message)

class Explainer:
    def __init__(self, model_name, use_ollama=True, ollama_model_name="", load_json_params=False, hf_token =""):
        self.model_name = model_name
        self.use_ollama = use_ollama        
        if hf_token != "":
            self.hf_token = hf_token
            #self.api_url = f"https://router.huggingface.co/hf-inference/models/{model_name}/v1/chat/completions"
            #self.api_url = "https://router.huggingface.co/novita/v3/openai/chat/completions"
            self.api_url = "https://router.huggingface.co/nebius/v1/chat/completions"
            self.headers = {"Authorization": f"Bearer {self.hf_token}"}
            self.client = InferenceClient(provider="nebius", api_key=self.hf_token,)
            self.query_model = self.query_hf
        else:
            self.use_gpu = torch.cuda.is_available()
            logger.debug('Use GPU: %r' % self.use_gpu)
            if self.use_ollama and ollama_model_name == "":
                logger.error('Missing model name to call ollama, aborting...')
            elif self.use_ollama:
                logger.info("Using ollama.")
                self.ollama_model_name = ollama_model_name
                self.url = "http://localhost:11434/api/generate"
                self.query_model = self.query_ollama
            elif not self.use_ollama:
                logger.info("Using transformers.")
                if self.use_gpu:
                    quantization_config = BitsAndBytesConfig(load_in_4bit=True)
                    self.model = AutoModelForCausalLM.from_pretrained(
                        model_name,
                        quantization_config=quantization_config,
                        torch_dtype=torch.float16,
                        device_map="auto",
                        low_cpu_mem_usage=True)
                else:
                    self.model = AutoModelForCausalLM.from_pretrained(model_name)
                self.device = "cuda" if self.use_gpu else "cpu"
                self.model.to(self.device)
                self.query_model = self.query_transformers
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.load_params = load_json_params
        logger.debug('Ready.')

    def load_from_json(self):
        try:
            filename = "LLM_experiments/tmp/best_params_" + self.model_name.split("/")[-1] + ".json"
            with open(filename, "r") as f:
                params = json.load(f)
            return params
        except FileNotFoundError:
            logger.warning(f"No saved params, using model's default.")
            return {}

    def query_ollama(self, prompt, **kwargs):
        start_time = time()    
        inputs = self.tokenizer(prompt, return_tensors="pt")
        prompt_size = len(inputs['input_ids'][0])
        payload = {
            "model": self.ollama_model_name,
            "prompt": prompt,
            "stream": False,
        }
        if kwargs:  # Include options only if kwargs is provided
            logger.info('Using provided params.')
            payload["options"] = kwargs
        elif self.load_params:
            logger.info("Loading params from json.")
            payload["options"] = self.load_from_json()
        else: 
            logger.info("Using model's default params.")
        response = requests.post(self.url, json=payload)
        answer = response.json().get("response", "").strip()
        answer = self.clean_answer(answer,prompt)        
        # Get the length of the answer in tokens
        answer_tokens = self.tokenizer(answer, return_tensors="pt")
        answer_size = len(answer_tokens['input_ids'][0])
        logger.debug(f'Model prompted in {time()-start_time:.2f} seconds.')
        return answer, prompt_size, answer_size
    
    def query_transformers(self, prompt, **kwargs):
        start_time = time()
        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.device)
        prompt_size = len(inputs['input_ids'][0])
        # Filter out kwargs to only include non-empty values
        if kwargs:  # Include options only if kwargs is provided
            logger.info('Using provided params.')
            generate_kwargs = {key: value for key, value in kwargs.items() if value is not None}
        elif self.load_params:
            logger.info("Loading params from json.")
            generate_kwargs = self.load_from_json()
        else:
            logger.info("Using model's default params.")        
            generate_kwargs = {key: value for key, value in kwargs.items() if value is not None}
        logger.debug(f"Prompting {self.model_name}.")
        outputs = self.model.generate(**inputs, **generate_kwargs).to(self.device)

        answer = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        answer = self.clean_answer(answer,prompt)
        # Get the length of the answer in tokens
        answer_tokens = self.tokenizer(answer, return_tensors="pt")
        answer_size = len(answer_tokens['input_ids'][0])
        logger.debug(f'Model prompted in {time()-start_time:.2f} seconds.')
        return answer, prompt_size, answer_size

    def query_hf(self, prompt, **kwargs):
        start_time = time()
        inputs = self.tokenizer(prompt, return_tensors="pt")
        prompt_size = len(inputs['input_ids'][0])
        messages = [{"role": "assistant", "content": prompt}]        
        # Handle extra parameters
        if kwargs:
            logger.info("Using provided params.")
        elif self.load_params:
            logger.info("Loading params from json.")
            kwargs = self.load_from_json()
        else:
            logger.info("Using default model params.")
        completion = self.client.chat.completions.create(
            model=self.model_name,
            messages=messages,
            **kwargs
        )
        answer = completion.choices[0].message.content

        answer = self.clean_answer(answer, prompt)
        answer_tokens = self.tokenizer(answer, return_tensors="pt")
        answer_size = len(answer_tokens['input_ids'][0])

        logger.debug(f"Model prompted in {time() - start_time:.2f} seconds.")
        return answer, prompt_size, answer_size

    def clean_answer(self, answer, prompt):
        if "</think>" in answer:
            answer = answer.split("</think>")[1]
        # Remove the prompt from the start of the generated answer
        if answer.startswith(prompt):
            answer = answer[len(prompt):].lstrip()
        return answer
    
    def select_random_params(self, trial):
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
        return params

    def objective(self, trial, policy):
        # Define search space for hyperparameters
        params = self.select_random_params(trial)
        # selecting a random combination of subject, action, obj
        # This way each execution is done with a different triple_query, it must allow for a better selection of parameters
        subject, action, obj = policy.select_combination()
        new_access = AccessRight(subject, action, obj, policy.graph, policy.example_uri)
        explanations = new_access.get_logic_explanations()
        prompt = new_access.generate_prompt() 
        # Add try catch here to avoid model stopping when error:
        # Generate textual explanation
        generated_text, _, _ = self.query_model(prompt, **params)        
        # Get the evaluation scores
        evaluator = Evaluator()
        metrics = evaluator.run_evaluations(new_access, generated_text, explanations)
        # Combine the scores into a single objective value to maximize (you can use a weighted sum or average)
        # Example: Using equal weights for all metrics # coverage, completness, correctness, clarity
        combined_score = (metrics['coverage'] + metrics['completness'] + metrics['correctness'] + metrics['clarity'] + (1 - metrics["hallucination"])) / 5.0 # + metrics['grammar_score']) / 5.0
        # Save the metrics to the trial's user_attrs for later access
        trial.set_user_attr('metrics', metrics)
        # Return the combined score to maximize
        return combined_score
    
    def optimize_model(self, n_trials, policy):
        optuna_logger = optuna.logging.get_logger("optuna")
        optuna_logger.setLevel(logging.INFO)  # Set logging level (adjust if needed)
        optuna_logger.addHandler(LogzeroHandler())
        # Create an Optuna study to maximize the combined score
        study = optuna.create_study(direction='maximize')  # Maximize a combined score
        # Use partial to pass model and tokenizer to the objective function        
        objective_with_model = partial(self.objective, policy=policy)
        # Optimize the objective function with Optuna
        study.optimize(objective_with_model, n_trials=n_trials)  # Run 'n_trials' trials of random search
        # Print the best hyperparameters and metrics from the best trial
        best_trial = study.best_trial
        # Save best params to json
        file_name = "LLM_experiments/tmp/best_params_" + self.model_name.split("/")[-1] + ".json"
        with open(file_name, "a") as f:
            json.dump(best_trial.params, f, indent=4)
        return best_trial
    
    def chat(self, initial_prompt, user_prompt="", refine_last_response=False, conversation=None):
        """
        Generates an AI response based on the initial prompt and user refinement.
        """
        ROLE = "You are an expert access control decisions explainer."
        if conversation is None:
            conversation = []  # Ensures a new list is created each time
        if refine_last_response and conversation:
            prompt = f"{initial_prompt}\nAI (Explanation): {conversation[-1]}\nUser: {user_prompt}\nAI (Edited Explanation):"
        else:
            prompt = ROLE + initial_prompt + "**Explanation:** \n"
        # Generate textual explanation
        answer, prompt_size, answer_size = self.query_model(prompt)
        return answer, prompt_size, answer_size

    def interactive_prompting(self, evaluator, access, iterations=1):
        logger.info('Starting interactive prompting.')
        PARAMS_THRESHOLD = 0.6 # Tune as needed
        IMPROVE = "The first answer did not cover well: \n"
        IMPROVE_COVERAGE = "- The relations and preferences leading to the decision were missing or incomplete. Provide more details about that. \n"
        IMPROVE_CORRECTNESS = "- The decision outcome was not fully correct. Please focus on improving the correctness of the decision outcome in the explanation. \n"
        IMPROVE_CLARITY = "- The explanation was unclear in some places. Focus on clarifying the reasoning behind the decision. \n"
        self.load_params = True
        logger.debug('Loaded parameters and access right elements.')
        explanations = access.get_logic_explanations()
        initial_prompt = access.generate_prompt()
        coverage, correctness, clarity = 0, 0, 0
        conversation = []
        logger.debug('Trials.')
        trial = 0
        while trial < iterations and (coverage < PARAMS_THRESHOLD or correctness < PARAMS_THRESHOLD or clarity < PARAMS_THRESHOLD) :
            try:
                if trial > 0:
                    user_prompt = IMPROVE
                    if coverage < PARAMS_THRESHOLD:
                        user_prompt += IMPROVE_COVERAGE
                    if correctness < PARAMS_THRESHOLD:
                        user_prompt += IMPROVE_CORRECTNESS
                    if clarity < PARAMS_THRESHOLD:
                        user_prompt += IMPROVE_CLARITY
                    generated_text, prompt_size, answer_size = self.chat(initial_prompt, user_prompt, refine_last_response=True, conversation=conversation)
                else:
                    generated_text, prompt_size, answer_size = self.chat(initial_prompt)
                conversation.append(generated_text)
                # Get the evaluation scores
                metrics = evaluator.run_evaluations(access, generated_text, explanations)
                coverage, correctness, clarity = metrics["coverage"], metrics['correctness'], metrics['clarity']
                logger.debug(f'Trial {trial} scores: coverage {coverage}, correctness {correctness}, clarity {clarity}.')
                combined_score = (metrics['coverage'] + metrics['completness'] + metrics['correctness'] + metrics['clarity'] + (1 - metrics["hallucination"])) / 5.0
                # Store output in dictionary
                output = {
                    "trial": trial,
                    "subject": access.subject,
                    "action": access.action,
                    "obj": access.obj,
                    "outcome": access.outcome,
                    "decision": access.verbalise_outcome(),
                    "logical_explanations": access.verbalise_logic_explanations(explanations),
                    "prompt_text": initial_prompt,
                    "prompt_size": prompt_size,
                    "answer_size": answer_size,
                    "answer": conversation[-1],
                    "combined_score": combined_score,
                    **metrics  # Unpack all metric scores into the dictionary
                }
                csv_file_path = "LLM_experiments/tmp/output_{}.csv".format(self.model_name.split("/")[-1])
                file_exists = os.path.isfile(csv_file_path)

                # Write to CSV without using pandas
                with open(csv_file_path, mode="a", newline="", encoding="utf-8") as file:
                    writer = csv.DictWriter(file, fieldnames=output.keys(), delimiter=";")
                    
                    # Write header only if file does not exist
                    if not file_exists:
                        writer.writeheader()
                    
                    writer.writerow(output)
                logger.debug(f'Trial {trial} results stored in csv file {csv_file_path}.')
                trial += 1
            except Exception as e:
                logger.error(f"Error: {e}")
                trial += 1
                continue
        logger.debug(f'Out of interaction loop, trials number: {trial}')

    def few_shot_prompting(self, evaluator, access):
        """"""
        self.load_params = True
        logger.debug('Loaded parameters and access right elements.')
        explanations = access.get_logic_explanations()
        prompt = access.generate_few_shot_prompt()
        try:
            generated_text, prompt_size, answer_size = self.query_model(prompt) # self.chat(prompt)
            # Get the evaluation scores
            metrics = evaluator.run_evaluations(access, generated_text, explanations)
            coverage, correctness, clarity = metrics["coverage"], metrics['correctness'], metrics['clarity']
            logger.debug(f'Scores: coverage {coverage}, correctness {correctness}, clarity {clarity}.')
            combined_score = (metrics['coverage'] + metrics['completness'] + metrics['correctness'] + metrics['clarity'] + (1 - metrics["hallucination"])) / 5.0
            # Store output in dictionary
            output = {
                "subject": access.subject,
                "action": access.action,
                "obj": access.obj,
                "outcome": access.outcome,
                "decision": access.verbalise_outcome(),
                "logical_explanations": access.verbalise_logic_explanations(explanations),
                "prompt_text": prompt,
                "prompt_size": prompt_size,
                "answer_size": answer_size,
                "answer": generated_text,
                "combined_score": combined_score,
                **metrics  # Unpack all metric scores into the dictionary
            }
            csv_file_path = "LLM_experiments/tmp/few_shot_output_{}_updated.csv".format(self.model_name.split("/")[-1])
            file_exists = os.path.isfile(csv_file_path)
            # Write to CSV without using pandas
            with open(csv_file_path, mode="a", newline="", encoding="utf-8") as file:
                writer = csv.DictWriter(file, fieldnames=output.keys(), delimiter=";")                
                # Write header only if file does not exist
                if not file_exists:
                    writer.writeheader()                
                writer.writerow(output)
            logger.debug(f'Few shot prompting results stored in csv file {csv_file_path}.')
        except Exception as e:
            logger.error(f"Error: {e}")
            return