
# Overview

Script should create/update an A record for a domain, managed within Linode DNS Manager, with the local machines public IP address.

## Background Research

* Review Linode API
 * Work out how to do what I want to do
* Look into Linode API python bindings

## Research Notes
http://www.linode.com/api/ - grap API key, quickly demo using HTTP GET in browser. returns JSON
http://www.linode.com/api/dns - dns api documented here. Probably want to do following

* Call `domain.resource.list` for given API key
 * check if given domain exists in list, if not fail. if yes continue with `domainid`
* Call `domain.resource.list` for retrieved `domainid`, look for given A record
 * if A record already exists, call `domain.resource.update` with args
 * if A record doesn't exist, call `domain.resource.create` with args

Other Points

* If A record already exists, check if value is set to what is expected, if so, break
 * if not expected value, update (+ send email notificaiton?)
* Check if CNAME already exists for given domain ?

