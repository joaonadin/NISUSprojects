import numpy as np

def get_vibration_parameters(a, b, k, c, If):
    """Get vibration parameters for the system."""
    omega_n = (a + b) * np.sqrt(k / If)
    zeta = c / (2 * (a + b) * np.sqrt(k * If))
    return omega_n, zeta

def get_C1_C2(omega_n, zeta, theta_eq, theta_0_dot):
    """Calculate constants C1 and C2 for all responses."""
    if zeta<1:  # underdamped
        omega_d = omega_n * np.sqrt(1 - zeta**2)
        C1 = -theta_eq
        C2 = 1 / omega_d * (theta_0_dot - omega_n * zeta * theta_eq)
    if zeta == 1:  # critically damped
        s = -omega_n
        C1 = theta_eq
        C2 = theta_0_dot - s * theta_eq
    else:  # overdamped
        s1 = -zeta * omega_n + omega_n * np.sqrt(zeta**2 - 1)
        s2 = -zeta * omega_n - omega_n * np.sqrt(zeta**2 - 1)
        C1 = (theta_0_dot + omega_n * s2 * theta_eq) / (omega_n * (s1 - s2))
        C2 = -(theta_0_dot + omega_n * s1 * theta_eq) / (omega_n * (s1 - s2))
    return C1, C2