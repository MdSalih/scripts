Overview
-----
Script that will update an 'A' record for a Domain in Linode DNS Manager, via Linode API

Instructions
-----
Create the file `conf/settings.cfg` from the sample file `conf/settings.cfg.sample`
Add settings for your setup

```
[api]
  key = someKeyObtainedFromLinodeControlPanel
[site]
  domain = mysite.com
  subdomain = apples
  ipResolveFunc = getCurrentIp
```

You can then run the following command (possibly off a cron) to update the 'A' record for `apples.mysite.com` with the IP address returned by the funciton `getCurrentIp`

```
python updateSubdomain.py
```

### The `ipResolveFunc`

There is currently only one `ipResolveFunc` implemented - `getCurrentIp` which returns the public IP of the box the script is running from (IP retrieved via [www.whatismyip.com](http://whatismyip.com))
```Python
def getCurrentIp():
  return urlopen('http://automation.whatismyip.com/n09230945.asp').read()  
```
### Added a New IP Resolving Function
A new `ipResolveFunc` can be added by implementing the new function in `lib/ipResolveFuncs.py`. It should return the IP address as a String in [dotted decimal](http://en.wikipedia.org/wiki/Dotted_decimal) format. For example `127.0.0.1`

