__author__ = 'blaze'

import pygeoip
import whois
import argparse
import re
import os
import subprocess


def geosnipe(tgt, ofile, o):
    if o:
        of = open(ofile, 'a')
        delim = "=" * 60
    info = geodb.record_by_name(tgt)
    city = info['city']
    region = info['region_code']
    country = info['country_name']
    areacode = info['area_code']
    metro = info['metro_code']
    lat = info['latitude']
    lon = info['longitude']
    if o:
        print "\n[!] Geolocation complete for %s" % tgt
        of.write("\n[!] Geolocation complete for %s\n" % tgt)
    else:
        print "\n[!] Geolocation complete for %s" % tgt
    if city and region:
        if o:
            print "\tCity: %s, %s" % (city.encode('utf8'), region.encode('utf8'))
            of.write("\tCity: %s, %s\n" % (city.encode('utf8'), region.encode('utf8')))
        else:
            print "\tCity: %s, %s" % (city.encode('utf8'), region.encode('utf8'))
    if country:
        if o:
            print "\tCountry: %s" % country
            of.write("\tCountry: %s\n" % country)
        else:
            print "\tCountry: %s" % country
    if metro:
        if o:
            print "\tMetro Area: %s" % metro
            of.write("\tMetro Area: %s\n" % metro)
        else:
            print "\tMetro Area: %s" % metro
    if areacode:
        if o:
            print "\tArea Code: %s" % areacode
            of.write("\tArea Code: %s\n" % areacode)
        else:
            print "\tArea Code: %s" % areacode
    if lat and lon:
        gmap = 'https://maps.google.com/maps?q=loc:%s,%s' % (repr(lat), repr(lon))
        if o:
            print "\tLatitude: %s \t Longitude: %s" % (repr(lat), repr(lon))
            of.write("\tLatitude: %s \t Longitude: %s\n" % (repr(lat), repr(lon)))
        else:
            print "\tLatitude: %s \t Longitude: %s" % (repr(lat), repr(lon))
        if o:
            print "\tGoogle Maps Link: %s" % gmap
            of.write("\tGoogle Maps Link: %s\n" % gmap)
        else:
            print "\tGoogle Maps Link: %s" % gmap
    if o:
        of.write("%s\n" % delim)
        of.close()


def parsewhois(searchstring, whodata, whotype):
    if whotype == 'py':
        try:
            dstring = '%s: .*' % searchstring
            data = re.findall(dstring, whodata.text)
            sstring = '%s: ' % searchstring
            data[0] = re.sub(sstring, '', data[0])
            return data
        except IndexError:
            return False
    if whotype == 'local':
        try:
            dstring = '%s: .*' % searchstring
            data = re.findall(dstring, whodata)
            sstring = '%s:\s+' % searchstring
            if len(data) > 1:
                for i in range(0,len(data)):
                    data[i] = re.sub(sstring, '', data[i])
            else:
                data[0] = re.sub(sstring, '', data[0])
            return data
        except IndexError:
            return False


