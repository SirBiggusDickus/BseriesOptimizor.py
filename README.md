# BseriesOptimizor.py

done for the Minor [AETS](https://www.nhlstenden.com/minoren/advanced-engineering-tools-for-ShipX) at NHLstenden, Leeuwarden.

**BseriesOptimizor** is a template project for optimizing B-series propellers using Python. It leverages the optimization power of [AMPL's COIN module](https://amplpy.readthedocs.io/en/latest/modules/coin/) via `amplpy` and the dynamic modeling capabilities of `GEKKO`. The optimization is based on ship-specific parameters such as resistance, speed, wake, thrust deduction, and blade area coefficient.

This project is designed for open-source development and provides a flexible framework to explore and optimize key propeller design parameters, including:

- **Number of blades** (`z`)
- **Rotational speed** (`n`)
- **Diameter** (`D`)
- **Pitch ratio** (`P/D`)

resulting in a graph like this:
![graph_example](https://github.com/user-attachments/assets/2aaa9689-d32f-49e5-9771-33c1abacb59b)

---

## Dependencies

Ensure Python 3 is installed:
- matplotlib
- os (standard library)
- numpy

point of note:
the KT and KQ graph seem to be swapped. my guess is that the titles in the txt are swiched around. but this file was given to me from a third party, i maybe wrong here.

```bash
python --version
pip --version
pip install --upgrade pip

pip install gekko
python -m pip install amplpy
