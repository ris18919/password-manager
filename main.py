from tkinter import *
from tkinter import messagebox
import random
import pyperclip


# ---------------------------- PASSWORD GENERATOR ------------------------------- #
def password_generator():
    letters = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']
    numbers = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
    symbols = ['!', '#', '$', '%', '&', '(', ')', '*', '+']

    password_letter=[random.choice(letters) for _ in range(random.randint(8,10))]
    password_number=[random.choice(numbers) for _ in range(random.randint(2,4))]
    password_symbols=[random.choice(symbols) for _ in range(random.randint(2,4))]

    password_list=password_letter+password_symbols+password_number
    random.shuffle(password_list)
    password_generate="".join(password_list)
    password_entry.insert(0,password_generate)
    pyperclip.copy(password_generate)


# ---------------------------- SAVE PASSWORD ------------------------------- #
def add_entry():
    website_get=website_entry.get()
    password_get=password_entry.get()
    email_get=email.get()
    if len(website_get)==0 or len(password_get)==0 or len(email_get)==0:
        messagebox.showinfo(title="Oops",message="do not leave any field empty")
    else:
        is_ok=messagebox.askokcancel(message=f"These are the details entered: \nEmail:{email}"f"\npassword: {password_entry} \nIs it ok to save?")
        if is_ok:
                website_entry.delete(0,END)
                password_entry.delete(0,END)


# ---------------------------- UI SETUP ------------------------------- #

window=Tk()
window.title("Password Manager")
window.config(padx=20,pady=20)
canvas=Canvas(width=200,height=200,highlightthickness=0)
lock_image=PhotoImage(file="logo.png")
canvas.create_image(100,100,image=lock_image)
canvas.grid(column=1,row=0)

#label
website=Label(text="Website:")
website.grid(row=1,column=0)
username=Label(text="Email/Username:")
username.grid(row=2,column=0)
password=Label(text="Password:")
password.grid(row=3,column=0)

#entries
website_entry=Entry(width=35)
website_entry.grid(row=1,column=1,columnspan=1)
website_entry.focus()
email=Entry(width=35)
email.grid(row=2,column=1,columnspan=1)
email.insert(0,"rishabh@gmail.com")
password_entry=Entry(width=35)
password_entry.grid(row=3,column=1)

#button
generate_password=Button(text="Generate Password",command=password_generator)
generate_password.grid(row=3,column=2)
add=Button(text="Add",width=45,command=add_entry)
add.grid(row=4,column=1,columnspan=2)

window.mainloop()