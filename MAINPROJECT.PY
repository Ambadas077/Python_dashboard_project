from tkinter import *
from tkinter import messagebox
import pandas as pd
import random
import smtplib
from email.mime.text import MIMEText
from datetime import datetime
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import mean_squared_error
import matplotlib.pyplot as plt
from PIL import Image, ImageTk
import os
USER_DATA_FILE = 'user_data.csv'  
PREDICTIONS_FILE = 'predictions.csv'  

# Load the dataset
df = pd.read_csv('C:/Gold Price Prediction/goldstock1.csv')

# Preprocess the data
df['Date'] = pd.to_datetime(df['Date'])
df['Month'] = df['Date'].dt.month  
# Encode month column
label_encoder = LabelEncoder()
df['Month'] = label_encoder.fit_transform(df['Month'])

# Define the features and target variable
features = ['Month', 'Open', 'High', 'Low', 'Close']
target = 'Close'

X = df[features]
y = df[target]

# Split the data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train the Linear Regression model
model = LinearRegression()
model.fit(X_train, y_train)

# Function to predict gold price based on user inputs
def predict_gold_price(month, open_price, high_price, low_price, close_price):
    try:
        # Convert the month name to integer (1-12)
        month_num = months.index(month) + 1
        # Create a DataFrame for the input data
        input_data = pd.DataFrame([[month_num, open_price, high_price, low_price, close_price]], 
                                  columns=features)
        # Predict the gold price (in INR)
        predicted_price_usd = model.predict(input_data)[0]
        # Assuming exchange rate of 1 USD = 83.52 INR (replace with actual exchange rate)
        exchange_rate = 83.52
        predicted_price_inr = predicted_price_usd * exchange_rate
        # Save prediction
        save_prediction(month, predicted_price_inr)
        return predicted_price_inr
    except ValueError:
        messagebox.showerror("Input Error", "Please enter valid input values")

# Function to save prediction to file
def save_prediction(month, predicted_price_inr):
    now = datetime.now()
    current_date = now.strftime("%Y-%m-%d %H:%M:%S")
    prediction_data = pd.DataFrame({'Date': [current_date], 'Month': [month], 'Predicted_Price_INR': [predicted_price_inr]})
    if os.path.exists(PREDICTIONS_FILE):
        prediction_data.to_csv(PREDICTIONS_FILE, mode='a', header=False, index=False)
    else:
        prediction_data.to_csv(PREDICTIONS_FILE, index=False)

# Function to show saved predictions
import tkinter as tk
from tkinter import messagebox, filedialog

def show_saved_predictions():
    if os.path.exists(PREDICTIONS_FILE):
        predictions_df = pd.read_csv(PREDICTIONS_FILE)
        message = predictions_df.to_string(index=False)
        
        root = tk.Tk()
        root.withdraw()  
        
        # Display message box with options to export predictions
        result = messagebox.askyesno("Saved Predictions", f"{message}\n\nDo you want to export these predictions to a CSV file?")
        
        if result:
            # Ask user to choose file location for export
            file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV Files", "*.csv")])
            if file_path:
                predictions_df.to_csv(file_path, index=False)
                messagebox.showinfo("Export Successful", f"Predictions exported to:\n{file_path}")
            else:
                messagebox.showinfo("Export Cancelled", "Export operation cancelled.")
        else:
            messagebox.showinfo("Saved Predictions", message)
    else:
        messagebox.showinfo("Saved Predictions", "No predictions saved yet.")

# Function to show the first 10 lines of data
def show_data():
    messagebox.showinfo("First 10 lines of Data", df.head(10).to_string())

# Function to show the accuracy and precision
def show_accuracy():
    y_pred = model.predict(X_test)
    accuracy = model.score(X_test, y_test) * 100  
    precision = mean_squared_error(y_test, y_pred)
    
    messagebox.showinfo("Accuracy and MSE", f"Accuracy: {accuracy:.2f}%\nMean Squared Error: {precision:.2f}")

    # Plot accuracy and MSE
    plt.figure(figsize=(8, 6))
    plt.bar(['Accuracy', 'MSE'], [accuracy, precision], color=['purple', 'orange'])
    plt.title('Model Accuracy and Mean Squared Error')
    plt.ylabel('Score')
    plt.ylim(0, 100)   
    plt.show()

