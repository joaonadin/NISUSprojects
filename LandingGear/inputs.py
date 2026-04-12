# Inputs
m = 10  # kg
v_stall = 10.79  # m/s
v_stall_y = 0.25 * v_stall
v0 = 1.1 * v_stall_y  # m/s
a = 0.138  # distance from front landing gear to center of mass (m)
b = 0.142  # distance from rear landing gear to center of mass (m)
Icg = 214416850 * 1e-3 * 1e-6  # convert from g*mm² to kg*m²
If = Icg + m * a**2  # moment of inertia of the system relative to front landing gear (kg·m²)
