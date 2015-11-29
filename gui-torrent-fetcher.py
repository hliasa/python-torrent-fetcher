#!/usr/bin/python
import gi,json,os
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk,Pango
from urllib.request import urlopen

columns = ["Torrent Name", "Seeders", "Leechers", "Size","hash"]

class MainWindow(Gtk.Window):

    def __init__(self):
        Gtk.Window.__init__(self, title="Lol")
        grid = Gtk.Grid()
        grid.set_row_spacing(5)
        grid.set_column_spacing(5)
        grid.set_margin_left(5)
        grid.set_margin_top(5)
        grid.set_margin_right(5)
        grid.set_margin_bottom(5)
        self.add(grid)
        self.btnSearch = Gtk.Button(label="Search")
        self.btnSearch.connect("clicked", self.on_btnSearch_clicked)
        self.btnQuit = Gtk.Button(label="Quit")
        self.btnQuit.connect("clicked", self.on_btnQuit_clicked)
        self.btnDownload = Gtk.Button(label="Download")
        self.btnDownload.connect("clicked", self.on_btnDownload_clicked)
        self.txtSearch = Gtk.Entry()
        self.txtSearch.set_placeholder_text("keyword(s)")
        self.lblTotal = Gtk.Label("")
        self.lsTorrent = Gtk.ListStore(str, str, str, str, str)
        self.tvTorrent = Gtk.TreeView.new_with_model(model=self.lsTorrent)
        self.scrList = Gtk.ScrolledWindow()
        self.scrList.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        self.scrList.set_min_content_height(200)
        self.scrList.set_min_content_width(800)
        self.scrList.add(self.tvTorrent)
        for i in range(len(columns)):
            cell = Gtk.CellRendererText()
            col = Gtk.TreeViewColumn(columns[i], cell, text=i)
            col.set_resizable(True)
            if i == 0:
                col.set_fixed_width(500)
            self.tvTorrent.append_column(col)
        grid.add(self.txtSearch)
        grid.attach(self.btnSearch,1,0,1,1)
        grid.attach(self.btnQuit,1,3,1,1)
        grid.attach(self.lblTotal,0,2,2,1)
        grid.attach(self.scrList,0,1,2,1)
        grid.attach(self.btnDownload,0,3,1,1)

    def on_btnDownload_clicked(self, widget):
        try:
            tree_selection = self.tvTorrent.get_selection()
            model, treeiter = tree_selection.get_selected()
            thash = model[treeiter][4]
            ttitle = model[treeiter][0]
            trackers_url = "http://torrentproject.org/"+thash+"/trackers_json"
            response = urlopen(trackers_url).read().decode("utf-8")
            obj = json.loads(response)
            torrent_magnet = "magnet:?xt=urn:btih:"+thash+"&dn="+ttitle
            for i in obj:
                torrent_magnet += "&tr="+i
            print(torrent_magnet)
            os.system("xdg-open \""+torrent_magnet+"\"")
        except TypeError:
            print("No selection")

    def on_btnSearch_clicked(self, widget):
        search_title = self.txtSearch.get_text()
        if search_title != "":
            search_title = search_title.replace(" ","+")
            url = "http://torrentproject.org/?s="+search_title+"&out=json&num=150"
            response = urlopen(url).read().decode("utf-8")
            obj = json.loads(response)
            total = int(obj.get("total_found"))
            if total != 0:
                self.lsTorrent.clear()
                if total > 150:
                    search_max = 150
                    self.lblTotal.set_text(str(total)+" torrents found. Server limit is 150 torrents. The above list contains 150 results(most relevant).")
                else:
                    search_max = total
                    self.lblTotal.set_text(str(total)+" torrents found")
                dlist = []
                for i in range(1, search_max+1):
                    title = str(obj.get(str(i), {}).get("title"))
                    seeders = str(obj.get(str(i), {}).get("seeds"))
                    leechers = str(obj.get(str(i), {}).get("leechs"))
                    size = hbytes(int(obj.get(str(i), {}).get("torrent_size")))
                    thash = str(obj.get(str(i), {}).get("torrent_hash"))
                    dlist.append([title,seeders,leechers,size,thash])
                for i in range(len(dlist)):
                    self.lsTorrent.append(dlist[i])
            else:
                self.lblTotal.set_text("0 results")
        else:
            print("No keyword given")

    def on_btnQuit_clicked(self, widget):
        Gtk.main_quit()

def hbytes(num):
    for x in ['bytes','KB','MB','GB']:
        if num < 1024.0:
            return "%3.1f%s" % (num, x)
        num /= 1024.0
    return "%3.1f%s" % (num, 'TB')

win = MainWindow()
win.connect("delete-event", Gtk.main_quit)
win.show_all()
Gtk.main()
