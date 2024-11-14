## Overview of the OrBAC Ontology

- **Entities in OrBAC**:
  - **Concrete Entities**:
    - **Objects**: Represented by `orbac:Object`.
    - **Subjects**: Represented by `orbac:Subject`.
    - **Actions**: Represented by `orbac:Action`.
    - **Organisations**: Represented by `orbac:Organisation`, also a subclass of `orbac:Subject`.
  - **Abstract Entities**:
    - **Roles**: Represented by `orbac:Role`.
    - **Views**: Represented by `orbac:View`.
    - **Activities**: Represented by `orbac:Activity`.
  - **Contexts**:
    - Represented by `orbac:Context`.

- **Policy Rules**:
  - **Access Types**:
    - Includes `orbac:Permission`, `orbac:Prohibition`, `orbac:Obligation`, and `orbac:Recommendation`.
    - All access types are subclasses of `orbac:AccessType`.
  - **Object Properties**:
    - **orbac:accessTypeOrg**: Links an access type with an organisation.
    - **orbac:accessTypeRole**: Links an access type with a role.
    - **orbac:accessTypeActivity**: Links an access type with an activity.
    - **orbac:accessTypeView**: Links an access type with a view.
    - **orbac:accessTypeContext**: Links an access type with a context.

- **Connection Rules**:
  - Represented by `orbac:Consider`, `orbac:Use`, `orbac:Employ`, and `orbac:Define` (subclasses of `orbac:ConnectionRule`).
  - **Consider**:
    - Properties: `orbac:considersActivity`, `orbac:considersAction`, `orbac:considersOrg`.
  - **Use**:
    - Properties: `orbac:usesView`, `orbac:usesObject`, `orbac:usesEmployer`.
  - **Employ**:
    - Properties: `orbac:employesRole`, `orbac:employesEmployee`, `orbac:employesEmployer`.
  - **Define**:
    - Properties: `orbac:definesSubject`, `orbac:definesAction`, `orbac:definesObject`, `orbac:definesContext`.
