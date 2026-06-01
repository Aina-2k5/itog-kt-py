import sys
import requests
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QComboBox
)

SUPPORTED_CURRENCIES = ["USD", "EUR", "RUB", "GBP", "JPY", "CNY"]

class CurrencyConverterApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Перевод валют")
        self.resize(400, 300)
        
        layout = QVBoxLayout(self)
        
        h1 = QHBoxLayout()
        h1.addWidget(QLabel("Мах:"))
        self.amount_input = QLineEdit()
        h1.addWidget(self.amount_input)
        layout.addLayout(h1)
        
        h2 = QHBoxLayout()
        h2.addWidget(QLabel("Из:"))
        self.from_currency = QComboBox()
        self.from_currency.addItems(SUPPORTED_CURRENCIES)
        h2.addWidget(self.from_currency)
        layout.addLayout(h2)
        
        h3 = QHBoxLayout()
        h3.addWidget(QLabel("В:"))
        self.to_currency = QComboBox()
        self.to_currency.addItems(SUPPORTED_CURRENCIES)
        self.to_currency.setCurrentText("RUB")
        h3.addWidget(self.to_currency)
        layout.addLayout(h3)
        
        self.convert_btn = QPushButton("Перевести")
        self.convert_btn.clicked.connect(self.convert)
        layout.addWidget(self.convert_btn)
        
        self.result = QLabel("Сабр ди...")
        self.result.setWordWrap(True)
        layout.addWidget(self.result)

    def convert(self):
        try:
            amount = float(self.amount_input.text().strip())
        except ValueError:
            self.result.setText("Ошибка: введите число")
            return
        
        from_curr = self.from_currency.currentText()
        to_curr = self.to_currency.currentText()
        
        try:
            response = requests.get(
                "http://127.0.0.1:8000/convert",
                params={
                    "amount": amount,
                    "from_currency": from_curr,
                    "to_currency": to_curr
                },
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                self.result.setText(
                    f"{data['amount']} {data['from_currency']} = "
                    f"{data['converted_amount']} {data['to_currency']}\n"
                    f"Курс: 1 {data['from_currency']} = {data['rate']} {data['to_currency']}"
                )
            else:
                error = response.json().get("detail", "Ошибка сервера")
                self.result.setText(error)
                
        except requests.exceptions.ConnectionError:
            self.result.setText("Связь яй.\nЗапустите: uvicorn server:app --reload")
        except Exception as e:
            self.result.setText(f"Ошибка: {e}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CurrencyConverterApp()
    window.show()
    sys.exit(app.exec_())
