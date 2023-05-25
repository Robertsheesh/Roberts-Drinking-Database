import sqlite3
import tkinter
import customtkinter as ctk
from datetime import datetime

ctk.set_appearance_mode("Dark")  # Modes: "System" (standard), "Dark", "Light"
ctk.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"


def create_database():
    conn = sqlite3.connect("drink_orders.db")
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS orders (id INTEGER PRIMARY KEY, user_id INTEGER, username TEXT UNIQUE, drink TEXT, quantity INTEGER, time TEXT, FOREIGN KEY(user_id) REFERENCES users(id))''')
    c.execute('''CREATE TABLE IF NOT EXISTS inventory (drink TEXT PRIMARY KEY, quantity INTEGER)''')
    c.execute('''CREATE TABLE IF NOT EXISTS users (id INTEGER UNIQUE PRIMARY KEY, username TEXT UNIQUE)''')
    conn.commit()
    conn.close()

def add_user(username):
    conn = sqlite3.connect("drink_orders.db")
    c = conn.cursor()
    try:
        c.execute("INSERT INTO users (username) VALUES (?)", (username,))
        conn.commit()
    except sqlite3.IntegrityError:
        print(f"Username '{username}' already exists.")
    conn.close()

def get_users():
    conn = sqlite3.connect("drink_orders.db")
    c = conn.cursor()
    c.execute("SELECT * FROM users")
    rows = c.fetchall()
    conn.close()
    return rows


def add_order(user_id, drink, quantity):
    # Check if there's enough stock
    inventory = dict(get_inventory())

    if drink not in inventory:
        print("The requested drink is not available in the inventory.")
        return

    if inventory[drink] < quantity:
        print(f"Only {inventory[drink]} available for the requested drink. Updating the order.")
        quantity = inventory[drink]

    if quantity > 0:
        # Update inventory
        update_inventory(drink, quantity)

        # Add order to the orders table
        conn = sqlite3.connect("drink_orders.db")
        c = conn.cursor()
        time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        c.execute("INSERT INTO orders (user_id, drink, quantity, time) VALUES (?, ?, ?, ?)",
                  (user_id, drink, quantity, time))
        conn.commit()
        conn.close()
    else:
        print("Not enough inventory for the requested drink.")



def get_all_orders():
    conn = sqlite3.connect("drink_orders.db")
    c = conn.cursor()
    c.execute('''SELECT orders.id, orders.user_id, users.username, orders.drink, orders.quantity, orders.time
                 FROM orders
                 JOIN users ON orders.user_id = users.id''')
    rows = c.fetchall()
    conn.close()
    return rows

def add_to_inventory(drink, quantity):
    conn = sqlite3.connect("drink_orders.db")
    c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO inventory (drink, quantity) VALUES (?, ?)", (drink, quantity))
    c.execute("UPDATE inventory SET quantity = quantity + ? WHERE drink = ?", (quantity, drink))
    conn.commit()
    conn.close()

def get_inventory():
    conn = sqlite3.connect("drink_orders.db")
    c = conn.cursor()
    c.execute("SELECT * FROM inventory")
    rows = c.fetchall()
    conn.close()
    return rows

def update_inventory(drink, quantity):
    conn = sqlite3.connect("drink_orders.db")
    c = conn.cursor()
    c.execute("UPDATE inventory SET quantity = quantity - ? WHERE drink = ?", (quantity, drink))
    conn.commit()
    conn.close()



class DrinkOrdersApp(ctk.CTk):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.title("Robert's Drinking Database")
        self.geometry("800x600")  # Set window size to 800px wide by 600px tall
        self.resizable(False, False)  # Prevent resizing of the window
        self.create_widgets()

    def create_widgets(self):

        # Robert's Drinking Database
        self.add_order_label = ctk.CTkLabel(self, text="Robert's Drinking Database", font=ctk.CTkFont(size=20, weight="bold"))
        self.add_order_label.place(relx=0.1, rely=0.02)

        # Add User
        self.add_user_label = ctk.CTkLabel(self, text="Add User")
        self.add_user_label.place(relx=0.05, rely=0.1)

        self.add_user_entry = ctk.CTkEntry(self, fg_color="grey")
        self.add_user_entry.place(relx=0.2, rely=0.1)
        self.add_user_entry.insert(0, "Username")
        self.add_user_entry.bind("<FocusIn>", lambda event: self.on_focus_in(event, self.add_user_entry, "Username"))
        self.add_user_entry.bind("<FocusOut>", lambda event: self.on_focus_out(event, self.add_user_entry, "Username"))

        self.add_user_button = ctk.CTkButton(self, text="Add User", command=self.on_add_user_click)
        self.add_user_button.place(relx=0.6, rely=0.1)

        # Add Order
        self.add_order_label = ctk.CTkLabel(self, text="Add Order")
        self.add_order_label.place(relx=0.05, rely=0.2)

        self.add_order_username_entry = ctk.CTkEntry(self, fg_color="grey")
        self.add_order_username_entry.place(relx=0.2, rely=0.2)
        self.add_order_username_entry.insert(0, "Username")
        self.add_order_username_entry.bind("<FocusIn>", lambda event: self.on_focus_in(event, self.add_order_username_entry, "Username"))
        self.add_order_username_entry.bind("<FocusOut>", lambda event: self.on_focus_out(event, self.add_order_username_entry, "Username"))

        #self.add_order_drink_label = tk.Label(self, text="Drink and Quantity:")
        #self.add_order_drink_label.place(relx=0.45, rely=0.2)
        self.add_order_drink_entry = ctk.CTkEntry(self, fg_color="grey")
        self.add_order_drink_entry.place(relx=0.4, rely=0.2)

        self.add_order_drink_entry.insert(0, "Drink and Quantity")
        self.add_order_drink_entry.bind("<FocusIn>", lambda event: self.on_focus_in(event, self.add_order_drink_entry, "Drink and Quantity"))
        self.add_order_drink_entry.bind("<FocusOut>", lambda event: self.on_focus_out(event, self.add_order_drink_entry, "Drink and Quantity"))

        self.add_order_button = ctk.CTkButton(self, text="Add Order", command=self.on_add_order_click)
        self.add_order_button.place(relx=0.6, rely=0.2)

        # Show Inventory
        self.show_inventory_button = ctk.CTkButton(self, text="Show Inventory", command=self.on_show_inventory_click)
        self.show_inventory_button.place(relx=0.8, rely=0.3)

        # Add to Inventory
        self.add_inventory_label = ctk.CTkLabel(self, text="Add to Inventory")
        self.add_inventory_label.place(relx=0.05, rely=0.3)

        self.add_inventory_entry = ctk.CTkEntry(self, fg_color="grey")
        self.add_inventory_entry.place(relx=0.2, rely=0.3)

        self.add_inventory_entry.insert(0, "Drink and Quantity")
        self.add_inventory_entry.bind("<FocusIn>", lambda event: self.on_focus_in(event, self.add_inventory_entry, "Drink and Quantity"))
        self.add_inventory_entry.bind("<FocusOut>", lambda event: self.on_focus_out(event, self.add_inventory_entry, "Drink and Quantity"))

        self.add_inventory_button = ctk.CTkButton(self, text="Add", command=self.on_add_inventory_click)
        self.add_inventory_button.place(relx=0.6, rely=0.3)

        # Show Users
        self.show_users_button = ctk.CTkButton(self, text="Show Users", command=self.on_show_users_click)
        self.show_users_button.place(relx=0.8, rely=0.1)

        # Show Order History
        self.show_order_history_button = ctk.CTkButton(self, text="Show Order History",
                                                   command=self.on_show_order_history_click)
        self.show_order_history_button.place(relx=0.8, rely=0.2)

        # Output Textbox
        self.output_text = ctk.CTkTextbox(self, wrap=ctk.WORD, width=800, height=500)
        self.output_text.place(relx=0, rely=0.45)

        # Appearance Mode
        self.appearance_mode_label = ctk.CTkLabel(self, text="", anchor="w")
        self.appearance_mode_label.place(relx=0.8, rely=0.2)
        self.appearance_mode_optionemenu = ctk.CTkOptionMenu(self,
                                                                       values=["Light", "Dark"],
                                                                       command=self.change_appearance_mode_event)
        self.appearance_mode_optionemenu.place(relx=0.8, rely=0.38)

        self.appearance_mode_optionemenu.set("Dark")

    def on_focus_in(self, event, entry_widget, placeholder_text):
        if entry_widget.get() == placeholder_text:
            entry_widget.delete(0, ctk.END)
            entry_widget.configure(fg_color="white")

    def on_focus_out(self, event, entry_widget, placeholder_text):
        if not entry_widget.get():
            entry_widget.insert(0, placeholder_text)
            entry_widget.configure(fg_color="grey")

    def on_add_user_click(self):
        username = self.add_user_entry.get()
        add_user(username)
        self.add_user_entry.delete(0, ctk.END)

    def on_add_order_click(self):
        username = self.add_order_username_entry.get()
        drink_and_quantity = self.add_order_drink_entry.get()

        user_id = None
        for user in get_users():
            if user[1] == username:
                user_id = user[0]
                break

        if user_id is None:
            print("User not found. Please add the user before placing an order.")
        else:
            drink, quantity = drink_and_quantity.split()
            add_order(user_id, drink, int(quantity))
            print("Order added!")

        self.add_order_username_entry.delete(0, ctk.END)
        self.add_order_drink_entry.delete(0, ctk.END)

    def on_show_inventory_click(self):
        inventory = get_inventory()
        self.output_text.delete(1.0, ctk.END)
        self.output_text.insert(ctk.END, "Inventory:\n")
        for item in inventory:
            self.output_text.insert(ctk.END, f"{item[0]}: {item[1]}\n")

    def on_add_inventory_click(self):
        drink_and_quantity = self.add_inventory_entry.get()
        drink, quantity = drink_and_quantity.split()
        add_to_inventory(drink, int(quantity))
        self.add_inventory_entry.delete(0, ctk.END)
        self.output_text.delete(1.0, ctk.END)
        self.output_text.insert(ctk.END, f"Added {quantity} of {drink} to inventory\n")

    def on_show_users_click(self):
        users = get_users()
        self.output_text.delete(1.0, ctk.END)
        self.output_text.insert(ctk.END, "Users:\n")
        for user in users:
            self.output_text.insert(ctk.END, f"{user[0]} - {user[1]}\n")

    def on_show_order_history_click(self):
        order_history = get_all_orders()
        self.output_text.delete(1.0, ctk.END)
        self.output_text.insert(ctk.END, "Order History:\n")
        for order in order_history:
            self.output_text.insert(ctk.END,
                                    f"Order ID: {order[0]}, User ID: {order[1]}, Username: {order[2]}, Drink: {order[3]}, Quantity: {order[4]}, Time: {order[5]}\n")

    def change_appearance_mode_event(self, new_appearance_mode: str):
        ctk.set_appearance_mode(new_appearance_mode)

def main():
    app = DrinkOrdersApp()
    app.mainloop()

if __name__ == "__main__":
    create_database()

    # Start the tkinter application
    main()
