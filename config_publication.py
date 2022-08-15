import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard to guess string'
    SSL_REDIRECT = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_RECORD_QUERIES = True
    MAIL_SERVER = 'smtp.qq.com'
    MAIL_PORT = 465
    MAIL_USE_SSL = True
    MAIL_USE_TLS = False
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME') or "yourqq@qq.com"   # 修改成个人qq邮箱
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD') or "password"  # qq邮箱的设置中生成授权码
    AUTOLITER_MAIL_SUBJECT_PREFIX = "autoLiter"
    AUTOLITER_MAIL_SENDER = os.environ.get('AUTOLITER_MAIL_SENDER') or "autoLiter <yourqq@qq.com>" # 修改
    AUTOLITER_ADMIN = os.environ.get('AUTOLITER_ADMIN') or "yourqq@qq.com" # 修改
    AUTOLITER_NOTES_PER_PAGE = 20  # 每页多少条目，默认20

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'data-dev.sqlite')    
        

class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'data-autoLiter.sqlite')

    @classmethod
    def init_app(cls, app):
        Config.init_app(app)

        # email errors to the administrators
        import logging
        from logging.handlers import SMTPHandler
        credentials = None
        secure = None
        if getattr(cls, 'MAIL_USERNAME', None) is not None:
            credentials = (cls.MAIL_USERNAME, cls.MAIL_PASSWORD)
            if getattr(cls, 'MAIL_USE_TLS', None):
                secure = ()
        mail_handler = SMTPHandler(
            mailhost=(cls.MAIL_SERVER, cls.MAIL_PORT),
            fromaddr=cls.AUTOLITER_MAIL_SENDER,
            toaddrs=[cls.AUTOLITER_ADMIN],
            subject=cls.AUTOLITER_MAIL_SUBJECT_PREFIX + ' Application Error',
            credentials=credentials,
            secure=secure)
        mail_handler.setLevel(logging.ERROR)
        app.logger.addHandler(mail_handler)



config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}

# proxy when download pdf format file
PROXY = "127.0.0.1:7890"