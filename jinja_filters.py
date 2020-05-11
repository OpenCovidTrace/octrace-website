from flask_babel import lazy_gettext
_lt = lazy_gettext


def hour_text(val):
    if val < 1:
        return _lt('%(minute)s minutes', minute=int(val*60))
    elif val == 1:
        return _lt('1 hour')
    else:
        return _lt('%(hour)s hours', hour=int(val))
