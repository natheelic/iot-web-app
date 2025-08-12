# 🌐 IoT Flask Web Application with MySQL

A modern IoT web application built with Flask that collects, stores, and visualizes sensor data from ESP32, Raspberry Pi Pico WH, and other IoT devices. Features a real-time dashboard, device management, and RESTful API endpoints.

## ✨ Key Features

- 📊 **Real-time Dashboard** - Live sensor data visualization with interactive charts
- 🔌 **IoT Device Integration** - Supports ESP32, PICO WH, Arduino, and other devices
- 💾 **MySQL Database** - Robust data storage and retrieval
- 📱 **Responsive Design** - Works seamlessly on desktop, tablet, and mobile
- 📈 **Data Visualization** - Chart.js powered graphs and statistics
- ⚙️ **Device Management** - Add, edit, and monitor IoT devices
- 🔒 **Secure API** - RESTful endpoints for device data transmission
- 📊 **Export Functionality** - Download data as CSV or JSON

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- MySQL Server (or access to remote MySQL instance)
- pip package manager

### Installation

1. **Clone or navigate to the project directory:**
   ```bash
   cd /Users/natheesrina/Sources/iot-web-app
   ```

2. **Create a virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env file with your database credentials
   ```

5. **Run the application:**
   ```bash
   python app.py
   ```

6. **Open your browser:**
   Navigate to `http://localhost:5001`

## 📱 Application Pages

- **Dashboard** (`/dashboard`) - Real-time sensor data visualization
- **Add Device** (`/devices/add`) - Register new IoT devices with generated code
- **Settings** (`/setting`) - Device management and system configuration

## 🔌 API Endpoints

### Sensor Data

- **POST** `/api/sensor-data` - Submit sensor readings from IoT devices
- **GET** `/api/sensor-data` - Retrieve sensor data with optional filtering

### Device Management

- **GET** `/api/devices` - List all registered devices
- **POST** `/devices` - Register a new device

### Example IoT Device Payload

```json
{
  "device_id": "ESP32_001",
  "temperature": 25.5,
  "humidity": 60.0,
  "pressure": 1013.25,
  "light": 500.0,
  "motion": false
}
```

## 🛠️ IoT Device Integration

### ESP32/Arduino Code

```cpp
#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>

const char* ssid = "YOUR_WIFI_SSID";
const char* password = "YOUR_WIFI_PASSWORD";
const char* serverURL = "http://your-server:5001/api/sensor-data";
const char* deviceID = "ESP32_001";

void setup() {
  Serial.begin(115200);
  WiFi.begin(ssid, password);
  
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.println("Connecting to WiFi...");
  }
}

void loop() {
  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;
    http.begin(serverURL);
    http.addHeader("Content-Type", "application/json");
    
    StaticJsonDocument<200> doc;
    doc["device_id"] = deviceID;
    doc["temperature"] = 25.5;  // Replace with actual sensor reading
    doc["humidity"] = 60.0;     // Replace with actual sensor reading
    
    String jsonString;
    serializeJson(doc, jsonString);
    
    int httpResponseCode = http.POST(jsonString);
    
    if (httpResponseCode > 0) {
      Serial.println("Data sent successfully");
    }
    
    http.end();
  }
  
  delay(10000); // Send data every 10 seconds
}
```

### Python (Raspberry Pi Pico WH)

```python
import network
import urequests
import json
import time

SSID = "YOUR_WIFI_SSID"
PASSWORD = "YOUR_WIFI_PASSWORD"
SERVER_URL = "http://your-server:5001/api/sensor-data"
DEVICE_ID = "PICO_001"

def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(SSID, PASSWORD)
    
    while not wlan.isconnected():
        print("Connecting to WiFi...")
        time.sleep(1)
    
    print("Connected to WiFi")

def send_data():
    data = {
        "device_id": DEVICE_ID,
        "temperature": 25.5,  # Replace with actual sensor reading
        "humidity": 60.0      # Replace with actual sensor reading
    }
    
    try:
        response = urequests.post(SERVER_URL, json=data)
        if response.status_code == 200:
            print("Data sent successfully")
        response.close()
    except Exception as e:
        print("Error:", str(e))

connect_wifi()

while True:
    send_data()
    time.sleep(10)
```

## 📊 Database Schema

### Devices Table
- `id` - Primary key
- `device_id` - Unique device identifier
- `device_name` - Human-readable name
- `device_type` - Device type (ESP32, PICO WH, etc.)
- `location` - Physical location
- `status` - Active/Inactive
- `created_at` - Registration timestamp

### Sensor Data Table
- `id` - Primary key
- `device_id` - Foreign key to device
- `temperature` - Temperature reading (°C)
- `humidity` - Humidity reading (%)
- `pressure` - Pressure reading (hPa)
- `light` - Light sensor reading
- `motion` - Motion detection (boolean)
- `timestamp` - Data timestamp

## 🔧 Configuration

### Environment Variables

Create a `.env` file with the following variables:

```env
# Database Configuration
DB_HOST=your_mysql_host
DB_PORT=3306
DB_USER=your_username
DB_PASSWORD=your_password
DB_NAME=iot_data

# Flask Configuration
SECRET_KEY=your-secret-key-here
FLASK_ENV=development
FLASK_DEBUG=True
```

### Database Setup

The application automatically creates the required tables on first run. Ensure your MySQL server is running and accessible with the provided credentials.

## 🎨 Customization

### Adding New Sensor Types

1. Update the database model in `app.py`
2. Modify the API endpoints to handle new sensor data
3. Update the dashboard templates to display new sensor types
4. Generate appropriate device code in the add device page

### Styling

- Modify `static/css/style.css` for custom styling
- Update templates in the `templates/` directory
- Charts can be customized in `static/js/app.js`

## 📋 Project Structure

```
iot-web-app/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── .env                  # Environment variables (create from .env.example)
├── .env.example          # Example environment variables
├── templates/            # HTML templates
│   ├── base.html         # Base template
│   ├── dashboard.html    # Dashboard page
│   ├── add_device.html   # Add device page
│   └── settings.html     # Settings page
├── static/               # Static files
│   ├── css/
│   │   └── style.css     # Custom styles
│   └── js/
│       └── app.js        # JavaScript functionality
└── README.md            # This file
```

## 🚀 Deployment

### Production Considerations

1. **Security:**
   - Change the default SECRET_KEY
   - Use environment variables for sensitive data
   - Enable HTTPS
   - Implement proper authentication

2. **Database:**
   - Use a production MySQL server
   - Set up proper backups
   - Configure connection pooling

3. **Performance:**
   - Use a WSGI server like Gunicorn
   - Set up a reverse proxy (Nginx)
   - Enable caching
   - Optimize database queries

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📝 License

This project is open source and available under the MIT License.

## 🆘 Support

If you encounter any issues or have questions:

1. Check the console logs for error messages
2. Verify database connectivity
3. Ensure all dependencies are installed
4. Check the API endpoints with a tool like Postman

## 🔄 Updates

- **v1.0.0** - Initial release with basic dashboard and device management
- Real-time data updates every 5 seconds
- Responsive design for all devices
- Export functionality for data analysis
