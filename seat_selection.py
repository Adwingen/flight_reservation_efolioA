# seat_seletion.py

import tkinter as tk
from tkinter import messagebox
import json

# Cores
AVAILABLE_SEAT_COLOR = "#4CAF50"  # Verde para assentos disponíveis
OCCUPIED_SEAT_COLOR = "#F44336"  # Vermelho para assentos ocupados
SELECTED_SEAT_COLOR = "#FFEB3B"  # Amarelo para assentos selecionados

# Cores
DEEP_FOREST = "#0B0C10"  # Fundo escuro
FOREST_GREEN = "#1F2833"  # Cinza-escuro
LEAF_GREEN = "#C5C6C7"  # Cinza claro
MOSS_YELLOW = "#66FCF1"  # Azul-turquesa brilhante
BRIGHT_YELLOW = "#45A29E"  # Verde-azulado

FONT_LABEL = ("Arial", 12, "bold")

class SeatSelectionView:
    def __init__(self, root, controller, flight, num_passengers):
        self.root = tk.Toplevel(root)
        self.controller = controller
        self.flight = flight
        self.num_passengers = num_passengers  # Recebe o número de passageiros
        self.selected_seats = []

        self.root.title("Select Your Seats")
        self.root.geometry("400x600")
        self.root.configure(bg=DEEP_FOREST)

        self.create_status_bar()
        self.create_seat_layout()
        self.update_status()

        self.root.resizable(False, False)

    def update_status(self):
        """Atualiza o contador de assentos restantes."""
        remaining_seats = self.num_passengers - len(self.selected_seats)
        self.status_label.config(
            text=f"Seats remaining: {remaining_seats}"
        )

    def create_status_bar(self):
        """Exibe o número de assentos restantes e botão no topo."""
        self.status_frame = tk.Frame(self.root, bg=DEEP_FOREST)
        self.status_frame.pack(pady=10)

        # Atualiza o contador corretamente
        self.status_label = tk.Label(
            self.status_frame,
            text=f"Seats remaining: {self.num_passengers - len(self.selected_seats)}",
            font=FONT_LABEL,
            bg=DEEP_FOREST,
            fg="white"
        )
        self.status_label.grid(row=0, column=0, padx=10)

        tk.Button(
            self.status_frame,
            text="Confirm Selection",
            command=self.confirm_selection,
            bg="#FFEB3B",
            fg="black",
            font=FONT_LABEL
        ).grid(row=0, column=1, padx=10)

    def create_seat_layout(self):
        """Cria o layout dos assentos com barra de rolagem e centralização."""
        self.seat_canvas = tk.Canvas(self.root, bg=DEEP_FOREST, highlightthickness=0)
        self.seat_canvas.pack(side="left", fill="both", expand=True)

        scrollbar = tk.Scrollbar(self.root, orient="vertical", command=self.seat_canvas.yview)
        scrollbar.pack(side="right", fill="y")
        self.seat_canvas.configure(yscrollcommand=scrollbar.set)

        self.seat_frame = tk.Frame(self.seat_canvas, bg=DEEP_FOREST)
        self.seat_canvas.create_window((0, 0), window=self.seat_frame, anchor="nw")

        rows = 20  # Quantidade de fileiras de assentos
        cols = "ABC DEF"  # Layout de colunas com corredor

        occupied_seats = self.load_occupied_seats()

        self.seat_buttons = {}

        for row in range(1, rows + 1):
            row_frame = tk.Frame(self.seat_frame, bg=DEEP_FOREST)  # Frame para alinhar cada fileira
            row_frame.grid(row=row, column=0, pady=5, padx=5)

            col_index = 0
            for col in cols:
                if col == " ":
                    tk.Label(row_frame, text=" ", bg=DEEP_FOREST, width=2).grid(row=0,
                                                                              column=col_index)  # Espaço para o corredor
                    col_index += 1
                    continue

                seat_id = f"{row}{col}"
                button = tk.Button(
                    row_frame, text=seat_id, width=5, height=2,
                    bg=AVAILABLE_SEAT_COLOR if seat_id not in occupied_seats else OCCUPIED_SEAT_COLOR,
                    state="normal" if seat_id not in occupied_seats else "disabled",
                    command=lambda s=seat_id: self.select_seat(s)
                )
                button.grid(row=0, column=col_index, padx=5, pady=5)
                self.seat_buttons[seat_id] = button
                col_index += 1

        self.seat_frame.update_idletasks()
        self.seat_canvas.config(scrollregion=self.seat_canvas.bbox("all"))

        # Ajusta largura do canvas para centralizar os assentos
        self.seat_canvas.bind("<Configure>", self.on_canvas_configure)

    def on_canvas_configure(self, event):
        """Ajusta o canvas para que o frame interno fique centralizado."""
        canvas_width = event.width
        frame_width = self.seat_frame.winfo_reqwidth()
        if frame_width < canvas_width:
            self.seat_canvas.itemconfig(
                self.seat_canvas.create_window((canvas_width // 2, 0), window=self.seat_frame, anchor="n"))

    def select_seat(self, seat_id):
        """Callback para seleção de assentos."""
        if seat_id in self.selected_seats:
            # Remove assento selecionado
            self.selected_seats.remove(seat_id)
            self.seat_buttons[seat_id].config(bg=AVAILABLE_SEAT_COLOR)
        elif len(self.selected_seats) < self.num_passengers:
            # Adiciona assento selecionado
            self.selected_seats.append(seat_id)
            self.seat_buttons[seat_id].config(bg=SELECTED_SEAT_COLOR)

        # Atualiza o contador
        self.update_status()

    def confirm_selection(self):
        """Confirma os assentos selecionados e avança para o próximo passo."""
        if len(self.selected_seats) == self.num_passengers:
            self.controller.confirm_seat_selection(self.selected_seats)
            self.root.destroy()
        else:
            messagebox.showwarning(
                "Incomplete Selection",
                f"Please select {self.num_passengers} seats before confirming."
            )

    def load_occupied_seats(self):
        """Carrega os assentos ocupados do arquivo JSON, se disponível."""
        try:
            with open("booking.json", "r") as file:
                bookings = [json.loads(line) for line in file]

                # Obter números de voo para o voo atual
                current_flight_numbers = [
                    segment["number"]
                    for itinerary in self.flight["itineraries"]
                    for segment in itinerary["segments"]
                ]

                # Filtrar os assentos ocupados com base nos números de voo
                occupied_seats = [
                    seat
                    for booking in bookings
                    if any(
                        segment["number"] in current_flight_numbers
                        for itinerary in booking["flight"]["itineraries"]
                        for segment in itinerary["segments"]
                    )
                    for seat in booking["seats"]
                ]
                return occupied_seats
        except FileNotFoundError:
            return []







