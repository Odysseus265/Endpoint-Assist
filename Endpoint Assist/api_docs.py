"""
Endpoint Assist - API Documentation
OpenAPI/Swagger specification for the REST API
"""

API_SPEC = {
    "openapi": "3.0.3",
    "info": {
        "title": "Endpoint Assist API",
        "description": "Professional IT Help Desk Dashboard - REST API Documentation",
        "version": "1.0.0",
        "contact": {
            "name": "API Support",
            "email": "support@endpointassist.local"
        },
        "license": {
            "name": "MIT",
            "url": "https://opensource.org/licenses/MIT"
        }
    },
    "servers": [
        {
            "url": "http://localhost:5001",
            "description": "Development server"
        }
    ],
    "tags": [
        {"name": "Authentication", "description": "User authentication endpoints"},
        {"name": "System", "description": "System diagnostics and health monitoring"},
        {"name": "Network", "description": "Network diagnostic tools"},
        {"name": "Devices", "description": "Peripheral device management"},
        {"name": "Security", "description": "Security status and monitoring"},
        {"name": "Tickets", "description": "Help desk ticket management"},
        {"name": "Reports", "description": "Report generation"},
        {"name": "Tools", "description": "IT maintenance tools"},
        {"name": "Audit", "description": "Audit logging"}
    ],
    "paths": {
        "/api/auth/login": {
            "post": {
                "tags": ["Authentication"],
                "summary": "User login",
                "description": "Authenticate user and receive session token",
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "required": ["username", "password"],
                                "properties": {
                                    "username": {"type": "string", "example": "admin"},
                                    "password": {"type": "string", "example": "password123"}
                                }
                            }
                        }
                    }
                },
                "responses": {
                    "200": {
                        "description": "Login successful",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "status": {"type": "string", "example": "success"},
                                        "data": {
                                            "type": "object",
                                            "properties": {
                                                "token": {"type": "string"},
                                                "user": {"$ref": "#/components/schemas/User"}
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    },
                    "401": {"description": "Invalid credentials"}
                }
            }
        },
        "/api/auth/logout": {
            "post": {
                "tags": ["Authentication"],
                "summary": "User logout",
                "security": [{"bearerAuth": []}],
                "responses": {
                    "200": {"description": "Logout successful"}
                }
            }
        },
        "/api/system/health": {
            "get": {
                "tags": ["System"],
                "summary": "Get system health",
                "description": "Returns comprehensive system health information including CPU, memory, disk, and battery status",
                "responses": {
                    "200": {
                        "description": "System health data",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "status": {"type": "string"},
                                        "data": {
                                            "type": "object",
                                            "properties": {
                                                "os": {"$ref": "#/components/schemas/OSInfo"},
                                                "cpu": {"$ref": "#/components/schemas/CPUInfo"},
                                                "memory": {"$ref": "#/components/schemas/MemoryInfo"},
                                                "disks": {
                                                    "type": "array",
                                                    "items": {"$ref": "#/components/schemas/DiskInfo"}
                                                },
                                                "battery": {"$ref": "#/components/schemas/BatteryInfo"}
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        },
        "/api/system/processes": {
            "get": {
                "tags": ["System"],
                "summary": "Get running processes",
                "description": "Returns list of running processes sorted by CPU usage",
                "responses": {
                    "200": {
                        "description": "Process list",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "status": {"type": "string"},
                                        "data": {
                                            "type": "array",
                                            "items": {"$ref": "#/components/schemas/Process"}
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        },
        "/api/system/startup": {
            "get": {
                "tags": ["System"],
                "summary": "Get startup programs",
                "responses": {
                    "200": {"description": "Startup programs list"}
                }
            }
        },
        "/api/system/clean-temp": {
            "post": {
                "tags": ["Tools"],
                "summary": "Clean temporary files",
                "description": "Removes temporary files from system temp directories",
                "responses": {
                    "200": {
                        "description": "Cleanup results",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "status": {"type": "string"},
                                        "data": {
                                            "type": "object",
                                            "properties": {
                                                "files_deleted": {"type": "integer"},
                                                "space_freed_mb": {"type": "number"}
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        },
        "/api/network/info": {
            "get": {
                "tags": ["Network"],
                "summary": "Get network information",
                "description": "Returns network configuration including IP addresses and interfaces",
                "responses": {
                    "200": {"description": "Network information"}
                }
            }
        },
        "/api/network/ping": {
            "get": {
                "tags": ["Network"],
                "summary": "Ping test",
                "parameters": [
                    {
                        "name": "target",
                        "in": "query",
                        "description": "Target host to ping",
                        "schema": {"type": "string", "default": "8.8.8.8"}
                    }
                ],
                "responses": {
                    "200": {"description": "Ping results"}
                }
            }
        },
        "/api/network/dns": {
            "get": {
                "tags": ["Network"],
                "summary": "DNS resolution test",
                "parameters": [
                    {
                        "name": "domain",
                        "in": "query",
                        "description": "Domain to resolve",
                        "schema": {"type": "string", "default": "google.com"}
                    }
                ],
                "responses": {
                    "200": {"description": "DNS resolution result"}
                }
            }
        },
        "/api/network/port-check": {
            "get": {
                "tags": ["Network"],
                "summary": "Check port connectivity",
                "parameters": [
                    {
                        "name": "host",
                        "in": "query",
                        "schema": {"type": "string", "default": "8.8.8.8"}
                    },
                    {
                        "name": "port",
                        "in": "query",
                        "schema": {"type": "integer", "default": 80}
                    }
                ],
                "responses": {
                    "200": {"description": "Port check result"}
                }
            }
        },
        "/api/network/traceroute": {
            "get": {
                "tags": ["Network"],
                "summary": "Traceroute to target",
                "parameters": [
                    {
                        "name": "target",
                        "in": "query",
                        "schema": {"type": "string", "default": "8.8.8.8"}
                    }
                ],
                "responses": {
                    "200": {"description": "Traceroute results"}
                }
            }
        },
        "/api/security/status": {
            "get": {
                "tags": ["Security"],
                "summary": "Get security status",
                "description": "Returns Windows Defender, Firewall, and update status",
                "responses": {
                    "200": {"description": "Security status"}
                }
            }
        },
        "/api/devices/printers": {
            "get": {
                "tags": ["Devices"],
                "summary": "Get connected printers",
                "responses": {
                    "200": {"description": "Printer list"}
                }
            }
        },
        "/api/devices/audio": {
            "get": {
                "tags": ["Devices"],
                "summary": "Get audio devices",
                "responses": {
                    "200": {"description": "Audio device list"}
                }
            }
        },
        "/api/devices/usb": {
            "get": {
                "tags": ["Devices"],
                "summary": "Get USB devices",
                "responses": {
                    "200": {"description": "USB device list"}
                }
            }
        },
        "/api/devices/bluetooth": {
            "get": {
                "tags": ["Devices"],
                "summary": "Get Bluetooth devices",
                "responses": {
                    "200": {"description": "Bluetooth device list"}
                }
            }
        },
        "/api/tickets": {
            "get": {
                "tags": ["Tickets"],
                "summary": "Get all tickets",
                "parameters": [
                    {
                        "name": "status",
                        "in": "query",
                        "description": "Filter by status",
                        "schema": {"type": "string", "enum": ["open", "in-progress", "resolved", "closed"]}
                    }
                ],
                "responses": {
                    "200": {"description": "Ticket list"}
                }
            },
            "post": {
                "tags": ["Tickets"],
                "summary": "Create a ticket",
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {"$ref": "#/components/schemas/TicketCreate"}
                        }
                    }
                },
                "responses": {
                    "200": {"description": "Ticket created"}
                }
            }
        },
        "/api/tickets/{ticket_id}": {
            "put": {
                "tags": ["Tickets"],
                "summary": "Update a ticket",
                "parameters": [
                    {
                        "name": "ticket_id",
                        "in": "path",
                        "required": True,
                        "schema": {"type": "string"}
                    }
                ],
                "requestBody": {
                    "content": {
                        "application/json": {
                            "schema": {"$ref": "#/components/schemas/TicketUpdate"}
                        }
                    }
                },
                "responses": {
                    "200": {"description": "Ticket updated"}
                }
            },
            "delete": {
                "tags": ["Tickets"],
                "summary": "Delete a ticket",
                "parameters": [
                    {
                        "name": "ticket_id",
                        "in": "path",
                        "required": True,
                        "schema": {"type": "string"}
                    }
                ],
                "responses": {
                    "200": {"description": "Ticket deleted"}
                }
            }
        },
        "/api/reports/pdf/system": {
            "get": {
                "tags": ["Reports"],
                "summary": "Generate system PDF report",
                "responses": {
                    "200": {
                        "description": "PDF file",
                        "content": {"application/pdf": {}}
                    }
                }
            }
        },
        "/api/reports/pdf/network": {
            "get": {
                "tags": ["Reports"],
                "summary": "Generate network PDF report",
                "responses": {
                    "200": {
                        "description": "PDF file",
                        "content": {"application/pdf": {}}
                    }
                }
            }
        },
        "/api/reports/pdf/full": {
            "get": {
                "tags": ["Reports"],
                "summary": "Generate comprehensive PDF report",
                "responses": {
                    "200": {
                        "description": "PDF file",
                        "content": {"application/pdf": {}}
                    }
                }
            }
        },
        "/api/reports/excel": {
            "get": {
                "tags": ["Reports"],
                "summary": "Generate Excel report",
                "responses": {
                    "200": {
                        "description": "Excel file",
                        "content": {"application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": {}}
                    }
                }
            }
        },
        "/api/audit-logs": {
            "get": {
                "tags": ["Audit"],
                "summary": "Get audit logs",
                "parameters": [
                    {
                        "name": "limit",
                        "in": "query",
                        "schema": {"type": "integer", "default": 100}
                    },
                    {
                        "name": "action",
                        "in": "query",
                        "description": "Filter by action type",
                        "schema": {"type": "string"}
                    }
                ],
                "responses": {
                    "200": {"description": "Audit log list"}
                }
            }
        },
        "/api/tools/flush-dns": {
            "post": {
                "tags": ["Tools"],
                "summary": "Flush DNS cache",
                "responses": {
                    "200": {"description": "DNS cache flushed"}
                }
            }
        },
        "/api/tools/network-reset": {
            "post": {
                "tags": ["Tools"],
                "summary": "Reset network configuration",
                "responses": {
                    "200": {"description": "Network reset complete"}
                }
            }
        }
    },
    "components": {
        "securitySchemes": {
            "bearerAuth": {
                "type": "http",
                "scheme": "bearer",
                "bearerFormat": "JWT"
            }
        },
        "schemas": {
            "User": {
                "type": "object",
                "properties": {
                    "id": {"type": "integer"},
                    "username": {"type": "string"},
                    "email": {"type": "string"},
                    "full_name": {"type": "string"},
                    "role": {"type": "string", "enum": ["admin", "technician", "viewer"]}
                }
            },
            "OSInfo": {
                "type": "object",
                "properties": {
                    "system": {"type": "string"},
                    "release": {"type": "string"},
                    "version": {"type": "string"},
                    "hostname": {"type": "string"},
                    "boot_time": {"type": "string", "format": "date-time"}
                }
            },
            "CPUInfo": {
                "type": "object",
                "properties": {
                    "physical_cores": {"type": "integer"},
                    "logical_cores": {"type": "integer"},
                    "usage_percent": {"type": "number"}
                }
            },
            "MemoryInfo": {
                "type": "object",
                "properties": {
                    "total_gb": {"type": "number"},
                    "used_gb": {"type": "number"},
                    "available_gb": {"type": "number"},
                    "percent": {"type": "number"}
                }
            },
            "DiskInfo": {
                "type": "object",
                "properties": {
                    "device": {"type": "string"},
                    "mountpoint": {"type": "string"},
                    "total_gb": {"type": "number"},
                    "free_gb": {"type": "number"},
                    "percent": {"type": "number"}
                }
            },
            "BatteryInfo": {
                "type": "object",
                "nullable": True,
                "properties": {
                    "percent": {"type": "number"},
                    "power_plugged": {"type": "boolean"},
                    "time_left": {"type": "string"}
                }
            },
            "Process": {
                "type": "object",
                "properties": {
                    "pid": {"type": "integer"},
                    "name": {"type": "string"},
                    "cpu_percent": {"type": "number"},
                    "memory_percent": {"type": "number"},
                    "status": {"type": "string"}
                }
            },
            "TicketCreate": {
                "type": "object",
                "required": ["title"],
                "properties": {
                    "title": {"type": "string"},
                    "description": {"type": "string"},
                    "category": {"type": "string"},
                    "priority": {"type": "string", "enum": ["low", "medium", "high", "critical"]}
                }
            },
            "TicketUpdate": {
                "type": "object",
                "properties": {
                    "status": {"type": "string", "enum": ["open", "in-progress", "resolved", "closed"]},
                    "priority": {"type": "string"},
                    "resolution": {"type": "string"}
                }
            }
        }
    }
}

def get_swagger_ui_html():
    """Generate Swagger UI HTML page"""
    return '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Endpoint Assist - API Documentation</title>
    <link rel="stylesheet" href="https://unpkg.com/swagger-ui-dist@5.9.0/swagger-ui.css">
    <style>
        body { margin: 0; padding: 0; }
        .swagger-ui .topbar { display: none; }
        .swagger-ui .info { margin: 20px 0; }
        .swagger-ui .info .title { color: #d00000; }
    </style>
</head>
<body>
    <div id="swagger-ui"></div>
    <script src="https://unpkg.com/swagger-ui-dist@5.9.0/swagger-ui-bundle.js"></script>
    <script>
        window.onload = function() {
            SwaggerUIBundle({
                url: "/api/docs/spec",
                dom_id: '#swagger-ui',
                presets: [
                    SwaggerUIBundle.presets.apis,
                    SwaggerUIBundle.SwaggerUIStandalonePreset
                ],
                layout: "BaseLayout",
                deepLinking: true,
                showExtensions: true,
                showCommonExtensions: true
            });
        };
    </script>
</body>
</html>
'''
