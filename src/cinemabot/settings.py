import os
import logging
import yaml

_logger = logging.getLogger(__name__)


def read_config():
    """
    Reads and returns content of config file

    :return:
    """
    settings = {}
    pth = os.path.join(os.path.dirname(__file__), 'configs', 'config.yml')
    print(pth)
    if not os.path.exists(pth):
        return settings
    with open(pth) as fid:
        try:
            settings = yaml.load(fid, Loader=yaml.SafeLoader)
        except Exception as err:
            _logger.debug(repr(err))
    return settings


def get_param(settings, config_name, env_name, cast_type=None):
    """
    Return value of the given parameter from environment variables or config file

    :param settings: dictionary of settings
    :param config_name: name of the variable in the settings' dictionary
    :param env_name: name of corresponding environment variable
    :param cast_type: Python type to cast the value
    :return:
    """
    token = os.getenv(env_name)
    if token is None:
        token = settings.get(config_name)

    if token is None:
        return None

    if (cast_type is not None) and (token is not None):
        token = cast_type(token)
    _logger.debug('Variable %s, value %s', config_name, str(token))
    return token


settings = read_config()

BOT_TOKEN = get_param(settings, 'bot_token', 'BOT_TOKEN')
HEROKU_APP_NAME = os.getenv('HEROKU_APP_NAME')


# webhook settings
WEBHOOK_HOST = f'https://{HEROKU_APP_NAME}.herokuapp.com'
WEBHOOK_PATH = f'/webhook/{BOT_TOKEN}'
WEBHOOK_URL = f'{WEBHOOK_HOST}{WEBHOOK_PATH}'

# webserver settings
WEBAPP_HOST = '0.0.0.0'
WEBAPP_PORT = get_param(settings, 'port', 'PORT')

# is local development?
LOCAL_DEV = get_param({}, 'local_dev', 'LOCAL_DEVELOPMENT')





