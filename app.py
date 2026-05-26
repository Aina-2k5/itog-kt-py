import sys
import requests
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QComboBox, QMessageBox
)


class CurrencyConverterApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Переводы валют")
        self.resize(420, 320)
        self.setStyleSheet("""
            QWidget { 
                background: #1e2a3a; 
                color: #e8f0fe; 
                font-size: 14px; 
                font-family: Arial, sans-serif;
            }
            QLineEdit, QComboBox { 
                background: #2c3e50; 
                border: 1px solid #4a90d9;
                border-radius: 6px; 
                padding: 8px 12px; 
                color: #e8f0fe;
            }
            QPushButton { 
                background: #4a90d9; 
                border: none; 
                border-radius: 6px;
                padding: 10px; 
                font-weight: bold;
                font-size: 15px;
            }
            QPushButton:hover { 
                background: #5aa0e8; 
            }
            QPushButton:pressed {
                background: #3a80c9;
            }
            QLabel { 
                color: #cdd9f0; 
                line-height: 1.6; 
            }
            QLabel#result {
                font-size: 16px;
                font-weight: bold;
                color: #a8d8ff;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(25, 25, 25, 25)
        
        amount_layout = QHBoxLayout()
        amount_layout.addWidget(QLabel("Сумма:"))
        self.amount_input = QLineEdit(placeholderText="массала: 100")
        amount_layout.addWidget(self.amount_input)
        layout.addLayout(amount_layout)
        
        from_layout = QHBoxLayout()
        from_layout.addWidget(QLabel("Из:"))
        self.from_currency = QComboBox()
        self.from_currency.addItems(SUPPORTED_CURRENCIES)
        self.from_currency.setCurrentText("USD")
        from_layout.addWidget(self.from_currency)
        layout.addLayout(from_layout)
        
        to_layout = QHBoxLayout()
        to_layout.addWidget(QLabel("В:"))
        self.to_currency = QComboBox()
        self.to_currency.addItems(SUPPORTED_CURRENCIES)
        self.to_currency.setCurrentText("RUB")
        to_layout.addWidget(self.to_currency)
        layout.addLayout(to_layout)
        
        self.convert_btn = QPushButton("Перевести")
        layout.addWidget(self.convert_btn)
        
        self.result = QLabel("Введите сумму")
        self.result.setObjectName("result")
        self.result.setWordWrap(True)
        layout.addWidget(self.result)
        
        self.convert_btn.clicked.connect(self.convert)
    
    def convert(self):
        try:
            amount = float(self.amount_input.text().strip())
        except ValueError:
            self.result.setText("Ошибка: введите правильное число")
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
                    f"Курс: 1 {data['from_currency']} = {data['rate']} {data['to_currency']}\n"
                    f"Источник: {data['source']}"
                )
            else:
                error = response.json().get("detail", "Неизвестная ошибка")
                self.result.setText(f"{error}")
                
        except requests.exceptions.ConnectionError:
            self.result.setText(
                "🔌 Нет связи с сервером.\n"
                "Запустите сервер командой:\n"
                "uvicorn server:app --reload"
            )
        except Exception as e:
            self.result.setText(f"Ошибка: {e}")

SUPPORTED_CURRENCIES = ["USD", "EUR", "RUB", "GBP", "JPY", "CNY"]


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CurrencyConverterApp()
    window.show()
    sys.exit(app.exec_())