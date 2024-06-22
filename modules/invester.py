from dataclasses import dataclass, field, asdict
from typing import List, Optional


@dataclass
class Invester:
    projects: List['Invester.Project'] = field(default_factory=list)

    def add_project(self, project_data: dict):
        project = self.Project(**project_data)
        self.projects.append(project)

    def get_project(self, index: int) -> Optional['Invester.Project']:
        if 0 <= index < len(self.projects):
            return self.projects[index]
        return None

    def list_projects(self) -> List['Invester.Project']:
        return self.projects

    def to_dict(self):
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict):
        invester = cls()
        for project_data in data["projects"]:
            invester.add_project(project_data)
        return invester

    @dataclass
    class Project:
        År: int
        Grundinvestering: float
        Inbetalningar: float
        Utbetalningar: float
        Rest: float
        Rörelsebindandekapital: float
        Kalkylräntan: float
        Skattesats: float
        Utbetalningar_0: Optional[float] = 0.0
        Avskrivningar: float = 0.0
        ar_sista_ack_nuvarde: int = 0
