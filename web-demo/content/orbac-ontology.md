## The OrBAC Ontology

- **Entities in OrBAC**:
  - **Concrete Entities**:
    - **Objects**: Represented by the class `orbac:Object`.
    - **Subjects**: Represented by the class `orbac:Subject`.
    - **Actions**: Represented by the class `orbac:Action`.
    - **Organisations**: Represented by the class `orbac:Organisation`, and also a subclass of `orbac:Subject`.
  - **Abstract Entities**:
    - **Roles**: Represented by the class `orbac:Role`.
    - **Views**: Represented by the class `orbac:View`.
    - **Activities**: Represented by the class `orbac:Activity`.
  - **Contexts**:
    - Represented by the class `orbac:Context`.

- **Policy Rules**:
  - **Access Types**:
    - Includes the classes `orbac:Permission`, `orbac:Prohibition`, `orbac:Obligation`, and `orbac:Recommendation`.
    - All access types are subclasses of `orbac:AccessType`.
  - **Object Properties**:
    - `orbac:accessTypeOrg`: Links an access type with an organisation.
    - `orbac:accessTypeRole`: Links an access type with a role.
    - `orbac:accessTypeActivity`: Links an access type with an activity.
    - `orbac:accessTypeView`: Links an access type with a view.
    - `orbac:accessTypeContext`: Links an access type with a context.

- **Connection Rules**:
  - Represented by the classes `orbac:Consider`, `orbac:Use`, `orbac:Employ`, and `orbac:Define` (subclasses of `orbac:ConnectionRule`).
  - **Consider** is the domain of the properties: `orbac:considersActivity`, `orbac:considersAction`, `orbac:considersOrg`.
  - **Use** is the domain of the properties: `orbac:usesView`, `orbac:usesObject`, `orbac:usesEmployer`.
  - **Employ** is the domain of the properties: `orbac:employesRole`, `orbac:employesEmployee`, `orbac:employesEmployer`.
  - **Define** is the domain of the properties: `orbac:definesSubject`, `orbac:definesAction`, `orbac:definesObject`, `orbac:definesContext`.
