# BseriesOptimizor.py
this project can be used as a template to create an openscource Bseries Propellor optimization using the COIN module from amplpy and GEKKO based on ship resistance, speed, wake, thrust deduction and blade area coëfficiënt.  optimizing the number of blades; z the rotational speed; n diameter; D and pitch ratio: PD

################################################

# List of dependency's installed using PIP:
# make sure python 3 is installed

python --version
pip --version
pip install --upgrade pip

pip install gekko
python -m pip install amplpy

# make sure you have acces to these library's aswell:
> matplotlib
> os
> numpy

# place the txt in the same directory as the python file.
# change the # Fixed parameters and/or variable-bounds acording to you needs and it should be ready to run.

point of note:
the KT and KQ graph seems to be swapped. my guess is that the titles in the txt are swiched around. but this file was given to me from a third party, i maybe wrong here.
