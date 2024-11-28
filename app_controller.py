# app_controller.py

from model.flight_model import FlightModel
from view.flight_view import FlightView
from tkinter import messagebox
from settings import API_KEY, API_SECRET
from view.seat_selection import SeatSelectionView
from view.passenger_info_view import PassengerInfoView
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from settings import SMTP_SERVER, SMTP_PORT, EMAIL_ADDRESS, EMAIL_PASSWORD
from datetime import datetime, date


class AppController:
    def __init__(self, root):
        self.model = FlightModel(API_KEY, API_SECRET)

        try:
            self.destinations = self.model.get_destinations()
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred while fetching destinations: {e}")
            self.destinations = []

        self.view = FlightView(root, self, self.destinations)

    def search_flights(self, data):
        """Busca voos com base nos dados fornecidos e os exibe."""
        print("Search Flights Triggered:", data)  # Debug
        try:
            flights, dictionaries = self.model.search_flights(
                origin=data["origin"],
                destination=data["destination"],
                departure=data["departure_date"],
                return_date=data["return_date"],
                passengers=data["passengers"],
            )
            if flights:
                self.view.display_flights(flights, dictionaries)
            else:
                messagebox.showinfo("No Flights", "No flights were found for the selected criteria.")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")

    def select_flight(self, flight):
        """Armazena o voo selecionado e avança para a próxima etapa."""
        # Salva o voo selecionado
        self.selected_flight = flight

        # Mostra uma mensagem de confirmação
        messagebox.showinfo("Flight Selected", "You have selected a flight!")

        # Avança para a próxima etapa: Seleção de assentos
        self.open_seat_selection()

    def open_seat_selection(self):
        """Abre a janela de seleção de assentos."""
        # Número de passageiros com base na pesquisa inicial
        num_passengers = self.view.passenger_var.get()
        self.selected_passengers = num_passengers
        SeatSelectionView(self.view.root, self, self.selected_flight, num_passengers)

    def confirm_seat_selection(self, selected_seats):
        """Lida com a confirmação da seleção de assentos."""
        self.selected_seats = selected_seats
        messagebox.showinfo(
            "Seats Confirmed",
            f"Seats {', '.join(self.selected_seats)} have been confirmed!"
        )
        # Avançar para a próxima etapa: informações dos passageiros
        self.open_passenger_info()

    def open_passenger_info(self):
        """Abre a janela para coletar informações dos passageiros."""
        PassengerInfoView(
            self.view.root,
            self,
            self.selected_flight,
            self.selected_seats,
            self.view.passenger_var.get()  # Pega o número de passageiros do formulário principal
        )

    def send_email(recipient, subject, body):
        try:
            # Configurar o e-mail
            msg = MIMEMultipart()
            msg["From"] = EMAIL_ADDRESS
            msg["To"] = recipient
            msg["Subject"] = subject

            # Adicionar corpo do e-mail
            msg.attach(MIMEText(body, "plain"))

            # Configurar servidor SMTP
            with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
                server.starttls()  # Iniciar conexão segura
                server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)  # Login
                server.sendmail(EMAIL_ADDRESS, recipient, msg.as_string())  # Enviar e-mail

            print(f"E-mail enviado com sucesso para {recipient}")

        except Exception as e:
            print(f"Erro ao enviar e-mail para {recipient}: {e}")
            raise Exception(f"Failed to send email: {e}")

    def reset_form(self):
        """Reinicia os campos do formulário inicial."""
        self.view.origin_var.set("LIS - Lisbon")  # Define o valor padrão para origem
        self.view.destination_var.set("JFK - New York")  # Define o valor padrão para destino

        # Define a data de hoje para as datas padrão
        today = date.today()
        self.view.departure_date.set_date(today)
        self.view.return_date.set_date(today)

        self.view.passenger_var.set(1)  # Número padrão de passageiros

        # Limpa quaisquer resultados anteriores na exibição de voos
        if hasattr(self.view, "results_canvas"):
            self.view.results_canvas.destroy()

        # Remove o scrollbar de resultados se ele existir
        if hasattr(self.view, "scrollbar"):
            self.view.scrollbar.destroy()
            del self.view.scrollbar


















