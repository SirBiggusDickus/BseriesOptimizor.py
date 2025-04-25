import numpy as np
from gekko import GEKKO
import amplpy.modules as ampymod
import matplotlib.pyplot as plt
import os

try:
    ampymod.install('coin')
    print("COIN module (including Bonmin) installed successfully.")
except Exception as e:
    print(f"Error installing COIN module: {e}")
    print("Make sure you have the necessary build tools and dependencies installed for amplpy modules.")

# Set working directory to the script's directory
working_directory = os.path.dirname(os.path.abspath(__file__))
os.chdir(working_directory)
print("Working directory set to:", os.getcwd())

# Read in Bserie data (same as before)
def read_bserie_data(filename="Bserie.txt"):
    try:
        with open(filename, 'r') as file:
            lines = file.readlines()
        data = {}
        section = None
        for line in lines:
            line = line.strip()
            if "KT coefficients" in line:
                section = "KT_coeffs"
                data[section] = []
            elif "KQ coefficients" in line:
                section = "KQ_coeffs"
                data[section] = []
            elif "KT powers" in line:
                section = "KT_powers"
                data[section] = []
            elif "KQ powers" in line:
                section = "KQ_powers"
                data[section] = []
            elif line:
                if section.endswith("coeffs"):
                    data[section].append(float(line))
                elif section.endswith("powers"):
                    data[section].append([int(x) for x in line.split()])
        return (np.array(data.get("KT_coeffs")), np.array(data.get("KT_powers")),
                np.array(data.get("KQ_coeffs")), np.array(data.get("KQ_powers")))
    except FileNotFoundError:
        print("Error: File 'Bserie.txt' not found in the current directory.")
        return None, None, None, None
    except Exception as e:
        print("An error occurred:", e)
        return None, None, None, None

def evaluate_bseries_polynomial(coeffs, powers, J, PD, AEA0, Z):
    result = 0.0
    for i, coeff in enumerate(coeffs):
        result += coeff * (J ** powers[i][0]) * (PD ** powers[i][1]) * (AEA0 ** powers[i][2]) * (Z ** powers[i][3])
    return result

def openwater_efficiency(KT, KQ, J):
    return 0.0 if (2 * np.pi * KQ) == 0 else (KT * J) / (2 * np.pi * KQ)

# Load the Bserie data
KT_coeffs, KT_powers, KQ_coeffs, KQ_powers = read_bserie_data()
if KT_coeffs is None or KQ_coeffs is None:
    raise Exception("Bserie data not found or invalid.")

# Create a GEKKO model instance
m = GEKKO(remote=False)

# Define decision variables with bounds
PD = m.Var(value=1.0, lb=0.5, ub=1.4)  #-
D  = m.Var(value=1.0, lb=0.1, ub=14.0) #m
n  = m.Var(value=2.0, lb=0.1, ub=10.0) #RPS
Z_possible_values = [2, 3, 4, 5, 6]    #Blades
Z_binary = [m.Var(value=0, lb=0, ub=1, integer=True) for _ in Z_possible_values]
Z = m.Var(value=4, lb=min(Z_possible_values), ub=max(Z_possible_values))

# Fixed parameters
AEA0_val = 0.6
trust_deduction = 0.18
Wake = 0.3
KTS = 15
rho = 1025
Calm_water_resistance_on_speed = 250e3

# Convert speed from knots to m/s and compute effective speed
Vs = KTS * 1852.0 / 3600.0
Va = Vs * (1 - Wake)

# Pre-calculate the required towing power (this formulation may be adjusted)
P_required = Calm_water_resistance_on_speed * Vs

# Define the advance coefficient J as an intermediate expression
J = m.Intermediate(Va / (n * D))

# Build the KT expression using the Bserie coefficients
KT_val = m.Intermediate(evaluate_bseries_polynomial(KT_coeffs, KT_powers, J, PD, AEA0_val, Z))

# Build the KQ expression similarly
KQ_val = m.Intermediate(evaluate_bseries_polynomial(KQ_coeffs, KQ_powers, J, PD, AEA0_val, Z))

# Define openwater efficiency
epsilon = 1e-9
eff = m.Intermediate((KT_val * J) / (2 * np.pi * KQ_val + epsilon))

# Calculate the power efficiency
power_eff = m.Intermediate((1 - trust_deduction)/(1 - Wake) * eff)

# Define the objective: maximize power efficiency (minimize its negative)
m.Obj(-power_eff)

# Compute thrust T and towing power P_towing
T = m.Intermediate(KT_val * rho * D**4 * n**2)
P_towing = m.Intermediate(T * Va)

# Add a constraint to ensure towing power is at least P_required
m.Equation(P_towing >= P_required)

# Constraint: Ensure Z takes only one of the allowed values
m.Equation(Z == m.sum([Z_possible_values[i] * Z_binary[i] for i in range(len(Z_possible_values))]))

# Constraint: Ensure only one binary variable is active (equal to 1)
m.Equation(m.sum(Z_binary) == 1)

# Set GEKKO options for steady-state optimization (IMODE=3)
m.options.IMODE = 3
m.options.SOLVER_EXTENSION = "AMPLPY"
m.options.SOLVER = "bonmin"

# Solve the optimization problem
m.solve(disp=True)

# Get optimized variable values
optimized_PD_val = PD.VALUE[0]
optimized_D = D.VALUE[0]
optimized_n = n.VALUE[0]
optimized_Z_val = Z.VALUE[0]
optimized_P_towing = P_towing.VALUE[0]

# --- Plotting Function for Optimized Propeller ---
def plot_optimized_propeller_characteristics(PD_val, AEA0_val, Z_val, optimized_J, title):
    J_values = np.linspace(0.01, 1.5, 100)
    KT_values = [evaluate_bseries_polynomial(KT_coeffs, KT_powers, J, PD_val, AEA0_val, Z_val) for J in J_values]
    KQ_values = [evaluate_bseries_polynomial(KQ_coeffs, KQ_powers, J, PD_val, AEA0_val, Z_val) for J in J_values]
    eta0_values = [openwater_efficiency(KT, KQ, J) for KT, KQ, J in zip(KT_values, KQ_values, J_values)]

    # Scale KQ for plotting only
    KQ10_values = [10 * KQ for KQ in KQ_values]

    plt.figure(figsize=(10, 6))
    plt.plot(J_values, KT_values, label="KT", color='b')
    plt.plot(J_values, KQ10_values, label="10KQ", color='r')
    plt.plot(J_values, eta0_values, label="Efficiency (eta)", color='g')
    # efficiency seems to include the wake and thrust deduction in this graph...?
    plt.xlabel("J (Advance Coefficient)")
    plt.ylabel("Value")
    plt.legend()
    plt.title(title)
    plt.grid(True)

    # Add a vertical line at the optimized J value
    plt.axvline(x=optimized_J, color='k', linestyle='--', label=f'Optimized J = {optimized_J:.3f}')
    plt.legend() # Show the label for the vertical line

    plt.show()

# Print optimized variable values
print("\nOptimized Variables:")
print("Openwater Efficiency;", power_eff.VALUE[0])
print("J :", J.VALUE[0])
print("PD:", optimized_PD_val)
print("D :", optimized_D, "m")
print("n :", optimized_n * 60, "rpm")
print("Z :", optimized_Z_val, "blades")
print("Delivered Towing Power:", optimized_P_towing, "Nm/s")

# Plot the characteristics of the optimized propeller
plot_optimized_propeller_characteristics(optimized_PD_val, AEA0_val, optimized_Z_val, J.VALUE[0], "Optimized Propeller Characteristics")
