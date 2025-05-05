from sqlalchemy import Enum


# USER_STATUS contains all of the general statuses of a user
# - Active: User account has been logged in to and using the application
# - Inactive: User account is verified but not in use
# - Terminated: User account has been closed indefinitely
# - Unverified: User has created an account but is yet to be verified
# - Locked: User account is temporarily unavailable
# - Closed: User has deleted their account with all of their information
USER_STATUS_ENUM = Enum('Active', 'Inactive', 'Terminated', 'Unverified', 'Locked', 'Closed', name='user_status_enum')

# GENDER_ENUM contains all of the genders a user can have
# - All statuses are self explanatory
GENDER_ENUM = Enum('Male', 'Female', 'Other', 'Prefer Not To Say', name='gender_enum')
