def main():
    my_dict = {'a': 4, 'b': ('значение', 4)}
    reversed_dict = dict((v, k) for k, v in my_dict.items())
    return {
        "список": [1, 2, 3],
        "словарь": reversed_dict,
        "кортеж": ('5', 6, 7),
        "множество": {8, (9, 10), '11'}
    }

