# OrBAC ontology project 

These files contain appendices of the OrBAC ontology:

## Ontology files

The files under the folder `ontology` contain both a version of the ontology with elements (or individuals) of an example `orbac-STARWARS.owl`, this version is used to illustrate the queries and the used algorithms. 
And a version of the ontology without any individuals (to be shared and published later).

## SPARQL queries:

The used queries can be found in the directory `queries.sparql` :

- `inference_query.sparql` : used to infer all tuples of the form (subject,action, object) which has a concrete permission.
- `prohibition_inference_query.sparql` : used to infer all tuples of the form (subject,action, object) which has a concrete prohibition.
- `consistency_checking.sparql` : a query used to check if the orbac knowledge base is consistenct, it returns True if both a permission and a prohibition are inferred for the same (subject,action, object).
- `conflicts_query.sparql` : returns all the conflicts of an orbac knowledge base. Similar to `consistency_checking.sparql` but instead of a truth value it returns subsets.
- `supports_query.sparql` : returns all the supports of a permission for a given (subject,action, object).
- `prohibition_supports_query.sparql` : returns all the supports of a prohibition for a given (subject,action, object).
- `dominance_query.sparql` : checks if an individual is strictly preferred to another.

## Checking acceptance of a permission

We developed an algorithm to check if a permission is accepted in the case the orbac knwoledge base is inconsistent. The method is inspired by the notion of acceptance defined in [1] for [__DL-Lite_R__](https://link.springer.com/article/10.1007/s10817-007-9078-x) lightweight ontologies. 

The algorithm is implemented in python and provided in `compute-accepted.py`.

The different methods used in this work rely on the [__RDFLib__](https://github.com/RDFLib/rdflib), which is a python library to read from the OWL ontology.

## Explanation of the accepatnce decisions


## References:

[1] A. Laouar, S. Belabbes, S. Benferhat, Tractable Closure-Based Possibilistic Repair for Partially Ordered DL-Lite Ontologies, in: European Conference on Logics in Artificial Intelligence, Springer, 2023, pp. 353–368