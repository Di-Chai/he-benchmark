FROM ubuntu:18.04

# Install python
RUN apt update && apt install -y python3 python3-pip wget vim libgmp3-dev libmpc-dev g++ make git python3-dev

# build the tf-wrapper and FedEval
RUN ln -s /usr/bin/python3 /usr/bin/python
RUN ln -s /usr/bin/pip3 /usr/bin/pip

# Install python requirements
RUN pip install setuptools numpy matplotlib gmpy2 phe

# Install cmake
WORKDIR /root/
RUN wget https://github.com/Kitware/CMake/releases/download/v3.18.0-rc1/cmake-3.18.0-rc1-Linux-x86_64.tar.gz
RUN tar -zxvf cmake-3.18.0-rc1-Linux-x86_64.tar.gz && mv cmake-3.18.0-rc1-Linux-x86_64 cmake
RUN ln -s /root/cmake/bin/* /usr/bin/ && cmake --version

RUN git clone https://github.com/Huelse/SEAL-Python.git
WORKDIR /root/SEAL-Python/SEAL/native/src
RUN cmake . && make
WORKDIR /root/SEAL-Python/
RUN pip install -r requirements.txt
RUN python setup.py install