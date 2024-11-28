"""

Flight simulation inspired by the crash of the flight AP603.
Pilots of the flight AP630 were not able to control the plane because a technician forgot to remove covers on pressure sensors and crash the plane.
In this simulation, alarms start to ring 30 seconds after the start of the simulation and the on board computer will start to give wrong altitude and speed values after 45 seconds.

Authors: 
- Florian Topeza, 
- Arthur Jolivet

ISAE-SUPAERO, 2024

"""


import pygame
import tkinter as tk
import time
import random as rd
from tkinter import messagebox
from physics_engine import *
import math

## Environment constants

G = 9.81

## Plane constants

MASS = 100_000
NB_ENGINES = 2
ENGINE_THRUST = 180_000 # in N
WING_SURFACE = 180
STALL_ANGLE_DEG = 15
STALL_ANGLE = STALL_ANGLE_DEG * math.pi/180
CL_MAX = 1.3
STATIC_MARGIN = 0.05*5 # in meters

## Plane main variables

pitch = 5 * math.pi/180 #radian
pitch_deg = 5 # degrees
roll = 0 #radian
roll_deg = 0 #degrees
altitude = 1000 #metres
altitude_feet = 3000 #feet
heading = 0 #radian
heading_deg = 0 # degrees
vz = 0 #(vertical speed, m/s)
vx = 100 #(horizontal speed, m/s)
throttle = 0.5 #Between 0 and 1

## Plane computed variables
speed = 100
aoa = 0 #radian
cl = 0 
cd = 0 
thrust = 0
lift = 0
drag = 0
slope = 0

rho = 0

def compute_rho(alt):
    return 352.995 * (1-0.0000225577*alt)**5.25516 / (288.15 - 0.0065*alt)

def update_rho(alt):
    global rho
    rho = compute_rho(alt)

def update_speed():
    global speed
    speed = int(math.sqrt(vz**2 + vx**2))

def update_aoa():
    global aoa
    aoa = (pitch - math.asin(vz/speed))*math.cos(roll)

def compute_cl(aoa):
    
    passing_points_deg = [
        (0,0),
        (STALL_ANGLE_DEG,CL_MAX),
        (1.2*STALL_ANGLE_DEG,0.8),
        (40,0.8),
        (90,0)
    ]

    passing_point = [(p[0]*math.pi/180, p[1]) for p in passing_points_deg]

    if aoa < 0:
        return -compute_cl(-aoa)
    for i in range(1,len(passing_point)):
        (a,c) = passing_point[i]
        if aoa < a:
            (a0,c0) = passing_point[i-1]
            return (c-c0)/(a-a0)*(aoa-a0)+c0
        
    return 0

def update_cl(aoa):
    global cl
    cl = compute_cl(aoa)

def update_cd():
    global cd

    def polar(cl):
        return 0.02 + 0.06*cl**2

    if abs(aoa) < STALL_ANGLE:
        cd = polar(cl)
        return
    
    cd = (1.5-polar(CL_MAX))/(math.pi/2 - STALL_ANGLE)*(abs(aoa) - STALL_ANGLE) + polar(CL_MAX)

def update_thrust():
    global thrust
    thrust = NB_ENGINES * throttle * ENGINE_THRUST * rho / compute_rho(0)

def update_lift():
    global lift
    lift = 1/2 * rho * WING_SURFACE * speed**2 * cl

def update_drag():
    global drag
    drag = 1/2 * rho * WING_SURFACE * speed**2 * cd

def update_slope():
    global slope
    slope = pitch - aoa

## Plane variable update functions

def update_vz(dt):
    global vz
    vertical_force = (lift * math.cos(slope) - drag * math.sin(slope))*math.cos(roll) + thrust * math.sin(pitch) - MASS * G
    vz += vertical_force * dt / MASS

def update_altitude(dt):
    global altitude
    altitude += vz * dt

def update_altitude_feet():
    global altitude_feet
    altitude_feet = int(3*altitude)

def update_vx(dt):
    global vx
    horizontal_force = lift * -math.sin(slope) - drag * math.cos(slope) + thrust * math.cos(pitch)
    vx += horizontal_force * dt / MASS

def update_heading(dt):
    global heading, heading_deg
    heading += dt * STATIC_MARGIN * math.sin(roll) * lift
    
def heading_rad2deg():
    global heading_deg
    heading_deg = heading * 180 / math.pi

def pitch_deg2rad():
    global pitch
    pitch = pitch_deg * math.pi / 180

def roll_deg2rad():
    global roll
    roll = roll_deg * math.pi / 180

## General update function

def update_all(dt, alt, aoa): #dt is supposed to be small
    update_rho(alt)
    update_speed()
    update_aoa()
    update_cl(aoa)
    update_cd()
    update_thrust()
    update_lift()
    update_drag()
    update_slope()
    update_vz(dt)
    update_altitude(dt)
    update_altitude_feet()
    update_vx(dt)
    update_heading(dt)

# Initializing plane alarms
stall = False
too_low = False
wrong_altitude_and_speed_initiated = False

# Initializing simulation variables
start_time = 0
dt = 0.5
start = False

# Load the sounds
pygame.mixer.init()
alarm_too_low = pygame.mixer.Sound('too_low_alarm.wav')
alarm_stall = pygame.mixer.Sound('stall_alarm.wav')
airplane = pygame.mixer.Sound('airplane.mp3')

def airplane_sound():
    airplane.play()
    root.after(60000, airplane_sound)

too_low_time = 0

