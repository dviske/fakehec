"""Tests for the HTTP Event Collector API."""
import pytest
import json
import base64
from flask import url_for
import sqlalchemy as sa
from app import db
from app.models import Collector, Message


class TestCollectorAPI:
    def test_post_without_auth(self, client, test_collector, app):
        """Test posting to the collector without authentication."""
        # Create a request with a subdomain
        with app.app_context():
            response = client.post(
                '/services/collector',
                base_url=f'http://testcollector.fakehec.test:5000',
                data=json.dumps({"event": "test"}),
                content_type='application/json'
            )
            assert response.status_code == 401
            assert b'Token is required' in response.data
    
    def test_post_with_invalid_token(self, client, test_collector, app):
        """Test posting to the collector with an invalid token."""
        with app.app_context():
            # Create Basic Auth header with invalid token
            auth_header = base64.b64encode(b'Splunk invalid-token').decode('utf-8')
            response = client.post(
                '/services/collector',
                base_url=f'http://testcollector.fakehec.test:5000',
                headers={'Authorization': f'Basic {auth_header}'},
                data=json.dumps({"event": "test"}),
                content_type='application/json'
            )
            assert response.status_code == 401
            assert b'invalid token' in response.data
    
    def test_post_to_invalid_collector(self, client, app):
        """Test posting to a non-existent collector."""
        with app.app_context():
            auth_header = base64.b64encode(b'Splunk some-token').decode('utf-8')
            response = client.post(
                '/services/collector',
                base_url=f'http://nonexistent.fakehec.test:5000',
                headers={'Authorization': f'Basic {auth_header}'},
                data=json.dumps({"event": "test"}),
                content_type='application/json'
            )
            assert response.status_code == 400
            assert b'Incorrect index' in response.data
    
    def test_post_valid_json_data(self, client, test_collector, app):
        """Test posting valid JSON data to the collector."""
        with app.app_context():
            # Query for the collector by name instead of using the test_collector object
            collector = db.session.scalar(sa.select(Collector).where(Collector.name == "testcollector"))
            
            # Send test data
            test_data = {"event": "test", "source": "test_source"}
            response = client.post(
                '/services/collector',
                base_url=f'http://testcollector.fakehec.test:5000',
                headers={'Authorization': 'Splunk test-token'},
                data=json.dumps(test_data),
                content_type='application/json'
            )
            
            # Check response
            assert response.status_code == 200
            assert response.json['text'] == 'Success'
            assert response.json['code'] == 0
            
            # Verify message was stored in the database
            message = db.session.scalar(
                sa.select(Message)
                .where(Message.collector_id == collector.id)
                .order_by(Message.received_at.desc())
            )
            assert message is not None
            assert json.loads(message.content)['event'] == 'test'
    
    def test_post_empty_data(self, client, test_collector, app):
        """Test posting empty data to the collector."""
        with app.app_context():
            # Query for the collector by name instead of using the test_collector object
            collector = db.session.scalar(sa.select(Collector).where(Collector.name == "testcollector"))
            
            # Send empty data
            response = client.post(
                '/services/collector',
                base_url=f'http://testcollector.fakehec.test:5000',
                headers={
                    'Authorization': f'Splunk test-token',
                    'Content-Type': 'application/json'
                },
                data=''
            )
            
            # Check response
            assert response.status_code == 200
            assert response.json['text'] == 'Success'
            assert response.json['code'] == 0
            
            # Verify message was stored in the database with None content
            message = db.session.scalar(
                sa.select(Message)
                .where(Message.collector_id == collector.id)
                .order_by(Message.received_at.desc())
            )
            assert message is not None
            assert message.content is None
    
    def test_x_real_ip_header(self, client, test_collector, app):
        """Test that X-Real-IP header is used if present."""
        with app.app_context():
            # Query for the collector by name instead of using the test_collector object
            collector = db.session.scalar(sa.select(Collector).where(Collector.name == "testcollector"))
            
            # Send test data with X-Real-IP header
            test_data = {"event": "test_ip"}
            response = client.post(
                '/services/collector',
                base_url=f'http://testcollector.fakehec.test:5000',
                headers={
                    'Authorization': f'Splunk test-token',
                    'Content-Type': 'application/json',
                    'X-Real-IP': '10.10.10.10'
                },
                data=json.dumps(test_data)
            )
            
            # Check response
            assert response.status_code == 200
            
            # Verify message was stored with the X-Real-IP
            message = db.session.scalar(
                sa.select(Message)
                .where(Message.collector_id == collector.id)
                .order_by(Message.received_at.desc())
            )
            assert message is not None
            assert message.received_from == '10.10.10.10'
