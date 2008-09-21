#!/usr/bin/env python
# coding: utf-8

""" Supplierplan.at reader """
import sys
import urllib
import urllib2
from optparse import OptionParser

try:
    from BeautifulSoup import BeautifulSoup
except ImportError:
    print 'This script requires BeautifulSoup to run\nGet it at' \
          'http://www.crummy.com/software/BeautifulSoup/'


VERSION = '%prog 1.0'
USAGE = 'Usage: %prog -s YOURSCHOOLID -c YOURCLASS -u USERNAME -p PASSWORD'

parser = OptionParser(usage=USAGE, version=VERSION)
parser.add_option('-s', '--schoolid', dest='school')
parser.add_option('-c', '--class', dest='cl')
parser.add_option('-u', '--user', dest='usr')
parser.add_option('-p', '--password', dest='pw')
(options, args) = parser.parse_args()

class SupplierplanReader:
    """ Fetches, parses and outputs data from supplierplan.at"""

    BREAKSTRING = 'Keine Supplierungen gefunden...'
    LOGINFAIL = 'supplierplan login'

    def __init__(self, school, cl, usr, pw):
        self.school = school
        self.cl = cl
        self.usr = usr
        self.pw = pw
        self.struct = {}
        self.html = ''

        # Get the HTML
        try:
            url = 'http://admin.supplierplan.at/cgi-bin/supp.pl?' \
                  'find=%s&id=%s&user=%s&pwd=%s' % (cl, school, usr, pw)
            hp = urllib2.urlopen(url)
            self.html = hp.read()
            if self.BREAKSTRING in self.html:
                sys.exit(BREAKSTRING)
            elif self.LOGINFAIL in self.html:
                sys.exit('Login into Supplierplan.at failed')
        except urllib2.HTTPError:
            sys.exit("Couldn't retrieve URL")
        except urllib2.URLError:
            sys.exit('URL not found')

    def proc_html(self):
        # modify html output so we can search for fonts safely
        self.html = self.html.replace(' <td align="right">&nbsp;</td>',
                            '<td align="right"><font>&nbsp;</font></td>') \
                    .replace('<td align="center">&nbsp;</td>',
                             '<td align="center"><font>&nbsp;</font></td>')
        # Soupify it and get the table
        soup = BeautifulSoup(self.html).table
        # isolate only the tds
        table = soup('td', {'class': 'topline'})
        # now fetch the font tags
        font = soup.findAll('font')

        # content of fonts into list
        plan = [str(x.contents[0]) for x in font[9:]]

        # structure the plan = {day: supplierungen,}
        # and get the list positions/length of each day
        self.struct = {}
        pos_start = []
        i = 0
        for x in plan:
            if '<b>' in x:
                self.struct[x] = []
                pos_start.append(i)
            i += 1

        positions = []
        for x in pos_start:
            positions.append(x)
            positions.append(x+1)
        positions = positions[1:]
        positions.append(len(plan))

        # positions consist of beginning and end
        # zip them into tuples
        # Note: * is for eating non-completes
        positions = zip(*[positions[i::2] for i in xrange(2)])

        i = 0
        for x in pos_start:
            self.struct[plan[x]] = plan[positions[i][0]:positions[i][1]]
            # Readability instead of performance:
            # each entry per day consists of 8 items:
            # Class, Hour, Substitute, Subject, Room, Instead of (x2), Notes
            # zip them into tuples! (again ;D)
            # Result: {DAY: [(entry 1), (entry 2)],..}
            self.struct[plan[x]] = zip(*[self.struct[plan[x]][o::8] \
                                         for o in xrange(8)])
            i += 1

    def output(self):
        for x, y in self.struct.iteritems():
            print x.replace('<b>', '').replace('</b>', '')
            for z in y:
                for a in z:
                    a = a.replace(self.cl.upper(), '')
                    if 'nbsp' in a:
                        a = a.replace('&nbsp;', '-')
                    print a,
                print

    def __repr__(self):
        return '<SupplierplanReader>'

if options.school and options.cl and options.usr and options.pw:
    suppl = SupplierplanReader(options.school, options.cl, options.usr,
                               options.pw)
    suppl.proc_html()
    suppl.output()
else:
    sys.exit('Please check your input! You either forgot the ' \
             'school-id, username, password or your class')