# Function to show the graph of predicted vs actual prices over time
import matplotlib.pyplot as plt
import mplcursors

def show_graph():
    plt.figure(figsize=(12, 8))
    
    # Plot actual and predicted prices
    plt.subplot(2, 1, 1)
    actual_plot, = plt.plot(df['Date'], df['Close'], label='Actual Prices', marker='o', markersize=5, color='blue')
    predicted_plot, = plt.plot(df['Date'], model.predict(X), label='Predicted Prices', linestyle='--', marker='x', markersize=5, color='red')
    plt.xlabel("Date")
    plt.ylabel("Gold Prices (INR)")
    plt.title("Actual vs Predicted Prices Over Time")
    plt.legend()
    plt.grid(True)
    plt.xticks(rotation=45)
    
    # Add cursors for interaction
    mplcursors.cursor(actual_plot, hover=True)
    mplcursors.cursor(predicted_plot, hover=True)
    
    residuals = df['Close'] - model.predict(X)
    plt.subplot(2, 1, 2)
    residuals_plot, = plt.plot(df['Date'], residuals, label='Residuals', marker='o', color='orange', markersize=5)
    plt.axhline(y=0, color='gray', linestyle='--', linewidth=1)
    plt.xlabel("Date")
    plt.ylabel("Residuals (INR)")
    plt.title("Residuals Plot (Actual - Predicted)")
    plt.grid(True)
    plt.xticks(rotation=45)
    
    # Add cursor for residuals
    mplcursors.cursor(residuals_plot, hover=True)
    
    plt.tight_layout()
    plt.show()

# Function to plot historical prices for a selected month
import mplcursors

def show_historical_prices(month):
    selected_month = months.index(month) + 1
    selected_month_prices = df[df['Month'] == selected_month]
    
    plt.figure(figsize=(10, 5))
    plot_line, = plt.plot(selected_month_prices['Date'], selected_month_prices['Close'], marker='o', linestyle='-')
    plt.xlabel("Date")
    plt.ylabel("Gold Prices (INR)")
    plt.title(f"Historical Gold Prices for {month}")
    plt.xticks(rotation=45)
    plt.grid(True)
    
    # Add cursor for interaction
    cursor = mplcursors.cursor(plot_line, hover=True)
    
    # Customize the cursor to show the date and close price
    @cursor.connect("add")
    def on_add(sel):
        sel.annotation.set(text=f"Date: {selected_month_prices['Date'].iloc[sel.index]}\nClose: {selected_month_prices['Close'].iloc[sel.index]:.2f} INR")
    
    plt.show()

# Function to predict and show the result
def show_result():
    month = month_var.get()
    open_price = float(open_entry.get())
    high_price = float(high_entry.get())
    low_price = float(low_entry.get())
    close_price = float(close_entry.get())
    predicted_price_inr = predict_gold_price(month, open_price, high_price, low_price, close_price)
    if predicted_price_inr is not None:
        messagebox.showinfo("Prediction Result", f"Predicted gold price (INR): {predicted_price_inr:.2f}")

# Function to handle login button click
def login():
    username = username_entry.get()
    password = password_entry.get()
    if os.path.exists(USER_DATA_FILE):
        user_data = pd.read_csv(USER_DATA_FILE)
        if username in user_data['Username'].values:
            stored_password = user_data.loc[user_data['Username'] == username, 'Password'].values[0]
            if password == stored_password:
                messagebox.showinfo("Login Successful", "Welcome to Gold Price Prediction!")
                root_login.destroy()  
                show_main_interface()
                return
            else:
                messagebox.showerror("Login Failed", "Invalid password")
        else:
            messagebox.showerror("Login Failed", "Username not found")
    else:
        messagebox.showerror("Error", "No user data available")

