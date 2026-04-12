import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import optimize_case
from get_responses import get_underdamped_response, get_overdamped_response, get_critically_damped_response
from get_initial_conditions import get_vibration_parameters
from get_forces_and_displacements import get_F_trans, get_reaction_force, get_displacement

# Use constants from optimize_case
m = optimize_case.m
g = optimize_case.g
v_stall = optimize_case.v_stall
v_stall_y = optimize_case.v_stall_y
v0 = optimize_case.v0
a = optimize_case.a
b = optimize_case.b
Icg = optimize_case.Icg
If = optimize_case.If

def evaluate_case_full(k, c, displacement_limit):
    """Evaluate a single case and return F_max and validity."""
    omega_n, zeta = get_vibration_parameters(a, b, k, c, If)
    
    # Equilibrium and initial conditions
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
    
    # Max values
    F_max = np.max(F)
    R_max = np.max(R)
    X_max = get_displacement(F_max, k)
    
    # Check constraints
    all_positive = np.all(F > 0) and np.all(R > 0)
    r_less_f_initial = R[0] < F[0]
    valid = all_positive and r_less_f_initial and (X_max < displacement_limit)
    
    return F_max, valid

# User inputs
k_min = 100
k_max = 5000
c_min = 5
c_max = 500
displacement_limit = 0.1
num_points = 80

# Create grid
k_vals = np.linspace(k_min, k_max, num_points)
c_vals = np.linspace(c_min, c_max, num_points)
K, C = np.meshgrid(k_vals, c_vals)

# Compute F_max and validity
F_max_grid = np.zeros_like(K)
valid_grid = np.zeros_like(K, dtype=bool)

for i in range(num_points):
    for j in range(num_points):
        k = K[i, j]
        c = C[i, j]
        F_max, valid = evaluate_case_full(k, c, displacement_limit)
        F_max_grid[i, j] = F_max
        valid_grid[i, j] = valid

# Flatten for plotting
k_flat = K.flatten()
c_flat = C.flatten()
F_max_flat = F_max_grid.flatten()
valid_flat = valid_grid.flatten()

# Separate valid and invalid
k_valid = k_flat[valid_flat]
c_valid = c_flat[valid_flat]
F_max_valid = F_max_flat[valid_flat]

k_invalid = k_flat[~valid_flat]
c_invalid = c_flat[~valid_flat]
F_max_invalid = F_max_flat[~valid_flat]

# 3D Plot
fig = plt.figure(figsize=(10, 8))
ax = fig.add_subplot(111, projection='3d')

# Plot invalid points in red
ax.scatter(k_invalid, c_invalid, F_max_invalid, c='red', label='Invalid', alpha=0.5, s=10)

# Plot valid points in green
ax.scatter(k_valid, c_valid, F_max_valid, c='green', label='Valid', alpha=0.8, s=20)

ax.set_xlabel('k (N/m)')
ax.set_ylabel('c (N·s/m)')
ax.set_zlabel('F_max (N)')
ax.set_title('Transmitted Force F_max vs k and c\nGreen: Valid regions')
ax.legend()

plt.show()