## Overview of the OrBAC Model

- **Core Concepts in Access Control**:
  - **Subjects**: Represent users performing actions.
  - **Objects**: Passive entities like resources or files.
  - **Actions**: Operations performed by subjects on objects (e.g., read, write).

- **OrBAC Model**:
  - Introduces abstract groupings for these concepts:
    - **Roles**: Groups of subjects with similar functions.
    - **Views**: Groups of objects with shared properties.
    - **Activities**: Grouped actions that share principles.
  - Adds **Organizations**: Defines rules within specific organizational contexts.

- **Relationship Definitions**:
  - **Employ(org, s, r)**: Subject “s” plays role “r” in organization “org.”
  - **Use(org, o, v)**: Object “o” is part of view “v” within organization “org.”
  - **Consider(org, α, a)**: Organization “org” treats action “α” as part of activity “a.”

- **Dynamic Contexts**:
  - Contexts determine when privileges apply (e.g., time, emergency).
  - **Define(org, s, α, o, c)**: Context “c” applies for subject “s” performing action “α” on object “o” in organization “org.”

- **Policy Rules**:
  - **Abstract Privileges**: Defined by permissions, prohibitions, obligations, and recommendations.
  - Example: **Permission(org, r, a, v, c)** grants role “r” permission for activity “a” on view “v” within context “c” in organization “org.”

- **Concrete Privileges**:
  - Derived permissions for specific subjects, actions, and objects.
  - Example: **Is-permitted(s, α, o)** means subject “s” is allowed to perform action “α” on object “o.”