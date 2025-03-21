import sys, os
import zipfile
import tempfile
import shutil
from PyQt6.QtWidgets import (QApplication, QMainWindow, QLabel, QPushButton, QVBoxLayout, 
                             QWidget, QFileDialog, QLineEdit, QTextEdit, QCheckBox, QHBoxLayout, 
                             QStatusBar, QSizePolicy, QFileDialog, QMessageBox)
from PyQt6.QtGui import QAction, QPixmap, QIcon, QKeyEvent, QTransform
from PyQt6.QtCore import Qt
from PyQt6.QtPrintSupport import QPrinter, QPrintDialog

class Photo(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Photo") # Imposta il titolo della finestra
        self.setGeometry(100, 100, 450, 700) # Imposta la dimensione della finestra
        
        # Layout principale
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout()

        # Elementi dell'interfaccia
        btn_layout = QHBoxLayout() # Crea un layout ORIZZONTALE per i pulsanti di navigazione
        btn_act_layout = QHBoxLayout() # Crea un layout ORIZZONTALE per i pulsanti di azione
        self.image_label = QLabel(self) # Crea un'etichetta per l'immagine

        self.layout.addWidget(self.image_label, alignment=Qt.AlignmentFlag.AlignCenter) # Aggiungi l'etichetta all'interfaccia
        self.layout.addLayout(btn_layout) # Aggiungi il layout dei pulsanti di navigazione all'interfaccia
        self.layout.addLayout(btn_act_layout) # Aggiungi il layout dei pulsanti di azione all'interfaccia
        self.is_image_fullscreen = False # Imposta la modalità fullscreen dell'immagine a false di default
        
        # Barra di stato
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        # Menù
        menubar = self.menuBar()
        file_menu = menubar.addMenu("File")
        open_action = QAction("Carica Immagini", self) # Crea un'opzione per caricare le immagini
        open_action.triggered.connect(self.load_images) # Collega l'opzione al metodo load_images
        file_menu.addAction(open_action) # Aggiungi l'opzione al menù
        exit_action = QAction("Esci", self) # Crea un'opzione per uscire dall'applicazione
        exit_action.triggered.connect(self.close) # Collega l'opzione al metodo close
        file_menu.addAction(exit_action) # Aggiungi l'opzione al menù
        
        # Etichetta immagine
        self.image_label.setScaledContents(True) # Ridimensiona l'immagine per adattarla alla finestra
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter) # Allinea l'immagine al centro
        self.image_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding) # Permetti l'espansione dell'etichetta

        
        # Pulsanti per la navigazione
        # Pulsante nav sinistra
        self.prev_btn = QPushButton("←") # Crea un pulsante per l'immagine precedente
        self.prev_btn.setStyleSheet("padding: 5px;")
        self.prev_btn.clicked.connect(self.prev_image)
        self.prev_btn.setFixedHeight(50)
        # Pulsante Fullscreen per l'immagine
        self.fullscreen_img_btn = QPushButton() # Crea un pulsante per attivare/disattivare la modalità fullscreen
        self.fullscreen_img_btn.setIcon(QIcon("icons/fullscreen.png")) # Usa un'icona di fullscreen
        self.fullscreen_img_btn.setFixedSize(50, 50) # Imposta la dimensione del pulsante
        self.fullscreen_img_btn.setStyleSheet("padding: 5px;")
        self.fullscreen_img_btn.clicked.connect(self.toggle_image_fullscreen) # Collega il pulsante al metodo toggle_image_fullscreen
        # Pulsante nav destra
        self.next_btn = QPushButton("→") # Crea un pulsante per l'immagine successiva
        self.next_btn.setFixedHeight(50)
        self.next_btn.setStyleSheet("padding: 5px;")
        self.next_btn.clicked.connect(self.next_image) # Collega il pulsante al metodo next_image
        btn_layout.addWidget(self.prev_btn) # Aggiungi il pulsante precedente al layout
        btn_layout.addWidget(self.fullscreen_img_btn) # Aggiungi il pulsante fullscreen al layout
        btn_layout.addWidget(self.next_btn) # Aggiungi il pulsante successivo al layout
        
        # Pulsante Like
        self.like_btn = QPushButton()
        self.like_btn.setIcon(QIcon("icons/heart_empty.png"))
        self.like_btn.setFixedSize(50, 50)
        self.like_btn.setStyleSheet("padding: 5px;")
        btn_act_layout.setAlignment(Qt.AlignmentFlag.AlignLeft) # Allinea il pulsante a sinistra
        self.like_btn.clicked.connect(self.toggle_like) # Collega il pulsante al metodo toggle_like
        btn_act_layout.addWidget(self.like_btn) # Aggiungi il pulsante alla barra dei pulsanti

        # Pulsante Ruota
        self.rotate_btn = QPushButton()
        self.rotate_btn.setIcon(QIcon("icons/rotate.png"))
        self.rotate_btn.setFixedSize(50, 50)
        self.rotate_btn.setStyleSheet("padding: 5px;")
        btn_act_layout.setAlignment(Qt.AlignmentFlag.AlignLeft) # Allinea il pulsante a sinistra
        self.rotate_btn.clicked.connect(self.rotate_image)  # Collega il pulsante al metodo rotate_image
        btn_act_layout.addWidget(self.rotate_btn) # Aggiungi il pulsante alla barra dei pulsanti   

        # Pulsante Download
        self.dwn_btn = QPushButton()
        self.dwn_btn.setIcon(QIcon("icons/download.png"))
        self.dwn_btn.setFixedSize(50, 50)
        self.dwn_btn.setStyleSheet("padding: 5px;")
        btn_act_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.dwn_btn.clicked.connect(self.download_images) # Collega il pulsante al metodo download_image        
        btn_act_layout.addWidget(self.dwn_btn) # Aggiungi il pulsante alla barra dei pulsanti

        # Pulsante Elimina
        self.del_btn = QPushButton()
        self.del_btn.setIcon(QIcon("icons/delete.png"))
        self.del_btn.setFixedSize(50, 50)
        self.del_btn.setStyleSheet("padding: 5px;")
        btn_act_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        # implementare il metodo delete_image
        btn_act_layout.addWidget(self.del_btn) # Aggiungi il pulsante alla barra dei pulsanti

        # Pulsante Stampa
        self.print_btn = QPushButton()
        self.print_btn.setIcon(QIcon("icons/print.png"))
        self.print_btn.setFixedSize(50, 50)
        self.print_btn.setStyleSheet("padding: 5px;")
        btn_act_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        # implementare il metodo print_image
        btn_act_layout.addWidget(self.print_btn) # Aggiungi il pulsante alla barra dei pulsanti        
        
        # Casella di testo per descizioni
        self.comment_box = QTextEdit() # Crea una casella di testo per le descrizioni delle foto
        self.comment_box.setReadOnly(True) # Imposta la casella di testo come sola lettura
        self.comment_box.setFixedHeight(self.comment_box.fontMetrics().height() + 10)  # Altezza iniziale per una riga
        self.comment_box.textChanged.connect(self.adjust_textedit_height)  # Connetti al ridimensionamento automatico
        self.layout.addWidget(self.comment_box) # Aggiungi la casella di testo all'interfaccia
        
        # Casella di input per nuova descrizione
        self.comment_input = QLineEdit()
        self.comment_input.setPlaceholderText("Aggiungi una descrizione...") # Testo di esempio nella casella di input
        self.comment_input.returnPressed.connect(self.add_comment) # Collega la pressione del tasto Invio al metodo add_comment
        self.layout.addWidget(self.comment_input) # Aggiungi la casella di input all'interfaccia
        
        # Casella di selezione per preferiti
        self.favorite_check = QCheckBox("Aggiungi alla selezione multipla") # Crea una casella di selezione per le immagini multiple selezionate per scaricarle
        self.favorite_check.stateChanged.connect(self.toggle_favorite)
        self.layout.addWidget(self.favorite_check) # Aggiungi la casella di selezione all'interfaccia
        
        self.central_widget.setLayout(self.layout) # Imposta il layout principale per la finestra
        
        # Variabili di stato
        self.image_paths = [] # Lista di percorsi delle immagini
        self.current_index = 0 # Indice dell'immagine corrente
        self.likes = [] # Lista di like per le immagini
        self.comments = {} # Dizionario di commenti per le immagini
        self.favorites = {} # Lista di immagini preferite
        self.rotation_angle = 0  # Variabile per memorizzare l'angolo di rotazione dell'immagine
        self.selected_images = []  # Lista per tenere traccia delle immagini selezionate


