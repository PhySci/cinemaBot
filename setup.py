from setuptools import setup, find_packages
import os

setup_dir = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(setup_dir, 'requirements.txt'), 'r') as req_file:
    requirements = [line.strip() for line in req_file if line.strip()]

setup(name='cinemabot',
      version='0.2.0',
      description='Telegram bot for the cinema',
      author='Fedor Mushenok',
      author_email='mushenokf@gmail.com',
      include_package_data=True,
      packages=find_packages(exclude=['test']),
      install_requires=requirements
      )
