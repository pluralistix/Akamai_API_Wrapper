import json
import urllib
import urlparse
import sys

with open('cpcodes', 'r') as f:
    VALID_CPCODES = eval(f.read())


class JsonObject:
    def __init__(self, topurge, object_type='arl', domain='production', action='remove'):
        self.topurge = topurge
        self.data = {'objects': []}
        if object_type.lower().strip() in ('arl', 'cpcode'):
            self.type = object_type.lower().strip()
            self.data.update({'type': object_type.lower().strip()})
        else:
            print '%s as type is not allowed here' % object_type
            sys.exit(1)
        if domain.lower().strip() in ('production', 'staging'):
            self.data.update({'domain': domain.lower().strip()})
        else:
            print '%s as domain is not allowed here' % domain
            sys.exit(1)
        if action.lower().strip() in ('invalidate', 'remove'):
            self.data.update({'action': action.lower().strip()})
        else:
            print '%s as action is not allowed here' % action
            sys.exit(1)
        self.rework_data()

    def rework_data(self):
        mydata = self.data.get('objects')
        self.topurge = self.topurge.replace(',', '\n').replace(';', '\n').split('\n')
        if self.type == 'arl':
            [mydata.append(self.encode(x.strip())) for x in self.topurge]
        else:
            try:
                for cpcode in self.topurge:
                    cp = cpcode.strip().upper()
                    try:
                        cp = int(cp)
                        if cp in VALID_CPCODES.keys():
                            mydata.append(str(cp))
                        else:
                            print '%s is not a valid cpcode for your company' % cpcode
                            print 'valid are \n' + '\n'.join('%s -> %s' % tup for tup in list(VALID_CPCODES.items()))
                            sys.exit(1)
                    except ValueError:
                        cp = VALID_CPCODES.keys()[VALID_CPCODES.values().index(cp)]
                        mydata.append(str(cp))
            except (ValueError, IndexError):
                print '%s is not a valid cpcode for your company' % cpcode
                print 'valid are \n' + '\n'.join('%s -> %s' % tup for tup in list(VALID_CPCODES.items()))
                sys.exit(1)
        self.data.update({'objects': list(set(mydata))})

    def get_json(self):
        return json.dumps(self.data)

    @staticmethod
    def encode(string):
        scheme, netloc, path, qs, anchor = urlparse.urlsplit(string)
        path = urllib.quote(path, safe="%/:=&?~#+!$,;'@()*[]")
        qs = urllib.quote_plus(qs, safe="%/:=&?~#+!$,;'@()*[]")
        return urlparse.urlunsplit((scheme, netloc, path, qs, anchor))

    @staticmethod
    def print_cpcode():
        return VALID_CPCODES

    @staticmethod
    def transform_cpcode(cpcode):
        try:
            cpcode = int(cpcode)
            return VALID_CPCODES.get(cpcode)
        except (ValueError, TypeError) as e:
            return None