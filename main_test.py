import os
import random
import pandas as pd
from os import listdir
from os.path import isfile, join
from logzero import logger
from dotenv import load_dotenv
import torch
from core.Policy import Policy
from core.AccessRight import AccessRight
from core.Explainer import Explainer
from core.Evaluator import Evaluator

# Load Hugging Face token from .env or streamlit secrets
load_dotenv()
HF_TOKEN = os.getenv("HF_TOKEN")

EXAMPLES_PATH = "ontology/examples"
MODELS = [
    "deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B",
    "deepseek-ai/DeepSeek-R1-Distill-Qwen-7B",
    "meta-llama/Llama-3.2-3B",
    "meta-llama/Llama-3.2-3B-Instruct",
    "google/gemma-2-9b",
    "google/gemma-2-9b-it",
]

ollama_name = {
    "meta-llama/Llama-3.2-3B": "llama3.2:latest",
    "meta-llama/Llama-3.2-3B-Instruct": "llama3.2:3b-instruct-fp16",
    "google/gemma-2-9b": "gemma2:9b",
    "google/gemma-2-9b-it": "gemma2:9b",
    "deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B": "deepseek-r1:1.5b",
    "deepseek-ai/DeepSeek-R1-Distill-Qwen-7B": "deepseek-r1:7b"
}

def choose_backend():
    print("\nSelect explanation backend:")
    print("1. HuggingFace Inference API (default)")
    print("2. Transformers (local)")
    print("3. Ollama")
    choice = input("Enter choice (1-3): ").strip()

    if choice == "2":
        if not torch.cuda.is_available():
            logger.warning("⚠️ No GPU detected. Transformers inference on CPU can be extremely slow or fail.")
            cont = input("Do you want to continue anyway? (y/n): ").strip().lower()
            if cont not in ['y', 'yes']:
                logger.info("Aborting as requested by the user.")
                exit(0)
        return "transformers"
    elif choice == "3":
        return "ollama"
    return "hf_api"

def choose_model():
    print("\nSelect a model:")
    for idx, name in enumerate(MODELS):
        print(f"{idx+1}. {name}")
    choice = input("Enter choice (1-6): ").strip()
    try:
        return MODELS[int(choice)-1]
    except:
        logger.warning("Invalid input. Using default model.")
        return MODELS[3]

def main():
    try:
        backend = choose_backend()
        model_name = choose_model()

        if backend == "hf_api" and not HF_TOKEN:
            logger.error("❌ No Hugging Face token found. Set HF_TOKEN in .env file.")
            return
        else:
            HF_TOKEN = ""

        files = sorted([f for f in listdir(EXAMPLES_PATH) if isfile(join(EXAMPLES_PATH, f))])
        policy_file = random.choice(files)
        logger.info(f"Selected policy: {policy_file}")
        policy = Policy(join(EXAMPLES_PATH, policy_file))

        combos = pd.DataFrame(policy.get_combinations())
        combo = combos.sample(n=1).iloc[0]
        subject, action, obj = combo['Subject'], combo['Action'], combo['Object']
        logger.info(f"Testing: is-permitted({subject}, {action}, {obj})?")

        access = AccessRight(subject, action, obj, policy.graph, policy.example_uri)

        logger.info("Permission supports:")
        for s in access.permission_supports:
            logger.info(f"- Permission support {access.permission_supports.index(s) + 1}:")
            for x in s.values():
                logger.info(f"    - {x.get_predicate()}")
        logger.info("Prohibition supports:")
        for s in access.prohibition_supports:
            logger.info(f"- Prohibition support {access.prohibition_supports.index(s) + 1}:")
            for x in s.values():
                logger.info(f"    - {x.get_predicate()}")

        logger.info("Access decision:")
        if access.outcome:
            logger.info("✅ Permission accepted")
        else:
            logger.info("❌ Permission rejected")

        logger.info("Generating explanation...")
        prompt = access.generate_few_shot_prompt()

        try:
            explainer = Explainer(
                model_name,
                use_ollama=(backend == "ollama"),
                ollama_model_name=ollama_name.get(model_name, ""),
                load_json_params=True,
                hf_token=HF_TOKEN
            )
            answer, _, _ = explainer.query_model(prompt)
            print("\n📘 Explanation:\n", answer)
        except Exception as e:
            logger.error(f"❌ Failed to generate explanation: {str(e)}")
            if backend == "ollama":
                logger.warning("💡 Check if the Ollama server is running and the model name is correct.")
            elif backend == "ollama" and explainer.ollama_model_name == "":
                logger.warning("💡 Could not find matching Ollama model name. Make sure the model is installed and named correctly.")
            elif backend == "hf_api":
                logger.warning("💡 Verify your Hugging Face token and internet connection.")
            elif backend == "transformers":
                logger.warning("💡 Ensure the model is downloaded and enough memory is available.")
            return

        logger.info("Evaluating explanation...")
        explanations = access.get_logic_explanations()
        evaluator = Evaluator()
        metrics = evaluator.run_evaluations(access, answer, explanations)
        for key, value in metrics.items():
            logger.info(f"{key}: {value}")
    
    except KeyboardInterrupt:
        logger.warning("🛑 Aborted by user.")
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")

if __name__ == "__main__":
    main()