def whoistarget(tgt, ofile, o):
    if o:
        of = open(ofile, 'a')
        delim = "=" * 60
        of.write("%s\n" % delim)
    w = whois.whois(tgt)
    try:
        lw = subprocess.check_output(['whois', tgt, '2>/dev/null'])
    except subprocess.CalledProcessError:
        lw = False
    if w.domain_name:
        domain = w.domain_name[0]
    else:
        domain = False
    if w.creation_date:
        try:
            created = w.creation_date[1]
        except TypeError:
            created = w.creation_date
    else:
        created = False
    if w.updated_date:
        try:
            updated = w.updated_date[1]
        except TypeError:
            updated = w.updated_date
    else:
        updated = False
    if w.expiration_date:
        try:
            expires = w.expiration_date[1]
        except TypeError:
            expires = w.expiration_date
    else:
        expires = False
    if w.registrar:
        registrar = w.registrar[0]
    else:
        registrar = False
    if w.status:
        status = w.status
    else:
        status = False
    reg = dict()
    admin = dict()
    tech = dict()
    org = dict()
    orgnoc = dict()
    orgabuse = dict()
    orgtech = dict()
    if lw:
        org['name'] = parsewhois('OrgName', lw, 'local')
    else:
        org['name'] = parsewhois('OrgName', w, 'py')
    if lw:
        org['cidr'] = parsewhois('CIDR', lw, 'local')
    else:
        org['cidr'] = parsewhois('CIDR', w, 'py')
    if lw:
        org['address'] = parsewhois('Address', lw, 'local')
    else:
        org['address'] = parsewhois('Address', w, 'py')
    if lw:
        org['city'] = parsewhois('StateProv', lw, 'local')
    else:
        org['city'] = parsewhois('StateProv', w, 'py')
    if lw:
        org['country'] = parsewhois('Country', lw, 'local')
    else:
        org['country'] = parsewhois('Country', w, 'py')
    if lw:
        org['regdate'] = parsewhois('RegDate', lw, 'local')
    else:
        org['regdate'] = parsewhois('RegDate', w, 'py')
    if lw:
        org['updated'] = parsewhois('Updated', lw, 'local')
    else:
        org['updated'] = parsewhois('Updated', w, 'py')
    if lw:
        orgnoc['name'] = parsewhois('OrgNOCName', lw, 'local')
    else:
        orgnoc['name'] = parsewhois('OrgNOCName', w, 'py')
    if lw:
        orgnoc['phone'] = parsewhois('OrgNOCPhone', lw, 'local')
    else:
        orgnoc['phone'] = parsewhois('OrgNOCPhone', w, 'py')
    if lw:
        orgnoc['email'] = parsewhois('OrgNOCEmail', lw, 'local')
    else:
        orgnoc['email'] = parsewhois('OrgNOCEmail', w, 'py')
    if lw:
        orgabuse['name'] = parsewhois('OrgAbuseName', lw, 'local')
    else:
        orgabuse['name'] = parsewhois('OrgAbuseName', w, 'py')
    if lw:
        orgabuse['phone'] = parsewhois('OrgAbusePhone', lw, 'local')
    else:
        orgabuse['phone'] = parsewhois('OrgAbusePhone', w, 'py')
    if lw:
        orgabuse['email'] = parsewhois('OrgAbuseEmail', lw, 'local')
    else:
        orgabuse['email'] = parsewhois('OrgAbuseEmail', w, 'py')
    if lw:
        orgtech['name'] = parsewhois('OrgTechName', lw, 'local')
    else:
        orgtech['name'] = parsewhois('OrgTechName', w, 'py')
    if lw:
        orgtech['phone'] = parsewhois('OrgTechPhone', lw, 'local')
    else:
        orgtech['phone'] = parsewhois('OrgTechPhone', w, 'py')
    if lw:
        orgtech['email'] = parsewhois('OrgTechEmail', lw, 'local')
    else:
        orgtech['email'] = parsewhois('OrgTechEmail', w, 'py')
    if lw:
        reg['name'] = parsewhois('Registrant Name', lw, 'local')
    else:
        reg['name'] = parsewhois('Registrant Name', w, 'py')
    if lw:
        reg['org'] = parsewhois('Registrant Organization', lw, 'local')
    else:
        reg['org'] = parsewhois('Registrant Organization', w, 'py')
    if lw:
        reg['phone'] = parsewhois('Registrant Phone', lw, 'local')
    else:
        reg['phone'] = parsewhois('Registrant Phone', w, 'py')
    if lw:
        reg['email'] = parsewhois('Registrant Email', lw, 'local')
    else:
        reg['email'] = parsewhois('Registrant Email', w, 'py')
    if lw:
        reg['street'] = parsewhois('Registrant Street', lw, 'local')
    else:
        reg['street'] = parsewhois('Registrant Street', w, 'py')
    if lw:
        reg['city'] = parsewhois('Registrant City', lw, 'local')
    else:
        reg['city'] = parsewhois('Registrant City', w, 'py')
    if lw:
        reg['state'] = parsewhois('Registrant State/Province', lw, 'local')
    else:
        reg['state'] = parsewhois('Registrant State/Province', w, 'py')
    if lw:
        reg['country'] = parsewhois('Registrant Country', lw, 'local')
    else:
        reg['country'] = parsewhois('Registrant Country', w, 'py')
    if lw:
        admin['name'] = parsewhois('Admin Name', lw, 'local')
    else:
        admin['name'] = parsewhois('Admin Name', w, 'py')
    if lw:
        admin['org'] = parsewhois('Admin Organization', lw, 'local')
    else:
        admin['org'] = parsewhois('Admin Organization', w, 'py')
    if lw:
        admin['phone'] = parsewhois('Admin Phone', lw, 'local')
    else:
        admin['phone'] = parsewhois('Admin Phone', w, 'py')
    if lw:
        admin['email'] = parsewhois('Admin Email', lw, 'local')
    else:
        admin['email'] = parsewhois('Admin Email', w, 'py')
    if lw:
        admin['street'] = parsewhois('Admin Street', lw, 'local')
    else:
        admin['street'] = parsewhois('Admin Street', w, 'py')
    if lw:
        admin['city'] = parsewhois('Admin City', lw, 'local')
    else:
        admin['city'] = parsewhois('Admin City', w, 'py')
    if lw:
        admin['state'] = parsewhois('Admin State/Province', lw, 'local')
    else:
        admin['state'] = parsewhois('Admin State/Province', w, 'py')
    if lw:
        admin['country'] = parsewhois('Admin Country', lw, 'local')
    else:
        admin['country'] = parsewhois('Admin Country', w, 'py')
    if lw:
        tech['name'] = parsewhois('Tech Name', lw, 'local')
    else:
        tech['name'] = parsewhois('Tech Name', w, 'py')
    if lw:
        tech['org'] = parsewhois('Tech Organization', lw, 'local')
    else:
        tech['org'] = parsewhois('Tech Organization', w, 'py')
    if lw:
        tech['phone'] = parsewhois('Tech Phone', lw, 'local')
    else:
        tech['phone'] = parsewhois('Tech Phone', w, 'py')
    if lw:
        tech['email'] = parsewhois('Tech Email', lw, 'local')
    else:
        tech['email'] = parsewhois('Tech Email', w, 'py')
    if lw:
        tech['street'] = parsewhois('Tech Street', lw, 'local')
    else:
        tech['street'] = parsewhois('Tech Street', w, 'py')
    if lw:
        tech['city'] = parsewhois('Tech City', lw, 'local')
    else:
        tech['city'] = parsewhois('Tech City', w, 'py')
    if lw:
        tech['state'] = parsewhois('Tech State/Province', lw, 'local')
    else:
        tech['state'] = parsewhois('Tech State/Province', w, 'py')
    if lw:
        tech['country'] = parsewhois('Tech Country', lw, 'local')
    else:
        tech['country'] = parsewhois('Tech Country', w, 'py')
    if o:
        print "\n[!] Whois data for %s" % tgt
        of.write("\n[!] Whois data for %s\n" % tgt)
    else:
        print "\n[!] Whois data for %s" % tgt
    if domain:
        if o:
            print "\tDomain Name: \t%s" % domain
            of.write("\tDomain Name: \t%s\n" % domain)
        else:
            print "\tDomain Name: \t%s" % domain
    if created:
        if o:
            print "\tCreated on: \t%s" % created
            of.write("\tCreated on: \t%s\n" % created)
        else:
            print "\tCreated on: \t%s" % created
    if updated:
        if o:
            print "\tUpdated on: \t%s" % updated
            of.write("\tUpdated on: \t%s\n" % updated)
        else:
            print "\tUpdated on: \t%s" % updated
    if expires:
        if o:
            print "\tExpires on: \t%s" % expires
            of.write("\tExpires on: \t%s\n" % expires)
        else:
            print "\tExpires on: \t%s" % expires
    if registrar:
        if o:
            print "\tRegistrar: \t%s" % registrar
            of.write("\tRegistrar: \t%s\n" % registrar)
        else:
            print "\tRegistrar: \t%s" % registrar
    if status:
        if o:
            print "\tStatus: \t%s" % w.status[0]
            of.write("\tStatus: \t%s\n" % w.status[0])
        else:
            print "\tStatus: \t%s" % w.status[0]
        for s in w.status[1:]:
            if o:
                print "\t\t\t%s" % s
                of.write("\t\t\t%s\n" % s)
            else:
                print "\t\t\t%s" % s
    if reg['name'] or reg['phone'] or reg['email'] or reg['street'] or (reg['city'] and reg['state'] and reg['country']):
        if o:
            print "\n[+] Whois Registrant Info"
            of.write("\n[+] Whois Registrant Info\n")
        else:
            print "\n[+] Whois Registrant Info"
        if reg['name'][0]:
            if o:
                print "\tName: \t\t%s" % reg['name'][0]
                of.write("\tName: \t\t%s\n" % reg['name'][0])
            else:
                print "\tName: \t\t%s" % reg['name'][0]
        if reg['phone'][0]:
            if o:
                print "\tPhone: \t\t%s" % reg['phone'][0]
                of.write("\tPhone: \t\t%s\n" % reg['phone'][0])
            else:
                print "\tPhone: \t\t%s" % reg['phone'][0]
        if reg['email'][0]:
            if o:
                print "\tEmail: \t\t%s" % reg['email'][0]
                of.write("\tEmail: \t\t%s\n" % reg['email'][0])
            else:
                print "\tEmail: \t\t%s" % reg['email'][0]
        if reg['street'][0]:
            if o:
                print "\tAddress: \t%s" % reg['street'][0]
                of.write("\tAddress: \t%s\n" % reg['street'][0])
            else:
                print "\tAddress: \t%s" % reg['street'][0]
        if reg['city'][0] and reg['state'][0] and reg['country'][0]:
            if o:
                print "\t\t\t%s, %s. %s" % (reg['city'][0], reg['state'][0], reg['country'][0])
                of.write("\t\t\t%s, %s. %s\n" % (reg['city'][0], reg['state'][0], reg['country'][0]))
            else:
                print "\t\t\t%s, %s. %s" % (reg['city'][0], reg['state'][0], reg['country'][0])
    if admin['name'] or admin['phone'] or admin['email'] or admin['street'] or (admin['city'] and admin['state'] and admin['country']):
        if o:
            print "\n[+] Whois Admin Info"
            of.write("\n[+] Whois Admin Info\n")
        else:
            print "\n[+] Whois Admin Info"
        if admin['name'][0]:
            if o:
                print "\tName: \t\t%s" % admin['name'][0]
                of.write("\tName: \t\t%s\n" % admin['name'][0])
            else:
                print "\tName: \t\t%s" % admin['name'][0]
        if admin['phone'][0]:
            if o:
                print "\tPhone: \t\t%s" % admin['phone'][0]
                of.write("\tPhone: \t\t%s\n" % admin['phone'][0])
            else:
                print "\tPhone: \t\t%s" % admin['phone'][0]
        if admin['email'][0]:
            if o:
                print "\tEmail: \t\t%s" % admin['email'][0]
                of.write("\tEmail: \t\t%s\n" % admin['email'][0])
            else:
                print "\tEmail: \t\t%s" % admin['email'][0]
        if admin['street'][0]:
            if o:
                print "\tAddress: \t%s" % admin['street'][0]
                of.write("\tAddress: \t%s\n" % admin['street'][0])
            else:
                print "\tAddress: \t%s" % admin['street'][0]
        if admin['city'][0] and admin['state'][0] and admin['country'][0]:
            if o:
                print "\t\t\t%s, %s. %s" % (admin['city'][0], admin['state'][0], admin['country'][0])
                of.write("\t\t\t%s, %s. %s\n" % (admin['city'][0], admin['state'][0], admin['country'][0]))
            else:
                print "\t\t\t%s, %s. %s" % (admin['city'][0], admin['state'][0], admin['country'][0])
    if tech['name'] or tech['phone'] or tech['email'] or tech['street'] or (tech['city'] and tech['state'] and tech['country']):
        if o:
            print "\n[+] Whois Tech Info"
            of.write("\n[+] Whois Tech Info\n")
        else:
            print "\n[+] Whois Tech Info"
        if tech['name'][0]:
            if o:
                print "\tName: \t\t%s" % tech['name'][0]
                of.write("\tName: \t\t%s\n" % tech['name'][0])
            else:
                print "\tName: \t\t%s" % tech['name'][0]
        if tech['phone'][0]:
            if o:
                print "\tPhone: \t\t%s" % tech['phone'][0]
                of.write("\tPhone: \t\t%s\n" % tech['phone'][0])
            else:
                print "\tPhone: \t\t%s" % tech['phone'][0]
        if tech['email'][0]:
            if o:
                print "\tEmail: \t\t%s" % tech['email'][0]
                of.write("\tEmail: \t\t%s\n" % tech['email'][0])
            else:
                print "\tEmail: \t\t%s" % tech['email'][0]
        if tech['street'][0]:
            if o:
                print "\tAddress: \t%s" % tech['street'][0]
                of.write("\tAddress: \t%s\n" % tech['street'][0])
            else:
                print "\tAddress: \t%s" % tech['street'][0]
        if tech['city'][0] and tech['state'][0] and tech['country'][0]:
            if o:
                print "\t\t\t%s, %s. %s" % (tech['city'][0], tech['state'][0], tech['country'][0])
                of.write("\t\t\t%s, %s. %s\n" % (tech['city'][0], tech['state'][0], tech['country'][0]))
            else:
                print "\t\t\t%s, %s. %s" % (tech['city'][0], tech['state'][0], tech['country'][0])
    if org['name'] or org['cidr'] or (org['address'] and org['city'] and org['country']) or org['regdate'] or org['updated']:
        if o:
            print "\n[!] Whois Organization Info"
            of.write("\n[!] Whois Organization Info\n")
        else:
            print "\n[!] Whois Organization Info"
        if len(org['name']) > 1:
            for i in range(0,len(org['name'])):
                if o:
                    print "\n[+] Organization %s" % str(i + 1)
                    of.write("\n[+] Organization %s\n" % str(i + 1))
                else:
                    print "\n[+] Organization %s" % str(i + 1)
                if org['name'][i]:
                    if o:
                        print "\tName: \t\t%s" % org['name'][i]
                        of.write("\tName: \t\t%s\n" % org['name'][i])
                    else:
                        print "\tName: \t\t%s" % org['name'][i]
                if org['cidr'][i]:
                    if o:
                        print "\tCIDR: \t\t%s" % org['cidr'][i]
                        of.write("\tCIDR: \t\t%s\n" % org['cidr'][i])
                    else:
                        print "\tCIDR: \t\t%s" % org['cidr'][i]
                if org['regdate'][i]:
                    if o:
                        print "\tRegister Date: \t%s" % org['regdate'][i]
                        of.write("\tRegister Date: \t%s\n" % org['regdate'][i])
                    else:
                        print "\tRegister Date: \t%s" % org['regdate'][i]
                if org['updated'][i]:
                    if o:
                        print "\tLast Updated: \t%s" % org['updated'][i]
                        of.write("\tLast Updated: \t%s\n" % org['updated'][i])
                    else:
                        print "\tLast Updated: \t%s" % org['updated'][i]
                if org['address'][i] and org['city'][i] and org['country'][i]:
                    if o:
                        print "\t\t\t%s, %s. %s" % (org['address'][i], org['city'][i], org['country'][i])
                        of.write("\t\t\t%s, %s. %s\n" % (org['address'][i], org['city'][i], org['country'][i]))
                    else:
                        print "\t\t\t%s, %s. %s" % (org['address'][i], org['city'][i], org['country'][i])
                try:
                    if orgnoc['name'][i] or orgnoc['phone'][i] or orgnoc['email'][i]:
                        if o:
                            print "\n\t-NOC Info"
                            of.write("\n\t-NOC Info\n")
                        else:
                            print "\n\t-NOC Info"
                        if orgnoc['name'][i]:
                            if o:
                                print "\tName: \t\t%s" % orgnoc['name'][i]
                                of.write("\tName: \t\t%s\n" % orgnoc['name'][i])
                            else:
                                print "\tName: \t\t%s" % orgnoc['name'][i]
                        if orgnoc['phone'][i]:
                            if o:
                                print "\tPhone: \t\t%s" % orgnoc['phone'][i]
                                of.write("\tPhone: \t\t%s\n" % orgnoc['phone'][i])
                            else:
                                print "\tPhone: \t\t%s" % orgnoc['phone'][i]
                        if orgnoc['email'][i]:
                            if o:
                                print "\tEmail: \t\t%s" % orgnoc['email'][i]
                                of.write("\tEmail: \t\t%s\n" % orgnoc['email'][i])
                            else:
                                print "\tEmail: \t\t%s" % orgnoc['email'][i]
                except IndexError:
                    pass
                try:
                    if orgabuse['name'][i] or orgabuse['phone'][i] or orgabuse['email'][i]:
                        if o:
                            print "\n\t-Abuse Info"
                            of.write("\n\t-Abuse Info\n")
                        else:
                            print "\n\t-Abuse Info"
                        if orgabuse['name'][i]:
                            if o:
                                print "\tName: \t\t%s" % orgabuse['name'][i]
                                of.write("\tName: \t\t%s\n" % orgabuse['name'][i])
                            else:
                                print "\tName: \t\t%s" % orgabuse['name'][i]
                        if orgabuse['phone'][i]:
                            if o:
                                print "\tPhone: \t\t%s" % orgabuse['phone'][i]
                                of.write("\tPhone: \t\t%s\n" % orgabuse['phone'][i])
                            else:
                                print "\tPhone: \t\t%s" % orgabuse['phone'][i]
                        if orgabuse['email'][i]:
                            if o:
                                print "\tEmail: \t\t%s" % orgabuse['email'][i]
                                of.write("\tEmail: \t\t%s\n" % orgabuse['email'][i])
                            else:
                                print "\tEmail: \t\t%s" % orgabuse['email'][i]
                except IndexError:
                    pass
                try:
                    if orgtech['name'][i] or orgtech['phone'][i] or orgtech['email'][i]:
                        if o:
                            print "\n\t-Tech Info"
                            of.write("\n\t-Tech Info\n")
                        else:
                            print "\n\t-Tech Info"
                        if orgtech['name'][i]:
                            if o:
                                print "\tName: \t\t%s" % orgtech['name'][i]
                                of.write("\tName: \t\t%s\n" % orgtech['name'][i])
                            else:
                                print "\tName: \t\t%s" % orgtech['name'][i]
                        if orgtech['phone'][i]:
                            if o:
                                print "\tPhone: \t\t%s" % orgtech['phone'][i]
                                of.write("\tPhone: \t\t%s\n" % orgtech['phone'][i])
                            else:
                                print "\tPhone: \t\t%s" % orgtech['phone'][i]
                        if orgtech['email'][i]:
                            if o:
                                print "\tEmail: \t\t%s" % orgtech['email'][i]
                                of.write("\tEmail: \t\t%s\n" % orgtech['email'][i])
                            else:
                                print "\tEmail: \t\t%s" % orgtech['email'][i]
                except IndexError:
                    pass
        else:
            if org['name'][0]:
                if o:
                    print "\tName: \t\t%s" % org['name'][0]
                    of.write("\tName: \t\t%s\n" % org['name'][0])
                else:
                    print "\tName: \t\t%s" % org['name'][0]
            if org['cidr'][0]:
                if o:
                    print "\tCIDR: \t\t%s" % org['cidr'][0]
                    of.write("\tCIDR: \t\t%s\n" % org['cidr'][0])
                else:
                    print "\tCIDR: \t\t%s" % org['cidr'][0]
            if org['regdate'][0]:
                if o:
                    print "\tRegister Date: \t\t%s" % org['regdate'][0]
                    of.write("\tRegister Date: \t\t%s\n" % org['regdate'][0])
                else:
                    print "\tRegister Date: \t\t%s" % org['regdate'][0]
            if org['updated'][0]:
                if o:
                    print "\tLast Updated: \t\t%s" % org['updated'][0]
                    of.write("\tLast Updated: \t\t%s\n" % org['updated'][0])
                else:
                    print "\tLast Updated: \t\t%s" % org['updated'][0]
            if org['address'][0] and org['city'][0] and org['country'][0]:
                if o:
                    print "\t\t\t%s, %s. %s" % (org['address'][0], org['city'][0], org['country'][0])
                    of.write("\t\t\t%s, %s. %s\n" % (org['address'][0], org['city'][0], org['country'][0]))
                else:
                    print "\t\t\t%s, %s. %s" % (org['address'][0], org['city'][0], org['country'][0])
            if orgnoc['name'][0] or orgnoc['phone'][0] or orgnoc['email'][0]:
                if o:
                    print "\n[+] Whois Organization NOC Info"
                    of.write("\n[+] Whois Organization NOC Info\n")
                else:
                    print "\n[+] Whois Organization NOC Info"
                if orgnoc['name'][0]:
                    of.write("\tName: \t\t%s\n" % orgnoc['name'][0])
                if orgnoc['phone'][0]:
                    of.write("\tPhone: \t\t%s\n" % orgnoc['phone'][0])
                if orgnoc['email'][0]:
                    of.write("\tEmail: \t\t%s\n" % orgnoc['email'][0])
            if orgabuse['name'][0] or orgabuse['phone'][0] or orgabuse['email'][0]:
                if o:
                    print "\n[+] Whois Organization Abuse Info"
                    of.write("\n[+] Whois Organization Abuse Info\n")
                else:
                    print "\n[+] Whois Organization Abuse Info"
                if orgabuse['name'][0]:
                    if o:
                        print "\tName: \t\t%s" % orgabuse['name'][0]
                        of.write("\tName: \t\t%s\n" % orgabuse['name'][0])
                    else:
                        print "\tName: \t\t%s" % orgabuse['name'][0]
                if orgabuse['phone'][0]:
                    if o:
                        print "\tPhone: \t\t%s" % orgabuse['phone'][0]
                        of.write("\tPhone: \t\t%s\n" % orgabuse['phone'][0])
                    else:
                        print "\tPhone: \t\t%s" % orgabuse['phone'][0]
                if orgabuse['email'][0]:
                    if o:
                        print "\tEmail: \t\t%s" % orgabuse['email'][0]
                        of.write("\tEmail: \t\t%s\n" % orgabuse['email'][0])
                    else:
                        print "\tEmail: \t\t%s" % orgabuse['email'][0]
            if orgtech['name'][0] or orgtech['phone'][0] or orgtech['email'][0]:
                if o:
                    print "\n[+] Whois Organization Tech Info"
                    of.write("\n[+] Whois Organization Tech Info\n")
                else:
                    print "\n[+] Whois Organization Tech Info"
                if orgtech['name'][0]:
                    if o:
                        print "\tName: \t\t%s" % orgtech['name'][0]
                        of.write("\tName: \t\t%s\n" % orgtech['name'][0])
                    else:
                        print "\tName: \t\t%s" % orgtech['name'][0]
                if orgtech['phone'][0]:
                    if o:
                        print "\tPhone: \t\t%s" % orgtech['phone'][0]
                        of.write("\tPhone: \t\t%s\n" % orgtech['phone'][0])
                    else:
                        print "\tPhone: \t\t%s" % orgtech['phone'][0]
                if orgtech['email'][0]:
                    if o:
                        print "\tEmail: \t\t%s" % orgtech['email'][0]
                        of.write("\tEmail: \t\t%s\n" % orgtech['email'][0])
                    else:
                        print "\tEmail: \t\t%s" % orgtech['email'][0]
    if o:
        of.close()


