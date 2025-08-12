from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json
import os
from dotenv import load_dotenv
import pymysql
from urllib.parse import quote_plus

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Remote MySQL Database Configuration ONLY
DB_HOST = os.getenv('DB_HOST', '61.19.114.86')
DB_PORT = os.getenv('DB_PORT', '54000')
DB_USER = os.getenv('DB_USER', 'nathee')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'Root@1234')
DB_NAME = os.getenv('DB_NAME', 'iot_data')

# Properly escape the password in the connection string
escaped_password = quote_plus(DB_PASSWORD)

# Configure Flask app to use ONLY remote MySQL database
app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{DB_USER}:{escaped_password}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-key-change-in-production')

db = SQLAlchemy(app)

# Database Models
class Device(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    device_id = db.Column(db.String(50), unique=True, nullable=False)
    device_name = db.Column(db.String(100), nullable=False)
    device_type = db.Column(db.String(50), nullable=False)
    location = db.Column(db.String(100))
    description = db.Column(db.Text)
    wifi_ssid = db.Column(db.String(100))
    wifi_security = db.Column(db.String(50))
    static_ip = db.Column(db.String(15))
    update_interval = db.Column(db.Integer, default=10)
    has_temperature = db.Column(db.Boolean, default=False)
    has_humidity = db.Column(db.Boolean, default=False)
    has_pressure = db.Column(db.Boolean, default=False)
    has_light = db.Column(db.Boolean, default=False)
    has_motion = db.Column(db.Boolean, default=False)
    has_distance = db.Column(db.Boolean, default=False)
    is_online = db.Column(db.Boolean, default=False)
    last_seen = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'device_id': self.device_id,
            'device_name': self.device_name,
            'device_type': self.device_type,
            'location': self.location,
            'description': self.description,
            'wifi_ssid': self.wifi_ssid,
            'wifi_security': self.wifi_security,
            'static_ip': self.static_ip,
            'update_interval': self.update_interval,
            'has_temperature': self.has_temperature,
            'has_humidity': self.has_humidity,
            'has_pressure': self.has_pressure,
            'has_light': self.has_light,
            'has_motion': self.has_motion,
            'has_distance': self.has_distance,
            'is_online': self.is_online,
            'last_seen': self.last_seen.isoformat() if self.last_seen else None,
            'created_at': self.created_at.isoformat()
        }

class SensorData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    device_id = db.Column(db.String(50), nullable=False)
    temperature = db.Column(db.Float)
    humidity = db.Column(db.Float)
    pressure = db.Column(db.Float)
    light = db.Column(db.Float)
    motion = db.Column(db.Boolean)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'device_id': self.device_id,
            'temperature': self.temperature,
            'humidity': self.humidity,
            'pressure': self.pressure,
            'light': self.light,
            'motion': self.motion,
            'timestamp': self.timestamp.isoformat()
        }

# Routes
@app.route('/')
def index():
    return redirect(url_for('dashboard'))

@app.route('/dashboard')
def dashboard():
    # Get latest sensor data for dashboard
    latest_data = db.session.query(SensorData).order_by(SensorData.timestamp.desc()).limit(10).all()
    devices = Device.query.all()
    return render_template('dashboard.html', sensor_data=latest_data, devices=devices)

@app.route('/devices/add')
def add_device_page():
    return render_template('add_device.html')

