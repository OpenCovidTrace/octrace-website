# -*- coding: utf-8 -*-
"""
Asset management plugin for Pelican
===================================

This plugin allows you to use the `webassets`_ module to manage assets such as
CSS and JS files.

The ASSET_URL is set to a relative url to honor Pelican's RELATIVE_URLS
setting. This requires the use of SITEURL in the templates::

    <link rel="stylesheet" href="{{ SITEURL }}/{{ ASSET_URL }}">

.. _webassets: https://webassets.readthedocs.org/

"""
from __future__ import unicode_literals

import os
import logging

from pelican import signals
logger = logging.getLogger(__name__)

try:
    import webassets
    from webassets import Environment
    from webassets.filter import uglifyjs, register_filter, FilterError
    from webassets.ext.jinja2 import AssetsExtension
except ImportError:
    webassets = None
    raise


class UglifyJSSourceMap(uglifyjs.UglifyJS):
    name = 'uglifyjs_sm'
    options = {
        'binary': 'CUSTOM_UGLIFYJS_BIN',
        'extra_args': 'CUSTOM_UGLIFYJS_EXTRA_ARGS',
        'outdir': 'CUSTOM_UGLIFYJS_OUTDIR'
    }

    def output(self, _in, out, **kw):
        # UglifyJS 2 doesn't properly read data from stdin (#212).
        args = [self.binary or 'uglifyjs', '{input}', '--output', '{output}']
        if self.extra_args:
            args.extend(self.extra_args)
        self.subprocess(args, out, data=_in, outdir=self.outdir)

    @classmethod
    def subprocess(cls, argv, out, data=None, cwd=None, outdir=None):
        """Execute the commandline given by the list in ``argv``.
        If a byestring is given via ``data``, it is piped into data.
        If ``cwd`` is not None, the process will be executed in that directory.
        ``argv`` may contain two placeholders:
        ``{input}``
            If given, ``data`` will be written to a temporary file instead
            of data. The placeholder is then replaced with that file.
        ``{output}``
            Will be replaced by a temporary filename. The return value then
            will be the content of this file, rather than stdout.
        """
        import os
        import shutil
        import subprocess
        import tempfile

        class tempfile_on_demand(object):
            def __init__(self, directory=None):
                self.filename = None
                self.dir = directory

            def __repr__(self):
                if self.filename is None:
                    fd, self.filename = tempfile.mkstemp(dir=self.dir)
                    os.close(fd)
                return self.filename

            @property
            def created(self):
                return self.filename is not None

        # Replace input and output placeholders
        tmpdir = tempfile.mkdtemp()
        input_file = tempfile_on_demand(tmpdir)
        output_file = tempfile_on_demand(tmpdir)
        argv = list(map(
            lambda item: item.format(input=input_file, output=output_file),
            argv
        ))

        try:
            data = (data.read() if hasattr(data, 'read') else data)
            if data is not None:
                data = data.encode('utf-8')

            if input_file.created:
                if data is None:
                    raise ValueError(
                        '{input} placeholder given, but no data passed')
                with open(input_file.filename, 'wb') as f:
                    f.write(data)
                    # No longer pass to stdin
                    data = None
            try:
                proc = subprocess.Popen(
                    argv,
                    # we cannot use the in/out streams directly,
                    # as they might be StringIO objects
                    # which are not supported by subprocess
                    stdout=subprocess.PIPE,
                    stdin=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    cwd=cwd,
                    shell=os.name == 'nt')
            except OSError:
                raise FilterError('Program file not found: %s.' % argv[0])
            stdout, stderr = proc.communicate(data)
            if proc.returncode:
                raise FilterError(
                    '%s: subprocess returned a non-success result code: '
                    '%s, stdout=%s, stderr=%s' % (
                        cls.name or cls.__name__,
                        proc.returncode, stdout, stderr))
            else:
                if output_file.created:
                    fpath = output_file.filename
                    with open(fpath, 'rb') as f:
                        out.write(f.read().decode('utf-8'))
                    _, fname = os.path.split(fpath)
                    for tmp_file in os.listdir(tmpdir):
                        if (
                            tmp_file.startswith(fname) and
                            tmp_file.endswith('map')
                        ):
                            rest_path = os.path.join(
                                outdir, 'packed.js.map')
                            tmp_path = os.path.join(
                                tmpdir, tmp_file)
                            with open(rest_path, 'wb') as out_fp, open(tmp_path, 'rb') as tmp_fp:
                                out_fp.write(tmp_fp.read())

                else:
                    out.write(stdout.decode('utf-8'))
        finally:
            if output_file.created:
                os.unlink(output_file.filename)
            if input_file.created:
                os.unlink(input_file.filename)
            try:
                shutil.rmtree(tmpdir)
            except OSError:
                pass


register_filter(UglifyJSSourceMap)


def add_jinja2_ext(pelican):
    """Add Webassets to Jinja2 extensions in Pelican settings."""

    if 'JINJA_ENVIRONMENT' in pelican.settings:  # pelican 3.7+
        pelican.settings['JINJA_ENVIRONMENT']['extensions'].append(
            AssetsExtension)
    else:
        pelican.settings['JINJA_EXTENSIONS'].append(AssetsExtension)


def create_assets_env(generator):
    """Define the assets environment and pass it to the generator."""

    theme_static_dir = generator.settings['THEME_STATIC_DIR']
    assets_destination = os.path.join(generator.output_path, theme_static_dir)
    generator.env.assets_environment = Environment(
        assets_destination, theme_static_dir)

    if 'ASSET_CONFIG' in generator.settings:
        for item in generator.settings['ASSET_CONFIG']:
            generator.env.assets_environment.config[item[0]] = item[1]

    if 'ASSET_BUNDLES' in generator.settings:
        for name, args, kwargs in generator.settings['ASSET_BUNDLES']:
            generator.env.assets_environment.register(name, *args, **kwargs)

    if 'ASSET_DEBUG' in generator.settings:
        generator.env.assets_environment.debug = (
            generator.settings['ASSET_DEBUG']
        )
    elif logging.getLevelName(logger.getEffectiveLevel()) == "DEBUG":
        generator.env.assets_environment.debug = True

    for path in (generator.settings['THEME_STATIC_PATHS'] +
                 generator.settings.get('ASSET_SOURCE_PATHS', [])):
        full_path = os.path.join(generator.theme, path)
        generator.env.assets_environment.append_path(full_path)


def register():
    """Plugin registration."""
    if webassets:
        signals.initialized.connect(add_jinja2_ext)
        signals.generator_init.connect(create_assets_env)
    else:
        logger.warning('`assets` failed to load dependency `webassets`.'
                       '`assets` plugin not loaded.')
