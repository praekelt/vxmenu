import redis
import sys

from twisted.internet.defer import inlineCallbacks
from vumi.application import ApplicationWorker, SessionManager


def class_from_str(str):
    """
    Returns a class for given string.
    """
    module = '.'.join(str.split('.')[:-1])
    cls = str.split('.')[-1]
    return getattr(sys.modules[module], cls)


class DynamicMenu(object):
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
            self.response_menu = class_from_str(resolved_choice[2])(message, session)
        else:
            self.response_menu = self


class DynamicMenuApplicationWorker(ApplicationWorker):
    @inlineCallbacks
    def startWorker(self):
        """
        Setup session manager.
        """
        self.redis_config = self.config.get('redis_config', {})
        self.redis_server = redis.Redis(**self.redis_config)
        self.session_manager = SessionManager(
            r_server=self.redis_server,
            prefix="%(worker_name)s:%(transport_name)s" % self.config,
            max_session_length=getattr(self, 'MAX_SESSION_LENGTH', None)
        )
        self.redis_server.flushdb()
        yield super(DynamicMenuApplicationWorker, self).startWorker()

    @inlineCallbacks
    def stopWorker(self):
        """
        Stop session manager.
        """
        yield self.session_manager.stop()
        yield super(DynamicMenuApplicationWorker, self).stopWorker()

    def consume_user_message(self, message):
        """
        Dynamically contruct menu based on user input.
        If no session is found self.initial_menu is used as frist menu.
        """
        user_id = message.user()
        session = self.session_manager.load_session(user_id)
        try:
            if not session:
                session = self.session_manager.create_session(user_id)
                menu_class = self.initial_menu
            else:
                if 'class' in session:
                    menu_class = class_from_str(session['class'])
                else:
                    menu_class = self.initial_menu

            try:
                menu = menu_class(message, session, int(message['content']))
            except ValueError:
                menu = menu_class(message, session, '')

            self.session_manager.save_session(user_id, session)
            self.reply_to(message, menu.generate_menu(message['content']))

        except Exception, e:
            self.reply_to(message, str(e))
