# -*- coding: utf-8 -*-
"""
Descriptive task init status codes, for code readability
"""
from collections import namedtuple


HttpStatus = namedtuple('HttpStatus', ('code', 'message'))


OK = HttpStatus(10000, 'ok')

# user
INVALID_TICKET = HttpStatus(12001, u'参数错误')
# SELECTED_NO_GROUP = HttpStatus(12002, u'no selected group')
# GROUP_NO_AUTH = HttpStatus(12003, 'no group permission')
# URL_NO_AUTH = HttpStatus(12004, 'tab no permission')
# PARAM_ERROR = HttpStatus(12005, 'request parameter is invalid')
INVALID_PARAM = HttpStatus(12006, u'参数错误')


def main():
    print(OK._asdict())


if __name__ == '__main__':
    main()
