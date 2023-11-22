from setuptools import setup

setup(
    name="envgym",
    version="0.1.0",
    install_requires=["gymnasium==0.26.3", "pygame==2.1.0"],
)

# import requests
# import zipfile
# import os
# import site

# # URL of the zip file
# version = "0.2.0-2"
# url = f"https://github.com/hanzi/libmgba-py/releases/download/{version}/libmgba-py_{version}_ubuntu-lunar.zip"

# # Send a HTTP request to the URL of the zip file
# response = requests.get(url)

# # Save the zip file
# with open(f'libmgba-py_{version}_ubuntu-lunar.zip', 'wb') as f:
#   f.write(response.content)

# # Open the zip file
# with zipfile.ZipFile(f'libmgba-py_{version}_ubuntu-lunar.zip', 'r') as zip_ref:
#   # Extract the zip file to the site-packages directory
#   site_packages_dir = site.getsitepackages()[0]
#   zip_ref.extractall(site_packages_dir)
