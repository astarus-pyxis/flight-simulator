"""

Flight simulation inspired by the crash of the flight AP603.
Pilots of the flight AP630 were not able to control the plane because a technician forgot to remove covers on pressure sensors and crash the plane.
In this simulation, alarms start to ring 30 seconds after the start of the simulation and the on board computer will start to give wrong altitude and speed values after 45 seconds.

Author: Florian Topeza, ISAE-SUPAERO, 2024

"""


import pygame
import tkinter as tk
import time
import random as rd
from tkinter import messagebox

# Initialising plane variables
pitch = 0
roll = 0
yaw = 0
speed = 200
altitude = 3000

# Initialiting plane alarms
stall = False
too_low = False
wrong_altitude_and_speed_initiated = False

# Initialiting simulation variables
start_time = 0
start = False

# Load the sounds
pygame.mixer.init()
alarm_too_low = pygame.mixer.Sound('too_low_alarm.wav')
alarm_stall = pygame.mixer.Sound('stall_alarm.wav')
airplane = pygame.mixer.Sound('airplane.mp3')

def airplane_sound():
    airplane.play()
    root.after(60000, airplane_sound)

# Function to manage the too low alarm
def too_low_alarm():
    if too_low:
        alarm_too_low.play()
        status_label.config(text="STALL & PUSH DOWN", fg="red")
        update_labels()


# Function to manage the stall alarm
def stall_alarm():
    if (pitch > 45 or pitch < -20 or roll > 45 or roll < -45 or yaw > 45 or yaw < -45 or speed < 100 or stall):
        alarm_stall.play()
        if not too_low:
            status_label.config(text="STALL", fg="red")
    else:
        alarm_stall.stop()
        if not too_low:
            status_label.config(text="Flight is nominal", fg="white")
    if stall:
        update_labels()


# Function to update the simulation
def update():
    global start_time, stall, too_low
    if start:
        too_low_alarm()
        stall_alarm()
        wrong_altitude_and_speed()
        too_low_warning()
        elapsed_time = time.time() - start_time
        if elapsed_time > 60:
            stall = True
        if elapsed_time > 120:
            too_low = True
        if elapsed_time > 300:
            root.quit()
    root.after(2000, update)


def too_low_warning():
    if too_low and altitude < 500:
        too_low_frame = tk.Frame(root)
        too_low_label = tk.Label(too_low_frame, text="TOO LOW TERRAIN, PULL UP !", font=("Arial", 16), fg="red")
        too_low_frame.pack(pady=20)
        too_low_label.pack()

# Function to manage the wrong altitude and speed
def wrong_altitude_and_speed():
    global altitude, speed, wrong_altitude_and_speed_initiated
    if too_low:
        if not wrong_altitude_and_speed_initiated:
            altitude = 2500
            speed = 400
            wrong_altitude_and_speed_initiated = True
        
        delta_altitude = rd.randint(-10, 0)
        altitude += delta_altitude
        delta_speed = rd.randint(0, 10)
        speed += delta_speed

# Function to manage the key press
def on_key_press(event):
    global pitch, roll, yaw, altitude, speed, cap, start, start_time
    if event.keysym == 'P':
        pitch += 1
    elif event.keysym == 'p':
        pitch -= 1
    elif event.keysym == 'R':
        roll += 1
    elif event.keysym == 'r':
        roll -= 1
    elif event.keysym == 'Y':
        yaw += 1
    elif event.keysym == 'y':
        yaw -= 1
    elif event.keysym == 'A':
        altitude += 50
    elif event.keysym == 'a':
        altitude -= 50
    elif event.keysym == 'T':
        speed += 10
    elif event.keysym == 't':
        speed -= 10
    elif event.keysym == 'C':
        cap += 1
    elif event.keysym == 'c':
        cap -=1  
    elif event.keysym == 'S':
        start = True
        airplane_sound()
        start_time = time.time()
    elif event.keysym == 'Escape':
        root.quit()
    update_labels()

# Function to update the labels
def update_labels():
    pitch_label.config(text=f"Pitch: {pitch}")
    roll_label.config(text=f"Roll: {roll}")
    yaw_label.config(text=f"Yaw: {yaw}")
    altitude_label.config(text=f"Altitude: {altitude}")
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

controls_label = tk.Label(controls_frame, text="Controls:\nP: Pitch up\np: Pitch down\nR: Roll up\nr: Roll down\nY: Yaw up\ny: Yaw down\nA: Altitude up\na: Altitude down\nT: Speed up\nt: Speed down", font=("Arial", 10), bg="black", fg="white", justify=tk.LEFT)
controls_label.pack(pady=10)

# Labels for the indicators
pitch_label = tk.Label(indicators_frame, text=f"Pitch: {pitch}", font=("Helvetica", 16), bg="black", fg="white")
pitch_label.pack(pady=10)

roll_label = tk.Label(indicators_frame, text=f"Roll: {roll}", font=("Helvetica", 16), bg="black", fg="white")
roll_label.pack(pady=10)

yaw_label = tk.Label(indicators_frame, text=f"Yaw: {yaw}", font=("Helvetica", 16), bg="black", fg="white")
yaw_label.pack(pady=10)

# Labels for the altitude
altitude_label = tk.Label(altitude_frame, text=f"Altitude: {altitude}", font=("Helvetica", 16), bg="black", fg="white")
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