# Function to display the main interface after successful login
def show_main_interface():
    # Create the main Tkinter window
    root = Tk()
    root.title("GOLD PRICE PREDICTION")
    root.geometry("1000x1000")

    # Add background image (assuming it's a valid path)
    try:
        bg_image = Image.open("C:/Gold Price Prediction/goldimage8.jpg")
        bg_image = bg_image.resize((1600, 1000))
        bg_photo = ImageTk.PhotoImage(bg_image)
        bg_label = Label(root, image=bg_photo)
        bg_label.place(x=0, y=0, relwidth=1, relheight=1)
    except FileNotFoundError:
        messagebox.showerror("Image Error", "Image file not found. Please check the path.")

    # Add input labels and entries for gold price prediction
    input_frame = Frame(root, bg="black")
    input_frame.place(relx=0.5, rely=0.3, anchor=CENTER)

    Label(input_frame, text="Select the month:", bg="black", fg="white").grid(row=0, column=0, padx=10, pady=10, sticky=E)
    global month_var
    month_var = StringVar(root)
    month_var.set(months[0])  
    month_menu = OptionMenu(input_frame, month_var, *months)
    month_menu.grid(row=0, column=1, padx=10, pady=10)

    Label(input_frame, text="Enter the open price:", bg="black", fg="white").grid(row=1, column=0, padx=10, pady=10, sticky=E)
    global open_entry
    open_entry = Entry(input_frame)
    open_entry.grid(row=1, column=1, padx=10, pady=10)

    Label(input_frame, text="Enter the high price:", bg="black", fg="white").grid(row=2, column=0, padx=10, pady=10, sticky=E)
    global high_entry
    high_entry = Entry(input_frame)
    high_entry.grid(row=2, column=1, padx=10, pady=10)

    Label(input_frame, text="Enter the low price:", bg="black", fg="white").grid(row=3, column=0, padx=10, pady=10, sticky=E)
    global low_entry
    low_entry = Entry(input_frame)
    low_entry.grid(row=3, column=1, padx=10, pady=10)

    Label(input_frame, text="Enter the close price:", bg="black", fg="white").grid(row=4, column=0, padx=10, pady=10, sticky=E)
    global close_entry
    close_entry = Entry(input_frame)
    close_entry.grid(row=4, column=1, padx=10, pady=10)

    Button(input_frame, text="Predict Gold Price", command=show_result, bg="blue", fg="white").grid(row=5, columnspan=2, padx=10, pady=10)

    # Add button frame for additional functionalities
    button_frame = Frame(root, bg="black")
    button_frame.place(relx=0.5, rely=0.7, anchor=CENTER)

    Button(button_frame, text="Show Accuracy and Precision", command=show_accuracy, bg="orange", fg="white").grid(row=0, column=0, padx=10, pady=10)
    Button(button_frame, text="Show Graph", command=show_graph, bg="purple", fg="white").grid(row=0, column=1, padx=10, pady=10)
    Button(button_frame, text="Show Saved Predictions", command=show_saved_predictions, bg="pink", fg="black").grid(row=1, column=0, columnspan=2, padx=10, pady=10)
    Button(button_frame, text="Show Historical Prices", command=show_historical_prices_interface, bg="green", fg="white").grid(row=2, column=0, columnspan=2, padx=10, pady=10)

    # Run the main event loop for the main interface
    root.mainloop()

# Function to create the interface for selecting month for historical prices
def show_historical_prices_interface():
    historical_prices_window = Toplevel()
    historical_prices_window.title("Select Month for Historical Prices")
    historical_prices_window.geometry("300x150")

    Label(historical_prices_window, text="Select the month:", bg="black", fg="white").pack(pady=5)
    global historical_month_var
    historical_month_var = StringVar()
    historical_month_var.set(months[0])  
    month_menu = OptionMenu(historical_prices_window, historical_month_var, *months)
    month_menu.pack(pady=5)

    Button(historical_prices_window, text="Show Historical Prices", command=show_historical_prices_window, bg="blue", fg="white").pack(pady=10)

# Function to display historical prices based on selected month
def show_historical_prices_window():
    selected_month = historical_month_var.get()
    show_historical_prices(selected_month)

