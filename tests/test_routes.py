"""Tests for the main application routes."""
import pytest
from flask import url_for
import sqlalchemy as sa
from app import db
from app.models import Collector, Message


def test_home_page(client):
    """Test that home page loads properly."""
    response = client.get('/')
    assert response.status_code == 200
    assert b'Welcome to FakeHEC!' in response.data


def test_register_new_collector(client):
    """Test registering a new collector."""
    response = client.post(
        '/',
        data={'name': 'newcollector', 'password': 'testpassword'},
        follow_redirects=True
    )
    assert response.status_code == 200
    assert b'FakeHEC - newcollector' in response.data
    
    # Check that the collector was created in the database
    with client.application.app_context():
        collector = db.session.scalar(sa.select(Collector).where(Collector.name == 'newcollector'))
        assert collector is not None
        assert collector.check_password('testpassword')


def test_login_existing_collector(client, test_collector):
    """Test logging in with an existing collector."""
    response = client.post(
        '/',
        data={'name': 'testcollector', 'password': 'password'},
        follow_redirects=True
    )
    assert response.status_code == 200
    assert b'FakeHEC - testcollector' in response.data


def test_login_wrong_password(client, test_collector):
    """Test login with wrong password."""
    response = client.post(
        '/',
        data={'name': 'testcollector', 'password': 'wrongpassword'},
        follow_redirects=True
    )
    assert response.status_code == 200
    assert b'Invalid password' in response.data


def test_view_collector_requires_login(client):
    """Test that the collector view requires login."""
    response = client.get('/collector', follow_redirects=True)
    assert response.status_code == 200
    assert b'Please log in to access this page.' in response.data


def test_collector_view(auth_client):
    """Test viewing the collector page."""
    response = auth_client.get('/collector')
    assert response.status_code == 200
    assert b'FakeHEC - testcollector' in response.data
    assert b'Host:' in response.data
    assert b'Token:' in response.data


def test_regenerate_token(auth_client):
    """Test regenerating a token."""
    # Get the original token
    with auth_client.application.app_context():
        collector = db.session.scalar(sa.select(Collector).where(Collector.name == 'testcollector'))
        original_token = collector.token
    
    response = auth_client.get('/regenerate', follow_redirects=True)
    assert response.status_code == 200
    assert b'Token regenerated' in response.data
    
    # Check that the token was changed
    with auth_client.application.app_context():
        collector = db.session.scalar(sa.select(Collector).where(Collector.name == 'testcollector'))
        assert collector.token != original_token


def test_delete_collector(auth_client, test_collector):
    """Test deleting a collector."""
    response = auth_client.get('/delete', follow_redirects=True)
    assert response.status_code == 200
    assert b'Collector deleted' in response.data
    
    # Check that the collector was deleted
    with auth_client.application.app_context():
        collector = db.session.scalar(sa.select(Collector).where(Collector.name == 'testcollector'))
        assert collector is None


def test_logout(auth_client):
    """Test logging out."""
    response = auth_client.get('/logout', follow_redirects=True)
    assert response.status_code == 200
    assert b'Welcome to FakeHEC!' in response.data
    
    # Check that accessing the collector view redirects to login
    response = auth_client.get('/collector', follow_redirects=True)
    assert b'Please log in to access this page.' in response.data
