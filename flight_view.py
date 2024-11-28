# flight_view.py

import tkinter as tk
from tkinter import ttk
from tkcalendar import DateEntry
from PIL import Image, ImageTk

# Cores
DEEP_FOREST = "#0B0C10"  # Fundo escuro
FOREST_GREEN = "#1F2833"  # Cinza-escuro
LEAF_GREEN = "#C5C6C7"  # Cinza claro
MOSS_YELLOW = "#66FCF1"  # Azul-turquesa brilhante
BRIGHT_YELLOW = "#45A29E"  # Verde-azulado

# Fontes
FONT_LABEL = ("Arial", 14, "bold")
FONT_BUTTON = ("Arial", 12, "bold")
FONT_ENTRY = ("Arial", 12)




class FlightView:
    def __init__(self, root, controller, destinations):
        self.root = root
        self.controller = controller
        self.destinations = destinations

        # Configuração do frame principal
        self.frame = tk.Frame(self.root, background=DEEP_FOREST)
        self.frame.pack(padx=20, pady=20, fill="both", expand=True)

        self.root.resizable(False, False)


        self.create_widgets()


    def create_widgets(self):
        """Cria os widgets do formulário de busca de voos."""
        tk.Label(self.frame, text="Origin:", bg=DEEP_FOREST, fg=BRIGHT_YELLOW, font=FONT_LABEL).grid(
            row=0, column=0, sticky="e", pady=10, padx=10
        )
        self.origin_var = tk.StringVar(value="LIS - Lisbon")
        self.origin_dropdown = ttk.Combobox(
            self.frame, textvariable=self.origin_var, font=FONT_ENTRY, width=30
        )
        self.origin_dropdown['values'] = sorted(self.destinations)
        self.origin_dropdown.grid(row=0, column=1, pady=10, padx=10)


        tk.Label(self.frame, text="Destination:", bg=DEEP_FOREST, fg=BRIGHT_YELLOW, font=FONT_LABEL).grid(
            row=1, column=0, sticky="e", pady=10, padx=10
        )
        self.destination_var = tk.StringVar(value="JFK - New York")
        self.destination_dropdown = ttk.Combobox(
            self.frame, textvariable=self.destination_var, font=FONT_ENTRY, width=30
        )
        self.destination_dropdown['values'] = sorted(self.destinations)
        self.destination_dropdown.grid(row=1, column=1, pady=10, padx=10)


        tk.Label(self.frame, text="Departure Date:", bg=DEEP_FOREST, fg=BRIGHT_YELLOW, font=FONT_LABEL).grid(
            row=2, column=0, sticky="e", pady=10, padx=10
        )
        self.departure_date = DateEntry(self.frame, width=12, font=FONT_ENTRY)
        self.departure_date.grid(row=2, column=1, pady=10, padx=10, sticky="w")

        tk.Label(self.frame, text="Return Date:", bg=DEEP_FOREST, fg=BRIGHT_YELLOW, font=FONT_LABEL).grid(
            row=3, column=0, sticky="e", pady=10, padx=10
        )
        self.return_date = DateEntry(self.frame, width=12, font=FONT_ENTRY)
        self.return_date.grid(row=3, column=1, pady=10, padx=10, sticky="w")

        tk.Label(self.frame, text="Passengers:", bg=DEEP_FOREST, fg=BRIGHT_YELLOW, font=FONT_LABEL).grid(
            row=4, column=0, sticky="e", pady=10, padx=10
        )
        self.passenger_var = tk.IntVar(value=1)
        tk.Spinbox(
            self.frame, from_=1, to=10, textvariable=self.passenger_var, font=FONT_ENTRY, width=5
        ).grid(row=4, column=1, pady=10, padx=10, sticky="w")

        self.search_button = tk.Button(
            self.frame, text="Search Flights", bg=LEAF_GREEN, fg=DEEP_FOREST,
            activebackground=MOSS_YELLOW, activeforeground=BRIGHT_YELLOW, font=FONT_BUTTON,
            command=self.collect_search_data
        )
        self.search_button.grid(row=5, column=0, columnspan=2, pady=20)

    def collect_search_data(self):
        """Coleta os dados do formulário e envia para o controlador."""
        try:
            data = {
                "origin": self.origin_var.get().split(" - ")[0],
                "destination": self.destination_var.get().split(" - ")[0],
                "departure_date": self.departure_date.get_date().strftime("%Y-%m-%d"),
                "return_date": self.return_date.get_date().strftime("%Y-%m-%d"),
                "passengers": self.passenger_var.get(),
            }
            self.controller.search_flights(data)
        except Exception as e:
            tk.messagebox.showerror("Error", f"Failed to collect search data: {e}")

    def display_flights(self, flights, dictionaries):
        """Exibe os voos disponíveis no canvas usando grid."""
        # Remove widgets antigos do canvas
        if hasattr(self, "results_canvas"):
            self.results_canvas.destroy()

        if hasattr(self, "scrollbar"):
            self.scrollbar.destroy()
            del self.scrollbar

        # Remove duplicados
        seen_flights = set()
        unique_flights = []
        for flight in flights:
            flight_key = (
                flight["price"]["grandTotal"],
                flight["itineraries"][0]["duration"],
                tuple((segment["departure"]["iataCode"], segment["arrival"]["iataCode"]) for segment in
                      flight["itineraries"][0]["segments"]),
            )
            if flight_key not in seen_flights:
                seen_flights.add(flight_key)
                unique_flights.append(flight)

        # Cria um novo canvas para exibir os voos
        self.results_canvas = tk.Canvas(self.frame, bg=DEEP_FOREST, highlightthickness=0)
        self.results_canvas.grid(row=6, column=0, columnspan=3, sticky="nsew", pady=10)

        scrollbar = tk.Scrollbar(self.frame, orient="vertical", command=self.results_canvas.yview)
        scrollbar.grid(row=6, column=3, sticky="ns", pady=10)

        self.results_canvas.configure(yscrollcommand=scrollbar.set)
        self.results_frame = tk.Frame(self.results_canvas, bg=DEEP_FOREST)
        self.results_canvas.create_window((10, 10), window=self.results_frame, anchor="n")

        for i, flight in enumerate(unique_flights):
            frame = tk.Frame(self.results_frame, bg=FOREST_GREEN, bd=2, relief="solid")
            frame.pack(padx=10, pady=10, fill="x", expand=True)

            # Processa detalhes do voo
            price = flight["price"]
            traveler_pricing = flight["travelerPricings"][0]
            checked_bags = traveler_pricing["fareDetailsBySegment"][0].get("includedCheckedBags", {}).get("quantity", 0)

            amenities = traveler_pricing["fareDetailsBySegment"][0].get("amenities", [])
            services = "\n".join(
                [f"  - {amenity['description']}: {'Included' if not amenity['isChargeable'] else 'Paid'}" for amenity in
                 amenities]
            )

            # Detalhes do itinerário (companhia e avião)
            itinerary_details = ""
            for itinerary in flight["itineraries"]:
                for segment in itinerary["segments"]:
                    departure = segment["departure"]["iataCode"]
                    arrival = segment["arrival"]["iataCode"]
                    airline = dictionaries["carriers"].get(segment["carrierCode"], "Unknown Airline")
                    aircraft = dictionaries["aircraft"].get(segment["aircraft"]["code"], "Unknown Aircraft")
                    departure_time = segment["departure"]["at"]
                    duration = segment["duration"]

                    itinerary_details += f"""
                    - From {departure} to {arrival}
                      Airline: {airline}
                      Aircraft: {aircraft}
                      Departure: {departure_time}
                      Duration: {duration}
                    """

            # Informações detalhadas
            flight_info = f"""
    Flight {i + 1}:\n
    Total Price: {price['grandTotal']} {price['currency']}
    Duration: {flight['itineraries'][0]['duration']}
    Stops: {len(flight['itineraries'][0]['segments']) - 1}
    Bags Included: {checked_bags}\n
    Amenities:
    {services}\n
    Itinerary Details:
    {itinerary_details}
            """

            # Ajusta exibição do texto no frame
            tk.Label(frame, text=flight_info.strip(), bg=FOREST_GREEN, fg=BRIGHT_YELLOW, font=("Arial", 10),
                     justify="left", anchor="w", wraplength=700).pack(side="left", padx=10, pady=5)

            tk.Button(
                frame,
                text="Select",
                bg=LEAF_GREEN,
                fg=DEEP_FOREST,
                font=("Arial", 10, "bold"),
                command=lambda f=flight: self.controller.select_flight(f),
            ).pack(side="right", padx=10, pady=10)

        self.results_frame.update_idletasks()
        self.results_canvas.config(scrollregion=self.results_canvas.bbox("all"))
















