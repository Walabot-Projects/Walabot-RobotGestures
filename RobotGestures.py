from __future__ import print_function, division
from math import radians, sin, pi
try: input = raw_input # python2-python3 compatibillity
except NameError: pass
import WalabotAPI
import paramiko

class Walabot:
    """ Designed to control the Walabot device.
    """

    def __init__(self):
        """ Set useful arena constants and load the Walabot SDK.
        """
        self.wlbt = WalabotAPI
        self.wlbt.Init()
        self.wlbt.SetSettingsFolder()
        self.R_MIN, self.R_MAX, self.R_RES = 5, 30, 1
        self.THETA_MIN, self.THETA_MAX, self.THETA_RES = -0, 20, 10
        self.PHI_MIN, self.PHI_MAX, self.PHI_RES = -30, 30, 1
        self.TSHLD = 40
        self.Y_MAX = self.R_MAX * sin(radians(self.PHI_MAX))
        self.ROTATE_RANGE = self.Y_MAX / 2
        self.DRIVE_RANGE = self.R_MAX * 7 / 8
        self.distance = lambda t: (t.xPosCm**2+t.yPosCm**2+t.zPosCm**2) ** 0.5

    def connect(self):
        """ Connect to a Walabot device. Prompt the user to connect one if
            it can't detect it.
        """
        while True:
            try:
                self.wlbt.ConnectAny()
            except self.wlbt.WalabotError as err:
                if err.code == 19: # 'WALABOT_INSTRUMENT_NOT_FOUND'
                    input("- Connect Walabot and press 'Enter'.")
            else:
                print('- Connection to Walabot established.')
                return

    def setParametersAndStart(self):
        """ Set the Walabot required parameters according to the constants.
            Then start the Walabot.
        """
        self.wlbt.SetProfile(self.wlbt.PROF_SENSOR)
        self.wlbt.SetArenaR(self.R_MIN, self.R_MAX, self.R_RES)
        self.wlbt.SetArenaTheta(self.THETA_MIN, self.THETA_MAX, self.THETA_RES)
        self.wlbt.SetArenaPhi(self.PHI_MIN, self.PHI_MAX, self.PHI_RES)
        self.wlbt.SetThreshold(self.TSHLD)
        self.wlbt.SetDynamicImageFilter(self.wlbt.FILTER_TYPE_MTI)
        self.wlbt.Start()
        print('- Walabot started.')

    def getClosestTarget(self):
        """ Trigger the Walabot and retrieve SensorTargets. Return the closest.
            Return:
                targets     Of SensorTarget type (from WalabotAPI).
        """
        self.wlbt.Trigger()
        targets = self.wlbt.GetSensorTargets()
        try:
            return max(targets, key=self.distance)
        except ValueError: # 'targets' is empty; no targets were found
            return None

    def stopAndDisconnect(self):
        """ Stop and disconnect from the Walabot device.
        """
        self.wlbt.Stop()
        self.wlbt.Disconnect()
        print('- Walabot stopped and disconnected.')

class RaspberryPi:
    """ Designed to control the Raspberry Pi.
    """

    def __init__(self):
        """ Set Raspberry Pi network information.
        """
        self.HOST = '192.168.1.39'
        self.USERNAME = 'pi'
        self.PASSWORD = 'raspberry'

    def connect(self):
        """ Connect to the Raspberry Pi over SHH using paramiko.
        """
        self.ssh = paramiko.SSHClient()
        self.ssh.load_system_host_keys()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        while True:
            try:
                self.ssh.connect(self.HOST, username=self.USERNAME,
                    password=self.PASSWORD)
                break
            except paramiko.ssh_exception.NoValidConnectionsError as sshError:
                input("- RaspPi connection failure. Press 'enter' to retry.")
        print('- Connection to RaspPi established.')

    def drive(self, speed):
        """ Send a command to the Raspberry Pi to drive the robot straight at
            a given speed.
            Arguments:
                speed       A number between -MAX_SPEED to MAX_SPEED.
        """
        command = 'sudo python -c "from pololu_drv8835_rpi import motors;'
        command += 'motors.setSpeeds({:.0f}, {:.0f})"'.format(speed, speed)
        self.ssh.exec_command(command)

    def rotate(self, speed):
        """ Send a command to the Raspberry Pi to rotate the robot at a given
            speed. Direction of rotation is according to the speed sign.
            Basically, the right motor get the opposite speed that the left
            motor get.
            Arguments:
                speed       A number between -MAX_SPEED to MAX_SPEED.
        """
        command = 'sudo python -c "from pololu_drv8835_rpi import motors;'
        command += 'motors.setSpeeds({:.0f}, {:.0f})"'.format(-speed, speed)
        self.ssh.exec_command(command)

    def stop(self):
        """ Send a command to the Raspberry Pi to set the robot speed to 0.
        """
        command = 'sudo python -c "from pololu_drv8835_rpi import motors;'
        command += 'motors.setSpeeds(0, 0)"'
        self.ssh.exec_command(command)

wlbt = Walabot()
raspPi  = RaspberryPi()

MAX_SPEED = 480 # according to Pololu DRV883 documentation

def moveRobotAccordingToTarget(target):
    """ Moves the robot according to the target location in the arena by a
        certain logic.
        If a target is at the sides of the Walabot's arena, the robot will
        rotate (proportionally to the target y-axis component).
        The middle area of the Walabot's arena is the 'drive section'. The
        speed that is given to the robot is proportional to the location of
        the target in the z-axis (closer to the Walabot - greater speed).
        If no target is found in the arena, the robot will stop.
    """
    if not target:
        raspPi.stop()
    elif abs(target.yPosCm) > wlbt.ROTATE_RANGE: # hand is at 'rotate section'
        raspPi.rotate(rotationSpeed(target.yPosCm))
    elif target.zPosCm < wlbt.DRIVE_RANGE: # hand is at 'drive section'
        raspPi.drive(drivingSpeed(target.zPosCm))
    else: # target is in the bottom-middle of arena
        raspPi.stop()

def drivingSpeed(z):
    return (1 - z / wlbt.DRIVE_RANGE) * MAX_SPEED * 2

def rotationSpeed(y):
    numerator = y - wlbt.ROTATE_RANGE if y > 0 else y + wlbt.ROTATE_RANGE
    return numerator / (wlbt.Y_MAX - wlbt.ROTATE_RANGE) * MAX_SPEED

def robotGestures():
    """ Main function. Initialize the Walabot device and the Raspberry PI,
        and send commands to the Raspberry PI according to the Walabot input.
    """
    wlbt.connect()
    wlbt.setParametersAndStart()
    raspPi.connect() # connect over SSH
    print('- Up and running! Start driving!')
    print("- Press 'CTRL-C' to terminate the app.")
    try:
        while True:
            moveRobotAccordingToTarget(wlbt.getClosestTarget())
    finally: # make sure to stop the robot on any case.
        raspPi.stop()
        wlbt.stopAndDisconnect()
        print('- Terminated successfully.')

if __name__ == '__main__':
    robotGestures()
