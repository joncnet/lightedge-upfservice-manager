## build : docker build -t upfservice-runtime .
## run :   docker run --net=host --rm --privileged -it upfservice-runtime

FROM python:3.7-alpine
MAINTAINER Roberto Riggio <rriggio@fbk.eu>
RUN pip3 install tornado==6.0.3 pymodm==0.4.1 influxdb==5.2.3

# Fetching the latest repository from upfservice-runtime.
RUN wget https://github.com/lightedge/upfservice-runtime/archive/master.zip
RUN unzip master.zip
RUN rm master.zip
RUN ln -sf /upfservice-runtime-master/conf/ /etc/upfservice

# Run the controller
ENTRYPOINT ["/upfservice-runtime-master/upfservice-runtime.py"]

# Expose Web GUI
EXPOSE 8888

# Expose LVAPP Server
EXPOSE 4433

# Expose VBSP Server
EXPOSE 5533
