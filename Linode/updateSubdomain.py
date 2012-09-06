import ConfigParser,logging,logging.config
from sys import exit
from operator import itemgetter
from pprint import pprint
from linode import api as LinodeAPI
import lib.ipResolveFuncs
from lib.helpers import isValidIp

# Setup Logging
logging.config.fileConfig('conf/logging.cfg')
log = logging.getLogger('main')

# Setup Config 
cfgFile = "conf/settings.cfg"
cfg = ConfigParser.ConfigParser()
cfg.read(cfgFile)

# Get Config info for this script
apiKey = cfg.get('api','key')
domain = cfg.get('site','domain')
subdomain = cfg.get('site','subdomain')
ipResolveFunc = cfg.get('site','ipResolveFunc')
# TODO: check for AlertEmailAddress 

log.info('Attempting to update subdomain [ %s ] of domain [ %s ] with IP address resolved by [ %s ]',subdomain,domain,ipResolveFunc)

# Check if ipResolveFunc is valid
if(not ipResolveFunc in dir(lib.ipResolveFuncs)):
  log.fatal("IP resolve func [ %s ] is not a valid function to resolve IP addr. Can't continue, exiting...", ipResolveFunc)
  exit(1)

# Get ip address
ipAddr = getattr(lib.ipResolveFuncs,ipResolveFunc)()

# Check if we got a valid IP address
if(not isValidIp(ipAddr)):
  log.fatal("Got an invalid IP address [ %s ] from resolve function [ %s ]. Can't continue, exiting...", ipAddr, ipResolveFunc)
  exit(1)
else:
  log.info('Got IP address [ %s ]',ipAddr)

# Begin comms with Linode DNS Manager
linode = LinodeAPI.Api(apiKey)
domains = linode.domain_list()

# Get list of domains & find domain we're interested in
try:
  domainId = domains[map(itemgetter('DOMAIN'),domains).index(domain)]['DOMAINID']
except:
  log.fatal("Couldn't find domain [ %s ] in domains managed at linode. Available list is:\n\t%s",domain, map(itemgetter('DOMAIN'),domans))

log.info("Got domain ID [ %s ] for domain [ %s ]",domainId,domain)  

# Find resoure ('A' record) for subdomain of interest
domainResources = linode.domain_resource_list(DomainID=domainId)
targetSubdomain = [dr for dr in domainResources if dr['TYPE'].lower() == 'a' and dr['NAME'].lower() == subdomain.lower()]

# If we find more than one 'A' record for given subdomain, error out
if(len(targetSubdomain) > 1):
  log.fatal("Found [ %d ] matching A records for subdomain [ %s ] of domain [ %s ]. Records printed below. Can't continue, exiting...", len(targetSubdomain), subdomain, domain)
  pprint(targetSubdomain, indent=4)
  exit(1)
 
# If we dont find an 'A' record for subdomain, exit 
if(not len(targetSubdomain)):
  log.info("Couldn't find 'A' record for subdomain [ %s ] of domain [ %s ]... creating a new A record", subdomain, domain)
  newRecord = linode.domain_resource_create(DomainID = domainId, Type='A', Name = subdomain, Target = ipAddr, TTL_Sec=300)
  aRecord = linode.domain_resource_list(DomainID = domainId, ResourceID = newRecord['ResourceID'])
  log.info("Created a new 'A' record:")
  pprint(aRecord, indent=4)
else:
  log.info("Found 'A' record for subdomain [ %s ] of domain [ %s ]", subdomain, domain)
  targetSubdomain = targetSubdomain[0]
  # If we find an 'A' record and it already has the IP address set to it
  if(targetSubdomain['TARGET'] == ipAddr):
    log.info("Target IP address [ %s ] matches expected value [ %s ] - nothing to do, exiting...", targetSubdomain['TARGET'], ipAddr)
    exit(0)
  else:
    # If we find an 'A' record and the IP address is different to what we need it to be
    log.info("Target IP address [ %s ] does not match expected valid [ %s ] - updating...", targetSubdomain['TARGET'], ipAddr)
    newRecord = linode.domain_resource_update(DomainID = domainId, ResourceID = targetSubdomain['RESOURCEID'], Target=ipAddr, TTL_Sec=300)
    aRecord = linode.domain_resource_list(DomainID = domainId, ResourceID = newRecord['ResourceID'])
    log.info("Updated 'A' record:")
    pprint(aRecord, indent=4)
 
log.info("All done, exiting...")
