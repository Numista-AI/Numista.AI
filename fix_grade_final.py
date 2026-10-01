import re

def fix():
    path = "numista_backend/tests/test_grade_flag_resolve.py"
    with open(path, "r", encoding="utf-8") as f:
        c = f.read()

    c = c.replace("from unittest.mock import patch, MagicMock", "from unittest.mock import patch, MagicMock\nfrom main import app\nfrom routes.deps import get_current_user, require_admin_user\nfrom fastapi import HTTPException")
    c = c.replace("/api/admin/grade-flags/", "/api/admin/grade_flags/")

    # Setup the mock replacement manually
    # Replace the with patch... lines entirely
    lines = c.split("\n")
    out = []
    i = 0
    while i < len(lines):
        if "def test_resolve_flag" in lines[i]:
            out.append(lines[i])
            i += 1
            # Next lines are the with patch
            while "with patch" in lines[i] or "patch(" in lines[i]:
                i += 1
            # We reached the end of with patch block
            
            # Now we add our app.dependency_overrides
            out.append("    app.dependency_overrides[get_current_user] = lambda: {'uid': 'admin1', 'email': 'admin@numista.ai'}")
            out.append("    app.dependency_overrides[require_admin_user] = lambda: {'uid': 'admin1', 'email': 'admin@numista.ai'}")
            
            if "test_resolve_flag_non_admin" in out[-3]:
                out.pop() # remove the last line
                out.pop()
                out.append("    app.dependency_overrides[get_current_user] = lambda: {'uid': 'user1', 'email': 'user@numista.ai'}")
                out.append("    def raise_403(): raise HTTPException(status_code=403, detail='Admin required')")
                out.append("    app.dependency_overrides[require_admin_user] = raise_403")

            out.append("    try:")
            out.append("        with patch('routes.grade_review_routes.db') as mock_db:")
            
            # Skip mock_user and mock_admin assignment lines if present
            while i < len(lines):
                if "mock_user" in lines[i] or "mock_admin" in lines[i] or "from fastapi import HTTPException" in lines[i]:
                    i += 1
                else:
                    break
        elif "assert response.status_code ==" in lines[i]:
            out.append(lines[i])
            out.append("    finally:")
            out.append("        app.dependency_overrides.clear()")
            i += 1
        else:
            out.append(lines[i])
            i += 1

    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(out))

fix()
