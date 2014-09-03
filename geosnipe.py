__author__ = 'blaze'

import pygeoip
import whois
import argparse
import re

geodat = '/opt/geoip/GeoliteCity.dat'
geodb = pygeoip.GeoIP(geodat)


def geosnipe(tgt):
    info = geodb.record_by_name(tgt)
    city = info['city']
    region = info['region_code']
    country = info['country_name']
    areacode = info['area_code']
    metro = info['metro_code']
    lat = info['latitude']
    lon = info['longitude']
    gmap = 'https://maps.google.com/maps?q=loc:%s,%s' % (repr(lat), repr(lon))
    print "\n[!] Geolocation complete for %s" % tgt
    print "\tCity: %s, %s " % (city.encode('utf8'), region.encode('utf8'))
    print "\tCountry: %s" % country
    print "\tMetro Area: %s" % metro
    print "\tArea Code: %s" % areacode
    print "\tLatitude: %s \t Longitude: %s" % (repr(lat), repr(lon))
    print "\tGoogle Maps Link: %s\n" % gmap


def parsewhois(searchstring, whodata):
    dstring = '%s: .*' % searchstring
    data = re.findall(dstring, whodata.text)
    sstring = '%s: ' % searchstring
    data = re.sub(sstring, '', data[0])
    return data


def whoistarget(tgt):
    w = whois.whois(tgt)
    reg = {}
    admin = {}
    tech = {}
    reg['name'] = parsewhois('Registrant Name', w)
    reg['org'] = parsewhois('Registrant Organization', w)
    reg['phone'] = parsewhois('Registrant Phone', w)
    reg['email'] = parsewhois('Registrant Email', w)
    reg['street'] = parsewhois('Registrant Street', w)
    reg['city'] = parsewhois('Registrant City', w)
    reg['state'] = parsewhois('Registrant State/Province', w)
    reg['country'] = parsewhois('Registrant Country', w)
    admin['name'] = parsewhois('Admin Name', w)
    admin['org'] = parsewhois('Admin Organization', w)
    admin['phone'] = parsewhois('Admin Phone', w)
    admin['email'] = parsewhois('Admin Email', w)
    admin['street'] = parsewhois('Admin Street', w)
    admin['city'] = parsewhois('Admin City', w)
    admin['state'] = parsewhois('Admin State/Province', w)
    admin['country'] = parsewhois('Admin Country', w)
    tech['name'] = parsewhois('Tech Name', w)
    tech['org'] = parsewhois('Tech Organization', w)
    tech['phone'] = parsewhois('Tech Phone', w)
    tech['email'] = parsewhois('Tech Email', w)
    tech['street'] = parsewhois('Tech Street', w)
    tech['city'] = parsewhois('Tech City', w)
    tech['state'] = parsewhois('Tech State/Province', w)
    tech['country'] = parsewhois('Tech Country', w)
    print "[!] Whois data for %s" % tgt
    print "\tDomain Name: \t%s" % w.domain_name[0]
    print "\tCreated on: \t%s" % w.creation_date[1]
    print "\tUpdated on: \t%s" % w.updated_date[1]
    print "\tExpires on: \t%s" % w.expiration_date[1]
    print "\tRegistrar: \t%s" % w.registrar[0]
    print "\tStatus: \t%s" % w.status[0]
    for s in w.status[1:]:
        print "\t\t\t%s" % s
    print "\n[+] Whois Registrant Info"
    print "\tName: \t\t%s" % reg['name']
    print "\tPhone: \t\t%s" % reg['phone']
    print "\tEmail: \t\t%s" % reg['email']
    print "\tAddress: \t%s" % reg['street']
    print "\t\t\t%s, %s. %s" % (reg['city'], reg['state'], reg['country'])
    print "\n[+] Whois Admin Info"
    print "\tName: \t\t%s" % admin['name']
    print "\tPhone: \t\t%s" % admin['phone']
    print "\tEmail: \t\t%s" % admin['email']
    print "\tAddress: \t%s" % admin['street']
    print "\t\t\t%s, %s. %s" % (admin['city'], admin['state'], admin['country'])
    print "\n[+] Whois Tech Info"
    print "\tName: \t\t%s" % tech['name']
    print "\tPhone: \t\t%s" % tech['phone']
    print "\tEmail: \t\t%s" % tech['email']
    print "\tAddress: \t%s" % tech['street']
    print "\t\t\t%s, %s. %s" % (tech['city'], tech['state'], tech['country'])


parser = argparse.ArgumentParser()
main = parser.add_argument_group('Target Options')
main.add_argument('-t', '--target', required=True, help='Enter a target to geolocate')
main.add_argument('-w', '--whois', dest='who', action="store_true", help='Get whois data on the target')

args = parser.parse_args()

target = args.target
who = args.who

if __name__ == '__main__':
    if who:
        whoistarget(target)
        geosnipe(target)
    else:
        geosnipe(target)