#!/usr/bin/env python

__all__ = ['WosClient']

import suds as _suds

class WosClient():
    """Query the Web of Science.
       You must provide user and password only to user premium WWS service.

       with WosClient() as wos:
           results = wos.search(...)"""

    base_url = 'http://search.webofknowledge.com'
    auth_url = base_url + '/esti/wokmws/ws/WOKMWSAuthenticate?wsdl'
    search_url = base_url + '/esti/wokmws/ws/WokSearch?wsdl'

    def __init__(self, user=None, password=None, SID=None, close_on_exit=True):
        """Create the SOAP clients. user and password for premium access."""
        self._search = _suds.client.Client(self.search_url)
        self._auth = _suds.client.Client(self.auth_url)
        self._close_on_exit = close_on_exit
        self._SID = SID

        if user and password:
            authorization = ('%s:%s' % (user, password)).encode('base64')
            headers = {'Authorization': ('Basic %s' % authorization).strip()}
            self._auth.set_options(headers=headers)

    def __enter__(self):
        """Automatically connect when used with 'with' statements."""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """Close connection after closing the 'with' statement."""
        if self._close_on_exit:
            self.close()

    def __del__(self):
        """Close connection when deleting the object."""
        if self._close_on_exit:
            self.close()

    def connect(self):
        """Authenticate to WOS and set the SID cookie."""
        if not self._SID:
            self._SID = self._auth.service.authenticate()

        print 'Authenticated using SID:', self._SID
        self._search.set_options(headers={'Cookie': 'SID="%s"' % self._SID})
        self._auth.options.headers.update({'Cookie': 'SID="%s"' % self._SID})

    def close(self):
        """Close the session."""
        if self._SID:
            self._auth.service.closeSession()
            self._SID = None

    def search(self, query, count=5):
        """Perform a query. Check the WOS documentation for v3 syntax."""
        if not self._SID:
            raise RuntimeError('Session not open. Invoke .connect() before.')

        qparams = {'databaseId': 'WOS',
                   'userQuery': query,
                   'queryLanguage': 'en'}

        rparams = {'firstRecord': 1,
                   'count': count,
                   'sortField': {'name': 'RS', 'sort': 'D'}}

        return self._search.service.search(qparams, rparams)