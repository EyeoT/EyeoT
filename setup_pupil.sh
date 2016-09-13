python get-pip.py

URL=https://www.github.com/pupil-labs/pupil/releases/download/v0.8.4/pupil_capture_linux_os_x64_v0.8.4.deb
FILE=pupil_capture.deb
wget $URL -O $FILE

dpkg -i $FILE

pip install numpy
pip install pyzmq
pip install msgpack-python
