import importlib

from pkg_resources import iter_entry_points


def available_authentication_types():
    auth_types = [getattr(importlib.import_module(x[0], package=__name__), x[1])() for x in [
        ('.aws', 'AWSAuthentication'),
    ]]

    ret = {auth_type.name(): auth_type for auth_type in auth_types}
    for entry_point in iter_entry_points(group='mfado.auth_types'):
        for auth_type in entry_point.load()():
            ret[auth_type.name()] = auth_type
    return ret
