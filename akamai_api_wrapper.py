#!/usr/bin/env python


from JsonObject import JsonObject
from CustomFormatter import CustomFormatter
import os
import sys
import argparse
import textwrap
import requests
import smtplib
from email.mime.text import MIMEText
import getpass

with open('auth', 'r') as f:
    auth = eval(f.read())

purge_request_post_uri = 'https://api.ccu.akamai.com/ccu/v2/queues/default'
purge_queues_get_uri = 'https://api.ccu.akamai.com/ccu/v2/queues/default'

purge_status_get_uri = 'https://api.ccu.akamai.com/ccu/v2/purges/'


def set_credentials():
    return auth.get('username') if getattr(parsed_args, 'akamai_user') is None else getattr(parsed_args,
                                                                                            'akamai_user'), auth.get(
        'username') if getattr(parsed_args, 'akamai_password') is None else getattr(parsed_args, 'akamai_password')


def send_email_notification(message, subject):
    with open('email_settings', 'r') as f:
        email_settings = eval(f.read())
    sender = email_settings.get('default_sender')
    recipient = email_settings.get('default_recipient')
    if sender is not None:
        recipients = recipient if getattr(parsed_args, 'email_recipients') is None else getattr(parsed_args, 'email_recipients')
        if recipients is not None:
            msg = MIMEText(message)
            msg['Subject'] = subject
            s = smtplib.SMTP('localhost')
            msg['From'] = '%s <%s>' % (getpass.getuser(), sender)
            msg['To'] = recipients
            try:
                s.sendmail('"%s <%s>"' % (getpass.getuser(), sender), recipients.replace(';',',').split(','), msg.as_string())
            except Exception as e:
                print e
            s.quit()


def do_purge():
    data2purge = getattr(parsed_args, 'data2purge')
    if data2purge is None:
        print 'you MUST specify what to purge'
        sys.exit(1)
    if os.path.isfile(data2purge):
        f = open(data2purge)
        data2purge = f.read()
        f.close()

    data = JsonObject(data2purge, getattr(parsed_args, 'object_type'), getattr(parsed_args, 'domain'),
                      getattr(parsed_args, 'akamai_action')).get_json()

    do_request_and_handle_response(purge_request_post_uri, method='POST', data=data, success=201)


def do_check_status():
    purgeid = getattr(parsed_args, 'purgeid')
    if purgeid is None:
        print 'you MUST specify a purgeid'
        sys.exit(1)
    purgeid = purgeid.replace('/ccu/v2/purges/', '')

    do_request_and_handle_response(purge_status_get_uri + purgeid)


def do_check_queues():
    do_request_and_handle_response(purge_queues_get_uri)


def do_request_and_handle_response(uri, method='GET', data=None, success=200):
    r = requests.request(method, uri, auth=(username, password), headers={'content-type': 'application/json'},
                         data=data)
    msg = ''
    if r.status_code == success:
        if method == 'POST':
            progressuri = r.json().get('progressUri')
            progressuri = purge_status_get_uri + progressuri
            msg += '\nYou may want to follow the progress on\n' + progressuri
        for x, y in r.json().iteritems():
            msg += str(x) + ': ' + str(y) + '\n'
        msg = 'URL: ' + uri + '\nDATA: ' + (data if data is not None else 'None') + '\n\nRESULT: \n' + msg
        print msg
        if getattr(parsed_args, 'send_mail_on_success'):
            send_email_notification(msg, 'Akamai - Successfully called Akamai-API')
    else:
        print 'something went wrong. please check the message'
        try:
            for x, y in r.json().iteritems():
                msg += str(x) + ': ' + str(y) + '\n'
        except ValueError as e:
            msg = r.text
        msg = 'URL: ' + uri + '\nDATA: ' + (data if data is not None else 'None') + '\n\nRESULT: \n' + msg
        print msg
        if getattr(parsed_args, 'send_mail_on_error'):
            send_email_notification(msg, 'Akamai - Error while talking to Akamai-API')
        sys.exit(1)


def usage():
    return 'see some examples (at the bottom)'


def epilog(name):
    return textwrap.dedent('''\
        - file auth must be present and contain a dict with username and password e.g. {'username': 'test', 'password': 'pass'}
        - file cpcode must be present and contain a dict with cpode and human readable name for it e.g. {111: 'FOO', 222: 'BAR'}

        some examples
        --------------------------------
        %s --do_purge -data testdata.txt (for purging the content of file testdata.txt - since no object_type is given, the content is assumend URLs)
        %s --do_purge -data "www.foo.bar/test1, www.bar.foo/test2?me" (for purging www.foo.bar/test1 and www.bar.foo/test2?me)
        %s --do_purge --object_type cpcode -data 12345 (for purging the content of the cpcode 12345)
        %s --do_purge --object_type cpcode -data 12345 --send_mail_on_success True --email_recipients "sender@domain.org" (for purging the content of the cpcode 12345 and sending the response/result to the given email-address)
        %s --do_purge --object_type cpcode -data FOO --domain staging (for purging the content of the cpcode FOO in staging, where FOO is a mapped cpcode for better reading and understanding)
        %s --do_check_status
        %s --do_check_queues
        valid cpcodes are %s
        for more examples and possibilities refer to https://api.ccu.akamai.com/ccu/v2/docs/index.html#section_Reference and read the optional arguments from this program
    ''' % (name, name, name, name, name, name, name, JsonObject.print_cpcode()))


parser = argparse.ArgumentParser(epilog=epilog(sys.argv[0].split(os.path.sep)[-1]), usage=usage(),
                                 formatter_class=CustomFormatter)

parser.add_argument('--do_purge', dest='action', action='store_const', const=do_purge,
                    help='purge a list of urls/arls or cpcodes')
parser.add_argument('--do_check_status', dest='action', action='store_const', const=do_check_status,
                    help='check the status of a given purgeid')
parser.add_argument('--do_check_queues', dest='action', action='store_const', const=do_check_queues,
                    help='check the current queuelength')
parser.add_argument('--object_type', '-o', type=str, default='arl', metavar='arl or cpcode', choices=['arl', 'cpcode'],
                    help=' ')
parser.add_argument('--domain', '-d', type=str, default='production', metavar='production or staging',
                    choices=['production', 'staging'], help=' ')
parser.add_argument('--akamai_action', '-a', type=str, default='remove', metavar='remove or invalidate',
                    choices=['remove', 'invalidate'], help=' ')
parser.add_argument('--data2purge', '-data', default=None,
                    help='can be a file which contains the objects to purge or a list on the comand line')
parser.add_argument('--purgeid', '-id', type=str, default=None, metavar='to check', help=' ')
parser.add_argument('--send_mail_on_success', type=bool, default=False, metavar='send optional email on success',
                    help=' ')
parser.add_argument('--send_mail_on_error', type=bool, default=True, metavar='send optional email on error', help=' ')
parser.add_argument('--email_recipients', type=str, default=None, metavar='email addresses to send result to', help=' ')
parser.add_argument('--akamai_user', '-u', type=str, default=None, metavar='overwrite akamai user with this', help=' ')
parser.add_argument('--akamai_password', '-p', type=str, default=None, metavar='overwrite akamai password with this',
                    help=' ')

parsed_args = parser.parse_args()
if parsed_args.action is None:
    parser.parse_args(['-h'])
(username, password) = set_credentials()
parsed_args.action()
