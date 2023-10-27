import sys
import sqlite3
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QPushButton,
    QLabel,
    QLineEdit,
    QMessageBox,
    QFormLayout,
    QTabWidget,
    QInputDialog,
)
from PyQt5.QtGui import QFont, QImage, QPalette, QBrush
from PyQt5.QtCore import Qt, QDateTime
from datetime import datetime

class MyWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Mesai Takip")
        self.setGeometry(100, 100, 800, 600)
        self.users = {"yilmaz": "1234", "aysenur": "5678", "emrehan": "abcd"}
        self.current_user = None

        # Giriş ekranı widget'ı
        self.login_widget = QWidget(self)
        login_layout = QVBoxLayout()
        login_layout.setContentsMargins(150, 150, 150, 150)  # Sağdan ve soldan kırpma
        self.login_widget.setLayout(login_layout)
        self.setCentralWidget(self.login_widget)

        # Arka plan resmini ayarla
        background_image = QImage("background.jpg")
        background_image = background_image.scaled(self.width(), self.height())
        palette = QPalette()
        palette.setBrush(QPalette.Window, QBrush(background_image))
        self.login_widget.setPalette(palette)

        # Giriş ekranı öğeleri
        self.username_label = QLabel("Kullanıcı Adı:")
        self.username_label.setFont(QFont("Arial", 12, QFont.Bold))
        self.username_input = QLineEdit()
        self.username_input.setFont(QFont("Arial", 12))
        self.password_label = QLabel("Şifre:")
        self.password_label.setFont(QFont("Arial", 12, QFont.Bold))
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setFont(QFont("Arial", 12))
        self.login_button = QPushButton("Giriş Yap")
        self.login_button.setFont(QFont("Arial", 14, QFont.Bold))
        self.login_button.clicked.connect(self.login)

        # Giriş ekranı düzeni
        form_layout = QFormLayout()
        form_layout.addRow(self.username_label, self.username_input)
        form_layout.addRow(self.password_label, self.password_input)
        login_layout.addLayout(form_layout)
        login_layout.addWidget(self.login_button)
        login_layout.setAlignment(Qt.AlignCenter)

        # Giriş düğmesi stilini özelleştir
        self.login_button.setStyleSheet("background-color: #4CAF50; color: white;")

        # İşlem düğmeleri
        self.start_button = self.create_button("Başlangıç", "#3498db", self.send_time)
        self.break_button = self.create_button("Mola", "#e74c3c", self.send_time)
        self.break_return_button = self.create_button("Mola Dönüşü", "#f39c12", self.send_time)
        self.end_button = self.create_button("Bitiş", "#2ecc71", self.send_time)

        # Şifre değiştir düğmesi
        self.change_password_button = QPushButton("Şifre Değiştir")
        self.change_password_button.setFont(QFont("Arial", 10))
        self.change_password_button.clicked.connect(self.show_change_password_dialog)

    def resizeEvent(self, event):
        # Ekran boyutu değiştiğinde arka plan resmi boyutunu güncelle
        background_image = QImage("background.jpg")
        background_image = background_image.scaled(self.width(), self.height())
        palette = QPalette()
        palette.setBrush(QPalette.Window, QBrush(background_image))
        self.login_widget.setPalette(palette)

    def center_window(self):
        # Pencereyi ekranın ortasına taşı
        available_geometry = QApplication.primaryScreen().availableGeometry()
        frame_geometry = self.frameGeometry()
        frame_geometry.moveCenter(available_geometry.center())
        self.move(frame_geometry.topLeft())

    def login(self):
        username = self.username_input.text()
        password = self.password_input.text()

        if username in self.users and self.users[username] == password:
            self.current_user = username
            self.show_user_tab()
        else:
            QMessageBox.warning(self, "Hata", "Kullanıcı adı veya şifre hatalı!")

    def show_user_tab(self):
        # Ana sekme widget'ı
        main_widget = QWidget(self)
        self.setCentralWidget(main_widget)

        # Sekmeleri içerecek olan sekme widget'ı
        tab_widget = QTabWidget(main_widget)
        main_layout = QVBoxLayout()
        main_layout.addWidget(QLabel("Mesai Takip Uygulaması", alignment=Qt.AlignCenter))
        main_layout.addWidget(tab_widget)
        main_widget.setLayout(main_layout)

        # Kişi isimleri ve sekme adları
        kisi_isimleri = {"yilmaz": "Yılmaz", "aysenur": "Ayşenur", "emrehan": "Emrehan", "ayse": "Ayşe", "cengiz": "Cengiz", "pinar": "Pınar"}

        # Kullanıcının sekmesini oluştur
        if self.current_user in kisi_isimleri:
            tab = QWidget()
            layout = QVBoxLayout()

            # Kişi adını ekle
            isim_label = QLabel(kisi_isimleri[self.current_user])
            isim_label.setFont(QFont("Arial", 16, QFont.Bold))
            isim_label.setAlignment(Qt.AlignCenter)
            layout.addWidget(isim_label)

            tab.setLayout(layout)
            tab_widget.addTab(tab, kisi_isimleri[self.current_user])  # Kullanıcının kendi sekmesini ekler

            # İşlem butonları
            layout.addWidget(self.start_button)
            layout.addWidget(self.break_button)
            layout.addWidget(self.break_return_button)
            layout.addWidget(self.end_button)

            # Şifre değiştir düğmesini en alta ekle
            layout.addWidget(self.change_password_button, alignment=Qt.AlignBottom | Qt.AlignCenter)

    def create_button(self, text, color, action, font_size=14):
        button = QPushButton(text)
        button.setFont(QFont("Arial", font_size, QFont.Bold))
        if color:
            button.setStyleSheet(f"background-color: {color}; color: white;")
        button.clicked.connect(action)
        return button

    def send_time(self):
        sender_button = self.sender()
        if self.current_user:
            now = datetime.now()
            saat_dakika = now.strftime("%H:%M")
            button_text = sender_button.text()

            veri = {
                'isim': self.current_user,
                'saat': saat_dakika,
                'islem': button_text,
            }

            self.veritabanina_ekle(veri)

    def veritabanina_ekle(self, veri):
        conn = sqlite3.connect("veritabani.db")
        cursor = conn.cursor()

        cursor.execute('''INSERT INTO saatler (isim, saat, islem)
                          VALUES (?, ?, ?)''',
                       (veri['isim'], veri['saat'], veri['islem']))

        conn.commit()
        conn.close()

    def show_change_password_dialog(self):
        new_password, ok_pressed = QInputDialog.getText(self, "Şifre Değiştir", "Yeni Şifre:")
        if ok_pressed:
            self.users[self.current_user] = new_password
            self.update_password_in_database(self.current_user, new_password)
            QMessageBox.information(self, "Başarılı", "Şifre değiştirildi!")

    def update_password_in_database(self, username, new_password):
        conn = sqlite3.connect("veritabani.db")
        cursor = conn.cursor()

        cursor.execute("UPDATE kullanici SET sifre = ? WHERE kullanici_ad = ?", (new_password, username))

        conn.commit()
        conn.close()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MyWindow()
    window.center_window()
    window.show()
    sys.exit(app.exec_())

