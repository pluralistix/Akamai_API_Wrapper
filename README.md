Akamai_API_Wrapper
==================

make it simple to access new akamai restfull api

examples

akamai_api_wrapper.py --do_purge -data testdata.txt (for purging the content of file testdata.txt - since no object_type is given, the content is assumend URLs)

akamai_api_wrapper.py --do_purge -data "www.foo.bar/test1, www.bar.foo/test2?me" (for purging www.foo.bar/test1 and www.bar.foo/test2?me)

akamai_api_wrapper.py --do_purge --object_type cpcode -data 12345 (for purging the content of the cpcode 12345)

akamai_api_wrapper.py --do_purge --object_type cpcode -data 12345 --send_mail_on_success True --email_recipients "sender@domain.org" (for purging the content of the cpcode 12345 and sending the response/result to the given email-address)

akamai_api_wrapper.py --do_purge --object_type cpcode -data FOO --domain staging (for purging the content of the cpcode FOO in staging, where FOO is a mapped cpcode for better reading and understanding)

akamai_api_wrapper.py --do_check_status -id XYZ

akamai_api_wrapper.py --do_check_queues
