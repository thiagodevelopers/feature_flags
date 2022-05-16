from gatekeeper_config import FF_CONFIG_MAP


class Gatekeeper(object):
    def __init__(self, user_id=None,
                 app=None,
                 request=None,
                 session=None,
                 config_map=None):

        self.user_id = user_id
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

    def get_feature_flag_variant(self, flag, user_id_override):
        config = self.config_map.get(flag)
        if not config:
            return None

        variant = config.get_variant(
            user_id=user_id_override or self.user_id,
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

def initialize_gatekeeper(user_id=None, app=None, config_map=None):
    from flask import current_app
    from flask import request
    from flask import session
    from flask_login import current_user

    if not app:
        app = current_app

    if user_id is None and current_user and not current_user.is_anonymous:
        user_id = current_user.id

    gk = Gatekeeper(
        user_id=user_id,
        app=app,
        request=request,
        session=session,
        config_map=config_map)
    return gk