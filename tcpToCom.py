import serial
import socket
import sys
import threading
import argparse
import tkinter as tk
from tkinter import ttk, messagebox
import serial.tools.list_ports

class SerialTCPForm:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Serial to TCP Forwarder")
        self.root.geometry("300x300")
      
        # COM Port
        ttk.Label(self.root, text="COM Port:").pack(pady=5)
        self.com_ports = [port.device for port in serial.tools.list_ports.comports()]
        self.com_var = tk.StringVar()
        self.com_dropdown = ttk.Combobox(self.root, textvariable=self.com_var, values=self.com_ports)
        if self.com_ports:
            self.com_dropdown.set(self.com_ports[0])
        else:
            self.com_dropdown.set("No ports available")
        self.com_dropdown.pack()
      
        # Baud Rate
        ttk.Label(self.root, text="Baud Rate:").pack(pady=5)
        self.baud_rates = ['1200', '2400', '4800', '9600', '19200', '38400', '57600', '115200']
        self.baud_var = tk.StringVar()
        self.baud_dropdown = ttk.Combobox(self.root, textvariable=self.baud_var, values=self.baud_rates)
        self.baud_dropdown.set('9600')
        self.baud_dropdown.pack()
      
        # TCP Port
        ttk.Label(self.root, text="TCP Port:").pack(pady=5)
        self.port_entry = ttk.Entry(self.root)
        self.port_entry.insert(0, "8000")
        self.port_entry.pack()
      
        # Start Button
        ttk.Button(self.root, text="Start Forwarding", command=self.start_forwarding).pack(pady=20)
      
    def start_forwarding(self):
        com = self.com_var.get()
        try:
            baud = int(self.baud_var.get())
            port = int(self.port_entry.get())
        except ValueError:
            messagebox.showerror("Error", "Baud rate and port must be numbers")
            return
          
        self.root.withdraw()  # Hide the window
        self.start_server(com, baud, port)
      
    def start_server(self, com, baud, port):
        try:
            ser = serial.Serial(com, baud, timeout=1)
        except serial.SerialException as e:
            messagebox.showerror("Error", f"Error opening serial port: {e}")
            self.root.quit()
            return

        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            server.bind(('0.0.0.0', port))
            server.listen(1)
            print(f"Listening on port {port}")

            while True:
                conn, addr = server.accept()
                print(f"Connected by {addr}")

                t1 = threading.Thread(target=serial_to_tcp, args=(ser, conn))
                t2 = threading.Thread(target=tcp_to_serial, args=(conn, ser))
              
                t1.daemon = True
                t2.daemon = True
              
                t1.start()
                t2.start()
        except Exception as e:
            messagebox.showerror("Error", f"Server error: {e}")
            self.root.quit()

def serial_to_tcp(ser, conn):
    try:
        while True:
            data = ser.read(1024)
            if data:
                conn.send(data)
    except:
        pass

def tcp_to_serial(conn, ser):
    try:
        while True:
            data = conn.recv(1024)
            if data:
                ser.write(data)
    except:
        pass

def main():
    app = SerialTCPForm()
    app.root.mainloop()

if __name__ == '__main__':
    main()