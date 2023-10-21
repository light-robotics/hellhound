import math
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import configs.kinematics_config as cfg
from cybernetic_core.geometry.lines import Point

a = cfg.leg.a
b = cfg.leg.b

d = cfg.leg.d
d2 = cfg.leg.d2


def leg_angles(Cx: float, Cy: float) -> [float, float]:
    dist = math.sqrt(Cx ** 2 + Cy ** 2)

    alpha1 = math.acos((a ** 2 + dist ** 2 - b ** 2) / (2 * a * dist))
    beta1 = math.acos((a ** 2 + b ** 2 - dist ** 2) / (2 * a * b))
    #beta = -1 * (math.pi - beta1)
    beta = math.pi - beta1

    alpha2 = math.atan2(Cy, Cx)
    alpha = alpha1 + alpha2

    return math.degrees(alpha), math.degrees(beta)

    Bx = a * math.cos(alpha)
    By = a * math.sin(alpha)

    Cx = Bx + b * math.cos(alpha + beta)
    Cy = By + b * math.sin(alpha + beta)

    print(f'alpha: {math.degrees(alpha)}')
    print(f'beta : {math.degrees(beta)}')
    print(f'B: {[Bx, By]}. C: {[Cx, Cy]}')




def get_knee_angles(Cx, Cz):
    Cz = Cz - d2
    dist = math.sqrt(Cx ** 2 + Cz ** 2)

    alpha1 = math.acos((a ** 2 + dist ** 2 - b ** 2) / (2 * a * dist))
    beta1 = math.acos((a ** 2 + b ** 2 - dist ** 2) / (2 * a * b))
    beta = math.pi - beta1

    alpha2 = math.atan2(Cx, Cz)
    alpha = alpha1 + alpha2

    Bx = a * math.cos(alpha)
    By = a * math.sin(alpha)

    Cx = Bx + b * math.cos(alpha + beta)
    Cy = By + b * math.sin(alpha + beta)

    #print(f'alpha: {math.degrees(alpha)}')
    #print(f'beta : {math.degrees(beta)}')
    #print(f'B: {[Bx, By]}. C: {[Cx, Cy]}')

    return alpha, beta

def get_leg_angles(Cx, Cy, Cz):
    # hip joint operates in Cy, Cz plane
    # the rest of the leg operates in Cx, Cz plane

    l_hip = math.sqrt(Cy**2 + Cz**2)

    gamma1 = math.asin(Cy/l_hip)
    gamma2 = math.acos(d/l_hip)
    gamma = gamma1 + gamma2 - math.pi/2

    Cz_adapted = Cz / math.cos(gamma)

    alpha, beta = get_knee_angles(Cx, Cz_adapted)

    return [
        round(math.degrees(gamma), 2), 
        round(math.degrees(alpha), 2), 
        round(math.degrees(beta), 2)]

def calculate_leg_angles(O: Point, C: Point):
    return get_leg_angles(O.x - C.x, O.y - C.y, O.z - C.z)
