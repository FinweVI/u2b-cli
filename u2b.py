#!/usr/bin/env python3
import configparser
import argparse
import shutil
import time
import json
import sys
import os
import re
import requests

class U2B:

    """Main class to manage the API"""

    def __init__(self, download_path=None):
        config_file = os.environ['HOME'] + "/.u2b.ini"
        if os.path.isfile(config_file):
            # Loading the token from the config file
            config = configparser.ConfigParser()
            config.sections()
            config.read(config_file)
            self.__token = config['DEFAULT']['TOKEN']
            self.__api = config['DEFAULT']['API_BASE']
            self.__dl_path = config['DEFAULT']['DL_FOLDER']
            if download_path is not None:
                self.__dl_path = download_path
        else:
            print("The config file doesn't exist! Can't continue!")
            print("Please read the doc!")
            sys.exit(1)

    def get_file_id(self, data):
        """We extract the file ID from the link.
        Accepted format:
            https://uptobox.com/file_id/file_name.ext
            https://uptobox.com/file_id
            file_id
        """
        if data.startswith("http"):
            file_match = re.match(
                r'http[s]{0,1}://\w+.[\w]{2,3}/(\w{12})[/]?.*',
                data)
            if file_match:
                return file_match.group(1)
        if len(data) != 12:
            return False
        return False

    def get_link(self, file_id, password, waiting_token=None):
        """Send the proper request to the API.
        Will send the password in the payload if the waitingToken is not
        defined.
        It'll send the waitingToken otherwise, because it means we have waiting
        long enough.
        """

        payload = {'token': self.__token, 'id': self.get_file_id(file_id)}
        if waiting_token is not None:
            payload['waitingToken'] = waiting_token
        else:
            payload['password'] = password
        return requests.get("{}/link".format(self.__api), params=payload)

    def process_link(self, file_id, password=""):
        """Process the link and deal with the waiting time on the API side."""

        waiting_token = None
        try:
            while True:
                json_output = self.get_link(file_id, password, waiting_token).json()
                if 'waitingToken' in json_output['data']:
                    waiting = json_output['data']['waiting'] + 5
                    print("We need to wait {}s".format(waiting))
                    time.sleep(waiting)
                    continue
                if json_output['statusCode'] == 0:
                    return json_output['data']['dlLink']

                return False
        except (json.decoder.JSONDecodeError, KeyError):
            return False

    def download(self, link, force):
        """Download a given file with the provided link to the DL_FOLDER
        specified in the configuration file."""

        get_file = requests.get(link, stream=True)
        filename = link.split('/')[-1]
        download_full_path = self.__dl_path + "/" + filename
        if os.path.isfile(download_full_path) and not force:
            print("The file {} already exist in {}. Skipping.".format(
                filename, self.__dl_path))
            return False
        if get_file.status_code == 200:
            with open(download_full_path, 'wb') as downloaded_file:
                shutil.copyfileobj(get_file.raw, downloaded_file)
            return True
        else:
            print("Unable to retrieve the file! {}"
                  "{}".format(get_file.status_code, get_file.text))
            sys.exit(1)

def main(u2b_data):
    if not u2b_data.file_id and not u2b_data.file:
        print("Error! You need to specify at least a file_id or a file.")
        sys.exit(1)

    manage = U2B(u2b_data.folder)
    toprocess_file_id = []
    if u2b_data.file_id is not None:
        toprocess_file_id.append(u2b_data.file_id)
    if u2b_data.file is not None:
        with open(u2b_data.file, 'r') as links_file:
            content = links_file.readlines()
        toprocess_file_id.extend([x.strip() for x in content])
    print("Getting the file link for {} file(s).".format(
        len(toprocess_file_id)))
    for file_id in toprocess_file_id:
        link = manage.process_link(file_id, u2b_data.password)
        if not link:
            print("Unable to process the link for file {} ; {}".format(
                file_id, link))
            continue
        if u2b_data.download:
            print("""Downloading the file {}, please wait, this could take a
                  while""".format(link.split('/')[-1]))
            download_status = manage.download(link, u2b_data.force_download)
            if not download_status:
                print("Oops, something went wrong during the download!")
            else:
                print("File downloaded !")
        else:
            print(link)

if __name__ == '__main__':
    PARSER = argparse.ArgumentParser("U2B CLI")
    PARSER.add_argument("--file_id", default=None,
                        help="The File ID you want to retrieve")
    PARSER.add_argument("--password", default="",
                        help="The password of the file you want to retrieve. default to empty")
    PARSER.add_argument("--folder", default=None,
                        help="The folder you want to download the file to")
    PARSER.add_argument("--file", default=None,
                        help="The file with all the links")
    PARSER.add_argument("--download", action="store_true",
                        help="Download the files after getting the links")
    PARSER.add_argument("--force_download", action="store_true",
                        help="Force the download even if the file already exist")
    ARGS = PARSER.parse_args()
    main(ARGS)
