"""designating the classes Invester and
nestled within the class Project"""
from dataclasses import dataclass, field, asdict
from typing import List, Optional
# from utils import generate_random_id


@dataclass
class Investor:
    """Class that contains all relevant info to a individual"""
    username: str | int
    password: str | int
    # user_id: str = field(init=False)
    projects: List["Investor.Project"] = field(default_factory=list)

    def add_project(self, project_data: dict):
        """Add a project to the list"""
        project = self.Project(**project_data)
        self.projects.append(project)

    def get_project(self, index: int) -> Optional["Investor.Project"]:
        """Retrieves given project based on index"""
        if 0 <= index < len(self.projects):
            return self.projects[index]
        return None

    def list_projects(self) -> List["Investor.Project"]:
        """Function to make list of projects"""
        return self.projects

    def to_dict(self):
        """Converts class instance into dictionary"""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict):
        """Returns dictionary into class instance."""
        investor = cls(username=data["username"], password=data["password"])
        allowed_keys = {
            field.name for field in Investor.Project.__dataclass_fields__.values()  # type: ignore[attr-defined]  # noqa: E501  # pylint: disable=no-member,line-too-long
        }

        for project_data in data["projects"]:
            cleaned_data = {
                k: v for k, v in project_data.items() if k in allowed_keys
            }
            investor.add_project(cleaned_data)

        return investor

    @classmethod
    def from_list(cls, data: list):
        """Return last list entry into class instance"""
        investor = cls(
            username=data[-1]["username"], password=data[-1]["password"]
        )
        for project_data in data[-1]["projects"]:
            investor.add_project(project_data)
        return investor

    @dataclass
    class Project:
        """Contains all the different projects a
        individual invester have in their portfolio"""
        project_name: str
        lifetime: int
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
        break_even: Optional[int] = None
