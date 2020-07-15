FROM ubuntu:18.04

# Change the source of apt
RUN sed -i 's/archive.ubuntu.com/mirrors.ustc.edu.cn/g' /etc/apt/sources.list

# Install packages
RUN apt update && apt install -y python3 python3-pip wget vim libgmp3-dev libmpc-dev g++ make git python3-dev unzip

# Config ssh
RUN apt install -y openssh-server
RUN echo 'root:123456'|chpasswd
RUN mkdir -p /var/run/sshd
RUN sed -ri 's/^PermitRootLogin\s+.*/PermitRootLogin yes/' /etc/ssh/sshd_config
EXPOSE 22
CMD [ "sh", "-c", "service ssh start" ]

# build the tf-wrapper and FedEval
RUN ln -s /usr/bin/python3 /usr/bin/python
RUN ln -s /usr/bin/pip3 /usr/bin/pip

# Install python packages
RUN pip install setuptools numpy matplotlib gmpy2 phe psutil memory_profiler pympler \
    -i https://pypi.doubanio.com/simple --trusted-host pypi.doubanio.com

# Install cmake
WORKDIR /root/
RUN wget https://github.com/Kitware/CMake/releases/download/v3.18.0-rc1/cmake-3.18.0-rc1-Linux-x86_64.tar.gz
RUN tar -zxvf cmake-3.18.0-rc1-Linux-x86_64.tar.gz && mv cmake-3.18.0-rc1-Linux-x86_64 cmake
RUN ln -s /root/cmake/bin/* /usr/bin/ && cmake --version

# Install SEAL-Python
RUN git clone https://github.com/Huelse/SEAL-Python.git
WORKDIR /root/
RUN unzip SEAL-Python-master.zip
WORKDIR /root/SEAL-Python-master/SEAL/native/src
RUN cmake . && make
WORKDIR /root/SEAL-Python/
RUN pip install -r requirements.txt
RUN python setup.py install
