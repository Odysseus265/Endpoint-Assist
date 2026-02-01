# Changelog

All notable changes to Endpoint Assist will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- WebSocket support for real-time system monitoring
- Excel report generation alongside PDF reports
- Role-based authentication system (admin, technician, viewer)
- Interactive Swagger API documentation
- GitHub Actions CI/CD pipeline
- Security policy and contributing guidelines
- GitHub issue and PR templates

## [1.0.0] - 2024-01-XX

### Added
- **Dashboard**: Real-time system overview with key metrics
- **System Diagnostics**: Comprehensive hardware and software analysis
  - CPU usage and information
  - Memory utilization
  - Disk space monitoring
  - Running processes list
  - Startup programs management
- **Network Diagnostics**: Network connectivity and configuration
  - Network adapters information
  - Active connections
  - DNS configuration
  - Gateway and routing info
  - Network speed testing
- **Log Analysis**: Windows Event Log viewer
  - System logs
  - Application logs
  - Security logs
  - Filtering and search capabilities
- **Ticket System**: IT support ticket management
  - Create, update, close tickets
  - Priority levels (Low, Medium, High, Critical)
  - Status tracking (Open, In Progress, Resolved, Closed)
  - SQLite database persistence
- **Report Generation**: Professional PDF reports
  - System health reports
  - Network reports
  - Full comprehensive reports
- **Audit Logging**: Track all diagnostic actions
- **Docker Support**: Containerized deployment
- **Unit Tests**: Comprehensive test coverage
- **API Documentation**: RESTful API with documentation

### Technical
- Flask 2.3+ backend
- WMI integration for Windows diagnostics
- psutil for cross-platform metrics
- ReportLab for PDF generation
- SQLite for data persistence
- Responsive web interface

## [0.1.0] - Initial Development

### Added
- Initial project structure
- Basic Flask application
- Core system diagnostic functions
- Web interface prototype

---

## Version History

| Version | Date | Description |
|---------|------|-------------|
| 1.0.0 | 2024-XX-XX | First stable release |
| 0.1.0 | 2024-XX-XX | Initial development |

---

## Upgrade Guide

### From 0.x to 1.0

1. Update dependencies: `pip install -r requirements.txt`
2. Initialize database: Database is auto-created on first run
3. Review new configuration options
4. Test authentication features

---

[Unreleased]: https://github.com/Odysseus265/endpoint-assist/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/Odysseus265/endpoint-assist/releases/tag/v1.0.0
