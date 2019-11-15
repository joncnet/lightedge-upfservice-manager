## build : docker build -t upfservice-runtime .
## run :   docker run --net=host --rm --privileged -it upfservice-runtime

FROM ubuntu:18.04
MAINTAINER Roberto Riggio <rriggio@fbk.eu>

RUN apt update
RUN apt install -y git software-properties-common build-essential curl wget unzip iptables
RUN add-apt-repository -y ppa:deadsnakes/ppa
RUN apt install -y python3.7
RUN curl "https://bootstrap.pypa.io/get-pip.py" -o "get-pip.py"
RUN python3.7 get-pip.py

RUN python3.7 -m pip install tornado==6.0.3 pymodm==0.4.1 influxdb==5.2.3 python-iptables==0.14.0

# Fetching the latest repository from upfservice-runtime.
RUN wget https://github.com/lightedge/lightedge-upfservice/archive/master.zip
RUN unzip master.zip
RUN rm master.zip
RUN ln -sf /lightedge-upfservice-master/conf/ /etc/upfservice

# Run the controller
ENTRYPOINT ["python3.7", "/lightedge-upfservice-master/upfservice-runtime.py"]

# Expose Web GUI
EXPOSE 8888

# Expose LVAPP Server
EXPOSE 4433

# Expose VBSP Server
EXPOSE 5533
