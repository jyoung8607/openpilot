# flake8: noqa

from selfdrive.car import dbc_dict
from cereal import car
Ecu = car.CarParams.Ecu

class CarControllerParams:
  HCA_STEP = 2                   # HCA_01 message frequency 50Hz
  LDW_STEP = 10                  # LDW_02 message frequency 10Hz
  GRA_ACC_STEP = 3               # GRA_ACC_01 message frequency 33Hz

  GRA_VBP_STEP = 100             # Send ACC virtual button presses once a second
  GRA_VBP_COUNT = 16             # Send VBP messages for ~0.5s (GRA_ACC_STEP * 16)

  # Observed documented MQB limits: 3.00 Nm max, rate of change 5.00 Nm/sec.
  # Limiting rate-of-change based on real-world testing and Comma's safety
  # requirements for minimum time to lane departure.
  STEER_MAX = 300                # Max heading control assist torque 3.00 Nm
  STEER_DELTA_UP = 4             # Max HCA reached in 1.50s (STEER_MAX / (50Hz * 1.50))
  STEER_DELTA_DOWN = 10          # Min HCA reached in 0.60s (STEER_MAX / (50Hz * 0.60))
  STEER_DRIVER_ALLOWANCE = 80
  STEER_DRIVER_MULTIPLIER = 3    # weight driver torque heavily
  STEER_DRIVER_FACTOR = 1        # from dbc

class CANBUS:
  pt = 0
  cam = 2

TransmissionType = car.CarParams.TransmissionType
GearShifter = car.CarState.GearShifter

