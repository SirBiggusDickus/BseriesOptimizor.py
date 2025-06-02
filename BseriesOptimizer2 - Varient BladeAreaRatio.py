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

# Read in Bserie data

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

KT_coeffs, KT_powers, KQ_coeffs, KQ_powers = read_bserie_data()
if KT_coeffs is None or KQ_coeffs is None:
    raise Exception("Bserie data not found or invalid.")

m = GEKKO(remote=False)
#Variable Ranges
PD = m.Var(value=1.0, lb=0.5, ub=1.4)
D = m.Var(value=1.0, lb=0.1, ub=3.0)
n = m.Var(value=2.0, lb=1, ub=30.0)
AEA0 = m.Var(value=0.6, lb=0.3, ub=1.05)

Z_possible = [3, 4, 5]
Z_bin = [m.Var(value=0, lb=0, ub=1, integer=True) for _ in Z_possible]
Z = m.Var(value=4, lb=min(Z_possible), ub=max(Z_possible))
m.Equation(Z == m.sum([z * b for z, b in zip(Z_possible, Z_bin)]))
m.Equation(m.sum(Z_bin) == 1)

#Fixed Valiables
trust_deduction = 0.18
Wake = 0.3
KTS = 14
rho = 1025
propellers_aft = 2
Calm_water_resistance_on_speed = 390.26e3 / propellers_aft

#Calulatable Values
Vs = KTS * 1852.0 / 3600.0
Va = Vs * (1 - Wake)
P_required = Calm_water_resistance_on_speed * Vs

J = m.Intermediate(Va / (n * D))
KT_val = m.Intermediate(evaluate_bseries_polynomial(KT_coeffs, KT_powers, J, PD, AEA0, Z))
KQ_val = m.Intermediate(evaluate_bseries_polynomial(KQ_coeffs, KQ_powers, J, PD, AEA0, Z))

epsilon = 1e-9
eff = m.Intermediate((KT_val * J) / (2 * np.pi * KQ_val + epsilon))
power_eff = m.Intermediate((1 - trust_deduction)/(1 - Wake) * eff)

m.Obj(-power_eff)

T = m.Intermediate(KT_val * rho * D**4 * n**2)
P_towing = m.Intermediate(T * Va)
m.Equation(P_towing >= P_required)

#Solver
m.options.IMODE = 3
m.options.SOLVER_EXTENSION = "AMPLPY"
m.options.SOLVER = "bonmin"

m.solve(disp=True)

def plot_optimized_propeller_characteristics(PD_val, AEA0_val, Z_val, optimized_J, title):
    J_values = np.linspace(0.01, 1.5, 100)
    KT_values = [evaluate_bseries_polynomial(KT_coeffs, KT_powers, J, PD_val, AEA0_val, Z_val) for J in J_values]
    KQ_values = [evaluate_bseries_polynomial(KQ_coeffs, KQ_powers, J, PD_val, AEA0_val, Z_val) for J in J_values]
    eta0_values = [openwater_efficiency(KT, KQ, J) for KT, KQ, J in zip(KT_values, KQ_values, J_values)]

    plt.figure(figsize=(10, 6))
    plt.plot(J_values, KT_values, label="KT", color='b')
    plt.plot(J_values, [10 * KQ for KQ in KQ_values], label="10KQ", color='r')
    plt.plot(J_values, eta0_values, label="Efficiency (eta)", color='g')
    plt.axvline(x=optimized_J, color='k', linestyle='--', label=f'Optimized J = {optimized_J:.3f}')
    plt.xlabel("J (Advance Coefficient)")
    plt.ylabel("Value")
    plt.title(title)
    plt.legend()
    plt.grid(True)

    # Set fixed axis limits
    plt.xlim(0, 1.5)
    plt.ylim(0, 1.2)

    plt.show()

print("\nOptimized Result:")
print(f"Z: {Z.VALUE[0]:.0f} blades")
print(f"AEA0: {AEA0.VALUE[0]:.3f}")
print(f"PD: {PD.VALUE[0]:.3f}")
print(f"D: {D.VALUE[0]:.3f} m")
print(f"n: {n.VALUE[0] * 60:.1f} rpm")
print(f"J: {J.VALUE[0]:.3f}")
print(f"Openwater Efficiency: {power_eff.VALUE[0]:.4f}")
print(f"Total Delivered Towing Power: {2 * P_towing.VALUE[0]:.2f} Nm/s")

plot_optimized_propeller_characteristics(PD.VALUE[0], AEA0.VALUE[0], Z.VALUE[0], J.VALUE[0], "Optimized Propeller Characteristics")

# i understand now why wind-turbines are long, thin, and use 3 blades at a relatively low speed....
# too bad Cavitation exists.
# its probably why most props use ~0.6 Blade Area Ratio; AEA0.