import redis
from twisted.internet.defer import inlineCallbacks
from vumi.application import ApplicationWorker, SessionManager
from vumi.utils import load_class_by_string


class MenuApplicationWorker(ApplicationWorker):
    flush_sessions = False

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
        if self.flush_sessions:
            self.redis_server.flushdb()
        yield super(MenuApplicationWorker, self).startWorker()

    @inlineCallbacks
    def stopWorker(self):
        """
        Stop session manager.
        """
        yield self.session_manager.stop()
        yield super(MenuApplicationWorker, self).stopWorker()

    def consume_user_message(self, message):
        """
        Dynamically contruct menu based on user input.
        If no session is found self.initial_menu is constructed.
        """
        user_id = message.user()
        session = self.session_manager.load_session(user_id)
        try:
            if not session:
                session = self.session_manager.create_session(user_id)
                menu_class = self.initial_menu
            else:
                if 'class' in session:
                    menu_class = load_class_by_string(session['class'])
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
