from setuptools import find_packages, setup
import os.path
from glob import glob

package_name = 'ros_piper'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name + '/launch', glob('launch/*.launch.xml')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Robotnik Automation',
    maintainer_email='support@robotnik.es',
    description='ROS wrapper for the text2speech library piper',
    license='Apache-2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'piper = ros_piper.piper:main',
        ],
    },
)
