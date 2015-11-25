#!/usr/bin/python
import json
import os
from urllib.request import urlopen
def hbytes(num):
    for x in ['bytes','KB','MB','GB']:
        if num < 1024.0:
            return "%3.1f%s" % (num, x)
        num /= 1024.0
    return "%3.1f%s" % (num, 'TB')

search_title = input("What to search for?\n")
print("Fetching results...")
search_title = search_title.replace(" ","+")
url = "http://torrentproject.org/?s="+search_title+"&out=json&num=150"
response = urlopen(url).read().decode('utf8')
obj = json.loads(response)
total_found = int(obj.get('total_found'))

if total_found > 150:
    search_max = 150
else:
    search_max = total_found
print("==============================RESULTS==============================")
for i in range(search_max, 0, -1):
    print(i,")",obj.get(str(i), {}).get("title")," | Size:", hbytes(obj.get(str(i), {}).get("torrent_size")), "Seeds:", obj.get(str(i), {}).get("seeds"))
print("==============================RESULTS==============================")

if total_found > 150:
    print("Result number exceeds server's limit (150). Printed 150 first results in descending order.")
print("Total torrents found:",total_found)
valid_choice = 0
while valid_choice==0:
    choice = str(input("Type in the number of the torrent you want to download:"))
    if 0 < int(choice) < search_max :
        valid_choice = 1

choice_title = obj.get(choice, {}).get("title")
choice_hash = obj.get(choice, {}).get("torrent_hash")
print("Hash of torrent:",choice_hash,"\nFetching trackers...")
trackers_url = "http://torrentproject.org/"+choice_hash+"/trackers_json"
response = urlopen(trackers_url).read().decode("utf8")
obj = json.loads(response)
torrent_link = "magnet:?xt=urn:btih:"+choice_hash+"&dn="+choice_title
for i in obj:
    torrent_link += "&tr="+i
print("Launching xdg-open with torrent link..")
cmd="xdg-open \""+torrent_link+"\""
os.system(cmd)
print("Exit")
