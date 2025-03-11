class Permission:
    def __init__(self, org_perm, r_perm, a_perm, v_perm, c_perm):
        self.accessTypeOrganisation = org_perm
        self.accessTypeRole = r_perm
        self.accessTypeActivity = a_perm
        self.accessTypeView = v_perm
        self.accessTypeContext = c_perm

    def __eq__(self, __value: object) -> bool:
        if not isinstance(__value, Permission):
            return False
        return (self.accessTypeOrganisation == __value.accessTypeOrganisation and
                self.accessTypeRole == __value.accessTypeRole and
                self.accessTypeActivity == __value.accessTypeActivity and
                self.accessTypeView == __value.accessTypeView and
                self.accessTypeContext == __value.accessTypeContext)

    def __hash__(self):
        return hash((self.accessTypeOrganisation, 
                     self.accessTypeRole, 
                     self.accessTypeActivity, 
                     self.accessTypeView, 
                     self.accessTypeContext))

class Prohibition:
    def __init__(self, org_proh, r_proh, a_proh, v_proh, c_proh):
        self.accessTypeOrganisation = org_proh
        self.accessTypeRole = r_proh
        self.accessTypeActivity = a_proh
        self.accessTypeView = v_proh
        self.accessTypeContext = c_proh

    def __eq__(self, __value: object) -> bool:
        if not isinstance(__value, Prohibition):
            return False
        return (self.accessTypeOrganisation == __value.accessTypeOrganisation and
                self.accessTypeRole == __value.accessTypeRole and
                self.accessTypeActivity == __value.accessTypeActivity and
                self.accessTypeView == __value.accessTypeView and
                self.accessTypeContext == __value.accessTypeContext)

    def __hash__(self):
        return hash((self.accessTypeOrganisation, 
                     self.accessTypeRole, 
                     self.accessTypeActivity, 
                     self.accessTypeView, 
                     self.accessTypeContext))

class Employ:
    def __init__(self, org, r, s):
        self.employesEmployer = org
        self.employesRole = r
        self.employesEmployee = s

    def __eq__(self, __value: object) -> bool:
        if not isinstance(__value, Employ):
            return False
        return (self.employesEmployer == __value.employesEmployer and
                self.employesRole == __value.employesRole and
                self.employesEmployee == __value.employesEmployee)

    def __hash__(self):
        return hash((self.employesEmployer, 
                     self.employesRole, 
                     self.employesEmployee))

class Use:
    def __init__(self, org, v, o):
        self.usesEmployer = org
        self.usesObject = o
        self.usesView = v

    def __eq__(self, __value: object) -> bool:
        if not isinstance(__value, Use):
            return False
        return (self.usesEmployer == __value.usesEmployer and
                self.usesObject == __value.usesObject and
                self.usesView == __value.usesView)

    def __hash__(self):
        return hash((self.usesEmployer, 
                     self.usesObject, 
                     self.usesView))

class Consider:
    def __init__(self, org, a, alpha):
        self.considersOrganisation = org
        self.considersAction = alpha
        self.considersActivity = a

    def __eq__(self, __value: object) -> bool:
        if not isinstance(__value, Consider):
            return False
        return (self.considersOrganisation == __value.considersOrganisation and
                self.considersAction == __value.considersAction and
                self.considersActivity == __value.considersActivity)

    def __hash__(self):
        return hash((self.considersOrganisation, 
                     self.considersAction, 
                     self.considersActivity))

class Define:
    def __init__(self, org, s, a, o, c):
        self.definesOrganisation = org
        self.definesSubject = s
        self.definesAction = a
        self.definesObject = o
        self.definesContext = c

    def __eq__(self, __value: object) -> bool:
        if not isinstance(__value, Define):
            return False
        return (self.definesOrganisation == __value.definesOrganisation and
                self.definesSubject == __value.definesSubject and
                self.definesAction == __value.definesAction and
                self.definesObject == __value.definesObject and
                self.definesContext == __value.definesContext)

    def __hash__(self):
        return hash((self.definesOrganisation, 
                     self.definesSubject, 
                     self.definesAction, 
                     self.definesObject, 
                     self.definesContext))

class subOrganisationOf:
    def __init__(self, org_1, org_2):
        self.org_1 = org_1
        self.org_2 = org_2

    def __eq__(self, __value: object) -> bool:
        if not isinstance(__value, subOrganisationOf):
            return False
        return (self.org_1 == __value.org_1 and
                self.org_2 == __value.org_2)
    
    def __hash__(self):
        return hash((self.org_1, self.org_2))
    
