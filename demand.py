import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from statsmodels.tsa.arima.model import ARIMA
import customtkinter
import pymongo

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
def update_height_color(frame):
    ax.clear()
    ax.bar(df.index, df['demand'], label='Actual Demand', align='center', width=10)
    forecast_dates = df.index[-1] + pd.DateOffset(months=1) * np.arange(1, frame + 1)
    december_demand = df[df.index.month == 12]['demand'].values[0]
    for i in range(frame):
        if predictions_with_noise[i] < december_demand:
            color = 'red'
        else:
            color = 'green'
        ax.bar(forecast_dates[i], predictions_with_noise[i], label='Forecasted Demand', align='center', width=10, color=color, alpha=0.4)
        ax.text(forecast_dates[i], predictions_with_noise[i], f"{forecast_dates[i].strftime('%b')[:3]}", ha='center', va='bottom')
    ax.set_xticks(df.index.union(forecast_dates))
    ax.set_xticklabels([date.strftime('%b') for date in df.index.union(forecast_dates)])
    ax.set_title('Demand Forecasting with ARIMA')
    ax.set_xlabel('Date')
    ax.set_ylabel('Demand')
    ax.legend()
    return ax,

# Connect to MongoDB and define function to store demand forecast data
def store_demand_forecast_data(demand, forecast_steps, sales, marketing_cost, price, graph_data_path):
    try:
        # Connect to MongoDB
        client = pymongo.MongoClient("mongodb://127.0.0.1:27017")
        db = client['Demand']
        collection = db['demand_forecasting']

        # Store demand, forecast steps, and other data
        document = {
            'demand': demand,
            'forecast_steps': forecast_steps,
            'sales_data': sales,
            'marketing_cost': marketing_cost,
            'price': price,
            'graph_data': graph_data_path  # Assuming you save the plot as an image file
        }
        collection.insert_one(document)
        print("Data stored successfully in MongoDB.")
    except Exception as e:
        print(f"Error occurred while storing data in MongoDB: {e}")

# Define function to start demand forecasting process
def start_forecasting(sales, marketing_cost, price, forecast_steps, screen_width, screen_height):
    app.withdraw()  # Hide the main window

    # Generate date range
    dates = pd.date_range(start='2023-01-01', end='2023-12-31', freq='M')

    # Generate demand using the provided formula
    demand = 0.6 * sales + 0.4 * marketing_cost - 0.3 * price

    # Sample data
    data = {'date': dates, 'demand': demand}

    # Create DataFrame
    global df
    df = pd.DataFrame(data)
    df.set_index('date', inplace=True)

    # Forecast for the specified number of steps
    order = (2, 1, 1)  # ARIMA order (p, d, q)
    global predictions_with_noise
    predictions = arima_model(df['demand'], order, forecast_steps)

    # Generate random noise with the same length as predictions
    np.random.seed(0)  # for reproducibility
    noise = np.random.normal(loc=0, scale=10, size=len(predictions))

    # Add noise to the predictions
    predictions_with_noise = predictions + noise

    # Create a figure and axis
    global fig, ax
    fig, ax = plt.subplots(figsize=(10, 6))

    # Create animation
    ani = FuncAnimation(fig, update_height_color, frames=forecast_steps + 1, blit=True, repeat=False)

    # Set x label and y label
    ax.set_xlabel('Date')
    ax.set_ylabel('Demand')

    plt.show()

    # Store data in MongoDB
    store_demand_forecast_data(demand, forecast_steps, sales, marketing_cost, price, graph_data_path)  # Replace with the actual path to the graph image

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
    l1 = customtkinter.CTkLabel(root, text="Sales Data (comma-separated):", width=label_width, text_color="#118ab2", font=("Arial", screen_height*0.043))
    l1.pack(pady=(20, 0))  # Add vertical padding between the widget and the one above it
    sales_entry = customtkinter.CTkEntry(root, width=int(0.4 * screen_height))
    sales_entry.pack(pady=(0, 20))  # Add vertical padding between the widget and the one below it

    l2 = customtkinter.CTkLabel(root, text="Marketing Cost Data (comma-separated):", width=label_width, text_color="#118ab2", font=("Arial", screen_height*0.043))
    l2.pack(pady=(20, 0))  # Add vertical padding between the widget and the one above it
    marketing_cost_entry = customtkinter.CTkEntry(root, width=int(0.4 * screen_height))
    marketing_cost_entry.pack(pady=(0, 20))  # Add vertical padding between the widget and the one below it

    l3 = customtkinter.CTkLabel(root, text="Price of the Product:", width=label_width, text_color="#118ab2", font=("Arial", screen_height*0.043))
    l3.pack(pady=(20, 0))  # Add vertical padding between the widget and the one above it
    price_entry = customtkinter.CTkEntry(root, width=int(0.4 * screen_height))
    price_entry.pack(pady=(0, 20))  # Add vertical padding between the widget and the one below it

    l4 = customtkinter.CTkLabel(root, text="Forecast Steps:", width=label_width, text_color="#118ab2", font=("Arial", screen_height*0.043))
    l4.pack(pady=(20, 0))  # Add vertical padding between the widget and the one above it
    forecast_steps_entry = customtkinter.CTkEntry(root, width=int(0.2 * screen_height))
    forecast_steps_entry.pack(pady=(0, 20))  # Add vertical padding between the widget and the one below it

    # Define function to start forecasting on the page
    def start_forecasting_on_page():
        sales_str = sales_entry.get()
        sales = list(map(int, sales_str.split(',')))
        marketing_cost_str = marketing_cost_entry.get()
        marketing_cost = list(map(int, marketing_cost_str.split(',')))
        price = int(price_entry.get())
        forecast_steps = int(forecast_steps_entry.get())

        # Start forecasting
        start_forecasting(sales, marketing_cost, price, forecast_steps, screen_width, screen_height)

    # Create button to start forecasting
    b1 = customtkinter.CTkButton(root, text="Start Forecasting", width=0.09 * root_width, height=0.05 * root_height, corner_radius=50, command=start_forecasting_on_page)
    b1.pack(pady=(20, 0))  # Add vertical padding between the widget and the one above it

    root.mainloop()

# Adjust the window size and create the label widget
adjust_window()

# Run the application
app.mainloop()
