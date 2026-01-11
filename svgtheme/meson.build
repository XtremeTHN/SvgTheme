pkgdatadir = get_option('prefix') / get_option('datadir')
moduledir = pkgdatadir / meson.project_name()

python = import('python')
python_i = python.find_installation('python3')

conf = configuration_data()
conf.set('pkgdatadir', pkgdatadir)

configure_file(
    input: 'svgtheme.in',
    output: 'svgtheme',
    configuration: conf,
    install: true,
    install_dir: get_option('bindir'),
    install_mode: 'r-xr-xr-x'
)

svgtheme_sources = [
    '__init__.py',
    'main.py',
    'svg.py'
]

install_data(svgtheme_sources, install_dir: moduledir)