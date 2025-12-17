# =====================================================================
# FILE: src/teamdynamix/projects.py
# =====================================================================
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from .session import Session
from . import PatchPayload


@dataclass(slots=True)
class Project:
    """
    Minimal Project model.

    Keep this intentionally lean: the SDK should stay close to the vendor API
    surface. If callers need additional fields, they can access raw dicts from
    session.request(...) or we can expand this dataclass later with proven needs.
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
        data = self.session.request("POST", f"{self._base_path}/search", json=criteria) or []
        if not isinstance(data, list):
            return []
        return [Project.from_dict(item) for item in data if isinstance(item, dict)]

    def get(self, project_id: int) -> Project:
        """
        GET /api/projects/{id}
        """
        self.session.log(f"Projects.get: id={project_id}")
        data = self.session.request("GET", f"{self._base_path}/{project_id}")
        if not isinstance(data, dict):
            return Project()
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
        data = self.session.request("POST", self._base_path, params=params, json=project_data)
        if not isinstance(data, dict):
            return Project()
        return Project.from_dict(data)

    def edit(self, project_id: int, updates: Dict[str, Any]) -> Project:
        """
        POST /api/projects/{id}
        (TDX uses POST for edit on this resource.)
        """
        self.session.log(f"Projects.edit: id={project_id}, keys={list(updates.keys())}")
        data = self.session.request("POST", f"{self._base_path}/{project_id}", json=updates)
        if not isinstance(data, dict):
            return Project()
        return Project.from_dict(data)

    def patch(
        self,
        project_id: int,
        operations: List[PatchPayload] | Dict[str, Any],
    ) -> Project:
        """
        PATCH /api/projects/{id}

        Accepts either:
          - a list[PatchPayload] (explicit JSON Patch operations), OR
          - a dict[str, Any] which will be converted into JSON Patch "replace"
            operations by Transport (shared behavior across modules).
        """
        if isinstance(operations, list):
            payload = [op.__dict__ for op in operations]
        else:
            payload = operations  # Transport will convert dict -> JSON Patch list for PATCH

        self.session.log(f"Projects.patch: id={project_id}")
        data = self.session.request("PATCH", f"{self._base_path}/{project_id}", json=payload)
        if not isinstance(data, dict):
            return Project()
        return Project.from_dict(data)

    # ---------------------------
    # Project Feed endpoints
    # ---------------------------

    def get_feed(self, project_id: int) -> List[Dict[str, Any]]:
        """
        GET /api/projects/{id}/feed
        """
        self.session.log(f"Projects.get_feed: project_id={project_id}")
        data = self.session.request("GET", f"{self._base_path}/{project_id}/feed") or []
        return data if isinstance(data, list) else []

    def add_feed(self, project_id: int, body: str) -> Dict[str, Any]:
        """
        POST /api/projects/{projectId}/feed
        Body: { "Body": "<string>" }
        """
        payload = {"Body": body}
        self.session.log(f"Projects.add_feed: project_id={project_id}")
        data = self.session.request("POST", f"{self._base_path}/{project_id}/feed", json=payload)
        return data if isinstance(data, dict) else {}

    # ---------------------------
    # Plan / task endpoints
    # ---------------------------

    def get_plan(self, project_id: int, plan_id: int) -> Dict[str, Any]:
        """
        GET /api/projects/{projectId}/plans/{planId}
        """
        self.session.log(f"Projects.get_plan: project_id={project_id}, plan_id={plan_id}")
        data = self.session.request("GET", f"{self._base_path}/{project_id}/plans/{plan_id}")
        return data if isinstance(data, dict) else {}

    def edit_task(
        self,
        project_id: int,
        plan_id: int,
        task_id: int,
        updates: Dict[str, Any],
        *,
        notify_new_resources: bool = False,
    ) -> Dict[str, Any]:
        """
        POST /api/projects/{projectId}/plans/{planId}/tasks/{taskId}/edit
        Query:
          notifyNewResources (bool)
        """
        params = {"notifyNewResources": str(bool(notify_new_resources)).lower()}
        self.session.log(
            f"Projects.edit_task: project_id={project_id}, plan_id={plan_id}, task_id={task_id}, params={params}"
        )
        data = self.session.request(
            "POST",
            f"{self._base_path}/{project_id}/plans/{plan_id}/tasks/{task_id}/edit",
            params=params,
            json=updates,
        )
        return data if isinstance(data, dict) else {}

    # ---------------------------
    # Project Issue Feed endpoints (subset)
    # ---------------------------

    def get_issue_feed(self, project_id: int, issue_id: int) -> List[Dict[str, Any]]:
        """
        GET /api/projects/{projectId}/issues/{issueId}/feed
        """
        self.session.log(f"Projects.get_issue_feed: project_id={project_id}, issue_id={issue_id}")
        data = self.session.request(
            "GET",
            f"{self._base_path}/{project_id}/issues/{issue_id}/feed",
        ) or []
        return data if isinstance(data, list) else []

    def add_issue_comment(
        self,
        project_id: int,
        issue_id: int,
        comment_payload: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        POST /api/projects/{projectId}/issues/{issueId}/feed

        Payload shape (per Postman examples) typically includes:
          Comments, Notify, IsPrivate, IsRichHtml, IsCommunication
        We keep it as a dict to match the vendor surface and avoid guessing fields.
        """
        self.session.log(f"Projects.add_issue_comment: project_id={project_id}, issue_id={issue_id}")
        data = self.session.request(
            "POST",
            f"{self._base_path}/{project_id}/issues/{issue_id}/feed",
            json=comment_payload,
        )
        return data if isinstance(data, dict) else {}
