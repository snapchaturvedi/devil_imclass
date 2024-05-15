sudo apt-get install -y build-essential tk-dev libncurses5-dev libncursesw5-dev libreadline6-dev libdb5.3-dev libgdbm-dev libsqlite3-dev libssl-dev libbz2-dev libexpat1-dev liblzma-dev zlib1g-dev libffi-dev
wget https://www.python.org/ftp/python/3.9.2/Python-3.9.2.tgz`
sudo tar zxf Python-3.9.2.tgz
rm -r Python-3.9.2.tgz
cd Python-3.9.2
sudo ./configure --enable-optimizations
sudo make -j 4
sudo make altinstall
echo "alias python=/usr/local/bin/python3.9" >> ~/.bashrc
source ~/.bashrc
python3.9 -m pip install --upgrade pip
