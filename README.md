# BseriesOptimizor.py

done for the Minor [AETS](https://www.nhlstenden.com/minoren/advanced-engineering-tools-for-ShipX) at NHLstenden, Leeuwarden.

**BseriesOptimizor** is a template project for optimizing B-series propellers using Python. It leverages the optimization power of [AMPL's COIN module](https://amplpy.readthedocs.io/en/latest/modules/coin/) via `amplpy` and the dynamic modeling capabilities of `GEKKO`. The optimization is based on ship-specific parameters such as resistance, speed, wake, thrust deduction, and blade area coefficient.

This project is designed for open-source development and provides a flexible framework to explore and optimize key propeller design parameters, including:

- **Number of blades** (`z`)
- **Rotational speed** (`n`)
- **Diameter** (`D`)
- **Pitch ratio** (`P/D`)

resulting in a graph like this:
![graph_example](https://github.com/user-attachments/assets/20ad7f12-58fe-4e0d-8318-8aac217739ca)
or this, depending on the bounds:
![graph_example2](https://github.com/user-attachments/assets/113bb519-2555-4043-a1de-c6df24c7cc76)

---

## Dependencies

Ensure [Python 3](https://www.pythonguis.com/installation/install-python-windows/) is installed: 
- [matplotlib](https://pythonguides.com/how-to-install-matplotlib-python/)
- os (standard library)
- [numpy](https://numpy.org/install/)

use the bash below with pip for updating pip and installing GEKKO and AMPLYPY

```bash
python -m pip install --upgrade pip

python -m pip install gekko
python -m pip install amplpy
