"""designating the classes Invester and
nestled within the class Project"""
from dataclasses import dataclass, field, asdict
from typing import List, Optional


@dataclass
class Invester:
    """Class that contains all relevant info to a individual"""

    username: str | int
    password: str | int
    projects: List["Invester.Project"] = field(default_factory=list)

    def add_project(self, project_data: dict):
        """Add a project to the list"""
        project = self.Project(**project_data)
        self.projects.append(project)

    def get_project(self, index: int) -> Optional["Invester.Project"]:
        """Retrieves given project based on index"""
        if 0 <= index < len(self.projects):
            return self.projects[index]
        return None

    def list_projects(self) -> List["Invester.Project"]:
        """Function to make list of projects"""
        return self.projects

    def to_dict(self):
        """Converts class instance into dictionary"""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict):
        """Returns dictionary into class instance"""
        invester = cls(username=data["username"], password=data["password"])
        for project_data in data["projects"]:
            invester.add_project(project_data)
        return invester

    @dataclass
    class Project:
        """Contains all the different projects a
        individual invester have in their portfolio"""
        year: int
        initial_investment: float
        incoming_payments: float
        outgoing_payments: float
        residual: float
        restricted_equity: float
        discount_rate: float
        tax_rate: float
        outgoing_payments_0: Optional[float] = 0.0
        depreciation: float = 0.0
        net_present_value: int = 0
        accumulated_net_value_list: list = field(default_factory=list)