# METODI -------------------------------------------------------------------------------------------------------
    
    def load_images(self): # Metodo per caricare le immagini
        files, _ = QFileDialog.getOpenFileNames(self, "Seleziona Immagini", "", "Images (*.png *.jpg *.jpeg)")
        if files: # Se sono state selezionate delle immagini
            self.image_paths = files # Aggiorna la lista di percorsi delle immagini
            self.current_index = 0 # Imposta l'indice dell'immagine corrente a 0
            self.comments = {img: "" for img in self.image_paths} # Inizializza i commenti per le immagini
            self.likes = [False] * len(self.image_paths) # Inizializza i like per le immagini
            self.favorites = [False] * len(self.image_paths) # Inizializza le immagini preferite
            self.update_display() # Aggiorna l'interfaccia con l'immagine corrente

    def rotate_image(self): # Metodo per ruotare l'immagine di 90 gradi
        if self.image_paths:
            self.rotation_angle = (self.rotation_angle + 90) % 360  # Incrementa l'angolo di rotazione di 90 gradi
            self.update_display()  # Rendi l'immagine ruotata
            
    def update_display(self): # Metodo per aggiornare l'interfaccia con l'immagine corrente
        if self.image_paths: # Se ci sono immagini caricate
            size = min(self.central_widget.height(), self.central_widget.width(), 400) # Dimensione massima dell'immagine
            pixmap = QPixmap(self.image_paths[self.current_index]) # Crea una mappa di pixel dall'immagine corrente
            # Ritaglia l'immagine per mantenerla quadrata
            min_side = min(pixmap.width(), pixmap.height())
            x_offset = (pixmap.width() - min_side) // 2
            y_offset = (pixmap.height() - min_side) // 2
            cropped_pixmap = pixmap.copy(x_offset, y_offset, min_side, min_side)
            # Ruota l'immagine
            if self.rotation_angle != 0:  # If the image needs to be rotated
                transform = QTransform().rotate(self.rotation_angle)  # Create a transform with the rotation angle
                cropped_pixmap = cropped_pixmap.transformed(transform)  # Apply the rotation to the cropped_pixmap instead
            # Scala l'immagine per adattarla alla finestra solo se necessario
            if cropped_pixmap.width() > size or cropped_pixmap.height() > size:
                scaled_pixmap = cropped_pixmap.scaled(size, size, aspectRatioMode=Qt.AspectRatioMode.KeepAspectRatio)
            else:
                scaled_pixmap = cropped_pixmap
            self.image_label.setPixmap(scaled_pixmap) # Imposta l'immagine nell'etichetta
            self.image_label.setFixedSize(size, size)  # Mantieni l'immagine quadrata
            # Aggiorna i commenti e i like
            self.comment_box.setPlainText(self.comments.get(self.image_paths[self.current_index], "")) # Aggiorna i commenti
            self.like_btn.setIcon(QIcon("icons/heart_filled.png") if self.likes[self.current_index] else QIcon("icons/heart_empty.png")) # Aggiorna l'icona del like
            self.favorite_check.setChecked(self.favorites[self.current_index]) # Aggiorna la casella di selezione preferiti
            self.update_image_details() # Aggiorna i dettagli dell'immagine

            filename = os.path.basename(self.image_paths[self.current_index])  # Ottieni solo il nome del file
            self.setWindowTitle(f"Photo - {filename}")  # Imposta il titolo della finestra con il nome del file

    def resizeEvent(self, event): # Sovrascrive il metodo resizeEvent della finestra principale
        self.update_display()
        super().resizeEvent(event)  # Chiama il metodo originale di QMainWindow
 
    def prev_image(self): # Metodo per visualizzare l'immagine precedente
        if self.image_paths and self.current_index > 0:
            self.current_index -= 1
            self.update_display()

    def next_image(self): # Metodo per visualizzare l'immagine successiva
        if self.image_paths and self.current_index < len(self.image_paths) - 1:
            self.current_index += 1
            self.update_display()

    def toggle_image_fullscreen(self): # Metodo per attivare/disattivare la modalità fullscreen
        if self.is_image_fullscreen: # Se l'immagine è in modalità fullscreen
            self.is_image_fullscreen = False # Disattiva la modalità fullscreen
            self.showNormal()  # Torna alla modalità finestra normale
            self.comment_box.show()  # Mostra i commenti
            self.comment_input.show()  # Mostra la casella di input commenti
            self.favorite_check.show()  # Mostra la checkbox per preferiti
            self.layout.setContentsMargins(10, 10, 10, 10)  # Ripristina i margini
            self.setWindowState(Qt.WindowState.WindowNoState)  # Ripristina la finestra a normale
        else:
            # Vai in modalità fullscreen
            self.is_image_fullscreen = True # Attiva la modalità fullscreen
            self.showFullScreen()  # Vai in modalità schermo intero
            self.like_btn.hide()  # Nascondi il pulsante like
            self.dwn_btn.hide()  # Nascondi il pulsante download
            self.del_btn.hide()  # Nascondi il pulsante delete
            self.print_btn.hide()  # Nascondi il pulsante print
            self.comment_box.hide()  # Nascondi i commenti
            self.comment_input.hide()  # Nascondi la casella di input commenti
            self.favorite_check.hide()  # Nascondi la checkbox per preferiti
            self.layout.setContentsMargins(0, 0, 0, 0)  # Rimuovi i margini

    def keyPressEvent(self, event: QKeyEvent): # Sovrascrive il metodo keyPressEvent della finestra principale (per uscire dalla modalità fullscreen con ESC)
        if event.key() == Qt.Key.Key_Escape and self.is_image_fullscreen:
            self.toggle_image_fullscreen()  # Esci dalla modalità fullscreen con ESC
        super().keyPressEvent(event)
    
    def toggle_like(self): # Metodo per aggiungere/rimuovere un like
        if self.image_paths:
            self.likes[self.current_index] = not self.likes[self.current_index]
            self.update_display()

    def adjust_textedit_height(self): # Metodo per regolare l'altezza della casella di testo in base al contenuto
        doc = self.comment_box.document()
        new_height = int(doc.documentLayout().documentSize().height()) + 10  # Corretto per PyQt6
        max_height = 200  # Limite massimo opzionale
        self.comment_box.setFixedHeight(min(new_height, max_height))  # Imposta la nuova altezza

    def add_comment(self): # Metodo per aggiungere una descrizione
        comment = self.comment_input.text() # Ottieni il testo dalla casella di input
        if not self.image_paths:  # Se la lista è vuota
            self.show_alert("Errore: Nessuna immagine caricata!")
            return

        if not comment.strip():  # Se il commento è vuoto o solo spazi
            self.show_alert("Errore: Il commento non può essere vuoto!")
            return
        if comment:
            self.comments[self.image_paths[self.current_index]] = comment # Aggiorna il commento per l'immagine corrente
            self.comment_box.setPlainText(comment) # Aggiorna la casella di testo con il nuovo commento
            self.comment_input.clear() # Cancella il testo dalla casella di input

    def toggle_favorite(self):
        if self.image_paths:
            # Update the favorite status for the current image
            self.favorites[self.current_index] = self.favorite_check.isChecked()
            # Add or remove the current image from the selected_images list
            current_image = self.image_paths[self.current_index]
            if self.favorite_check.isChecked():
                if current_image not in self.selected_images:
                    self.selected_images.append(current_image)
            else:
                if current_image in self.selected_images:
                    self.selected_images.remove(current_image)
            # Update the status bar message
            self.status_bar.showMessage(f"Immagini selezionate: {len(self.selected_images)}")

    def update_ui(self): # Aggiorna l'interfaccia quando si cambia immagine
        if self.image_paths:
            self.image_label.setPixmap(QPixmap(self.image_paths[self.current_index]))  

            # Controlla se l'immagine è nei preferiti e aggiorna la checkbox
            self.favorite_check.blockSignals(True)  # Evita attivazione del segnale mentre aggiorniamo lo stato
            self.favorite_check.setChecked(self.favorites.get(self.current_index, False))
            self.favorite_check.blockSignals(False)  # Riattiva i segnali dopo l'aggiornamento


    def download_images(self):
        # If no images are selected, download the currently displayed image
        if not self.selected_images:
            if not self.image_paths:
                QMessageBox.warning(self, "Attenzione", "Nessuna immagine da scaricare.")
                return
            # Use the current image as the only image to download
            images_to_download = [self.image_paths[self.current_index]]
        else:
            images_to_download = self.selected_images
        # If only one image is being downloaded, save it directly without zipping
        if len(images_to_download) == 1:
            image_path = images_to_download[0]
            # Ask the user where to save the image
            save_path, _ = QFileDialog.getSaveFileName(
                self,
                "Salva Immagine",
                os.path.basename(image_path),  # Default filename
                "Images (*.png *.jpg *.jpeg);;All Files (*)"            )
            
            if save_path:
                try:
                    shutil.copy(image_path, save_path)  # Copy the image to the selected location
                    QMessageBox.information(self, "Download completato", f"Immagine salvata in:\n{save_path}")
                except Exception as e:
                    QMessageBox.critical(self, "Errore", f"Impossibile salvare l'immagine: {str(e)}")
        
        else:  # If multiple images are selected, zip them
            # Ask the user where to save the ZIP file
            save_path, _ = QFileDialog.getSaveFileName(
                self,
                "Salva Immagini come ZIP",
                "",
                "ZIP Files (*.zip);;All Files (*)"
            )            
            if save_path:
                # Create a temporary directory to store the images before zipping
                temp_dir = tempfile.mkdtemp()                
                try:
                    # Copy selected images to the temporary directory                
                    for i, image_path in enumerate(images_to_download):
                        shutil.copy(image_path, os.path.join(temp_dir, f"image_{i+1}{os.path.splitext(image_path)[1]}"))                    
                    # Create a ZIP file
                    with zipfile.ZipFile(save_path, 'w') as zipf:
                        for root, dirs, files in os.walk(temp_dir):
                            for file in files:
                                zipf.write(os.path.join(root, file), os.path.basename(file))
                    
                    QMessageBox.information(self, "Download completato", f"Immagini salvate in:\n{save_path}")
                
                except Exception as e:
                    QMessageBox.critical(self, "Errore", f"Impossibile creare il file ZIP: {str(e)}")                
                finally:
                    # Clean up the temporary directory                
                    shutil.rmtree(temp_dir)

    def update_image_details(self):
        if self.image_paths:
            current_image_path = self.image_paths[self.current_index]
            pixmap = QPixmap(current_image_path)

            # Ottieni dimensioni dell'immagine in pixel
            width = pixmap.width()
            height = pixmap.height()

            # Ottieni la dimensione del file in KB o MB
            file_size = os.path.getsize(current_image_path)  # Dimensione in byte
            file_size_kb = file_size / 1024  # Converti in KB
            file_size_str = f"{file_size_kb:.2f} KB" if file_size_kb < 1024 else f"{file_size_kb/1024:.2f} MB"

            # Aggiorna l'etichetta con le informazioni
            self.status_bar.showMessage(f"Dimensioni: {width}x{height} px | Peso: {file_size_str}")
        else:
            self.image_details_label.setText("Nessuna immagine selezionata")

    def show_alert(self, message): # Metodo per mostrare un messaggio di avviso
        alert = QMessageBox()
        alert.setIcon(QMessageBox.Icon.Warning)
        alert.setWindowTitle("Errore")
        alert.setText(message)
        alert.setStandardButtons(QMessageBox.StandardButton.Ok)
        alert.exec()  # Mostra la finestra di dialogo



if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Photo()
    window.show()
    sys.exit(app.exec())