#Setup argparse options
parser = argparse.ArgumentParser(conflict_handler='resolve')
taropts = parser.add_argument_group('Target Options')
taropts.add_argument('-t', '--target', dest='target', help='Enter a target to geolocate')
taropts.add_argument('-l', '--list', dest='tlist', help='Enter a file containing a list of IP\'s to geolocate')
main = parser.add_argument_group('Main Options')
main.add_argument('-w', '--whois', dest='who', action="store_true", help='Get whois data on the target')
main.add_argument('-d', '--dat', dest='dat', help='Specify a GeoIP dat file')
main.add_argument('-o', '--output', dest='output', help='Specify a GeoIP dat file')
hopts = parser.add_argument_group('Help')
hopts.add_argument('-h', '--help', dest='help', action='store_true', help='Show this message and exit')

#Assign args
args = parser.parse_args()
target = args.target
tlist = args.tlist
who = args.who
dat = args.dat
outfile = args.output
h = args.help
geodat = ''

#Check if help was specified
if h:
    parser.print_help()
    exit(0)

#Check for target
if not target and not tlist:
    parser.print_help()
    print "\n[!] Error, you need to specify a single target with -t or a target list with -l\n"
    exit(1)

if not outfile:
    #This is just a placeholder and does not get used
    outfile = "geosnipeout.txt"

