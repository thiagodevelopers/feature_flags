from abc import ABC
from abc import abstractmethod
from enum import Enum
import json

import flask


class FeatureFlagConfig(ABC):
    FLAG_NAME: str
    VARIANTS_ENUM_STR: str

    def __init__(self, overrides=None):
        self.variants_enum = Enum(
            f'{self.__class__.__name__}Variants', self.VARIANTS_ENUM_STR)
        self.overrides = overrides

    def get_variants(self):
        return list(self.variants_enum.__members__.keys())

    @abstractmethod
    def _get_variant(
            self,
            user_id: Optional[int] = None,
            app: Optional[Flask] = None,
            request: Optional[Request] = None,
            session: Optional[Any] = None):
        pass

    def get_variant(self, user_id: Optional[int] = None, app: Optional[Flask] = None,
                    request: Optional[Request] = None, session: Optional[Any] = None):
        override_variant = self.get_override_variant(
            user_id=user_id, app=app, request=request, session=session)
        if override_variant:
            return override_variant
        else:
            return self._get_variant(
                user_id=user_id, app=app, request=request, session=session)

    def get_override_variant(
            self, user_id=None, app=None, request=None, session=None):
        if request:
            browser_override_variant = self.get_browser_override_variant(request)
            if browser_override_variant:
                return browser_override_variant
        if self.overrides:
            for variant, user_ids in self.overrides.items():
                if user_id in user_ids:
                    return self.variants_enum[variant]
        return None

    def set_browser_override_variant(self, request, variant):
        browser_override_variants = self.get_browser_override_variants(request)
        if variant == '':
            browser_override_variants.pop(self.FLAG_NAME, None)
        else:
            browser_override_variants[self.FLAG_NAME] = variant

        response = flask.make_response()
        response.set_cookie(
            'gatekeeper',
            json.dumps(browser_override_variants))
        return response

    def get_browser_override_variants(self, request):
        return json.loads(request.cookies.get('gatekeeper', '{}'))

    def get_browser_override_variant(self, request):
        browser_override_variants = self.get_browser_override_variants(request)
        browser_override_variant = browser_override_variants.get(self.FLAG_NAME)
        if browser_override_variant:
            return self.variants_enum[browser_override_variant]
        else:
            return None