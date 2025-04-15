# SE_PBL_Pollution_Monitoring
 Pollution Monitoring through heatmaps

 # 🌍 Mobile Air Pollution Monitoring System

This project monitors real-time environmental and air pollution data using an ESP32-based mobile setup. The system logs data from multiple sensors every 20 seconds while moving and generates separate heatmaps using Python and Folium. The heatmaps are then displayed and made downloadable via a Flask-based web application.

---

## 🚀 Features

- Real-time sensor data logging every 20 seconds
- Mobile setup with GPS-based location tracking
- Measures temperature, humidity, PM2.5, PM10, CO, and harmful gases (NH3, SO2, NOx, Benzene)
- Stores data in CSV format
- Generates interactive heatmaps using Folium
- Flask web app to display and download heatmaps
- Post-processing and visualization using Python

---

## 🧰 Hardware Components

| Component      | Functionality                                           |
|----------------|---------------------------------------------------------|
| **ESP32**      | Microcontroller for data acquisition & logging          |
| **DHT11**      | Measures temperature and humidity                       |
| **NEO-6M GPS** | Provides latitude and longitude coordinates             |
| **DSM501A**    | Detects particulate matter (PM2.5 & PM10)               |
| **MQ-7**       | Detects carbon monoxide (CO)                            |
| **MQ-135**     | Detects NH3, SO2, NOx, Benzene and other harmful gases |

---

## 📁 Data Logging Format

Each row in the CSV contains:

```
Latitude, Longitude, Temperature, Humidity, PM2.5, PM10, CO, MQ135_Gas, Timestamp
```

- Logged every 20 seconds while the system is in motion
- Data saved locally in `.csv` format

---

## 🧪 Heatmap Generation

1. Run the provided Python script after data collection to process the CSV data.
2. Normalize values for each parameter.
3. Generate individual heatmaps using Folium.
4. The heatmaps are saved as `.html` and `.png` files.

---

## 🖥️ Flask Web App for Heatmap Display

- The Flask app allows users to:
  - View generated heatmaps.
  - Download heatmaps as PNG images.
- The app uses Folium to display heatmaps dynamically in a web browser.

---

## 🗺️ Heatmaps Generated

- 🌡️ Temperature Distribution
- 💧 Humidity Levels
- 🌀 PM2.5 & PM10 Concentration
- 🚗 CO Pollution Levels
- ☠️ Overall Harmful Gases (MQ-135 Readings)

---

## 📊 Current Workflow

- Data is collected offline and processed later.
- Heatmaps are generated via Python and displayed using Flask.
- Users can interact with heatmaps via the web interface and download them.

---

## 🌐 Future Enhancements

- Cloud-based data storage and processing.
- Real-time data transmission via WiFi/Bluetooth.
- Live web dashboard for dynamic heatmap display.
- Integration with environmental alert systems.

---

## 📌 Summary

- 📡 ESP32 logs multi-sensor data every 20 seconds with GPS.
- 📄 Data is stored in CSV files.
- 🧠 Python processes data and generates separate heatmaps.
- 🖥️ Heatmaps are displayed and downloadable via Flask-based web application.
- 💡 Useful for urban planning, health research & environmental monitoring.

---

## 🔧 Running the Flask App

1. **Install dependencies**:

   ```
   pip install flask folium pandas
   ```

2. **Run the Flask app**:

   ```
   python app.py
   ```

3. **Access the app**:
   - Open `http://127.0.0.1:5000/` in your web browser to view and interact with the heatmaps.

4. **Download the heatmaps**:
   - After visualizing the heatmaps, you can download them as `.png` files.

---

