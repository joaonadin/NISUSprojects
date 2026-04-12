import numpy as np
from scipy.optimize import brute
import matplotlib.pyplot as plt
from get_responses import get_underdamped_response, get_overdamped_response, get_critically_damped_response
from get_forces_and_displacements import get_F_trans, get_reaction_force, get_displacement
from get_initial_conditions import get_vibration_parameters
from inputs import *
from constants import g

def evaluate_case(x):
    """Evaluate a single case and return F_max if valid, else inf."""
    k, c = x
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
    
    # Check constraints
    all_positive = np.all(F > 0) and np.all(R > 0)
    r_less_f_initial = R[0] < F[0]
    F_max = np.max(F)
    X_max = get_displacement(F_max, k)
    
    if all_positive and r_less_f_initial and X_max < displacement_limit:
        return F_max
    else:
        return np.inf

if __name__ == "__main__":
    
    # User inputs
    k_min = 100
    k_max = 5000
    c_min = 5
    c_max = 500
    displacement_limit = 0.1

    # Optimization using brute force grid search
    ranges = [(k_min, k_max), (c_min, c_max)]
    Ns = 50  # number of points per dimension

    result = brute(evaluate_case, ranges, Ns=Ns, full_output=True, finish=None)

    optimal_k, optimal_c = result[0]
    min_F_max = result[1]

    if min_F_max == np.inf:
        print("No valid combination found within the constraints.")
    else:
        print(f"Optimal k: {optimal_k:.2f} N/m")
        print(f"Optimal c: {optimal_c:.2f} N·s/m")
        print(f"Min F_max: {min_F_max:.2f} N")
        
        # Re-evaluate to get other values
        omega_n, zeta = get_vibration_parameters(a, b, optimal_k, optimal_c, If)
        theta_eq = m * g * a / (optimal_k * (a + b)**2)
        theta_0_dot = v0 / (a + b)
        t = np.concatenate([[0], np.logspace(-3, np.log10(5), 199)])
        
        if zeta < 1:
            theta, theta_dot, theta_dot_dot = get_underdamped_response(omega_n, zeta, theta_eq, theta_0_dot)
        elif zeta == 1:
            theta, theta_dot, theta_dot_dot = get_critically_damped_response(omega_n, theta_eq, theta_0_dot)
        else:
            theta, theta_dot, theta_dot_dot = get_overdamped_response(omega_n, zeta, theta_eq, theta_0_dot)
        
        F = np.array([get_F_trans(a, b, optimal_k, optimal_c,  theta(ti), theta_dot(ti)) for ti in t])
        R = np.array([get_reaction_force(get_F_trans(a, b, optimal_k, optimal_c, theta(ti), theta_dot(ti)), m, theta_dot_dot(ti)) for ti in t])
        
        R_max = np.max(R)
        X_max = get_displacement(min_F_max, optimal_k)
        
        print(f"R_max: {R_max:.2f} N")
        print(f"X_max: {X_max:.2f} m")
        print(f"Damping ratio zeta: {zeta:.3f}")

        plt.subplot(1,2,1)
        plt.plot(t, F, label='Transmitted Force F(t)', marker='o', markersize=3)
        plt.plot(t, R, label='Reaction Force R(t)', marker='s', markersize=3)
        plt.xlabel('Time (s)')
        plt.ylabel('Force (N)')
        plt.title('Force vs. Time for Optimal Parameters')
        plt.legend()

        plt.subplot(1,2,2)
        plt.plot(t, (a+b)*theta(t), label='X(t)', marker='^', markersize=3)
        plt.xlabel('Time (s)')
        plt.ylabel('Displacement (m)')
        plt.title('Displacement vs. Time for Optimal Parameters')
        plt.legend()
        plt.show()