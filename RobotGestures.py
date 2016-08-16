from __future__ import print_function, division
from imp import load_source
from os.path import join
from os import system
from math import radians, sin, pi
import paramiko

class Walabot:

    def __init__(self):
        wlbtPath = join('/usr', 'share', 'walabot', 'python')
        self.wlbt = load_source('WalabotAPI', join(wlbtPath, 'WalabotAPI.py'))
        self.wlbt.Init()
        self.wlbt.SetSettingsFolder()
        self.R_MIN, self.R_MAX, self.R_RES = 5, 40, 1
        self.THETA_MIN, self.THETA_MAX, self.THETA_RES = -20, 20, 10
        self.PHI_MIN, self.PHI_MAX, self.PHI_RES = -30, 30, 1
        self.TSHLD = 40
        self.Y_MAX = self.R_MAX * sin(radians(self.PHI_MAX))
        self.distance = lambda t: (t.xPosCm**2+t.yPosCm**2+t.zPosCm**2) ** 0.5

    def verifyThatConnected(self):
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
        self.wlbt.SetProfile(self.wlbt.PROF_SENSOR)
        self.wlbt.SetArenaR(self.R_MIN, self.R_MAX, self.R_RES)
        self.wlbt.SetArenaTheta(self.THETA_MIN, self.THETA_MAX, self.THETA_RES)
        self.wlbt.SetArenaPhi(self.PHI_MIN, self.PHI_MAX, self.PHI_RES)
        self.wlbt.SetThreshold(self.TSHLD)
        self.wlbt.SetDynamicImageFilter(self.wlbt.FILTER_TYPE_MTI)
        self.wlbt.Start()
        print('- Walabot started.')

    def getClosestTarget(self):
        self.wlbt.Trigger()
        targets = self.wlbt.GetSensorTargets()
        try:
            return max(targets, key=self.distance)
        except ValueError: # 'targets' is empty; no targets were found
            return None

    def stopAndDisconnect(self):
        self.wlbt.Stop()
        self.wlbt.Disconnect()
        print('- Walabot stopped and disconnected.')

class RaspberryPi:

    def __init__(self):
        self.HOST = '192.168.1.39'
        self.USER = 'pi'
        self.PSWRD = 'raspberry'

    def connect(self):
        self.ssh = paramiko.SSHClient()
        self.ssh.load_system_host_keys()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.ssh.connect(self.HOST, username=self.USER, password=self.PSWRD)
        print('- Connection to RaspPi established.')

    def drive(self, speed):
        command = 'sudo python -c "from pololu_drv8835_rpi import motors;'
        command += 'motors.setSpeeds({:.0f}, {:.0f})"'.format(speed, speed)
        self.ssh.exec_command(command)

    def rotate(self, speed):
        command = 'sudo python -c "from pololu_drv8835_rpi import motors;'
        command += 'motors.setSpeeds({:.0f}, {:.0f})"'.format(-speed, speed)
        self.ssh.exec_command(command)

    def stop(self):
        command = 'sudo python -c "from pololu_drv8835_rpi import motors;'
        command += 'motors.setSpeeds(0, 0)"'
        self.ssh.exec_command(command)

wlbt = Walabot()
raspPi  = RaspberryPi()

MAX_SPEED = 480 # according to Pololu DRV883 documentation

ROTATE_RANGE = wlbt.Y_MAX / 2
DRIVE_RANGE = wlbt.R_MAX * 7 / 8

def moveRobotAccordingToTarget(target):
    if not target:
        raspPi.stop()
    elif abs(target.yPosCm) > ROTATE_RANGE: # hand is at 'rotate section'
        raspPi.rotate(rotationSpeed(target.yPosCm))
    elif target.zPosCm < DRIVE_RANGE: # hand is at 'drive section'
        raspPi.drive(drivingSpeed(target.zPosCm))
    else: # target is in the middle of arena
        raspPi.stop()

def drivingSpeed(z):
    return (1 - z / DRIVE_RANGE) * MAX_SPEED * 2

def rotationSpeed(y):
    numerator = y - ROTATE_RANGE if y > 0 else y + ROTATE_RANGE
    return numerator / (wlbt.Y_MAX - ROTATE_RANGE) * MAX_SPEED

def robotGestures():
    wlbt.verifyThatConnected()
    wlbt.setParametersAndStart()
    raspPi.connect()
    try:
        while True:
            moveRobotAccordingToTarget(wlbt.getClosestTarget())
    finally:
        raspPi.stop()
        wlbt.stopAndDisconnect()

if __name__ == '__main__':
    robotGestures()
