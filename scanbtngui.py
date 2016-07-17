#!/bin/python
# This is a python2 script

import os, sys, datetime, ConfigParser
from Tkinter import *
from subprocess import Popen, PIPE

sys.argv.append("todo: device")

class ScanCommand(object):
    program = "scanimage"
    device = sys.argv[1]
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    fmt_adf_simplex = ""
    fmt_adf_duplex = ""
    format = "jpeg"
    resolution = "100"

    def __init__(self, config):
        self.config = config

    def getscancmd(self):
        if self.config.get("General", "pagemode") == "duplex":
            source = self.fmt_adf_duplex
        elif self.config.get("General", "pagemode") == "simplex":
            source = self.fmt_adf_simplex
        else:
            print "Error: mode '%s' not implemented" % self.config.mode
            source = None

        cmd = [
            self.program,
            "--device-name", self.device,
            "--resolution", self.config.get("General", "resolution"),
            "--format", self.format,
        ]
        if source != None:
            cmd.append("--source")
            cmd.append(source)

        return cmd

class BrotherAPC1100(ScanCommand):
    fmt_adf_simplex = "Automatic Document Feeder(left aligned,Simplex)"
    fmt_adf_duplex = "Automatic Document Feeder(left aligned,Duplex)"

class ScanGui(Frame):
    def __init__(self, parent):
        Frame.__init__(self, parent)

        self.RESOLUTIONS = [
            ("100", "100"),
            ("300", "300"),
            ("600", "600"),
        ]

        self.COLORS = [
            ("Color", "rgb"),
            ("Gray", "gray"),
        ]

        self.MODES = [
            ("Duplex", "duplex"),
            ("Simplex", "simplex"),
        ]
        self.parent = parent
        self.initOCR()
        self.initUI()

    def initOCR(self):

        self.langs_available = ["ocr not available"]

        try:
            p=Popen(["which", "ocrmypdf"], stdout=PIPE, stderr=PIPE)
            out, err = p.communicate()
        except OSError:
            print "error checking for ocrmypdf"
            self.ocravailable = False
        else:
            if p.returncode != 0:
                print "ocrmypdf not found"
                self.ocravailable = False
            else:
                self.ocravailable = True

        if not self.ocravailable:
            return

        try:
            p=Popen(["tesseract", "--list-langs"], stdout=PIPE, stderr=PIPE)
            out, err=p.communicate()
            # tesseract prints this list into stderr?
            langs=err
        except OSError:
            print "could not determine available languages"
        else:
            self.langs_available = langs.strip().split("\n")[1:]
            self.langs_available.insert(0, "no ocr")

    def initUI(self):
        self.parent.title("brscan-key")
        self.pack(fill=BOTH, expand=False)
        self.columnconfigure(1, weight=1)
        self.columnconfigure(3, pad=7)
        self.rowconfigure(3, weight=1)
        self.rowconfigure(5, pad=7)

        lbl = Label(self, text="Resolution")
        lbl.grid(sticky=W+E, pady=4, padx=5, row=0, column=0)

        self.resolution = StringVar()
        for i, (text, value) in enumerate(self.RESOLUTIONS):
            b = Radiobutton(self, text=text, variable=self.resolution, value=value, command=self.onResolutionChange)
            b.grid(row=i+1, column=0, columnspan=1, rowspan=1, padx=5, sticky=E+W)
        self.resolution.set(config.get("General", "resolution"))

        lbl = Label(self, text="Colorscale")
        lbl.grid(sticky=E+W, pady=4, padx=5, column=1, row=0)

        self.color = StringVar()

        for i, (text, value) in enumerate(self.COLORS):
            b = Radiobutton(self, text=text, variable=self.color, value=value, command=self.onColorChange)
            b.grid(row=i+1, column=1, columnspan=1, rowspan=1, padx=5, sticky=E+W)
        self.color.set(config.get("General", "color"))

        lbl = Label(self, text="Mode")
        lbl.grid(sticky=E+W, pady=4, padx=5, column=2, row=0)

        self.pagemode = StringVar()

        for i, (text, value) in enumerate(self.MODES):
            b = Radiobutton(self, text=text, variable=self.pagemode, value=value, command=self.onPagemodeChange)
            b.grid(row=i+1, column=2, columnspan=1, rowspan=1, padx=5, sticky=E+W)
        self.pagemode.set(config.get("General", "pagemode"))

        lbl = Label(self, text="Ask again (minutes)")
        lbl.grid(sticky=E+W, pady=4, padx=5, column=0, columnspan=2)
        timeout = IntVar()
        timeout.set(2)

        e = Entry(self, textvariable=timeout, width=3, justify=LEFT)
        e.grid(padx=5, row=4, column=2, sticky=E+W)

        lbl = Label(self, text="OCR options")
        lbl.grid(sticky=E+W, pady=4, padx=5, column=0, columnspan=1)

        self.ocrlang = StringVar()
        if len(self.langs_available):
            self.ocrlang.set(config.get("OCR", "language"))
        o = OptionMenu(self, self.ocrlang, *self.langs_available, command=self.onOCRLangChange)
        o.grid(row=6, column=0, sticky=E+W)


        cancelbtn = Button(self, text="Cancel", command=self.cancel)
        cancelbtn.grid(column=0, row=7, sticky=E+W)

        okbtn = Button(self, text="Scan", command=self.startscan)
        okbtn.grid(column=2, row=7, sticky=E+W)

    def onColorChange(self):
        config.set("General", "color", self.color.get())
        self.storeconfig()

    def onPagemodeChange(self):
        config.set("General", "pagemode", self.pagemode.get())
        self.storeconfig()

    def onResolutionChange(self):
        config.set("General", "resolution", self.resolution.get())
        self.storeconfig()

    def onOCRLangChange(self, language):
        config.set("OCR", "language", self.ocrlang.get())
        self.storeconfig()

    def storeconfig(self):
        with open(configpath, "wb") as configfile:
            config.write(configfile)

    def startscan(self):
        print "TODO: start scan"
        s = BrotherAPC1100(config)
        print s.getscancmd()

    def cancel(self):
        exit(0)



def main():
    global configpath
    configpath = os.path.join(os.path.expanduser("~"), ".config", "scanbtngui.ini")
    global config
    config = ConfigParser.ConfigParser()
    if os.path.exists(configpath):
        config.readfp(open(configpath))
    else:
        print "Create default config"
        config.add_section("General")
        config.set("General", "pagemode", "duplex")
        config.set("General", "color", "rgb")
        config.set("General", "resolution", 300)
        config.add_section("OCR")
        config.set("OCR", "language", "no ocr")

        configfile = open(configpath, "wb")
        config.write(configfile)
        configfile.close()

    top = Tk()
    app = ScanGui(top)
    top.mainloop()

if __name__ == "__main__":
    main()

