from setuptools import setup

setup(
    name='xnat2jupyterhub',
    version='1.0.0-beta1',
    url='https://bitbucket.org/xnat-containers/xnat-jupyterhub',
    author='Andrew Lassiter',
    author_email='andrewl@wustl.edu',
    packages=['xnat2jupyterhub', 'xnat2jupyterhub.hooks'],
    license='Simplified BSD',
    description='XNAT extensions for JupyterHub',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown'
)
