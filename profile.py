"""
PROFILE CLASS
"""


class Profile:
    def __init__(self, name, version):
#Initialize a profile with default launch settings
        self.name = name
        self.version = version
        self.options = None
        self.profile_directory = "instances/" + self.name

    def set_options(self, options):
#Update launch options for the profile
        self.options = options
