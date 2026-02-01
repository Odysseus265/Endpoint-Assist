"""
Endpoint Assist - Utility Tests
Unit tests for utility functions
"""

import pytest
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestUtilityFunctions:
    """Test utility functions"""
    
    def test_run_command_success(self):
        """Test running a simple command"""
        from app import run_command
        result = run_command('echo hello')
        assert 'hello' in result.lower()
    
    def test_run_command_with_error(self):
        """Test running an invalid command"""
        from app import run_command
        result = run_command('nonexistent_command_12345')
        # Should return error message, not crash
        assert result is not None


class TestSystemInfo:
    """Test system information gathering"""
    
    def test_psutil_cpu(self):
        """Test CPU information retrieval"""
        import psutil
        cpu_percent = psutil.cpu_percent(interval=0.1)
        assert isinstance(cpu_percent, float)
        assert 0 <= cpu_percent <= 100
    
    def test_psutil_memory(self):
        """Test memory information retrieval"""
        import psutil
        memory = psutil.virtual_memory()
        assert memory.total > 0
        assert 0 <= memory.percent <= 100
    
    def test_psutil_disk(self):
        """Test disk information retrieval"""
        import psutil
        partitions = psutil.disk_partitions()
        assert len(partitions) > 0
        
        for partition in partitions:
            try:
                usage = psutil.disk_usage(partition.mountpoint)
                assert usage.total > 0
            except:
                pass  # Some partitions may not be accessible
    
    def test_platform_info(self):
        """Test platform information retrieval"""
        import platform
        assert platform.system() in ['Windows', 'Linux', 'Darwin']
        assert platform.release() is not None
        assert platform.machine() is not None
    
    def test_socket_hostname(self):
        """Test hostname retrieval"""
        import socket
        hostname = socket.gethostname()
        assert hostname is not None
        assert len(hostname) > 0


class TestNetworkUtilities:
    """Test network utility functions"""
    
    def test_local_ip_detection(self):
        """Test local IP address detection"""
        import socket
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(('8.8.8.8', 80))
            local_ip = s.getsockname()[0]
            s.close()
            assert local_ip is not None
            # Basic IP format check
            parts = local_ip.split('.')
            assert len(parts) == 4
        except:
            # Network may not be available in test environment
            pass
    
    def test_network_interfaces(self):
        """Test network interface enumeration"""
        import psutil
        interfaces = psutil.net_if_addrs()
        assert len(interfaces) > 0


class TestReportGeneration:
    """Test report generation"""
    
    def test_report_generator_import(self):
        """Test report generator can be imported"""
        from reports import ReportGenerator
        generator = ReportGenerator()
        assert generator is not None
    
    def test_generate_system_pdf(self):
        """Test system PDF generation"""
        from reports import generate_system_pdf
        try:
            pdf_buffer = generate_system_pdf()
            assert pdf_buffer is not None
            # Check it has content
            pdf_buffer.seek(0, 2)  # Go to end
            size = pdf_buffer.tell()
            assert size > 0
        except ImportError:
            pytest.skip("reportlab not installed")
    
    def test_generate_full_pdf(self):
        """Test full PDF generation"""
        from reports import generate_full_pdf
        try:
            pdf_buffer = generate_full_pdf()
            assert pdf_buffer is not None
        except ImportError:
            pytest.skip("reportlab not installed")


class TestDataValidation:
    """Test data validation"""
    
    def test_ticket_data_validation(self):
        """Test ticket data structure"""
        ticket = {
            "title": "Test",
            "description": "Test description",
            "priority": "medium",
            "status": "open"
        }
        assert 'title' in ticket
        assert ticket['priority'] in ['low', 'medium', 'high', 'critical']
        assert ticket['status'] in ['open', 'in-progress', 'resolved', 'closed']


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