# Function to manage the too low alarm
def too_low_alarm():
    global too_low_time
    if too_low:
        too_low_dt = time.time() - too_low_time
        if too_low_dt > 2:
            too_low_time = time.time()
            alarm_too_low.play()
        status_label.config(text="STALL & PUSH DOWN", fg="red")

stall_time = 0

# Function to manage the stall alarm
def stall_alarm():
    global stall_time
    if (pitch_deg > STALL_ANGLE_DEG or pitch_deg < -STALL_ANGLE_DEG or roll_deg > 45 or roll_deg < -45 or speed < 50 or stall):
        stall_time_dt = time.time() - stall_time
        if stall_time_dt > 1.8:
            stall_time = time.time()
            alarm_stall.play()
        if not too_low:
            status_label.config(text="STALL", fg="red")
    else:
        alarm_stall.stop()
        if not too_low:
            status_label.config(text="Flight is nominal", fg="white")


# Function to update the simulation
def update():
    global stall, too_low
    if start:
        update_all(dt, altitude, aoa)
        too_low_alarm()
        stall_alarm()
        wrong_altitude_and_speed()
        too_low_warning()
        update_labels()
        elapsed_time = time.time() - start_time
        if elapsed_time > 60:
            stall = True
        if elapsed_time > 120:
            too_low = True
        if elapsed_time > 300:
            root.quit()
    root.after(100, update)


def too_low_warning():
    if too_low and altitude_feet < 500:
        too_low_frame = tk.Frame(root)
        too_low_label = tk.Label(too_low_frame, text="TOO LOW TERRAIN, PULL UP !", font=("Arial", 16), fg="red")
        too_low_frame.pack(pady=20)
        too_low_label.pack()

# Function to manage the wrong altitude and speed
def wrong_altitude_and_speed():
    global altitude_feet, speed, wrong_altitude_and_speed_initiated
    if too_low:
        if not wrong_altitude_and_speed_initiated:
            altitude_feet = 2500
            speed = 400
            wrong_altitude_and_speed_initiated = True
        
        delta_altitude = rd.randint(10, 40)
        altitude_feet += delta_altitude
        delta_speed = rd.randint(10, 20)
        speed += delta_speed

# Function to manage the key press
def on_key_press(event):
    global pitch_deg, roll_deg, throttle, start, start_time, stall_time
    if event.keysym == 'P':
        pitch_deg += 1
        pitch_deg2rad()
    elif event.keysym == 'p':
        pitch_deg -= 1
        pitch_deg2rad()
    elif event.keysym == 'R':
        roll_deg += 1
        roll_deg2rad()
    elif event.keysym == 'r':
        roll_deg -= 1
        roll_deg2rad()
    elif event.keysym == 'T':
        if throttle < 1:
            throttle = round(throttle + 0.01,2)
    elif event.keysym == 't':
        if throttle > 0.01:
            throttle = round(throttle - 0.01,2)
    elif event.keysym == 'S':
        start = True
        airplane_sound()
        start_time = time.time()
        stall_time = start_time
        too_low_time = start_time
    elif event.keysym == 'Escape':
        root.quit()

# Function to update the labels
def update_labels():
    pitch_label.config(text=f"Pitch: {pitch_deg}")
    roll_label.config(text=f"Roll: {roll_deg}")
    throttle_label.config(text=f"Throttle: {throttle}")
    altitude_label.config(text=f"Altitude: {altitude_feet}")
    speed_label.config(text=f"Speed: {speed}")


# Creating the graphical interface
root = tk.Tk()
root.title("Cockpit Simulation")
root.geometry("800x600")

status_label = tk.Label(root, text="Flight is nominal", font=("Helvetica", 16), bg="black", fg="white")
status_label.pack(pady=20)

# Frame for the indicators
indicators_frame = tk.Frame(root, bg="black", bd=2, relief=tk.SUNKEN)
indicators_frame.pack(pady=20, padx=20, fill=tk.X)

# Frame for the altitude
altitude_frame = tk.Frame(root, bg="black", bd=2, relief=tk.SUNKEN)
altitude_frame.pack(pady=20, padx=20, fill=tk.Y, side=tk.LEFT)

# Frame for the controls
controls_frame = tk.Frame()
controls_frame.pack(pady=20, padx=20, fill=tk.X, side=tk.RIGHT)

controls_label = tk.Label(controls_frame, text="Controls:\nP: Pitch up\np: Pitch down\nR: Roll up\nr: Roll down\nT: Throttle up\nt: Throttle down", font=("Arial", 10), bg="black", fg="white", justify=tk.LEFT)
controls_label.pack(pady=10)

# Labels for the indicators
pitch_label = tk.Label(indicators_frame, text=f"Pitch: {pitch_deg}", font=("Helvetica", 16), bg="black", fg="white")
pitch_label.pack(pady=10)

roll_label = tk.Label(indicators_frame, text=f"Roll: {roll_deg}", font=("Helvetica", 16), bg="black", fg="white")
roll_label.pack(pady=10)

throttle_label = tk.Label(indicators_frame, text=f"Throttle: {throttle}", font=("Helvetica", 16), bg="black", fg="white")
throttle_label.pack(pady=10)

# Labels for the altitude
altitude_label = tk.Label(altitude_frame, text=f"Altitude: {altitude_feet}", font=("Helvetica", 16), bg="black", fg="white")
altitude_label.pack(pady=10)

# Labels for the speed
speed_label = tk.Label(altitude_frame, text=f"Speed: {speed}", font=("Helvetica", 16), bg="black", fg="white")
speed_label.pack(pady=10)

# Binding the key press event
root.bind("<KeyPress>", on_key_press)

# Start the update function
update()

# Start the graphical interface
root.mainloop()