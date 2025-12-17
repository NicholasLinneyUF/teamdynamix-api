# =====================================================================
# FILE: src/teamdynamix/projects.py
# =====================================================================
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Sequence, Union

from .session import Session
from .transport import PatchPayload


def _as_list(data: Any) -> List[Dict[str, Any]]:
    """
    Normalize an API response into list[dict].

    Rules:
      - None / [] -> []
      - dict -> [dict]
      - list -> only dict entries (filters safely)
      - anything else -> []
    """
    if not data:
        return []
    if isinstance(data, list):
        return [x for x in data if isinstance(x, dict)]
    if isinstance(data, dict):
        return [data]
    return []


def _as_dict(data: Any) -> Optional[Dict[str, Any]]:
    """
    Normalize an API response into dict | None.

    Rules:
      - None / {} -> None
      - dict -> dict
      - anything else -> None
    """
    if not data:
        return None
    return data if isinstance(data, dict) else None


@dataclass(slots=True)
class Project:
    """
    Minimal Project model.

    Keep this intentionally lean: the SDK should stay close to the vendor API
    surface. If callers need additional fields, they can access raw dicts from
    response.json() or we can expand this dataclass later with proven needs.
    """
    ID: Optional[int] = None
    Name: Optional[str] = None
    IsActive: Optional[bool] = None
    Description: Optional[str] = None
    ManagerUid: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Project":
        return cls(
            ID=data.get("ID") or data.get("Id") or data.get("id"),
            Name=data.get("Name"),
            IsActive=data.get("IsActive"),
            Description=data.get("Description"),
            ManagerUid=data.get("ManagerUid") or data.get("ManagerUID"),
        )


