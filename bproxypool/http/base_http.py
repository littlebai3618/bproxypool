class BaseHttp(object):

    def _set_url(self, url):
        if isinstance(url, str):
            return url
        else:
            raise TypeError('{} url must be str, got: {}'.format(type(self).__name__, type(url).__name__))

    def _set_headers(self, headers):
        if headers is None:
            return {}
        elif not isinstance(headers, dict):
            raise TypeError("{} headers must be dict. ".format(type(self).__name__))
        else:
            return headers

    def _set_cookies(self, cookies):
        if cookies is None:
            return
        elif not isinstance(cookies, dict):
            raise TypeError("{} cookies must be dict or None. ".format(type(self).__name__))
        else:
            return cookies

    def _set_method(self, method):
        if method is None:
            return 'GET'
        if isinstance(method, str):
            method = method.upper()
            if method in 'GET, POST, PUT ,PATCH, OPTIONS, HEAD, DELETE':
                return method
            else:
                raise TypeError("{} method: {} is not support. ".format(type(self).__name__, method))

        raise TypeError("{} method must be str. ".format(type(self).__name__))

    def _set_meta(self, meta):
        if meta is None:
            return {}
        elif not isinstance(meta, dict):
            raise TypeError("{} meta must be dict or None. ".format(type(self).__name__))
        else:
            return meta

    def _set_data(self, data):
        if data is None:
            return
        elif not isinstance(data, dict):
            raise TypeError("{} data must be dict or None. ".format(type(self).__name__))
        else:
            return data

    # Response API
    def _set_text(self, text):
        if text is None:
            return ''
        elif not isinstance(text, str):
            raise TypeError("{} text must be str. ".format(type(self).__name__))
        else:
            return text

    def _set_callback(self, callback):
        if callable(callback):
            return callback.__name__
        elif isinstance(callback, str):
            return callback
        else:
            raise TypeError('callback must be callable or str')

    def _set_errback(self, errback):
        if callable(errback):
            return errback.__name__
        elif isinstance(errback, str) or errback is None:
            return errback
        else:
            raise TypeError('error callback must be callable or str')
