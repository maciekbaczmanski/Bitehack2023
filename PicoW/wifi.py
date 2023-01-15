import network

def connect():
  SSID = 'MamNaCiebieOko'
  PASSWD = 'Niezgadniesz.'

  wlan = network.WLAN(network.STA_IF)
  wlan.active(True)
  wlan.connect(SSID, PASSWD)
  while wlan.status() != 3 or not wlan.isconnected():
    print("Connecting to WiFi network")
    pass
  print("Succesfully connected to WiFi")

  return wlan
