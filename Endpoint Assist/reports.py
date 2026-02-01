"""
Endpoint Assist - PDF Report Generator
Generates professional PDF reports for system diagnostics
"""

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from datetime import datetime
import io
import os
import psutil
import platform
import socket

class ReportGenerator:
    """Generate professional PDF reports"""
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Setup custom styles for the report"""
        # Title style
        self.styles.add(ParagraphStyle(
            name='ReportTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#d00000'),
            spaceAfter=30,
            alignment=TA_CENTER
        ))
        
        # Section header style
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#1a1a2e'),
            spaceBefore=20,
            spaceAfter=10,
            borderPadding=5
        ))
        
        # Info style
        self.styles.add(ParagraphStyle(
            name='InfoText',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#4a4a5a'),
            spaceAfter=5
        ))
        
        # Footer style
        self.styles.add(ParagraphStyle(
            name='Footer',
            parent=self.styles['Normal'],
            fontSize=8,
            textColor=colors.gray,
            alignment=TA_CENTER
        ))
    
    def _create_header(self, elements):
        """Create report header"""
        # Title
        elements.append(Paragraph("🛡️ Endpoint Assist", self.styles['ReportTitle']))
        elements.append(Paragraph("System Diagnostic Report", self.styles['Heading2']))
        elements.append(Spacer(1, 10))
        
        # Report metadata
        metadata = [
            ["Generated:", datetime.now().strftime("%Y-%m-%d %H:%M:%S")],
            ["Hostname:", socket.gethostname()],
            ["Report Type:", "Comprehensive System Analysis"]
        ]
        
        meta_table = Table(metadata, colWidths=[1.5*inch, 4*inch])
        meta_table.setStyle(TableStyle([
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.gray),
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ]))
        elements.append(meta_table)
        elements.append(Spacer(1, 20))
    
    def _add_system_section(self, elements, data=None):
        """Add system information section"""
        elements.append(Paragraph("💻 System Information", self.styles['SectionHeader']))
        
        # Gather system info
        os_info = {
            "Operating System": f"{platform.system()} {platform.release()}",
            "OS Version": platform.version(),
            "Machine": platform.machine(),
            "Processor": platform.processor(),
            "Hostname": socket.gethostname(),
            "Boot Time": datetime.fromtimestamp(psutil.boot_time()).strftime("%Y-%m-%d %H:%M:%S")
        }
        
        system_data = [[k, v] for k, v in os_info.items()]
        
        table = Table(system_data, colWidths=[2*inch, 4.5*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f5f5f7')),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e0e0e0')),
            ('PADDING', (0, 0), (-1, -1), 8),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        elements.append(table)
        elements.append(Spacer(1, 15))
    
    def _add_performance_section(self, elements, data=None):
        """Add performance metrics section"""
        elements.append(Paragraph("📊 Performance Metrics", self.styles['SectionHeader']))
        
        # CPU Info
        cpu_percent = psutil.cpu_percent(interval=1)
        cpu_cores = psutil.cpu_count(logical=False)
        cpu_threads = psutil.cpu_count(logical=True)
        
        # Memory Info
        memory = psutil.virtual_memory()
        
        # Disk Info
        disk = psutil.disk_usage('/')
        
        performance_data = [
            ["Metric", "Value", "Status"],
            ["CPU Usage", f"{cpu_percent}%", self._get_status(cpu_percent, 80, 60)],
            ["CPU Cores", f"{cpu_cores} Physical / {cpu_threads} Logical", "ℹ️ Info"],
            ["Memory Usage", f"{memory.percent}% ({round(memory.used/(1024**3), 1)} / {round(memory.total/(1024**3), 1)} GB)", self._get_status(memory.percent, 85, 70)],
            ["Memory Available", f"{round(memory.available/(1024**3), 1)} GB", "ℹ️ Info"],
            ["Disk Usage (C:)", f"{disk.percent}% ({round(disk.used/(1024**3), 1)} / {round(disk.total/(1024**3), 1)} GB)", self._get_status(disk.percent, 90, 75)],
            ["Disk Free", f"{round(disk.free/(1024**3), 1)} GB", "ℹ️ Info"],
        ]
        
        table = Table(performance_data, colWidths=[2*inch, 2.5*inch, 2*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a1a2e')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e0e0e0')),
            ('PADDING', (0, 0), (-1, -1), 8),
            ('ALIGN', (1, 0), (1, -1), 'CENTER'),
            ('ALIGN', (2, 0), (2, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f9f9f9')]),
        ]))
        elements.append(table)
        elements.append(Spacer(1, 15))
    
    def _get_status(self, value, critical_threshold, warning_threshold):
        """Get status indicator based on thresholds"""
        if value >= critical_threshold:
            return "🔴 Critical"
        elif value >= warning_threshold:
            return "🟡 Warning"
        else:
            return "🟢 Good"
    
    def _add_network_section(self, elements, data=None):
        """Add network information section"""
        elements.append(Paragraph("🌐 Network Information", self.styles['SectionHeader']))
        
        # Get local IP
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(('8.8.8.8', 80))
            local_ip = s.getsockname()[0]
            s.close()
        except:
            local_ip = '127.0.0.1'
        
        # Network interfaces
        interfaces = []
        for name, addrs in psutil.net_if_addrs().items():
            for addr in addrs:
                if addr.family == socket.AF_INET:
                    interfaces.append([name, addr.address, addr.netmask or "N/A"])
        
        network_data = [["Interface", "IP Address", "Netmask"]] + interfaces[:5]
        
        table = Table(network_data, colWidths=[2.5*inch, 2*inch, 2*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a1a2e')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e0e0e0')),
            ('PADDING', (0, 0), (-1, -1), 8),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f9f9f9')]),
        ]))
        elements.append(table)
        elements.append(Spacer(1, 15))
    
    def _add_disk_section(self, elements, data=None):
        """Add disk information section"""
        elements.append(Paragraph("💾 Disk Partitions", self.styles['SectionHeader']))
        
        disk_data = [["Drive", "File System", "Total", "Used", "Free", "Usage %"]]
        
        for partition in psutil.disk_partitions():
            try:
                usage = psutil.disk_usage(partition.mountpoint)
                disk_data.append([
                    partition.device,
                    partition.fstype,
                    f"{round(usage.total/(1024**3), 1)} GB",
                    f"{round(usage.used/(1024**3), 1)} GB",
                    f"{round(usage.free/(1024**3), 1)} GB",
                    f"{usage.percent}%"
                ])
            except:
                pass
        
        table = Table(disk_data, colWidths=[1*inch, 1*inch, 1.1*inch, 1.1*inch, 1.1*inch, 1.2*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a1a2e')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e0e0e0')),
            ('PADDING', (0, 0), (-1, -1), 6),
            ('ALIGN', (2, 0), (-1, -1), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f9f9f9')]),
        ]))
        elements.append(table)
        elements.append(Spacer(1, 15))
    
    def _add_process_section(self, elements, data=None):
        """Add top processes section"""
        elements.append(Paragraph("⚡ Top Processes (by CPU)", self.styles['SectionHeader']))
        
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
            try:
                pinfo = proc.info
                if pinfo['cpu_percent'] is not None and pinfo['cpu_percent'] > 0:
                    processes.append(pinfo)
            except:
                pass
        
        # Sort by CPU usage
        processes.sort(key=lambda x: x['cpu_percent'], reverse=True)
        
        process_data = [["PID", "Process Name", "CPU %", "Memory %"]]
        for p in processes[:10]:
            process_data.append([
                str(p['pid']),
                p['name'][:30],
                f"{round(p['cpu_percent'], 1)}%",
                f"{round(p['memory_percent'], 1)}%" if p['memory_percent'] else "N/A"
            ])
        
        table = Table(process_data, colWidths=[1*inch, 3*inch, 1.25*inch, 1.25*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a1a2e')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e0e0e0')),
            ('PADDING', (0, 0), (-1, -1), 6),
            ('ALIGN', (0, 0), (0, -1), 'CENTER'),
            ('ALIGN', (2, 0), (-1, -1), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f9f9f9')]),
        ]))
        elements.append(table)
        elements.append(Spacer(1, 15))
    
    def _add_footer(self, elements):
        """Add report footer"""
        elements.append(Spacer(1, 30))
        elements.append(Paragraph(
            "Generated by Endpoint Assist - Professional IT Help Desk Dashboard",
            self.styles['Footer']
        ))
        elements.append(Paragraph(
            f"© {datetime.now().year} | Confidential - Internal Use Only",
            self.styles['Footer']
        ))
    
    def generate_system_report(self):
        """Generate a system-focused PDF report"""
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.5*inch, bottomMargin=0.5*inch)
        
        elements = []
        self._create_header(elements)
        self._add_system_section(elements)
        self._add_performance_section(elements)
        self._add_disk_section(elements)
        self._add_footer(elements)
        
        doc.build(elements)
        buffer.seek(0)
        return buffer
    
    def generate_network_report(self):
        """Generate a network-focused PDF report"""
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.5*inch, bottomMargin=0.5*inch)
        
        elements = []
        self._create_header(elements)
        self._add_network_section(elements)
        self._add_footer(elements)
        
        doc.build(elements)
        buffer.seek(0)
        return buffer
    
    def generate_full_report(self):
        """Generate a comprehensive PDF report"""
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.5*inch, bottomMargin=0.5*inch)
        
        elements = []
        self._create_header(elements)
        self._add_system_section(elements)
        self._add_performance_section(elements)
        self._add_disk_section(elements)
        self._add_network_section(elements)
        self._add_process_section(elements)
        self._add_footer(elements)
        
        doc.build(elements)
        buffer.seek(0)
        return buffer


# Create global instance
report_generator = ReportGenerator()


def generate_system_pdf():
    """Helper function to generate system report"""
    return report_generator.generate_system_report()

def generate_network_pdf():
    """Helper function to generate network report"""
    return report_generator.generate_network_report()

def generate_full_pdf():
    """Helper function to generate full report"""
    return report_generator.generate_full_report()
