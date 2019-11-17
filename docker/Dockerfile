## build : docker build -t upfservice-runtime .
## run :   docker run --net=host --rm --privileged -it upfservice-runtime

FROM ubuntu:19.10
MAINTAINER Roberto Riggio <rriggio@fbk.eu>

RUN apt update
RUN apt -y install python3-pip wget unzip
RUN pip3 install tornado==6.0.3 pymodm==0.4.1 influxdb==5.2.3 python-iptables==0.14.0

# Fetching the latest repository from upfservice-runtime.
RUN wget https://github.com/lightedge/lightedge-upfservice-manager/archive/master.zip
RUN unzip master.zip
RUN rm master.zip
RUN ln -sf /lightedge-upfservice-manager-master/conf/ /etc/upfservice
RUN mkdir -p /var/www/
RUN ln -sf /lightedge-upfservice-manager-master/webui/ /var/www/upfservice

# Run the controller
ENTRYPOINT ["python3.7", "/lightedge-upfservice-manager-master/upfservice-runtime.py"]

# Expose Web GUI
EXPOSE 8888
