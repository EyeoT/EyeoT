# EyeoT
This is the code for a senior capstone project using the [Pupil Eye Tracker](pupil-labs.com).

##Set-up
The system is designed to be run on a Ubuntu 16.04 machine or on a VM using Vagrant with VirtualBox.

To install requirements on a vagrant machine vagrant:
```
git clone https://github.com/EyeoT/EyeoT.git
cd EyeoT
vagrant up
vagrant ssh
sudo bash setup_pupil.sh
```

If pupil device does not show up on vagrant machine, remove pupil from usb port and then reinsert.

To use pre-commit hooks, download [pre-commit by Yelp](http://www.pre-commit.com).
