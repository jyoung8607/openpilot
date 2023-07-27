def create_steering_control(packer, bus, apply_steer, lkas_enabled):
  values = {
    "ENABLED_1": 2 if lkas_enabled else 1,
    "ENABLED_2": 1 if lkas_enabled else 0,
    "SET_ME_0X54": 0x54 if lkas_enabled else 0,
    "ASSIST_TORQUE": abs(apply_steer),
    "ASSIST_DIRECTION": 1 if apply_steer < 0 else 0,
  }
  return packer.make_can_msg("HCA_NEW", bus, values)


def create_lka_hud_control(packer, bus, ldw_stock_values, enabled, steering_pressed, hud_alert, hud_control):
  return {}


def create_acc_buttons_control(packer, bus, gra_stock_values, cancel=False, resume=False):
  values = {s: gra_stock_values[s] for s in [
    "GRA_Hauptschalter",           # ACC button, on/off
    "GRA_Typ_Hauptschalter",       # ACC main button type
    "GRA_Codierung",               # ACC button configuration/coding
    "GRA_Tip_Stufe_2",             # unknown related to stalk type
    "GRA_ButtonTypeInfo",          # unknown related to stalk type
  ]}

  values.update({
    "COUNTER": (gra_stock_values["COUNTER"] + 1) % 16,
    "GRA_Abbrechen": cancel,
    "GRA_Tip_Wiederaufnahme": resume,
  })

  return packer.make_can_msg("GRA_ACC_01", bus, values)


def acc_control_value(main_switch_on, acc_faulted, long_active):
  return {}


def acc_hud_status_value(main_switch_on, acc_faulted, long_active):
  return {}


def create_acc_accel_control(packer, bus, acc_type, acc_enabled, accel, acc_control, stopping, starting, esp_hold):
  return {}


def create_acc_hud_control(packer, bus, acc_hud_status, set_speed, lead_distance):
  return {}