class Projects:
    """
    Projects client for TeamDynamix PPM endpoints.

    Pattern: thin endpoint wrapper (keeps vendor API surface recognizable),
    using Session as the facade and Transport as the sole HTTP boundary.
    """

    _base_path = "/api/projects"

    def __init__(self, session: Session):
        self.session = session

    # ---------------------------
    # Core endpoints
    # ---------------------------

    def search(self, criteria: Dict[str, Any]) -> List[Project]:
        """
        POST /api/projects/search
        Returns: list of projects (possibly empty, which is valid).
        """
        self.session.log(f"Projects.search: keys={list(criteria.keys())}")
        resp = self.session.request("POST", f"{self._base_path}/search", json=criteria)
        items = _as_list(resp.json())
        return [Project.from_dict(item) for item in items]

    def get(self, project_id: int) -> Project:
        """
        GET /api/projects/{id}
        """
        self.session.log(f"Projects.get: id={project_id}")
        resp = self.session.request("GET", f"{self._base_path}/{int(project_id)}")
        data = _as_dict(resp.json())
        if data is None:
            raise ValueError("Unexpected response shape from Projects.get (expected dict).")
        return Project.from_dict(data)

    def create(
        self,
        project_data: Dict[str, Any],
        *,
        notify_new_manager: bool = False,
        notify_new_alt_managers: bool = False,
    ) -> Project:
        """
        POST /api/projects
        Query:
          notifyNewManager (bool)
          notifyNewAltManagers (bool)
        """
        params = {
            "notifyNewManager": str(bool(notify_new_manager)).lower(),
            "notifyNewAltManagers": str(bool(notify_new_alt_managers)).lower(),
        }
        self.session.log(f"Projects.create: params={params}, keys={list(project_data.keys())}")
        resp = self.session.request("POST", self._base_path, params=params, json=project_data)
        data = _as_dict(resp.json())
        if data is None:
            raise ValueError("Unexpected response shape from Projects.create (expected dict).")
        return Project.from_dict(data)

    def edit(self, project_id: int, updates: Dict[str, Any]) -> Project:
        """
        POST /api/projects/{id}
        (TDX uses POST for edit on this resource.)
        """
        self.session.log(f"Projects.edit: id={project_id}, keys={list(updates.keys())}")
        resp = self.session.request("POST", f"{self._base_path}/{int(project_id)}", json=updates)
        data = _as_dict(resp.json())
        if data is None:
            raise ValueError("Unexpected response shape from Projects.edit (expected dict).")
        return Project.from_dict(data)

    def patch(
        self,
        project_id: int,
        operations: Union[List[PatchPayload], List[Dict[str, Any]], Dict[str, Any]],
    ) -> Project:
        """
        PATCH /api/projects/{id}

        Accepts:
          - list[PatchPayload]       -> serialized via .to_dict()
          - list[dict[str, Any]]     -> passed through unchanged (assumed already RFC6902)
          - dict[str, Any]           -> passed through; Transport converts dict->JSON Patch list for PATCH
        """
        payload: Any
        if isinstance(operations, dict):
            payload = operations  # Transport converts dict -> patch list (replace ops)
        elif isinstance(operations, list):
            if all(isinstance(op, PatchPayload) for op in operations):
                payload = [op.to_dict() for op in operations]
            elif all(isinstance(op, dict) for op in operations):
                payload = operations
            else:
                raise TypeError("Projects.patch operations list must be all PatchPayload or all dict.")
        else:
            raise TypeError("Projects.patch operations must be a dict, list[PatchPayload], or list[dict].")

        self.session.log(f"Projects.patch: id={project_id}")
        resp = self.session.request("PATCH", f"{self._base_path}/{int(project_id)}", json=payload)
        data = _as_dict(resp.json())
        if data is None:
            raise ValueError("Unexpected response shape from Projects.patch (expected dict).")
        return Project.from_dict(data)

    # ---------------------------
    # Project Feed endpoints
    # ---------------------------

    def get_feed(self, project_id: int) -> List[Dict[str, Any]]:
        """
        GET /api/projects/{id}/feed
        Returns [] when empty (valid).
        """
        self.session.log(f"Projects.get_feed: project_id={project_id}")
        resp = self.session.request("GET", f"{self._base_path}/{int(project_id)}/feed")
        return _as_list(resp.json())

    def add_feed(self, project_id: int, body: str) -> Dict[str, Any]:
        """
        POST /api/projects/{projectId}/feed
        Body: { "Body": "<string>" }
        """
        payload = {"Body": body}
        self.session.log(f"Projects.add_feed: project_id={project_id}")
        resp = self.session.request("POST", f"{self._base_path}/{int(project_id)}/feed", json=payload)
        return _as_dict(resp.json()) or {}

    # ---------------------------
    # Plan / task endpoints
    # ---------------------------

    def get_plan(self, project_id: int, plan_id: int) -> Optional[Dict[str, Any]]:
        """
        GET /api/projects/{projectId}/plans/{planId}
        """
        self.session.log(f"Projects.get_plan: project_id={project_id}, plan_id={plan_id}")
        resp = self.session.request(
            "GET",
            f"{self._base_path}/{int(project_id)}/plans/{int(plan_id)}",
        )
        return _as_dict(resp.json())

    def edit_task(
        self,
        project_id: int,
        plan_id: int,
        task_id: int,
        updates: Dict[str, Any],
        *,
        notify_new_resources: bool = False,
    ) -> Optional[Dict[str, Any]]:
        """
        POST /api/projects/{projectId}/plans/{planId}/tasks/{taskId}/edit
        Query:
          notifyNewResources (bool)
        """
        params = {"notifyNewResources": str(bool(notify_new_resources)).lower()}
        self.session.log(
            f"Projects.edit_task: project_id={project_id}, plan_id={plan_id}, task_id={task_id}, params={params}"
        )
        resp = self.session.request(
            "POST",
            f"{self._base_path}/{int(project_id)}/plans/{int(plan_id)}/tasks/{int(task_id)}/edit",
            params=params,
            json=updates,
        )
        return _as_dict(resp.json())

    # ---------------------------
    # Issue feed endpoints
    # ---------------------------

    def get_issue_feed(self, project_id: int, issue_id: int) -> List[Dict[str, Any]]:
        """
        GET /api/projects/{projectId}/issues/{issueId}/feed
        Returns [] when empty (valid).
        """
        self.session.log(f"Projects.get_issue_feed: project_id={project_id}, issue_id={issue_id}")
        resp = self.session.request(
            "GET",
            f"{self._base_path}/{int(project_id)}/issues/{int(issue_id)}/feed",
        )
        return _as_list(resp.json())

    def add_issue_comment(self, project_id: int, issue_id: int, comment_payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        POST /api/projects/{projectId}/issues/{issueId}/feed
        Body: (per Postman / TDX schema; typically includes "Body")
        """
        self.session.log(f"Projects.add_issue_comment: project_id={project_id}, issue_id={issue_id}")
        resp = self.session.request(
            "POST",
            f"{self._base_path}/{int(project_id)}/issues/{int(issue_id)}/feed",
            json=comment_payload,
        )
        return _as_dict(resp.json()) or {}
