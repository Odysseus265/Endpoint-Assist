"""
Endpoint Assist - Database Tests
Unit tests for database operations
"""

import pytest
import sys
import os
import tempfile

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Override database path for testing
import database
database.DATABASE_PATH = os.path.join(tempfile.gettempdir(), 'test_endpoint_assist.db')

from database import (
    init_db,
    create_ticket, get_all_tickets, get_ticket_by_id, update_ticket, delete_ticket, get_ticket_stats,
    add_audit_log, get_audit_logs,
    get_setting, set_setting
)


@pytest.fixture(autouse=True)
def setup_database():
    """Setup clean database for each test"""
    # Remove test database if exists
    if os.path.exists(database.DATABASE_PATH):
        os.remove(database.DATABASE_PATH)
    init_db()
    yield
    # Cleanup after test
    if os.path.exists(database.DATABASE_PATH):
        os.remove(database.DATABASE_PATH)


class TestTicketOperations:
    """Test ticket database operations"""
    
    def test_create_ticket(self):
        """Test creating a ticket"""
        ticket_id = create_ticket({
            "title": "Test Ticket",
            "description": "Test description",
            "priority": "high",
            "category": "testing"
        })
        assert ticket_id is not None
        assert len(ticket_id) == 36  # UUID length
    
    def test_get_ticket_by_id(self):
        """Test retrieving a ticket by ID"""
        ticket_id = create_ticket({
            "title": "Test Ticket",
            "description": "Test description"
        })
        ticket = get_ticket_by_id(ticket_id)
        assert ticket is not None
        assert ticket['title'] == "Test Ticket"
    
    def test_get_all_tickets(self):
        """Test retrieving all tickets"""
        create_ticket({"title": "Ticket 1"})
        create_ticket({"title": "Ticket 2"})
        create_ticket({"title": "Ticket 3"})
        
        tickets = get_all_tickets()
        assert len(tickets) >= 3
    
    def test_update_ticket(self):
        """Test updating a ticket"""
        ticket_id = create_ticket({
            "title": "Original Title",
            "status": "open"
        })
        
        success = update_ticket(ticket_id, {
            "status": "in-progress",
            "priority": "high"
        })
        
        assert success
        updated_ticket = get_ticket_by_id(ticket_id)
        assert updated_ticket['status'] == "in-progress"
        assert updated_ticket['priority'] == "high"
    
    def test_delete_ticket(self):
        """Test deleting a ticket"""
        ticket_id = create_ticket({"title": "To Be Deleted"})
        
        success = delete_ticket(ticket_id)
        assert success
        
        ticket = get_ticket_by_id(ticket_id)
        assert ticket is None
    
    def test_ticket_stats(self):
        """Test ticket statistics"""
        create_ticket({"title": "Open Ticket", "status": "open"})
        create_ticket({"title": "Resolved Ticket", "status": "resolved"})
        
        stats = get_ticket_stats()
        assert 'total' in stats
        assert stats['total'] >= 2
    
    def test_filter_tickets_by_status(self):
        """Test filtering tickets by status"""
        create_ticket({"title": "Open 1", "status": "open"})
        create_ticket({"title": "Open 2", "status": "open"})
        ticket_id = create_ticket({"title": "Resolved", "status": "open"})
        update_ticket(ticket_id, {"status": "resolved"})
        
        open_tickets = get_all_tickets(status_filter="open")
        for ticket in open_tickets:
            assert ticket['status'] == "open"


class TestAuditLogOperations:
    """Test audit log database operations"""
    
    def test_add_audit_log(self):
        """Test adding an audit log entry"""
        log_id = add_audit_log("Test Action", "Test details", "TestUser")
        assert log_id is not None
    
    def test_get_audit_logs(self):
        """Test retrieving audit logs"""
        add_audit_log("Action 1", "Details 1")
        add_audit_log("Action 2", "Details 2")
        add_audit_log("Action 3", "Details 3")
        
        logs = get_audit_logs(limit=10)
        assert len(logs) >= 3
    
    def test_audit_logs_order(self):
        """Test audit logs are returned in descending order"""
        add_audit_log("First", "First log")
        add_audit_log("Second", "Second log")
        add_audit_log("Third", "Third log")
        
        logs = get_audit_logs(limit=3)
        # Most recent should be first
        assert logs[0]['action'] == "Third"
    
    def test_filter_audit_logs(self):
        """Test filtering audit logs by action"""
        add_audit_log("Login", "User logged in")
        add_audit_log("Ticket", "Ticket created")
        add_audit_log("Login", "Another login")
        
        login_logs = get_audit_logs(action_filter="Login")
        for log in login_logs:
            assert "Login" in log['action']


class TestSettingsOperations:
    """Test settings database operations"""
    
    def test_set_and_get_setting(self):
        """Test setting and getting a setting"""
        set_setting("test_key", "test_value")
        value = get_setting("test_key")
        assert value == "test_value"
    
    def test_get_nonexistent_setting(self):
        """Test getting a non-existent setting returns default"""
        value = get_setting("nonexistent", default="default_value")
        assert value == "default_value"
    
    def test_update_setting(self):
        """Test updating an existing setting"""
        set_setting("update_key", "original")
        set_setting("update_key", "updated")
        value = get_setting("update_key")
        assert value == "updated"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
