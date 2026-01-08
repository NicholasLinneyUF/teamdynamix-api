#!/usr/bin/env python3
"""
add_resources_to_project.py
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Uses the up‑to‑date *teamdynamix* helper library to add a list of
resource UIDs (read from a CSV file) to a specific Project.
The script now:

* Uses the bundled :class:`teamdynamix.Session` for authentication and
  HTTP transport.
* Uses the library’s :class:`teamdynamix.Logger` for all log output
  (no direct ``requests`` calls are required).
* Reads the CSV file under ``./data/resources.csv`` – the column name
  is ignored and the first non‑UUID row is treated as a header.
* Adds a brief ``time.sleep`` between requests to be courteous to the
  TeamDynamix API.

The script is purposely lightweight – it’s all in a single
``scripts/add_resources_to_project.py`` file.
"""

from __future__ import annotations

import csv
import uuid
import time
from pathlib import Path
from typing import Iterable, List

# The new helper library lives in the ``teamdynamix`` package
from teamdynamix import Session  # type: ignore[arg-type]
from teamdynamix.session import Session as SessionType

# --------------------------------------------------------------------------- #
# Configuration – tweak these values for your environment
# --------------------------------------------------------------------------- #
PROJECT_ID: int = 52 # Projects 52, 53, and 54
CSV_PATH: Path = Path("data") / "resources.csv"
# --------------------------------------------------------------------------- #
# Helper functions
# --------------------------------------------------------------------------- #
def is_valid_uuid(value: str) -> bool:
    """Return ``True`` if *value* is a valid UUID string; otherwise ``False``."""
    try:
        uuid.UUID(value)
        return True
    except ValueError:
        return False


def get_resource_uids(csv_path: Path, session: SessionType) -> List[str]:
    """
    Read *csv_path* and return a list of the resource UIDs found in the
    first column.  The first row is inspected; if it does not contain a
    UUID it is treated as a header and skipped.

    Parameters
    ----------
    csv_path
        Path to the input CSV file (must exist).
    session
        The :class:`teamdynamix.Session` instance – used only for logging
        feedback while parsing the file.

    Returns
    -------
    list[str]
        All valid UUIDs found in the CSV.
    """
    uids: List[str] = []

    with csv_path.open(newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        for i, row in enumerate(reader):
            if not row:  # skip blank lines
                continue
            uid: str = row[0].strip()
            if not uid:
                continue

            # If the first line does not look like a UUID it’s probably a header
            if i == 0 and not is_valid_uuid(uid):
                session.log(
                    f"Header detected (row 1 has non‑UUID value '{uid}'); skipping this row."
                )
                continue

            if not is_valid_uuid(uid):
                session.log(
                    f"Skipping row {i + 1}: value '{uid}' is not a valid UUID."
                )
                continue

            uids.append(uid)

    return uids


def add_resource_to_project(
    session: SessionType,
    project_id: int,
    resource_id: str,
) -> None:
    """
    POST the ``/api/projects/{project_id}/resources/{resource_id}``
    endpoint to add *resource_id* to *project_id*.

    The API expects an empty POST body; the query string tells TeamDynamix
    whether notifications should be sent.
    """
    path = (
        f"/api/projects/{int(project_id)}/resources/{resource_id}"
        "?notifyManagers=false&notifyResource=false"
    )
    # ``session.request`` automatically prepends ``base_url`` and injects
    # the Authorization header, so we only need to supply the method,
    # path, and an empty ``json`` payload.
    resp = session.request("POST", path, json={})
    if resp.ok:
        session.log(
            f"[OK] Added UID {resource_id} – Server responded with {resp.status_code}."
        )
    else:
        session.log(
            f"[XX] Failed to add UID {resource_id} – "
            f"{resp.status_code}: {resp.text}"
        )


def main() -> None:
    """
    Driver routine.  The script flow is:

    1.  Create a :class:`teamdynamix.Session` using the sandbox config.
    2.  Read all resource UIDs from the CSV file.
    3.  Add each UID to the target project, logging each attempt.
    """
    # 1.  Initialise the session – ``Session`` loads credentials
    #    from the provided configuration file.
    session = Session("./config/sandbox.config.ini")

    # 2.  Load the UID list
    uids = get_resource_uids(CSV_PATH, session)
    if not uids:
        session.log("No UIDs found in the CSV – aborting.")
        return

    # 3.  Add every UID to the project, pausing between calls
    for uid in uids:
        time.sleep(1.2)  # give the API time to settle
        add_resource_to_project(session, PROJECT_ID, uid)


# --------------------------------------------------------------------------- #
# Entry point
# --------------------------------------------------------------------------- #
if __name__ == "__main__":
    main()