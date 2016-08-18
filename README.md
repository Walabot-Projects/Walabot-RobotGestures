# RobotGestures - A Walabot Application

This is a simple Walabot application that allows you control a [Pololu DRV8835 Dual Motor Driver Kit](https://www.pololu.com/product/2753) through Walabot gestures.

* The code is written in Python and works on both Python 2 and Python 3.  
* The app was tested on Windows 10 and Ubuntu 16.04.  
* The app's using [Python library for the Pololu DRV8835 Dual Motor Driver Kit for Raspberry Pi.](https://github.com/pololu/drv8835-motor-driver-rpi)
* Connection to the Raspberry PI is achieved using [Paramiko.](http://www.paramiko.org/)

### What does the Walabot Do?

The app uses the Walabot sensor to detect a hand inside it's arena.  
The Z axis is used to control the driving speed.  
The Y axis is used to control the rotation speed.  

### How to use

1. Install the [Walabot SDK](http://walabot.com/getting-started) and the [WalabotAPI Python library](http://api.walabot.com/_pythonapi.html) using pip.
2. Install the [Paramiko library.](https://github.com/paramiko/paramiko/)
3. Install the [Python library for the Pololu DRV8835 Dual Motor Driver Kit for Raspberry Pi.](https://github.com/pololu/drv8835-motor-driver-rpi)
4. Configure the SSH settings in the code to match yours (lines 80-82 in `RobotGestures.py`).
5. Position the Walabot as the image below.
6. Run `RobotGestures.py` and start driving! :blue_car: :red_car: :taxi:

**IMPORTANT NOTE:** Current Walabot settings are for vMaker18.

##### Positioning the Walabot

![Positioning the Walabot](https://raw.githubusercontent.com/Walabot-Projects/Walabot-RobotGestures/master/example.png)

### Editing the code

'Walabot Settings' variables are necessary to configure the Walabot arena.  
'Raspberry PI Settings' variables are required to connect to the device over SSH.

##### Walabot Settings - the `Walabot` class

* `R_MIN, R_MAX, R_RES`: Walabot [`SetArenaR`](http://api.walabot.com/_walabot_a_p_i_8h.html#aac6cafa27c4a7d069dd64c903964632c) parameters. Determines how low (from it's location) the Walabot will "see".
* `THETA_MIN, THETA_MAX, THETA_RES`:  Walabot [`SetArenaTheta`](http://api.walabot.com/_walabot_a_p_i_8h.html#a3832f1466248274faadd6c23127b998d) parameters. The theta axis is ignored in this app, those values should always be the "lowest" possible.
* `PHI_MIN, PHI_MAX, PHI_RES`: Walabot [`SetArenaPhi`]((http://api.walabot.com/_walabot_a_p_i_8h.html#a9afb632b5cce965eba63b323bc579557)) parameters. Used to set how "far" the Walabot will "see" (from it's location).
* `THRESHOLD`: Walabot [`SetThreshold`](http://api.walabot.com/_walabot_a_p_i_8h.html#a4a19aa1afc64d7012392c5c91e43da15) parameter. Lower this value if you wish to detect objects smaller the a man's head.

A comprehensive explanation about the Walabot imaging features can be found [here](http://api.walabot.com/_features.html).

##### Raspberry PI Settings - the `RaspberryPi` class

* `HOST`: The Raspberry PI ip.
* `USERNAME`: The Raspberry PI OS username.
* `PASSWORD`: The Raspberry PI OS user's password.
