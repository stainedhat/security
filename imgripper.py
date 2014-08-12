#!/usr/bin/python

import urllib2
import argparse
import os
import exifread
from bs4 import BeautifulSoup
from urlparse import urlsplit, urlparse


def findimages(url):
    try:
        html = urllib2.urlopen(url).read()
        soup = BeautifulSoup(html)
        imgs = soup.findAll('img')
        #print imgs
        return imgs
    except urllib2.HTTPError, e:
        print "[!] Something went very wrong!"
        print "[!] Error msg: %s" % e
        exit(0)


def ripimage(itag, url, outdir):
    imgsrc = itag['src']
    try:
        #this is to handle weird urls that append stuff after the jpg extension.
        #ran acrossed it on one site so I figure this can't hurt and will correct the issue if it happens
        if 'jpg' in imgsrc:
            imgsrc = imgsrc.split("jpg")[0] + 'jpg'
        elif 'jpeg' in imgsrc:
            imgsrc = imgsrc.split("jpeg")[0] + 'jpeg'
        elif 'png' in imgsrc:
            imgsrc = imgsrc.split("png")[0] + 'png'
        imgname = os.path.basename(urlsplit(imgsrc)[2])
        imgcontent = ''
        try:
            #handle links that are not absolute (may need more testing!)
            if "http" not in imgsrc:
                abpath = urlparse(url)[2]
                abpath = abpath.split('/')
                imgsrc = urlparse(url)[0] + "://" + urlparse(url)[1] + "/" + "/".join(abpath[1:-1]) + "/" + itag['src']
            imgcontent = urllib2.urlopen(imgsrc).read()
        except urllib2.HTTPError:
            imgsrc = urlparse(url)[0] + "://" + urlparse(url)[1] + itag['src']
            imgcontent = urllib2.urlopen(imgsrc).read()
        except urllib2.URLError, e:
            print "[!] There was an error with %s" % imgsrc
            print "[!] Error msg: %s" % e
        if not os.path.exists(outdir):
            os.mkdir(outdir)
        print "[+] Image found: " + imgname
        outpath = outdir + '/' + imgname
        imgfile = open(outpath, 'wb')
        imgfile.write(imgcontent)
        imgfile.close()
        return outpath, imgname
    except Exception, e:
        print "[!] There was an error with \'%s\'" % imgsrc
        print "[!] Error msg: %s" % e
        return '', ''


def pyexif(path, imgname, outdir):
    try:
        if path:
            i = open(path, 'rb')
            tags = exifread.process_file(i)
            i.close()
            data = '=' * 50 + '\n'
            data += '[!] Image Name = %s\n' % str(imgname)
            if len(tags) < 1:
                data += '[!] No data for this image\n'
            else:
                for tag in tags.keys():
                    if tag not in ('JPEGThumbnail', 'TIFFThumbnail', 'Filename', 'EXIF MakerNote'):
                        exif = tag.replace('EXIF ', '')
                        data += "%s: %s\n" % (exif, tags[tag])
            data += '=' * 50 + '\n'
            f = open('%s/exifdata.txt' % str(outdir), 'a')
            f.write(data)
            f.close()
    except:
        pass


def main():
    parser = argparse.ArgumentParser(epilog="Example: %(prog)s -u http://domain.com/index.html -o domain_images",
                                     description="%(prog)s accepts a URL as input and downloads all images located "
                                                 "on the page. It then generates exif data for all images and writes"
                                                 " it to a txt file for inspection.",
                                     conflict_handler='resolve')
    opts = parser.add_argument_group('Options')
    opts.add_argument('-u', '--url', help='URL of page to rip images from')
    opts.add_argument('-o', '--output', help="Directory name to store ripped images in. "
                                             "[Default is the domain name of the URL provided]")
    opts.add_argument('-h', '--help', dest='help', action='store_true', help='Prints this help message and exits')
    args = parser.parse_args()
    if args.help:
        parser.print_help()
        exit(0)
    url = args.url
    output = args.output
    if url is None:
        parser.print_help()
        print '\n[!] Error: ***** URL is required!! *****\n'
        exit(0)
    if not output:
        outdir = os.path.basename(urlsplit(url)[1])
    else:
        outdir = output
    imgtags = findimages(url)
    for imgtag in imgtags:
        path, imgname = ripimage(imgtag, url, outdir)
        pyexif(path, imgname, outdir)
    print "[+] Images saved to %s" % outdir
    print "[+] Exif data written to %s/exifdata.txt" % outdir

if __name__ == '__main__':
    main()
