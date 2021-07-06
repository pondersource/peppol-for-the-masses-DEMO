import requests
from django.conf import settings

def qbo_query(access_token, realm_id, table):
    """[summary]
    
    """
    
    if settings.ENVIRONMENT == 'production':
        base_url = settings.QBO_BASE_PROD
    else:
        base_url =  settings.QBO_BASE_SANDBOX

    route = '/v3/company/{0}/query?query=select * from {1} maxresults 20&minorversion=59'.format(realm_id, table)
    auth_header = 'Bearer {0}'.format(access_token)
    headers = {
        'Authorization': auth_header, 
        'Accept': 'application/json'
    }
    return requests.get('{0}{1}'.format(base_url, route), headers=headers)

    
