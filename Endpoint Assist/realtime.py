"""
Endpoint Assist - WebSocket Real-time Updates
Provides live system monitoring via WebSocket connections
"""

from flask_socketio import SocketIO, emit, join_room, leave_room
from flask import request
import psutil
import threading
import time
from datetime import datetime

# SocketIO instance - will be initialized in app.py
socketio = None

def init_socketio(app):
    """Initialize SocketIO with Flask app"""
    global socketio
    socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')
    register_handlers()
    return socketio

def register_handlers():
    """Register WebSocket event handlers"""
    
    @socketio.on('connect')
    def handle_connect():
        """Handle client connection"""
        print(f"🔌 Client connected: {request.sid}")
        emit('connected', {'message': 'Connected to Endpoint Assist', 'sid': request.sid})
    
    @socketio.on('disconnect')
    def handle_disconnect():
        """Handle client disconnection"""
        print(f"🔌 Client disconnected: {request.sid}")
    
    @socketio.on('subscribe')
    def handle_subscribe(data):
        """Subscribe to a monitoring channel"""
        channel = data.get('channel', 'system')
        join_room(channel)
        emit('subscribed', {'channel': channel, 'message': f'Subscribed to {channel} updates'})
        print(f"📡 Client {request.sid} subscribed to {channel}")
    
    @socketio.on('unsubscribe')
    def handle_unsubscribe(data):
        """Unsubscribe from a monitoring channel"""
        channel = data.get('channel', 'system')
        leave_room(channel)
        emit('unsubscribed', {'channel': channel})
    
    @socketio.on('request_update')
    def handle_request_update(data):
        """Handle manual update request"""
        channel = data.get('channel', 'system')
        if channel == 'system':
            emit('system_update', get_system_stats())
        elif channel == 'network':
            emit('network_update', get_network_stats())
        elif channel == 'processes':
            emit('process_update', get_process_stats())

# ==================== DATA GATHERING ====================

