import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import mysql.connector
from datetime import datetime

# Connect to MySQL database
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="hotel_booking"
)

# Create a cursor object
cursor = db.cursor()


class MainWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("Hotel Room Booking System")
        self.root.geometry("400x300")
        self.root.configure(bg='#2C3E50')  # Dark background color

        # Create buttons to open different windows with better styling
        ttk.Button(root, text="Home", command=self.open_home).pack(pady=10)
        ttk.Button(root, text="Book a Room", command=self.open_book_room).pack(pady=10)
        ttk.Button(root, text="View Bookings", command=self.open_view_bookings).pack(pady=10)
        ttk.Button(root, text="Manage Rooms", command=self.open_manage_rooms).pack(pady=10)

    def open_home(self):
        HomeWindow()

    def open_book_room(self):
        BookRoomWindow()

    def open_view_bookings(self):
        ViewBookingsWindow()

    def open_manage_rooms(self):
        ManageRoomsWindow()


class HomeWindow:
    def __init__(self):
        self.window = tk.Toplevel()
        self.window.title("Home")
        self.window.geometry("400x300")
        self.window.configure(bg='#34495E')
        self.window.iconbitmap(r"hotel_poster_holiday_icon_188534.ico")
        tk.Label(self.window, text="Welcome to Hotel Booking System!", font=("Arial", 16), bg='#34495E', fg='white').pack(pady=20)


class BookRoomWindow:
    def __init__(self):
        self.window = tk.Toplevel()
        self.window.title("Book a Room")
        self.window.geometry("400x400")
        self.window.configure(bg='#34495E')
        self.window.iconbitmap(r"hotel_poster_holiday_icon_188534.ico")

        # Customer information fields with improved layout
        ttk.Label(self.window, text="Full Name:").grid(row=0, column=0, padx=10, pady=10, sticky='e')
        self.name_entry = ttk.Entry(self.window)
        self.name_entry.grid(row=0, column=1, padx=10, pady=10)

        ttk.Label(self.window, text="Phone Number:").grid(row=1, column=0, padx=10, pady=10, sticky='e')
        self.phone_entry = ttk.Entry(self.window)
        self.phone_entry.grid(row=1, column=1, padx=10, pady=10)

        ttk.Label(self.window, text="Check-in Date (YYYY-MM-DD):").grid(row=2, column=0, padx=10, pady=10, sticky='e')
        self.checkin_entry = ttk.Entry(self.window)
        self.checkin_entry.grid(row=2, column=1, padx=10, pady=10)

        ttk.Label(self.window, text="Check-out Date (YYYY-MM-DD):").grid(row=3, column=0, padx=10, pady=10, sticky='e')
        self.checkout_entry = ttk.Entry(self.window)
        self.checkout_entry.grid(row=3, column=1, padx=10, pady=10)

        ttk.Label(self.window, text="Number of Guests:").grid(row=4, column=0, padx=10, pady=10, sticky='e')
        self.guests_entry = ttk.Entry(self.window)
        self.guests_entry.grid(row=4, column=1, padx=10, pady=10)

        ttk.Label(self.window, text="Room Type:").grid(row=5, column=0, padx=10, pady=10, sticky='e')
        self.room_var = tk.StringVar()
        room_dropdown = ttk.Combobox(self.window, textvariable=self.room_var)
        room_dropdown['values'] = ('Single', 'Double', 'Suite')
        room_dropdown.grid(row=5, column=1, padx=10, pady=5)

        # Booking confirmation button
        ttk.Button(self.window, text="Book Now", command=self.book_room).grid(row=6, columnspan=2, pady=20)

    def book_room(self):
        name = self.name_entry.get()
        phone = self.phone_entry.get()
        checkin = self.checkin_entry.get()
        checkout = self.checkout_entry.get()
        guests = int(self.guests_entry.get())

        room_prices = {'Single': 100.0, 'Double': 150.0, 'Suite': 200.0}

        try:
            checkin_date = datetime.strptime(checkin, "%Y-%m-%d")
            checkout_date = datetime.strptime(checkout, "%Y-%m-%d")
            total_nights = (checkout_date - checkin_date).days

            if total_nights <= 0:
                messagebox.showerror("Error", "Check-out date must be after Check-in date.")
                return

            room_type = self.room_var.get()
            total_cost = room_prices[room_type] * total_nights

            summary = f"Booking Summary:\nName: {name}\nPhone: {phone}\nCheck-in: {checkin}\nCheck-out: {checkout}\nGuests: {guests}\nRoom Type: {room_type}\nTotal Cost: ${total_cost:.2f}"
            messagebox.showinfo("Booking Confirmation", summary)

            sql = "INSERT INTO bookings (name, phone, checkin, checkout, guests, room_type, total_cost) VALUES (%s,%s,%s,%s,%s,%s,%s)"
            values = (name, phone, checkin, checkout, guests, room_type, total_cost)
            cursor.execute(sql, values)
            db.commit()

        except Exception as e:
            messagebox.showerror("Error", str(e))


