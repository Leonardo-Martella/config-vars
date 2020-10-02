from setuptools import setup, find_packages


setup(name="configvars",
      version="1.0.0",
      description="Configuration variables made easy!",
      url="https://github.com/Leonardo-Martella/config-vars",
      author="Leonardo Martella",
      author_email="leonardomartella2002@gmail.com",
      license="MIT",
      keywords="config configuration variables development",
      project_urls={
          'Source': 'https://github.com/Leonardo-Martella/config-vars',
          'Tracker': 'https://github.com/pypa/sampleproject/issues',
      },
      install_requires=[],
      python_requires=">=3.7",
      packages=find_packages("src"),
      package_dir={"": "src"})
