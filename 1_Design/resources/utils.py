def plot_velocity_triangle(U_vec, c_vec, title="Velocity Triangle"):
    """Plots a velocity triangle given U and c vectors. w is calculated automatically."""
    
    import matplotlib.pyplot as plt

    # Calculate w vector as the difference between c and U
    w_vec = [c_vec[0] - U_vec[0], c_vec[1] - U_vec[1]]
    
    plt.figure(figsize=(6,6))
    # Plot U (from origin)
    plt.quiver(0, 0, U_vec[0], U_vec[1], angles='xy', scale_units='xy', scale=1, color='green', label='U')
    # Plot c (from origin)
    plt.quiver(0, 0, c_vec[0], c_vec[1], angles='xy', scale_units='xy', scale=1, color='blue', label='c')
    # Plot w (starts at tip of U, ends at tip of c)
    plt.quiver(U_vec[0], U_vec[1], w_vec[0], w_vec[1], angles='xy', scale_units='xy', scale=1, color='red', label='w')
    
    plt.title(title)
    plt.axhline(0, color='black', linewidth=0.5)
    plt.axvline(0, color='black', linewidth=0.5)
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.legend()
    plt.axis('equal')
    plt.show()


def naca65_thickness(x, thickness_ratio):
    """NACA 65-series thickness distribution"""
    import numpy as np
    # Coefficients for NACA 65-series thickness distribution
    a0 = 0.2969
    a1 = -0.1260
    a2 = -0.3516
    a3 = 0.2843
    a4 = -0.1015
    return (thickness_ratio/0.2) * (a0*np.sqrt(x) + a1*x + a2*x**2 + a3*x**3 + a4*x**4)