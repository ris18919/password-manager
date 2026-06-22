import json
import random
import pyperclip
import tkinter as tk
from tkinter import messagebox, ttk
import os

# ─────────────────────────── THEME ───────────────────────────
BG        = "#0f1117"
PANEL     = "#1a1d27"
ACCENT    = "#7c5cfc"
ACCENT2   = "#5e3ebd"
SUCCESS   = "#22c55e"
DANGER    = "#ef4444"
TEXT      = "#e2e8f0"
SUBTEXT   = "#8892a4"
BORDER    = "#2d3148"
ENTRY_BG  = "#252836"
ENTRY_FG  = "#e2e8f0"
CURSOR    = "#7c5cfc"
FONT_HEAD = ("Segoe UI", 22, "bold")
FONT_SUB  = ("Segoe UI", 10)
FONT_LABEL= ("Segoe UI", 10, "bold")
FONT_ENTRY= ("Segoe UI", 11)
FONT_BTN  = ("Segoe UI", 10, "bold")
FONT_TINY = ("Segoe UI", 9)

DATA_FILE = os.path.join(os.path.dirname(__file__), "data.json")


# ─────────────────────────── HELPERS ─────────────────────────
def load_data():
    try:
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)


def styled_button(parent, text, command, bg=ACCENT, fg="white",
                  width=None, font=FONT_BTN, padx=20, pady=10):
    kw = dict(text=text, command=command, bg=bg, fg=fg,
              font=font, relief="flat", cursor="hand2",
              activebackground=ACCENT2, activeforeground="white",
              padx=padx, pady=pady, bd=0)
    if width:
        kw["width"] = width
    btn = tk.Button(parent, **kw)

    def on_enter(e):
        btn.config(bg=ACCENT2 if bg == ACCENT else _darken(bg))
    def on_leave(e):
        btn.config(bg=bg)

    btn.bind("<Enter>", on_enter)
    btn.bind("<Leave>", on_leave)
    return btn


def _darken(hex_color):
    """Return a slightly darker version of a hex colour."""
    h = hex_color.lstrip("#")
    r, g, b = (max(0, int(h[i:i+2], 16) - 20) for i in (0, 2, 4))
    return f"#{r:02x}{g:02x}{b:02x}"


def styled_entry(parent, width=30, show=""):
    frame = tk.Frame(parent, bg=BORDER, padx=1, pady=1)
    e = tk.Entry(frame, width=width, bg=ENTRY_BG, fg=ENTRY_FG,
                 insertbackground=CURSOR, font=FONT_ENTRY,
                 relief="flat", bd=8, highlightthickness=0, show=show)
    e.pack(fill="x")

    def on_focus_in(ev):  frame.config(bg=ACCENT)
    def on_focus_out(ev): frame.config(bg=BORDER)

    e.bind("<FocusIn>",  on_focus_in)
    e.bind("<FocusOut>", on_focus_out)
    return frame, e


