import os
import sys
import pytest

root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from app import app, init_db


@pytest.fixture(scope='module')
def client():
    init_db()
    app.config['TESTING'] = True
    return app.test_client()


def test_health_check(client):
    response = client.get('/health')
    assert response.status_code == 200
    assert response.json['status'] == 'healthy'


def test_get_suppliers(client):
    response = client.get('/api/suppliers')
    assert response.status_code == 200
    assert 'suppliers' in response.json
    assert isinstance(response.json['suppliers'], list)


def test_frontdesk_submit_and_history(client):
    payload = {'name': 'Test User', 'phone': '9999999999', 'issue': 'Test issue', 'notes': 'note'}
    response = client.post('/api/frontdesk', json=payload)
    assert response.status_code == 201
    assert response.json['success'] is True

    response = client.get('/api/frontdesk/history')
    assert response.status_code == 200
    assert any(item['name'] == 'Test User' for item in response.json)


def test_record_payment_and_dashboard(client):
    response = client.post('/api/payments', json={'supplier_id': 1, 'amount': 1000, 'method': 'cash', 'reference': 't1'})
    assert response.status_code == 201
    assert response.json['success'] is True

    response = client.get('/api/dashboard')
    assert response.status_code == 200
    assert 'total_suppliers' in response.json
