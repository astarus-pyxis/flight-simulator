## Commercial Aircraft Flight simulator ##

By Florian Topeza and Arthur Jolivet, ISAE-SUPAERO, 2024

Repository under MIT License

# Repository organisation

+-src

 |      - flight simulation.py

 |      - AP603_simulation.py

 |      - airplane.mp3

 |      - stall_alarm.wav
 
 |      - too_low_alarm.wav  

This repository provides a basic flight simulator in the file flight_simulation.py. The code implements equations from flight mechanics and a graphic interface with sounds to simulate the cockpit of a commercial aircraft.

The file AP603_simulation.oy provides a simulation inspired by the accident of the flight AP603. Stall and too low alarms start to ring without any reason at a certain point of the simulation, and the altitude and speed values displayed are wrong. This simulation automatically ends after 5 minutes.

The MP3 and WAV files provide sounds fot the simulation and should be kept in the same folder as the simulation files.

# The simulation

To control the aircraft:

- P: pitch up
- p: pitch down
- T: throttle up
- t: throttle down
- R: roll on one side
- r: roll on the other side

- S: start the simulation
- Escape: quit the simulation

Pitch and roll angles are displayed in degrees. Altitude is displayed in feet and the speed in meters per second.

Stall alarm will ring if there is too much pitch or roll, or if the speed is too low given the altitude.
Too low alarm will ring if the plane gets close to the ground with a too important vertical speed.

The current version of the simulator does not features landing or crash detection, it is simply made to fly and experiment the effect of pitch and throttle on the behavior of the plane.


 