# ─────────────────────────── VAULT LIST WINDOW ───────────────
def show_vault():
    data = load_data()
    if not data:
        toast("Vault is empty — add some entries first!", DANGER)
        return

    win = tk.Toplevel(window)
    win.title("Your Vault")
    win.config(bg=BG)
    win.resizable(True, True)
    win.geometry("660x500")

    # header
    hdr = tk.Frame(win, bg=PANEL, pady=14)
    hdr.pack(fill="x")
    tk.Label(hdr, text="🔐  Your Vault", font=("Segoe UI", 15, "bold"),
             bg=PANEL, fg=TEXT).pack(side="left", padx=20)
    count_lbl = tk.Label(hdr, text=f"{len(data)} entries", font=FONT_TINY,
                          bg=PANEL, fg=SUBTEXT)
    count_lbl.pack(side="right", padx=20)

    # search
    sf = tk.Frame(win, bg=BG, pady=8, padx=16)
    sf.pack(fill="x")
    tk.Label(sf, text="🔍", bg=BG, fg=SUBTEXT, font=("Segoe UI", 13)).pack(side="left")
    sv = tk.StringVar()
    se = tk.Entry(sf, textvariable=sv, bg=ENTRY_BG, fg=ENTRY_FG,
                  insertbackground=CURSOR, font=FONT_ENTRY,
                  relief="flat", bd=6, highlightthickness=0)
    se.pack(side="left", fill="x", expand=True, padx=6)

    # treeview
    cols = ("Website", "Email / Username", "Password")
    sty = ttk.Style()
    sty.theme_use("default")
    sty.configure("Vault.Treeview",
                  background=PANEL, foreground=TEXT,
                  fieldbackground=PANEL, font=FONT_ENTRY,
                  rowheight=34, borderwidth=0)
    sty.configure("Vault.Treeview.Heading",
                  background=ACCENT, foreground="white",
                  font=FONT_BTN, relief="flat")
    sty.map("Vault.Treeview",
            background=[("selected", ACCENT)],
            foreground=[("selected", "white")])

    tf = tk.Frame(win, bg=BG)
    tf.pack(fill="both", expand=True, padx=16, pady=(0, 8))

    tree = ttk.Treeview(tf, columns=cols, show="headings", style="Vault.Treeview")
    tree.heading("Website",          text="🌐  Website")
    tree.heading("Email / Username", text="✉  Email / Username")
    tree.heading("Password",         text="🔒  Password")
    tree.column("Website",          width=160)
    tree.column("Email / Username", width=220)
    tree.column("Password",         width=180)

    sb = ttk.Scrollbar(tf, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=sb.set)
    tree.pack(side="left", fill="both", expand=True)
    sb.pack(side="right", fill="y")

    def populate(filter_text=""):
        tree.delete(*tree.get_children())
        for site, vals in data.items():
            if filter_text.lower() in site.lower() \
                    or filter_text.lower() in vals["email"].lower():
                pw_masked = "•" * min(len(vals["password"]), 14)
                tree.insert("", "end",
                             values=(site, vals["email"], pw_masked),
                             tags=(vals["password"],))

    populate()
    sv.trace_add("write", lambda *_: populate(sv.get()))

    # actions
    af = tk.Frame(win, bg=BG, pady=8)
    af.pack(fill="x", padx=16)

    def copy_password():
        sel = tree.selection()
        if not sel:
            return
        site = tree.item(sel[0])["values"][0]
        pyperclip.copy(data[site]["password"])
        toast(f"Password for '{site}' copied!", SUCCESS)

    def delete_entry():
        sel = tree.selection()
        if not sel:
            return
        site = tree.item(sel[0])["values"][0]
        if messagebox.askyesno("Delete", f"Delete entry for '{site}'?", parent=win):
            del data[site]
            save_data(data)
            count_lbl.config(text=f"{len(data)} entries")
            populate(sv.get())

    styled_button(af, "📋  Copy Password", copy_password,
                  bg="#1e3a5f").pack(side="left", padx=(0, 8))
    styled_button(af, "🗑  Delete Entry", delete_entry,
                  bg="#3f1515").pack(side="left")


# ─────────────────────────── TOAST ───────────────────────────
def toast(msg, color=SUCCESS):
    t = tk.Toplevel(window)
    t.overrideredirect(True)
    t.attributes("-topmost", True)
    t.attributes("-alpha", 0.93)
    t.config(bg=color)
    wx = window.winfo_x() + window.winfo_width() // 2
    wy = window.winfo_y() + window.winfo_height() - 56
    t.geometry(f"+{wx - 190}+{wy}")
    tk.Label(t, text=msg, bg=color, fg="white",
             font=FONT_BTN, padx=20, pady=10).pack()
    t.after(2400, t.destroy)


# ─────────────────────────── LOGIC ───────────────────────────
def password_generator():
    letters = list("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ")
    numbers = list("0123456789")
    symbols = list("!#$%&()*+@^~")
    pw = (
        [random.choice(letters) for _ in range(random.randint(8, 10))]
      + [random.choice(numbers) for _ in range(random.randint(2, 4))]
      + [random.choice(symbols) for _ in range(random.randint(2, 4))]
    )
    random.shuffle(pw)
    generated = "".join(pw)
    password_entry.delete(0, tk.END)
    password_entry.insert(0, generated)
    pyperclip.copy(generated)
    toast("Password generated & copied!", SUCCESS)


def toggle_password():
    if password_entry.cget("show") == "•":
        password_entry.config(show="")
        eye_btn.config(text="🙈")
    else:
        password_entry.config(show="•")
        eye_btn.config(text="👁")


def add_entry():
    site = website_entry.get().strip()
    pw   = password_entry.get().strip()
    em   = email_entry.get().strip()
    if not site or not pw or not em:
        toast("Please fill all fields!", DANGER)
        return
    if not messagebox.askokcancel(
            "Confirm Save",
            f"Save credentials for '{site}'?\n\nEmail:    {em}\nPassword: {pw}",
            parent=window):
        return
    data = load_data()
    data[site] = {"email": em, "password": pw}
    save_data(data)
    website_entry.delete(0, tk.END)
    password_entry.delete(0, tk.END)
    toast(f"'{site}' saved to vault!", SUCCESS)


