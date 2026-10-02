import re

def fix_stripe():
    path = 'numista_backend/tests/test_stripe_auth.py'
    with open(path, 'r', encoding='utf-8') as f:
        c = f.read()
    
    # Insert import
    c = c.replace('from unittest.mock import patch, MagicMock', 'from unittest.mock import patch, MagicMock\nfrom main import app\nfrom routes.deps import get_current_user\nfrom fastapi import HTTPException')
    
    # Fix passport pdf route
    c = c.replace('/api/transfers/pdf/', '/api/transfer/passport-pdf/')
    c = c.replace(\"patch('main.generate_certificate_of_transfer')\", \"patch('services.passport_pdf_generator.generate_passport_pdf')\")
    
    c = c.replace(\"with patch('routes.deps.get_current_user') as mock_user,\", \"app.dependency_overrides[get_current_user] = lambda: {'uid': 'userA', 'email': 'userA@numista.ai'}\n    with\")
    c = c.replace(\"with patch('routes.deps.get_current_user') as mock_user:\", \"app.dependency_overrides[get_current_user] = lambda: {'uid': 'userA', 'email': 'userA@numista.ai'}\n    with patch('main.db') as mock_db:\")

    c = c.replace(\"mock_user.return_value = {'uid': 'userA', 'email': 'userA@numista.ai'}\", \"\")
    
    with open(path, 'w', encoding='utf-8') as f:
        f.write(c)

def fix_grade():
    path = 'numista_backend/tests/test_grade_flag_resolve.py'
    with open(path, 'r', encoding='utf-8') as f:
        c = f.read()
    
    c = c.replace('from unittest.mock import patch, MagicMock', 'from unittest.mock import patch, MagicMock\nfrom main import app\nfrom routes.deps import get_current_user, require_admin_user\nfrom fastapi import HTTPException')
    c = c.replace('/api/admin/grade-flags/', '/api/admin/grade_flags/')
    
    with open(path, 'w', encoding='utf-8') as f:
        f.write(c)

fix_stripe()
fix_grade()
