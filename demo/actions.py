from fife_rpg.actions.base import Base

class PrintAction(Base):

    def __init__(self, application, text, commands = None):
        Base.__init__(self, application, None, None, commands)
        self.text = text

    def execute(self):
        Base.execute(self)
        print self.text

    @classmethod
    def register(cls, name="Print"):
        """Registers the class as an action

        Args:
            name: The name under which the class should be registered
            *args: Additional arguments to pass to the class constructor
            **kwargs: Additional keyword arguments to pass to the class 
            constructor

        Returns:
            True if the action was registered, False if not.
        """
        return (super(PrintAction, cls).register(name))