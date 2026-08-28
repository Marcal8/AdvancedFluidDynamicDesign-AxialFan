import numpy as np

def ReynoldsNumber(U, c, nu):
    """ 
    Return Reynolds number given the velocity, chord length and kinematic viscosity
    """
    Re = U * c / nu
    print(f"Reynolds number: Re = {Re:.2e}")
    return Re

def velocityComponents(U,alpha):
    """ 
    Return velocity components given the magnitude and the incident angle
    """
    alpha = np.radians(alpha)
    u = U * np.cos(alpha)
    v = U * np.sin(alpha)
    print(f"Velocity components: u = {u:.3f} m/s, v = {v:.3f} m/s")
    return u, v

def get_forces_from_csv(file_path):
    """ 
    Return mean forces and their standard deviation from a CSV file
    """
    import pandas as pd
    df = pd.read_csv(file_path).tail(200) # We keep only the last 200 rows to avoid transient effects
    Fx = df['TOTAL_FORCE_X'].mean()
    Fy = df['TOTAL_FORCE_Y'].mean()
    Fx_err = 2 * df['TOTAL_FORCE_X'].std() # multiplying by 2 to get a 95% confidence interval
    Fy_err = 2 * df['TOTAL_FORCE_Y'].std()
    print(f"Mean forces: Fx = {Fx:.2f} N, Fy = {Fy:.2f} N")
    print(f"Standard deviation of forces: Fx_err = {Fx_err:.2g} N, Fy_err = {Fy_err:.2g} N")
    return Fx, Fy, Fx_err, Fy_err

def LiftDragCoefficients(Fx,Fy,Fx_err,Fy_err,U,rho,c,b,alpha):
    """ 
    Return lift and drag coefficients given the forces, velocity and incident angle
    """
    alpha = np.radians(alpha)
    eps_x = Fx_err / Fx if Fx != 0 else 0
    eps_y = Fy_err / Fy if Fy != 0 else 0
    L = Fy * np.cos(alpha) - Fx * np.sin(alpha)
    L_err = np.sqrt((eps_x * L)**2 + (eps_y * L)**2)
    D = Fx * np.cos(alpha) + Fy * np.sin(alpha)
    D_err = np.sqrt((eps_x * D)**2 + (eps_y * D)**2)
    Cl = 2 * L / (rho * U**2 * c * b)
    Cl_err = 2 * L_err / (rho * U**2 * c * b)
    Cd = 2 * D / (rho * U**2 * c * b)
    Cd_err = 2 * D_err / (rho * U**2 * c * b)
    print(f"Lift: L = {L:.2f} +/- {L_err:.2f} N")
    print(f"Drag: D = {D:.2f} +/- {D_err:.2f} N")
    print(f"Lift coefficient: Cl = {Cl:.4f} +/- {Cl_err:.4f}")
    print(f"Drag coefficient: Cd = {Cd:.4f} +/- {Cd_err:.4f}")
    return Cl, Cd, Cl_err, Cd_err

