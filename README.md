# 1. Flight configuration app
This project contains a Django-based web application that was designed to be embedded onto a edge device, such as nvidias Jetson TX2. 
It allows a person to 1) configure remotely edge device processing parameters, and 2) to view information produced by the deep learning suite mid-flight on a remote device through a browser.

The application was designed in the context of road monitoring research project. More information about the UAV-based monitoring system can be found in [PAPER LINK]

![alt text](https://github.com/SofiaTilon/flightconfig-webapp/blob/main/fig1.jpg?raw=true)

The figures below shows the landing page where users can set mission parameters that pertain to processes that need to be carried out mid-flight and on-board the edge-device
1) The flight organization (“Flightname”),
2) The deep learning suite, e.g. which models to execute (“Model”),
3) The on-board camera and its associated capturing protocol (“Camera”),
4) The name of the GCS (“Groundstation”),
5) Which information variables should be transmitted mid-flight (“Transfer”),
6) Whether these variables should be compressed (“Compressed”), or
7) Ancillary information (“Notes”).

![alt text](https://github.com/SofiaTilon/flightconfig-webapp/blob/main/fig4a.jpg?raw=true)
![alt text](https://github.com/SofiaTilon/flightconfig-webapp/blob/main/fig4b.jpg?raw=true)

# 2. Installation

Install the requirements file using conda
```
conda install --file requirements.txt
```
Install django following the instructions here: https://docs.djangoproject.com/en/4.0/topics/install/


# 3. How to use
The web application serves as a template for remote communication with your UAV embedded edge device. 
After installation, it can be connected to your own deep learning backend to show information relevant to your needs. 
Modifications should mainly be made the websockets residing in tx2/monitor/templates/monitor/flight_monitoring.html


