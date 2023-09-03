import tkinter as tk
from tkinter import ttk
from tkinter import StringVar
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.ticker import FuncFormatter
import time
import threading
from scipy.interpolate import make_interp_spline
import numpy as np
from datetime import datetime, timezone
import os
import platform
import serial.tools.list_ports
import serial

def list_uart_devices():
    if platform.system() == 'Linux':
        uart_devices = []
        for device in os.listdir('/dev'):
            if device.startswith('ttyUSB') or device.startswith('ttyS'):
                uart_devices.append(f'/dev/{device}')
        return uart_devices
    elif platform.system() == 'Windows':
        uart_devices = []
        for port_info in serial.tools.list_ports.comports():
            uart_devices.append(port_info.device)
        return uart_devices
    else:
        return "Unsupported OS"

# This function converts Unix timestamps to human-readable time strings.
def format_time(x, pos=None):
    try:
        return datetime.fromtimestamp(x).strftime('%H:%M:%S')
    except OSError as e:
        print(f"Error formatting time for timestamp {x}: {e}")
        return "Invalid Time"

def read_distance_from_serial(ser):
    distance = None
    if ser.in_waiting > 0:
        header_byte = ser.read(1)
        if header_byte == b'\xFF':
            data_bytes = ser.read(3)
            checksum = (0xFF + data_bytes[0] + data_bytes[1]) & 0xFF
            if checksum == data_bytes[2]:
                distance = (data_bytes[0] << 8) + data_bytes[1]
            else:
                print("Checksum mismatch")
        else:
            print("Incorrect header")
        ser.flushInput()
    return distance

## Creating CSV log file storing data
def checkFike():
    global file1
    file1 = open("log.csv","a+")
    file1.seek(0)
    if len(file1.readlines())==0:
        file1.write("timeStamp(UTC)"+","+"localTimeStamp"+","+"Distance\n")
        file1.flush()

def WriteToFile(Reading):
    global file1
    timeStamp = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')   ## Getting UTC timeStamp
    LocaltimeStamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')  ## Getting local timeStamp
    file1.write(timeStamp + "," + LocaltimeStamp + "," + str(Reading)+"\n") ## Writing those into a CSV file
    file1.flush()  ## Flushing data into a CSV file

        