def initialize_database():
    conn = sqlite3.connect("veritabani.db")
    cursor = conn.cursor()

    # Saatler tablosunu oluştur
    cursor.execute('''CREATE TABLE IF NOT EXISTS saatler (
                    id INTEGER PRIMARY KEY,
                    isim TEXT,
                    saat TEXT,
                    islem TEXT
                )''')

    # Kullanıcı tablosunu oluştur ve örnek kullanıcıları ekleyin
    cursor.execute('''CREATE TABLE IF NOT EXISTS kullanici (
                    id INTEGER PRIMARY KEY,
                    kullanici_ad TEXT,
                    sifre TEXT
                )''')

    # Örnek kullanıcıları ekleyin
    cursor.execute("INSERT OR IGNORE INTO kullanici (kullanici_ad, sifre) VALUES ('yilmaz', '1234')")
    cursor.execute("INSERT OR IGNORE INTO kullanici (kullanici_ad, sifre) VALUES ('aysenur', '5678')")
    cursor.execute("INSERT OR IGNORE INTO kullanici (kullanici_ad, sifre) VALUES ('emrehan', 'abcd')")

    # "saatler" tablosuna "islem" sütununu ekleyin (eğer daha önce eklenmediyse)
    try:
        cursor.execute("ALTER TABLE saatler ADD COLUMN islem TEXT")
    except sqlite3.OperationalError:
        pass

    conn.commit()
    conn.close()

if __name__ == "__main__":
    initialize_database()
