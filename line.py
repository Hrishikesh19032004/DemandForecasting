# Import necessary libraries
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from statsmodels.tsa.arima.model import ARIMA
import pymongo
import customtkinter

# Define ARIMA model function
def arima_model(train_data, order, forecast_steps):
    history = [x for x in train_data]
    predictions = []
    for _ in range(forecast_steps):
        try:
            model = ARIMA(history, order=order)
            model_fit = model.fit()
            yhat = model_fit.forecast()[0]
            predictions.append(yhat)
            history.append(yhat)
        except Exception as e:
            print(f"Error occurred: {e}")
    return predictions

# Define function to update plot
def update_line_plot():
    plt.clf()  # Clear the current figure
    plt.plot(df.index, df['demand'], label='Actual Demand', marker='o')
    plt.plot(forecast_dates, predictions_with_noise, label='Forecasted Demand', marker='o')
    plt.title('Demand Forecasting with ARIMA')
    plt.xlabel('Date')
    plt.ylabel('Demand')
    plt.legend()
    plt.grid(True)
    plt.savefig('line_plot.png')  # Save the plot as an image file
    plt.show()

# Define function to start demand forecasting process
def start_forecasting(product_name, demand, forecast_steps, screen_width, screen_height):
    app.withdraw()  # Hide the main window

    # Sample data
    data = {'date': pd.date_range(start='2023-01-01', end='2023-12-31', freq='M'), 'demand': demand}

    # Create DataFrame
    global df
    df = pd.DataFrame(data)
    df.set_index('date', inplace=True)

    # Forecast for the specified number of steps
    order = (2, 1, 1)  # ARIMA order (p, d, q)
    global predictions_with_noise, forecast_dates
    predictions = arima_model(df['demand'], order, forecast_steps)

    # Generate random noise with the same length as predictions
    np.random.seed(0)  # for reproducibility
    noise = np.random.normal(loc=0, scale=10, size=len(predictions))

    # Add noise to the predictions
    predictions_with_noise = predictions + noise

    # Generate forecast dates
    forecast_dates = df.index[-1] + pd.DateOffset(months=1) * np.arange(1, forecast_steps + 1)

    # Create line plot
    update_line_plot()

    # Store data in MongoDB
    store_demand_forecast_data(product_name, demand, forecast_steps, 'line_plot.png')

# Define function to store demand forecast data
def store_demand_forecast_data(product_name, demand, forecast_steps, graph_data_path):
    try:
        # Connect to MongoDB
        client = pymongo.MongoClient("mongodb://127.0.0.1:27017")
        db = client['Demand']
        collection = db['demand_forecasting']

        # Store demand, forecast steps, and graph data
        document = {
            'product_name': product_name,
            'demand': demand,
            'forecast_steps': forecast_steps,
            'graph_data': graph_data_path  # Path to the saved image file
        }
        collection.insert_one(document)
        print("Data stored successfully in MongoDB.")
    except Exception as e:
        print(f"Error occurred while storing data in MongoDB: {e}")

# Create the main application window
app = customtkinter.CTk()
app.title("DemandWise")
customtkinter.set_appearance_mode("dark")

# Define function to adjust window size and create widgets
def adjust_window():
    screen_width = app.winfo_screenwidth()
    screen_height = app.winfo_screenheight()
    app.geometry(f"{screen_width}x{screen_height}+0+0")

    # Calculate the width of l1 as 40% of the screen width
    label_width = int(0.09 * screen_width)

    # Create the label widget with the calculated width
    l1 = customtkinter.CTkLabel(app, text="Demand Wise", width=label_width, text_color="#118ab2", font=("Arial", screen_height*0.18))
    l1.pack(pady=(20, 0))  # Add vertical padding between the widget and the one above it
    l2 = customtkinter.CTkLabel(app, text="Your intelligent companion for accurate and insightful demand forecasting.", width=label_width, text_color="#faf9f9", font=("Arial", screen_height*0.025))
    l2.pack(pady=(10, 0))  # Add vertical padding between the widget and the one above it
    b1 = customtkinter.CTkButton(app, text="Get Started", width=0.12 * screen_width, height=0.07 * screen_height, corner_radius=50, command=lambda: start_forecasting_page(screen_width, screen_height))
    b1.pack(pady=(20, 0))  # Add vertical padding between the widget and the one above it

# Define function to start the forecasting process page
def start_forecasting_page(screen_width, screen_height):
    app.withdraw()  # Hide the main window

    # Create the forecasting page window
    root = customtkinter.CTk()
    root.title("Forecasting Page")
    root_width = int(0.8 * screen_width)  # Adjusted width
    root_height = int(0.8 * screen_height)  # Adjusted height
    root.geometry(f"{screen_width}x{screen_height}+0+0")
    # Calculate the width of l1 as 40% of the screen width
    label_width = int(0.09 * root_width)

    # Create labels and entry fields
    l1 = customtkinter.CTkLabel(root, text="Product Name:", width=label_width, text_color="#118ab2", font=("Arial", screen_height*0.043))
    l1.pack(pady=(20, 0))  # Add vertical padding between the widget and the one above it
    product_name_entry = customtkinter.CTkEntry(root, width=int(0.4 * screen_height))
    product_name_entry.pack(pady=(0, 20))  # Add vertical padding between the widget and the one below it

    l2 = customtkinter.CTkLabel(root, text="Historical demand data :", width=label_width, text_color="#118ab2", font=("Arial", screen_height*0.043))
    l2.pack(pady=(20, 0))  # Add vertical padding between the widget and the one above it
    demand_entry = customtkinter.CTkEntry(root, width=int(0.4 * screen_height))
    demand_entry.pack(pady=(0, 20))  # Add vertical padding between the widget and the one below it

    l3 = customtkinter.CTkLabel(root, text="Forecast steps:", width=label_width, text_color="#118ab2", font=("Arial", screen_height*0.043))
    l3.pack(pady=(20, 0))  # Add vertical padding between the widget and the one above it
    forecast_steps_entry = customtkinter.CTkEntry(root, width=int(0.2 * screen_height))
    forecast_steps_entry.pack(pady=(0, 20))  # Add vertical padding between the widget and the one below it

    # Define function to start forecasting on the page
    def start_forecasting_on_page():
        product_name = product_name_entry.get()
        demand_str = demand_entry.get()
        demand = list(map(int, demand_str.split(',')))
        forecast_steps = int(forecast_steps_entry.get())

        # Start forecasting
        start_forecasting(product_name, demand, forecast_steps, screen_width, screen_height)

    # Create button to start forecasting
    b1 = customtkinter.CTkButton(root, text="Start Forecasting", width=0.09 * root_width, height=0.05 * root_height, corner_radius=50, command=start_forecasting_on_page)
    b1.pack(pady=(20, 0))  # Add vertical padding between the widget and the one above it

    root.mainloop()

# Define function to handle window closing event
def on_closing():
    app.destroy()
    plt.close('all')  # Close all matplotlib windows when the application is closed

# Set up the main application window
app.protocol("WM_DELETE_WINDOW", on_closing)
adjust_window()
app.mainloop()
