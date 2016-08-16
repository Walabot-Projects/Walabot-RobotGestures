from __future__ import print_function, division
from pololu_drv8835_rpi import motors, MAX_SPEED
from imp import load_source

R_MIN, R_MAX, R_RES = 5, 30, 10
THETA_MIN, THETA_MAX, THETA_RES = -10, 10, 10
PHI_MIN, PHI_MAX, PHI_RES = -60, 60, 10
TSHLD = 60

distance = lambda t: sqrt(t.xPosCm**2 + t.yPosCm**2 + t.zPosCm**2)
motors.drive = lambda speed: motors.setSpeeds(speed, speed)
motors.rotate = lambda speed: motors.setSpeeds(speed, -speed)
motors.stop = lambda: motors.setSpeeds(0, 0)

def initWalabotLibrary():
    wlbtPath = join('/usr', 'share', 'walabot', 'python')
    wlbt = load_source('WalabotAPI', join(wlbtPath, 'WalabotAPI.py'))
    wlbt.Init()
    wlbt.SetSettingsFolder()
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

def moveRobotAccordingToHand(target):
    if not target:
        motors.stop()
    elif handIsAtDriveArena(target):
        motors.drive(calculateDrivingSpeed(target.zPosCm))
    elif handIsAtRotateArena(target):
        motors.rotate(calculateRotationSpeed(target.yPosCm))
    else: # target is in the middle of arena
        motors.stop()

def handIsAtDriveArena(z):
    pass # TODO: implement it!

def handIsAtRotateArena(y):
    pass # TODO: implement it!

def calculateDrivingSpeed(z):
    pass # TODO: implement it!

def calculateRotationSpeed(y):
    pass # TODO: implement it!

def stopRobotAndDisconnectWalabot():
    motors.stop()
    wlbt.Stop()
    wlbt.Disconnect()

def robotGestures():
    verifyWalabotIsConnected()
    setParametersAndStart()
    try:
        while True:
            moveRobotAccordingToHand(getClosestTarget())
    finally:
        stopRobotAndDisconnectWalabot()

if __name__ == '__main__':
    robotGestures()
