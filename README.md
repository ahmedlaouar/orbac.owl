# 🛡️ ORBAC-LLM: Conflict Resolution & Explanation with Ontologies and LLMs

This project addresses **access conflict resolution in ORBAC (Organization-Based Access Control)** policies using an **acceptance-based method**, and enhances it by generating **human-friendly natural language explanations** using **Large Language Models (LLMs)**.

It integrates **symbolic reasoning over OWL ontologies** with **neural explanation generation**, and supports **experiments, evaluation, and a web-based demo**.

---

## 🎯 Project Aim

- Implement efficient **conflict resolution** in access control policies using the **acceptance method**.
- Leverage **LLMs** to produce **clear, natural language explanations** justifying granted or denied access.
- Provide tools for **experimentation, evaluation**, and **user-friendly demonstration**.

---

## 🧱 Project Structure

### `core/`
Houses all the core classes:
- `Policy`: Parses and loads ORBAC ontology and example graphs.
- `AccessRight`: Represents a specific access instance (Subject, Action, Object).
- `Explainer`: Interfaces with LLMs (HuggingFace API, Ollama, Transformers) to generate natural language explanations.
- `Evaluator`: Evaluates explanations based on **logical entailment, grammar, readability, and hallucination**.

### `dataset_generation/`
- Scripts to automatically generate synthetic **ORBAC policy instances and examples** in RDF format.
- Useful for scaling evaluations and testing generalization.

### `LLM_experiments/`
- Main engine to **run and evaluate experiments**.
- Supports:
  - `zero_shot`, `few_shot`, `interactive`, and `parameters_tuning` setups.
- Uses `optuna` for tuning, stores logs and results in:
  - `tmp/` (logs + best trial JSONs)
  - `results/` (CSV outputs, `figures/` for plots)
- Notebook: `OrBAC_LLMs_stats.ipynb` for full result analysis and visualization.

### `ontology/`
- The **core ORBAC ontology** (`.owl`) in OWL format.
- Example policies (`.owl`) demonstrating real and synthetic datasets for access rules and permissions.

### `queries.sparql/`
- Collection of **SPARQL queries** used throughout the codebase.
- Supports querying ontology data, resolving access rights, detecting conflicts, and collecting supports.

### `web-demo/`
- A **Streamlit web application** that:
  - Loads the ontology
  - Accepts input (subject, action, object)
  - Checks permissions
  - Displays **LLM-generated explanations** interactively.

---

## 🔐 Setup & Hugging Face Token
To run the LLM experiments or the Streamlit web demo, you need a **Hugging Face access token** for loading transformer models.

1. **Get your token**
   
   Create an account at https://huggingface.co and generate a token at:
https://huggingface.co/settings/tokens

2. **Agree to model terms** (if required)

   Some models require you to manually accept their terms of use on their Hugging Face model card before access is granted.
   
   Make sure to visit the model’s page and click **“Agree and access model”** if required. This applies in particular to:
    - `deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B`
    - `deepseek-ai/DeepSeek-R1-Distill-Qwen-7B`
    - `meta-llama/Llama-3.2-3B`
    - `meta-llama/Llama-3.2-3B-Instruct`
    - `google/gemma-2-9b`


3. **Save your token securely**

   Add your token in one of the following ways (depending on what part of the project you use):

    - **For LLM experiments** (`LLM_experiments/`): Create a `.env` file in the directory with:

      ```ini
      HF_TOKEN=your_token_here
      ```

    - **For the web demo** (`web-demo/`): Create a `.env` file in the directory:
      ```ini
      HF_TOKEN=your_token_here
      ```

    - **Alternatively**, for use with Streamlit: Create or edit the file `.streamlit/secrets.toml` with:
      ```toml
      HF_TOKEN = "your_token_here"
      ```

4. **Important**:
These token files (`.env`, `.streamlit/secrets.toml`) are listed in `.gitignore` to avoid exposing credentials. You must create them manually to run or reproduce the experiments or web app.

---

## 🛠️ Technologies & Libraries

### 🔎 Symbolic Reasoning
- `rdflib` – RDF/OWL parsing and querying via SPARQL
- `owlready2` – OWL ontologies manipulation (alternative or auxiliary)

### 📖 LLM-based Explanations
- `transformers`, `torch`, `AutoModelForCausalLM`, `AutoTokenizer` – LLMs for explanation generation
- `HuggingFace Inference API` – Cloud-hosted LLMs
- `Ollama` – Local LLM backend (optional)
- `optuna` – Hyperparameter tuning for prompting strategies
- `python-dotenv` – Secure environment variable management
- `nltk`, `simplenlg` – Natural Language Generation utilities

### 🧠 Text Quality & Evaluation
- `language-tool-python` – Grammar and style checking
- `textstat` – Readability scoring
- `facebook/bart-large-mnli` – NLI model for logical similarity scoring
- `language-tool-python` – Grammar and style checking

### 📊 Experiment Management
- `pandas`, `numpy` – Data processing and numerical computation
- `CSV`, `logging`, `logzero` – Result tracking and experiment logging

### 🌐 Frontend
- `streamlit` – Web interface for real-time demo and testing
- `streamlit_shadcn_ui` – Enhanced UI components for Streamlit
- `htbuilder` – HTML builder for custom component rendering

---

## 🚀 How to Use

1. **Prepare Dataset**: Use `dataset_generation/` or examples in `ontology/`.
2. **Run Experiments**:
    ```bash
    python LLM_experiments/experiments.py [zero_shot|few_shot|parameters_tuning|interactive] [model_name]
    ```
3. Analyze Results: Open the notebook in `LLM_experiments/OrBAC_LLMs_stats.ipynb`.
4. Try the Web Demo:
    ```bash
    streamlit run web-demo/app.py
    ```

## 📄 License

This project is licensed under the Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License.  
To view a copy of this license, visit [https://creativecommons.org/licenses/by-nc-sa/4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/).


## 👩‍🔬 Citation