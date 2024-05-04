import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from statsmodels.tsa.arima.model import ARIMA
import pymongo
import customtkinter

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

def update_bar_plot(frame):
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

def update_line_plot(frame):
    plt.clf()
    plt.plot(df.index[:len(df)+frame], df['demand'][:len(df)+frame], label='Actual Demand', marker='o')
    plt.plot(forecast_dates[:frame], predictions_with_noise[:frame], label='Forecasted Demand', marker='o')
    plt.title('Demand Forecasting with ARIMA')
    plt.xlabel('Date')
    plt.ylabel('Demand')
    plt.legend()
    plt.grid(True)
    plt.show()

def start_forecasting(product_name, demand, forecast_steps, screen_width, screen_height):
    app.withdraw()
    data = {'date': pd.date_range(start='2023-01-01', end='2023-12-31', freq='M'), 'demand': demand}
    global df
    df = pd.DataFrame(data)
    df.set_index('date', inplace=True)
    order = (2, 1, 1)
    global predictions_with_noise
    predictions = arima_model(df['demand'], order, forecast_steps)
    np.random.seed(0)
    noise = np.random.normal(loc=0, scale=10, size=len(predictions))
    predictions_with_noise = predictions + noise
    global forecast_dates
    forecast_dates = df.index[-1] + pd.DateOffset(months=1) * np.arange(1, forecast_steps + 1)
    global fig, ax
    fig, ax = plt.subplots(figsize=(10, 6))
    ani = FuncAnimation(fig, update_bar_plot, frames=forecast_steps + 1, blit=True, repeat=False)
    ax.set_xlabel('Date')
    ax.set_ylabel('Demand')
    graph_data_path = f"forecast_plot_{product_name}.png"
    plt.savefig(graph_data_path)
    plt.show()
    store_demand_forecast_data(product_name, demand, forecast_steps, graph_data_path)

def store_demand_forecast_data(product_name, demand, forecast_steps, graph_data_path):
    try:
        client = pymongo.MongoClient("mongodb://127.0.0.1:27017")
        db = client['MPR']
        collection = db['demand_forecasting']
        document = {
            'product_name': product_name,
            'demand': demand,
            'forecast_steps': forecast_steps,
            'graph_data': graph_data_path
        }
        collection.insert_one(document)
        print("Data stored successfully in MongoDB.")
    except Exception as e:
        print(f"Error occurred while storing data in MongoDB: {e}")

app = customtkinter.CTk()
app.title("DemandWise")
customtkinter.set_appearance_mode("dark")

def adjust_window():
    screen_width = app.winfo_screenwidth()
    screen_height = app.winfo_screenheight()
    app.geometry(f"{screen_width}x{screen_height}+0+0")
    label_width = int(0.09 * screen_width)
    l1 = customtkinter.CTkLabel(app, text="Demand Wise", width=label_width, text_color="#118ab2", font=("Arial", screen_height*0.18))
    l1.pack(pady=(20, 0))
    l2 = customtkinter.CTkLabel(app, text="Your intelligent companion for accurate and insightful demand forecasting.", width=label_width, text_color="#faf9f9", font=("Arial", screen_height*0.025))
    l2.pack(pady=(10, 0))
    b1 = customtkinter.CTkButton(app, text="Get Started", width=0.12 * screen_width, height=0.07 * screen_height, corner_radius=50, command=lambda: start_forecasting_page(screen_width, screen_height))
    b1.pack(pady=(20, 0))

def start_forecasting_page(screen_width, screen_height):
    app.withdraw()
    root = customtkinter.CTk()
    root.title("Demand Forecasting")
    customtkinter.set_appearance_mode("dark")

    def start_forecasting_on_page():
        product_name = product_name_entry.get()
        demand_str = demand_entry.get()
        demand = list(map(int, demand_str.split(',')))
        forecast_steps = int(forecast_steps_entry.get())
        start_forecasting(product_name, demand, forecast_steps, screen_width, screen_height)

    label_width = int(0.4 * screen_height)
    l1 = customtkinter.CTkLabel(root, text="Product Name:", width=label_width, text_color="#118ab2", font=("Arial", screen_height*0.043))
    l1.pack(pady=(20, 0))
    product_name_entry = customtkinter.CTkEntry(root, width=int(0.4 * screen_height))
    product_name_entry.pack(pady=(0, 20))
    l2 = customtkinter.CTkLabel(root, text="Historical demand data (comma-separated):", width=label_width, text_color="#118ab2", font=("Arial", screen_height*0.043))
    l2.pack(pady=(20, 0))
    demand_entry = customtkinter.CTkEntry(root, width=int(0.4 * screen_height))
    demand_entry.pack(pady=(0, 20))
    l3 = customtkinter.CTkLabel(root, text="Forecast steps:", width=label_width, text_color="#118ab2", font=("Arial", screen_height*0.043))
    l3.pack(pady=(20, 0))
    forecast_steps_entry = customtkinter.CTkEntry(root, width=int(0.2 * screen_height))
    forecast_steps_entry.pack(pady=(0, 20))
    b1 = customtkinter.CTkButton(root, text="Start Forecasting", width=0.09 * screen_width, height=0.05 * screen_height, corner_radius=50, command=start_forecasting_on_page)
    b1.pack(pady=(20, 0))
    b2 = customtkinter.CTkButton(root, text="Show Line Graph", width=0.09 * screen_width, height=0.05 * screen_height, corner_radius=50, command=start_line_plot_animation)
    b2.pack(pady=(10, 0))
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root_width = int(0.8 * screen_width)
    root_height = int(0.8 * screen_height)
    root.geometry(f"{root_width}x{root_height}+0+0")
    root.mainloop()

def on_closing():
    app.destroy()
    plt.close('all')

def start_line_plot_animation():
    fig, ax = plt.subplots(figsize=(10, 6))
    ani = FuncAnimation(fig, update_line_plot, frames=len(df), blit=False, repeat=False)
    ax.set_xlabel('Date')
    ax.set_ylabel('Demand')
    plt.show()

def start_line_plot():
    plt.plot(df.index, df['demand'], label='Actual Demand', marker='o')
    plt.plot(forecast_dates, predictions_with_noise, label='Forecasted Demand', marker='o')
    plt.title('Demand Forecasting with ARIMA')
    plt.xlabel('Date')
    plt.ylabel('Demand')
    plt.legend()
    plt.grid(True)
    plt.show()

def start_line_plot_animation():
    fig, ax = plt.subplots(figsize=(10, 6))
    ani = FuncAnimation(fig, update_line_plot, frames=len(df)+1, blit=False, repeat=False)
    ax.set_xlabel('Date')
    ax.set_ylabel('Demand')
    plt.show()

adjust_window()
app.mainloop()



# 120,130,150,170,190,210,220,240,280,290,310,350
# 150,120,130,180,140,190,210,170,160,110,100,140
#