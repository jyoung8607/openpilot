from collections import namedtuple
from dataclasses import dataclass, field

from cereal import car
from openpilot.selfdrive.car import dbc_dict, CarSpecs, DbcDict, PlatformConfig, Platforms
from openpilot.selfdrive.car.docs_definitions import CarHarness, CarInfo, CarParts

Ecu = car.CarParams.Ecu
NetworkLocation = car.CarParams.NetworkLocation
TransmissionType = car.CarParams.TransmissionType
GearShifter = car.CarState.GearShifter
Button = namedtuple('Button', ['event_type', 'can_addr', 'can_msg', 'values'])


class CarControllerParams:
  STEER_MAX = 300  # FIXME: placeholder


class CANBUS:
  pt = 0
  adas = 1
  cam = 2


@dataclass
class RivianPlatformConfig(PlatformConfig):
  dbc_dict: DbcDict = field(default_factory=lambda: dbc_dict('rivian', None))


@dataclass
class RivianCarInfo(CarInfo):
  package: str = "Adaptive Cruise Control (ACC) & Lane Assist"
  car_parts: CarParts = field(default_factory=CarParts.common([CarHarness.hyundai_r]))


class CAR(Platforms):
  R1S = RivianPlatformConfig(
    "RIVIAN R1S",
    RivianCarInfo("Rivian R1S 2023"),
    CarSpecs(mass=3206, wheelbase=3.08, steerRatio=15.0),
  )


CAR_INFO = CAR.create_carinfo_map()
DBC = CAR.create_dbc_map()
