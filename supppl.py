# coding: utf-8
import re
import sys
import urllib
import urllib2
import datetime

try:
    from BeautifulSoup import BeautifulSoup
except ImportError:
    print 'This library requires BeautifulSoup to work\nGet it at ' \
          'http://www.crummy.com/software/BeautifulSoup/'

class Supplierplan:
    """
    Supplierplan.at process library
    """

    URL = 'http://admin.supplierplan.at/cgi-bin/supp.pl?' \
          'find=%s&id=%s&user=%s&pwd=%s'
    BREAKSTRING = 'Keine Supplierungen gefunden...'
    LOGINFAIL = 'supplierplan login'

    def __init__(self, school=None, cl=None, usr=None, pw=None, auth=False,
                 proxy=None):
        self.school = school
        self.cl = cl
        self.usr = usr
        self.pw = pw
        self.struct = {}
        self.html = ''
        self.proxy = proxy
        self.auth = auth

        # check for proxies
        proxy_type = isinstance(proxy, dict)
        if not auth and proxy and not proxy_type:
            sys.exit('proxy must be a dictionary mapping scheme names to ' \
                     'proxy URLs\ne.g.: {"http": "http://wtf.com:8080"}')
        if auth and proxy and not proxy_type or auth and not proxy:
            sys.exit('proxy must be a dictionary containing a valid '\
                'username, password, port and host\n' \
                'e.g.: {"user": "username", "pass": "password", ' \
                '"host":"proxy.name.com", "port": 1337}')
        if auth and proxy and proxy_type:
            try:
                usr = proxy['user']
                pw = proxy['pass']
                host = proxy['host']
                port = proxy['port']

                # thx comp.lang.python
                proxy_support = urllib2.ProxyHandler(
                    {'http': 'http://%s:%s@%s:%d' % (usr, pw, host, port)})
                opener = urllib2.build_opener(proxy_support,
                                              urllib2.HTTPHandler)
                urllib2.install_opener(opener)
            except KeyError:
                sys.exit('proxy not containing all necessary informations')

        # Get the HTML
        try:
            url = self.URL % (cl, school, usr, pw)
            hp = urllib2.urlopen(url, proxy)
            self.html = hp.read()
            # check for failed login
            if self.LOGINFAIL in self.html:
                sys.exit('Login failed')
        except urllib2.HTTPError:
            sys.exit("Couldn't retrieve URL")
        except urllib2.URLError:
            sys.exit('URL not found')

    def __repr__(self):
        return '<Supplierplan>'

    def proc_html(self):
        """
        Processes the HTML from __init__

        returns a dict in the following format:
        {datetime-object: [(entry1), (entry2),], datetime-object2: ...}
        """
        # hacky'sh
        self.html = self.html.replace(
                            '<td align="right">&nbsp;</td>',
                            '<td align="right"><font>&nbsp;</font></td>') \
                   .replace('<td align="center">&nbsp;</td>',
                            '<td align="center"><font>&nbsp;</font></td>')
        self.html = self.html.split('<!-- Supplierungen Begin -->')[1] \
                             .split('<!-- Supplierungen Ende -->')[0]
        soup = BeautifulSoup(self.html).findAll('td', {'width': None,})

        # soup returns lists, merge them into one and fill empty lists
        rawplan = []
        for x in soup:
            # we only need the contents of every font tag
            # NOTE: days are inside <b> tags so they will stay a soup instance
            y = x.font.contents
            if y == []:
                y.append(u'&nbsp;')
            rawplan.append(y[0])

        # strip 'BEMERKUNG'
        rawplan = rawplan[1:]
        # delete class from list and create a new list
        p = re.compile('^\d[a-zA-Z]+')
        for i in xrange(len(rawplan)):
            if p.match(str(rawplan[i])):
                del rawplan[i]
                rawplan.insert(i, '-')
                rawplan.insert(i, '-')

        struct = {}
        parent = ''
        for a in rawplan:
            # Since days are still soup instances, we can easily build
            # a semantic dict
            if isinstance(a, basestring):
                if 'nbsp' in a or '-' in a or '?' in a:
                    struct[parent].append(None)
                else:
                    try:
                        struct[parent].append(int(a))
                    except ValueError:
                        struct[parent].append(a)
            else:
                # parents are date strings
                # so parents will become datetime objects
                datestring = a.contents[0]
                day, month, year = datestring[3:].split('.')
                dateobj = datetime.datetime(int(year), int(month), int(day))
                struct[dateobj] = []
                parent = dateobj

        # every entry per day consists of 8 items
        # this code groups them into tuples of 8
        for b, c in struct.iteritems():
            struct[b] = zip(*[c[i::9] for i in xrange(9)])
        return struct

    def check_supps(self):
        """
        Wrapper around proc_html

        Checks if any *supplierungen* could be found
        """
        if self.BREAKSTRING in self.html:
            return False
        else:
            return True
