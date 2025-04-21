Files and folders to setup the "devil detector" onto a Raspberry Pi (tested on 3B+ and Zero 2W)

# Setup
## Use Raspberry Pi Bullseye (Legacy 32-bit) Lite OS to get Python 3.9 by default
1. ```sudo apt update``` 
2.	```sudo apt upgrade --yes```
3.	Install git: ```sudo apt install git-all --yes```
4.	Clone this Github repository: ```git clone https://github.com/snapchaturvedi/devil_imclass.git```
5.	Run shell script: ```bash devil_imclass/libsetup.sh```

##### Downgrade/upgrade to Python3 V3.9 if other OS flavours used:
1.	Download all packages required: ```sudo apt-get install -y build-essential tk-dev libncurses5-dev libncursesw5-dev libreadline6-dev libdb5.3-dev libgdbm-dev libsqlite3-dev libssl-dev libbz2-dev libexpat1-dev liblzma-dev zlib1g-dev libffi-dev```
2.	Download python3.9: ```wget https://www.python.org/ftp/python/3.9/Python-3.9.tgz```
3.	Unzip: ```sudo tar zxf Python-3.9.tgz```
4.	Go to dir: ```cd Python-3.9```
5.	```sudo ./configure --enable-optimizations```
6.	```sudo make -j 4```
7.	```sudo make altinstall```
8.	Change alias name to ```python3```: ```echo "alias python3=/usr/local/bin/python3.9" >> ~/.bashrc```
9.	```source ~/.bashrc```
10.	```python3.9 -m pip install --upgrade pip```
11.	```sudo apt-get install python3-pip```
12.	```sudo reboot```
13. ```sudo apt-get remove python3.11```
14.	```sudo apt-get remove python3-numpy```
15.	```pip3 install numpy```
16.	```sudo apt-get install libopenblas-dev``` # for numpy
17.	```pip3 install tflite-runtime```
18.	```sudo apt-get install libpcap-dev``` # for picamera2
19.	```pip3 install picamera2```
20. ```sudo reboot```
