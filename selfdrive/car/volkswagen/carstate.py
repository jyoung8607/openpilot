import numpy as np
from cereal import car
from openpilot.common.conversions import Conversions as CV
from openpilot.selfdrive.car.interfaces import CarStateBase
from opendbc.can.parser import CANParser
from openpilot.selfdrive.car.volkswagen.values import DBC, CANBUS, NetworkLocation, TransmissionType, GearShifter, \
                                            CarControllerParams, VolkswagenFlags


class CarState(CarStateBase):
  def __init__(self, CP):
    super().__init__(CP)
    self.frame = 0
    self.eps_init_complete = False
    self.CCP = CarControllerParams(CP)
    self.button_states = {button.event_type: False for button in self.CCP.BUTTONS}
    self.acc_type = 0
    self.esp_hold_confirmation = False
    self.upscale_lead_car_signal = False
    self.eps_stock_values = False

  def create_button_events(self, pt_cp, buttons):
    button_events = []

    for button in buttons:
      state = pt_cp.vl[button.can_addr][button.can_msg] in button.values
      if self.button_states[button.event_type] != state:
        event = car.CarState.ButtonEvent.new_message()
        event.type = button.event_type
        event.pressed = state
        button_events.append(event)
      self.button_states[button.event_type] = state

    return button_events

  def update(self, pt_cp, cam_cp, ext_cp, trans_type):
    if self.CP.flags & VolkswagenFlags.PQ:
      return self.update_pq(pt_cp, cam_cp, ext_cp, trans_type)

    ret = car.CarState.new_message()

    if self.CP.flags & VolkswagenFlags.MLB:
      # MLB platform specific signals
      ret.wheelSpeeds = self.get_wheel_speeds(
        pt_cp.vl["ESP_03"]["ESP_VL_Radgeschw"],
        pt_cp.vl["ESP_03"]["ESP_VR_Radgeschw"],
        pt_cp.vl["ESP_03"]["ESP_HL_Radgeschw"],
        pt_cp.vl["ESP_03"]["ESP_HR_Radgeschw"],
      )
      ret.gas = pt_cp.vl["Motor_03"]["MO_Fahrpedalrohwert_01"] / 100.0
      ret.gasPressed = ret.gas > 0
      brake_pedal_pressed = bool(pt_cp.vl["Motor_03"]["MO_Fahrer_bremst"])
      ret.espDisabled = pt_cp.vl["ESP_01"]["ESP_Tastung_passiv"] != 0

      # Gearshift signal
      # TODO: alternatives to string parsing? edit parse_gear_shifter or edit DBC string values
      ret.gearShifter = self.parse_gear_shifter(str(self.CCP.shifter_values.get(pt_cp.vl["Getriebe_03"]["GE_Waehlhebel"], "P")).replace('POSITION_', ''))

      # TODO: this is only present on powertrain
      ret.doorOpen = any([pt_cp.vl["Gateway_05"]["FT_Tuer_geoeffnet"],
                          pt_cp.vl["Gateway_05"]["BT_Tuer_geoeffnet"],
                          pt_cp.vl["Gateway_05"]["HL_Tuer_geoeffnet"],
                          pt_cp.vl["Gateway_05"]["HR_Tuer_geoeffnet"]])

      # TODO: is this the instantaneous or the comfort blink signal?
      ret.leftBlinker = bool(pt_cp.vl["Blinkmodi_01"]["BM_links"])
      ret.rightBlinker = bool(pt_cp.vl["Blinkmodi_01"]["BM_rechts"])

      # ACC okay but disabled (1), ACC ready (2), a radar visibility or other fault/disruption (6 or 7)
      # currently regulating speed (3), driver accel override (4), brake only (5)
      ret.cruiseState.available = ext_cp.vl["ACC_05"]["ACC_Status_ACC"] in (2, 3, 4, 5)
      ret.cruiseState.enabled = ext_cp.vl["ACC_05"]["ACC_Status_ACC"] in (3, 4, 5)
      ret.accFaulted = ext_cp.vl["ACC_05"]["ACC_Status_ACC"] in (6, 7)

      self.gra_stock_values = pt_cp.vl["LS_01"]

    else:
      # MQB platform specific signals
      ret.wheelSpeeds = self.get_wheel_speeds(
        pt_cp.vl["ESP_19"]["ESP_VL_Radgeschw_02"],
        pt_cp.vl["ESP_19"]["ESP_VR_Radgeschw_02"],
        pt_cp.vl["ESP_19"]["ESP_HL_Radgeschw_02"],
        pt_cp.vl["ESP_19"]["ESP_HR_Radgeschw_02"],
      )

      ret.gas = pt_cp.vl["Motor_20"]["MO_Fahrpedalrohwert_01"] / 100.0
      ret.gasPressed = ret.gas > 0
      brake_pedal_pressed = bool(pt_cp.vl["Motor_14"]["MO_Fahrer_bremst"])
      self.esp_hold_confirmation = bool(pt_cp.vl["ESP_21"]["ESP_Haltebestaetigung"])
      ret.espDisabled = pt_cp.vl["ESP_21"]["ESP_Tastung_passiv"] != 0

      # Digital instrument clusters expect the ACC HUD lead car distance to be scaled differently
      self.upscale_lead_car_signal = bool(pt_cp.vl["Kombi_03"]["KBI_Variante"])

      if trans_type == TransmissionType.automatic:
        ret.gearShifter = self.parse_gear_shifter(self.CCP.shifter_values.get(pt_cp.vl["Getriebe_11"]["GE_Fahrstufe"], None))
      elif trans_type == TransmissionType.direct:
        ret.gearShifter = self.parse_gear_shifter(self.CCP.shifter_values.get(pt_cp.vl["EV_Gearshift"]["GearPosition"], None))
      elif trans_type == TransmissionType.manual:
        ret.clutchPressed = not pt_cp.vl["Motor_14"]["MO_Kuppl_schalter"]
        if bool(pt_cp.vl["Gateway_72"]["BCM1_Rueckfahrlicht_Schalter"]):
          ret.gearShifter = GearShifter.reverse
        else:
          ret.gearShifter = GearShifter.drive

      ret.doorOpen = any([pt_cp.vl["Gateway_72"]["ZV_FT_offen"],
                          pt_cp.vl["Gateway_72"]["ZV_BT_offen"],
                          pt_cp.vl["Gateway_72"]["ZV_HFS_offen"],
                          pt_cp.vl["Gateway_72"]["ZV_HBFS_offen"],
                          pt_cp.vl["Gateway_72"]["ZV_HD_offen"]])

      # ACC okay but disabled (1), ACC ready (2), a radar visibility or other fault/disruption (6 or 7)
      # currently regulating speed (3), driver accel override (4), brake only (5)
      ret.cruiseState.available = pt_cp.vl["TSK_06"]["TSK_Status"] in (2, 3, 4, 5)
      ret.cruiseState.enabled = pt_cp.vl["TSK_06"]["TSK_Status"] in (3, 4, 5)
      # Speed limiter mode; ECM faults if we command ACC while not pcmCruise
      ret.cruiseState.nonAdaptive = bool(pt_cp.vl["TSK_06"]["TSK_Limiter_ausgewaehlt"])
      ret.accFaulted = pt_cp.vl["TSK_06"]["TSK_Status"] in (6, 7)

      self.gra_stock_values = pt_cp.vl["GRA_ACC_01"]

      # Stock FCW is considered active if the release bit for brake-jerk warning
      # is set. Stock AEB considered active if the partial braking or target
      # braking release bits are set.
      # Refer to VW Self Study Program 890253: Volkswagen Driver Assistance
      # Systems, chapter on Front Assist with Braking: Golf Family for all MQB
      ret.stockFcw = bool(ext_cp.vl["ACC_10"]["AWV2_Freigabe"])
      ret.stockAeb = bool(ext_cp.vl["ACC_10"]["ANB_Teilbremsung_Freigabe"]) or bool(ext_cp.vl["ACC_10"]["ANB_Zielbremsung_Freigabe"])

      # VW Emergency Assist status tracking and mitigation
      self.eps_stock_values = pt_cp.vl["LH_EPS_03"]
      if self.CP.flags & VolkswagenFlags.STOCK_HCA_PRESENT:
        ret.carFaultedNonCritical = bool(cam_cp.vl["HCA_01"]["EA_Ruckfreigabe"]) or cam_cp.vl["HCA_01"][
          "EA_ACC_Sollstatus"] > 0

      self.acc_type = ext_cp.vl["ACC_06"]["ACC_Typ"]
      ret.leftBlinker = bool(pt_cp.vl["Blinkmodi_02"]["Comfort_Signal_Left"])
      ret.rightBlinker = bool(pt_cp.vl["Blinkmodi_02"]["Comfort_Signal_Right"])

    # Common MLB/MQB signal handling

    ret.vEgoRaw = float(np.mean([ret.wheelSpeeds.fl, ret.wheelSpeeds.fr, ret.wheelSpeeds.rl, ret.wheelSpeeds.rr]))
    ret.vEgo, ret.aEgo = self.update_speed_kf(ret.vEgoRaw)
    ret.standstill = ret.vEgoRaw == 0

    # Update EPS position and state info. For signed values, VW sends the sign in a separate signal.
    ret.steeringAngleDeg = pt_cp.vl["LWI_01"]["LWI_Lenkradwinkel"] * (1, -1)[int(pt_cp.vl["LWI_01"]["LWI_VZ_Lenkradwinkel"])]
    ret.steeringRateDeg = pt_cp.vl["LWI_01"]["LWI_Lenkradw_Geschw"] * (1, -1)[int(pt_cp.vl["LWI_01"]["LWI_VZ_Lenkradw_Geschw"])]
    ret.steeringTorque = pt_cp.vl["LH_EPS_03"]["EPS_Lenkmoment"] * (1, -1)[int(pt_cp.vl["LH_EPS_03"]["EPS_VZ_Lenkmoment"])]
    ret.steeringPressed = abs(ret.steeringTorque) > self.CCP.STEER_DRIVER_ALLOWANCE
    ret.yawRate = pt_cp.vl["ESP_02"]["ESP_Gierrate"] * (1, -1)[int(pt_cp.vl["ESP_02"]["ESP_VZ_Gierrate"])] * CV.DEG_TO_RAD
    hca_status = self.CCP.hca_status_values.get(pt_cp.vl["LH_EPS_03"]["EPS_HCA_Status"])
    ret.steerFaultTemporary, ret.steerFaultPermanent = self.update_hca_state(hca_status)

    # Update gas, brakes, and gearshift.
    ret.brake = pt_cp.vl["ESP_05"]["ESP_Bremsdruck"] / 250.0  # FIXME: this is pressure in Bar, not sure what OP expects
    brake_pressure_detected = bool(pt_cp.vl["ESP_05"]["ESP_Fahrer_bremst"])
    ret.brakePressed = brake_pedal_pressed or brake_pressure_detected
    ret.parkingBrake = bool(pt_cp.vl["Kombi_01"]["KBI_Handbremse"])

    # Update seatbelt fastened status.
    ret.seatbeltUnlatched = pt_cp.vl["Gateway_06"]["AB_Gurtschloss_FA"] != 3

    # Consume blind-spot monitoring info/warning LED states, if available.
    # Infostufe: BSM LED on, Warnung: BSM LED flashing
    if self.CP.enableBsm:
      ret.leftBlindspot = bool(ext_cp.vl["SWA_01"]["SWA_Infostufe_SWA_li"]) or bool(ext_cp.vl["SWA_01"]["SWA_Warnung_SWA_li"])
      ret.rightBlindspot = bool(ext_cp.vl["SWA_01"]["SWA_Infostufe_SWA_re"]) or bool(ext_cp.vl["SWA_01"]["SWA_Warnung_SWA_re"])

    # Consume factory LDW data relevant for factory SWA (Lane Change Assist)
    # and capture it for forwarding to the blind spot radar controller
    self.ldw_stock_values = cam_cp.vl["LDW_02"] if self.CP.networkLocation == NetworkLocation.fwdCamera else {}

    ret.cruiseState.standstill = self.CP.pcmCruise and self.esp_hold_confirmation

    # Update ACC setpoint. When the setpoint is zero or there's an error, the
    # radar sends a set-speed of ~90.69 m/s / 203mph.
    # TODO: ugly hack while testing CC-only S4
    if self.CP.pcmCruise and not self.CP.flags & VolkswagenFlags.MLB:
      ret.cruiseState.speed = ext_cp.vl["ACC_02"]["ACC_Wunschgeschw_02"] * CV.KPH_TO_MS
      if ret.cruiseState.speed > 90:
        ret.cruiseState.speed = 0

    # Update button states for turn signals and ACC controls, capture all ACC button state/config for passthrough
    ret.buttonEvents = self.create_button_events(pt_cp, self.CCP.BUTTONS)

    self.frame += 1
    return ret

  def update_pq(self, pt_cp, cam_cp, ext_cp, trans_type):
    ret = car.CarState.new_message()
    # Update vehicle speed and acceleration from ABS wheel speeds.
    ret.wheelSpeeds = self.get_wheel_speeds(
      pt_cp.vl["Bremse_3"]["Radgeschw__VL_4_1"],
      pt_cp.vl["Bremse_3"]["Radgeschw__VR_4_1"],
      pt_cp.vl["Bremse_3"]["Radgeschw__HL_4_1"],
      pt_cp.vl["Bremse_3"]["Radgeschw__HR_4_1"],
    )

    # vEgo obtained from Bremse_1 vehicle speed rather than Bremse_3 wheel speeds because Bremse_3 isn't present on NSF
    ret.vEgoRaw = pt_cp.vl["Bremse_1"]["Geschwindigkeit_neu__Bremse_1_"] * CV.KPH_TO_MS
    ret.vEgo, ret.aEgo = self.update_speed_kf(ret.vEgoRaw)
    ret.standstill = ret.vEgoRaw == 0

    # Update EPS position and state info. For signed values, VW sends the sign in a separate signal.
    ret.steeringAngleDeg = pt_cp.vl["Lenkhilfe_3"]["LH3_BLW"] * (1, -1)[int(pt_cp.vl["Lenkhilfe_3"]["LH3_BLWSign"])]
    ret.steeringRateDeg = pt_cp.vl["Lenkwinkel_1"]["Lenkradwinkel_Geschwindigkeit"] * (1, -1)[int(pt_cp.vl["Lenkwinkel_1"]["Lenkradwinkel_Geschwindigkeit_S"])]
    ret.steeringTorque = pt_cp.vl["Lenkhilfe_3"]["LH3_LM"] * (1, -1)[int(pt_cp.vl["Lenkhilfe_3"]["LH3_LMSign"])]
    ret.steeringPressed = abs(ret.steeringTorque) > self.CCP.STEER_DRIVER_ALLOWANCE
    ret.yawRate = pt_cp.vl["Bremse_5"]["Giergeschwindigkeit"] * (1, -1)[int(pt_cp.vl["Bremse_5"]["Vorzeichen_der_Giergeschwindigk"])] * CV.DEG_TO_RAD
    hca_status = self.CCP.hca_status_values.get(pt_cp.vl["Lenkhilfe_2"]["LH2_Sta_HCA"])
    ret.steerFaultTemporary, ret.steerFaultPermanent = self.update_hca_state(hca_status)

    # Update gas, brakes, and gearshift.
    ret.gas = pt_cp.vl["Motor_3"]["Fahrpedal_Rohsignal"] / 100.0
    ret.gasPressed = ret.gas > 0
    ret.brake = pt_cp.vl["Bremse_5"]["Bremsdruck"] / 250.0  # FIXME: this is pressure in Bar, not sure what OP expects
    ret.brakePressed = bool(pt_cp.vl["Motor_2"]["Bremslichtschalter"])
    ret.parkingBrake = bool(pt_cp.vl["Kombi_1"]["Bremsinfo"])

    # Update gear and/or clutch position data.
    if trans_type == TransmissionType.automatic:
      ret.gearShifter = self.parse_gear_shifter(self.CCP.shifter_values.get(pt_cp.vl["Getriebe_1"]["Waehlhebelposition__Getriebe_1_"], None))
    elif trans_type == TransmissionType.manual:
      ret.clutchPressed = not pt_cp.vl["Motor_1"]["Kupplungsschalter"]
      reverse_light = bool(pt_cp.vl["Gate_Komf_1"]["GK1_Rueckfahr"])
      if reverse_light:
        ret.gearShifter = GearShifter.reverse
      else:
        ret.gearShifter = GearShifter.drive

    # Update door and trunk/hatch lid open status.
    ret.doorOpen = any([pt_cp.vl["Gate_Komf_1"]["GK1_Fa_Tuerkont"],
                        pt_cp.vl["Gate_Komf_1"]["BSK_BT_geoeffnet"],
                        pt_cp.vl["Gate_Komf_1"]["BSK_HL_geoeffnet"],
                        pt_cp.vl["Gate_Komf_1"]["BSK_HR_geoeffnet"],
                        pt_cp.vl["Gate_Komf_1"]["BSK_HD_Hauptraste"]])

    # Update seatbelt fastened status.
    ret.seatbeltUnlatched = not bool(pt_cp.vl["Airbag_1"]["Gurtschalter_Fahrer"])

    # Consume blind-spot monitoring info/warning LED states, if available.
    # Infostufe: BSM LED on, Warnung: BSM LED flashing
    if self.CP.enableBsm:
      ret.leftBlindspot = bool(ext_cp.vl["SWA_1"]["SWA_Infostufe_SWA_li"]) or bool(ext_cp.vl["SWA_1"]["SWA_Warnung_SWA_li"])
      ret.rightBlindspot = bool(ext_cp.vl["SWA_1"]["SWA_Infostufe_SWA_re"]) or bool(ext_cp.vl["SWA_1"]["SWA_Warnung_SWA_re"])

    # Consume factory LDW data relevant for factory SWA (Lane Change Assist)
    # and capture it for forwarding to the blind spot radar controller
    self.ldw_stock_values = cam_cp.vl["LDW_Status"] if self.CP.networkLocation == NetworkLocation.fwdCamera else {}

    # Stock FCW is considered active if the release bit for brake-jerk warning
    # is set. Stock AEB considered active if the partial braking or target
    # braking release bits are set.
    # Refer to VW Self Study Program 890253: Volkswagen Driver Assistance
    # Systems, chapters on Front Assist with Braking and City Emergency
    # Braking for the 2016 Passat NMS
    # TODO: deferred until we can collect data on pre-MY2016 behavior, AWV message may be shorter with fewer signals
    ret.stockFcw = False
    ret.stockAeb = False

    # Update ACC radar status.
    self.acc_type = ext_cp.vl["ACC_System"]["ACS_Typ_ACC"]
    ret.cruiseState.available = bool(pt_cp.vl["Motor_5"]["GRA_Hauptschalter"])
    ret.cruiseState.enabled = pt_cp.vl["Motor_2"]["GRA_Status"] in (1, 2)
    if self.CP.pcmCruise:
      ret.accFaulted = ext_cp.vl["ACC_GRA_Anzeige"]["ACA_StaACC"] in (6, 7)
    else:
      ret.accFaulted = pt_cp.vl["Motor_2"]["GRA_Status"] == 3

    # Update ACC setpoint. When the setpoint reads as 255, the driver has not
    # yet established an ACC setpoint, so treat it as zero.
    ret.cruiseState.speed = ext_cp.vl["ACC_GRA_Anzeige"]["ACA_V_Wunsch"] * CV.KPH_TO_MS
    if ret.cruiseState.speed > 70:  # 255 kph in m/s == no current setpoint
      ret.cruiseState.speed = 0

    # Update button states for turn signals and ACC controls, capture all ACC button state/config for passthrough
    ret.leftBlinker, ret.rightBlinker = self.update_blinker_from_stalk(300, pt_cp.vl["Gate_Komf_1"]["GK1_Blinker_li"],
                                                                            pt_cp.vl["Gate_Komf_1"]["GK1_Blinker_re"])
    ret.buttonEvents = self.create_button_events(pt_cp, self.CCP.BUTTONS)
    self.gra_stock_values = pt_cp.vl["GRA_Neu"]

    # Additional safety checks performed in CarInterface.
    ret.espDisabled = bool(pt_cp.vl["Bremse_1"]["ESP_Passiv_getastet"])

    self.frame += 1
    return ret

  def update_hca_state(self, hca_status):
    # Treat INITIALIZING and FAULT as temporary for worst likely EPS recovery time, for cars without factory Lane Assist
    # DISABLED means the EPS hasn't been configured to support Lane Assist
    self.eps_init_complete = self.eps_init_complete or (hca_status in ("DISABLED", "READY", "ACTIVE") or self.frame > 600)
    perm_fault = hca_status == "DISABLED" or (self.eps_init_complete and hca_status in ("INITIALIZING", "FAULT"))
    temp_fault = hca_status in ("REJECTED", "PREEMPTED") or not self.eps_init_complete
    return temp_fault, perm_fault

  @staticmethod
  def get_can_parser(CP):
    if CP.flags & VolkswagenFlags.PQ:
      return CarState.get_can_parser_pq(CP)
    elif CP.flags & VolkswagenFlags.MLB:
      return CarState.get_can_parser_mlb(CP)

    messages = [
      # sig_address, frequency
      ("LWI_01", 100),      # From J500 Steering Assist with integrated sensors
      ("LH_EPS_03", 100),   # From J500 Steering Assist with integrated sensors
      ("ESP_19", 100),      # From J104 ABS/ESP controller
      ("ESP_05", 50),       # From J104 ABS/ESP controller
      ("ESP_21", 50),       # From J104 ABS/ESP controller
      ("Motor_20", 50),     # From J623 Engine control module
      ("TSK_06", 50),       # From J623 Engine control module
      ("ESP_02", 50),       # From J104 ABS/ESP controller
      ("GRA_ACC_01", 33),   # From J533 CAN gateway (via LIN from steering wheel controls)
      ("Gateway_72", 10),   # From J533 CAN gateway (aggregated data)
      ("Motor_14", 10),     # From J623 Engine control module
      ("Airbag_02", 5),     # From J234 Airbag control module
      ("Kombi_01", 2),      # From J285 Instrument cluster
      ("Blinkmodi_02", 1),  # From J519 BCM (sent at 1Hz when no lights active, 50Hz when active)
      ("Kombi_03", 0),      # From J285 instrument cluster (not present on older cars, 1Hz when present)
    ]

    if CP.transmissionType == TransmissionType.automatic:
      messages.append(("Getriebe_11", 20))  # From J743 Auto transmission control module
    elif CP.transmissionType == TransmissionType.direct:
      messages.append(("EV_Gearshift", 10))  # From J??? unknown EV control module

    if CP.networkLocation == NetworkLocation.fwdCamera:
      # Radars are here on CANBUS.pt
      messages += MqbExtraSignals.fwd_radar_messages
      if CP.enableBsm:
        messages += MqbExtraSignals.bsm_radar_messages

    return CANParser(DBC[CP.carFingerprint]["pt"], messages, CANBUS.pt)

  @staticmethod
  def get_cam_can_parser(CP):
    if CP.flags & VolkswagenFlags.PQ:
      return CarState.get_cam_can_parser_pq(CP)
    elif CP.flags & VolkswagenFlags.MLB:
      return CarState.get_cam_can_parser_mlb(CP)

    messages = []

    if CP.flags & VolkswagenFlags.STOCK_HCA_PRESENT:
      messages += [
        ("HCA_01", 1),  # From R242 Driver assistance camera, 50Hz if steering/1Hz if not
      ]

    if CP.networkLocation == NetworkLocation.fwdCamera:
      messages += [
        # sig_address, frequency
        ("LDW_02", 10)      # From R242 Driver assistance camera
      ]
    else:
      # Radars are here on CANBUS.cam
      messages += MqbExtraSignals.fwd_radar_messages
      if CP.enableBsm:
        messages += MqbExtraSignals.bsm_radar_messages

    return CANParser(DBC[CP.carFingerprint]["pt"], messages, CANBUS.cam)

  @staticmethod
  def get_can_parser_mlb(CP):
    messages = [
      # sig_address, frequency
      ("LWI_01", 100),      # From J500 Steering Assist with integrated sensors
      ("LH_EPS_03", 100),   # From J500 Steering Assist with integrated sensors
      ("Motor_03", 100),    # From J623 Engine control module
      ("ESP_03", 50),       # From J104 ABS/ESP controller
      ("ESP_05", 50),       # From J104 ABS/ESP controller
      ("ESP_02", 50),       # From J104 ABS/ESP controller
      ("ESP_01", 33),       # From J104 ABS/ESP controller
      ("LS_01", 5),         # From J533 CAN gateway (via LIN from steering wheel controls)
      # FIXME: Testing using radar state instead of TSK state for Macan
      #("TSK_02", 33),       # From J623 Engine control module
      ("Gateway_05", 10),   # From J533 CAN gateway (aggregated data)
      ("Gateway_06", 10),   # TODO: what is source of this signal?
      ("Kombi_01", 2),      # From J285 Instrument cluster
      ("Blinkmodi_01", 0),  # From J519 BCM (sent at 1Hz when no lights active, 50Hz when active)
      ("Kombi_03", 0),      # From J285 instrument cluster (not present on older cars, 1Hz when present)
      ("Getriebe_03", 50),  # TODO: what is the source of this signal?  transmission ecu?
    ]

    # TODO: gear shift parsing
    # TODO: BSM parsing

    return CANParser(DBC[CP.carFingerprint]["pt"], messages, CANBUS.pt)

  @staticmethod
  def get_cam_can_parser_mlb(CP):
    messages = [
      ("ACC_05", 50),  # Macan test: from radar
    ]

    if CP.networkLocation == NetworkLocation.fwdCamera:
      messages += [
        # sig_address, frequency
        ("LDW_02", 10),     # From R242 Driver assistance camera
      ]
    else:
      if CP.enableBsm:
        messages += MqbExtraSignals.bsm_radar_messages  # FIXME: switch this to MlbExtraSignals later

    return CANParser(DBC[CP.carFingerprint]["pt"], messages, CANBUS.cam)

  @staticmethod
  def get_can_parser_pq(CP):
    messages = [
      # sig_address, frequency
      ("Bremse_1", 100),    # From J104 ABS/ESP controller
      ("Bremse_3", 100),    # From J104 ABS/ESP controller
      ("Lenkhilfe_3", 100),  # From J500 Steering Assist with integrated sensors
      ("Lenkwinkel_1", 100),  # From J500 Steering Assist with integrated sensors
      ("Motor_3", 100),     # From J623 Engine control module
      ("Airbag_1", 50),     # From J234 Airbag control module
      ("Bremse_5", 50),     # From J104 ABS/ESP controller
      ("GRA_Neu", 50),      # From J??? steering wheel control buttons
      ("Kombi_1", 50),      # From J285 Instrument cluster
      ("Motor_2", 50),      # From J623 Engine control module
      ("Motor_5", 50),      # From J623 Engine control module
      ("Lenkhilfe_2", 20),  # From J500 Steering Assist with integrated sensors
      ("Gate_Komf_1", 10),  # From J533 CAN gateway
    ]

    if CP.transmissionType == TransmissionType.automatic:
      messages += [("Getriebe_1", 100)]  # From J743 Auto transmission control module
    elif CP.transmissionType == TransmissionType.manual:
      messages += [("Motor_1", 100)]  # From J623 Engine control module

    if CP.networkLocation == NetworkLocation.fwdCamera:
      # Extended CAN devices other than the camera are here on CANBUS.pt
      messages += PqExtraSignals.fwd_radar_messages
      if CP.enableBsm:
        messages += PqExtraSignals.bsm_radar_messages

    return CANParser(DBC[CP.carFingerprint]["pt"], messages, CANBUS.pt)

  @staticmethod
  def get_cam_can_parser_pq(CP):

    messages = []

    if CP.networkLocation == NetworkLocation.fwdCamera:
      messages += [
        # sig_address, frequency
        ("LDW_Status", 10)      # From R242 Driver assistance camera
      ]

    if CP.networkLocation == NetworkLocation.gateway:
      # Radars are here on CANBUS.cam
      messages += PqExtraSignals.fwd_radar_messages
      if CP.enableBsm:
        messages += PqExtraSignals.bsm_radar_messages

    return CANParser(DBC[CP.carFingerprint]["pt"], messages, CANBUS.cam)


class MqbExtraSignals:
  # Additional signal and message lists for optional or bus-portable controllers
  fwd_radar_messages = [
    ("ACC_06", 50),                              # From J428 ACC radar control module
    ("ACC_10", 50),                              # From J428 ACC radar control module
    ("ACC_02", 17),                              # From J428 ACC radar control module
  ]
  bsm_radar_messages = [
    ("SWA_01", 20),                              # From J1086 Lane Change Assist
  ]

class PqExtraSignals:
  # Additional signal and message lists for optional or bus-portable controllers
  fwd_radar_messages = [
    ("ACC_System", 50),                          # From J428 ACC radar control module
    ("ACC_GRA_Anzeige", 25),                     # From J428 ACC radar control module
  ]
  bsm_radar_messages = [
    ("SWA_1", 20),                               # From J1086 Lane Change Assist
  ]
