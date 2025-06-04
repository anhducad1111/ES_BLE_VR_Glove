import csv
import os
import time
import asyncio
from .imu import IMUDataObserver, BaseIMUData, IMUEulerData

class IMULogger(IMUDataObserver):
    """Scalable async queue-based IMU logger that can handle unlimited number of IMUs"""
    
    def __init__(self, path):
        """Initialize scalable async IMU logger
        
        Args:
            path: Directory path where CSV files will be created
        """
        self.path = path
        self.is_logging = False
        
        # Dynamic storage for IMUs - can handle unlimited IMUs
        self.imu_queues = {}      # {imu_number: asyncio.Queue}
        self.imu_tasks = {}       # {imu_number: asyncio.Task}
        self.imu_files = {}       # {imu_number: file_object}
        self.imu_writers = {}     # {imu_number: csv.writer}
        self.headers_written = {} # {imu_number: bool}
        
    async def start_logging(self):
        """Start logging system - IMUs will be added dynamically as data arrives"""
        try:
            BaseIMUData.add_observer(self)
            
            self.is_logging = True
            return True
            
        except Exception as e:
            print(f"Error starting logging: {e}")
            await self.stop_logging()
            return False
    
    async def stop_logging(self):
        """Stop logging and clean up all resources"""
        self.is_logging = False
        
        # Unregister from observer pattern
        try:
            BaseIMUData.remove_observer(self)
        except:
            pass
        
        # Cancel all tasks and wait for them to finish
        for imu_number, task in self.imu_tasks.items():
            if task and not task.done():
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
        
        # Close all files
        for imu_number, file_obj in self.imu_files.items():
            if file_obj:
                file_obj.close()
        
        # Clear all dictionaries
        self.imu_queues.clear()
        self.imu_tasks.clear()
        self.imu_files.clear()
        self.imu_writers.clear()
        self.headers_written.clear()
    
    def on_imu_data_received(self, imu_number, imu_data, euler_data):
        """Observer method - dynamically handle any IMU number"""
        if not self.is_logging:
            return
        
        # Ensure IMU is set up
        self._ensure_imu_setup(imu_number)
        
        timestamp = int(time.time() * 1000)
        data_package = {
            'timestamp': timestamp,
            'imu_data': imu_data,
            'euler_data': euler_data
        }
        
        try:
            if imu_number in self.imu_queues:
                # Queue data for async processing
                asyncio.create_task(self.imu_queues[imu_number].put(data_package))
        except Exception as e:
            print(f"Error queuing data for IMU{imu_number}: {e}")
    
    def _ensure_imu_setup(self, imu_number):
        """Ensure IMU resources are set up (files, writers, queues, tasks)"""
        if imu_number in self.imu_files:
            return  # Already set up
        
        try:
            # Create CSV file
            filename = f'imu{imu_number}.csv'
            file_path = os.path.join(self.path, filename)
            file_obj = open(file_path, 'w', newline='')
            
            # Create CSV writer
            writer = csv.writer(file_obj)
            
            # Create async queue
            queue = asyncio.Queue()
            
            # Create processing task
            task = asyncio.create_task(self._process_imu_queue(imu_number))
            
            # Store in dictionaries
            self.imu_files[imu_number] = file_obj
            self.imu_writers[imu_number] = writer
            self.imu_queues[imu_number] = queue
            self.imu_tasks[imu_number] = task
            self.headers_written[imu_number] = False
            
            print(f"Set up async logging for IMU{imu_number}")
            
        except Exception as e:
            print(f"Error setting up IMU{imu_number}: {e}")
    
    async def _process_imu_queue(self, imu_number):
        """Process data queue for specific IMU"""
        while self.is_logging:
            try:
                if imu_number not in self.imu_queues:
                    break
                    
                data_package = await asyncio.wait_for(
                    self.imu_queues[imu_number].get(), timeout=0.1
                )
                await self._write_imu_data_async(imu_number, data_package)
                
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                print(f"Error processing IMU{imu_number} queue: {e}")

    async def _write_imu_data_async(self, imu_number, data_package):
        """Write IMU data to appropriate CSV file (async version)"""
        try:
            if imu_number not in self.imu_writers:
                return
                
            timestamp = data_package['timestamp']
            imu_data = data_package['imu_data']
            euler_data = data_package['euler_data']
            
            writer = self.imu_writers[imu_number]
            file_obj = self.imu_files[imu_number]
            
            # Write headers if not yet written
            if not self.headers_written[imu_number]:
                imu_headers = imu_data.get_log_headers()
                euler_headers = ['ex', 'ey', 'ez']
                full_headers = ['timestamp'] + imu_headers + euler_headers
                writer.writerow(full_headers)
                self.headers_written[imu_number] = True
            
            # Get flexible field data from IMU
            imu_fields = imu_data.get_log_fields()
            euler_fields = [
                euler_data.euler['yaw'],
                euler_data.euler['pitch'],
                euler_data.euler['roll']
            ]
            
            # Prepare row data in correct order
            row = [timestamp] + list(imu_fields.values()) + euler_fields
            
            # Write row
            writer.writerow(row)
            file_obj.flush()
            
        except Exception as e:
            print(f"Error writing IMU{imu_number} data: {e}")
    
    def get_active_imus(self):
        """Get list of currently active IMU numbers"""
        return list(self.imu_files.keys())
    
    def get_imu_count(self):
        """Get count of active IMUs"""
        return len(self.imu_files)
    
    # Legacy methods for backward compatibility
    def log_imu_data(self, imu_number, imu_data, euler_data):
        """Legacy method - now handled by observer pattern"""
        self.on_imu_data_received(imu_number, imu_data, euler_data)
