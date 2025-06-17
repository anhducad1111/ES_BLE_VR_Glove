import asyncio


class DeviceManager:
    """Class for managing device services and notifications"""

    _instance = None

    def __new__(cls, ble_service=None, presenters=None):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, ble_service=None, presenters=None):
        """Initialize device manager

        Args:
            ble_service: BLE service instance
            presenters: Dictionary containing presenter instances
        """
        if not hasattr(self, "initialized"):
            self.service = ble_service
            self.presenters = presenters
            self._verify_required_presenters()
            self.initialized = True

    def _verify_required_presenters(self):
        """Verify all required presenters are available"""
        required = [
            "profile",
            "overall_status",
            "imu1",
            "imu2",
            "timestamp",
            "sensor",
            "connection",
            "gamepad",
        ]
        for name in required:
            if name not in self.presenters:
                raise KeyError(f"Missing required presenter: {name}")

    async def _start_service_with_retry(self, service_name, max_retries=10, delay=0.1):
        """Start a service with retry logic and delay

        Args:
            service_name: Name of the service to start
            max_retries: Maximum number of retry attempts
            delay: Delay in seconds between retries

        Returns:
            bool: True if service started successfully, False otherwise
        """
        for attempt in range(max_retries):
            try:
                if await self.presenters[service_name].start_notifications():
                    print(f"✓ Started {service_name} service (attempt {attempt + 1})")
                    return True

                if attempt < max_retries - 1:
                    print(f"! {service_name} service start returned False, retrying...")
                    await asyncio.sleep(delay)

            except Exception as e:
                if attempt < max_retries - 1:
                    print(
                        f"! Error starting {service_name} service (attempt {attempt + 1}): {e}"
                    )
                    await asyncio.sleep(delay)
                else:
                    print(
                        f"✕ Failed to start {service_name} service after {max_retries} attempts: {e}"
                    )

        return False

    async def start_services(self):
        """Start all device services concurrently after connection"""
        try:
            # Wait for services to be fully discovered
            await asyncio.sleep(0.5)

            # Define services to start
            services = [
                "profile",  # Device profile & battery
                "overall_status",  # System status monitoring
                "imu1",  # IMU services
                "imu2",
                "sensor",  # Sensors
                "gamepad",  # Gamepad
                "log",     # Log manager
            ]

            # Start all services concurrently
            results = await asyncio.gather(
                *[self._start_service_with_retry(service) for service in services],
                return_exceptions=True,
            )

            # Process results and collect failures
            failures = []
            for service, result in zip(services, results):
                if isinstance(result, Exception):
                    print(f"Error starting {service}: {result}")
                    failures.append(service)
                elif not result:
                    failures.append(service)

            # Read timestamp and auto-sync device time
            await self.presenters["timestamp"].read_timestamp()
            if await self.presenters["timestamp"].write_current_time():
                print("✓ Device time synchronized with PC")
            else:
                print("! Failed to synchronize device time")

            # Handle critical services
            critical_services = {"imu1", "imu2"}
            if critical_services.intersection(failures):
                print(
                    f"Critical service(s) failed: {critical_services.intersection(failures)}"
                )
                await self.cleanup()
                return False

            return True

        except Exception as e:
            print(f"Error during service initialization: {e}")
            await self.cleanup()
            return False

    async def cleanup(self):
        """Clean up all device services"""
        services = [
            "profile",  # Device profile & battery
            "overall_status",  # System status monitoring
            "imu1",  # IMU services
            "imu2",
            "sensor",  # Sensors
            "gamepad",  # Gamepad
            "log",    # Log manager
        ]

        try:
            # First stop all notifications concurrently
            stop_tasks = []
            for service in services:
                if service in self.presenters:
                    stop_tasks.append(self.presenters[service].stop_notifications())

            if stop_tasks:
                await asyncio.gather(*stop_tasks)

            # Brief delay for notifications to stop
            await asyncio.sleep(0.2)

            # Then clear views (synchronously)
            for service in services:
                presenter = self.presenters.get(service)
                if not presenter:
                    continue

                view = getattr(presenter, "view", None)
                if not view:
                    continue

                try:
                    if hasattr(view, "clear_values"):
                        view.clear_values()
                except Exception as e:
                    print(f"Error clearing {service} view: {e}")

        except Exception as e:
            print(f"Error during cleanup: {e}")

    async def connect(self, device_info):
        """Connect to device only"""
        try:
            # Convert dict to profile
            profile = self.presenters["profile"].create_profile(
                {
                    "address": device_info["address"],
                    "name": device_info["name"],
                    "rssi": device_info["rssi"],
                }
            )

            # Only connect, don't start services
            return await self.presenters["connection"].connect_to_device(profile)
        except Exception as e:
            print(f"Error connecting to device: {e}")
            return False

    async def start_device_services(self):
        """Start all device services after OK button is clicked"""
        return await self.start_services()

    async def disconnect(self):
        """Disconnect from device and cleanup"""
        try:
            await self.cleanup()
            await self.presenters["connection"].disconnect()
        except Exception:
            pass

    def is_connected(self):
        """Check if device is connected"""
        return self.service and self.service.is_connected()
