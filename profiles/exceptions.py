from rest_framework.exceptions import APIException

class UnauthorizedExcp(APIException):
    status_code = 401
    default_detail = 'Unauthorized'
    default_code = 'Unauthorized'

# used in accounts.views
class NoProfileFound(APIException):
    status_code = 404
    ''' do not change these value bcz word 'No_Profile_Found' used for the  of purpose of opening 404 page in frontend if profile not found.  '''
    default_detail = 'No_Profile_Found'
    default_code = 'No_Profile_Found'