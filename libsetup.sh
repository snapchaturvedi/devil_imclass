# Install pip3 (just if need be)
sudo apt install python3-pip --yes

# Libraries 
sudo apt install python3-gpiozero
sudo apt install python3-RPi.GPIO
sudo apt install python3-picamera
sudo apt install python3-numpy
python3 -m pip install tflite-runtime

# To resolve numpy conflict issue with tflite-runtime
sudo apt-get install libopenblas-dev --yes
