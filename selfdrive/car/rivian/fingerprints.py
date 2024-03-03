from cereal import car
from openpilot.selfdrive.car.rivian.values import CAR

Ecu = car.CarParams.Ecu


FW_VERSIONS = {
  # TODO: temporary placeholder only, not real data from the vehicle
  CAR.R1S: {
    (Ecu.engine, 0x7e0, None): [
      b'\xf1\x873G0906259AH\xf1\x890001',
    ],
    (Ecu.transmission, 0x7e1, None): [
      b'\xf1\x8709G927158L \xf1\x893611',
    ],
    (Ecu.srs, 0x715, None): [
      b'\xf1\x873Q0959655BK\xf1\x890703\xf1\x82\x0e1616001613121157161111572900',
    ],
    (Ecu.eps, 0x712, None): [
      b'\xf1\x873Q0909144K \xf1\x895072\xf1\x82\x0571B41815A1',
    ],
    (Ecu.fwdRadar, 0x757, None): [
      b'\xf1\x872Q0907572AA\xf1\x890396',
    ],
  },
}
