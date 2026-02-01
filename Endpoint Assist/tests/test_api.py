"""
Endpoint Assist - API Tests
Unit tests for API endpoints
"""

import pytest
import json
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app


@pytest.fixture
def client():
    """Create test client"""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


class TestHealthEndpoints:
    """Test system health endpoints"""
    
    def test_index_page(self, client):
        """Test main page loads"""
        response = client.get('/')
        assert response.status_code == 200
    
    def test_system_health(self, client):
        """Test system health endpoint"""
        response = client.get('/api/system/health')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'success'
        assert 'cpu' in data['data']
        assert 'memory' in data['data']
        assert 'disks' in data['data']
    
    def test_system_processes(self, client):
        """Test processes endpoint"""
        response = client.get('/api/system/processes')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'success'
        assert isinstance(data['data'], list)


class TestNetworkEndpoints:
    """Test network diagnostic endpoints"""
    
    def test_network_info(self, client):
        """Test network info endpoint"""
        response = client.get('/api/network/info')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'success'
        assert 'local_ip' in data['data']
        assert 'hostname' in data['data']
    
    def test_ping_test(self, client):
        """Test ping endpoint"""
        response = client.get('/api/network/ping?target=127.0.0.1')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'success'
        assert 'reachable' in data['data']
    
    def test_dns_test(self, client):
        """Test DNS resolution endpoint"""
        response = client.get('/api/network/dns?domain=localhost')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'success'
    
    def test_port_check(self, client):
        """Test port check endpoint"""
        response = client.get('/api/network/port-check?host=127.0.0.1&port=80')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'success'
        assert 'open' in data['data']


class TestTicketEndpoints:
    """Test ticket management endpoints"""
    
    def test_get_tickets(self, client):
        """Test get tickets endpoint"""
        response = client.get('/api/tickets')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'success'
        assert isinstance(data['data'], list)
    
    def test_create_ticket(self, client):
        """Test create ticket endpoint"""
        ticket_data = {
            "title": "Test Ticket",
            "description": "This is a test ticket",
            "category": "testing",
            "priority": "low"
        }
        response = client.post(
            '/api/tickets',
            data=json.dumps(ticket_data),
            content_type='application/json'
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'success'
        assert data['data']['title'] == "Test Ticket"
    
    def test_get_ticket_stats(self, client):
        """Test ticket stats endpoint"""
        response = client.get('/api/tickets/stats')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'success'


class TestAuditEndpoints:
    """Test audit log endpoints"""
    
    def test_get_audit_logs(self, client):
        """Test get audit logs endpoint"""
        response = client.get('/api/audit-logs')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'success'
        assert isinstance(data['data'], list)
    
    def test_audit_logs_with_limit(self, client):
        """Test audit logs with limit parameter"""
        response = client.get('/api/audit-logs?limit=10')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'success'


class TestSecurityEndpoints:
    """Test security status endpoints"""
    
    def test_security_status(self, client):
        """Test security status endpoint"""
        response = client.get('/api/security/status')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'success'
        assert 'defender' in data['data']
        assert 'firewall' in data['data']


class TestDeviceEndpoints:
    """Test device management endpoints"""
    
    def test_get_printers(self, client):
        """Test printers endpoint"""
        response = client.get('/api/devices/printers')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'success'
    
    def test_get_audio_devices(self, client):
        """Test audio devices endpoint"""
        response = client.get('/api/devices/audio')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'success'
    
    def test_get_usb_devices(self, client):
        """Test USB devices endpoint"""
        response = client.get('/api/devices/usb')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'success'


class TestReportEndpoints:
    """Test report generation endpoints"""
    
    def test_generate_report(self, client):
        """Test JSON report generation"""
        response = client.get('/api/reports/generate?type=full')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'generated' in data or data.get('status') == 'success'


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
