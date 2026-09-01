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

def compute_bulk_beta2_from_distribution(y, W2x, W2y):
    """
    Computes the bulk representative outlet flow angle (beta2) from the spatial 
    distributions of axial (W2x) and tangential (W2y) velocities across the pitch.
    
    It uses mass-flow weighted averaging of the individual velocity components:
        W2x_mass = integral(W2x^2 dy) / integral(W2x dy)
        W2y_mass = integral(W2y * W2x dy) / integral(W2x dy)
        beta2 = arctan(W2y_mass / W2x_mass)
        
    Parameters:
    -----------
    y : array_like
        Pitchwise coordinate array [m] (e.g. from -0.06 to 0.06).
    W2x : array_like
        Axial velocity distribution array [m/s] (weighting factor).
    W2y : array_like
        Relative tangential velocity distribution array [m/s].
        
    Returns:
    --------
    beta2 : float
        The bulk mass-weighted outlet flow angle.
    W2x_mass : float
        The bulk mass-weighted axial velocity component.
    W2y_mass : float
        The bulk mass-weighted tangential velocity component.
    """
    from scipy.integrate import trapezoid
    # Convert inputs to numpy arrays to ensure vector math
    y = np.asarray(y)
    W2x = np.asarray(W2x)
    W2y = np.asarray(W2y)
    
    # 1. Compute the common denominator: integral(W2x dy)
    den = trapezoid(W2x, y)
    
    # 2. Compute mass-weighted velocity components
    W2x_mass = trapezoid(W2x * W2x, y) / den
    W2y_mass = trapezoid(W2y * W2x, y) / den
    
    # 3. Compute the bulk representative angle using arctan2 for safety
    beta2_rad = np.arctan2(W2y_mass, W2x_mass)
    beta2_deg = np.degrees(beta2_rad)

    print(f"Computed bulk mass-weighted outlet flow angle: beta2 = {beta2_deg:.2f} degrees")
    print(f"Computed bulk mass-weighted axial velocity: W2x_mass = {W2x_mass:.2f} m/s")
    print(f"Computed bulk mass-weighted tangential velocity: W2y_mass = {W2y_mass:.2f} m/s")
    
    return beta2_deg, W2x_mass, W2y_mass

def compute_cascade_coefficients(F_x, F_y, c_x, U_y1, rho, s, l, b, beta_2):
    """
    Computes the Lift and Drag coefficients (C_L, C_D) for a 2D turbomachinery cascade.
    
    Parameters:
    -----------
    F_x : float
        Axial force on the blade (N). Typically negative (thrust opposing flow).
    F_y : float
        Tangential force on the blade (N).
    c_x : float
        Axial velocity component (m/s). Constant across the cascade.
    U_y1 : float
        Inlet tangential velocity component (m/s).
    rho : float
        Fluid density (kg/m^3).
    s : float
        Blade spacing / pitch (m).
    l : float
        Blade chord length (m).
    b : float
        Blade span / extrusion thickness (m).
    beta_2 : float
        Directly measured outlet relative flow angle (degrees) from post-processing.
    """
    # 1. Calculate relative inlet flow angle (beta_1)
    beta_1 = np.arctan(U_y1 / c_x)
    
    # 2. Determine relative outlet flow angle (beta_2)
    beta_2 = np.radians(beta_2)
    W_y2 = c_x * np.tan(beta_2)
    
    # 3. Compute mean flow angle (beta_m)
    tan_beta_m = 0.5 * (np.tan(beta_1) + np.tan(beta_2))
    beta_m = np.arctan(tan_beta_m)
    
    # 4. Compute mean relative velocity (W_m)
    W_m = c_x / np.cos(beta_m)
        
    # 3. Compute mean flow angle (beta_m)
    tan_beta_m = 0.5 * (np.tan(beta_1) + np.tan(beta_2))
    beta_m = np.arctan(tan_beta_m)
    
    # 4. Compute mean relative velocity (W_m)
    W_m = c_x / np.cos(beta_m)
    
    # 5. Resolve forces along the mean flow direction (Lift & Drag)
    L = F_y * np.cos(beta_m) - F_x * np.sin(beta_m)
    D = F_y * np.sin(beta_m) + F_x * np.cos(beta_m)
    
    # 6. Compute coefficients based on mean relative dynamic pressure
    q = 0.5 * rho * (W_m**2) * l * b
    C_L = L / q
    C_D = D / q

    sigma = l / s
    DF = (1-np.cos(beta_1)/np.cos(beta_2)) + 0.5 / sigma * np.cos(beta_1) * (np.tan(beta_1) - np.tan(beta_2)) 
    
    return {
        'beta_1_deg': np.degrees(beta_1),
        'beta_2_deg': np.degrees(beta_2),
        'beta_m_deg': np.degrees(beta_m),
        'W_m': W_m,
        'L_force': L,
        'D_force': D,
        'C_L': C_L,
        'C_D': C_D,
        'DF': DF
    }