def get_system_stats():
    """Get current system statistics"""
    try:
        cpu_percent = psutil.cpu_percent(interval=0.1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        # Get CPU per-core usage
        per_cpu = psutil.cpu_percent(interval=0.1, percpu=True)
        
        return {
            'timestamp': datetime.now().isoformat(),
            'cpu': {
                'percent': cpu_percent,
                'per_core': per_cpu,
                'count': psutil.cpu_count()
            },
            'memory': {
                'percent': memory.percent,
                'used_gb': round(memory.used / (1024**3), 2),
                'total_gb': round(memory.total / (1024**3), 2),
                'available_gb': round(memory.available / (1024**3), 2)
            },
            'disk': {
                'percent': disk.percent,
                'used_gb': round(disk.used / (1024**3), 2),
                'total_gb': round(disk.total / (1024**3), 2),
                'free_gb': round(disk.free / (1024**3), 2)
            }
        }
    except Exception as e:
        return {'error': str(e)}

def get_network_stats():
    """Get current network statistics"""
    try:
        net_io = psutil.net_io_counters()
        return {
            'timestamp': datetime.now().isoformat(),
            'bytes_sent': net_io.bytes_sent,
            'bytes_recv': net_io.bytes_recv,
            'packets_sent': net_io.packets_sent,
            'packets_recv': net_io.packets_recv,
            'bytes_sent_mb': round(net_io.bytes_sent / (1024**2), 2),
            'bytes_recv_mb': round(net_io.bytes_recv / (1024**2), 2)
        }
    except Exception as e:
        return {'error': str(e)}

def get_process_stats():
    """Get top processes by CPU usage"""
    try:
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
            try:
                pinfo = proc.info
                if pinfo['cpu_percent'] is not None and pinfo['cpu_percent'] > 0:
                    processes.append({
                        'pid': pinfo['pid'],
                        'name': pinfo['name'],
                        'cpu_percent': round(pinfo['cpu_percent'], 1),
                        'memory_percent': round(pinfo['memory_percent'], 1) if pinfo['memory_percent'] else 0
                    })
            except:
                pass
        
        # Sort by CPU usage and take top 10
        processes.sort(key=lambda x: x['cpu_percent'], reverse=True)
        return {
            'timestamp': datetime.now().isoformat(),
            'processes': processes[:10]
        }
    except Exception as e:
        return {'error': str(e)}

# ==================== BACKGROUND MONITORING ====================

class SystemMonitor:
    """Background system monitor that broadcasts updates"""
    
    def __init__(self, interval=2):
        self.interval = interval
        self.running = False
        self.thread = None
    
    def start(self):
        """Start the background monitoring"""
        if self.running:
            return
        self.running = True
        self.thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.thread.start()
        print("📊 System monitor started")
    
    def stop(self):
        """Stop the background monitoring"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=5)
        print("📊 System monitor stopped")
    
    def _monitor_loop(self):
        """Main monitoring loop"""
        while self.running:
            try:
                if socketio:
                    # Broadcast system stats to subscribed clients
                    socketio.emit('system_update', get_system_stats(), room='system')
                    socketio.emit('network_update', get_network_stats(), room='network')
            except Exception as e:
                print(f"Monitor error: {e}")
            
            time.sleep(self.interval)

# Global monitor instance
system_monitor = SystemMonitor(interval=2)

def start_monitoring():
    """Start the background system monitor"""
    system_monitor.start()

def stop_monitoring():
    """Stop the background system monitor"""
    system_monitor.stop()

# ==================== ALERT SYSTEM ====================

class AlertManager:
    """Manages system alerts and notifications"""
    
    def __init__(self):
        self.thresholds = {
            'cpu': 80,
            'memory': 85,
            'disk': 90
        }
        self.alert_cooldown = {}  # Prevent alert spam
        self.cooldown_seconds = 60
    
    def check_alerts(self, stats):
        """Check for threshold violations and emit alerts"""
        alerts = []
        current_time = time.time()
        
        # CPU Alert
        if stats.get('cpu', {}).get('percent', 0) > self.thresholds['cpu']:
            if self._can_alert('cpu', current_time):
                alerts.append({
                    'type': 'cpu',
                    'level': 'warning',
                    'message': f"High CPU usage: {stats['cpu']['percent']}%",
                    'value': stats['cpu']['percent'],
                    'threshold': self.thresholds['cpu']
                })
        
        # Memory Alert
        if stats.get('memory', {}).get('percent', 0) > self.thresholds['memory']:
            if self._can_alert('memory', current_time):
                alerts.append({
                    'type': 'memory',
                    'level': 'warning',
                    'message': f"High memory usage: {stats['memory']['percent']}%",
                    'value': stats['memory']['percent'],
                    'threshold': self.thresholds['memory']
                })
        
        # Disk Alert
        if stats.get('disk', {}).get('percent', 0) > self.thresholds['disk']:
            if self._can_alert('disk', current_time):
                alerts.append({
                    'type': 'disk',
                    'level': 'critical',
                    'message': f"Critical disk usage: {stats['disk']['percent']}%",
                    'value': stats['disk']['percent'],
                    'threshold': self.thresholds['disk']
                })
        
        # Emit alerts
        for alert in alerts:
            if socketio:
                socketio.emit('alert', alert, room='alerts')
        
        return alerts
    
    def _can_alert(self, alert_type, current_time):
        """Check if we can send an alert (cooldown check)"""
        last_alert = self.alert_cooldown.get(alert_type, 0)
        if current_time - last_alert > self.cooldown_seconds:
            self.alert_cooldown[alert_type] = current_time
            return True
        return False
    
    def set_threshold(self, alert_type, value):
        """Set a threshold value"""
        if alert_type in self.thresholds:
            self.thresholds[alert_type] = value

# Global alert manager
alert_manager = AlertManager()
