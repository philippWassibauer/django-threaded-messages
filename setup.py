from distutils.core import setup

setup(
    name='django-threaded-messages',
    version=__import__('threaded_messages').__version__,
    description='User-to-user threaded messaging system (similar to facebook) for Django',
    author='John Debs, Philipp Wassibauer',
    author_email='johnthedebs@gmail.com',
    url='http://github.com/johnthedebs',
    download_url='http://github.com/johnthedebs',
    packages=(
        'threaded_messages',
        'threaded_messages.templatetags',
    ),
    package_data={
        'threaded_messages': [
            'templates/django_messages/*',
            'templates/notification/*/*',
            'locale/*/LC_MESSAGES/*',
        ]
    },
    classifiers=(
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Utilities',
        'Framework :: Django',
    ),
)