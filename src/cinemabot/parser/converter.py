from pickle import load
from cinemaBot.src.cinemabot.parser.parser import ShowInfo, Movie


def flatten_list(l: list) -> list:
    """

    :param l:
    :return:
    """
    flat_list = []
    for l2 in l:
        for el in l2:
            flat_list.append(el)
    return flat_list


def main(data) -> dict:
    """

    :param data:
    :return:
    """
    res = {}
    for movie in flatten_list(data):
        show_info: Movie = movie[0]
        show_info.show_time = movie[1]

        hash = show_info.hash

        if hash not in res.keys():
            res.update({hash: show_info})
        else:
            t = res[hash]
            new = t + show_info
            res[hash] = new
    return [v.to_dict(return_lists=False) for _, v in res.items()]


if __name__ == '__main__':
    inp_file = 'info.pkl'
    out_file = 'info.json'

    with open(inp_file, 'rb') as fid:
        data = load(fid)

    res = main(data)
    for el in res:
        print(el)