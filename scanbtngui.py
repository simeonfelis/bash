#!/bin/python
# This is a python2 script

from Tkinter import *
from subprocess import Popen, PIPE


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
        self.initLangs()
        self.initUI()

    def initLangs(self):
        try:
            #langs=check_output(["tesseract", "--list-langs"])
            p=Popen(["tesseract", "--list-langs"], stdout=PIPE, stderr=PIPE)
            out, err=p.communicate()
            # tesseract prints this list into stderr?
            langs=err
        except OSError:
            self.langs_available = ["ocr not available"]
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
            b = Radiobutton(self, text=text, variable=self.resolution, value=value)
            b.grid(row=i+1, column=0, columnspan=1, rowspan=1, padx=5, sticky=E+W)
        self.resolution.set("300")

        lbl = Label(self, text="Colorscale")
        lbl.grid(sticky=E+W, pady=4, padx=5, column=1, row=0)

        self.color = StringVar()

        for i, (text, value) in enumerate(self.COLORS):
            b = Radiobutton(self, text=text, variable=self.color, value=value)
            b.grid(row=i+1, column=1, columnspan=1, rowspan=1, padx=5, sticky=E+W)
        self.color.set("rgb")

        lbl = Label(self, text="Mode")
        lbl.grid(sticky=E+W, pady=4, padx=5, column=2, row=0)

        self.pagemode = StringVar()

        for i, (text, value) in enumerate(self.MODES):
            b = Radiobutton(self, text=text, variable=self.pagemode, value=value)
            b.grid(row=i+1, column=2, columnspan=1, rowspan=1, padx=5, sticky=E+W)
        self.pagemode.set("duplex")

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
            if "deu" in self.langs_available:
                self.ocrlang.set("deu")
            else:
                self.ocrlang.set(self.langs_available[0])
        else:
            self.ocrlang.set("ocr not available")
        o = OptionMenu(self, self.ocrlang, *self.langs_available)
        o.grid(row=6, column=0, sticky=E+W)


        cancelbtn = Button(self, text="Cancel")
        cancelbtn.grid(column=0, row=7, sticky=E+W)

        okbtn = Button(self, text="Scan")
        okbtn.grid(column=2, row=7, sticky=E+W)

    def onocrclick(self):
        print "useocr clicked"


def main():
    top = Tk()
    #top.geometry("350x300")
    app = ScanGui(top)
    top.mainloop()

if __name__ == "__main__":
    main()

