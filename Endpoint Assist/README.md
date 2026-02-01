# 🛡️ Endpoint Assist

<div align="center">

![Endpoint Assist Banner](https://img.shields.io/badge/🛡️_Endpoint_Assist-IT_Help_Desk_Dashboard-d00000?style=for-the-badge)

**A comprehensive, professional-grade IT Help Desk web application for system diagnostics, network troubleshooting, and endpoint management.**

[![Python](https://img.shields.io/badge/Python-3.8+-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-2.3+-000000?style=flat-square&logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![SQLite](https://img.shields.io/badge/SQLite-Database-003B57?style=flat-square&logo=sqlite&logoColor=white)](https://sqlite.org)
[![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)](LICENSE)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?style=flat-square&logo=docker&logoColor=white)](Dockerfile)
[![Swagger](https://img.shields.io/badge/Swagger-API_Docs-85EA2D?style=flat-square&logo=swagger&logoColor=black)](api_docs.py)
[![Code Style](https://img.shields.io/badge/Code_Style-PEP8-blue?style=flat-square)](https://pep8.org/)
[![PRs Welcome](https://img.shields.io/badge/PRs-Welcome-brightgreen?style=flat-square)](CONTRIBUTING.md)

[Features](#-features) • [Quick Start](#-quick-start) • [Documentation](#-documentation) • [API Reference](#-api-reference) • [Contributing](#-contributing)

</div>

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Features](#-features)
- [Architecture](#-architecture)
- [Quick Start](#-quick-start)
- [Docker Deployment](#-docker-deployment)
- [API Reference](#-api-reference)
- [Configuration](#-configuration)
- [Testing](#-testing)
- [Contributing](#-contributing)
- [License](#-license)

---

## 🎯 Overview

**Endpoint Assist** is a modern, feature-rich IT Help Desk dashboard designed for IT professionals and support technicians. Built with Python/Flask backend and a responsive JavaScript frontend, it provides real-time system monitoring, comprehensive diagnostics, and streamlined ticket management.

### Why Endpoint Assist?

- 🚀 **Zero Configuration** - Works out of the box on Windows systems
- 📊 **Real-time Monitoring** - Live CPU, RAM, disk, and network statistics with WebSocket support
- 🔧 **40+ Diagnostic Tools** - Everything from ping tests to registry inspection
- 🎫 **Built-in Ticketing** - Track issues with SQLite-backed persistence
- 📄 **PDF & Excel Reports** - Generate professional system reports in multiple formats
- 🔐 **Role-Based Auth** - Admin, Technician, and Viewer access levels
- 📖 **Swagger API Docs** - Interactive API documentation at `/api/docs`
- 🐳 **Docker Ready** - Deploy anywhere with containerization
- 🎨 **Modern UI** - Dark/light mode, responsive design

### 🛠️ Tech Stack

| Category | Technologies |
|----------|--------------|
| **Backend** | Python 3.8+, Flask 2.3+, Flask-CORS, Flask-SocketIO |
| **Database** | SQLite with custom ORM |
| **System Info** | psutil, WMI (Windows), pywin32 |
| **Reports** | ReportLab (PDF), openpyxl (Excel) |
| **Real-time** | WebSocket via Flask-SocketIO |
| **Frontend** | Vanilla JavaScript, CSS3 with CSS Variables |
| **Documentation** | Swagger/OpenAPI 3.0 |
| **Testing** | pytest, pytest-cov |
| **Deployment** | Docker, Docker Compose |

---

## ✨ Features

### System Diagnostics
| Feature | Description |
|---------|-------------|
| 💻 **System Health** | Real-time CPU, RAM, disk monitoring with visual gauges |
| 🔄 **Process Manager** | View and manage running processes |
| 🚀 **Startup Programs** | Audit and control startup applications |
| 🔋 **Battery Status** | Laptop battery health and time remaining |
| 💾 **Disk Analysis** | Storage usage across all drives |

### Network Tools
| Feature | Description |
|---------|-------------|
| 🌐 **Network Info** | Local/public IP, interfaces, and statistics |
| 📡 **Ping Test** | ICMP connectivity testing |
| 🔍 **DNS Lookup** | Domain name resolution testing |
| 🛤️ **Traceroute** | Network path analysis |
| 🚪 **Port Scanner** | Check port accessibility |
| 📶 **WiFi Status** | Connection details and signal strength |

### Device Management
| Feature | Description |
|---------|-------------|
| 🖨️ **Printers** | Printer status and troubleshooting |
| 🔊 **Audio Devices** | Audio endpoint management |
| 📷 **Cameras** | Webcam detection and status |
| 💿 **USB Devices** | Connected USB device inventory |
| 📱 **Bluetooth** | Bluetooth adapter and device status |

### Help Desk Features
| Feature | Description |
|---------|-------------|
| 🎫 **Ticket System** | Create, track, and resolve support tickets with SQLite persistence |
| 📚 **Knowledge Base** | Built-in IT troubleshooting guides (16+ articles) |
| 📋 **Audit Logging** | Track all system activities with timestamps |
| 📊 **PDF Reports** | Generate professional diagnostic reports with ReportLab |
| 📗 **Excel Reports** | Export data to Excel spreadsheets with openpyxl |
| 👤 **AD User Lookup** | Active Directory user information and account management |
| 🔐 **Authentication** | Role-based access control (Admin, Technician, Viewer) |
| 📖 **API Documentation** | Interactive Swagger/OpenAPI documentation |
| ⚡ **Real-time Updates** | WebSocket support for live system monitoring |

### Security & Maintenance
| Feature | Description |
|---------|-------------|
| 🛡️ **Security Status** | Windows Defender and Firewall status |
| 🔄 **Windows Updates** | Update status and history |
| 🧹 **Temp Cleaner** | Clean temporary files |
| 🌐 **DNS Flush** | Flush DNS resolver cache |
| 🔧 **Network Reset** | Reset network stack |
| 🔑 **Session Management** | Secure session-based authentication |

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        ENDPOINT ASSIST                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────┐     ┌─────────────┐     ┌─────────────┐       │
│  │   Browser   │────▶│   Flask     │────▶│   SQLite    │       │
│  │  (Frontend) │◀────│   Backend   │◀────│  Database   │       │
│  └─────────────┘     └─────────────┘     └─────────────┘       │
│        │                    │                                   │
│        │              ┌─────┴─────┐                             │
│        │              │           │                             │
│        ▼              ▼           ▼                             │
│  ┌───────────┐  ┌─────────┐ ┌─────────┐                        │
│  │ JavaScript│  │  psutil │ │   WMI   │                        │
│  │  (UI/UX)  │  │ (System)│ │(Windows)│                        │
│  └───────────┘  └─────────┘ └─────────┘                        │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                         API ENDPOINTS                           │
├─────────────────────────────────────────────────────────────────┤
│  /api/system/*     - System diagnostics & health               │
│  /api/network/*    - Network tools & diagnostics               │
│  /api/devices/*    - Peripheral device management              │
│  /api/security/*   - Security status & checks                  │
│  /api/tickets/*    - Help desk ticket management               │
│  /api/reports/*    - PDF & Excel report generation             │
│  /api/tools/*      - Maintenance & utility tools               │
│  /api/auth/*       - Authentication & session management       │
│  /api/docs         - Interactive Swagger API documentation     │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🚀 Quick Start

### Prerequisites

- **Python 3.8+**
- **Windows 10/11** (uses WMI for system diagnostics)
- **pip** (Python package manager)

### Installation

```bash
# Clone the repository
git clone https://github.com/Odysseus265/endpoint-assist.git
cd endpoint-assist

# Create virtual environment (recommended)
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/macOS

# Install dependencies
pip install -r requirements.txt

# Initialize the database
python -c "from app import init_db; init_db()"

# Run the application
python app.py
```

### Access the Dashboard

Open your browser and navigate to: **http://localhost:5001**

---

## 🐳 Docker Deployment

### Using Docker

```bash
# Build the image
docker build -t endpoint-assist .

# Run the container
docker run -d -p 5001:5001 --name endpoint-assist endpoint-assist
```

### Using Docker Compose

```bash
# Start the application
docker-compose up -d

# View logs
docker-compose logs -f

# Stop the application
docker-compose down
```

---

## 📖 API Reference

### System Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/system/health` | Complete system health information |
| `GET` | `/api/system/processes` | Running processes list |
| `GET` | `/api/system/startup` | Startup programs |
| `POST` | `/api/system/clean-temp` | Clean temporary files |

### Network Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/network/info` | Network configuration |
| `GET` | `/api/network/ping?target=` | Ping test |
| `GET` | `/api/network/dns?domain=` | DNS resolution |
| `GET` | `/api/network/traceroute?target=` | Traceroute |
| `GET` | `/api/network/port-check?host=&port=` | Port check |

### Ticket Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/tickets` | List all tickets |
| `POST` | `/api/tickets` | Create new ticket |
| `PUT` | `/api/tickets/<id>` | Update ticket |
| `DELETE` | `/api/tickets/<id>` | Delete ticket |

### Report Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/reports/pdf/system` | Generate system report PDF |
| `GET` | `/api/reports/pdf/network` | Generate network report PDF |
| `GET` | `/api/reports/pdf/full` | Generate comprehensive PDF report |
| `GET` | `/api/reports/excel` | Generate full Excel report |
| `GET` | `/api/reports/excel/system` | Generate system Excel report |
| `GET` | `/api/reports/excel/network` | Generate network Excel report |

### Authentication Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/auth/login` | User login |
| `POST` | `/api/auth/logout` | User logout |
| `GET` | `/api/auth/me` | Get current user info |
| `GET` | `/api/auth/users` | List all users (admin only) |
| `POST` | `/api/auth/users` | Create new user (admin only) |

### Documentation

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/docs` | Interactive Swagger UI |
| `GET` | `/api/docs/spec` | OpenAPI JSON specification |

---

## ⚙️ Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `FLASK_ENV` | `production` | Flask environment |
| `SECRET_KEY` | Auto-generated | Session secret key |
| `DATABASE_URL` | `sqlite:///endpoint_assist.db` | Database connection |
| `PORT` | `5001` | Server port |

### Database

Endpoint Assist uses SQLite for data persistence. The database is automatically created on first run.

```bash
# Reset database
rm endpoint_assist.db
python -c "from app import init_db; init_db()"
```

---

## 🧪 Testing

```bash
# Install test dependencies
pip install pytest pytest-cov

# Run all tests
pytest

# Run with coverage report
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_api.py -v
```

---

## 📁 Project Structure

```
endpoint-assist/
├── 📄 app.py                 # Main Flask application
├── 📄 database.py            # SQLite database models & persistence
├── 📄 reports.py             # PDF report generation (ReportLab)
├── 📄 excel_reports.py       # Excel report generation (openpyxl)
├── 📄 auth.py                # Authentication & RBAC system
├── 📄 api_docs.py            # Swagger/OpenAPI documentation
├── 📄 realtime.py            # WebSocket real-time monitoring
├── 📄 requirements.txt       # Python dependencies
├── 📄 pytest.ini             # Pytest configuration
├── 🐳 Dockerfile             # Docker configuration
├── 🐳 docker-compose.yml     # Docker Compose config
├── 📁 static/
│   ├── 📁 css/
│   │   └── 📄 style.css      # Application styles (3500+ lines)
│   └── 📁 js/
│       └── 📄 main.js        # Frontend JavaScript (2500+ lines)
├── 📁 templates/
│   ├── 📄 index.html         # Main dashboard
│   └── 📄 documentation.html # Documentation page
├── 📁 tests/
│   ├── 📄 __init__.py
│   ├── 📄 test_api.py        # API endpoint tests
│   └── 📄 test_utils.py      # Utility function tests
├── 📁 .github/
│   ├── 📁 ISSUE_TEMPLATE/    # Bug & feature request templates
│   ├── 📁 workflows/         # CI/CD GitHub Actions
│   └── 📄 pull_request_template.md
├── 📄 CONTRIBUTING.md        # Contribution guidelines
├── 📄 SECURITY.md            # Security policy
├── 📄 CHANGELOG.md           # Version history
├── 📄 LICENSE                # MIT License
└── 📄 README.md              # This file
```

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/AmazingFeature`)
3. **Commit** your changes (`git commit -m 'Add some AmazingFeature'`)
4. **Push** to the branch (`git push origin feature/AmazingFeature`)
5. **Open** a Pull Request

### Development Setup

```bash
# Clone your fork
git clone https://github.com/Odysseus265/endpoint-assist.git

# Create branch
git checkout -b feature/your-feature

# Install dev dependencies
pip install -r requirements.txt

# Run tests before submitting
pytest
```

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 👤 Author

**Odysseus265**

- GitHub: [@Odysseus265](https://github.com/Odysseus265)

Built with ❤️ for IT support professionals

---

## ⭐ Show Your Support

If this project helped you, please give it a ⭐ on GitHub!

---

## 📊 Project Stats

- **40+** API Endpoints
- **16+** Knowledge Base Articles
- **3500+** Lines of CSS
- **2500+** Lines of JavaScript
- **100%** Windows Compatible
