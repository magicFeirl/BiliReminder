import os
import json

rootpath = os.path.abspath(os.path.join(__file__, '../../..', 'db.json'))


class ReactiveDict(dict):
    def __getitem__(self, __key: any) -> any:
        if __key not in self:
            self[__key] = ReactiveDict()
            return self[__key]

        return super().__getitem__(__key)

    def __setitem__(self, __key: any, __value: any) -> None:
        data = super().__setitem__(__key, __value)

        with open(rootpath, 'w', encoding='utf-8') as f:
            json.dump(reactive_dict, f)

        return data


reactive_dict = None


def init_db(overwrite: bool = False):
    if overwrite or not os.path.isfile(rootpath):
        with open(rootpath, 'w', encoding="utf-8") as f:
            f.write("{}")


def load_db():
    global reactive_dict

    try:
        with open(rootpath, 'r', encoding="utf-8") as f:
            reactive_dict = ReactiveDict(json.load(f))
    except FileNotFoundError:
        init_db(True)
        reactive_dict = ReactiveDict({})

    return reactive_dict


