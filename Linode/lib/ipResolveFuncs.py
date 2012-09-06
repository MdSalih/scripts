from urllib import urlopen

def getCurrentIp():
  return urlopen('http://automation.whatismyip.com/n09230945.asp').read()  
