from dataclasses import dataclass,field

@dataclass
class Finding:
    rule_id:str
    title:str
    severity:str
    resource_type:str
    resource_id:str
    evidence:str
    remediation:str
    standards: list[str]=field(default_factory=list)


