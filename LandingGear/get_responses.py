import numpy as np

def get_underdamped_response(omega_n, zeta, theta_eq, theta_0_dot):
    omega_d = omega_n * np.sqrt(1 - zeta**2)
    C1 = -theta_eq
    C2 = 1 / omega_d * (theta_0_dot - omega_n * zeta * theta_eq)
    theta = lambda t: np.exp(-zeta * omega_n * t) * (C1 * np.cos(omega_d * t) + C2 * np.sin(omega_d * t)) + theta_eq
    theta_dot = lambda t: -zeta * omega_n * np.exp(-zeta * omega_n * t) * (C1 * np.cos(omega_d * t) + C2 * np.sin(omega_d * t)) + omega_d * np.exp(-zeta * omega_n * t) * (-C1 * np.sin(omega_d * t) + C2 * np.cos(omega_d * t))
    theta_dot_dot = lambda t: (zeta**2 * omega_n**2 * np.exp(-zeta * omega_n * t) * (C1 * np.cos(omega_d * t) + C2 * np.sin(omega_d * t)) -
                            2 * zeta * omega_n * omega_d * np.exp(-zeta * omega_n * t) * (-C1 * np.sin(omega_d * t) + C2 * np.cos(omega_d * t)) -
                            omega_d**2 * np.exp(-zeta * omega_n * t) * (C1 * np.cos(omega_d * t) + C2 * np.sin(omega_d * t)))
    return theta, theta_dot, theta_dot_dot

def get_overdamped_response(omega_n, zeta, theta_eq, theta_0_dot):
    s1 = -zeta * omega_n + omega_n * np.sqrt(zeta**2 - 1)
    s2 = -zeta * omega_n - omega_n * np.sqrt(zeta**2 - 1)
    C1 = (theta_0_dot + omega_n * s2 * theta_eq) / (omega_n * (s1 - s2))
    C2 = -(theta_0_dot + omega_n * s1 * theta_eq) / (omega_n * (s1 - s2))
    theta = lambda t: C1 * np.exp(s1 * t) + C2 * np.exp(s2 * t) + theta_eq
    theta_dot = lambda t: s1 * C1 * np.exp(s1 * t) + s2 * C2 * np.exp(s2 * t)
    theta_dot_dot = lambda t: s1**2 * C1 * np.exp(s1 * t) + s2**2 * C2 * np.exp(s2 * t)
    return theta, theta_dot, theta_dot_dot

def get_critically_damped_response(omega_n, theta_eq, theta_0_dot):
    s = -omega_n
    C1 = theta_eq
    C2 = theta_0_dot - s * theta_eq
    theta = lambda t: (C1 + C2 * t) * np.exp(s * t) + theta_eq
    theta_dot = lambda t: s * (C1 + C2 * t) * np.exp(s * t) + C2 * np.exp(s * t)
    theta_dot_dot = lambda t: s**2 * (C1 + C2 * t) * np.exp(s * t) + 2 * s * C2 * np.exp(s * t)
    return theta, theta_dot, theta_dot_dot