#Check id dat was specified and validate as a file
if dat:
    if os.path.isfile(dat):
        geodat = dat
    else:
        print "\n[!] Error! The dat file you specified does not exist! Check the path and try again!"
        exit(1)
else:
    #hardcoded for my system
    #this file can be downloaded from http://geolite.maxmind.com/download/geoip/database/GeoLiteCity.dat.gz
    geodat = '/opt/geoip/GeoLiteCity.dat'

geodb = pygeoip.GeoIP(geodat)

if __name__ == '__main__':
    if tlist:
        if os.path.isfile(tlist):
            with open(tlist) as f:
                targets = f.readlines()
                for targ in targets:
                    targ = targ.strip()
                    if who:
                        if outfile:
                            whoistarget(targ, outfile, True)
                            geosnipe(targ, outfile, True)
                        else:
                            whoistarget(targ, outfile, False)
                            geosnipe(targ, outfile, False)
                    else:
                        if outfile:
                            geosnipe(targ, outfile, True)
                        else:
                            geosnipe(targ, outfile, False)
        else:
            print "\n[!] Error! The target file you listed does not exist. Check the path and try again!"
            exit(1)
    else:
        if who:
            if outfile:
                whoistarget(target, outfile, True)
                geosnipe(target, outfile, True)
            else:
                whoistarget(target, outfile, False)
                geosnipe(target, outfile, False)
        else:
            if outfile:
                geosnipe(target, outfile, True)
            else:
                geosnipe(target, outfile, False)