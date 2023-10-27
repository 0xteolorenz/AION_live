#####################################################################################################
#            This module contains a collections of custom errors                                    #
#####################################################################################################

#####################################################################################################
#            Import section                                                                         #
#####################################################################################################


class ConfigurationNotValid(Exception):
    '''
    Exception raised for errors in the configuration of the program.
    '''
    def __init__(self):
        self.message = 'Change settings'
        super().__init__(self.message)

