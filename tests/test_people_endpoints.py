# =====================================================================
# FILE: test_people_endpoints.py
#
# Minimal endpoint test script for People API client.
# - Assumes your config is valid at ./config/sandbox.config.ini (adjust as needed).
# - Uses the library as currently implemented: Session + People + Person.
# =====================================================================

from __future__ import annotations

from teamdynamix.session import Session
from teamdynamix.people import People


def main() -> None:
    # 0) Initialize session + client
    session = Session("./config/sandbox.config.ini")
    people = People(session)

    # Optional: prime authentication explicitly (useful for deterministic testing)
    session.authenticate()

    # 1) Search a person based on the string "000000"
    search_text = "000000"
    results = people.search(search_text, max_results=10)

    if not results:
        print(f"No people matched search text: {search_text}")
        return

    # Choose the first match for this test
    person = results[0]
    if not person.UID:
        print("Search result missing UID; cannot proceed.")
        return

    uid = person.UID
    print(f"[1] Search OK: UID={uid}, FullName={person.FullName}, Email={person.PrimaryEmail}")

    # 2) Get the full user object (raw dict) via People.get_raw + typed view via People.get
    typed_person = people.get(uid)
    raw_person = people.get_raw(uid)

    if typed_person is None or raw_person is None:
        print(f"[2] People.get/get_raw returned no data for UID={uid}")
        return

    print(f"[2] Get OK: FirstName={typed_person.FirstName!r}, LastName={typed_person.LastName!r}, UserName={typed_person.UserName!r}")

    # Capture original FirstName from raw payload (authoritative for patching)
    original_first_name = raw_person.get("FirstName") or ""
    if not isinstance(original_first_name, str):
        original_first_name = str(original_first_name)

    # 3) Update the User's FirstName by appending "TestPatch"
    suffix = "TestPatch"
    if original_first_name.endswith(suffix):
        patched_first_name = original_first_name
    else:
        patched_first_name = f"{original_first_name}{suffix}"

    print(f"[3] Patching FirstName -> {patched_first_name!r}")
    people.update(uid, {"FirstName": patched_first_name})

    # Confirm (re-fetch)
    verify_after_patch = people.get_raw(uid) or {}
    print(f"[3] Verify FirstName: {verify_after_patch.get('FirstName')!r}")

    # 4) Update the User's FirstName by removing "TestPatch" from the end
    current_first_name = verify_after_patch.get("FirstName") or ""
    if not isinstance(current_first_name, str):
        current_first_name = str(current_first_name)

    if current_first_name.endswith(suffix):
        reverted_first_name = current_first_name[: -len(suffix)]
    else:
        # If suffix is not present, revert to original to be safe
        reverted_first_name = original_first_name

    print(f"[4] Reverting FirstName -> {reverted_first_name!r}")
    people.update(uid, {"FirstName": reverted_first_name})

    # Confirm (re-fetch)
    verify_after_revert = people.get_raw(uid) or {}
    print(f"[4] Verify FirstName: {verify_after_revert.get('FirstName')!r}")

    # 5) List the user's functional roles
    roles_before = people.list_functional_roles(uid)
    print(f"[5] Functional roles before: {roles_before}")

    # 6) Add the user to Functional Role with ID 6
    role_id = 6
    print(f"[6] Adding functional role {role_id} (is_primary=False)")
    people.add_functional_role(uid, role_id, is_primary=False)

    roles_after_add = people.list_functional_roles(uid)
    print(f"[6] Functional roles after add: {roles_after_add}")

    # 7) Remove Functional Role with ID 6 from the User
    print(f"[7] Removing functional role {role_id}")
    people.remove_functional_role(uid, role_id)

    roles_after_remove = people.list_functional_roles(uid)
    print(f"[7] Functional roles after remove: {roles_after_remove}")

    print("Done.")


if __name__ == "__main__":
    main()
