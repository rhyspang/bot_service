# -*- coding: utf-8 -*-

from rest_framework.response import Response
from rest_framework.serializers import Serializer

from response import standard_errors


class ServiceResponse(Response):

    def __init__(self, data=None, error='', status=None, template_name=None,
                 message=standard_errors.MRDP_OK.message,
                 code=standard_errors.MRDP_OK.code, headers=None,
                 exception=False, content_type=None):
        """
        Alters the init arguments slightly.
        For example, drop 'template_name', and instead use 'data'.
        Setting 'renderer' and 'media_type' will typically be deferred,
        For example being set automatically by the `APIView`.
        """
        super(ServiceResponse, self).__init__(None, status=status)

        if isinstance(data, Serializer):
            msg = (
                'You passed a Serializer instance as data, but '
                'probably meant to pass serialized `.data` or '
                '`.error`. representation.'
            )
            raise AssertionError(msg)

        self.data = {"status": code, "error": message, "value": data}
        self.template_name = template_name
        self.exception = exception
        self.content_type = content_type

        if headers:
            for name, value in headers.items():
                self[name] = value
