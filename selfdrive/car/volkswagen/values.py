from cereal import car
from selfdrive.car import dbc_dict

BUTTON_STATES = {
  "leftBlinker": False,
  "rightBlinker": False,
  "accelCruise": False,
  "decelCruise": False,
  "cancel": False,
  "setCruise": False,
  "resumeCruise": False,
  "gapAdjustCruise": False
}

MQB_LDW_MESSAGES = {
  "none": 0,                            # Nothing to display
  "laneAssistUnavailChime": 1,          # "Lane Assist currently not available." with chime
  "laneAssistUnavailNoSensorChime": 3,  # "Lane Assist not available. No sensor view." with chime
  "laneAssistTakeOverUrgent": 4,        # "Lane Assist: Please Take Over Steering" with urgent beep
  "emergencyAssistUrgent": 6,           # "Emergency Assist: Please Take Over Steering" with urgent beep
  "laneAssistTakeOverChime": 7,         # "Lane Assist: Please Take Over Steering" with chime
  "laneAssistTakeOverSilent": 8,        # "Lane Assist: Please Take Over Steering" silent
  "emergencyAssistChangingLanes": 9,    # "Emergency Assist: Changing lanes..." with urgent beep
  "laneAssistDeactivated": 10,          # "Lane Assist deactivated." silent with persistent icon afterward
}

class NETWORK_MODEL:
  MQB = 0
  PQ = 1

class CAR:
  GENERICMQB = "Generic Volkswagen MQB Platform Vehicle"
  GENERICPQ = "Generic Volkswagen PQ35/PQ46/NMS Platform Vehicle"

# Mega-fingerprint used to identify any and all MQB platform vehicles. Specific
# make and model characteristics are looked up from the VIN later.
FINGERPRINTS = {
  CAR.GENERICMQB: [
    {178: 8, 1600: 8, 1601: 8, 1603: 8, 1605: 8, 695: 8, 1624: 8, 1626: 8, 1629: 8, 1631: 8, 1122: 8, 1123: 8,
     1124: 8, 1646: 8, 1648: 8, 1153: 8, 134: 8, 1162: 8, 1175: 8, 159: 8, 795: 8, 679: 8, 681: 8, 173: 8, 1712: 6,
     1714: 8, 1716: 8, 1717: 8, 1719: 8, 1720: 8, 1721: 8, 1312: 8, 806: 8, 253: 8, 1792: 8, 257: 8, 260: 8, 262: 8,
     897: 8, 264: 8, 779: 8, 780: 8, 783: 8, 278: 8, 279: 8, 792: 8, 283: 8, 285: 8, 286: 8, 901: 8, 288: 8, 289: 8,
     290: 8, 804: 8, 294: 8, 807: 8, 808: 8, 809: 8, 299: 8, 302: 8, 1351: 8, 346: 8, 870: 8, 1385: 8, 896: 8, 64: 8,
     898: 8, 1413: 8, 917: 8, 919: 8, 927: 8, 1440: 5, 929: 8, 930: 8, 427: 8, 949: 8, 958: 8, 960: 4, 418: 8, 981: 8,
     987: 8, 988: 8, 991: 8, 997: 8, 1000: 8, 1514: 8, 1515: 8, 1520: 8, 1019: 8, 385:8, 668:8, 1120:8,
     1438:8, 1461:8, 391:8, 1511: 8, 1516: 8, 568:8, 569:8, 826:8, 827:8, 1156:8, 1157:8, 1158:8, 1471:8, 1635:8
     },
  ],
  CAR.GENERICPQ: [
    {80: 4, 194: 8, 208: 6, 210: 5, 294: 8, 416: 8, 428: 8, 640: 8, 648: 8, 800: 8, 835: 3, 870: 8, 872: 8, 878: 8,
    896: 8, 906: 4, 912: 8, 914: 8, 919: 8, 928: 8, 978: 7, 1056: 8, 1088: 8, 1152: 8, 1175: 8, 1184: 8, 1192: 8,
    1312: 8, 1386: 8, 1392: 5, 1394: 1, 1408: 8, 1440: 8, 1463: 8, 1470: 5, 1472: 8, 1488: 8, 1490: 8, 1500: 8,
    1550: 2, 1651: 3, 1652: 8, 1654: 2, 1658: 4, 1691: 3, 1736: 2, 1757: 8, 1824: 7, 1845: 7, 2000: 8},
    {80: 4, 194: 8, 208: 6, 416: 8, 428: 8, 640: 8, 648: 8, 800: 8, 896: 8, 906: 4, 912: 8, 914: 8, 928: 8,
     978: 7, 1056: 8, 1088: 8, 1152: 8, 1184: 8, 1192: 8, 1312: 8, 1392: 5, 1394: 1, 1408: 8, 1420: 8,
     1440: 8, 1488: 8, 1500: 8, 1550: 2, 1654: 2, 1658: 2, 1736: 2, 1824: 7, 2000: 8},
  ]

}

GEAR = car.CarState.GearShifter
TRANS = car.CarParams.TransmissionType

class ECU:
  CAM = 0
  RADAR = 1
  AUTO_TRANS = 2
  EV_TRANS = 3

ECU_FINGERPRINT = {
  ECU.CAM: [294, 919],                    # HCA_01 Heading Control Assist, LDW_02 Lane Departure Warning
  ECU.RADAR: [780, 804, 290, 302, 279],   # ACC_02, ACC_04, ACC_06, ACC_07, ACC_10
  ECU.AUTO_TRANS: [173],                  # Getriebe_11 Automatic gearbox
  ECU.EV_TRANS: [391],                    # Community documented e-Golf gearshift position message
}

DBC = {
  CAR.GENERICMQB: dbc_dict('vw_mqb_2010', None),
  CAR.GENERICPQ: dbc_dict('vw_golf_mk4', None),
}
