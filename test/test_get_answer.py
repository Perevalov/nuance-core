import tempfile
import pytest

from app import app


class TestGetAnswer:

    @pytest.fixture
    def initialize_app(self):
        app.config['TESTING'] = True
        app.config['DEBUG'] = False
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['DATABASE'] = tempfile.mkstemp()
        app.testing = True

    def test_get_answer(self):
        with app.test_client() as client:
            user_message = {'user_text': 'How many people live in Amsterdam?'}
            response = client.get('/get_answer', data=user_message)
        assert response.status == 200
