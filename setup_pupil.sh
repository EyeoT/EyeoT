# install pip from the get-pip.py
python get-pip.py

# install python dev tools
apt-get install python-dev

# getting the pupil capture debian file
URL=https://www.github.com/pupil-labs/pupil/releases/download/v0.8.4/pupil_capture_linux_os_x64_v0.8.4.deb
FILE=pupil_capture.deb
wget $URL -O $FILE

# installing the pupil capture debian file
dpkg -i $FILE

# install some python dependencies
pip install numpy
pip install pyzmq
pip install msgpack-python

# install dependencies for pyglui
pip install cython
apt-get install libglew-dev

# install pyglui
cd ~/
git clone http://github.com/pupil-labs/pyglui --recursive
cd pyglui
sudo python setup.py install
