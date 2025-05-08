# 📦 Dataset Generation for OrBAC Ontology

This module is responsible for generating OWL examples that instantiate OrBAC policy cases, covering both permissions and prohibitions, with varying numbers of supports and intentional conflicts.

---

## 🔧 How Examples Are Generated

Each generated dataset simulates conflict scenarios by:

1. Selecting a random combination of **Subject**, **Action**, and **Object**.
2. Creating multiple **supports** for both:
   - `Permission` statements with supporting axioms: `Employ`, `Use`, `Consider`, `Define`.
   - `Prohibition` statements with similar supporting axioms.
3. The number of support rules per policy is randomly chosen between 1 and 5.
4. A preference relation `isPreferredTo` is added between:
   - Up vs. down **Roles**
   - Up vs. down **Contexts**
5. All elements are added to an RDF graph and serialized as `.owl`.

### propagation of preference relations

The generated `.owl` files contain only preferences between Roles and Contexts, however, for OrBAC reasoning one needs preference between predicates. Therefore, the preference is propagated from roles to `Employ` relations, and from contexts to `Define` relations. Prefrences are also inferred from role hierarchies.

This step is achieved using some predefined SWRL rules:

```bash
- orbac-owl:Context(?context1) ^ orbac-owl:Context(?context2) ^ orbac-owl:isPreferredTo(?context1, ?context2) ^ orbac-owl:definesContext(?define1, ?context1) ^ orbac-owl:definesContext(?define2, ?context2) -> orbac-owl:isPreferredTo(?define1, ?define2)

- orbac-owl:Role(?role1) ^ orbac-owl:Role(?role2) ^ orbac-owl:isPreferredTo(?role1, ?role2) ^ orbac-owl:employesRole(?employ1, ?role1) ^ orbac-owl:employesRole(?employ2, ?role2) -> orbac-owl:isPreferredTo(?employ1, ?employ2)

- orbac-owl:hasParent(?R1, ?R2) -> orbac-owl:isPreferredTo(?R1, ?R2)
```

SWRL rules are executed efficiently using [Drools](https://github.com/protegeproject/swrlapi-drools-engine): (also found in Protege)

Proctor, M.: Drools: a rule engine for complex event processing. In: Applications of Graph Transformations with Industrial Relevance: 4th International Symposium, AGTIVE 2011, Budapest, Hungary, October 4-7, 2011, Revised Selected and Invited Papers 4. pp. 2–2. Springer (2012)

## Source of data elements

We used two different domain sets of basic entities given randomly:

- Staff-exchange dataset.
- Hospital dataset (classical example usually used in OrBAC papers).

Both are provided as `.json` files, similar file structure can be followed to generate similar examples.

To generate data:

```bash
python dataset_generation/generate_datasets.py --file path/to/input.json --conflicts <number_of_conflicts>
```

## Table: Generated Datasets

| Dataset         | #Permission | #Prohibition | #Employ | #Consider | #Use | #Define | #Conflicts |
|-----------------|-------------|--------------|---------|-----------|------|---------|------------|
| staff−exchange  | 94          | 92           | 174     | 15        | 181  | 182     | 76         |
| hospital       | 100         | 102          | 185     | 18        | 151  | 195     | 50         |