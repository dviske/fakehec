import os
import tempfile
import pytest
from app import create_app, db, scheduler
from app.models import Collector, Message
from config import Config


class TestConfig(Config):
    """Test configuration."""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite://'  # Use in-memory database
    WTF_CSRF_ENABLED = False
    SERVER_NAME = 'fakehec.test:5000'
    SECRET_KEY = 'test-key'
    SCHEDULER_API_ENABLED = False  # Disable the scheduler API


@pytest.fixture
def app():
    """Create and configure a Flask app for testing."""
    # Stop any existing scheduler to avoid the "already running" error
    if scheduler.running:
        scheduler.shutdown()
    
    app = create_app(TestConfig)
    app.config.update({
        "TESTING": True,
    })
    
    # Create the database and the database tables
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()


@pytest.fixture
def runner(app):
    """A test CLI runner for the app."""
    return app.test_cli_runner()


@pytest.fixture
def test_collector(app):
    """Create a test collector."""
    with app.app_context():
        collector = Collector(name='testcollector', token='test-token')
        collector.set_password('password')
        db.session.add(collector)
        db.session.commit()
        return collector


@pytest.fixture
def auth_client(client, test_collector):
    """Authenticate a test client."""
    client.post('/', data={
        'name': 'testcollector',
        'password': 'password',
    }, follow_redirects=True)
    return client


@pytest.fixture
def test_message(app, test_collector):
    """Create a test message for a collector."""
    with app.app_context():
        message = Message(
            received_from='127.0.0.1',
            content='{"test": "data"}',
            collector=test_collector
        )
        db.session.add(message)
        db.session.commit()
        return message
