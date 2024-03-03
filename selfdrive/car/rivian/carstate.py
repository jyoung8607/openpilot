from cereal import car
from openpilot.common.conversions import Conversions as CV
from openpilot.selfdrive.car.interfaces import CarStateBase
from opendbc.can.can_define import CANDefine
from opendbc.can.parser import CANParser
from openpilot.selfdrive.car.rivian.values import DBC, CANBUS, CarControllerParams


class CarState(CarStateBase):
  def __init__(self, CP):
    super().__init__(CP)
    self.CCP = CarControllerParams(CP)
    can_define = CANDefine(DBC[CP.carFingerprint]["pt"])
    self.shifter_values = can_define.dv["VDM_PropStatus"]["VDM_Prndl_Status"]

  def update(self, pt_cp, adas_cp, cam_cp):
    ret = car.CarState.new_message()

    # Update vehicle speed and acceleration from ABS wheel speeds.
    # TODO: what do we do about Rivian 200Hz wheel speed messages?

    ret.vEgoRaw = pt_cp.vl["VDM_PropStatus"]["VDM_VehicleSpeed"]
    ret.vEgo, ret.aEgo = self.update_speed_kf(ret.vEgoRaw)
    ret.standstill = ret.vEgoRaw == 0

    ret.steeringAngleDeg = adas_cp.vl["SAS_Status"]["SAS_Status_AngleSafe"] * CV.RAD_TO_DEG
    ret.steeringRateDeg = adas_cp.vl["SAS_Status"]["SAS_Status_AngleSpeedSafe"] * CV.RAD_TO_DEG
    ret.steeringTorque = pt_cp.vl["EPAS_SystemStatus"]["EPAS_TorsionBarTorque"]
    ret.steeringPressed = abs(ret.steeringTorque) > 1.0  # N-m
    ret.yawRate = adas_cp.vl["RCM_IMU_LatAccYaw"]["RCM_IMU_Yaw"]

    #ret.steerFaultPermanent = TBD
    #ret.steerFaultTemporary = TBD

    ret.gas = pt_cp.vl["VDM_PropStatus"]["VDM_AcceleratorPedalPosition"]
    ret.gasPressed = ret.gas > 0
    #ret.brake = TBD, there's a brake torque available but maybe not pressure
    ret.brakePressed = bool(pt_cp.vl["ESP_AebFb"]["iB_BrakePedalApplied"])
    #ret.parkingBrake = TBD

    ret.gearShifter = self.parse_gear_shifter(self.shifter_values.get(pt_cp.vl["VDM_PropStatus"]["VDM_Prndl_Status"], None))

    #ret.doorOpen = TBD
    #ret.seatbeltUnlatched = TBD

    #ret.leftBlindspot = TBD
    #ret.rightBlindspot = TBD

    #ret.stockFcw = TBD
    #ret.stockAeb = TBD

    #ret.cruiseState.available = TBD
    #ret.cruiseState.enabled = TBD
    #ret.cruiseState.standstill = TBD
    #ret.accFaulted = TBD

    #ret.cruiseState.speed = TBD

    #ret.leftBlinker = TBD
    #ret.rightBlinker = TBD
    #ret.buttonEvents = self.create_button_events(pt_cp, self.CCP.BUTTONS)

    #ret.espDisabled = TBD

    return ret

  @staticmethod
  def get_can_parser(CP):
    messages = [
      # sig_address, frequency
      ("VDM_PropStatus", 50),
      ("EPAS_SystemStatus", 100),
      ("ESP_AebFb", 100),
    ]

    return CANParser(DBC[CP.carFingerprint]["pt"], messages, CANBUS.pt)

  @staticmethod
  def get_adas_can_parser(CP):
    messages = [
      # sig_address, frequency
      ("SAS_Status", 50),
      ("RCM_IMU_LatAccYaw", 100),
    ]

    return CANParser(DBC[CP.carFingerprint]["pt"], messages, CANBUS.adas)

  @staticmethod
  def get_cam_can_parser(CP):
    messages = []

    return CANParser(DBC[CP.carFingerprint]["pt"], messages, CANBUS.cam)
