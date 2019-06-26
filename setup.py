from distutils.core import setup

setup(
    name='dbmclient',
    version='0.1.0',
    author='Emmanuel Job',
    author_email='emmanuel.job@accuenmedia.com',
    packages=['dbmclient'],
    scripts=[],
    url='http://www.accuenmedia.com',
    license='LICENSE.txt',
    description='A simple client for the TTD console.',
    long_description=open('README.txt').read(),
    install_requires=[
        "requests",
        "google-api-python-client>=1.5.1",
        "httplib2",
        "oauth2client>=2.1.0",
        "pyOpenSSL",
        "cryptography",
    ],
)
