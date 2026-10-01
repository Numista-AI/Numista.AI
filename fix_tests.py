path1 = 'numista_backend/tests/test_stripe_auth.py'
with open(path1, 'r', encoding='utf-8') as f:
    c = f.read()

c = c.replace('from unittest.mock import patch, MagicMock', 'from unittest.mock import patch, MagicMock\nfrom main import app\nfrom routes.deps import get_current_user\nfrom fastapi import HTTPException')
c = c.replace('/api/transfers/pdf/', '/api/transfer/passport-pdf/')
c = c.replace('patch(\'main.generate_certificate_of_transfer\')', 'patch(\'services.passport_pdf_generator.generate_passport_pdf\')')

c = c.replace('with patch(\'routes.deps.get_current_user\') as mock_user, \\\\', 'app.dependency_overrides[get_current_user] = lambda: {\'uid\': \'userA\', \'email\': \'userA@numista.ai\'}\n    with')
c = c.replace('with patch(\'routes.deps.get_current_user\') as mock_user:', 'app.dependency_overrides[get_current_user] = lambda: {\'uid\': \'userA\', \'email\': \'userA@numista.ai\'}\n    with patch(\'main.db\') as mock_db:')
c = c.replace('mock_user.return_value = {\'uid\': \'userA\', \'email\': \'userA@numista.ai\'}', '')

with open(path1, 'w', encoding='utf-8') as f:
    f.write(c)

path2 = 'numista_backend/tests/test_grade_flag_resolve.py'
with open(path2, 'r', encoding='utf-8') as f:
    c2 = f.read()

c2 = c2.replace('from unittest.mock import patch, MagicMock', 'from unittest.mock import patch, MagicMock\nfrom main import app\nfrom routes.deps import get_current_user, require_admin_user\nfrom fastapi import HTTPException')
c2 = c2.replace('/api/admin/grade-flags/', '/api/admin/grade_flags/')

c2 = c2.replace('with patch(\'routes.deps.get_current_user\') as mock_user, \\\\', 'app.dependency_overrides[get_current_user] = lambda: {\'uid\': \'admin1\', \'email\': \'admin@numista.ai\'}\n    app.dependency_overrides[require_admin_user] = lambda: {\'uid\': \'admin1\', \'email\': \'admin@numista.ai\'}\n    with')
c2 = c2.replace('patch(\'routes.deps.require_admin_user\') as mock_admin, \\\\', '')
c2 = c2.replace('patch(\'routes.deps.require_admin_user\') as mock_admin:', 'patch(\'routes.grade_review_routes.db\') as mock_db:')

c2 = c2.replace('mock_user.return_value = {\'uid\': \'admin1\', \'email\': \'admin@numista.ai\'}', '')
c2 = c2.replace('mock_admin.return_value = {\'uid\': \'admin1\', \'email\': \'admin@numista.ai\'}', '')

with open(path2, 'w', encoding='utf-8') as f:
    f.write(c2)
