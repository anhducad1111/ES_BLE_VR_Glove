import queue
import time

from src.util.base_log import BaseLog


class SensorLog(BaseLog):
    """Sensor logger with thread queue processing"""

    def write_csv(self, flex_values, force_value):
        """Write sensor data to CSV file"""
        if not self.is_logging:
            return

        try:
            data = {
                "timestamp": int(time.time() * 1000),
                "flex_values": flex_values,
                "force_value": force_value,
            }
            self.queue.put(data, block=False)
        except queue.Full:
            pass

    def _write_row(self, data):
        """Write a single row of sensor data to CSV"""
        try:
            flex_values = data["flex_values"]
            row = [data["timestamp"]]
            row.extend(flex_values)
            row.append(data["force_value"])

            self.writer.writerow(row)
            self.file.flush()
            self.row_count += 1
        except:
            pass

    def _get_headers(self):
        """Get headers for sensor CSV file"""
        headers = ["timestamp"]
        headers.extend([f"flex{i+1}" for i in range(5)])
        headers.append("force")
        return headers

    def _get_filename(self):
        """Get filename for sensor log file"""
        return "sensors.csv"
