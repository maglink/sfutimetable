import re
import os
import shutil
import urllib.request
import urllib.error
from time import sleep


def search_url(url,pat):
    """Search file at /url/ for /pat/"""
    try:
        furl = urllib.request.urlopen(url)
        html = furl.read().decode("utf8", "replace")
        found_list = re.findall(pat,html)
    
        return found_list

    except urllib.error.URLError:
        print("ERROR: Could not open url: {0}".format(url))
        return []
        

def download_files(file_list,dir_name="data",sleep_time=0.05):
    for file_url in file_list:
        print(os.path.basename(file_url))
        file_name = os.path.join(dir_name,os.path.basename(file_url))
        try:
            file_data = urllib.request.urlretrieve(file_url,file_name)
        except urllib.error.HTTPError as e:
            print("Failed to download:{} ({})".format(file_name,e))

        sleep(sleep_time)   


if __name__=="__main__":
    URL = "http://edu.sfu-kras.ru/timetable.xls"
    PAT = r"href='([:\w\.\/-]+\.xls)"
    PAT2 = r'''href=['"](.*?\?\d*)['"]'''
    if os.path.exists("data"):
        shutil.rmtree('data')
    sleep(0.1)
    if not os.path.exists('data'):
        os.mkdir('data')
    print("Connecting...")
    flist = search_url(URL,PAT)
    print("Downloading {} files:\t".format(len(flist)))
    download_files(flist,"data")
