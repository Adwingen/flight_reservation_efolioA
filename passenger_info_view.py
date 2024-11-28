# passenger_info_view.py

import tkinter as tk
from tkinter import messagebox
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from settings import SMTP_SERVER, SMTP_PORT, EMAIL_ADDRESS, EMAIL_PASSWORD
import re

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

class PassengerInfoView:
    def __init__(self, root, controller, flight, seats, num_passengers):
        self.passenger_data = None
        self.root = tk.Toplevel(root)
        self.controller = controller
        self.flight = flight
        self.seats = seats
        self.num_passengers = num_passengers
        self.passenger_entries = []

        self.root.title("Passenger Information")
        self.root.configure(bg=DEEP_FOREST)

        self.root.resizable(False, False)

        self.create_widgets()

    def create_widgets(self):
        """Cria o formulário para informações dos passageiros."""
        tk.Label(self.root, text="Flight Summary:", bg=DEEP_FOREST, fg=BRIGHT_YELLOW, font=FONT_LABEL).pack(pady=10)

        # Resumo do voo
        flight_summary = f"""
        - Flight Number: {self.flight['itineraries'][0]['segments'][0]['carrierCode']} {self.flight['itineraries'][0]['segments'][0]['number']}
        - From: {self.flight['itineraries'][0]['segments'][0]['departure']['iataCode']}
        - To: {self.flight['itineraries'][0]['segments'][-1]['arrival']['iataCode']}
        - Total Price: {self.flight['price']['grandTotal']} {self.flight['price']['currency']}
        - Seats: {', '.join(self.seats)}
        """
        tk.Label(
            self.root, text=flight_summary.strip(),
            bg=FOREST_GREEN, fg=BRIGHT_YELLOW, font=("Arial", 10),
            justify="left", anchor="w", wraplength=400
        ).pack(pady=5, padx=10, fill="x")

        # Detalhes dos passageiros
        tk.Label(self.root, text="Passenger Details", bg=DEEP_FOREST, fg=BRIGHT_YELLOW, font=FONT_LABEL).pack(pady=10)

        # Adiciona os campos de entrada
        self.passenger_frame = tk.Frame(self.root, bg=DEEP_FOREST)
        self.passenger_frame.pack(pady=5, padx=10)

        # Atribuir assentos aos passageiros e criar entradas
        self.passenger_entries = []
        for i in range(self.num_passengers):
            assigned_seat = self.seats[i]  # Atribuir assento a cada passageiro

            tk.Label(self.passenger_frame, text=f"Passenger {i + 1} Seat: {assigned_seat}", bg=DEEP_FOREST, fg="white",
                     anchor="w").grid(row=i * 3, column=0, columnspan=2, sticky="w", pady=5)

            tk.Label(self.passenger_frame, text=f"Passenger {i + 1} Name:", bg=DEEP_FOREST, fg="white",
                     anchor="w").grid(row=i * 3 + 1, column=0, sticky="w", pady=5)
            name_entry = tk.Entry(self.passenger_frame, font=FONT_ENTRY, width=30)
            name_entry.grid(row=i * 3 + 1, column=1, pady=5, padx=10, sticky="w")

            tk.Label(self.passenger_frame, text=f"Passenger {i + 1} Email:", bg=DEEP_FOREST, fg="white",
                     anchor="w").grid(row=i * 3 + 2, column=0, sticky="w", pady=5)
            email_entry = tk.Entry(self.passenger_frame, font=FONT_ENTRY, width=30)
            email_entry.grid(row=i * 3 + 2, column=1, pady=5, padx=10, sticky="w")

            self.passenger_entries.append({"name": name_entry, "email": email_entry, "seat": assigned_seat})

        # Botões de confirmação e cancelamento
        button_frame = tk.Frame(self.root, bg=DEEP_FOREST)
        button_frame.pack(pady=10)

        tk.Button(
            button_frame, text="Confirm", command=self.confirm_passenger_info,
            bg=LEAF_GREEN, fg=DEEP_FOREST, font=FONT_BUTTON, width=10
        ).grid(row=0, column=0, padx=10)

        tk.Button(
            button_frame, text="Cancel", command=self.root.destroy,
            bg="#F44336", fg="white", font=FONT_BUTTON, width=10
        ).grid(row=0, column=1, padx=10)

    def confirm_passenger_info(self):
        """Confirma as informações dos passageiros, valida e salva em JSON."""
        passenger_data = []
        invalid_emails = []

        for i in range(self.num_passengers):
            name = self.passenger_entries[i]['name'].get()
            email = self.passenger_entries[i]['email'].get()
            seat = self.passenger_entries[i]['seat']  # Recupera o assento atribuído

            # Valida o e-mail com regex
            if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
                invalid_emails.append(email)

            # Adiciona o passageiro ao dicionário, incluindo o assento
            passenger_data.append({"name": name, "email": email, "seat": seat})

        # Exibe erro caso existam e-mails inválidos
        if invalid_emails:
            invalid_emails_str = ", ".join(invalid_emails)
            messagebox.showerror(
                "Invalid Email",
                f"The following emails are invalid: {invalid_emails_str}"
            )
            return  # Interrompe o processo se houver e-mails inválidos

        # Salva no arquivo JSON e envia os e-mails
        self.save_booking(passenger_data)
        self.send_confirmation_emails(passenger_data)

        # Coleta todos os e-mails dos passageiros
        all_emails = ", ".join([passenger["email"] for passenger in passenger_data])

        # Exibe a mensagem com todos os e-mails
        messagebox.showinfo(
            "Reserva realizada com sucesso!",
            f"Confirmação enviada para: {all_emails}"
        )


        # Fecha o formulário
        self.root.destroy()

        # Reinicia o formulário inicial
        self.controller.reset_form()


    def save_booking(self, passenger_data):
        """Salva a reserva em um arquivo JSON."""
        booking_data = {
            "flight": self.flight,
            "seats": self.seats,
            "passengers": passenger_data
        }
        try:
            with open("booking.json", "a") as file:
                file.write(json.dumps(booking_data) + "\n")  # Salva cada reserva em uma nova linha
            print("Reserva salva com sucesso.")
        except Exception as e:
            print(f"Erro ao salvar reserva: {e}")
            messagebox.showerror("Error", f"An error occurred while saving the booking: {e}")

    def save_to_json(self):
        """Salva as informações dos passageiros em um arquivo JSON."""
        booking = {
            "flight": self.flight,
            "passengers": self.passenger_data
        }
        with open("booking.json", "w") as file:
            json.dump(booking, file, indent=4)

    def send_confirmation_emails(self, passenger_data):
        """Envia e-mails de confirmação para os passageiros."""
        for passenger in passenger_data:
            try:
                # Configurar e-mail
                msg = MIMEMultipart()
                msg["From"] = EMAIL_ADDRESS
                msg["To"] = passenger["email"]
                msg["Subject"] = "Flight Booking Confirmation"

                # Corpo do e-mail
                body = f"""
                Dear {passenger['name']},

                Thank you for booking with us!

                Flight Details:
                - Flight Number: {self.flight['itineraries'][0]['segments'][0]['carrierCode']} {self.flight['itineraries'][0]['segments'][0]['number']}
                - From: {self.flight['itineraries'][0]['segments'][0]['departure']['iataCode']}
                - To: {self.flight['itineraries'][0]['segments'][-1]['arrival']['iataCode']}
                - Seat: {passenger['seat']}
                - Total Price: {self.flight['price']['grandTotal']} {self.flight['price']['currency']}

                Have a great trip!

                Best regards,
                Flight Booking System
                """
                msg.attach(MIMEText(body, "plain"))

                # Enviar e-mail via SMTP
                with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
                    server.starttls()
                    server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
                    server.sendmail(EMAIL_ADDRESS, passenger["email"], msg.as_string())

                print(f"Email enviado com sucesso para {passenger['email']}")

            except Exception as e:
                print(f"Erro ao enviar e-mail para {passenger['email']}: {e}")
                messagebox.showwarning(
                    "Email Error",
                    f"Failed to send email to {passenger['email']}: {e}"
                )


