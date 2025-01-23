import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np

class Waypoint:
    def __init__(self, name, latitude, longitude):
        self.name = name
        self.latitude = latitude
        self.longitude = longitude

    def __repr__(self):
        return f"{self.name} ({self.latitude}, {self.longitude})"

class Route:
    def __init__(self, origin: Waypoint, destination: Waypoint):
        self.origin = origin
        self.destination = destination
        self.waypoints = []

    def add_waypoint(self, waypoint):
        self.waypoints.append(waypoint)

    def get_coordinates(self):
        coords = [(self.origin.latitude, self.origin.longitude)]
        for wp in self.waypoints:
            coords.append((wp.latitude, wp.longitude))
        coords.append((self.destination.latitude, self.destination.longitude))
        return coords

class PerformanceInit:
    def __init__(self):
        self.cost_index = 0
        self.reserves = 0
        self.zfw = 0
        self.total_fuel = 0
        self.optimum_flight_level = 0
        self.transition_altitude = 0

    def calculate_gross_weight(self):
        return self.zfw + self.total_fuel

class FMS:
    def __init__(self):
        self.route = Route(Waypoint("Unknown", 0, 0), Waypoint("Unknown", 0, 0))
        self.performance = PerformanceInit()

    def program_performance(self, cost_index, reserves, zfw, total_fuel, fl, transition_altitude):
        self.performance.cost_index = cost_index
        self.performance.reserves = reserves
        self.performance.zfw = zfw
        self.performance.total_fuel = total_fuel
        self.performance.optimum_flight_level = fl
        self.performance.transition_altitude = transition_altitude

