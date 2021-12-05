class Error(Exception):
    """Base class for exceptions in this module."""
    pass


class InputError(Error):
    """Exception raised for errors in the input.

    Attributes:
        expression -- input expression in which the error occurred
        message -- explanation of the error
    """

    def __init__(self, expression, message):
        self.expression = expression
        self.message = message


class URDFerror(Error):
    """Raised when the robot's body in urdf is not defined as box"""

    def __init__(self, message="Body can only be a box"):
        self.message = message
        super().__init__(self.message)


class Wheelerror(Error):
    """Raised when the robot has more than two wheels"""

    def __init__(self, message="Only allows 2 wheels for now"):
        self.message = message
        super().__init__(self.message)