@app.route('/api/devices', methods=['POST'])
def add_device_api():
    try:
        data = request.json
        
        # Check if device already exists
        existing_device = Device.query.filter_by(device_id=data['device_id']).first()
        if existing_device:
            return jsonify({'error': 'Device ID already exists'}), 400
        
        # Create new device with all configuration
        new_device = Device(
            device_id=data['device_id'],
            device_name=data['device_name'],
            device_type=data['device_type'],
            location=data.get('location', ''),
            description=data.get('description', ''),
            wifi_ssid=data.get('wifi_ssid', ''),
            wifi_security=data.get('wifi_security', 'WPA2'),
            static_ip=data.get('static_ip', ''),
            update_interval=int(data.get('update_interval', 10)),
            has_temperature=data.get('has_temperature', False),
            has_humidity=data.get('has_humidity', False),
            has_pressure=data.get('has_pressure', False),
            has_light=data.get('has_light', False),
            has_motion=data.get('has_motion', False),
            has_distance=data.get('has_distance', False)
        )
        
        db.session.add(new_device)
        db.session.commit()
        
        return jsonify({
            'message': 'Device added successfully',
            'device_id': new_device.device_id
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/setting')
def settings():
    devices = Device.query.all()
    return render_template('settings.html', devices=devices)

# API Endpoints for IoT devices
@app.route('/api/sensor-data', methods=['POST'])
def receive_sensor_data():
    """Endpoint for IoT devices to send sensor data"""
    try:
        data = request.json
        sensor_data = SensorData(
            device_id=data['device_id'],
            temperature=data.get('temperature'),
            humidity=data.get('humidity'),
            pressure=data.get('pressure'),
            light=data.get('light'),
            motion=data.get('motion', False)
        )
        db.session.add(sensor_data)
        db.session.commit()
        return jsonify({'status': 'success', 'message': 'Data received'}), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400

@app.route('/api/sensor-data', methods=['GET'])
def get_sensor_data():
    """Get sensor data for dashboard updates"""
    device_id = request.args.get('device_id')
    limit = request.args.get('limit', 50)
    
    query = SensorData.query
    if device_id:
        query = query.filter_by(device_id=device_id)
    
    data = query.order_by(SensorData.timestamp.desc()).limit(limit).all()
    return jsonify([item.to_dict() for item in data])

@app.route('/api/devices', methods=['GET'])
def get_devices():
    """Get all devices"""
    devices = Device.query.all()
    return jsonify([device.to_dict() for device in devices])

@app.route('/api/devices/<int:device_id>', methods=['PUT'])
def update_device(device_id):
    """Update a device"""
    try:
        device = Device.query.get_or_404(device_id)
        data = request.json
        
        # Update device fields
        device.device_name = data.get('device_name', device.device_name)
        device.device_type = data.get('device_type', device.device_type)
        device.location = data.get('location', device.location)
        device.description = data.get('description', device.description)
        device.wifi_ssid = data.get('wifi_ssid', device.wifi_ssid)
        device.wifi_security = data.get('wifi_security', device.wifi_security)
        device.static_ip = data.get('static_ip', device.static_ip)
        device.update_interval = int(data.get('update_interval', device.update_interval))
        
        # Update sensor capabilities
        device.has_temperature = data.get('has_temperature', device.has_temperature)
        device.has_humidity = data.get('has_humidity', device.has_humidity)
        device.has_pressure = data.get('has_pressure', device.has_pressure)
        device.has_light = data.get('has_light', device.has_light)
        device.has_motion = data.get('has_motion', device.has_motion)
        device.has_distance = data.get('has_distance', device.has_distance)
        
        db.session.commit()
        return jsonify({'status': 'success', 'message': 'Device updated successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 400

@app.route('/api/devices/<int:device_id>', methods=['DELETE'])
def delete_device(device_id):
    """Delete a device and all its sensor data"""
    try:
        device = Device.query.get_or_404(device_id)
        device_id_str = device.device_id
        
        # Delete all sensor data for this device
        SensorData.query.filter_by(device_id=device_id_str).delete()
        
        # Delete the device
        db.session.delete(device)
        db.session.commit()
        
        return jsonify({'status': 'success', 'message': 'Device and all related data deleted successfully'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400

@app.route('/api/devices/<int:device_id>', methods=['GET'])
def get_device(device_id):
    """Get a specific device"""
    try:
        device = Device.query.get_or_404(device_id)
        return jsonify(device.to_dict())
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400

if __name__ == '__main__':
    try:
        print("🔗 Connecting to Remote MySQL Database...")
        print(f"📍 Server: {DB_HOST}:{DB_PORT}")
        print(f"👤 User: {DB_USER}")
        print(f"💾 Database: {DB_NAME}")
        print("")
        
        # Test connection and create database if needed
        connection = pymysql.connect(
            host=DB_HOST,
            port=int(DB_PORT),
            user=DB_USER,
            password=DB_PASSWORD,
            charset='utf8mb4'
        )
        
        with connection.cursor() as cursor:
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME}")
            print(f"✅ Database '{DB_NAME}' created or verified on remote server")
        
        connection.close()
        
        # Create tables and add demo data
        with app.app_context():
            # Drop all tables and recreate with new schema
            db.drop_all()
            print("🔄 Dropped existing tables to update schema")
            
            db.create_all()
            print("✅ Database tables created successfully")
            
            # Add demo data if no devices exist
            if not Device.query.first():
                demo_devices = [
                    Device(
                        device_id='ESP32_001',
                        device_name='Living Room Sensor',
                        device_type='ESP32',
                        location='Living Room',
                        description='Temperature and humidity monitoring',
                        wifi_ssid='MyWiFi',
                        wifi_security='WPA2',
                        update_interval=30,
                        has_temperature=True,
                        has_humidity=True
                    ),
                    Device(
                        device_id='PICO_001',
                        device_name='Kitchen Sensor',
                        device_type='PICO WH',
                        location='Kitchen',
                        description='Motion detection and light monitoring',
                        wifi_ssid='MyWiFi', 
                        wifi_security='WPA2',
                        update_interval=15,
                        has_motion=True,
                        has_light=True
                    ),
                    Device(
                        device_id='ESP32_002',
                        device_name='Bedroom Sensor',
                        device_type='ESP32',
                        location='Bedroom',
                        description='Environmental monitoring',
                        wifi_ssid='MyWiFi',
                        wifi_security='WPA2',
                        update_interval=60,
                        has_temperature=True,
                        has_pressure=True
                    )
                ]
                
                demo_data = [
                    SensorData(device_id='ESP32_001', temperature=24.5, humidity=58.2, pressure=1013.25, light=450.0, motion=False),
                    SensorData(device_id='ESP32_001', temperature=25.1, humidity=59.5, pressure=1012.8, light=470.0, motion=True),
                    SensorData(device_id='PICO_001', temperature=22.8, humidity=55.0, pressure=1014.2, light=320.0, motion=False),
                    SensorData(device_id='PICO_001', temperature=23.2, humidity=56.3, pressure=1013.9, light=340.0, motion=False),
                    SensorData(device_id='ESP32_002', temperature=21.5, humidity=52.1, pressure=1015.1, light=280.0, motion=False),
                ]
                
                for device in demo_devices:
                    db.session.add(device)
                
                for data in demo_data:
                    db.session.add(data)
                
                db.session.commit()
                print("📝 Demo data created successfully!")
            
        print("✅ Remote MySQL Database connected successfully!")
        print("")
        print("🚀 Starting IoT Dashboard on http://localhost:5001")
        print("📊 Dashboard: http://localhost:5001/dashboard")
        print("➕ Add Device: http://localhost:5001/devices/add")
        print("⚙️  Settings: http://localhost:5001/setting")
        print("")
        print("🔗 API Endpoints:")
        print("   POST http://localhost:5001/api/sensor-data - Submit sensor data")
        print("   GET  http://localhost:5001/api/sensor-data - Retrieve sensor data")
        print("   GET  http://localhost:5001/api/devices - List devices")
        print("")
        print("🌐 Remote Database Info:")
        print(f"   MySQL Server: {DB_HOST}:{DB_PORT}")
        print(f"   Database: {DB_NAME}")
        print("   Status: Connected ✅")
        print("")
        
        app.run(debug=True, host='0.0.0.0', port=5001)
        
    except Exception as e:
        print("❌ CRITICAL ERROR: Cannot connect to remote MySQL database!")
        print(f"🔴 Error: {e}")
        print("")
        print("📋 Please verify:")
        print(f"   • MySQL server is running at {DB_HOST}:{DB_PORT}")
        print(f"   • Username '{DB_USER}' has proper permissions")
        print("   • Password is correct")
        print("   • Network connection is available")
        print("   • Firewall allows connection to port", DB_PORT)
        print("")
        print("🚫 Application will NOT start without remote MySQL connection")
        exit(1)
