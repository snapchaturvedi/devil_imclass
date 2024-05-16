# Install pip3 (just if need be)
sudo apt install python3-pip --yes

# Libraries 
pip3 install gpiozero==1.6.2
pip3 install RPi.GPIO==0.7.0
pip3 install picamera==1.13
pip3 install numpy==1.26.4
pip3 install tflite-runtime==2.13.0

# To resolve numpy conflict issue with tflite-runtime
sudo apt-get install libopenblas-dev --yes

# Enable legacy camera
sudo raspi-config nonint do_legacy 0

# Reboot to enable camera
sudo reboot
