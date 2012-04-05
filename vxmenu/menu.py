from vumi.utils import load_class_by_string


class Menu(object):
    """
    Base class from which all dynamic menus should inherit.
    Provides logic for constructing menus and proceeding to subsequent menus.
    """
    text = None
    options = []

    def get_text(self):
        """
        By default menu text (header) is defined in self.text.
        This allows for dynamic text creation through method overriding.
        """
        return self.text

    def get_options(self):
        """
        By default menu options is defined in self.options.
        This allows for dynamic option creation through method overriding.
        """
        return self.options

    def process_response(self, choice):
        """
        Override to perform any additional menu specific processing.
        """
        pass

    def generate_menu(self, choice):
        """
        Generates menu based on determined text and options.
        """
        options = self.response_menu.get_options()
        return self.response_menu.get_text() + '\n' + '\n'.join(
            ['%s. %s' % (idx, opt[0]) for idx, opt in enumerate(options, 1)])

    def __init__(self, message, session, choice=None):
        """
        Initiate menu based on incomming choice from previous menu.
        Options specific session data for given choice is
        added to session data.
        """
        self.message = message
        self.session = session
        if choice:
            options = self.get_options()
            resolved_choice = options[int(choice) - 1]
            session.update(resolved_choice[1])
            session['class'] = resolved_choice[2]
            self.process_response(choice)
            self.response_menu = \
                    load_class_by_string(resolved_choice[2])(message, session)
        else:
            self.response_menu = self
