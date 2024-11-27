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

pitch = 12 * math.pi/180 #radian
roll = 0 #radian
altitude = 0 #metres
heading = 0 #radian
vz = 0 #(vertical speed, m/s)
vx = 100 #(horizontal speed, m/s)
throttle = 1 #Between 0 and 1

## Plane computed variables
speed = 0
aoa = 0 #radian
cl = 0 
cd = 0 
thrust = 0
lift = 0
drag = 0
slope = 0

rho = 0

def compute_rho(altitude):
    return 352.995 * (1-0.0000225577*altitude)**5.25516 / (288.15 - 0.0065*altitude)

def update_rho():
    global rho
    rho = compute_rho(altitude)

def update_speed():
    global speed
    speed = math.sqrt(vz**2 + vx**2)

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

def update_cl():
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

def update_vx(dt):
    global vx
    horizontal_force = lift * -math.sin(slope) - drag * math.cos(slope) + thrust * math.cos(pitch)
    vx += horizontal_force * dt / MASS

def update_heading(dt):
    global heading
    heading += dt * STATIC_MARGIN * math.sin(roll) * lift

## General update function

def update(dt): #dt is supposed to be small
    update_rho()
    update_speed()
    update_aoa()
    update_cl()
    update_cd()
    update_thrust()
    update_lift()
    update_drag()
    update_slope()
    update_vz(dt)
    update_altitude(dt)
    update_vx(dt)
    update_heading(dt)


## Tests

import matplotlib.pyplot as plt

# # Cl Cd curves

# old_aoa = aoa
# aoa = -math.pi/2
# alpha = [i/10 for i in range(-900,900)]
# l = []
# d = []
# for i in alpha:
#     aoa = i * math.pi/180
#     update_cd()
#     update_cl()
#     l.append(cl)
#     d.append(cd)
# aoa = old_aoa

# plt.figure()
# plt.plot(alpha, l)
# plt.plot(alpha, d)
# plt.show()

# # Simulation

# duration = 6000
# dt = 0.1

# time = [i*dt for i in range(int(duration/dt))]
# altitude_r = []
# speed_r = []
# thrust_r = []
# vz_r = []
# vx_r = []
# aoa_r = []
# slope_r = []
# cl_r = []
# cd_r = []
# lift_r = []
# drag_r = []
# for t in time:
#     update(dt)
#     altitude_r.append(altitude)
#     speed_r.append(speed)
#     thrust_r.append(thrust)
#     vz_r.append(vz)
#     vx_r.append(vx)
#     aoa_r.append(aoa)
#     slope_r.append(slope)
#     cl_r.append(cl)
#     cd_r.append(cd)
#     lift_r.append(lift)
#     drag_r.append(drag)

# print_index = 0

# print("altitude", altitude_r[print_index])
# print("speed", speed_r[print_index])
# print("thrust", thrust_r[print_index])
# print("vz", vz_r[print_index])
# print("vx", vx_r[0])
# print("aoa", aoa_r[print_index])
# print("slope", slope_r[print_index])
# print("cl", cl_r[print_index])
# print("cd", cd_r[print_index])
# print("lift", lift_r[print_index])
# print("drag", drag_r[print_index])

# start_,stop_ = 0,duration #175,175.7
# start,stop = int(start_/dt),int(stop_/dt)

# plt.figure("altitude")
# plt.plot(time[start:stop],altitude_r[start:stop])
# plt.figure("speed")
# plt.plot(time[start:stop],speed_r[start:stop])
# plt.figure("thrust")
# plt.plot(time[start:stop],thrust_r[start:stop])
# plt.figure("vz")
# plt.plot(time[start:stop],vz_r[start:stop])
# plt.figure("vx")
# plt.plot(time[start:stop],vx_r[start:stop])
# plt.figure("angle of attack")
# plt.plot(time[start:stop],aoa_r[start:stop])
# plt.figure("slope")
# plt.plot(time[start:stop],slope_r[start:stop])
# plt.figure("cl, cd")
# plt.plot(time[start:stop], cl_r[start:stop])
# plt.plot(time[start:stop], cd_r[start:stop])
# plt.figure("lift")
# plt.plot(time[start:stop], lift_r[start:stop])
# plt.figure("drag")
# plt.plot(time[start:stop], drag_r[start:stop])
# plt.show()