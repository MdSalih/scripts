import socket
def isValidIp(ip):
  try:
    socket.inet_aton(ip)
    return True
  except:
    return False
