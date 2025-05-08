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

Inputs: Subject, Action, Object, RDF Graph, and ontology URI.

Automatically loads related policies and hierarchical context from the RDF graph.

### 🔍 Reasoning Methods

```python
get_supports(accessType)
```
→ Extracts permission or prohibition supports from RDF.

```python
is_strictly_preferred(member1, member2)
```
→ Checks if a member is preferred via isPreferredTo.

```python
check_dominance(subset1, subset2)
```
→ Logical comparison between sets of supports.

```python
check_acceptance()
```
→ Returns boolean for whether the access is accepted.

```python
check_acceptance_query()
```
→ Returns the result from a formal acceptance query.

```python
get_logic_explanations()
```
→ Extracts supports and preference paths explaining the outcome.

###  📈 Hierarchy Handling

```python
get_hierarchical_relations()
```
→ Fills role and context hierarchies from ontology.

```python
compute_hierarchy_supports(accessType=0)
```
→ Generates supports from inferred hierarchies.

```python
check_if_role_from_hierarchy(...)
```
→ Tests if a new role can be inferred through hierarchy.

```python
add_new_employ(...)
```
→ Adds a new Employ support inferred from hierarchy.

### 🗣️ Verbalisation & Prompting

```python
verbalise_outcome()

verbalise_support(support)

verbalise_supports()

verbalise_preferences()

verbalise_logic_explanations(explanations)
```
→ Verbalises relevant parts of an access right.

```python
generate_prompt()
```
→ Builds LLM-compatible prompt from access request.

```python
generate_few_shot_prompt()
```
→ Builds prompt using few-shot examples.

These methods allow the class to interface with LLMs and other NLP-based analysis tools.