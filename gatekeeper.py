from gatekeeper_config import FF_CONFIG_MAP


class Gatekeeper(object):
    def __init__(self, 
                 app=None,
                 request=None,
                 session=None,
                 config_map=None):

        self.app = app
        self.request = request
        self.session = session

        self.config_map = config_map if config_map else FF_CONFIG_MAP

    def ff(self, *args, **kwargs):
        '''Shorthand wrapper for `feature_flag`.'''
        return self.feature_flag(*args, **kwargs)

    def feature_flag(self, flag, variant):
        return self.get_feature_flag_variant(flag) == variant

    def ff_variant(self, *args, **kwargs):
        '''Shorthand wrapper for `get_feature_flag_variant`.'''
        return self.get_feature_flag_variant(*args, **kwargs)

    def get_feature_flag_variant(self, flag):
        config = self.config_map.get(flag)
        if not config:
            return None

        variant = config.get_variant(
            app=self.app,
            request=self.request,
            session=self.session)
        return variant.name

    def get_config_map(self):
        return self.config_map

    def get_browser_override_variants(self, request):
        return json.loads(request.cookies.get('gatekeeper', '{}'))

    def set_browser_override_variant(self, request, flag, variant):
        config = self.config_map.get(flag)
        if not config:
            return None

        return config.set_browser_override_variant(request, variant)

def initialize_gatekeeper(app=None, config_map=None):
    from flask import current_app
    from flask import request
    from flask import session

    if not app:
        app = current_app

    gk = Gatekeeper(
        app=app,
        request=request,
        session=session,
        config_map=config_map)
    return gk