# CMPSC 497 Final Project: Industrial Monitoring System

## Project Description:
This project is designed to simulate an Industrial Equipment Monitoring and Predictive Maintenance System, using a Raspberry Pi 4. The project includes a vibration sensor, temperature sensor, and current sensor, all monitoring the condition of a servomotor, and set up to trigger a buzzer and relay module if abnormalities are detected, sounding an alarm and cutting power to the servomotor. 

## Project Usage:
1. Run **main.py**. This will turn on the servomotor, have the program check how much current the servo is supposed to draw, then begin the monitoring loop.
2. **Test the sensors**:
  
   2a. **Testing the current sensor**: After calibration has completed, attempt to push the servomotor away from its held position. It should attempt to draw more current to resist this push, and trip the current sensor, shutting down the system.
   
   2b. **Testing the temperature sensor**: Pinch the black nub on the temperature sensor. This should soon increase the detected temperature high enough to make the check fail, shutting down the system.
   
   2c. **Testing the vibration sensor**: The servomotor is set to change its position every so often. Hold it in place when this occurs, preventing it from moving. This should cause it to vibrate enough to notify the vibration sensor, shutting down the system.

