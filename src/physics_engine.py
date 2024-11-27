import math

# Environment constants
G = 9.81
RHO = 1.225

# Plane constants
MASS = 100_000
NB_ENGINES = 2
ENGINE_THRUST = 180_000

# Plane main variables
pitch = 0
roll = 0
speed = 200
altitude = 0
vz = 0 #(vertical speed)

# Plane computed variables
aoa = 0 # Angle of attack
def update_aoa():
    global aoa
    aoa = pitch - math.asin(vz/speed)

cl = 0 # Lift coefficient
def compute_cl(aoa):
    if aoa < 0:
        return -compute_cl(-aoa)
    if aoa < 12:
        return 1.3/12*aoa
    if aoa < 20:
        return -0.3/(20-12)*aoa + 20*(1 +0.3/(20-12))
    if aoa < 40:
        return 1
    return 1/50*(90-aoa)

def update_cl():
    global cl
    cl = compute_cl(aoa)    