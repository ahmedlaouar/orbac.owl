# 🧠 Core Classes Overview – OrBAC Ontology Project

This module defines the core Python classes that represent and manipulate OrBAC ontology elements. These classes are used to construct, extract, and reason about access policies, permissions, prohibitions, and their supporting elements, and are tightly integrated with RDF/OWL ontologies.

---

## 📚 OrBAC Element Classes

The following classes each represent a basic component of an OrBAC policy and share a common structure for comparison, hashing, RDF parsing, and verbalisation.

- **`AccessType`** – Can be either `Permission`, `Prohibition`, `Obligation`, or `Recommendation`.
- **`Employ`**
- **`Use`**
- **`Consider`**
- **`Define`**

Each of these classes:

- Is initialized with a **name**, an **organization**, and 1–2 associated elements (such as a **role**, **view**, or **context**).
- Implements:
  - `__eq__` and `__hash__` for use in sets/dictionaries.
  - `create_from_graph(graph, uri, name, subject)` – loads from RDF.
  - `verbalise()` – returns a human-readable explanation.
  - `get_predicate()` – returns a logical form, e.g., `Use(org, view, object)`.

Example verbalisation (for `Use`):
```
The organisation Hospital uses recordSystem in the view HealthData.
```

---

## 🔐 `AccessRight` Class

The central class representing a specific access decision request, related to a specific `Subject`, `Action`, and `Object`, including logic for reasoning over policy rules and preference hierarchies.

### 🏗️ Constructor

```python
AccessRight(subject, action, obj, graph, uri)
```

- Inputs: Subject, Action, Object, RDF Graph, and ontology URI.
- Automatically loads related policies and hierarchical context from the RDF graph.

### 🔍 Reasoning Methods

`get_supports(accessType)` – Extracts permission or prohibition supports from RDF.

`is_strictly_preferred(member1, member2)` – Checks if a member is preferred via isPreferredTo.

`check_dominance(subset1, subset2)` – Logical comparison between sets of supports.

`check_acceptance()` – Returns boolean for whether the access is accepted.

`check_acceptance_query()` – Returns the result from a formal acceptance query.

`get_logic_explanations()` – Extracts supports and preference paths explaining the outcome.

###  📈 Hierarchy Handling

`get_hierarchical_relations()` – Fills role and context hierarchies from ontology.

`compute_hierarchy_supports(accessType=0)` – Generates supports from inferred hierarchies.

`check_if_role_from_hierarchy(...)` – Tests if a new role can be inferred through hierarchy.

`add_new_employ(...)` – Adds a new Employ support inferred from hierarchy.

### 🗣️ Verbalisation & Prompting

```python
verbalise_outcome()

verbalise_support(support)

verbalise_supports()

verbalise_preferences()

verbalise_logic_explanations(explanations)
```
– Verbalises relevant parts of an access right.

`generate_prompt()` – Builds LLM-compatible prompt from access request.

`generate_few_shot_prompt()` – Builds prompt using few-shot examples.

These methods allow the class to interface with LLMs and other NLP-based analysis tools.

---

## 🗂️ `Policy` Class

Represents a complete OrBAC policy loaded from a `.owl` ontology file. Provides querying, extraction, and consistency checking functionalities.

### 🏗️ Constructor

```python
Policy(instance_file_path)
```

- Loads base ontology and instance file into a single RDF graph.
- Extracts and normalizes the base URI for querying.

### 🔎 Query Methods

`get_concrete_concepts()` – Extracts concrete (Subject, Action, Object) triples from Define rules.

`select_combination()` – Randomly selects a unique (S, A, O) combination.

`get_combinations()`– Returns all unique (S, A, O) combinations.

`get_define_rules()`– Loads Define rules from SPARQL file.

`get_abstract_rules()`– Loads abstract AccessType rules.

`get_connection_rules()`– Loads connection relations (e.g., Use, Employ).

### ✅ Analysis Methods

`check_consistency()`– Returns True if the policy is consistent.

`compute_conflicts()`– Detects conflicts between permissions/prohibitions.

---

## 🤖 `Explainer` Class

Core module for generating natural language explanations using LLMs (HuggingFace API, Ollama, or Transformers). Central to the explanation experiments.

### 🏗️ Constructor

```python
Explainer(model_name, use_ollama=True, ollama_model_name="", load_json_params=False, hf_token ="")
```

- Supports multiple backends: HuggingFace API, Ollama server, local Transformers.

- Auto-selects querying method and initializes tokenizer.

- Optional loading of generation parameters from JSON.

### 🧠 Model Query Functions

`query_ollama(prompt, **kwargs)`– Query an Ollama server.

`query_transformers(prompt, **kwargs)`– Use a local Transformers model.

`query_hf(prompt, **kwargs)`– Query HuggingFace inference API.

`clean_answer(answer, prompt)`– Cleans model response from artifacts.

### 🛠️ Prompting Strategies

`chat(initial_prompt, user_prompt="", ...)`– Zero-shot or iterative conversation.

`interactive_prompting(evaluator, access, iterations=1)`– Interactive querying.

`few_shot_prompting(evaluator, access)`– Few-shot explanation prompting.

### ⚙️ Tuning & Optimization

`load_from_json()`– Load generation parameters from JSON.

`select_random_params(trial)`– Select trial-specific generation parameters.

`objective(trial, policy)`– Objective function for model tuning.

`optimize_model(n_trials, policy)`– Optimize model settings via trials.

---

## 📏 `Evaluator` Class

Evaluates LLM-generated explanations using **logical** and **linguistic** criteria. Central to the paper's contribution.

### 🏗️ Constructor

```python
Evaluator()
```
- Loads BART-MNLI model for natural language inference (NLI).
- Loads LanguageTool for grammar checking (with fallback).
- Detects GPU availability for acceleration.

### 🧠 Evaluation Methods

`get_nli_score(fact, text)` – Entailment score of a fact given explanation.

`evaluate_answer_logic_similarity_outcome_granted(text, explanations)` – Evaluates logic when access is granted.

`evaluate_answer_logic_similarity_outcome_denied(text, explanations)` – Evaluates logic when access is denied.

`evaluate_grammaticality(text)` – Grammar error count via LanguageTool.

`evaluate_readability(text)` – Returns readability score (e.g., Flesch).

`get_hallucination_score(text, facts)` – Hallucination detection based on fact grounding.

`run_evaluations(access, answer, explanations)` – Runs all evaluations and returns dictionary of scores.

