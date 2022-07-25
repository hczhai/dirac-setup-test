build a wheel for https://gitlab.com/dirac/dirac.git

git clone --recursive https://gitlab.com/dirac/dirac.git .
git checkout v22.0

yum install -y libhdf5-dev

$PY_EXE -m pip install sphinx
export PATH=$PATH:/opt/python/cp37-cp37m/bin
sed -i "s/env python/env python3/g" pam.in
./setup --python=/opt/python/cp37-cp37m/bin/python3 build
cd build
make
cd ..