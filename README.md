# CMPSC 497 Final Project: Industrial Monitoring System

## Project Description:
This project is designed to simulate an Industrial Equipment Monitoring and Predictive Maintenance System, using a Raspberry Pi 4. The project includes a vibration sensor, temperature sensor, and current sensor, all monitoring the condition of a servomotor, and set up to trigger a buzzer and relay module if abnormalities are detected, sounding an alarm and cutting power to the servomotor. 

## Project Usage:
1. First install the dependancies of the project. This only depends on gpiozero which may or may not come installed on your Raspberry Pi. Simply run `pip install gpiozero` to ensure it's installed.
2. Run **main.py**. This will turn on the servomotor, have the program check how much current the servo is supposed to draw, then begin the monitoring loop. Whenever the servo moves, it will recalibrate the sensors, which pauses the monitoring for some duration.
3. **Test the sensors**:
  
   2a. **Testing the current sensor**: After calibration has completed, attempt to push the servomotor away from its held position. It should attempt to draw more current to resist this push, and trip the current sensor, shutting down the system.
   
   2b. **Testing the temperature sensor**: Pinch the black nub on the temperature sensor. This should soon increase the detected temperature high enough to make the check fail, shutting down the system.
   
   2c. **Testing the vibration sensor**: The vibration sensor detects any internal or external vibrations. You can test this by simply shaking the device while will trigger the sensor and shut down the system.

