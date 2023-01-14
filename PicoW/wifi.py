import network

def connect():
  SSID = 'MamNaCiebieOko'
  PASSWD = 'Niezgadniesz.'
  
  wlan = network.WLAN(network.STA_IF)
  wlan.active(True)
  wlan.connect(SSID, PASSWD)
  return wlan