class RealTimeGraphApp:
    file1 = None  # Class variable to hold the file object
    
    @staticmethod
    def checkFile():
        RealTimeGraphApp.file1 = open("log.csv", "a+")
        RealTimeGraphApp.file1.seek(0)
        if len(RealTimeGraphApp.file1.readlines()) == 0:
            RealTimeGraphApp.file1.write("timeStamp(UTC),localTimeStamp,Distance\n")
            RealTimeGraphApp.file1.flush()

    @staticmethod
    def WriteToFile(Reading):
        timeStamp = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S.%f')[:-2]
        LocaltimeStamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-2]
        RealTimeGraphApp.file1.write(timeStamp + "," + LocaltimeStamp + "," + str(Reading) + "\n")
        RealTimeGraphApp.file1.flush()
        
    def __init__(self, master):
        # Store the Tkinter root window for future reference
        self.master = master
        # Set the title and initial size of the Tkinter window
        self.master.title("JSN-SR04T Reader")
        self.master.geometry("1000x600")

        # Initialize a variable to control the graph updating loop
        self.is_running = False

        # Create a frame to hold the control widgets (buttons, labels, etc.)
        self.control_frame = tk.Frame(self.master)
        # Pack the control frame at the top of the window, allowing horizontal expansion
        self.control_frame.pack(side=tk.TOP, fill=tk.X)

        ## Serial Device title
        self.label_device = ttk.Label(self.control_frame, text="Select serial device:")
        self.label_device.grid(row=0, column=1, padx=10, pady=5)

        ## Serial Device Drop-Down
        self.combo_device = ttk.Combobox(self.control_frame, values=["None"] + list_uart_devices())
        self.combo_device.grid(row=0, column=2, padx=10, pady=5)
        self.combo_device.current(0)
        self.combo_device.bind('<Button-1>', self.show_device_dropdown)

        ## Baud rate title
        self.label_baud = ttk.Label(self.control_frame, text="Baud rate:")
        self.label_baud.grid(row=1, column=1, padx=10, pady=5)

        ## Baud rate Drop-Down
        self.combo_baud = ttk.Combobox(self.control_frame, values=[4800, 9600, 19200, 38400, 57600, 115200, 250000])
        self.combo_baud.grid(row=1, column=2, padx=10, pady=5)
        self.combo_baud.current(1)

        ## start and stop button
        self.start_button = tk.Button(self.control_frame, text="Start", bg="green", command=self.toggle_run)
        self.start_button.grid(row=0, column=5, padx=20, pady=10)

        ## graph clear button
        self.clear_button = tk.Button(self.control_frame, text="Clear", command=self.clear_graph)
        self.clear_button.grid(row=0, column=6, padx=20, pady=10)

        ## interval selection
        self.label_interval = ttk.Label(self.control_frame, text="Update Interval:")
        self.label_interval.grid(row=0, column=7, padx=10, pady=5)

        ## interval selection Defult value
        self.interval_var = StringVar()
        self.interval_var.set("1s")  # default value

        ## interval selection Drop-Down
        self.combo_interval = ttk.Combobox(self.control_frame, textvariable=self.interval_var, values=["0.5s", "1s", "3s", "5s", "No Interval"])
        self.combo_interval.grid(row=0, column=8, padx=10, pady=5)
        self.combo_interval.current(1)  # default index

        ## logging
        self.logging_var = tk.IntVar()
        self.logging_checkbutton = tk.Checkbutton(self.control_frame, text="Enable Logging", variable=self.logging_var)
        self.logging_checkbutton.grid(row=1, column=7, padx=10, pady=10)
        self.checkFile()  # Initialize the log file using the class method
        
        ## Exit Button
        self.exit_button = tk.Button(self.control_frame, text="Exit", command=self.exit_app)
        self.exit_button.grid(row=0, column=10, padx=20, pady=10)
        
        # Create a new Matplotlib figure to hold the graph
        self.fig = Figure()
        # Adjust the layout to use full horizontal space
        self.fig.subplots_adjust(left=0.05, right=0.95)
        # Create a canvas to embed the Matplotlib figure in the Tkinter window
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.master)
        # Pack the canvas in the Tkinter window, allowing it to expand and fill available space
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)        
        
        # Create a subplot for the graph
        self.ax = self.fig.add_subplot(111)
        # Initialize empty lists to hold x and y data points for the graph
        self.x_data = []
        self.y_data = []
        # Set the x-axis to display time in HH:MM:SS format
        self.ax.xaxis.set_major_formatter(FuncFormatter(format_time))
        self.line, = self.ax.plot(self.x_data, self.y_data)  # creates a line plot using the empty x and y data lists    

        # Set initial x-axis limits to avoid negative timestamps
        current_time = time.time()
        self.ax.set_xlim([current_time, current_time + 60])
        # Create an initial line on the graph, which will be updated in real-time
        # The line object is stored in self.line for future updates
        self.latest_value_text = self.ax.text(0.85, 0.95, '', transform=self.ax.transAxes, color='green')
      
    def show_device_dropdown(self, event):
        self.combo_device['values'] = [""] + list_uart_devices()
        self.combo_device.event_generate('<Down>')
        
    def toggle_run(self):
        if self.is_running:
            self.is_running = False
            self.start_button.config(text="Start", bg="green")
            self.ser.close()
        else:
            selected_device = self.combo_device.get()
            selected_baud = int(self.combo_baud.get())
            self.ser = serial.Serial(selected_device, selected_baud, timeout=1)
            time.sleep(2)

            self.is_running = True
            self.start_button.config(text="Stop", bg="red")
            self.update_thread = threading.Thread(target=self.update_graph)
            self.update_thread.daemon = True
            self.update_thread.start()
    
    def exit_app(self):
        try:
            if self.is_running:
                self.is_running = False
                self.start_button.config(text="Start", bg="green")
                self.ser.close()
        except Exception as e:
            print(f"Error while closing serial connection: {e}")
        finally:
            self.master.destroy()  # Close the Tkinter window

    def clear_graph(self):
        self.x_data.clear()
        self.y_data.clear()
        self.line.set_data(self.x_data, self.y_data)
        self.ax.relim()
        self.ax.autoscale_view()
        self.canvas.draw()
        
    def update_graph(self):
        current_time = None  # Initialize to None
        while self.is_running:
            current_time = time.time()  # Update current_time
            sensor_data = read_distance_from_serial(self.ser)

            if sensor_data is not None:
                self.x_data.append(current_time)
                self.y_data.append(sensor_data)

                if self.logging_var.get() == 1:
                    self.WriteToFile(sensor_data)
                    
                if len(self.x_data) > 30:
                    self.x_data = self.x_data[-30:]
                    self.y_data = self.y_data[-30:]

                if len(self.y_data) > 0:
                    latest_value = self.y_data[-1]
                    self.latest_value_text.set_text(f'Latest Value: {latest_value:.2f} mm')
              
                # Update x-axis limits to fit the latest data
                if len(self.x_data) > 0:
                    self.ax.set_xlim([min(self.x_data), max(self.x_data) + 0.5])
                    
                if len(self.x_data) >= 4:
                    xnew = np.linspace(min(self.x_data), max(self.x_data), 300)
                    spl = make_interp_spline(self.x_data, self.y_data, k=3)
                    ynew = spl(xnew)
                    self.line.set_data(xnew, ynew)
                else:
                    self.line.set_data(self.x_data, self.y_data)

                self.ax.relim()
                self.ax.autoscale_view()

                self.canvas.draw()
                self.canvas.flush_events()
                
            interval_str = self.interval_var.get()
            if interval_str != "No Interval":
                try:
                    interval = float(interval_str.replace("s", ""))
                except ValueError:
                    interval = 1.0  # default to 1 second if input is invalid
                time.sleep(interval)

if __name__ == "__main__":
    root = tk.Tk()
    app = RealTimeGraphApp(root)
    root.mainloop()