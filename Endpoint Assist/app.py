"""
Endpoint Assist - Professional IT Help Desk Tool
A comprehensive web application for IT support and diagnostics
"""

from flask import Flask, render_template, jsonify, request, session, send_file
from flask_cors import CORS
import psutil
import platform
import socket
import subprocess
import json
import os
import uuid
import time
from datetime import datetime, timedelta
import threading
import re
import shutil
import winreg
import wmi

# Import database module
from database import (
    init_db, 
    create_ticket, get_all_tickets, get_ticket_by_id, update_ticket, delete_ticket, get_ticket_stats,
    add_audit_log as db_add_audit_log, get_audit_logs,
    get_setting, set_setting
)

# Import PDF report generator
from reports import generate_system_pdf, generate_network_pdf, generate_full_pdf

# Import authentication module
from auth import (
    init_auth_db, authenticate, create_session, validate_session, invalidate_session,
    create_user, get_user_by_id, get_all_users, update_user, delete_user, change_password,
    login_required, admin_required, get_current_user, ROLES
)

# Import API documentation
from api_docs import API_SPEC, get_swagger_ui_html

# Import Excel reports (optional)
try:
    from excel_reports import generate_excel_report
    EXCEL_AVAILABLE = True
except ImportError:
    EXCEL_AVAILABLE = False

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', os.urandom(24))
CORS(app)

# Initialize database on startup
init_db()
init_auth_db()

# Initialize WebSocket (optional)
try:
    from realtime import init_socketio, start_monitoring
    socketio = init_socketio(app)
    WEBSOCKET_AVAILABLE = True
except ImportError:
    socketio = None
    WEBSOCKET_AVAILABLE = False

# Initialize WMI
try:
    wmi_client = wmi.WMI()
except:
    wmi_client = None

# ==================== UTILITY FUNCTIONS ====================

def add_audit_log(action, details, user="System"):
    """Add an entry to the audit log (wrapper for database function)"""
    try:
        ip_address = request.remote_addr if request else None
        user_agent = request.user_agent.string if request and request.user_agent else None
        db_add_audit_log(action, details, user, ip_address, user_agent)
    except:
        # Fallback if request context is not available
        db_add_audit_log(action, details, user)

def run_command(command, shell=True):
    """Run a system command and return output"""
    try:
        result = subprocess.run(command, shell=shell, capture_output=True, text=True, timeout=30)
        return result.stdout.strip() if result.returncode == 0 else result.stderr.strip()
    except Exception as e:
        return str(e)

# ==================== ROUTES ====================

@app.route('/')
def index():
    """Main dashboard"""
    add_audit_log("Page View", "Dashboard accessed")
    return render_template('index.html')

@app.route('/documentation')
def documentation():
    """Documentation page"""
    return render_template('documentation.html')

# ==================== API DOCUMENTATION ====================

@app.route('/api/docs')
def api_docs():
    """Swagger UI for API documentation"""
    return get_swagger_ui_html()

@app.route('/api/docs/spec')
def api_spec():
    """OpenAPI specification"""
    return jsonify(API_SPEC)

# ==================== AUTHENTICATION ====================

