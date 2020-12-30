import os
import yaml

def get_api():
    file_config = read_yml('config.yml')
    if (file_config is not None) and (file_config.get('API_KEY') is not None):
        return file_config.get('API_KEY')
    else:
        raise ValueError('No API ley')


def read_yml(pth: str='./data/schedule.yml') -> dict:
    """

    :param pth:
    :return:
    """
    abs_pth = os.path.realpath(os.path.join(os.path.dirname(__file__), pth))

    res = {}
    with open(abs_pth, encoding='utf8') as fid:
        try:
            res = yaml.load(fid, Loader=yaml.SafeLoader)
        except Exception as err:
            print(err)
    return res
