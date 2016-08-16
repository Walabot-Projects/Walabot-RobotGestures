from __future__ import print_function, division
from imp import load_source
from os.path import join
from math import radians, sin, radians
import paramiko

HOST = '192.168.1.39'
USERNAME = 'pi'
PASSWORD = 'raspberry'

MAX_SPEED = 480 # according to Pololu DRV883 documentation
distance = lambda t: (t.xPosCm**2 + t.yPosCm**2 + t.zPosCm**2) ** 0.5

R_MIN, R_MAX, R_RES = 5, 40, 1
THETA_MIN, THETA_MAX, THETA_RES = -10, 10, 10
PHI_MIN, PHI_MAX, PHI_RES = -30, 30, 1
TSHLD = 40

Y_MAX = R_MAX * sin(radians(PHI_MAX))
ROTATE_RANGE = Y_MAX / 2
DRIVE_RANGE = R_MAX * 7 / 8

def connectToRaspPi():
    ssh.load_system_host_keys()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(HOST, username=USERNAME, password=PASSWORD)
    return ssh
raspPi = connectToRaspPi()

def initWalabotLibrary():
    wlbtPath = join('/usr', 'share', 'walabot', 'python')
    wlbt = load_source('WalabotAPI', join(wlbtPath, 'WalabotAPI.py'))
    wlbt.Init()
    wlbt.SetSettingsFolder()
    return wlbt
wlbt = initWalabotLibrary()

def verifyWalabotIsConnected():
    while True:
        try:
            wlbt.ConnectAny()
        except wlbt.WalabotError as err:
            if err.code == 19: # 'WALABOT_INSTRUMENT_NOT_FOUND'
                input("- Connect Walabot and press 'Enter'.")
        else:
            print('- Connection to Walabot established.')
            return

def setParametersAndStart():
    wlbt.SetProfile(wlbt.PROF_SENSOR)
    wlbt.SetArenaR(R_MIN, R_MAX, R_RES)
    wlbt.SetArenaTheta(THETA_MIN, THETA_MAX, THETA_RES)
    wlbt.SetArenaPhi(PHI_MIN, PHI_MAX, PHI_RES)
    wlbt.SetThreshold(TSHLD)
    wlbt.SetDynamicImageFilter(wlbt.FILTER_TYPE_MTI)
    wlbt.Start()

def getClosestTarget():
    wlbt.Trigger()
    targets = wlbt.GetSensorTargets()
    try:
        return max(targets, key=distance)
    except ValueError: # 'targets' is empty; no targets were found
        return None

def moveRobotAccordingToTarget(target):
    system('clear')
    if not target:
        print('Stop')
        #motors.stop()
    elif abs(target.yPosCm) > ROTATE_RANGE: # hand is at 'rotate section'
        print('Rotate')
        print(rotationSpeed(target.yPosCm))
    elif target.zPosCm < DRIVE_RANGE: # hand is at 'drive section'
        print('Drive')
        print(drivingSpeed(target.zPosCm))
    else: # target is in the middle of arena
        print('Stop')
        #motors.stop()

def drivingSpeed(z):
    return (1 - z / DRIVE_RANGE) * MAX_SPEED * 2

def rotationSpeed(y):
    numerator = y - ROTATE_RANGE if y > 0 else y + ROTATE_RANGE
    return numerator / (Y_MAX - ROTATE_RANGE) * 90

def stopRobotAndDisconnectWalabot():
    #motors.stop()
    wlbt.Stop()
    wlbt.Disconnect()

def robotGestures():
    verifyWalabotIsConnected()
    setParametersAndStart()
    try:
        while True:
            moveRobotAccordingToTarget(getClosestTarget())
    finally:
        stopRobotAndDisconnectWalabot()

if __name__ == '__main__':
    robotGestures()
