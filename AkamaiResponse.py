import requests
import time
import json
from DateConverter import DateConverter
from JsonObject import JsonObject

class AkamaiResponse():
    def __init__(self, username, password, uri, method='GET', data=None, success=200):
        self.method = method
        self.uri = uri
        self.data = data
        self.success = success
        self.auth = (username, password)
        self.headers = {'content-type': 'application/json'}

    def get_response(self):
        r = requests.request(self.method, self.uri, auth=self.auth, headers=self.headers, data=self.data)
        message = self.uri + '\n\n'
        try:
            for x, y in r.json().iteritems():
                if 'Time' in str(x) and y is not None:
                    message += str(x) + ': ' + DateConverter.convert_date(y) + '\n'
                else:
                    message += str(x) + ': ' + str(y) + '\n'
        except ValueError:
            message += r.text
        return message, r

    def get_response_but_wait_for_purge_completion(self):
        message, r = self.get_response()
        orig_data = None
        seconds_to_wait = 10
        inprogress = True
        if self.method == 'POST' and r.status_code == self.success:
            orig_data = self.data
            self.success = 200
            self.uri = 'https://api.ccu.akamai.com' + r.json().get('progressUri')
            self.data = None
            self.method = 'GET'
            while inprogress:
                time.sleep(seconds_to_wait)
                message, r = self.get_response()
                inprogress = r.json().get('purgeStatus') == 'In-Progress' and self.success == r.status_code
                seconds_to_wait = r.json().get('pingAfterSeconds')
        subject, msg = self.build_response_message(r.json(), json.loads(orig_data))
        return subject, msg, r

    def build_response_message(self, response, orig_data):
        subject = 'Your Akamai content removal request (%s)' % response.get('purgeId')

        if orig_data.get('type').upper() == 'CPCODE':
            objects = '\n'.join(x + ' (' + JsonObject.transform_cpcode(x) + ')' for x in orig_data.get('objects'))
        else:
            objects = '\n'.join(orig_data.get('objects'))

        msg = 'This message confirms that your Akamai content removal request has been processed by all active servers on our network. Here are the details.\n\n'
        msg += 'ID:                %s\n' % response.get('purgeId')
        msg += 'Domain:            %s\n' % orig_data.get('domain')
        msg += 'Requestor:         %s\n' % response.get('submittedBy')
        msg += 'Submission time:   %s\n' % DateConverter.convert_date(response.get('submissionTime'))
        msg += 'Completion time:   %s\n' % DateConverter.convert_date(response.get('completionTime'))
        msg += '\n'
        msg += 'Content purged:\n\n'
        msg += '%s %s(s)\n\n%s' % (orig_data.get('action'), orig_data.get('type'), objects)

        return subject, msg