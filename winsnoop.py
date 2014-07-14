__author__ = 'root'

from _winreg import *
import os
import argparse
import xml.etree.ElementTree as ET

def getmac(mac):
    addr = ""
    for x in mac:
        addr += ("%02x " % ord(x))
    addr = addr.strip(" ").replace(" ",":")[0:17]
    return addr

def findWifiInfo():
    ssids = {}
    reg = "SOFTWARE\Microsoft\Windows NT\CurrentVersion\NetworkList\Signatures\Unmanaged"
    key = OpenKey(HKEY_LOCAL_MACHINE, reg, 0, KEY_READ | KEY_WOW64_64KEY)
    for i in range(100):
        try:
            guid = EnumKey(key, i)
            netKey = OpenKey(key, str(guid))
            (n, addr, t) = EnumValue(netKey, 5)
            (n, name, t) = EnumValue(netKey, 4)
            mac = getmac(addr)
            ssid = str(name.strip())
            ssids[ssid] = mac
            #print '[!] SSID: ' + ssid + " MAC: " + mac
            CloseKey(netKey)
        except:
            break
    return ssids

def exportWifiProfiles(outfolder):
    passwords = {}
    try:
        os.system("netsh wlan export profile key=clear folder=\"%s\\\"" % outdir)
        print "[*] Wifi profiles have been exported to %s" % (outdir)
    except:
        print "[!] Could not export profiles!"
        return
    for root, dirs, file in os.walk(outdir):
        for file in files:
            if "Wi-Fi" in file:
                file = outfolder + file
                tree = ET.parse(file)
                root = tree.getroot()
                ssid = str(root[0].text.strip())
                print "[*] SSID: %s" % (ssid),
                for i in root.iter():
                    if "keyMaterial" in str(i):
                        passwords[ssid] = i.text
                        print " Password: %s" % (i.text)
    return passwords

def main():
    #setup args
    parser = argparse.ArgumentParser()
    parser.add_argument("-o", "--output", dest="outfolder", help="Output FOLDER to write results too. ie, C:\winsnoop\ "
                                                              "[Default is: %USERPROFILE%\AppData\Local\Temp\winsnoop\]")
    parser.add_argument("-w", "--wifi", dest="wifi", action="store_true", help="Scrape the system for wifi information such as SSIDs and Passwords")
    args = parser.parse_args()
    wifi = args.wifi
    outfolder = args.outfolder

    #setup output folder
    if not outfolder:
        home = os.getenv("USERPROFILE")
        outfolder = "%s\\AppData\\Local\\Temp\\winsnoop\\" % (home)
    try:
        if os.path.isdir(outfolder):
            pass
        else:
            os.mkdir(r"%s" % (outfolder))
    except:
        print "[!] Could not make output folder."
        print "[!] Leave output directory as default or specify the correct path! \n"
        exit()

    if wifi:
        ssids = findWifiInfo()
        passwords = exportWifiProfiles(outfolder)
        outfile = "Wifi_info.txt"
        outpath = outfolder + outfile
        for i in ssids.keys():
            if passwords[i]:
                f = open(r"%s" % (outpath), "a+")
                f.write("SSID: %s MAC: %s Password: %s \n" % (i, ssids[i], passwords[i]))
                f.close()
                print "SSID: %s MAC: %s Password: %s " % (i, ssids[i], passwords[i])
            else:
                f = open(r"%s" % (outpath), "a+")
                f.write("SSID: %s MAC: %s \n" % (i, ssids[i]))
                f.close()
                print "SSID: %s MAC: %s " % (i, ssids[i])

if __name__ == "__main__":
    main()














