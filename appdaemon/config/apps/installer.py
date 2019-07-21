import appdaemon.appapi as appapi
import subprocess


PACKAGES = ['python-dateutil',
            'pytz', 'requests','opencv-python-headless']


class DepeInstaller(appapi.AppDaemon): 
    def initialize(self):
        self.log("Installing packages")
        
        for package in PACKAGES:
            self.log("Installing {}".format(package))
            self.install(package)

    def install(self, package):
        # https://github.com/pypa/pip/issues/2553
        subprocess.call(['pip3', 'install', package])