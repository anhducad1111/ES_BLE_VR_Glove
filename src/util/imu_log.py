import queue
import time

from src.util.base_log import BaseLog


class IMULog(BaseLog):
    """IMU logger with thread queue processing"""

    def __init__(self, imu_number):
        super().__init__()
        self.imu_number = imu_number

    def write_csv(self, imu_data, euler_data):
        """Queue IMU data for writing"""
        if not self.is_logging:
            return

        try:
            data = {
                "timestamp": int(time.time() * 1000),
                "imu_data": imu_data,
                "euler_data": euler_data,
            }
            self.queue.put(data, block=False)
        except queue.Full:
            pass

    def _write_row(self, data):
        """Write IMU data row to CSV"""
        try:
            imu_data = data["imu_data"]
            euler_data = data["euler_data"]

            row = [
                data["timestamp"],
                imu_data.accel["x"],
                imu_data.accel["y"],
                imu_data.accel["z"],
                imu_data.gyro["x"],
                imu_data.gyro["y"],
                imu_data.gyro["z"],
                imu_data.mag["x"],
                imu_data.mag["y"],
                imu_data.mag["z"],
                euler_data.euler["yaw"],
                euler_data.euler["pitch"],
                euler_data.euler["roll"],
            ]

            self.writer.writerow(row)
            self.file.flush()
            self.row_count += 1
        except:
            pass

    def _get_headers(self):
        """Get headers for IMU CSV file"""
        return [
            "timestamp",
            "ax",
            "ay",
            "az",
            "gx",
            "gy",
            "gz",
            "mx",
            "my",
            "mz",
            "ex",
            "ey",
            "ez",
        ]

    def _get_filename(self):
        """Get filename for IMU log file"""
        return f"imu{self.imu_number}.csv"
