from cereal import car
from openpilot.selfdrive.car import get_safety_config
from openpilot.selfdrive.car.interfaces import CarInterfaceBase
from openpilot.selfdrive.car.rivian.values import CAR, TransmissionType, GearShifter

ButtonType = car.CarState.ButtonEvent.Type
EventName = car.CarEvent.EventName


class CarInterface(CarInterfaceBase):
  @staticmethod
  def _get_params(ret, candidate: CAR, fingerprint, car_fw, experimental_long, docs):
    ret.carName = "rivian"
    ret.radarUnavailable = True

    # Set global Rivian parameters
    ret.safetyConfigs = [get_safety_config(car.CarParams.SafetyModel.allOutput, 1)]  # FIXME: placeholder for development
    #ret.enableBsm = TBD

    ret.transmissionType = TransmissionType.automatic

    # Global lateral tuning defaults, can be overridden per-vehicle

    ret.steerLimitTimer = 0.4
    ret.steerActuatorDelay = 0.2
    CarInterfaceBase.configure_torque_tune(candidate, ret.lateralTuning)

    # Global longitudinal tuning defaults, can be overridden per-vehicle

    ret.experimentalLongitudinalAvailable = False
    ret.pcmCruise = not ret.openpilotLongitudinalControl
    ret.autoResumeSng = ret.minEnableSpeed == -1

    return ret

  # returns a car.CarState
  def _update(self, c):
    ret = self.CS.update(self.cp, self.cp_adas, self.cp_cam)

    events = self.create_common_events(ret, extra_gears=[GearShifter.eco, GearShifter.sport, GearShifter.manumatic],
                                       pcm_enable=not self.CS.CP.openpilotLongitudinalControl,
                                       enable_buttons=(ButtonType.setCruise, ButtonType.resumeCruise))

    ret.events = events.to_msg()

    return ret

  def apply(self, c, now_nanos):
    new_actuators, can_sends = self.CC.update(c, self.CS, now_nanos)
    return new_actuators, can_sends
