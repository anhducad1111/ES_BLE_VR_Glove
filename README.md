# VR Glove Control Application

This application provides a graphical interface for monitoring and controlling a VR glove device via Bluetooth LE connection. It features IMU data visualization, sensor monitoring, and data logging capabilities.

## Key Features

### Device Connection
- Connect/disconnect to BLE devices
- Display device information:
  - Name
  - Status
  - Battery level
  - Charging state
  - Firmware version
  - Model number
  - Manufacturer
  - Hardware version

### IMU Monitoring
- Real-time visualization of two IMU sensors
- For each IMU:
  - Accelerometer data (X, Y, Z)
  - Gyroscope data (X, Y, Z)
  - Magnetometer data (X, Y, Z)
  - Euler angles (Pitch, Roll, Yaw)
  - Graph visualization option
  - Calibration capabilities

### IMU Data Logging
1. Click "Log" button to open folder selection dialog
2. Choose destination folder and click "Apply"
3. Click "Start Log" to begin recording
   - Creates timestamped subfolder (format: ddmmyyyy_hhmmss_vr_glove)
   - Records IMU and Euler data from both sensors
4. Click "Stop Log" to end recording
   - Saves all data to CSV files
   - Returns to initial state for new recording

### Sensor Monitoring
- Flex sensor data visualization
- Force sensor data visualization
- Real-time updates
- Graphical representation

### Gamepad Features
- Joystick position monitoring
- Button state tracking
- Visual feedback of inputs

## Interface Layout

### Main Window
- Information panel with device details
- IMU1 and IMU2 data panels
- Sensor monitoring section
- Gamepad status display
- Footer with timestamp information

### Control Buttons
- Add device/Disconnect
- Log/Start Log/Stop Log
- Calibration options
- Graph toggles

### Dialog Windows
- Connection dialog with device scanning
- IMU calibration settings
- Folder selection for logging
- Configuration options

## Technical Details

### Communication
- Bluetooth LE connection
- Custom service UUIDs for different features
- Real-time data streaming
- Bidirectional communication

### Data Management
- CSV file logging
- Timestamped data recording
- Separate files for IMU1 and IMU2
- Automatic folder organization

#### Log File Structure
```
selected_folder/
└── ddmmyyyy_hhmmss_vr_glove/
    ├── imu1.csv
    └── imu2.csv
```

#### CSV Format
Each IMU CSV file contains the following columns:
```
timestamp,ax,ay,az,gx,gy,gz,mx,my,mz,ex,ey,ez
```
Where:
- timestamp: Unix timestamp in milliseconds
- ax,ay,az: Accelerometer data (X,Y,Z)
- gx,gy,gz: Gyroscope data (X,Y,Z)
- mx,my,mz: Magnetometer data (X,Y,Z)
- ex,ey,ez: Euler angles (Yaw, Pitch, Roll)

### Architecture
- Model-View-Presenter (MVP) pattern
- Asynchronous communication handling
- Event-driven updates
- Modular component design

## Installation & Setup

### Requirements
- Python 3.8 or higher
- Git (optional)

### Dependencies
- customtkinter: Enhanced tkinter widgets
- bleak: Bluetooth LE communication
- matplotlib: Data visualization
- PIL: Image handling
- asyncio: Asynchronous operations

### Installation Steps
1. Clone the repository (or download ZIP):
   ```bash
   git clone <repository-url>
   cd tutorial_python
   ```

2. Install required packages:
   ```bash
   pip install -r requirements.txt
   ```

## Usage Guide

### Starting the Application
1. Run the main script:
   ```bash
   python main.py
   ```

### Connecting a Device
1. Click "Add device" to scan for BLE devices
2. Select your VR glove from the list
3. Wait for connection confirmation
4. Device information will be displayed in the info panel

### Data Logging
1. Click "Log" to open folder selection
2. Choose a parent folder for storing log files
3. Click "Apply" to confirm folder selection
4. Click "Start Log" to begin recording data
5. Click "Stop Log" to end recording
   - Data is saved in timestamped subfolders
   - Each IMU's data is saved in separate CSV files

### IMU Calibration
1. Click calibration button on IMU panel
2. Follow on-screen instructions
3. Apply calibration settings

### Monitoring Data
- View real-time IMU data in numeric and graph forms
- Monitor flex and force sensor readings
- Track gamepad inputs
- Check battery level and charging status

## Troubleshooting

### Common Issues
1. Device not found
   - Ensure Bluetooth is enabled
   - Check device is powered on
   - Try restarting the device

2. Connection drops
   - Check device battery level
   - Ensure device is within range
   - Try reconnecting

3. Data logging issues
   - Verify write permissions in selected folder
   - Ensure sufficient disk space
   - Check folder path is valid

## Future Enhancements
- Extended calibration options
- Additional sensor support
- Enhanced data visualization
- Configuration profiles
- Data export formats