class FlightApp:
    def __init__(self, master):
        self.master = master
        master.title("Flight Management System")
        master.geometry("400x400")
        master.resizable(False, False)

        # Labels
        self.label_departure = tk.Label(master, text="Aéroport de départ:")
        self.label_departure.grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)

        self.label_arrival = tk.Label(master, text="Aéroport d'arrivée:")
        self.label_arrival.grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)

        self.label_fuel = tk.Label(master, text="Carburant total (tonnes):")
        self.label_fuel.grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)

        self.label_zfw = tk.Label(master, text="Masse sans carburant (tonnes):")
        self.label_zfw.grid(row=3, column=0, padx=5, pady=5, sticky=tk.W)

        # Dropdown for airports
        self.airports = ["CMN (Casablanca)", "MAD (Madrid)", "CDG (Paris)", "JFK (New York)"]
        self.departure_airport = ttk.Combobox(master, values=self.airports, state="readonly")
        self.departure_airport.grid(row=0, column=1, padx=5, pady=5)

        self.arrival_airport = ttk.Combobox(master, values=self.airports, state="readonly")
        self.arrival_airport.grid(row=1, column=1, padx=5, pady=5)

        # Fuel and ZFW entries
        self.fuel_entry = tk.Entry(master)
        self.fuel_entry.grid(row=2, column=1, padx=5, pady=5)

        self.zfw_entry = tk.Entry(master)
        self.zfw_entry.grid(row=3, column=1, padx=5, pady=5)

        # Start flight button
        self.start_button = tk.Button(master, text="Démarrer le vol", command=self.start_flight)
        self.start_button.grid(row=4, column=0, columnspan=2, pady=10)

        # Result area
        self.result_area = tk.Text(master, height=10, width=50, state="disabled", wrap="word")
        self.result_area.grid(row=5, column=0, columnspan=2, padx=5, pady=5)

    def validate_inputs(self):
        """Validates user inputs for fuel and ZFW."""
        try:
            fuel = float(self.fuel_entry.get())
            zfw = float(self.zfw_entry.get())
            if fuel <= 0 or zfw <= 0:
                raise ValueError
            return True
        except ValueError:
            messagebox.showerror("Erreur", "Veuillez entrer des valeurs valides pour le carburant et la masse sans carburant.")
            return False

    def start_flight(self):
        departure = self.departure_airport.get()
        arrival = self.arrival_airport.get()

        if not departure or not arrival:
            messagebox.showerror("Erreur", "Veuillez sélectionner les aéroports de départ et d'arrivée.")
            return

        if not self.validate_inputs():
            return

        fuel = float(self.fuel_entry.get())
        zfw = float(self.zfw_entry.get())

        # Simulate flight preparation
        fms = FMS()
        origin = Waypoint(departure, 34.0, -6.0)  # Remplacez par les coordonnées réelles
        destination = Waypoint(arrival, 36.0, -4.0)  # Remplacez par les coordonnées réelles
        fms.route = Route(origin, destination)
        fms.route.add_waypoint(Waypoint("VOR1", 34.1, -6.1))  # Exemple de waypoint
        fms.route.add_waypoint(Waypoint("VOR2", 35.0, -5.0))  # Exemple de waypoint
        fms.route.add_waypoint(Waypoint("VOR3", 36.0, -4.0))  # Exemple de waypoint
        fms.program_performance(cost_index=30, reserves=2.5, zfw=zfw, total_fuel=fuel, fl=380, transition_altitude=5000)

        # Display results
        gross_weight = fms.performance.calculate_gross_weight()

        self.result_area.config(state="normal")
        self.result_area.delete(1.0, tk.END)
        self.result_area.insert(tk.END, f"Vol simulé avec succès :\n")
        self.result_area.insert(tk.END, f"Départ: {departure}\n")
        self.result_area.insert(tk.END, f"Arrivée: {arrival}\n")
        self.result_area.insert(tk.END, f"Carburant: {fuel:.2f} tonnes\n")
        self.result_area.insert(tk.END, f"ZFW: {zfw:.2f} tonnes\n")
        self.result_area.insert(tk.END, f"Poids brut: {gross_weight:.2f} tonnes\n")
        self.result_area.config(state="disabled")

        # Afficher la route sur un graphique
        self.display_route_on_graph(fms.route)

        # Démarrer l'animation de l'avion
        self.animate_airplane(fms.route)

    def display_route_on_graph(self, route):
        coords = route.get_coordinates()
        latitudes, longitudes = zip(*coords)

        plt.figure()
        plt.plot(longitudes, latitudes, marker='o', label='Waypoints')
        plt.title("Trajectoire de vol")
        plt.xlabel("Longitude")
        plt.ylabel("Latitude")
        plt.grid()
        plt.legend()
        plt.show()

    def animate_airplane(self, route):
        coords = route.get_coordinates()
        latitudes, longitudes = zip(*coords)

        fig, ax = plt.subplots()
        ax.set_xlim(min(longitudes) - 0.1, max(longitudes) + 0.1)
        ax.set_ylim(min(latitudes) - 0.1, max(latitudes) + 0.1)
        ax.set_title("Mouvement de l'avion")
        ax.set_xlabel("Longitude")
        ax.set_ylabel("Latitude")
        ax.grid()

        airplane, = ax.plot([], [], 'ro', markersize=10)  # Avion en rouge
        speed = 0.01  # Vitesse de déplacement
        altitude = 38000  # Altitude initiale

        def init():
            airplane.set_data([], [])
            return airplane,

        def update(frame):
            if frame < len(coords):
                airplane.set_data(longitudes[frame], latitudes[frame])
                self.result_area.config(state="normal")
                self.result_area.delete(1.0, tk.END)
                self.result_area.insert(tk.END, f"Vitesse: {speed * 100} km/h\n")
                self.result_area.insert(tk.END, f"Altitude: {altitude} pieds\n")
                self.result_area.config(state="disabled")
            return airplane,

        ani = animation.FuncAnimation(fig, update, frames=len(coords), init_func=init, blit=True, interval=200)
        plt.show()

# Exemple d'utilisation
if __name__ == "__main__":
    root = tk.Tk()
    app = FlightApp(root)
    root.mainloop()