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
    QFormLayout,
    QTabWidget,
    QInputDialog,
    QDateEdit,
)
from PyQt5.QtGui import QFont, QImage, QPalette, QBrush
from PyQt5.QtCore import Qt
from datetime import datetime
from PyQt5.QtCore import *

def login(self):
    username = self.username_input.text()
    password = self.password_input.text()

    if username in self.users and self.users[username] == password:
        self.current_user = username
        self.show_user_tab()

        # Kullanıcı girişi doğrulandığında veri eklemeyi buraya ekleyin
        selected_date = self.date_input.date().toString("dd.MM.yyyy")
        saat = datetime.now().strftime("%H:%M")
        islem = "Başlangıç"  # veya diğer işlemler

        # Örnek olarak işlem verilerini ekleyin
        self.database.insert_time(username, selected_date, saat, islem)

        # Örnek olarak çalışma sürelerini ekleyin
        daily_hours = 8.0
        weekly_hours = 40.0
        monthly_hours = 160.0
        self.database.insert_work_hours(username, selected_date, daily_hours, weekly_hours, monthly_hours)
    else:
        QMessageBox.warning(self, "Hata", "Kullanıcı adı veya şifre hatalı!")


class Database:
    def __init__(self, db_name):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()

    def create_tables(self):
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS saatler (
            id INTEGER PRIMARY KEY,
            isim TEXT,
            tarih TEXT,
            saat TEXT,
            islem TEXT
        )''')

        self.cursor.execute('''CREATE TABLE IF NOT EXISTS kullanici (
            id INTEGER PRIMARY KEY,
            kullanici_ad TEXT,
            sifre TEXT
        )''')
        
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS calisma_sureleri (
            id INTEGER PRIMARY KEY,
            isim TEXT,
            tarih TEXT,
            gunluk_sure REAL,
            haftalik_sure REAL,
            aylik_sure REAL
            )''')

        self.conn.commit()

    def insert_user(self, username, password):
        self.cursor.execute("INSERT OR IGNORE INTO kullanici (kullanici_ad, sifre) VALUES (?, ?)", (username, password))
        self.conn.commit()

    def update_password(self, username, new_password):
        self.cursor.execute("UPDATE kullanici SET sifre = ? WHERE kullanici_ad = ?", (new_password, username))
        self.conn.commit()

    def insert_time(self, username, selected_date, saat, islem):
        self.cursor.execute("INSERT INTO saatler (isim, tarih, saat, islem) VALUES (?, ?, ?, ?)", (username, selected_date, saat, islem))
        self.conn.commit()
        
    def insert_work_hours(self, username, selected_date, daily_hours, weekly_hours, monthly_hours):
        self.cursor.execute("INSERT INTO calisma_sureleri (isim, tarih, gunluk_sure, haftalik_sure, aylik_sure) VALUES (?, ?, ?, ?, ?)",
                            (username, selected_date, daily_hours, weekly_hours, monthly_hours))
        self.conn.commit()

class UserData:
    def __init__(self):
        self.data = {}

    def add_data(self, username, selected_date, data):
        self.data.setdefault(username, {}).setdefault(selected_date, []).append(data)

class MyWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)  # Bu satırı ekleyin

        self.user_data = UserData()
        self.database = Database("veritabani.db")

        self.setWindowTitle("Mesai Takip")
        self.setGeometry(100, 100, 800, 600)
        self.current_user = None

        self.users = {"yilmaz": "1234", "aysenur": "5678", "emrehan": "abcd"}

        # Giriş ekranı widget'ı
        self.login_widget = QWidget(self)
        login_layout = QVBoxLayout()
        login_layout.setContentsMargins(150, 150, 150, 150)
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

        # Tarih seçimi
        self.date_label = QLabel("Tarih Seçin:")
        self.date_label.setFont(QFont("Arial", 12, QFont.Bold))
        self.date_input = QDateEdit()
        self.date_input.setFont(QFont("Arial", 12))
        self.date_input.setDisplayFormat("dd.MM.yyyy")
        self.date_input.setDate(QDate.currentDate())

        self.daily_work_hours = {}
        self.weekly_work_hours = {}
        self.monthly_work_hours = {}
        
    def center_window(self):
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
        main_widget = QWidget(self)
        self.setCentralWidget(main_widget)
        tab_widget = QTabWidget(main_widget)
        main_layout = QVBoxLayout()
        main_layout.addWidget(QLabel("Mesai Takip Uygulaması", alignment=Qt.AlignCenter))
        main_layout.addWidget(self.date_label)
        main_layout.addWidget(self.date_input)
        main_layout.addWidget(tab_widget)
        main_widget.setLayout(main_layout)
        kisi_isimleri = {"yilmaz": "Yılmaz", "aysenur": "Ayşenur", "emrehan": "Emrehan"}

        if self.current_user == "yilmaz":
            for user in self.users:
                if user != "yilmaz":
                    tab = QWidget()
                    layout = QVBoxLayout()
                    isim_label = QLabel(kisi_isimleri[user])
                    isim_label.setFont(QFont("Arial", 16, QFont.Bold))
                    isim_label.setAlignment(Qt.AlignCenter)
                    layout.addWidget(isim_label)
                    tab.setLayout(layout)
                    tab_widget.addTab(tab, kisi_isimleri[user])

                    # Kullanıcıya ait çalışma raporlarını görüntülemek için buton ekleyin
                    user_report_button = self.create_button(f"{kisi_isimleri[user]}'ın Raporu", "#3498db", lambda user=user: self.show_work_report(user))
                    layout.addWidget(user_report_button)
                else:
                    # Yılmaz için Ayşenur ve Emrehan raporlarını görüntülemek için düğmeleri ekleyin
                    aysenur_report_button = self.create_button("Ayşenur Raporu", "#3498db", self.show_aysenur_report)
                    emrehan_report_button = self.create_button("Emrehan Raporu", "#3498db", self.show_emrehan_report)
                    layout.addWidget(aysenur_report_button)
                    layout.addWidget(emrehan_report_button)

                    
        else:
            # Diğer kullanıcıların kendi arayüzlerini göstermesi
            tab = QWidget()
            layout = QVBoxLayout()
            isim_label = QLabel(kisi_isimleri[self.current_user])
            isim_label.setFont(QFont("Arial", 16, QFont.Bold))
            isim_label.setAlignment(Qt.AlignCenter)
            layout.addWidget(isim_label)
            tab.setLayout(layout)
            tab_widget.addTab(tab, kisi_isimleri[self.current_user])

            layout.addWidget(self.start_button)
            layout.addWidget(self.break_button)
            layout.addWidget(self.break_return_button)
            layout.addWidget(self.end_button)

            layout.addWidget(self.change_password_button, alignment=Qt.AlignBottom | Qt.AlignCenter)
   
    def show_work_report(self, user):
        if user in self.users:
            user_report = self.get_user_work_report(user)
            QMessageBox.information(self, f"{user}'ın Raporu", user_report)

    def get_user_work_report(self, user):
        user_work_hours = self.get_all_work_hours()
        if user in user_work_hours:
            work_hours = user_work_hours[user]
            daily_report = self.get_formatted_work_report(work_hours['daily'])
            weekly_report = self.get_formatted_work_report(work_hours['weekly'])
            monthly_report = self.get_formatted_work_report(work_hours['monthly'])
            return f"{user} Çalışma Raporu\nGünlük: {daily_report}\nHaftalık: {weekly_report}\nAylık: {monthly_report}"
        else:
            return f"{user} için rapor bulunamadı."

    def get_formatted_work_report(self, hours):
        return f"{hours:.2f} saat"

    def get_all_work_hours(self):
        # Tüm kullanıcıların günlük, haftalık ve aylık çalışma saatlerini burada hesaplayın
        all_work_hours = {}
        for user in self.users:
            daily_hours = self.calculate_daily_work_hours(user)
            weekly_hours = self.calculate_weekly_work_hours(user)
            monthly_hours = self.calculate_monthly_work_hours(user)
            all_work_hours[user] = {
                'daily': daily_hours,
                'weekly': weekly_hours,
                'monthly': monthly_hours,
            }
        return all_work_hours


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
          selected_date = self.date_input.date().toString("dd.MM.yyyy")

          veri = {
              'saat': saat_dakika,
              'islem': button_text,
          }

          daily_data = self.user_data.data.setdefault(self.current_user, {}).setdefault(selected_date, [])

          if any(item['islem'] == button_text for item in daily_data):
              return

          if button_text == "Başlangıç":
              veri["start_time"] = saat_dakika
          elif button_text == "Bitiş":
              if "start_time" in veri:
                  start_time = datetime.strptime(veri["start_time"], "%H:%M")
                  end_time = datetime.strptime(saat_dakika, "%H:%M")
                  work_hours = (end_time - start_time).seconds / 3600
                  if "break" in veri:
                      work_hours -= veri["break"]
                      veri["islem"] = f"Bitiş ({work_hours:.2f} saat)"
                      self.update_daily_work_hours(work_hours, selected_date)
                  else:
                      veri["islem"] = "Bitiş (Başlangıç yapmadan)"
                      del veri["start_time"]
                      del veri["break"]
              elif button_text == "Mola":
                  veri["break_start_time"] = saat_dakika
              elif button_text == "Mola Dönüşü":
                  if "break_start_time" in veri:
                      break_start_time = datetime.strptime(veri["break_start_time"], "%H:%M")
                      break_end_time = datetime.strptime(saat_dakika, "%H:%M")
                      break_duration = (break_end_time - break_start_time).seconds / 3600
                      veri["break"] = break_duration
                      veri["islem"] = f"Mola ({break_duration:.2f} saat)"
                      self.update_daily_work_hours(-break_duration, selected_date)
                  else:
                      veri["islem"] = "Mola Dönüşü (Mola başlatmadan)"
                      del veri["break_start_time"]

    def update_daily_work_hours(self, work_hours, selected_date):
      if self.current_user not in self.daily_work_hours:
          self.daily_work_hours[self.current_user] = {}
      self.daily_work_hours[self.current_user][selected_date] = self.daily_work_hours.get(self.current_user, {}).get(selected_date, 0) + work_hours

      if selected_date not in self.weekly_work_hours:
          self.weekly_work_hours[selected_date] = 0
      self.weekly_work_hours[selected_date] += work_hours

      if selected_date.split('.')[1] not in self.monthly_work_hours:
          self.monthly_work_hours[selected_date.split('.')[1]] = 0
      self.monthly_work_hours[selected_date.split('.')[1]] += work_hours

      daily_hours = self.daily_work_hours.get(self.current_user, {}).get(selected_date, 0)
      weekly_hours = self.weekly_work_hours.get(selected_date, 0)
      monthly_hours = self.monthly_work_hours.get(selected_date.split('.')[1], 0)
      self.database.insert_work_hours(self.current_user, selected_date, daily_hours, weekly_hours, monthly_hours)

    def show_all_work_hours(self):
        user_work_hours = self.get_all_work_hours()
        layout = QVBoxLayout()
        yilmaz_label = QLabel("Tüm Kullanıcıların Çalışma Saatleri", alignment=Qt.AlignCenter)
        layout.addWidget(yilmaz_label)

        for username, work_hours in user_work_hours.items():
            user_label = QLabel(f"{username}:\nGünlük: {work_hours['daily']} saat\nHaftalık: {work_hours['weekly']} saat\nAylık: {work_hours['monthly']} saat")
            layout.addWidget(user_label)

        self.yilmaz_widget.setLayout(layout)  
    def veritabanina_ekle(self, username, selected_date, veri):
        self.database.insert_time(username, selected_date, veri['saat'], veri['islem'])

    def show_change_password_dialog(self):
        new_password, ok_pressed = QInputDialog.getText(self, "Şifre Değiştir", "Yeni Şifre:")
        if ok_pressed:
            self.users[self.current_user] = new_password
            self.database.update_password(self.current_user, new_password)
            QMessageBox.information(self, "Başarılı", "Şifre değiştirildi!")

    def show_aysenur_report(self):
        aysenur_report = self.get_user_work_report("aysenur")
        QMessageBox.information(self, "Ayşenur'un Raporu", aysenur_report)

    def show_emrehan_report(self):
        emrehan_report = self.get_user_work_report("emrehan")
        QMessageBox.information(self, "Emrehan'ın Raporu", emrehan_report)

    def create_button(self, text, color, action, font_size=14):
        button = QPushButton(text)
        button.setFont(QFont("Arial", font_size, QFont.Bold))
        if color:
            button.setStyleSheet(f"background-color: {color}; color: white;")
        button.clicked.connect(action)
        return button

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MyWindow()
    window.center_window()
    window.show()
    sys.exit(app.exec_())

def initialize_database():
    database = Database("veritabani.db")
    database.create_tables()
    database.insert_user('yilmaz', '1234')
    database.insert_user('aysenur', '5678')
    database.insert_user('emrehan', 'abcd')

if __name__ == "__main__":
    initialize_database()