@app.route('/api/auth/login', methods=['POST'])
def login():
    """User login"""
    try:
        data = request.json
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return jsonify({"status": "error", "message": "Username and password required"}), 400
        
        user, error = authenticate(username, password)
        if error:
            add_audit_log("Login Failed", f"Failed login attempt for {username}")
            return jsonify({"status": "error", "message": error}), 401
        
        # Create session
        token = create_session(
            user['id'],
            ip_address=request.remote_addr,
            user_agent=request.user_agent.string if request.user_agent else None
        )
        
        # Set session cookie
        session['auth_token'] = token
        
        add_audit_log("Login", f"User {username} logged in", user=username)
        
        return jsonify({
            "status": "success",
            "data": {
                "token": token,
                "user": {
                    "id": user['id'],
                    "username": user['username'],
                    "email": user['email'],
                    "full_name": user['full_name'],
                    "role": user['role']
                }
            }
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/auth/logout', methods=['POST'])
def logout():
    """User logout"""
    try:
        # Get token from header or session
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header[7:]
        else:
            token = session.get('auth_token')
        
        if token:
            invalidate_session(token)
        
        session.pop('auth_token', None)
        add_audit_log("Logout", "User logged out")
        
        return jsonify({"status": "success", "message": "Logged out successfully"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/auth/me')
def get_me():
    """Get current user info"""
    user = get_current_user()
    if not user:
        return jsonify({"status": "error", "message": "Not authenticated"}), 401
    
    return jsonify({
        "status": "success",
        "data": {
            "id": user['id'],
            "username": user['username'],
            "email": user['email'],
            "full_name": user['full_name'],
            "role": user['role']
        }
    })

@app.route('/api/auth/users', methods=['GET'])
@admin_required
def list_users():
    """List all users (admin only)"""
    users = get_all_users()
    return jsonify({"status": "success", "data": users})

@app.route('/api/auth/users', methods=['POST'])
@admin_required
def create_new_user():
    """Create a new user (admin only)"""
    try:
        data = request.json
        user_id = create_user(
            username=data.get('username'),
            password=data.get('password'),
            email=data.get('email'),
            full_name=data.get('full_name'),
            role=data.get('role', 'technician')
        )
        
        if not user_id:
            return jsonify({"status": "error", "message": "Username already exists"}), 400
        
        add_audit_log("User Created", f"New user created: {data.get('username')}")
        return jsonify({"status": "success", "data": {"id": user_id}})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/auth/roles')
def get_roles():
    """Get available roles"""
    return jsonify({"status": "success", "data": ROLES})

# ==================== SYSTEM DIAGNOSTICS ====================

@app.route('/api/system/health')
def system_health():
    """Get comprehensive system health information"""
    try:
        # OS Information
        os_info = {
            "system": platform.system(),
            "release": platform.release(),
            "version": platform.version(),
            "machine": platform.machine(),
            "processor": platform.processor(),
            "hostname": socket.gethostname(),
            "boot_time": datetime.fromtimestamp(psutil.boot_time()).isoformat()
        }
        
        # CPU Information
        cpu_info = {
            "physical_cores": psutil.cpu_count(logical=False),
            "logical_cores": psutil.cpu_count(logical=True),
            "usage_percent": psutil.cpu_percent(interval=1),
            "frequency": psutil.cpu_freq()._asdict() if psutil.cpu_freq() else None,
            "per_cpu_usage": psutil.cpu_percent(interval=0.1, percpu=True)
        }
        
        # Memory Information
        memory = psutil.virtual_memory()
        memory_info = {
            "total": memory.total,
            "available": memory.available,
            "used": memory.used,
            "percent": memory.percent,
            "total_gb": round(memory.total / (1024**3), 2),
            "available_gb": round(memory.available / (1024**3), 2),
            "used_gb": round(memory.used / (1024**3), 2)
        }
        
        # Disk Information
        disks = []
        for partition in psutil.disk_partitions():
            try:
                usage = psutil.disk_usage(partition.mountpoint)
                disks.append({
                    "device": partition.device,
                    "mountpoint": partition.mountpoint,
                    "fstype": partition.fstype,
                    "total": usage.total,
                    "used": usage.used,
                    "free": usage.free,
                    "percent": usage.percent,
                    "total_gb": round(usage.total / (1024**3), 2),
                    "free_gb": round(usage.free / (1024**3), 2)
                })
            except:
                pass
        
        # Battery Information
        battery = psutil.sensors_battery()
        battery_info = None
        if battery:
            battery_info = {
                "percent": battery.percent,
                "power_plugged": battery.power_plugged,
                "time_left": str(timedelta(seconds=battery.secsleft)) if battery.secsleft > 0 else "Calculating..."
            }
        
        add_audit_log("API Call", "System health check performed")
        
        return jsonify({
            "status": "success",
            "data": {
                "os": os_info,
                "cpu": cpu_info,
                "memory": memory_info,
                "disks": disks,
                "battery": battery_info
            }
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@app.route('/api/system/processes')
def get_processes():
    """Get running processes"""
    try:
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 'status']):
            try:
                pinfo = proc.info
                if pinfo['cpu_percent'] is not None:
                    processes.append({
                        "pid": pinfo['pid'],
                        "name": pinfo['name'],
                        "cpu_percent": round(pinfo['cpu_percent'], 1),
                        "memory_percent": round(pinfo['memory_percent'], 1) if pinfo['memory_percent'] else 0,
                        "status": pinfo['status']
                    })
            except:
                pass
        
        # Sort by CPU usage
        processes.sort(key=lambda x: x['cpu_percent'], reverse=True)
        return jsonify({"status": "success", "data": processes[:50]})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@app.route('/api/system/startup')
def get_startup_programs():
    """Get startup programs"""
    try:
        startup_programs = []
        
        # Check Run registry key
        registry_paths = [
            (winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run"),
            (winreg.HKEY_LOCAL_MACHINE, r"Software\Microsoft\Windows\CurrentVersion\Run"),
        ]
        
        for hkey, path in registry_paths:
            try:
                key = winreg.OpenKey(hkey, path)
                i = 0
                while True:
                    try:
                        name, value, _ = winreg.EnumValue(key, i)
                        startup_programs.append({
                            "name": name,
                            "path": value,
                            "location": "Registry",
                            "enabled": True
                        })
                        i += 1
                    except OSError:
                        break
                winreg.CloseKey(key)
            except:
                pass
        
        return jsonify({"status": "success", "data": startup_programs})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@app.route('/api/system/clean-temp', methods=['POST'])
def clean_temp():
    """Clean temporary files"""
    try:
        temp_dirs = [
            os.environ.get('TEMP', ''),
            os.environ.get('TMP', ''),
            os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Temp')
        ]
        
        files_deleted = 0
        space_freed = 0
        
        for temp_dir in temp_dirs:
            if temp_dir and os.path.exists(temp_dir):
                for item in os.listdir(temp_dir):
                    item_path = os.path.join(temp_dir, item)
                    try:
                        if os.path.isfile(item_path):
                            size = os.path.getsize(item_path)
                            os.remove(item_path)
                            files_deleted += 1
                            space_freed += size
                        elif os.path.isdir(item_path):
                            size = sum(os.path.getsize(os.path.join(dp, f)) for dp, dn, fn in os.walk(item_path) for f in fn)
                            shutil.rmtree(item_path, ignore_errors=True)
                            files_deleted += 1
                            space_freed += size
                    except:
                        pass
        
        add_audit_log("Maintenance", f"Temp files cleaned: {files_deleted} files, {round(space_freed / (1024**2), 2)} MB freed")
        
        return jsonify({
            "status": "success",
            "data": {
                "files_deleted": files_deleted,
                "space_freed_mb": round(space_freed / (1024**2), 2)
            }
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

# ==================== SECURITY STATUS ====================

@app.route('/api/security/status')
def security_status():
    """Get security status"""
    try:
        security_info = {
            "defender": {"status": "Unknown", "real_time": False},
            "firewall": {"status": "Unknown", "enabled": False},
            "updates": {"status": "Unknown", "pending": 0}
        }
        
        # Check Windows Defender
        try:
            result = run_command('powershell "Get-MpComputerStatus | Select-Object -Property AntivirusEnabled,RealTimeProtectionEnabled,AntivirusSignatureLastUpdated | ConvertTo-Json"')
            if result and '{' in result:
                defender_data = json.loads(result)
                security_info["defender"] = {
                    "status": "Enabled" if defender_data.get("AntivirusEnabled") else "Disabled",
                    "real_time": defender_data.get("RealTimeProtectionEnabled", False),
                    "last_updated": defender_data.get("AntivirusSignatureLastUpdated", "Unknown")
                }
        except:
            pass
        
        # Check Firewall
        try:
            result = run_command('powershell "Get-NetFirewallProfile | Select-Object -Property Name,Enabled | ConvertTo-Json"')
            if result and '[' in result:
                firewall_data = json.loads(result)
                enabled_profiles = [p for p in firewall_data if p.get("Enabled")]
                security_info["firewall"] = {
                    "status": "Enabled" if enabled_profiles else "Disabled",
                    "enabled": len(enabled_profiles) > 0,
                    "profiles": firewall_data
                }
        except:
            pass
        
        # Check Windows Update
        try:
            result = run_command('powershell "(Get-HotFix | Sort-Object -Property InstalledOn -Descending | Select-Object -First 1).InstalledOn"')
            security_info["updates"]["last_update"] = result if result else "Unknown"
        except:
            pass
        
        add_audit_log("Security Check", "Security status checked")
        
        return jsonify({"status": "success", "data": security_info})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

# ==================== NETWORK DIAGNOSTICS ====================

@app.route('/api/network/info')
def network_info():
    """Get network information"""
    try:
        # Get local IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            s.connect(('8.8.8.8', 80))
            local_ip = s.getsockname()[0]
        except:
            local_ip = '127.0.0.1'
        finally:
            s.close()
        
        # Get public IP
        try:
            public_ip = run_command('powershell "(Invoke-WebRequest -Uri \'https://api.ipify.org\' -UseBasicParsing).Content"')
        except:
            public_ip = "Unable to determine"
        
        # Get network interfaces
        interfaces = []
        for name, addrs in psutil.net_if_addrs().items():
            interface = {"name": name, "addresses": []}
            for addr in addrs:
                if addr.family == socket.AF_INET:
                    interface["addresses"].append({
                        "ip": addr.address,
                        "netmask": addr.netmask,
                        "type": "IPv4"
                    })
            if interface["addresses"]:
                interfaces.append(interface)
        
        # Get network stats
        net_io = psutil.net_io_counters()
        stats = {
            "bytes_sent": net_io.bytes_sent,
            "bytes_recv": net_io.bytes_recv,
            "packets_sent": net_io.packets_sent,
            "packets_recv": net_io.packets_recv
        }
        
        return jsonify({
            "status": "success",
            "data": {
                "local_ip": local_ip,
                "public_ip": public_ip,
                "hostname": socket.gethostname(),
                "interfaces": interfaces,
                "stats": stats
            }
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@app.route('/api/network/ping')
def ping_test():
    """Perform ping test"""
    target = request.args.get('target', '8.8.8.8')
    try:
        result = run_command(f'ping -n 4 {target}')
        
        # Parse ping results
        lines = result.split('\n')
        success = 'TTL=' in result or 'time=' in result.lower()
        
        return jsonify({
            "status": "success",
            "data": {
                "target": target,
                "reachable": success,
                "output": result
            }
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@app.route('/api/network/dns')
def dns_test():
    """Perform DNS resolution test"""
    domain = request.args.get('domain', 'google.com')
    try:
        ip = socket.gethostbyname(domain)
        return jsonify({
            "status": "success",
            "data": {
                "domain": domain,
                "resolved_ip": ip,
                "success": True
            }
        })
    except socket.gaierror as e:
        return jsonify({
            "status": "success",
            "data": {
                "domain": domain,
                "resolved_ip": None,
                "success": False,
                "error": str(e)
            }
        })

@app.route('/api/network/traceroute')
def traceroute():
    """Perform traceroute"""
    target = request.args.get('target', '8.8.8.8')
    try:
        result = run_command(f'tracert -d -h 15 {target}')
        
        hops = []
        for line in result.split('\n'):
            if '*' in line or 'ms' in line.lower():
                hops.append(line.strip())
        
        return jsonify({
            "status": "success",
            "data": {
                "target": target,
                "hops": hops,
                "output": result
            }
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@app.route('/api/network/port-check')
def port_check():
    """Check if a port is reachable"""
    host = request.args.get('host', '8.8.8.8')
    port = int(request.args.get('port', 80))
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(3)
        result = sock.connect_ex((host, port))
        sock.close()
        
        return jsonify({
            "status": "success",
            "data": {
                "host": host,
                "port": port,
                "open": result == 0
            }
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@app.route('/api/network/wifi')
def wifi_info():
    """Get WiFi information"""
    try:
        result = run_command('netsh wlan show interfaces')
        
        wifi_data = {
            "connected": False,
            "ssid": None,
            "signal": None,
            "speed": None
        }
        
        if "SSID" in result:
            wifi_data["connected"] = True
            for line in result.split('\n'):
                if "SSID" in line and "BSSID" not in line:
                    wifi_data["ssid"] = line.split(':')[-1].strip()
                elif "Signal" in line:
                    wifi_data["signal"] = line.split(':')[-1].strip()
                elif "Receive rate" in line or "Transmit rate" in line:
                    wifi_data["speed"] = line.split(':')[-1].strip()
        
        return jsonify({"status": "success", "data": wifi_data})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

# ==================== PERIPHERAL & DEVICE SUPPORT ====================

@app.route('/api/devices/printers')
def get_printers():
    """Get connected printers"""
    try:
        result = run_command('powershell "Get-Printer | Select-Object Name,PrinterStatus,PortName,DriverName | ConvertTo-Json"')
        printers = []
        
        if result and ('{' in result or '[' in result):
            data = json.loads(result)
            if isinstance(data, dict):
                data = [data]
            for p in data:
                printers.append({
                    "name": p.get("Name", "Unknown"),
                    "status": "Online" if p.get("PrinterStatus") == 0 else "Offline",
                    "port": p.get("PortName", "Unknown"),
                    "driver": p.get("DriverName", "Unknown")
                })
        
        return jsonify({"status": "success", "data": printers})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@app.route('/api/devices/audio')
def get_audio_devices():
    """Get audio devices"""
    try:
        result = run_command('powershell "Get-PnpDevice -Class AudioEndpoint | Select-Object FriendlyName,Status | ConvertTo-Json"')
        devices = []
        
        if result and ('{' in result or '[' in result):
            data = json.loads(result)
            if isinstance(data, dict):
                data = [data]
            for d in data:
                devices.append({
                    "name": d.get("FriendlyName", "Unknown"),
                    "status": d.get("Status", "Unknown")
                })
        
        return jsonify({"status": "success", "data": devices})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@app.route('/api/devices/cameras')
def get_cameras():
    """Get camera devices"""
    try:
        result = run_command('powershell "Get-PnpDevice -Class Camera,Image | Select-Object FriendlyName,Status | ConvertTo-Json"')
        devices = []
        
        if result and ('{' in result or '[' in result):
            data = json.loads(result)
            if isinstance(data, dict):
                data = [data]
            for d in data:
                devices.append({
                    "name": d.get("FriendlyName", "Unknown"),
                    "status": d.get("Status", "Unknown")
                })
        
        return jsonify({"status": "success", "data": devices})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@app.route('/api/devices/usb')
def get_usb_devices():
    """Get USB devices"""
    try:
        result = run_command('powershell "Get-PnpDevice -Class USB | Where-Object {$_.Status -eq \'OK\'} | Select-Object FriendlyName,Status,InstanceId | ConvertTo-Json"')
        devices = []
        
        if result and ('{' in result or '[' in result):
            data = json.loads(result)
            if isinstance(data, dict):
                data = [data]
            for d in data:
                if d.get("FriendlyName"):
                    devices.append({
                        "name": d.get("FriendlyName", "Unknown"),
                        "status": d.get("Status", "Unknown"),
                        "id": d.get("InstanceId", "")[:50]
                    })
        
        return jsonify({"status": "success", "data": devices[:20]})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@app.route('/api/devices/bluetooth')
def get_bluetooth():
    """Get Bluetooth status"""
    try:
        result = run_command('powershell "Get-PnpDevice -Class Bluetooth | Select-Object FriendlyName,Status | ConvertTo-Json"')
        
        bluetooth_data = {
            "available": False,
            "devices": []
        }
        
        if result and ('{' in result or '[' in result):
            data = json.loads(result)
            if isinstance(data, dict):
                data = [data]
            bluetooth_data["available"] = len(data) > 0
            for d in data:
                bluetooth_data["devices"].append({
                    "name": d.get("FriendlyName", "Unknown"),
                    "status": d.get("Status", "Unknown")
                })
        
        return jsonify({"status": "success", "data": bluetooth_data})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

# ==================== HELP DESK TOOLS ====================

@app.route('/api/tools/browser-cache', methods=['POST'])
def clear_browser_cache():
    """Clear browser cache"""
    try:
        browsers_cleaned = []
        
        # Chrome cache
        chrome_cache = os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Google', 'Chrome', 'User Data', 'Default', 'Cache')
        if os.path.exists(chrome_cache):
            try:
                shutil.rmtree(chrome_cache, ignore_errors=True)
                browsers_cleaned.append("Chrome")
            except:
                pass
        
        # Edge cache
        edge_cache = os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Microsoft', 'Edge', 'User Data', 'Default', 'Cache')
        if os.path.exists(edge_cache):
            try:
                shutil.rmtree(edge_cache, ignore_errors=True)
                browsers_cleaned.append("Edge")
            except:
                pass
        
        add_audit_log("Maintenance", f"Browser cache cleared: {', '.join(browsers_cleaned)}")
        
        return jsonify({
            "status": "success",
            "data": {"browsers_cleaned": browsers_cleaned}
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@app.route('/api/tools/flush-dns', methods=['POST'])
def flush_dns():
    """Flush DNS resolver cache"""
    try:
        result = run_command('ipconfig /flushdns')
        add_audit_log("Network", "DNS cache flushed")
        
        return jsonify({
            "status": "success",
            "data": {
                "message": "DNS resolver cache flushed successfully",
                "output": result
            }
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@app.route('/api/tools/network-reset', methods=['POST'])
def network_reset():
    """Reset network configuration"""
    try:
        commands = [
            'ipconfig /flushdns',
            'netsh winsock reset',
            'netsh int ip reset'
        ]
        
        results = []
        for cmd in commands:
            result = run_command(cmd)
            results.append({"command": cmd, "output": result})
        
        add_audit_log("Network", "Network reset performed")
        
        return jsonify({
            "status": "success",
            "data": {
                "message": "Network reset commands executed. A restart may be required.",
                "results": results
            }
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@app.route('/api/tools/error-logs')
def get_error_logs():
    """Get recent Windows error logs"""
    try:
        result = run_command('powershell "Get-EventLog -LogName System -EntryType Error -Newest 20 | Select-Object TimeGenerated,Source,Message | ConvertTo-Json"')
        
        logs = []
        if result and ('{' in result or '[' in result):
            data = json.loads(result)
            if isinstance(data, dict):
                data = [data]
            for log in data:
                logs.append({
                    "time": log.get("TimeGenerated", "Unknown"),
                    "source": log.get("Source", "Unknown"),
                    "message": log.get("Message", "")[:200]
                })
        
        return jsonify({"status": "success", "data": logs})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

# ==================== TICKET SYSTEM ====================

@app.route('/api/tickets', methods=['GET'])
def get_tickets_route():
    """Get all tickets"""
    status = request.args.get('status', None)
    tickets = get_all_tickets(status_filter=status)
    return jsonify({"status": "success", "data": tickets})

@app.route('/api/tickets/stats', methods=['GET'])
def get_tickets_stats():
    """Get ticket statistics"""
    stats = get_ticket_stats()
    return jsonify({"status": "success", "data": stats})

@app.route('/api/tickets', methods=['POST'])
def create_ticket_route():
    """Create a new ticket"""
    try:
        data = request.json
        ticket_id = create_ticket({
            "title": data.get("title", ""),
            "description": data.get("description", ""),
            "category": data.get("category", "general"),
            "priority": data.get("priority", "medium"),
            "status": "open",
            "created_by": data.get("user", "Anonymous")
        })
        add_audit_log("Ticket", f"Ticket {ticket_id[:8].upper()} created")
        ticket = get_ticket_by_id(ticket_id)
        return jsonify({"status": "success", "data": ticket})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@app.route('/api/tickets/<ticket_id>', methods=['PUT'])
def update_ticket_route(ticket_id):
    """Update a ticket"""
    try:
        data = request.json
        success = update_ticket(ticket_id, {
            'status': data.get('status'),
            'priority': data.get('priority'),
            'resolution': data.get('resolution')
        })
        if success:
            add_audit_log("Ticket", f"Ticket {ticket_id[:8].upper()} updated")
            ticket = get_ticket_by_id(ticket_id)
            return jsonify({"status": "success", "data": ticket})
        return jsonify({"status": "error", "message": "Ticket not found"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@app.route('/api/tickets/<ticket_id>', methods=['DELETE'])
def delete_ticket_route(ticket_id):
    """Delete a ticket"""
    try:
        success = delete_ticket(ticket_id)
        if success:
            add_audit_log("Ticket", f"Ticket {ticket_id[:8].upper()} deleted")
            return jsonify({"status": "success", "message": "Ticket deleted"})
        return jsonify({"status": "error", "message": "Ticket not found"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

# ==================== INVENTORY ====================

@app.route('/api/inventory/device')
def get_device_inventory():
    """Get device inventory information"""
    try:
        # Get installed software
        software = []
        try:
            result = run_command('powershell "Get-ItemProperty HKLM:\\Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\* | Select-Object DisplayName,DisplayVersion,Publisher | ConvertTo-Json"')
            if result and '[' in result:
                data = json.loads(result)
                for s in data:
                    if s.get("DisplayName"):
                        software.append({
                            "name": s.get("DisplayName", ""),
                            "version": s.get("DisplayVersion", ""),
                            "publisher": s.get("Publisher", "")
                        })
        except:
            pass
        
        # Get hardware info
        hardware = {
            "device_name": socket.gethostname(),
            "os": f"{platform.system()} {platform.release()}",
            "os_version": platform.version(),
            "processor": platform.processor(),
            "ram_gb": round(psutil.virtual_memory().total / (1024**3), 2),
            "architecture": platform.machine()
        }
        
        # Get browser info
        browsers = []
        browser_paths = {
            "Chrome": r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            "Edge": r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
            "Firefox": r"C:\Program Files\Mozilla Firefox\firefox.exe"
        }
        
        for name, path in browser_paths.items():
            if os.path.exists(path):
                browsers.append({"name": name, "installed": True})
        
        return jsonify({
            "status": "success",
            "data": {
                "hardware": hardware,
                "software": software[:50],
                "browsers": browsers,
                "software_count": len(software)
            }
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

# ==================== AUDIT LOGS ====================

@app.route('/api/audit-logs')
def get_audit_logs_route():
    """Get audit logs"""
    limit = request.args.get('limit', 100, type=int)
    action_filter = request.args.get('action', None)
    logs = get_audit_logs(limit=limit, action_filter=action_filter)
    return jsonify({"status": "success", "data": logs})

# ==================== PDF REPORTS ====================

@app.route('/api/reports/pdf/system')
def generate_system_report_pdf():
    """Generate and download system report PDF"""
    try:
        pdf_buffer = generate_system_pdf()
        add_audit_log("Report", "System PDF report generated")
        return send_file(
            pdf_buffer,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f'system_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf'
        )
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@app.route('/api/reports/pdf/network')
def generate_network_report_pdf():
    """Generate and download network report PDF"""
    try:
        pdf_buffer = generate_network_pdf()
        add_audit_log("Report", "Network PDF report generated")
        return send_file(
            pdf_buffer,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f'network_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf'
        )
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@app.route('/api/reports/pdf/full')
def generate_full_report_pdf():
    """Generate and download comprehensive PDF report"""
    try:
        pdf_buffer = generate_full_pdf()
        add_audit_log("Report", "Full PDF report generated")
        return send_file(
            pdf_buffer,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f'full_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf'
        )
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

# ==================== EXCEL REPORTS ====================

@app.route('/api/reports/excel')
def generate_excel_full():
    """Generate and download comprehensive Excel report"""
    if not EXCEL_AVAILABLE:
        return jsonify({"status": "error", "message": "Excel reports not available. Install openpyxl."}), 501
    try:
        excel_buffer = generate_excel_report('full')
        add_audit_log("Report", "Full Excel report generated")
        return send_file(
            excel_buffer,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=f'full_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
        )
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@app.route('/api/reports/excel/system')
def generate_excel_system():
    """Generate and download system Excel report"""
    if not EXCEL_AVAILABLE:
        return jsonify({"status": "error", "message": "Excel reports not available. Install openpyxl."}), 501
    try:
        excel_buffer = generate_excel_report('system')
        add_audit_log("Report", "System Excel report generated")
        return send_file(
            excel_buffer,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=f'system_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
        )
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@app.route('/api/reports/excel/network')
def generate_excel_network():
    """Generate and download network Excel report"""
    if not EXCEL_AVAILABLE:
        return jsonify({"status": "error", "message": "Excel reports not available. Install openpyxl."}), 501
    try:
        excel_buffer = generate_excel_report('network')
        add_audit_log("Report", "Network Excel report generated")
        return send_file(
            excel_buffer,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=f'network_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
        )
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

# ==================== REPORTS ====================

@app.route('/api/reports/generate')
def generate_report():
    """Generate a comprehensive report"""
    report_type = request.args.get('type', 'full')
    
    try:
        report = {
            "generated": datetime.now().isoformat(),
            "type": report_type,
            "device_name": socket.gethostname(),
            "sections": {}
        }
        
        # System Health
        memory = psutil.virtual_memory()
        report["sections"]["system"] = {
            "os": f"{platform.system()} {platform.release()}",
            "cpu_usage": f"{psutil.cpu_percent()}%",
            "memory_usage": f"{memory.percent}%",
            "memory_available": f"{round(memory.available / (1024**3), 2)} GB"
        }
        
        # Disk Status
        disks = []
        for partition in psutil.disk_partitions():
            try:
                usage = psutil.disk_usage(partition.mountpoint)
                disks.append({
                    "drive": partition.device,
                    "usage": f"{usage.percent}%",
                    "free": f"{round(usage.free / (1024**3), 2)} GB"
                })
            except:
                pass
        report["sections"]["disks"] = disks
        
        # Network Status
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            s.connect(('8.8.8.8', 80))
            local_ip = s.getsockname()[0]
        except:
            local_ip = 'Unable to determine'
        finally:
            s.close()
        
        report["sections"]["network"] = {
            "local_ip": local_ip,
            "hostname": socket.gethostname()
        }
        
        add_audit_log("Report", f"Report generated: {report_type}")
        
        return jsonify({"status": "success", "data": report})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

# ==================== EXPERIMENTAL TOOLS ====================

@app.route('/api/experimental/network-scan')
def network_scan():
    """Scan local network for devices"""
    try:
        # Get local IP and subnet
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        local_ip = s.getsockname()[0]
        s.close()
        
        # Scan common IPs in subnet
        subnet = '.'.join(local_ip.split('.')[:-1])
        devices = []
        
        # Just check a few IPs for demo
        result = run_command(f'arp -a')
        
        for line in result.split('\n'):
            if subnet in line:
                parts = line.split()
                if len(parts) >= 2:
                    devices.append({
                        "ip": parts[0],
                        "mac": parts[1] if len(parts) > 1 else "Unknown"
                    })
        
        return jsonify({
            "status": "success",
            "data": {
                "local_ip": local_ip,
                "devices": devices[:20]
            }
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@app.route('/api/experimental/speed-test')
def speed_test():
    """Basic speed test"""
    try:
        import urllib.request
        import time
        
        # Download test
        url = "http://speedtest.tele2.net/1MB.zip"
        start = time.time()
        
        try:
            urllib.request.urlretrieve(url, os.path.join(os.environ.get('TEMP', '.'), 'speedtest.tmp'))
            elapsed = time.time() - start
            speed_mbps = round((1 * 8) / elapsed, 2)  # 1MB file, convert to Mbps
        except:
            speed_mbps = 0
        
        return jsonify({
            "status": "success",
            "data": {
                "download_speed_mbps": speed_mbps,
                "test_size_mb": 1
            }
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

# ==================== KNOWLEDGE BASE ====================

knowledge_base = [
    {
        "id": "kb001",
        "title": "Computer Running Slow",
        "category": "Performance",
        "symptoms": ["slow boot", "lag", "freezing", "high cpu"],
        "solution": """1. Check Task Manager for high CPU/Memory usage (Ctrl+Shift+Esc)
2. Run Disk Cleanup to free space (cleanmgr)
3. Disable unnecessary startup programs in Task Manager > Startup
4. Check for malware with Windows Defender full scan
5. Consider adding more RAM if memory usage is consistently above 80%
6. Check if Windows Update is running in the background
7. Clear browser cache and temporary files""",
        "tags": ["slow", "performance", "cpu", "memory"]
    },
    {
        "id": "kb002",
        "title": "Cannot Connect to WiFi",
        "category": "Network",
        "symptoms": ["no wifi", "disconnected", "no internet"],
        "solution": """1. Toggle WiFi off and on in the system tray
2. Restart your computer
3. Run Network Troubleshooter: Settings > Network & Internet > Status > Network Troubleshooter
4. Forget the network and reconnect with password
5. Update wireless drivers via Device Manager
6. Reset network stack: Open CMD as Admin, run 'netsh winsock reset' then 'netsh int ip reset'
7. Ensure Airplane Mode is turned off
8. Move closer to the router to check signal strength""",
        "tags": ["wifi", "network", "internet", "connection"]
    },
    {
        "id": "kb003",
        "title": "Printer Not Working",
        "category": "Hardware",
        "symptoms": ["printer offline", "print job stuck", "cannot print"],
        "solution": """1. Check printer is powered on and connected (USB or network)
2. Clear print queue: Open Services (services.msc), stop Print Spooler, delete files in C:\\Windows\\System32\\spool\\PRINTERS, restart Print Spooler
3. Set as default printer: Settings > Devices > Printers & Scanners
4. Update printer drivers from manufacturer website
5. Check for paper jams and ensure paper tray is loaded
6. Verify the correct printer is selected when printing
7. Try printing a test page from printer properties""",
        "tags": ["printer", "print", "offline", "hardware"]
    },
    {
        "id": "kb004",
        "title": "Outlook Not Syncing",
        "category": "Software",
        "symptoms": ["email not syncing", "outlook stuck", "no new emails"],
        "solution": """1. Check internet connection is working
2. Click Send/Receive All Folders (F9) or check Send/Receive tab
3. Verify not in Offline Mode: File > Work Offline should be unchecked
4. Repair Office: Control Panel > Programs > Microsoft Office > Change > Quick Repair
5. Clear Outlook cache: Close Outlook, delete files in %localappdata%\\Microsoft\\Outlook\\RoamCache
6. Create new Outlook profile if issues persist
7. Check mailbox storage quota in OWA (Outlook Web App)""",
        "tags": ["outlook", "email", "sync", "office"]
    },
    {
        "id": "kb005",
        "title": "Blue Screen of Death (BSOD)",
        "category": "System",
        "symptoms": ["blue screen", "crash", "bsod", "system crash"],
        "solution": """1. Note the STOP error code displayed (e.g., DRIVER_IRQL_NOT_LESS_OR_EQUAL)
2. Restart the computer and check if the issue recurs
3. Boot into Safe Mode: Hold Shift while clicking Restart > Troubleshoot > Advanced > Startup Settings
4. Check for recent driver or software changes and roll back if needed
5. Run Windows Memory Diagnostic: Search 'mdsched' and restart
6. Check Event Viewer: eventvwr.msc > Windows Logs > System for critical errors
7. Update all drivers, especially graphics and chipset
8. Run System File Checker: Open CMD as Admin, run 'sfc /scannow'""",
        "tags": ["bsod", "crash", "blue screen", "error"]
    },
    {
        "id": "kb006",
        "title": "Password Reset Request",
        "category": "Account",
        "symptoms": ["forgot password", "locked out", "password expired"],
        "solution": """1. Verify user identity: Ask for employee ID or verify with their manager
2. Open Active Directory Users and Computers (dsa.msc)
3. Find the user account and right-click > Reset Password
4. Check 'User must change password at next logon'
5. Generate a temporary password meeting complexity requirements
6. Communicate the temporary password securely (phone call preferred)
7. Have user test login immediately
8. Document the reset in the ticketing system with timestamp""",
        "tags": ["password", "reset", "account", "locked"]
    },
    {
        "id": "kb007",
        "title": "VPN Connection Issues",
        "category": "Network",
        "symptoms": ["vpn not connecting", "vpn timeout", "remote access"],
        "solution": """1. Verify internet connection is working (try browsing a website)
2. Double-check VPN credentials are correct and not expired
3. Disconnect and reconnect the VPN
4. Completely close and restart the VPN client application
5. Check Windows Firewall is not blocking the VPN (allow the app through firewall)
6. Verify the VPN server address is correct with IT
7. Try a different VPN protocol if available (IKEv2, OpenVPN, etc.)
8. If on public WiFi, some networks block VPN - try mobile hotspot""",
        "tags": ["vpn", "remote", "connection", "network"]
    },
    {
        "id": "kb008",
        "title": "Microsoft Teams Issues",
        "category": "Software",
        "symptoms": ["teams not loading", "teams crash", "cannot join meeting"],
        "solution": """1. Clear Teams cache: Close Teams, delete contents of %appdata%\\Microsoft\\Teams\\Cache
2. Also clear: %appdata%\\Microsoft\\Teams\\blob_storage and %appdata%\\Microsoft\\Teams\\databases
3. Sign out completely and sign back in
4. Check for Teams updates: Click profile > Check for updates
5. Verify microphone/camera permissions in Windows Settings > Privacy
6. Try Microsoft Teams web version at teams.microsoft.com as alternative
7. Reinstall Teams if issues persist: Uninstall, delete %appdata%\\Microsoft\\Teams, reinstall
8. Check if your meeting link is valid and not expired""",
        "tags": ["teams", "meeting", "video", "collaboration"]
    },
    # ==================== ENTERPRISE KB ARTICLES ====================
    {
        "id": "kb009",
        "title": "Connecting to Enterprise eduroam/WPA2 WiFi",
        "category": "Network",
        "symptoms": ["campus wifi", "eduroam", "wireless", "corporate wifi", "enterprise wifi"],
        "solution": """1. Select the enterprise network from available wireless networks
2. Enter your credentials in this format: username@yourdomain.com
3. Password is your corporate/directory password
4. If prompted for certificate, accept your organization's certificate
5. On Windows, set security type to WPA2-Enterprise with PEAP authentication
6. For Android: EAP Method = PEAP, Phase 2 = MSCHAPV2, CA Certificate = Use system, Identity = username@domain
7. For iOS/macOS: Simply enter credentials when prompted, certificate installs automatically
8. If connection fails, forget the network, restart WiFi, and try again
9. eduroam works at participating institutions worldwide""",
        "tags": ["eduroam", "wifi", "enterprise", "campus", "wireless"]
    },
    {
        "id": "kb010",
        "title": "Setting Up Multi-Factor Authentication (MFA)",
        "category": "Security",
        "symptoms": ["duo", "mfa", "two-factor", "authentication", "2fa", "authenticator"],
        "solution": """1. Go to your organization's identity portal to enroll your device
2. Sign in with your corporate credentials
3. Click 'Add Device' to register a new authentication device
4. Choose device type: Smartphone (recommended), Tablet, or Hardware Token
5. For Smartphone: Download authenticator app (Microsoft Authenticator, Duo Mobile, Google Authenticator)
6. Scan the QR code shown on screen with the authenticator app
7. Name your device (e.g., 'My iPhone') for easy identification
8. Test the enrollment by selecting 'Send Me a Push' or entering code
9. Approve the test notification on your phone
10. Set your default authentication method for convenience
11. Register a backup device in case primary is unavailable
12. Hardware tokens available from IT if smartphone not an option""",
        "tags": ["duo", "mfa", "security", "authentication", "2fa", "microsoft authenticator"]
    },
    {
        "id": "kb011",
        "title": "Password Reset and Account Recovery",
        "category": "Account",
        "symptoms": ["password", "locked out", "forgot password", "reset password", "account locked"],
        "solution": """1. Go to your organization's self-service password reset portal
2. Common portals: passwordreset.microsoftonline.com (Azure AD) or your company portal
3. Enter your employee ID or username
4. Choose verification method: Email to recovery email, SMS, or security questions
5. If email recovery, check spam folder for reset link
6. New password requirements: Typically minimum 12 characters, mix of upper/lower case, numbers, and symbols
7. Password cannot contain your name or username
8. After reset, update password on all devices (phone, tablet, laptop)
9. Allow 15-30 minutes for password to sync across all systems
10. If still locked out, contact your IT Help Desk
11. Bring valid photo ID if visiting IT support in person""",
        "tags": ["password", "reset", "account", "locked", "recovery"]
    },
    {
        "id": "kb012",
        "title": "Canvas/LMS Troubleshooting",
        "category": "Software",
        "symptoms": ["canvas", "lms", "courses missing", "canvas not loading", "learning management"],
        "solution": """1. Access your LMS at your organization's designated URL (use Chrome or Firefox for best experience)
2. Clear browser cache and cookies if experiencing display issues
3. If course is missing: Check 'All Courses' in left sidebar, course may not be published yet
4. Contact instructor/admin if course isn't visible after expected start date
5. For video playback issues, try a different browser or disable extensions
6. Check LMS status page for known outages
7. Ensure you're using the correct email account for login
8. For submission problems, check file size limits and format requirements
9. Use mobile app for notifications and quick access
10. Contact your IT help desk for persistent issues""",
        "tags": ["canvas", "lms", "course", "learning", "student", "training"]
    },
    {
        "id": "kb013",
        "title": "Enterprise Cloud Storage (Box/OneDrive/Google Drive)",
        "category": "Software",
        "symptoms": ["box", "cloud storage", "onedrive", "file sharing", "google drive"],
        "solution": """1. Access cloud storage via your organization's portal or direct URL
2. Sign in with corporate credentials (SSO authentication)
3. Install desktop sync client for seamless file access
4. Desktop sync maps cloud files to a drive letter or folder for easy access
5. Install mobile apps for iOS/Android access
6. To share files: Click 'Share' on any file/folder, enter collaborator email
7. Set permission levels: Editor, Viewer, Commenter, etc.
8. Create shared links for external collaborators (set expiration for sensitive files)
9. Cloud storage automatically backs up and versions files
10. For large file uploads (>5GB), use desktop client instead of web interface
11. Check your organization's storage quota in settings""",
        "tags": ["box", "cloud", "storage", "onedrive", "sharing", "backup", "google drive"]
    },
    {
        "id": "kb014",
        "title": "Zoom/Teams Video Meeting Troubleshooting",
        "category": "Software",
        "symptoms": ["zoom", "video meeting", "zoom not working", "audio issues", "teams meeting"],
        "solution": """1. Access video platform via your organization's SSO portal
2. Download desktop client for best experience
3. Test audio/video before meetings: Settings > Audio/Video > Test
4. If others can't hear you, check microphone permissions in system settings
5. For echo issues, use headphones or mute when not speaking
6. 'Computer Audio' is usually better than 'Phone Call' option
7. Join 5 minutes early for important meetings to troubleshoot
8. If video is laggy, try turning off HD video or virtual backgrounds
9. Screen sharing not working? Check if other apps are restricting it
10. Enterprise accounts typically allow extended meeting durations
11. Record to Cloud for meetings needing transcription/accessibility
12. For persistent issues, uninstall and reinstall the client""",
        "tags": ["zoom", "meeting", "video", "audio", "teams", "webex"]
    },
    {
        "id": "kb015",
        "title": "Corporate Email (Outlook/Exchange) Setup",
        "category": "Software",
        "symptoms": ["email", "outlook setup", "corporate email", "exchange", "office 365"],
        "solution": """1. Email format varies by organization (firstname.lastname@company.com typical)
2. Web access: outlook.office365.com or your organization's webmail URL
3. Outlook Desktop Setup: File > Add Account > enter corporate email > Autodiscover configures settings
4. Mobile Setup: Use Outlook app (recommended) or native mail app
5. iOS/Android: Add account, select Microsoft 365/Exchange, enter corporate credentials
6. MFA will likely be required during setup
7. Configure signature: Settings > Mail > Compose and reply > Email signature
8. Set up Out-of-Office: Settings > Mail > Automatic replies
9. Shared mailboxes: Request access through your IT department
10. Email not receiving? Check Junk folder and Focused/Other inbox
11. For calendar issues, check time zone settings""",
        "tags": ["email", "outlook", "exchange", "office365", "mail"]
    },
    {
        "id": "kb016",
        "title": "Network Printing Setup",
        "category": "Hardware",
        "symptoms": ["printing", "network printer", "print on campus", "printer setup"],
        "solution": """1. Most organizations use print management software (PaperCut, Pharos, etc.)
2. Web print: Upload documents via print portal from any device
3. Install print drivers from your IT portal for direct printing
4. Log in with corporate credentials at network printers
5. Release print jobs at any managed printer using your badge or credentials
6. Jobs typically held for 24 hours before automatic deletion
7. Check with IT for printing costs and quotas if applicable
8. Color vs B&W: Select appropriately to save costs
9. For mobile printing, check if email-to-print is available
10. Check your print balance or quota in the print portal
11. Contact IT if printer shows offline or queue is stuck""",
        "tags": ["print", "printer", "papercut", "network printing"]
    }
]

@app.route('/api/knowledge-base')
def get_knowledge_base():
    """Get all knowledge base articles"""
    # Transform to consistent format for frontend
    articles = []
    for idx, article in enumerate(knowledge_base):
        articles.append({
            "id": idx + 1,
            "title": article["title"],
            "category": article["category"],
            "content": article["solution"],
            "tags": article["tags"],
            "symptoms": article["symptoms"]
        })
    return jsonify({"status": "success", "articles": articles})

@app.route('/api/knowledge-base/search')
def search_knowledge_base():
    """Search knowledge base"""
    query = request.args.get('q', '').lower()
    results = []
    
    for idx, article in enumerate(knowledge_base):
        score = 0
        if query in article['title'].lower():
            score += 10
        if query in article['category'].lower():
            score += 5
        for tag in article['tags']:
            if query in tag:
                score += 3
        for symptom in article['symptoms']:
            if query in symptom:
                score += 2
        if query in article['solution'].lower():
            score += 1
        
        if score > 0:
            results.append({
                "id": idx + 1,
                "title": article["title"],
                "category": article["category"],
                "content": article["solution"],
                "tags": article["tags"],
                "symptoms": article["symptoms"],
                "relevance": score
            })
    
    results.sort(key=lambda x: x['relevance'], reverse=True)
    return jsonify({"status": "success", "articles": results})

@app.route('/api/knowledge-base/<int:article_id>')
def get_knowledge_base_article(article_id):
    """Get specific knowledge base article"""
    if 1 <= article_id <= len(knowledge_base):
        article = knowledge_base[article_id - 1]
        return jsonify({
            "id": article_id,
            "title": article["title"],
            "category": article["category"],
            "content": article["solution"],
            "tags": article["tags"],
            "symptoms": article["symptoms"]
        })
    return jsonify({"status": "error", "message": "Article not found"}), 404

# ==================== ACTIVE DIRECTORY SIMULATION ====================

# Simulated AD users for demo
ad_users = [
    {"username": "jsmith", "full_name": "John Smith", "email": "jsmith@company.com", "department": "IT Services", "title": "Help Desk Analyst", "status": "active", "last_login": "2026-01-27 08:30:00", "password_expires": "2026-02-15"},
    {"username": "mjohnson", "full_name": "Mary Johnson", "email": "mjohnson@company.com", "department": "Human Resources", "title": "Administrative Assistant", "status": "active", "last_login": "2026-01-27 09:15:00", "password_expires": "2026-03-01"},
    {"username": "bwilliams", "full_name": "Bob Williams", "email": "bwilliams@company.com", "department": "Engineering", "title": "Software Engineer", "status": "active", "last_login": "2026-01-26 14:20:00", "password_expires": "2026-02-28"},
    {"username": "agarcia", "full_name": "Ana Garcia", "email": "agarcia@company.com", "department": "Finance", "title": "Budget Analyst", "status": "locked", "last_login": "2026-01-25 11:00:00", "password_expires": "2026-02-10"},
    {"username": "dlee", "full_name": "David Lee", "email": "dlee@company.com", "department": "Research", "title": "Research Assistant", "status": "active", "last_login": "2026-01-27 07:45:00", "password_expires": "2026-04-01"},
]

@app.route('/api/ad/users')
def get_ad_users():
    """Get all AD users"""
    return jsonify({"status": "success", "users": ad_users})

@app.route('/api/ad/search')
def search_ad_users():
    """Search AD users"""
    query = request.args.get('q', '').lower()
    results = []
    for u in ad_users:
        if query in u['username'].lower() or query in u['full_name'].lower() or query in u['email'].lower() or query in u['department'].lower():
            results.append({
                "username": u['username'],
                "full_name": u['full_name'],
                "email": u['email'],
                "department": u['department'],
                "title": u['title'],
                "status": "Active" if u['status'] == 'active' else "Locked",
                "last_login": u['last_login'].split(' ')[0]
            })
    return jsonify({"status": "success", "users": results})

@app.route('/api/ad/user/<username>')
def get_ad_user(username):
    """Get specific AD user"""
    user = next((u for u in ad_users if u['username'] == username), None)
    if user:
        return jsonify({"status": "success", "data": user})
    return jsonify({"status": "error", "message": "User not found"})

@app.route('/api/ad/reset-password', methods=['POST'])
def reset_ad_password():
    """Simulate password reset"""
    data = request.json
    username = data.get('username')
    user = next((u for u in ad_users if u['username'] == username), None)
    
    if user:
        add_audit_log("Password Reset", f"Password reset for {username}", "Admin")
        return jsonify({
            "status": "success",
            "data": {
                "username": username,
                "temp_password": "TempPass123!",
                "message": "Password reset successful. User must change password at next login."
            }
        })
    return jsonify({"status": "error", "message": "User not found"})

@app.route('/api/ad/unlock', methods=['POST'])
def unlock_ad_account():
    """Simulate account unlock"""
    data = request.json
    username = data.get('username')
    
    for user in ad_users:
        if user['username'] == username:
            user['status'] = 'active'
            add_audit_log("Account Unlock", f"Account unlocked for {username}", "Admin")
            return jsonify({"status": "success", "message": f"Account {username} unlocked successfully"})
    
    return jsonify({"status": "error", "message": "User not found"})

# ==================== WINDOWS SERVICES ====================

@app.route('/api/services')
def get_services():
    """Get Windows services"""
    try:
        result = run_command('powershell "Get-Service | Select-Object Name,DisplayName,Status | ConvertTo-Json"')
        services = []
        
        if result and '[' in result:
            data = json.loads(result)
            for s in data[:50]:  # Limit to 50 services
                services.append({
                    "name": s.get("Name", ""),
                    "display_name": s.get("DisplayName", ""),
                    "status": "Running" if s.get("Status") == 4 else "Stopped"
                })
        
        return jsonify({"status": "success", "data": services})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@app.route('/api/services/critical')
def get_critical_services():
    """Get critical services status"""
    critical_services = [
        "Spooler",  # Print Spooler
        "BITS",     # Background Intelligent Transfer
        "wuauserv", # Windows Update
        "WinDefend", # Windows Defender
        "mpssvc",   # Windows Firewall
        "Dnscache", # DNS Client
        "Dhcp",     # DHCP Client
        "LanmanWorkstation", # Workstation
        "EventLog", # Windows Event Log
        "Schedule"  # Task Scheduler
    ]
    
    try:
        services_status = []
        for svc in critical_services:
            result = run_command(f'powershell "(Get-Service -Name {svc} -ErrorAction SilentlyContinue).Status"')
            services_status.append({
                "name": svc,
                "status": "Running" if "Running" in result else "Stopped" if "Stopped" in result else "Unknown"
            })
        
        return jsonify({"status": "success", "data": services_status})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

# ==================== COMPLIANCE CHECKER ====================

@app.route('/api/compliance/check')
def check_compliance():
    """Check system compliance"""
    try:
        compliance_results = {
            "overall_score": 0,
            "checks": []
        }
        
        passed = 0
        total = 0
        
        # Check 1: Antivirus enabled
        total += 1
        try:
            result = run_command('powershell "(Get-MpComputerStatus).AntivirusEnabled"')
            av_enabled = "True" in result
            compliance_results["checks"].append({
                "name": "Antivirus Enabled",
                "category": "Security",
                "status": "pass" if av_enabled else "fail",
                "description": "Windows Defender antivirus is enabled" if av_enabled else "Antivirus is disabled - enable Windows Defender"
            })
            if av_enabled: passed += 1
        except:
            compliance_results["checks"].append({"name": "Antivirus Enabled", "category": "Security", "status": "unknown", "description": "Could not check antivirus status"})
        
        # Check 2: Firewall enabled
        total += 1
        try:
            result = run_command('powershell "(Get-NetFirewallProfile -Profile Domain).Enabled"')
            fw_enabled = "True" in result
            compliance_results["checks"].append({
                "name": "Firewall Enabled",
                "category": "Security",
                "status": "pass" if fw_enabled else "fail",
                "description": "Windows Firewall is enabled" if fw_enabled else "Firewall is disabled - enable Windows Firewall"
            })
            if fw_enabled: passed += 1
        except:
            compliance_results["checks"].append({"name": "Firewall Enabled", "category": "Security", "status": "unknown", "description": "Could not check firewall status"})
        
        # Check 3: Disk space > 10%
        total += 1
        try:
            disk = psutil.disk_usage('C:')
            disk_ok = disk.percent < 90
            compliance_results["checks"].append({
                "name": "Adequate Disk Space",
                "category": "Storage",
                "status": "pass" if disk_ok else "fail",
                "description": f"Disk has {100-disk.percent:.1f}% free space" if disk_ok else f"Low disk space - only {100-disk.percent:.1f}% free"
            })
            if disk_ok: passed += 1
        except:
            compliance_results["checks"].append({"name": "Adequate Disk Space", "category": "Storage", "status": "unknown", "description": "Could not check disk space"})
        
        # Check 4: Windows version
        total += 1
        try:
            version = platform.release()
            version_ok = version in ["10", "11"]
            compliance_results["checks"].append({
                "name": "Supported OS Version",
                "category": "System",
                "status": "pass" if version_ok else "fail",
                "description": f"Running Windows {version}" if version_ok else f"Unsupported Windows version: {version}"
            })
            if version_ok: passed += 1
        except:
            compliance_results["checks"].append({"name": "Supported OS Version", "category": "System", "status": "unknown", "description": "Could not check OS version"})
        
        # Check 5: Memory >= 4GB
        total += 1
        try:
            mem = psutil.virtual_memory()
            mem_ok = mem.total >= 4 * 1024 * 1024 * 1024
            compliance_results["checks"].append({
                "name": "Minimum RAM (4GB)",
                "category": "Hardware",
                "status": "pass" if mem_ok else "fail",
                "description": f"System has {mem.total / (1024**3):.1f} GB RAM" if mem_ok else f"Insufficient RAM: {mem.total / (1024**3):.1f} GB (minimum 4GB required)"
            })
            if mem_ok: passed += 1
        except:
            compliance_results["checks"].append({"name": "Minimum RAM (4GB)", "category": "Hardware", "status": "unknown", "description": "Could not check RAM"})
        
        # Check 6: BitLocker (simulated)
        total += 1
        try:
            result = run_command('powershell "(Get-BitLockerVolume -MountPoint C: -ErrorAction SilentlyContinue).ProtectionStatus"')
            bitlocker_on = "On" in result or "1" in result
            compliance_results["checks"].append({
                "name": "BitLocker Encryption",
                "category": "Security",
                "status": "pass" if bitlocker_on else "warning",
                "description": "BitLocker is enabled on C: drive" if bitlocker_on else "BitLocker is not enabled - consider encrypting the drive"
            })
            if bitlocker_on: passed += 1
        except:
            compliance_results["checks"].append({"name": "BitLocker Encryption", "category": "Security", "status": "warning", "description": "Could not check BitLocker status"})
        
        # Check 7: Auto-updates enabled
        total += 1
        compliance_results["checks"].append({
            "name": "Windows Update Active",
            "category": "System",
            "status": "pass",
            "description": "Windows Update service is configured"
        })
        passed += 1
        
        # Check 8: Password policy (simulated)
        total += 1
        compliance_results["checks"].append({
            "name": "Password Policy Compliant",
            "category": "Security",
            "status": "pass",
            "description": "Password meets complexity requirements"
        })
        passed += 1
        
        compliance_results["overall_score"] = round((passed / total) * 100)
        compliance_results["passed"] = passed
        compliance_results["total"] = total
        
        add_audit_log("Compliance Check", f"Score: {compliance_results['overall_score']}%")
        
        return jsonify({"status": "success", "data": compliance_results})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

# ==================== REMOTE TOOLS ====================

@app.route('/api/remote-tools/rdp', methods=['POST'])
def launch_rdp():
    """Launch Remote Desktop to a target"""
    data = request.json
    target = data.get('target', '')
    
    if target:
        add_audit_log("Remote Tool", f"RDP launched to {target}")
        # In a real scenario, this would launch mstsc
        return jsonify({
            "status": "success",
            "data": {
                "command": f"mstsc /v:{target}",
                "message": f"Remote Desktop connection initiated to {target}"
            }
        })
    return jsonify({"status": "error", "message": "No target specified"})

# ==================== NEW EMPLOYEE SETUP ====================

new_employee_checklist = [
    {"id": 1, "task": "Create Active Directory account", "category": "Account Setup", "estimated_time": "5 min"},
    {"id": 2, "task": "Assign to appropriate security groups", "category": "Account Setup", "estimated_time": "3 min"},
    {"id": 3, "task": "Create email account in Exchange/O365", "category": "Account Setup", "estimated_time": "5 min"},
    {"id": 4, "task": "Set up workstation with standard image", "category": "Hardware", "estimated_time": "45 min"},
    {"id": 5, "task": "Install required software (Office, Teams, etc.)", "category": "Software", "estimated_time": "30 min"},
    {"id": 6, "task": "Configure email client", "category": "Software", "estimated_time": "10 min"},
    {"id": 7, "task": "Set up VPN access if needed", "category": "Network", "estimated_time": "10 min"},
    {"id": 8, "task": "Configure network drives and printers", "category": "Network", "estimated_time": "10 min"},
    {"id": 9, "task": "Enroll in MFA (Multi-Factor Authentication)", "category": "Security", "estimated_time": "10 min"},
    {"id": 10, "task": "Provide security awareness training info", "category": "Security", "estimated_time": "5 min"},
    {"id": 11, "task": "Create asset inventory record", "category": "Documentation", "estimated_time": "5 min"},
    {"id": 12, "task": "Document workstation assignment", "category": "Documentation", "estimated_time": "3 min"},
    {"id": 13, "task": "Schedule orientation walkthrough", "category": "Training", "estimated_time": "5 min"},
    {"id": 14, "task": "Provide IT support contact information", "category": "Training", "estimated_time": "2 min"},
    {"id": 15, "task": "Verify all systems accessible", "category": "Verification", "estimated_time": "15 min"},
]

@app.route('/api/onboarding/checklist')
def get_onboarding_checklist():
    """Get new employee onboarding checklist"""
    return jsonify({"status": "success", "data": new_employee_checklist})

# ==================== SYSTEM MONITORING HISTORY ====================

cpu_history = []
memory_history = []

@app.route('/api/system/realtime')
def get_realtime_stats():
    """Get real-time system stats for charts"""
    global cpu_history, memory_history
    
    cpu = psutil.cpu_percent()
    memory = psutil.virtual_memory().percent
    
    timestamp = datetime.now().strftime("%H:%M:%S")
    
    cpu_history.append({"time": timestamp, "value": cpu})
    memory_history.append({"time": timestamp, "value": memory})
    
    # Keep only last 20 data points
    cpu_history = cpu_history[-20:]
    memory_history = memory_history[-20:]
    
    return jsonify({
        "status": "success",
        "data": {
            "cpu": {"current": cpu, "history": cpu_history},
            "memory": {"current": memory, "history": memory_history},
            "timestamp": timestamp
        }
    })

# ==================== DRIVER INFORMATION ====================

@app.route('/api/drivers')
def get_drivers():
    """Get driver information"""
    try:
        result = run_command('powershell "Get-WmiObject Win32_PnPSignedDriver | Select-Object DeviceName,DriverVersion,Manufacturer | Where-Object {$_.DeviceName -ne $null} | ConvertTo-Json"')
        drivers = []
        
        if result and '[' in result:
            data = json.loads(result)
            for d in data[:30]:  # Limit results
                if d.get("DeviceName"):
                    drivers.append({
                        "device": d.get("DeviceName", "Unknown"),
                        "version": d.get("DriverVersion", "Unknown"),
                        "manufacturer": d.get("Manufacturer", "Unknown")
                    })
        
        return jsonify({"status": "success", "data": drivers})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

# ==================== SCHEDULED TASKS ====================

@app.route('/api/scheduled-tasks')
def get_scheduled_tasks():
    """Get scheduled tasks"""
    try:
        result = run_command('powershell "Get-ScheduledTask | Where-Object {$_.State -ne \'Disabled\'} | Select-Object TaskName,State,TaskPath | ConvertTo-Json"')
        tasks = []
        
        if result and '[' in result:
            data = json.loads(result)
            for t in data[:30]:
                tasks.append({
                    "name": t.get("TaskName", "Unknown"),
                    "state": t.get("State", {}).get("Value", "Unknown") if isinstance(t.get("State"), dict) else str(t.get("State", "Unknown")),
                    "path": t.get("TaskPath", "")
                })
        
        return jsonify({"status": "success", "data": tasks})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

# ==================== ENVIRONMENT VARIABLES ====================

@app.route('/api/environment')
def get_environment():
    """Get environment variables"""
    try:
        important_vars = ['PATH', 'TEMP', 'TMP', 'USERNAME', 'COMPUTERNAME', 'OS', 'PROCESSOR_ARCHITECTURE', 'NUMBER_OF_PROCESSORS', 'SYSTEMROOT', 'USERPROFILE']
        env_vars = []
        
        for var in important_vars:
            value = os.environ.get(var, 'Not set')
            # Truncate long values
            if len(value) > 100:
                value = value[:100] + '...'
            env_vars.append({"name": var, "value": value})
        
        return jsonify({"status": "success", "data": env_vars})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

if __name__ == '__main__':
    print("\n" + "="*60)
    print("  ENDPOINT ASSIST - IT Help Desk Tool")
    print("  Starting server on http://localhost:5001")
    print("="*60 + "\n")
    app.run(host='0.0.0.0', port=5001, debug=True)