BUTTON_STATES = {
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

class CAR:
  GOLF = "VOLKSWAGEN GOLF"
  JETTA_MK7 = "VOLKSWAGEN JETTA"
  PASSAT_B8 = "VOLKSWAGEN PASSAT"
  AUDI_A3 = "AUDI A3"
  SKODA_KODIAQ = "SKODA KODIAQ"
  SKODA_SCALA = "SKODA SCALA"

MQB_CARS = {
  CAR.GOLF,                 # Chassis AU, 2013-2020, includes Golf, Alltrack, Sportwagen, GTI, GTI TCR, GTE, GTD, Clubsport, Golf R, e-Golf
  CAR.JETTA_MK7,            # Chassis BU, 2018-2021, includes Jetta and Jetta GLI, marketed as Sagitar in China with a longer wheelbase
  CAR.PASSAT_B8,            # Chassis 3C, 2014-2020, includes Passat, Alltrack, GTE (does not include North America NMS Passat)
  CAR.AUDI_A3,              # Chassis 8V, 2013-2019, includes A3, A3 e-tron, A3 g-tron, S3, RS3
  CAR.SKODA_KODIAQ,         # Chassis 5N, 2016-2020, includes Kodiaq
  CAR.SKODA_SCALA,          # Chassis NW, 2019-2021, includes Scala

}

# During MQB FPv2 testing, ignore all traditional CAN fingerprints
IGNORED_FINGERPRINTS = [CAR.GOLF, CAR.AUDI_A3]

FINGERPRINTS = {
  CAR.GOLF: [{
    64: 8, 134: 8, 159: 8, 173: 8, 178: 8, 253: 8, 257: 8, 260: 8, 262: 8, 264: 8, 278: 8, 279: 8, 283: 8, 286: 8, 288: 8, 289: 8, 290: 8, 294: 8, 299: 8, 302: 8, 346: 8, 385: 8, 418: 8, 427: 8, 668: 8, 679: 8, 681: 8, 695: 8, 779: 8, 780: 8, 783: 8, 792: 8, 795: 8, 804: 8, 806: 8, 807: 8, 808: 8, 809: 8, 870: 8, 896: 8, 897: 8, 898: 8, 901: 8, 917: 8, 919: 8, 927: 8, 949: 8, 958: 8, 960: 4, 981: 8, 987: 8, 988: 8, 991: 8, 997: 8, 1000: 8, 1019: 8, 1120: 8, 1122: 8, 1123: 8, 1124: 8, 1153: 8, 1162: 8, 1175: 8, 1312: 8, 1385: 8, 1413: 8, 1440: 5, 1514: 8, 1515: 8, 1520: 8, 1529: 8, 1600: 8, 1601: 8, 1603: 8, 1605: 8, 1624: 8, 1626: 8, 1629: 8, 1631: 8, 1646: 8, 1648: 8, 1712: 6, 1714: 8, 1716: 8, 1717: 8, 1719: 8, 1720: 8, 1721: 8
  }],
  CAR.AUDI_A3: [{
    64: 8, 134: 8, 159: 8, 173: 8, 178: 8, 253: 8, 257: 8, 260: 8, 262: 8, 278: 8, 279: 8, 283: 8, 285: 8, 286: 8, 288: 8, 289: 8, 290: 8, 294: 8, 295: 8, 299: 8, 302: 8, 346: 8, 418: 8, 427: 8, 506: 8, 679: 8, 681: 8, 695: 8, 779: 8, 780: 8, 783: 8, 787: 8, 788: 8, 789: 8, 792: 8, 802: 8, 804: 8, 806: 8, 807: 8, 808: 8, 809: 8, 846: 8, 847: 8, 870: 8, 896: 8, 897: 8, 898: 8, 901: 8, 917: 8, 919: 8, 949: 8, 958: 8, 960: 4, 981: 8, 987: 8, 988: 8, 991: 8, 997: 8, 1000: 8, 1019: 8, 1122: 8, 1123: 8, 1124: 8, 1153: 8, 1162: 8, 1175: 8, 1312: 8, 1385: 8, 1413: 8, 1440: 5, 1514: 8, 1515: 8, 1520: 8, 1600: 8, 1601: 8, 1603: 8, 1624: 8, 1629: 8, 1631: 8, 1646: 8, 1648: 8, 1712: 6, 1714: 8, 1716: 8, 1717: 8, 1719: 8, 1720: 8, 1721: 8, 1792: 8, 1872: 8, 1976: 8, 1977: 8, 1982: 8, 1985: 8
  }],
}

FW_VERSIONS = {
  CAR.AUDI_A3: {
    (Ecu.engine, 0x7e0, None): [
      b'\xf1\x875G0906259L \xf1\x890002',  # 2017 Audi A3 Prestige (CNTC)
      b'\xf1\x8704E906023BL\xf1\x895190',  # 2018 A3 e-tron Sportback (CXUA)
    ],
    (Ecu.transmission, 0x7e1, None): [
      b'\xf1\x870D9300013B \xf1\x894931',  # 2017 Audi A3 Prestige (DQ250)
      b'\xf1\x870DD300046G \xf1\x891601',  # 2018 A3 e-tron Sportback (DQ400E)
    ],
    (Ecu.srs, 0x715, None): [
      b'\xf1\x875Q0959655J \xf1\x890830\xf1\x82\023121111111211--261117141112231291163221',  # 2017 Audi A3 Prestige
      b'\xf1\x875Q0959655J \xf1\x890830\xf1\x82\x13121111111111--341117141212231291163221',  # 2018 A3 e-tron Sportback
    ],
    (Ecu.eps, 0x712, None): [
      b'\xf1\x875Q0909144T \xf1\x891072\xf1\x82\00521G00807A1',  # 2017 Audi A3 Prestige
      b'\xf1\x875Q0909144T \xf1\x891072\xf1\x82\x0521G00807A1',  # 2018 A3 e-tron Sportback
    ],
    (Ecu.fwdRadar, 0x757, None): [
      b'\xf1\x875Q0907572G \xf1\x890571',  # 2017 Audi A3 Prestige
      b'\xf1\x875Q0907572G \xf1\x890571',  # 2018 A3 e-tron Sportback
    ],
    (Ecu.fwdCamera, 0x74f, None): [
      # FIXME: Comma's 2017 Audi A3 Prestige is known to have a camera, need to re-FP
      b'\xf1\x873Q0980654H \xf1\x890272\xf1\x82\x0436041111',  # 2018 A3 e-tron Sportback
    ],
  },
  CAR.GOLF: {
    (Ecu.engine, 0x7e0, None): [
      b'\xf1\x8704E906016AD\xf1\x895758',  # 2014 Golf (CPTA)
      b'\xf1\x8704E906016A \xf1\x897697',  # 2015 Golf (CJZA)
      b'\xf1\x875G0906259J \xf1\x890002',  # 2016 Golf R wagon (CJXB)
      b'\xf1\x8704L906056HE\xf1\x893758',  # 2018 Golf wagon (DDYA)
      b'\xf1\x8704E906023BN\xf1\x894518',  # 2018 Golf GTE (CUKB)
      b'\xf1\x878V0906259P \xf1\x890001',  # 2018 Golf R (DJJA)
      b'\xf1\x8704L906026NF\xf1\x899528',  # 2019 Golf (DFGA)
      b'\xf1\x878V0906259Q \xf1\x890002',  # 2019 Golf R (DLRA)
      b'\xf1\x870EA906016S \xf1\x897207',  # 2020 e-Golf (EBSA)
    ],
    (Ecu.transmission, 0x7e1, None): [
      b'\xf1\x870CW300045  \xf1\x894531',  # 2014 Golf (DQ200)
      b'\xf1\x870CW300047D \xf1\x895261',  # 2015 Golf (DQ200)
      b'\xf1\x870D9300012  \xf1\x894913',  # 2016 Golf R wagon (DQ250)
      b'\xf1\x870CW300042F \xf1\x891604',  # 2018 Golf wagon (DQ200)
      b'\xf1\x870DD300046F \xf1\x891601',  # 2018 Golf GTE (DQ400E)
      b'\xf1\x870GC300012A \xf1\x891403',  # 2018 Golf R (DQ381)
      b'\xf1\x870GC300043T \xf1\x899999',  # 2019 Golf (DQ381)
      b'\xf1\x870GC300014B \xf1\x892405',  # 2019 Golf R (DQ381)
    ],
    (Ecu.srs, 0x715, None): [
      b'\xf1\x875Q0959655M \xf1\x890361\xf1\x82\0211413001112120041114115121611169112',  # 2014 Golf
      b'\xf1\x875Q0959655AA\xf1\x890386\xf1\x82\0211413001113120043114317121C111C9113',  # 2015 Golf
      b'\xf1\x875Q0959655AA\xf1\x890388\xf1\x82\0211413001113120053114317121C111C9113',  # 2016 Golf R wagon
      b'\xf1\x875Q0959655BH\xf1\x890336\xf1\x82\02314160011123300314211012230229333463100',  # 2018 Golf wagon
      b'\xf1\x875Q0959655S \xf1\x890870\xf1\x82\x1315120011211200061104171717101791132111',  # 2018 Golf GTE
      b'\xf1\x875Q0959655J \xf1\x890830\xf1\x82\x13271212111312--071104171838103891131211',  # 2018 Golf R
      b'\xf1\x875Q0959655BH\xf1\x890336\xf1\x82\02314160011123300314211012230229333463100',  # 2019 Golf
      b'\xf1\x875Q0959655J \xf1\x890830\xf1\x82\023271212111312--071104171838103891131211',  # 2019 Golf R
      b'\xf1\x875Q0959655S \xf1\x890870\xf1\x82\02324230011211200061104171724102491132111',  # 2020 e-Golf
    ],
    (Ecu.eps, 0x712, None): [
      b'\xf1\x875Q0909144L \xf1\x891021\xf1\x82\00522A00402A0',  # 2014 Golf
      b'\xf1\x875Q0909144P \xf1\x891043\xf1\x82\00511A00403A0',  # 2015 Golf
      b'\xf1\x873Q0909144H \xf1\x895061\xf1\x82\00566A0J612A1',  # 2016 Golf R wagon (progressive ratio)
      b'\xf1\x875Q0909144AA\xf1\x891081\xf1\x82\00521A00441A1',  # 2018 Golf wagon
      b'\xf1\x875Q0909144AA\xf1\x891081\xf1\x82\x0521A00641A1',  # 2018 Golf GTE
      b'\xf1\x873Q0909144L \xf1\x895081\xf1\x82\x0571A0JA15A1',  # 2018 Golf R (progressive ratio)
      b'\xf1\x875Q0909144AB\xf1\x891082\xf1\x82\00521A00642A1',  # 2019 Golf
      b'\xf1\x873Q0909144M \xf1\x895082\xf1\x82\00571A0JA16A1',  # 2019 Golf R (progressive ratio)
      b'\xf1\x875Q0909144AB\xf1\x891082\xf1\x82\00521A07B05A1',  # 2020 e-Golf
    ],
    (Ecu.fwdRadar, 0x757, None): [
      b'\xf1\x875Q0907572A \xf1\x890141\xf1\x82\00101',  # 2014 Golf
      b'\xf1\x875Q0907572D \xf1\x890304\xf1\x82\00101',  # 2015 Golf
      b'\xf1\x875Q0907572F \xf1\x890400\xf1\x82\00101',  # 2016 Golf R wagon
      b'\xf1\x875Q0907572J \xf1\x890654',  # 2018 Golf wagon
      b'\xf1\x875Q0907572H \xf1\x890620',  # 2018 Golf GTE
      b'\xf1\x875Q0907572J \xf1\x890654',  # 2018 Golf R
      b'\xf1\x875Q0907572P \xf1\x890682',  # 2019 Golf, Golf R
      b'\xf1\x875Q0907572P \xf1\x890682',  # 2020 e-Golf
    ],
    (Ecu.fwdCamera, 0x74f, None): [
      b'\xf1\x875Q0980653E \xf1\x890050\xf1\x82\00401010253',  # 2014 Golf
      b'\xf1\x873Q0980654H \xf1\x890272\xf1\x82\x041P041117',  # 2018 Golf GTE
      b'\xf1\x873Q0980654H \xf1\x890272\xf1\x82\x0460041116',  # 2018 Golf R (modified parameterization)
      b'\xf1\x873Q0980654L \xf1\x890610\xf1\x82\00444041403',  # 2019 Golf
      b'\xf1\x873Q0980654L \xf1\x890610\xf1\x82\0041A041403',  # 2019 Golf R
      b'\xf1\x873Q0980654L \xf1\x890610\xf1\x82\0041J041403',  # 2020 e-Golf
    ],
  },
  CAR.JETTA_MK7: {
    (Ecu.engine, 0x7e0, None): [
      b'\xf1\x8704E906024B \xf1\x895594',  # 2018 Jetta (DGXA)
      b'\xf1\x8704E906024L \xf1\x895595',  # 2019 Jetta (DGXA)
      b'\xf1\x8704E906024AK\xf1\x899937',  # 2020 Jetta (DGXA)
      b'\xf1\x875G0906259T \xf1\x890003',  # 2021 Jetta GLI (DKFA)
    ],
    (Ecu.transmission, 0x7e1, None): [
      b'\xf1\x8709S927158R \xf1\x893552',  # 2018 Jetta (AQ300)
      b'\xf1\x8709S927158R \xf1\x893552',  # 2019 Jetta (AQ300)
      b'\xf1\x8709S927158R \xf1\x893587',  # 2020 Jetta (AQ300)
      b'\xf1\x870GC300020N \xf1\x892803',  # 2021 Jetta GLI (DQ381)
    ],
    (Ecu.srs, 0x715, None): [
      b'\xf1\x875Q0959655AG\xf1\x890336\xf1\x82\02314171231313500314611011630169333463100',  # 2018 Jetta
      b'\xf1\x875Q0959655AG\xf1\x890336\xf1\x82\x1314171231313500314611011630169333463100',  # 2019 Jetta
      b'\xf1\x875Q0959655BR\xf1\x890403\xf1\x82\02311170031313300314240011150119333433100',  # 2020 Jetta
      b'\xf1\x875Q0959655BM\xf1\x890403\xf1\x82\02314171231313500314643011650169333463100',  # 2021 Jetta GLI
    ],
    (Ecu.eps, 0x712, None): [
      b'\xf1\x875QM909144B \xf1\x891081\xf1\x82\00521A10A01A1',  # 2018 Jetta
      b'\xf1\x875QM909144B \xf1\x891081\xf1\x82\x0521B00404A1',  # 2019 Jetta
      b'\xf1\x875QM909144C \xf1\x891082\xf1\x82\00521A10A01A1',  # 2020 Jetta
      b'\xf1\x875QN909144B \xf1\x895082\xf1\x82\00571A10A11A1',  # 2021 Jetta GLI
    ],
    (Ecu.fwdRadar, 0x757, None): [
      b'\xf1\x875Q0907572N \xf1\x890681',  # 2018 Jetta
      b'\xf1\x875Q0907572N \xf1\x890681',  # 2019 Jetta 
      b'\xf1\x875Q0907572R \xf1\x890771',  # 2020 Jetta
      b'\xf1\x875Q0907572R \xf1\x890771',  # 2021 Jetta GLI
    ],
    (Ecu.fwdCamera, 0x74f, None): [
      b'\xf1\x873QD980654  \xf1\x891272\xf1\x82\0041H041119',  # 2018 Jetta
      b'\xf1\x873QD980654  \xf1\x891272\xf1\x82\x041H041119',  # 2019 Jetta
    ],
  },
  CAR.PASSAT_B8: {
    (Ecu.engine, 0x7e0, None): [
      b'\xf1\x8704E906023AH\xf1\x893379',  # 2016 Passat GTE wagon (CUKC)
    ],
    (Ecu.transmission, 0x7e1, None): [
      b'\xf1\x870DD300045T \xf1\x891601',  # 2016 Passat GTE wagon (DQ400E)
    ],
    (Ecu.srs, 0x715, None): [
      b'\xf1\x875Q0959655S \xf1\x890870\xf1\x82\02315120011111200631145171716121691132111',  # 2016 Passat GTE wagon
    ],
    (Ecu.eps, 0x712, None): [
      b'\xf1\x875Q0909143M \xf1\x892041\xf1\x820522B0080803',  # 2016 Passat GTE wagon
    ],
    (Ecu.fwdRadar, 0x757, None): [
      b'\xf1\x875Q0907572R \xf1\x890771',  # 2016 Passat GTE wagon (retrofitted)
    ],
    (Ecu.fwdCamera, 0x74f, None): [
      b'\xf1\x873Q0980654L \xf1\x890610\xf1\x82\00414041403',  # 2016 Passat GTE wagon
    ],
  },
  CAR.SKODA_KODIAQ: {
    (Ecu.engine, 0x7e0, None): [
      b'\xf1\x8704E906027DD\xf1\x893123',  # 2018 Skoda Kodiaq (CZEA)
      b'\xf1\x875NA907115E \xf1\x890003',  # 2018 Skoda Kodiaq (DGVA)
    ],
    (Ecu.transmission, 0x7e1, None): [
      b'\xf1\x870D9300043  \xf1\x895202',  # 2018 Skoda Kodiaq (DQ250)
      b'\xf1\x870DL300012M \xf1\x892107',  # 2018 Skoda Kodiaq (DQ500)
    ],
    (Ecu.srs, 0x715, None): [
      b'\xf1\x873Q0959655BJ\xf1\x890703\xf1\x82\0161213001211001205212111052100',  # 2018 Skoda Kodiaq
    ],
    (Ecu.eps, 0x712, None): [
      b'\xf1\x875Q0909143P \xf1\x892051\xf1\x820527T6050405',  # 2018 Skoda Kodiaq
      b'\xf1\x875Q0909143P \xf1\x892051\xf1\x820527T6060405',  # 2018 Skoda Kodiaq
    ],
    (Ecu.fwdRadar, 0x757, None): [
      b'\xf1\x872Q0907572R \xf1\x890372',  # 2018 Skoda Kodiaq
    ],
    (Ecu.fwdCamera, 0x74f, None): [
      b'\xf1\x873QD980654  \xf1\x890610\xf1\x82\00414041403',  # 2018 Skoda Kodiaq
      b'\xf1\x873QD980654  \xf1\x891272\xf1\x82\00469041118',  # 2018 Skoda Kodiaq
    ],
  },
  CAR.SKODA_SCALA: {
    (Ecu.engine, 0x7e0, None): [
      b'\xf1\x8704C906025AK\xf1\x897053',  # 2020 Skoda Scala (DKRF)
    ],
    (Ecu.transmission, 0x7e1, None): [
      b'\xf1\x870CW300050  \xf1\x891709',  # 2020 Skoda Scala (DQ200G2)
    ],
    (Ecu.srs, 0x715, None): [
      b'\xf1\x872Q0959655AM\xf1\x890351\xf1\x82\022111104111104112104040404111111112H14',  # 2020 Skoda Scala
    ],
    (Ecu.eps, 0x712, None): [
      b'\xf1\x872Q1909144M \xf1\x896041',  # 2020 Skoda Scala
    ],
    (Ecu.fwdRadar, 0x757, None): [
      b'\xf1\x872Q0907572R \xf1\x890372',  # 2020 Skoda Scala
    ],
    (Ecu.fwdCamera, 0x74f, None): [
      b'\xf1\x873Q0980654R \xf1\x890460\xf1\x82\0046s041313',  # 2020 Skoda Scala
    ],
  },
}

DBC = {
  CAR.GOLF: dbc_dict('vw_mqb_2010', None),
  CAR.JETTA_MK7: dbc_dict('vw_mqb_2010', None),
  CAR.PASSAT_B8: dbc_dict('vw_mqb_2010', None),
  CAR.AUDI_A3: dbc_dict('vw_mqb_2010', None),
  CAR.SKODA_KODIAQ: dbc_dict('vw_mqb_2010', None),
  CAR.SKODA_SCALA: dbc_dict('vw_mqb_2010', None),
}
