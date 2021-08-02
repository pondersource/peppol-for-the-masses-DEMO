from zeep import Client
from requests import Session
from requests.auth import HTTPBasicAuth
from zeep.transports import Transport
from zeep.exceptions import Fault
from zeep.wsse.username import UsernameToken

# When you want zeep to build and return the XML instead of sending it to the server,
# you can use the Client.create_message() call.
# It requires the ServiceProxy as the first argument and the operation name as the second argument.

#node = client.create_message(client.service, 'myOperation', user='hi')
#
# try:
#
#     wsdl = 'http://www.soapclient.com/xml/soapresponder.wsdl'
#     session = Session()
#     session.auth = HTTPBasicAuth(username, password)
#     user_name_token = UsernameToken('username', 'password')
#     signature = Signature(private_key_filename, public_key_filename,optional_password)
#     client = Client(wsdl=wsdl,
#                     transport=Transport(session=session),
#                     wsse=Signature( private_key_filename, public_key_filename,optional_password))
#
# except Fault as fault:
#
#     parsed_fault_detail = client.wsdl.types.deserialize(fault.detail[0])
