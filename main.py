from gpiozero import MCP3008, AngularServo, OutputDevice, DigitalInputDevice, Buzzer
from time import sleep
import threading

class ServoMonitor:
    def __init__(self, servo_pin=12, relay_pin=27, vibe_pin=22, buzzer_pin=17, current_sensor_channel=0, temp_sensor_channel=1,
                 vcc=5.0, dht_pin=4, sensitivity=0.1, threshold_multiplier=1.005):
        """Initialize the ServoMonitor with the specified GPIO pins and settings.
        
        Args:
            servo_pin: GPIO pin connected to the servo PWM control
            relay_pin: GPIO pin connected to the relay control
            current_sensor_channel: ADC channel for the current sensor
            vcc: Supply voltage (V)
            sensitivity: Current sensor sensitivity (V/A)
            threshold_multiplier: Factor to multiply baseline current by to set threshold
        """
        self.servo = AngularServo(servo_pin)
        self.relay = OutputDevice(relay_pin)
        self.current_sensor = MCP3008(current_sensor_channel)
        self.temp_sensor = MCP3008(temp_sensor_channel)
        self.vibration_sensor = DigitalInputDevice(vibe_pin)
        self.buzzer = Buzzer(buzzer_pin)
        self.vcc = vcc
        self.sensitivity = sensitivity
        self.threshold_multiplier = threshold_multiplier
        self.current_threshold = 0.5  # Default threshold until calibrated
        self.dht_pin = dht_pin
        self.monitoring_active = False
        self.monitor_thread = None
        self.current_monitoring_active = False
        self.temp_threshold_high = 0.89
        self.temp_threshold_low = 0.70
        self.enable_vibration = True
        self.enable_temp = True
        self.enable_current = True
        
        # Turn on relay by default
        self.relay.on()

        # Latest readings from DHT11
        self.last_temperature = None
        self.last_humidity = None
    
    def sample_sensor(self, samples=1000, time_span=1):
        """Sample the current sensor multiple times and return the average.
        
        Args:
            samples: Number of samples to take
            time_span: Total time over which to take samples (seconds)
        
        Returns:
            Average sensor reading (0-1 range)
        """
        delay = time_span / samples
        val = 0
        for _ in range(samples):
            val += self.current_sensor.value
            sleep(delay)
        return val / samples
    
    def calc_current(self, val):
        """Convert raw sensor value to normalized current value.
        
        Args:
            val: Raw sensor reading (0-1)
            
        Returns:
            Normalized current value (0-1 range)
        """
        return 1 - (((self.vcc / 2) - (self.vcc * val)) / self.sensitivity)
    
    def move_servo(self, angle, calibrate=True, delay=1):
        """Move the servo to the specified angle and optionally calibrate current threshold.
        
        Args:
            angle: Target angle for the servo (-90 to 90 degrees)
            calibrate: Whether to calibrate the current threshold after movement
        """
        # Temporarily pause monitoring during movement and calibration
        was_monitoring = self.monitoring_active
        if was_monitoring:
            self.stop_monitoring()
        
        # Ensure relay is on
        self.relay.on()
        
        # Move servo
        self.servo.angle = angle
        
        # Allow servo to complete movement
        sleep(delay)
        
        # Calibrate if requested
        if calibrate:
            self.calibrate_threshold()
        
        # Resume monitoring if it was active
        if was_monitoring:
            self.start_monitoring()
    
    def calibrate_threshold(self):
        """Calibrate the current threshold based on current servo state."""
        print("Calibrating current threshold...")
        
        # Sample current with extended parameters
        baseline = self.sample_sensor(samples=10000, time_span=5)
        
        # Set new threshold with safety margin
        self.current_threshold = baseline * self.threshold_multiplier
        
        print(f"New baseline: {baseline:.4f}, New threshold: {self.current_threshold:.4f}")
    
    def check_current(self):
        """Check if current exceeds threshold and handle accordingly."""
        current_val = self.sample_sensor(samples=100, time_span=1)
        print(f"Current: {current_val} {current_val - self.current_threshold} {current_val / self.current_threshold}")
        
        if current_val > self.current_threshold:
            print(f"Current exceeded threshold! Reading: {current_val:.4f}, Threshold: {self.current_threshold:.4f}")
            self.monitoring_active = False  # Stop monitoring
            return self.enable_current
        return False
    
    def check_vibration(self):
        if self.vibration_sensor.value:
            print("Vibration")
            return self.enable_vibration
        else:
            print("No Vibration")
            return False
    
    def check_temp(self):
        temperature = self.temp_sensor.value
        
        print(f"Temperature: {temperature:.10f}")
        
        # Check thresholds
        if (temperature > self.temp_threshold_high or 
            temperature < self.temp_threshold_low):
            
            print(f"Environment conditions exceeded thresholds!")
            print(f"Temperature: {temperature:.10f} (Thresholds: {self.temp_threshold_low:.3f}-{self.temp_threshold_high:.3f})")
            return self.enable_temp
            
        return False
    
    def monitor_loop(self):
        """Background monitoring loop to continuously check current."""
        while self.monitoring_active:
            if self.check_current() or self.check_vibration() or self.check_temp():
                self.relay.off()  # Cut power
                print("Safety cutoff activated!")
                self.buzzer.on()
                sleep(1)
                self.buzzer.off()
                break
            sleep(0.05)  # Check approximately 20 times per second
    
    def start_monitoring(self):
        """Start background current monitoring."""
        if not self.monitoring_active:
            self.monitoring_active = True
            self.relay.on()  # Ensure relay is on when starting monitoring
            self.monitor_thread = threading.Thread(target=self.monitor_loop)
            self.monitor_thread.daemon = True
            self.monitor_thread.start()
            print("Current monitoring started")
    
    def stop_monitoring(self):
        """Stop background current monitoring."""
        self.monitoring_active = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=1.0)
            self.monitor_thread = None
        print("Current monitoring stopped")
    
    def reset(self):
        """Reset after a safety cutoff."""
        self.relay.on()
        print("System reset - relay turned on")


# Example usage:
if __name__ == "__main__":
    # Create ServoMonitor instance
    monitor = ServoMonitor()
    
    # Calibrate with servo at center position
    monitor.move_servo(0, calibrate=False)
    
    # Start monitoring
    monitor.start_monitoring()
    
    try:
        # Move servo to different positions
        for angle in [30, -30, 45, -45, 0]:
            print(f"Moving servo to {angle} degrees")
            monitor.move_servo(angle, calibrate=True)
            sleep(10)
    
    except KeyboardInterrupt:
        print("Program interrupted")
    
    finally:
        # Clean up
        monitor.stop_monitoring()
        monitor.relay.off()
        monitor.buzzer.off()
        print("Program ended")
