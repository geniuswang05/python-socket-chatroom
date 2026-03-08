#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Apr 30 13:36:58 2021

@author: bing
"""

# import all the required  modules
import threading
import select
import tkinter.messagebox as msgb
from tkinter import *
from tkinter import Toplevel
from chat_utils import *
import json
import subprocess

# GUI class for the chat
class GUI:
    player_X = "X"
    player_O = "O"
    empty_space = " "
    # constructor method
    def __init__(self, send, recv, sm, s):
        # chat window which is currently hidden
        self.Window = Tk()
        self.Window.withdraw()
        self.send = send
        self.recv = recv
        self.sm = sm
        self.socket = s
        self.my_msg = ""
        self.system_msg = ""
        self.users = []
        self.error_msg = None
        self.game = None

    def _rounded_rect(self, canvas, x1, y1, x2, y2, r, **kwargs):
        points = [
            x1 + r, y1,
            x2 - r, y1,
            x2, y1,
            x2, y1 + r,
            x2, y2 - r,
            x2, y2,
            x2 - r, y2,
            x1 + r, y2,
            x1, y2,
            x1, y2 - r,
            x1, y1 + r,
            x1, y1
        ]
        return canvas.create_polygon(points, smooth=True, splinesteps=36, **kwargs)

    def _pill_button(
        self,
        parent,
        text,
        command,
        width=230,
        height=44,
        bg="#f8fafc",
        fg="#0f172a",
        hover="#e2e8f0",
        radius=16
    ):
        holder = Frame(parent, bg=parent.cget("bg"), highlightthickness=0, bd=0)
        holder.configure(width=width, height=height)
        holder.pack_propagate(False)

        c = Canvas(
            holder,
            width=width,
            height=height,
            bg=parent.cget("bg"),
            highlightthickness=0,
            bd=0,
            relief=FLAT,
            cursor="hand2"
        )
        c.pack(fill=BOTH, expand=True)
        shape = self._rounded_rect(c, 2, 2, width - 2, height - 2, radius, fill=bg, outline="")
        label = c.create_text(width // 2, height // 2, text=text, fill=fg, font=("Helvetica", 11, "bold"))

        def on_enter(_):
            c.itemconfig(shape, fill=hover)

        def on_leave(_):
            c.itemconfig(shape, fill=bg)

        def on_click(_):
            command()

        for target in (c,):
            target.bind("<Enter>", on_enter)
            target.bind("<Leave>", on_leave)
            target.bind("<Button-1>", on_click)

        c.tag_bind(label, "<Button-1>", on_click)
        c.tag_bind(shape, "<Button-1>", on_click)
        return holder
    def login_error(self, msg):
        self.error_msg.destroy()
        self.error_msg = Label(
            self.loginCard,
            text=msg,
            fg="#ef4444",
            bg="#ffffff",
            font=("Helvetica", 11, "bold")
        )
        self.error_msg.place(relx=0.08, rely=0.92)

    def login(self):
        # login window
        self.login = Toplevel()
        # set the title
        self.login.title("Live Chat Login")
        self.login.resizable(width=False, height=False)
        self.login.geometry("460x350")
        self.login.configure(bg="#f3f4f6")

        self.loginCard = Frame(self.login, bg="#ffffff", highlightthickness=1, highlightbackground="#e5e7eb")
        self.loginCard.place(relx=0.07, rely=0.08, relwidth=0.86, relheight=0.84)

        self.pls = Label(
            self.loginCard,
            text="Welcome to Live Chat",
            justify=CENTER,
            bg="#ffffff",
            fg="#111827",
            font=("Helvetica", 16, "bold")
        )
        self.pls.place(relx=0.08, rely=0.08)

        self.subTitle = Label(
            self.loginCard,
            text="Sign in or create an account",
            bg="#ffffff",
            fg="#6b7280",
            font=("Helvetica", 10)
        )
        self.subTitle.place(relx=0.08, rely=0.17)

        self.labelName = Label(self.loginCard, text="Username", bg="#ffffff", fg="#374151", font=("Helvetica", 11, "bold"))
        self.labelName.place(relx=0.08, rely=0.30)

        self.entryName = Entry(
            self.loginCard,
            font=("Helvetica", 12),
            relief=FLAT,
            bg="#f9fafb",
            highlightthickness=1,
            highlightbackground="#d1d5db",
            highlightcolor="#2563eb"
        )
        self.entryName.place(relwidth=0.84, relheight=0.12, relx=0.08, rely=0.38)
        # set the focus of the curser
        self.entryName.focus()
        # create a Continue Button
        # along with action
        self.labelPWD = Label(self.loginCard, text='Password', bg="#ffffff", fg="#374151", font=("Helvetica", 11, "bold"))
        self.labelPWD.place(relx=0.08, rely=0.53)
        self.entryPWD = Entry(
            self.loginCard,
            font=("Helvetica", 12),
            show="*",
            relief=FLAT,
            bg="#f9fafb",
            highlightthickness=1,
            highlightbackground="#d1d5db",
            highlightcolor="#2563eb"
        )
        self.entryPWD.place(relwidth=0.84, relheight=0.12, relx=0.08, rely=0.61)

        self.reg = self._pill_button(
            self.loginCard,
            text="Register",
            command=lambda: self.Register(self.entryName.get(), self.entryPWD.get()),
            bg="#e2e8f0",
            fg="#0f172a",
            hover="#cbd5e1",
            width=146,
            height=42,
            radius=14
        )
        self.go = self._pill_button(
            self.loginCard,
            text="Log In",
            command=lambda: self.goAhead(self.entryName.get(), self.entryPWD.get()),
            bg="#0ea5e9",
            fg="#f8fafc",
            hover="#0284c7",
            width=146,
            height=42,
            radius=14
        )
        self.reg.place(relx=0.08, rely=0.78)
        self.go.place(relx=0.54, rely=0.78)

        self.error_msg = Label(self.loginCard, text="", bg="#ffffff", font=("Helvetica", 11, "bold"))
        self.error_msg.place(relx=0.08, rely=0.92)

        self.Window.mainloop()

    def goAhead(self, name, pwd):
        # Check if a name is provided
        if len(name) > 0:
            # Create a JSON message containing login action, username, and password
            msg = json.dumps({"action": "login", "name": name, "pwd": pwd})
            # Send the login message to the server
            self.send(msg)
            # Receive response from the server
            response = json.loads(self.recv())
            # Check the status of the response
            if response["status"] == 'ok':
                # Close the login window upon successful login
                self.login.destroy()
                self.sm.set_state(S_LOGGEDIN)
                self.sm.set_myname(name)
                process = threading.Thread(target=self.proc)
                process.daemon = True
                process.start()
                process = threading.Thread(target=self.game)
                process.daemon = True
                process.start()
                #set up the layout and the text con
                self.layout(name)
                self.textCons.config(state=NORMAL)
                # self.textCons.insert(END, "hello" +"\n\n")
                self.textCons.insert(END, f"Hello, {self.name}!\nWelcome to the Chat Room!!\n\n")
                self.textCons.insert(END, menu + "\n\n")
                self.textCons.config(state=DISABLED)
                self.textCons.see(END)
            elif response["status"] == 'wrong pwd':
                self.login_error("Wrong Password")
            else:
                self.login_error("No Such User")

    def Register(self, name, pwd):
        if len(name) > 0:
            print(name, pwd)
            msg = json.dumps({"action": "register", "name": name, "pwd": pwd})
            self.send(msg)
            response = json.loads(self.recv())
            if response["status"] == 'ok':
                self.login.destroy()
                self.sm.set_state(S_LOGGEDIN)
                self.sm.set_myname(name)

                self.layout(name)
                self.textCons.config(state=NORMAL)
                self.textCons.insert(END, "Hello, " + name + "!\nWelcome to the Chat Room!!\n\n")
                self.textCons.insert(END, menu + "\n\n")
                self.textCons.config(state=DISABLED)
                self.textCons.see(END)
                process = threading.Thread(target=self.proc)
                process.daemon = True
                process.start()
            elif response["status"] == 'duplicate':
                self.login_error("Name Already Exists")
            else:
                self.login_error("Name should be less than 7 characters.")
    def gameButton(self):
        game_file = 'game.py'
        subprocess.run(['python', game_file])
    # The main layout of the chat
    def layout(self, name):
        self.name = name
        self.Window.deiconify()
        self.Window.title("Live Chat")
        self.Window.geometry("920x700")
        self.Window.minsize(780, 620)
        self.Window.configure(bg="#0b1220")

        # clear old widgets if layout is called again
        for widget in self.Window.winfo_children():
            widget.destroy()

        self.mainWrap = Frame(self.Window, bg="#0b1220")
        self.mainWrap.pack(fill=BOTH, expand=True, padx=20, pady=20)

        # ---------- header ----------
        header = Frame(self.mainWrap, bg="#0f172a", height=74, highlightthickness=1, highlightbackground="#1e293b")
        header.pack(fill=X)
        header.pack_propagate(False)

        Label(
            header,
            text="Live Chat Console",
            bg="#0f172a",
            fg="#f8fafc",
            font=("Helvetica", 19, "bold")
        ).pack(side=LEFT, padx=18, pady=18)

        Label(
            header,
            text=f"{self.name}  |  Online",
            bg="#0f172a",
            fg="#7dd3fc",
            font=("Helvetica", 11, "bold")
        ).pack(side=RIGHT, padx=18)

        # ---------- body ----------
        main = Frame(self.mainWrap, bg="#0b1220")
        main.pack(fill=BOTH, expand=True, pady=(14, 0))

        leftPanel = Frame(main, bg="#0f172a", width=250, highlightthickness=1, highlightbackground="#1e293b")
        leftPanel.pack(side=LEFT, fill=Y)
        leftPanel.pack_propagate(False)

        self.chatCard = Frame(main, bg="#f8fafc", highlightthickness=1, highlightbackground="#cbd5e1")
        self.chatCard.pack(side=LEFT, fill=BOTH, expand=True, padx=(14, 0))
        self.chatCard.grid_rowconfigure(1, weight=1)
        self.chatCard.grid_columnconfigure(0, weight=1)

        Label(
            leftPanel,
            text="Quick Actions",
            bg="#0f172a",
            fg="#f8fafc",
            font=("Helvetica", 12, "bold")
        ).pack(anchor="w", padx=14, pady=(16, 4))
        Label(
            leftPanel,
            text="All original chat controls",
            bg="#0f172a",
            fg="#94a3b8",
            font=("Helvetica", 9)
        ).pack(anchor="w", padx=14, pady=(0, 10))

        buttonPanel = Frame(leftPanel, bg="#0f172a")
        buttonPanel.pack(fill=X, padx=14, pady=(0, 12))

        def side_btn(text, cmd, tone="normal"):
            colors = {
                "normal": ("#f8fafc", "#0f172a", "#e2e8f0"),
                "primary": ("#bae6fd", "#082f49", "#7dd3fc"),
                "danger": ("#fee2e2", "#7f1d1d", "#fecaca")
            }
            bg, fg, active = colors[tone]
            return self._pill_button(
                buttonPanel,
                text=text,
                command=cmd,
                fg=fg,
                bg=bg,
                hover=active,
                width=222,
                height=42,
                radius=14
            )

        self.buttonWho = side_btn("Who", self.whoButton)
        self.buttonWho.pack(fill=X, pady=4)
        self.buttonTime = side_btn("Time", self.timeButton)
        self.buttonTime.pack(fill=X, pady=4)
        self.buttonGame = side_btn("Game", self.gameButton, "primary")
        self.buttonGame.pack(fill=X, pady=4)
        self.button_quit = side_btn("Quit", self.quit_window, "danger")
        self.button_quit.pack(fill=X, pady=4)

        Label(
            leftPanel,
            text="Connect User",
            bg="#0f172a",
            fg="#f8fafc",
            font=("Helvetica", 11, "bold")
        ).pack(anchor="w", padx=14, pady=(12, 6))

        self.entryPeer = Entry(
            leftPanel,
            font=("Helvetica", 11),
            bg="#020617",
            fg="#e2e8f0",
            insertbackground="#e2e8f0",
            relief=FLAT,
            highlightthickness=1,
            highlightbackground="#334155",
            highlightcolor="#38bdf8"
        )
        self.entryPeer.pack(fill=X, padx=14, ipady=9)

        self.buttonConnect = self._pill_button(
            leftPanel,
            text="Connect",
            command=lambda: self.connectButton(self.entryPeer.get()),
            bg="#bae6fd",
            fg="#082f49",
            hover="#7dd3fc",
            width=222,
            height=42,
            radius=14
        )
        self.buttonConnect.pack(fill=X, padx=14, pady=(8, 14))

        Label(
            leftPanel,
            text="Fetch Poem",
            bg="#0f172a",
            fg="#f8fafc",
            font=("Helvetica", 11, "bold")
        ).pack(anchor="w", padx=14, pady=(4, 6))

        self.entryPoem = Entry(
            leftPanel,
            font=("Helvetica", 11),
            width=10,
            bg="#020617",
            fg="#e2e8f0",
            insertbackground="#e2e8f0",
            relief=FLAT,
            highlightthickness=1,
            highlightbackground="#334155",
            highlightcolor="#38bdf8"
        )
        self.entryPoem.pack(fill=X, padx=14, ipady=9)

        self.buttonPoem = self._pill_button(
            leftPanel,
            text="Poem",
            command=lambda: self.poemButton(self.entryPoem.get()),
            bg="#f1f5f9",
            fg="#0f172a",
            hover="#e2e8f0",
            width=222,
            height=42,
            radius=14
        )
        self.buttonPoem.pack(fill=X, padx=14, pady=(8, 14))

        chatTitle = Label(
            self.chatCard,
            text="Conversation",
            bg="#f8fafc",
            fg="#111827",
            font=("Helvetica", 12, "bold")
        )
        chatTitle.grid(row=0, column=0, sticky="w", padx=16, pady=(14, 0))

        textWrap = Canvas(self.chatCard, bg="#f8fafc", highlightthickness=0, bd=0, relief=FLAT)
        textWrap.grid(row=1, column=0, sticky="nsew", padx=16, pady=(8, 10))

        textInner = Frame(textWrap, bg="#ffffff", bd=0, highlightthickness=0)
        textInnerWin = textWrap.create_window(14, 14, anchor="nw", window=textInner)
        convRect = {"id": None}

        def draw_conv_shell(_=None):
            w = textWrap.winfo_width()
            h = textWrap.winfo_height()
            if w < 20 or h < 20:
                return
            if convRect["id"] is not None:
                textWrap.delete(convRect["id"])
            convRect["id"] = self._rounded_rect(
                textWrap,
                2, 2, w - 2, h - 2, 18,
                fill="#ffffff",
                outline="#dbe3ef",
                width=2
            )
            textWrap.tag_lower(convRect["id"])
            textWrap.coords(textInnerWin, 14, 14)
            textWrap.itemconfigure(textInnerWin, width=max(10, w - 28), height=max(10, h - 28))

        textWrap.bind("<Configure>", draw_conv_shell)

        self.textCons = Text(
            textInner,
            bg="#ffffff",
            fg="#1f2937",
            insertbackground="#111827",
            font=("Helvetica", 13),
            wrap=WORD,
            relief=FLAT,
            bd=0,
            highlightthickness=0,
            padx=12,
            pady=12,
            spacing1=4,
            spacing3=8
        )
        self.textCons.pack(side=LEFT, fill=BOTH, expand=True)
        self.textCons.configure(cursor="arrow", state=DISABLED)

        scrollbar = Scrollbar(textInner, command=self.textCons.yview)
        scrollbar.pack(side=RIGHT, fill=Y)
        self.textCons.config(yscrollcommand=scrollbar.set)

        # ---------- composer ----------
        topRow = Frame(self.chatCard, bg="#f8fafc")
        topRow.grid(row=2, column=0, sticky="ew", padx=16, pady=(0, 16))

        self.entryMsg = Entry(
            topRow,
            bg="#ffffff",
            fg="#111827",
            insertbackground="#111827",
            relief=FLAT,
            font=("Helvetica", 12),
            highlightthickness=1,
            highlightbackground="#cbd5e1",
            highlightcolor="#38bdf8"
        )
        self.entryMsg.pack(side=LEFT, fill=X, expand=True, ipady=12, padx=(0, 10))
        self.entryMsg.focus()
        self.entryMsg.bind("<Return>", lambda event: self.sendButton(self.entryMsg.get()))

        self.buttonM = self._pill_button(
            topRow,
            text="Send",
            command=lambda: self.sendButton(self.entryMsg.get()),
            bg="#0ea5e9",
            fg="#f8fafc",
            hover="#0284c7",
            width=140,
            height=42,
            radius=16
        )
        self.buttonM.pack(side=RIGHT)
    # Definitions for Button Actions
    def timeButton(self):
        self.my_msg = 'time'
    def quitButton(self):
        self.my_msg = 'q'
    def poemButton(self,p):
        self.my_msg = 'p' + p
        self.entryPoem.delete(0, END)
    def connectButton(self,peer):
        self.my_msg = 'c' + peer
        self.entryPeer.delete(0, END)
    def whoButton(self):
        self.my_msg = 'who'
    def quit_window(self):
        self.state = "q"
        self.Window.destroy()
    def sendButton(self, msg):
        self.my_msg = msg
        self.entryMsg.delete(0, END)
        self.textCons.config(state=NORMAL)
        self.textCons.insert(END, f"You: {msg}\n")
        self.textCons.config(state=DISABLED)
        self.textCons.see(END)
    def checker(self, index):
        self.my_msg = f"press_button_{index + 1}"
    def game_layout(self):
        self.gameWindow = Toplevel(self.Window)
        self.gameWindow.title(f'TIC-TAC-TOE for {self.name}')
        Label(self.gameWindow, text="player1 : X", font="times 15").grid(row=0, column=1)
        Label(self.gameWindow, text="player2 : O", font="times 15").grid(row=0, column=2)
        self.buttons = []
        for i in range(9):
            button = Button(self.gameWindow, width=15, height=7, font=('Times 16 bold'),
                            command=lambda i=i: self.checker(i))
            button.grid(row=1 + i // 3, column=1 + i % 3)
            self.buttons.append(button)


    def proc(self):
        # print(self.msg)
        while True:
            read, write, error = select.select([self.socket], [], [], 0)
            peer_msg = []
            # print(self.msg)
            if self.socket in read:
                peer_msg = self.recv()
            if len(self.my_msg) > 0 or len(peer_msg) > 0:
                # print(self.system_msg)
                self.system_msg = self.sm.proc(self.my_msg, peer_msg)
                self.my_msg = ""
                self.textCons.config(state=NORMAL)
                self.textCons.insert(END, self.system_msg + "\n\n")
                self.textCons.config(state=DISABLED)
                self.textCons.see(END)

    def run(self):
        self.login()

# create a GUI class object
if __name__ == "__main__":
    # g = GUI()
    pass
