import os
from setuptools import find_packages, setup, Command


class CleanCommand(Command):
    """Custom clean command to tidy up the project root."""
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        os.system("rm -vrf ./build ./dist ./*.pyc ./*.tgz ./*.egg-info")


setup(
    name="gj_utils",
    packages=find_packages(),
    version="0.1.0",
    description="cross-repo utility functionality",
    author="gareth jones",
    cmdclass={"clean": CleanCommand}
)
