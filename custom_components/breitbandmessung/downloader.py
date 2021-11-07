#!/usr/bin/env python3

import os
import requests
import unix_ar
import tarfile
from bs4 import BeautifulSoup
from pathlib import Path
from urllib.parse import urljoin
from tempfile import TemporaryDirectory


CHROMIUM_URL = 'https://launchpad.net/ubuntu/bionic/arm64/chromium-chromedriver/'
BINARY_PATH = Path.home() / '.breitbandmessung/bin/chromiumdriver'


def download(update: bool = False, src_url: str = CHROMIUM_URL, dest_path: Path = BINARY_PATH) -> str:
    """
    Downloads the chromiumdriver and returns the path to the binary
    """
    if dest_path.exists():
        return str(dest_path)

    if not dest_path.parent.exists():
        dest_path.parent.mkdir(parents=True)

    r = requests.get(src_url)
    r.raise_for_status()

    doc = BeautifulSoup(r.content, 'html.parser')

    latest_package_version = doc.select('table#publishing-summary > tbody > tr:nth-of-type(1) > td:nth-last-of-type(1)')[0].text

    r = requests.get(urljoin(src_url, latest_package_version))
    r.raise_for_status()

    doc = BeautifulSoup(r.content, 'html.parser')

    download_uri = doc.select('div#downloadable-files a.sprite[href]')[0].attrs['href']

    with TemporaryDirectory() as tmpdir:
        data = requests.get(str(download_uri))
        data.raise_for_status()

        deb_path = Path(tmpdir) / 'package.deb'

        with open(deb_path, 'wb') as deb_file:
            deb_file.write(data.content)

        ar_file = unix_ar.open(deb_path)
        tarball = ar_file.open('data.tar.xz')
        with tarfile.open(fileobj=tarball) as tar_file:
            driver_obj = tar_file.extractfile('./usr/bin/chromedriver')
            try:
                with open(dest_path, 'wb') as dest_obj:
                    dest_obj.write(driver_obj.read())
            except IOError:
                os.remove(dest_path)

    os.chmod(dest_path, 755)

    return str(dest_path)
