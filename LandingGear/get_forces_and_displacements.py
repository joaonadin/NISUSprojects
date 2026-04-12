from constants import g

def get_F_trans(a, b, k, c, theta, theta_dot):
    """Transmitted force through the spring system."""
    F = (k * theta + c*theta_dot ) * (a+b)  # transmitted force through the spring system
    return F

def get_reaction_force(F_trans, m, theta_dot_dot):
    R = m * theta_dot_dot + m * g - F_trans
    return R

def get_displacement(F, k):
    """Calculate the vertical displacement of the system."""
    return F / k