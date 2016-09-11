#Install pip
python get-pip.py

#apt-get
sudo apt-get install python-opengl mesa-common-dev libglu1-mesa-dev git python-setuptools libusb-1.0-0-dev cmake python-zmq python-dev python-opencv python-scipy python-pip libav-tools build-essential libglew-dev nasm pkg-config wget libopencv-dev
#Install ffmpeg
curl https://gist.githubusercontent.com/mkassner/1caa1b45c19521c884d5/raw/b5ce332808b8e26406af0db78115761ea605441c/install_ffmpeg_ubuntu.sh | bash

#Install glfw3
sudo apt-get install libxrandr-dev libxi-dev libxcursor-dev libxxf86vm-dev libxinerama-dev
cd ~/
git clone http://github.com/glfw/glfw
cd glfw/
git checkout tags/3.1.2
cmake -G "Unix Makefiles"  -DBUILD_SHARED_LIBS=TRUE
sudo make install
sudo ln -s /usr/local/lib/libglfw.so.3 /usr/lib/libglfw.so.3 
cd ../
sudo rm -r glfw

#Install libuvc
git clone https://github.com/pupil-labs/libuvc
cd libuvc
mkdir build
cd build
cmake ..
make && sudo make install

#Install libjpeg-turbo
sudo apt-get install nasm
wget -O libjpeg-turbo-1.3.90.tar.gz http://sourceforge.net/projects/libjpeg-turbo/files/1.3.90%20%281.4%20beta1%29/libjpeg-turbo-1.3.90.tar.gz/download
tar xvzf libjpeg-turbo-1.3.90.tar.gz
cd libjpeg-turbo-1.3.90
./configure --with-pic
sudo make install

#Install GLEW 
sudo apt-get install libglew-dev

#Install packages with pip
sudo pip install numexpr
sudo pip install cython
sudo pip install psutil
sudo pip install pyzmq
sudo pip install msgpack_python
sudo pip install git+https://github.com/zeromq/pyre
sudo -H pip install git+https://github.com/pupil-labs/PyAV
sudo -H pip install git+https://github.com/pupil-labs/pyuvc
sudo -H pip install git+https://github.com/pupil-labs/pyglui

#Install 3D eye model dependencies
sudo apt-get install libgoogle-glog-dev libatlas-base-dev libeigen3-dev
sudo add-apt-repository ppa:bzindovic/suitesparse-bugfix-1319687
sudo apt-get update
sudo apt-get install libsuitesparse-dev
# install ceres-solver
git clone https://ceres-solver.googlesource.com/ceres-solver
cd ceres-solver
mkdir build && cd build
cmake .. -DBUILD_SHARED_LIBS=ON 
make -j3
make test
sudo make install
sudo sh -c 'echo "/usr/local/lib" > /etc/ld.so.conf.d/ceres.conf'
sudo ldconfig
#we also need boost and boost-python bindings
sudo apt-get install libboost-dev
sudo apt-get install libboost-python-dev
