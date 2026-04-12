### input c and k values to compute F, R, and X over time

import numpy as np
from inputs import *
from constants import g
from get_forces_and_displacements import get_F_trans, get_reaction_force, get_displacement
from get_responses import get_underdamped_response, get_critically_damped_response, get_overdamped_response
from get_initial_conditions import get_vibration_parameters
import matplotlib.pyplot as plt

k, c = 4000, 45  # example values for testing
omega_n, zeta = get_vibration_parameters(a, b, k, c, If)

theta_eq = m * g * a / (k * (a + b)**2)  # equilibrium angle
theta_0_dot = v0 / (a + b)  # initial angular velocity

# Time vector with higher resolution at the beginning using log spacing
t = np.concatenate([[0], np.logspace(-3, np.log10(5), 199)])

if zeta < 1:
    damping_type = "underdamped"
    theta, theta_dot, theta_dot_dot = get_underdamped_response(omega_n, zeta, theta_eq, theta_0_dot)
elif zeta == 1:
    damping_type = "critically damped"
    theta, theta_dot, theta_dot_dot = get_critically_damped_response(omega_n, theta_eq, theta_0_dot)
else:  # overdamped
    damping_type = "overdamped"
    theta, theta_dot, theta_dot_dot = get_overdamped_response(omega_n, zeta, theta_eq, theta_0_dot)

# Compute forces
F = np.array([get_F_trans(a, b, k, c, theta(ti), theta_dot(ti)) for ti in t])
R = np.array([get_reaction_force(get_F_trans(a, b, k, c, theta(ti), theta_dot(ti)), m, theta_dot_dot(ti)) for ti in t])
X = np.array([get_displacement(Fi, k) for Fi in F])

plt.subplot(1,2,1)
plt.plot(t, F, label='Transmitted Force (F)')
plt.plot(t, R, label='Reaction Force (R)')
plt.xlabel('Time (s)')
plt.ylabel('Force')
plt.title('Landing Gear Vibration Analysis')
plt.legend()

plt.subplot(1,2,2)
plt.plot(t, X, label='Displacement (X)')
plt.xlabel('Time (s)')
plt.ylabel('Displacement')
plt.title('Landing Gear Vibration Analysis')
plt.legend()

plt.show()