def find_passwords():
    site = website_entry.get().strip()
    if not site:
        toast("Enter a website to search!", DANGER)
        return
    data = load_data()
    if site in data:
        em = data[site]["email"]
        pw = data[site]["password"]
        pyperclip.copy(pw)
        messagebox.showinfo("Found!",
                            f"🌐  Website : {site}\n"
                            f"✉   Email   : {em}\n"
                            f"🔑  Password: {pw}\n\n"
                            "Password copied to clipboard!",
                            parent=window)
    else:
        toast(f"No entry found for '{site}'", DANGER)


# ─────────────────────────── MAIN WINDOW ─────────────────────
window = tk.Tk()
window.title("Vault — Password Manager")
window.resizable(False, False)
window.config(bg=BG)

# ── Header bar ──────────────────────────────────────────────
header_bar = tk.Frame(window, bg=PANEL, pady=0)
header_bar.pack(fill="x")

logo_inner = tk.Frame(header_bar, bg=PANEL, pady=16, padx=24)
logo_inner.pack(side="left")

try:
    raw_logo = tk.PhotoImage(
        file=os.path.join(os.path.dirname(__file__), "logo.png"))
    scale = max(1, raw_logo.width() // 48)
    logo_img = raw_logo.subsample(scale, scale)
    tk.Label(logo_inner, image=logo_img, bg=PANEL).pack(side="left", padx=(0, 12))
except Exception:
    logo_img = None

text_block = tk.Frame(logo_inner, bg=PANEL)
text_block.pack(side="left")
tk.Label(text_block, text="Vault", font=FONT_HEAD, bg=PANEL, fg=TEXT).pack(anchor="w")
tk.Label(text_block, text="Secure Password Manager",
         font=FONT_SUB, bg=PANEL, fg=SUBTEXT).pack(anchor="w")

styled_button(header_bar, "🔐  Open Vault", show_vault,
              bg=ACCENT, padx=14, pady=8).pack(side="right", padx=20)

# ── Form card ───────────────────────────────────────────────
card = tk.Frame(window, bg=PANEL, padx=32, pady=28,
                highlightbackground=BORDER, highlightthickness=1)
card.pack(padx=28, pady=(18, 8), fill="x")
card.columnconfigure(0, weight=1)

def lbl(text, row):
    tk.Label(card, text=text, font=FONT_LABEL,
             bg=PANEL, fg=SUBTEXT, anchor="w").grid(
        row=row, column=0, sticky="w", pady=(10, 2), columnspan=3)

# Website
lbl("🌐  Website", 0)
wf, website_entry = styled_entry(card, width=28)
wf.grid(row=1, column=0, columnspan=2, sticky="ew")
styled_button(card, "🔍  Search", find_passwords,
              bg="#1e3a5f", padx=12, pady=9).grid(
    row=1, column=2, sticky="ew", padx=(8, 0))

# Email
lbl("✉  Email / Username", 2)
ef, email_entry = styled_entry(card, width=38)
ef.grid(row=3, column=0, columnspan=3, sticky="ew")
email_entry.insert(0, "rishabh@gmail.com")

# Password
lbl("🔑  Password", 4)
pf, password_entry = styled_entry(card, width=22, show="•")
pf.grid(row=5, column=0, sticky="ew")

eye_btn = tk.Button(card, text="👁", bg=ENTRY_BG, fg=SUBTEXT,
                    relief="flat", bd=0, cursor="hand2",
                    font=("Segoe UI", 13), command=toggle_password,
                    activebackground=ENTRY_BG, activeforeground=TEXT)
eye_btn.grid(row=5, column=1, padx=(6, 0))

styled_button(card, "✨ Generate", password_generator,
              bg="#1a3a2a", padx=10, pady=9).grid(
    row=5, column=2, sticky="ew", padx=(8, 0))

# ── Add button ───────────────────────────────────────────────
add_frame = tk.Frame(window, bg=BG)
add_frame.pack(fill="x", padx=28, pady=(4, 6))
styled_button(add_frame, "＋  Add to Vault", add_entry,
              padx=0, pady=13).pack(fill="x")

# ── Footer ───────────────────────────────────────────────────
tk.Label(window, text="Your passwords are stored locally on this device.",
         font=FONT_TINY, bg=BG, fg=SUBTEXT).pack(pady=(0, 16))

website_entry.focus()
window.mainloop()
