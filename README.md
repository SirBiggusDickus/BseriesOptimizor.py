# BseriesOptimizor.py

**BseriesOptimizor** is a template project for optimizing B-series propellers using Python. It leverages the optimization power of [AMPL's COIN module](https://amplpy.readthedocs.io/en/latest/modules/coin/) via `amplpy` and the dynamic modeling capabilities of `GEKKO`. The optimization is based on ship-specific parameters such as resistance, speed, wake, thrust deduction, and blade area coefficient.

This project is designed for open-source development and provides a flexible framework to explore and optimize key propeller design parameters, including:

- **Number of blades** (`z`)
- **Rotational speed** (`n`)
- **Diameter** (`D`)
- **Pitch ratio** (`P/D`)

---

## Dependencies

Ensure Python 3 is installed:
- matplotlib
- os (standard library)
- numpy

```bash
python --version
pip --version
pip install --upgrade pip

pip install gekko
python -m pip install amplpy