# Function definitions for registration and password recovery
def register():
    def save_registration():
        new_username = new_username_entry.get()
        new_password = new_password_entry.get()
        confirm_password = confirm_password_entry.get()

        if new_password != confirm_password:
            messagebox.showerror("Registration Error", "Passwords do not match")
            return

        if os.path.exists(USER_DATA_FILE):
            user_data = pd.read_csv(USER_DATA_FILE)
            if new_username in user_data['Username'].values:
                messagebox.showerror("Registration Error", "Username already exists")
                return

        else:
            user_data = pd.DataFrame(columns=['Username', 'Password'])

        new_user = pd.DataFrame({'Username': [new_username], 'Password': [new_password]})
        user_data = pd.concat([user_data, new_user], ignore_index=True)
        user_data.to_csv(USER_DATA_FILE, index=False)
        messagebox.showinfo("Registration", "Registration successful")

    register_window = Toplevel(root_login)
    register_window.title("Register")
    register_window.geometry("300x250")

    Label(register_window, text="New Username:").pack(pady=5)
    new_username_entry = Entry(register_window)
    new_username_entry.pack(pady=5)

    Label(register_window, text="New Password:").pack(pady=5)
    new_password_entry = Entry(register_window, show="*")
    new_password_entry.pack(pady=5)

    Label(register_window, text="Confirm Password:").pack(pady=5)
    confirm_password_entry = Entry(register_window, show="*")
    confirm_password_entry.pack(pady=5)

    show_password_var = BooleanVar()
    show_password_check = Checkbutton(register_window, text="Show Password", variable=show_password_var, command=lambda: new_password_entry.config(show='' if show_password_var.get() else '*'))
    show_password_check.pack(pady=5)

    Button(register_window, text="Register", command=save_registration).pack(pady=10)

def forgot_credentials():
    forgot_credentials_window = Toplevel(root_login)
    forgot_credentials_window.title("Forgot Username or Password")
    forgot_credentials_window.geometry("300x150")

    Label(forgot_credentials_window, text="Enter your email:").pack(pady=5)
    email_entry = Entry(forgot_credentials_window)
    email_entry.pack(pady=5)

    Button(forgot_credentials_window, text="Send Recovery Email", command=send_recovery_email).pack(pady=10)

# Function to send recovery email
def send_recovery_email():
    email = email_entry.get()

    if not os.path.exists(USER_DATA_FILE):
        messagebox.showerror("Error", "No user data available")
        return

    user_data = pd.read_csv(USER_DATA_FILE)
    if email in user_data['Username'].values:
        new_password = ''.join(random.choices('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=8))
        user_data.loc[user_data['Username'] == email, 'Password'] = new_password
        user_data.to_csv(USER_DATA_FILE, index=False)

        try:
            smtp_server = "smtp.example.com"  
            smtp_port = 587  
            sender_email = "your_email@example.com"  
            sender_password = "your_password"  

            msg = MIMEText(f"Your new temporary password is: {new_password}")
            msg['Subject'] = 'Password Recovery'
            msg['From'] = sender_email
            msg['To'] = email

            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls()
                server.login(sender_email, sender_password)
                server.sendmail(sender_email, email, msg.as_string())

            messagebox.showinfo("Success", f"A recovery email has been sent to {email}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to send email: {str(e)}")
    else:
        messagebox.showerror("Error", "Email not found")

months = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December"
]

root_login = Tk()
root_login.title("Login to Gold Price Prediction")
root_login.geometry("400x250")
root_login.configure(bg="lightblue")  
# Login interface components
login_frame = Frame(root_login, bg="black")
login_frame.pack(pady=20)

Label(login_frame, text="Username:", bg="black", fg="white").grid(row=0, column=0, padx=10, pady=10)
username_entry = Entry(login_frame)
username_entry.grid(row=0, column=1, padx=10, pady=10)

Label(login_frame, text="Password:", bg="black", fg="white").grid(row=1, column=0, padx=10, pady=10)
password_entry = Entry(login_frame, show="*")
password_entry.grid(row=1, column=1, padx=10, pady=10)

show_password_var = BooleanVar()
show_password_check = Checkbutton(login_frame, text="Show Password", variable=show_password_var, command=lambda: password_entry.config(show='' if show_password_var.get() else '*'))
show_password_check.grid(row=2, column=1, padx=10, pady=10, sticky=W)

Button(login_frame, text="Login", command=login, bg="blue", fg="white").grid(row=3, column=0, padx=10, pady=10)
Button(login_frame, text="Register", command=register, bg="green", fg="white").grid(row=3, column=1, padx=10, pady=10)

# Run the main event loop for the login interface
root_login.mainloop()