class ViewBookingsWindow:
    def __init__(self):
        self.window = tk.Toplevel()
        self.window.title("View Bookings")
        self.window.geometry("600x400")
        self.window.configure(bg='#34495E')
        self.window.iconbitmap(r"hotel_poster_holiday_icon_188534.ico")

        # Search bar for filtering by name
        ttk.Label(self.window, text="Search by Name:").pack(pady=10)
        self.search_entry = ttk.Entry(self.window)
        self.search_entry.pack(pady=5)

        ttk.Button(self.window, text="Search", command=self.search_bookings).pack(pady=10)

        # Display bookings in a treeview with improved layout
        columns = ('Name', 'Phone', 'Check-in', 'Check-out', 'Room Type', 'Total Cost')
        self.bookings_tree = ttk.Treeview(self.window, columns=columns, show='headings')
        for col in columns:
            self.bookings_tree.heading(col, text=col)
            self.bookings_tree.column(col, width=100)

        self.bookings_tree.pack(pady=20, fill='both', expand=True)

        # Load bookings from database
        self.load_bookings()

    def load_bookings(self, name=None):
        # Clear current treeview
        for item in self.bookings_tree.get_children():
            self.bookings_tree.delete(item)

        # Modify the SQL query to filter by name if provided
        if name:
            sql = "SELECT * FROM bookings WHERE name LIKE %s"
            cursor.execute(sql, (f"%{name}%",))
        else:
            sql = "SELECT * FROM bookings"
            cursor.execute(sql)

        results = cursor.fetchall()

        for row in results:
            self.bookings_tree.insert('', 'end', values=(row[1], row[2], row[3], row[4], row[5], row[6]))

    def search_bookings(self):
        # Get the name from the search entry
        search_name = self.search_entry.get()
        self.load_bookings(search_name)  # Reload bookings with the search term


class ManageRoomsWindow:
    def __init__(self):
        self.window = tk.Toplevel()
        self.window.title("Manage Rooms")
        self.window.geometry("400x300")
        self.window.configure(bg='#34495E')
        self.window.iconbitmap(r"hotel_poster_holiday_icon_188534.ico")

        # Add room functionality with improved layout
        ttk.Label(self.window, text="Room Number:").grid(row=0, column=0, padx=10, pady=10, sticky='e')
        self.room_number_entry = tk.Entry(self.window)
        self.room_number_entry.grid(row=0, column=1, padx=10, pady=10)

        ttk.Label(self.window, text="Room Type:").grid(row=1, column=0, padx=10, pady=10, sticky='e')
        self.room_type_entry = tk.Entry(self.window)
        self.room_type_entry.grid(row=1, column=1, padx=10, pady=10)

        ttk.Label(self.window, text="Room Price:").grid(row=2, column=0, padx=10, pady=10, sticky='e')
        self.room_price_entry = tk.Entry(self.window)
        self.room_price_entry.grid(row=2, column=1, padx=10, pady=10)

        ttk.Label(self.window, text="Room Capacity:").grid(row=3, column=0, padx=10, pady=10, sticky='e')
        self.room_capacity_entry = tk.Entry(self.window)
        self.room_capacity_entry.grid(row=3, column=1, padx=10, pady=10)

        # Buttons for adding/updating/deleting rooms
        ttk.Button(self.window, text="Add Room", command=self.add_room).grid(row=4, columnspan=2, pady=20)

    def add_room(self):
        room_number = self.room_number_entry.get()
        room_type = self.room_type_entry.get()
        room_price = float(self.room_price_entry.get())
        room_capacity = int(self.room_capacity_entry.get())

        try:
            sql = "INSERT INTO rooms (room_number, room_type, room_price, room_capacity) VALUES (%s, %s, %s, %s)"
            values = (room_number, room_type, room_price, room_capacity)
            cursor.execute(sql, values)
            db.commit()
            messagebox.showinfo("Success", "Room added successfully!")

            # Clear the entry fields
            self.room_number_entry.delete(0, tk.END)
            self.room_type_entry.delete(0, tk.END)
            self.room_price_entry.delete(0, tk.END)
            self.room_capacity_entry.delete(0, tk.END)

        except Exception as e:
            messagebox.showerror("Error", str(e))


# Create the main window
root = tk.Tk()
root.iconbitmap(r"hotel_poster_holiday_icon_188534.ico")
app = MainWindow(root)
root.mainloop()

# Close the database connection when the application exits
db.close()
