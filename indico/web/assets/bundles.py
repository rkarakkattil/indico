# This file is part of Indico.
# Copyright (C) 2002 - 2018 European Organization for Nuclear Research (CERN).
#
# Indico is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 3 of the
# License, or (at your option) any later version.
#
# Indico is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Indico; if not, see <http://www.gnu.org/licenses/>.

from __future__ import unicode_literals

import errno
import os
from glob import glob
from urlparse import urlparse

import csscompressor
from flask.helpers import get_root_path
from markupsafe import Markup
from webassets import Bundle, Environment
from webassets.filter import Filter, register_filter
from webassets.filter.cssrewrite import CSSRewrite

from indico.core.config import config


SASS_BASE_MODULES = ["sass/*.scss", "sass/base/*.scss", "sass/custom/*.scss", "sass/partials/*.scss",
                     "sass/modules/*.scss", "sass/modules/*/*.scss"]


class CSSCompressor(Filter):
    name = 'csscompressor'

    def output(self, _in, out, **kw):
        out.write(csscompressor.compress(_in.read(), max_linelen=500))


class IndicoCSSRewrite(CSSRewrite):
    name = 'indico_cssrewrite'

    def __init__(self):
        super(IndicoCSSRewrite, self).__init__()
        self.base_url_path = urlparse(config.BASE_URL.rstrip('/')).path

    def replace_url(self, url):
        parsed = urlparse(url)
        if parsed.scheme or parsed.netloc:
            return url
        elif parsed.path.startswith('/'):
            # Prefix absolute urls with the base path. Like this we avoid
            # the mess that comes with relative URLs in CSS while still
            # supporting Indico running in a subdirectory (e.g. /indico)
            return self.base_url_path + url
        else:
            return super(IndicoCSSRewrite, self).replace_url(url)


# XXX: DO NOT move this to decorators. this function returns None,
# so super() calls using the decorated class name fail...
register_filter(CSSCompressor)
register_filter(IndicoCSSRewrite)


def _get_client_path():
    return os.path.join(get_root_path('indico'), 'web', 'client')


def configure_pyscss(environment):
    base_url_path = urlparse(config.BASE_URL).path
    environment.config['PYSCSS_STYLE'] = 'compact'
    environment.config['PYSCSS_DEBUG_INFO'] = False
    environment.config['PYSCSS_STATIC_URL'] = '{0}/static/'.format(base_url_path)
    environment.config['PYSCSS_LOAD_PATHS'] = [
        os.path.join(_get_client_path(), 'sass')
    ]


def get_webassets_cache_dir():
    return os.path.join(config.CACHE_DIR, 'webassets-{}-core'.format(config.WORKER_NAME))


class LazyCacheEnvironment(Environment):
    def _get_cache(self):
        # Create the cache dir if it doesn't exist. Like this we wait until
        # it is actually accessed instead of doing it at import time.
        # Not sure why webassets only lazily creates the cache dir when using
        # the default path but not when using a custom one...
        if isinstance(self._storage['cache'], basestring):
            try:
                os.mkdir(self._storage['cache'])
            except OSError as exc:
                if exc.errno != errno.EEXIST:
                    raise
        return Environment.cache.fget(self)
    cache = property(_get_cache, Environment.cache.fset)
    del _get_cache


class IndicoEnvironment(LazyCacheEnvironment):
    def init_app(self, app):
        self.config.update({'cache': get_webassets_cache_dir()})
        url_path = urlparse(config.BASE_URL).path
        self.directory = os.path.join(config.ASSETS_DIR, 'core')
        self.url = '{0}/static/assets/core/'.format(url_path)
        self.debug = app.debug
        configure_pyscss(self)
        self.append_path(_get_client_path(), '/')
        self.append_path(os.path.join(_get_client_path(), 'css'), '{0}/css'.format(url_path))
        self.append_path(os.path.join(_get_client_path(), 'js'), '{0}/js'.format(url_path))


def include_js_assets(bundle_name):
    """Jinja template function to generate HTML tags for a JS asset bundle."""
    return Markup('\n'.join('<script src="{}"></script>'.format(url) for url in core_env[bundle_name].urls()))


def include_css_assets(bundle_name):
    """Jinja template function to generate HTML tags for a CSS asset bundle."""
    return Markup('\n'.join('<link rel="stylesheet" type="text/css" href="{}">'.format(url)
                            for url in core_env[bundle_name].urls()))


def _get_custom_files(subdir, pattern):
    customization_dir = config.CUSTOMIZATION_DIR
    if not customization_dir:
        return []
    customization_dir = os.path.join(customization_dir, subdir)
    if not os.path.exists(customization_dir):
        return []
    return sorted(glob(os.path.join(customization_dir, pattern)))


def register_all_js(env):
    # Build a bundle with customization JS if enabled
    custom_js_files = _get_custom_files('js', '*.js')
    if custom_js_files:
        bundle = Bundle(*custom_js_files, filters='rjsmin', output='js/custom_%(version)s.min.js')
        env.register('custom_js', bundle)


def register_all_css(env):
    # Build a bundle with customization CSS if enabled
    custom_css_files = _get_custom_files('scss', '*.scss')
    if custom_css_files:
        env.register('custom_sass', Bundle(*custom_css_files, filters=('pyscss', 'csscompressor'),
                                           output='sass/custom_sass_%(version)s.css'))


core_env = IndicoEnvironment()
