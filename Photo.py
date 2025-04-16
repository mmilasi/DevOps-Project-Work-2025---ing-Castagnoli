import sys, os
import zipfile
import tempfile
import shutil
import requests
import webbrowser
from urllib.parse import quote
from PyQt6.QtWidgets import (QApplication, QMainWindow, QLabel, QPushButton, QVBoxLayout, 
                             QWidget, QFileDialog, QLineEdit, QTextEdit, QCheckBox, QHBoxLayout, 
                             QStatusBar, QSizePolicy, QFileDialog, QMessageBox, QScrollArea, QDialog)
from PyQt6.QtGui import QAction, QPixmap, QIcon, QKeyEvent, QTransform, QTextCursor, QTextBlockFormat, QPainter, QPageLayout, QWheelEvent
from PyQt6.QtCore import Qt, QPointF, QObject, QThread, pyqtSignal
from PyQt6.QtPrintSupport import QPrinter, QPrintDialog

class ImgurUploader(QObject): # dedicato al caricamento di immagini per la ricerca visiva Google Lens attraverso Imgur
    finished = pyqtSignal(str) 
    error = pyqtSignal(str)
    def __init__(self, image_path, client_id):
        super().__init__()
        self.image_path = image_path
        self.client_id = client_id
    def run(self):
        try:
            headers = {"Authorization": f"Client-ID {self.client_id}"}
            with open(self.image_path, "rb") as f:
                image_data = f.read()
            response = requests.post(
                "https://api.imgur.com/3/image",
                headers=headers,
                files={"image": image_data})
            if response.status_code == 200:
                data = response.json()
                img_url = data["data"]["link"]
                self.finished.emit(img_url)
            else:
                self.error.emit(f"Errore upload Imgur: {response.status_code}\n{response.text}")
        except Exception as e:
            self.error.emit(str(e))

class LoadingDialog(QDialog): # Finestra di caricamento immagine temporanea per ricerca visiva Google Lens
    def __init__(self, parent=None, message="Attendere..."):
        super().__init__(parent)
        self.setWindowTitle("Google Lens")
        self.setFixedSize(300, 100)
        self.setWindowModality(Qt.WindowModality.ApplicationModal)
        layout = QVBoxLayout()
        label = QLabel(message)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)
        self.setLayout(layout)

class Photo(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowIcon(QIcon("icons/gallery.svg"))
        self.setWindowTitle("Photo Gallery")  # Imposta il titolo della finestra
        self.setGeometry(100, 100, 450, 700)  # Imposta la dimensione della finestra

        # Layout principale
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)  # Imposta il layout principale UNA SOLA VOLTA
        self.is_image_fullscreen = False  # Imposta la modalità fullscreen dell'immagine a false di default

        # Barra di stato
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        # Menù
        menubar = self.menuBar()
        file_menu = menubar.addMenu("File")
        open_action = QAction("Carica Immagini", self)  # Crea un'opzione per caricare le immagini
        open_action.triggered.connect(self.load_images)  # Collega l'opzione al metodo load_images
        file_menu.addAction(open_action)  # Aggiungi l'opzione al menù
        exit_action = QAction("Esci", self)  # Crea un'opzione per uscire dall'applicazione
        exit_action.triggered.connect(self.close)  # Collega l'opzione al metodo close
        file_menu.addAction(exit_action)  # Aggiungi l'opzione al menù
        file_view = menubar.addMenu("Aspetto")
        light_action = QAction("Tema chiaro", self) # Crea un'opzione per scegliere il tema chiaro
        light_action.triggered.connect(self.set_light_theme)
        file_view.addAction(light_action) # Aggiungi l'opzione al menù
        dark_action = QAction("Tema scuro", self) # Crea un'opzione per scegliere il tema scuro
        dark_action.triggered.connect(self.set_dark_theme)
        file_view.addAction(dark_action) # Aggiungi l'opzione al menù

        # Etichetta immagine
        # Crea area di scorrimento (per zoom)
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # Crea l'etichetta per l'immagine, figlia dell'area di scorrimento
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.scroll_area.setWidget(self.image_label)
        self.layout.addWidget(self.scroll_area)  # Aggiungi area di scorrimento al layout

        # Casella di testo per descrizioni
        self.comment_box = QTextEdit()  # Crea una casella di testo per le descrizioni delle foto
        self.comment_box.setReadOnly(True)  # Imposta la casella di testo come sola lettura
        self.comment_box.setFixedHeight(self.comment_box.fontMetrics().height() + 10)  # Altezza iniziale per una riga
        self.comment_box.textChanged.connect(self.adjust_textedit_height)  # Connetti al ridimensionamento automatico
        self.comment_box.setAlignment(Qt.AlignmentFlag.AlignCenter)  # Centra il testo
        self.layout.addWidget(self.comment_box)  # Aggiungi la casella di testo all'interfaccia

        # Pulsanti per la navigazione
        btn_layout = QHBoxLayout()  # Crea un layout ORIZZONTALE per i pulsanti di navigazione
        self.layout.addLayout(btn_layout)  # Aggiungi il layout dei pulsanti di navigazione all'interfaccia
        # Pulsante nav sinistra
        self.prev_btn = QPushButton("←")
        self.prev_btn.setStyleSheet("padding: 5px;")
        self.prev_btn.clicked.connect(self.prev_image)
        self.prev_btn.setFixedHeight(50)
        # Pulsante Zoom Out
        self.zoom_out_btn = QPushButton()
        self.zoom_out_btn.setIcon(QIcon("icons/zoomout_white.png" if self.is_dark_theme() else "icons/zoomout.png"))        
        self.zoom_out_btn.setFixedSize(50, 50)
        self.zoom_out_btn.setStyleSheet("padding: 5px;")
        self.zoom_out_btn.clicked.connect(self.zoom_out)      
        # Pulsante Reset Zoom
        self.zoom_reset_btn = QPushButton("1:1")
        self.zoom_reset_btn.setFixedSize(50, 50)
        self.zoom_reset_btn.setStyleSheet("padding: 5px;")
        self.zoom_reset_btn.clicked.connect(self.reset_zoom)
        # Pulsante ricerca visiva
        self.search_btn = QPushButton()
        self.search_btn.setIcon(QIcon("icons/search_white.png" if self.is_dark_theme() else "icons/search.png"))        
        self.search_btn.setFixedSize(50, 50)
        self.search_btn.setStyleSheet("padding: 5px;")
        self.search_btn.clicked.connect(self.search_image)   
        # Pulsante Zoom In
        self.zoom_in_btn = QPushButton()
        self.zoom_in_btn.setIcon(QIcon("icons/zoomin_white.png" if self.is_dark_theme() else "icons/zoomin.png"))        
        self.zoom_in_btn.setFixedSize(50, 50)
        self.zoom_in_btn.setStyleSheet("padding: 5px;")
        self.zoom_in_btn.clicked.connect(self.zoom_in)   
        # Pulsante nav destra
        self.next_btn = QPushButton("→")
        self.next_btn.setFixedHeight(50)
        self.next_btn.setStyleSheet("padding: 5px;")
        self.next_btn.clicked.connect(self.next_image)
        # Aggiungi i pulsanti al layout
        btn_layout.addWidget(self.prev_btn)
        btn_layout.addWidget(self.zoom_out_btn)
        btn_layout.addWidget(self.zoom_reset_btn)
        btn_layout.addWidget(self.search_btn)
        btn_layout.addWidget(self.zoom_in_btn)        
        btn_layout.addWidget(self.next_btn)

        # Layout per i pulsanti di azione
        btn_act_layout = QHBoxLayout()
        self.layout.addLayout(btn_act_layout)  # Aggiungi il layout dei pulsanti di azione all'interfaccia
        # Pulsante Like
        self.like_btn = QPushButton()
        self.like_btn.setIcon(QIcon("icons/heart_empty_white.png" if self.is_dark_theme() else "icons/heart_empty.png"))        
        self.like_btn.setFixedSize(50, 50)
        self.like_btn.setStyleSheet("padding: 5px;")
        btn_act_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.like_btn.clicked.connect(self.toggle_like)
        # Pulsante Ruota
        self.rotate_btn = QPushButton()
        self.rotate_btn.setIcon(QIcon("icons/rotate_white.png" if self.is_dark_theme() else "icons/rotate.png"))
        self.rotate_btn.setFixedSize(50, 50)
        self.rotate_btn.setStyleSheet("padding: 5px;")
        btn_act_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.rotate_btn.clicked.connect(self.rotate_image)
        # Pulsante Fullscreen
        self.fullscreen_img_btn = QPushButton()
        self.fullscreen_img_btn.setIcon(QIcon("icons/fullscreen_white.png" if self.is_dark_theme() else "icons/fullscreen.png"))        
        self.fullscreen_img_btn.setFixedSize(50, 50)
        self.fullscreen_img_btn.setStyleSheet("padding: 5px;")
        self.fullscreen_img_btn.clicked.connect(self.toggle_image_fullscreen)
        # Pulsante Download
        self.dwn_btn = QPushButton()
        self.dwn_btn.setIcon(QIcon("icons/download_white.png" if self.is_dark_theme() else "icons/download.png"))        
        self.dwn_btn.setFixedSize(50, 50)
        self.dwn_btn.setStyleSheet("padding: 5px;")
        btn_act_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.dwn_btn.clicked.connect(self.download_images)
        # Pulsante Elimina
        self.del_btn = QPushButton()
        self.del_btn.setIcon(QIcon("icons/delete_white.png" if self.is_dark_theme() else "icons/delete.png"))
        self.del_btn.setFixedSize(50, 50)
        self.del_btn.setStyleSheet("padding: 5px;")
        btn_act_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.del_btn.clicked.connect(self.delete_images)
        # Pulsante Stampa
        self.print_btn = QPushButton()
        self.print_btn.setIcon(QIcon("icons/print_white.png" if self.is_dark_theme() else "icons/print.png"))
        self.print_btn.setFixedSize(50, 50)
        self.print_btn.setStyleSheet("padding: 5px;")
        btn_act_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.print_btn.clicked.connect(self.print_image)
        # Aggiungi i pulsanti al layout
        btn_act_layout.addWidget(self.like_btn)
        btn_act_layout.addWidget(self.rotate_btn)
        btn_act_layout.addWidget(self.fullscreen_img_btn)
        btn_act_layout.addWidget(self.dwn_btn)
        btn_act_layout.addWidget(self.del_btn)
        btn_act_layout.addWidget(self.print_btn)

        # Casella di input per nuova descrizione
        self.comment_input = QLineEdit()
        self.comment_input.setPlaceholderText("Aggiungi una descrizione...")
        self.comment_input.returnPressed.connect(self.add_comment)
        self.layout.addWidget(self.comment_input)
        # Casella di selezione multipla
        self.favorite_check = QCheckBox("Aggiungi alla selezione multipla")
        self.favorite_check.stateChanged.connect(self.toggle_favorite)
        self.layout.addWidget(self.favorite_check)

        # Variabili di stato
        self.image_paths = []  # Lista di percorsi delle immagini
        self.current_index = 0  # Indice dell'immagine corrente
        self.likes = {}  # Dizionario di like per le immagini
        self.comments = {}  # Dizionario di commenti per le immagini
        self.favorites = {}  # Dizionario di immagini preferite
        self.rotation_angle = 0  # Variabile per memorizzare l'angolo di rotazione dell'immagine
        self.selected_images = []  # Lista per tenere traccia delle immagini selezionate
        self.zoom_factor = 1.0    # Livello zoom attuale (1.0 = 100%)
        self.min_zoom = 0.1       # Livello zoom minimo (10%)
        self.max_zoom = 5.0       # Livello zoom massimo (500%)
        self.pan_start = None     # Per il movimento del mouse
        self.original_pixmap = None  # Salva temporaneamente l'immagine zoomata
        self.drag_start_pos = None
        self.image_offset = QPointF(0, 0)
        self.current_pixmap = None
        self.dragging = False
        self.zoom_factor = 1.0
        self.min_zoom = 0.1
        self.max_zoom = 5.0
        self.drag_start_pos = None
        self.dragging = False
        self._last_mouse_pos = None
        self.update_icons()

# METODI -------------------------------------------------------------------------------------------------------
    # CARICA IMMAGINI
    def load_images(self):
        files, _ = QFileDialog.getOpenFileNames(self, "Seleziona Immagini", "", "Images (*.png *.jpg *.jpeg)")
        if files: # Se sono state selezionate delle immagini
            for file in files: # per ogni immagine 
                if file not in self.image_paths: # se l'immagine non è nella lista
                    self.image_paths.append(file) # aggiunge nuove immagini alle esistenti, evitando duplicati
                    self.likes[file] = False  # aggiunge Like default
                    self.comments[file] = ""  # aggiunge descrizione vuota
                    self.favorites[len(self.image_paths)-1] = False # inizializza stato di preferito di default        
            # Se questo era il primo caricamento, aggiorna indice a 0
            self.current_index = len(self.image_paths) - 1
            self.update_display() # Aggiorna l'interfaccia con l'immagine corrente
    # RUOTA IMMAGINE -------------------------------------------------------------------------------------------
    def rotate_image(self):
        if not self.image_paths:
            return            
        self.rotation_angle = (self.rotation_angle + 90) % 360
        self._image_cache = {}
        self.update_display()
    # AGGIORNAMENTO INTERAFCCIA IMMAGINE CORRENTE --------------------------------------------------------------      
    def update_display(self):
        if self.image_paths:
            # Carica e ritaglia l'immagine originale
            pixmap = QPixmap(self.image_paths[self.current_index])
            min_side = min(pixmap.width(), pixmap.height())
            x_offset = (pixmap.width() - min_side) // 2
            y_offset = (pixmap.height() - min_side) // 2
            self.original_pixmap = pixmap.copy(x_offset, y_offset, min_side, min_side)            
            # in base a se è in fullscreen o meno, defnisci le dimensioni della finestra
            if self.is_image_fullscreen:
                display_size = min(self.screen().size().width(), self.screen().size().height())
            else:
                display_size = min(400, min_side)            
            # Crea versione ritagliata e scalata dell'immagine
            scaled_pixmap = self.original_pixmap.scaled(
                display_size, display_size,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation)
            if self.rotation_angle != 0:
                transform = QTransform().rotate(self.rotation_angle)
                scaled_pixmap = scaled_pixmap.transformed(transform)
            # Imposta pixmap e dimensioni
            self.image_label.setPixmap(scaled_pixmap)
            self.image_label.resize(scaled_pixmap.size())
            # Aggiorna elementi UI
            if not self.is_image_fullscreen:
                self.comment_box.setPlainText(self.comments.get(self.image_paths[self.current_index], ""))
                self.center_text_in_comment_box()
                self.favorite_check.setChecked(self.favorites.get(self.current_index, False))
                self.update_like_icon()
            self.update_image_details() # Mostra sia zoom che dettagli
            filename = os.path.basename(self.image_paths[self.current_index])
            self.setWindowTitle(f"Photo - {filename}")
            self.center_image()
    def center_image(self):
        if hasattr(self, 'scroll_area') and self.image_paths:
            h_bar = self.scroll_area.horizontalScrollBar()
            v_bar = self.scroll_area.verticalScrollBar()
            h_center = (h_bar.maximum() - h_bar.minimum()) // 2
            v_center = (v_bar.maximum() - v_bar.minimum()) // 2
            h_bar.setValue(h_center)
            v_bar.setValue(v_center)
    # RIDIMENSIONAMENTO FINESTRA -------------------------------------------------------------------------------
    def resizeEvent(self, event):
        self.update_display()
        super().resizeEvent(event)
    # IMMAGINE PRECEDENTE, FULLSCREEN E SUCCESSIVA --------------------------------------------------------------
    def prev_image(self):
        if self.image_paths and self.current_index > 0:
            self.current_index -= 1
            self.update_display()
    def next_image(self):
        if self.image_paths and self.current_index < len(self.image_paths) - 1:
            self.current_index += 1
            self.update_display()
    def toggle_image_fullscreen(self):
        if self.is_image_fullscreen:  # Uscita dalla modalità fullscreen
            self.is_image_fullscreen = False
            self.showNormal()
            # Mostra tutti gli elementi UI
            buttons_to_show = [
                self.like_btn,
                self.rotate_btn,
                self.dwn_btn,
                self.del_btn,
                self.print_btn,
                self.comment_box,
                self.comment_input,
                self.favorite_check]
            for btn in buttons_to_show:
                btn.show()
            self.layout.setContentsMargins(10, 10, 10, 10)
            self.setWindowState(Qt.WindowState.WindowNoState)
        else:  # Entrata in modalità fullscreen
            self.is_image_fullscreen = True
            self.showFullScreen()
            # Nasconde gli elementi UI indesiderati
            buttons_to_hide = [
                self.like_btn,
                self.rotate_btn,
                self.dwn_btn,
                self.del_btn,
                self.print_btn,
                self.comment_input,
                self.favorite_check]
            for btn in buttons_to_hide:
                btn.hide()
            self.layout.setContentsMargins(0, 0, 0, 0)
            self.update_display()
        self.update()
    # RICERCA VISIVA CON GOOGLE LENS ----------------------------------------------------------------------------
    def search_image(self):
        if not self.image_paths:
            QMessageBox.warning(self, "Attenzione", "Nessuna immagine da cercare.")
            return
        image_path = self.image_paths[self.current_index]
        client_id = "ec470077f964304"
        # Finestra di attesa
        self.loading_dialog = LoadingDialog(self, "Avvio ricerca visiva...")
        self.loading_dialog.show()
        # Setup del thread e uploader
        self.thread = QThread()
        self.uploader = ImgurUploader(image_path, client_id)
        self.uploader.moveToThread(self.thread)
        # Connessioni dei segnali
        self.thread.started.connect(self.uploader.run)
        self.uploader.finished.connect(self.upload_success)
        self.uploader.error.connect(self.upload_error)
        self.uploader.finished.connect(self.thread.quit)
        self.uploader.error.connect(self.thread.quit)
        self.uploader.finished.connect(self.uploader.deleteLater)
        self.uploader.error.connect(self.uploader.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.thread.start()
    def upload_success(self, img_url):
        self.loading_dialog.close()
        encoded_url = quote(img_url, safe='')
        lens_url = f"https://lens.google.com/uploadbyurl?url={encoded_url}"
        webbrowser.open_new_tab(lens_url)
    def upload_error(self, message):
        self.loading_dialog.close()
        QMessageBox.critical(self, "Errore", message)
    # GESTIONE DI EVENTI DEL MOUSE ------------------------------------------------------------------------------
    def mousePressEvent(self, event):
        if (event.button() == Qt.MouseButton.LeftButton and 
            self.image_paths and 
            self.zoom_factor > 1.0):
            self.drag_start_pos = event.pos()
            self.dragging = True
            self.setCursor(Qt.CursorShape.ClosedHandCursor)
        super().mousePressEvent(event)
    def mouseMoveEvent(self, event):
        if (self.dragging and 
            self.image_paths and 
            self.zoom_factor > 1.0 and
            self.drag_start_pos):
            delta = event.pos() - self.drag_start_pos
            self.drag_start_pos = event.pos()
            h_bar = self.scroll_area.horizontalScrollBar()
            v_bar = self.scroll_area.verticalScrollBar()
            h_bar.setValue(h_bar.value() - delta.x())
            v_bar.setValue(v_bar.value() - delta.y())
        super().mouseMoveEvent(event)
    def wheelEvent(self, event: QWheelEvent):
        if self.image_paths:
            modifiers = QApplication.keyboardModifiers()
            if modifiers == Qt.KeyboardModifier.ControlModifier:
                mouse_pos = event.position()                
                h_bar = self.scroll_area.horizontalScrollBar()
                v_bar = self.scroll_area.verticalScrollBar()
                old_h = h_bar.value()
                old_v = v_bar.value()                
                if event.angleDelta().y() > 0:
                    self.zoom_in()
                else:
                    self.zoom_out()                    
                if hasattr(self, 'current_pixmap') and self.current_pixmap:
                    img_center = QPointF(
                        self.current_pixmap.width() / 2,
                        self.current_pixmap.height() / 2)
                    zoom_center = mouse_pos - img_center
                    h_bar.setValue(int(zoom_center.x() * (self.zoom_factor - 1) + old_h))
                    v_bar.setValue(int(zoom_center.y() * (self.zoom_factor - 1) + old_v))
                event.accept()
            else:
                event.ignore()
    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and self.dragging:
            self.dragging = False
            self.setCursor(Qt.CursorShape.ArrowCursor)
        super().mouseReleaseEvent(event)
    def leaveEvent(self, event):
        if self.dragging:
            self.dragging = False
            self.setCursor(Qt.CursorShape.ArrowCursor)
        super().leaveEvent(event)
    # METODI ZOOM ------------------------------------------------------------------------------------------------
    def zoom_in(self):
        if self.image_paths:
            self.zoom_with_factor(1.1)
            self.update_image_details()
    def zoom_out(self):
        if self.image_paths:
            self.zoom_with_factor(0.9)
            self.update_image_details()
    def reset_zoom(self):
        if self.image_paths:
            self.zoom_factor = 1.0
            self.apply_zoom()
            self.center_image()
            self.update_image_details()
    def zoom_with_factor(self, factor):
        if not self.image_paths:
            return
        h_bar = self.scroll_area.horizontalScrollBar()
        v_bar = self.scroll_area.verticalScrollBar()
        old_h = h_bar.value()
        old_v = v_bar.value()
        viewport_center = self.scroll_area.viewport().rect().center()
        widget_center = self.image_label.mapFrom(self.scroll_area, viewport_center)
        new_zoom = self.zoom_factor * factor
        self.zoom_factor = max(self.min_zoom, min(new_zoom, self.max_zoom))
        self.apply_zoom()
        new_h = widget_center.x() * (self.zoom_factor - 1) + old_h
        new_v = widget_center.y() * (self.zoom_factor - 1) + old_v
        h_bar.setValue(int(new_h))
        v_bar.setValue(int(new_v))  
    def apply_zoom(self):
        if not self.image_paths or not self.original_pixmap:
            return
        try:
            base_size = min(400, min(self.original_pixmap.width(), self.original_pixmap.height()))
            scaled_size = int(base_size * self.zoom_factor)
            scaled_pixmap = self.original_pixmap.scaled(
                scaled_size, scaled_size,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            if self.rotation_angle != 0:
                transform = QTransform().rotate(self.rotation_angle)
                scaled_pixmap = scaled_pixmap.transformed(transform)
            self.current_pixmap = scaled_pixmap
            self.image_label.setPixmap(scaled_pixmap)
            self.image_label.resize(scaled_pixmap.size())
        except Exception as e:
            print(f"Error applying zoom: {str(e)}")
    # USCIRE DAL FULSCREEN CON ESC --------------------------------------------------------------------------------
    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key.Key_Escape and self.is_image_fullscreen:
            self.toggle_image_fullscreen()
        super().keyPressEvent(event)
    # AGGIUNGI/RIMUOVI LIKE
    def toggle_like(self):
        if self.image_paths:
            current_path = self.image_paths[self.current_index]
            self.likes[current_path] = not self.likes.get(current_path, False)
            self.update_like_icon()
            # Aggiorna anche lo stato nel dizionario dei preferiti se necessario
            if current_path in self.selected_images and not self.likes[current_path]:
                self.selected_images.remove(current_path)
                self.favorite_check.setChecked(False)     
    def update_like_icon(self):
        if self.image_paths:
            current_path = self.image_paths[self.current_index]
            is_liked = self.likes.get(current_path, False)
            icon = QIcon("icons/heart_filled_white.png" if self.is_dark_theme() else "icons/heart_filled.png") if is_liked else QIcon("icons/heart_empty_white.png" if self.is_dark_theme() else "icons/heart_empty.png")
            self.like_btn.setIcon(icon)
    # REGOLA ALTEZZA DELLA CASELLA DI TESTO IN BASE ALLA QUANTITA' DEL CONTENUTO ----------------------------------
    def adjust_textedit_height(self):
        doc = self.comment_box.document()
        new_height = int(doc.documentLayout().documentSize().height()) + 10
        max_height = 200
        self.comment_box.setFixedHeight(min(new_height, max_height))
    # CENTRA IL TESTO NELL'AREA DI TESTO --------------------------------------------------------------------------
    def center_text_in_comment_box(self):
        cursor = self.comment_box.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.Start) 
        cursor.movePosition(QTextCursor.MoveOperation.End, QTextCursor.MoveMode.KeepAnchor)
        format = QTextBlockFormat()
        format.setAlignment(Qt.AlignmentFlag.AlignCenter)
        cursor.mergeBlockFormat(format)
        cursor.movePosition(QTextCursor.MoveOperation.End)     
        self.comment_box.setTextCursor(cursor)
    # AGGIUNGI DESCRIZIONE (COMMENTO) -----------------------------------------------------------------------------
    def add_comment(self):
        comment = self.comment_input.text()  # Ottieni il testo dalla casella di input
        if not self.image_paths:  # Se la lista è vuota
            self.show_alert("Errore: Nessuna immagine caricata!")
            return
        if not comment.strip():  # Se il commento è vuoto o solo spazi
            self.show_alert("Errore: Il commento non può essere vuoto!")
            return
        if comment:
            self.comments[self.image_paths[self.current_index]] = comment  # Aggiorna il commento per l'immagine corrente
            self.comment_box.setPlainText(comment)  # Aggiorna la casella di testo con il nuovo commento
            self.center_text_in_comment_box()  # Centra il testo nel QTextEdit
            self.comment_input.clear()  # Cancella il testo dalla casella di input
    # SELEZIONE MULTIPLA -------------------------------------------------------------------------------------------
    def toggle_favorite(self):
        if self.image_paths:
            self.favorites[self.current_index] = self.favorite_check.isChecked() # Aggiorna lo stato del favorito dell'immagine corrente
            current_image = self.image_paths[self.current_index] # Aggiungi o rimuovi l'immagine corrente alla lista delle foto selzionate
            if self.favorite_check.isChecked():
                if current_image not in self.selected_images:
                    self.selected_images.append(current_image)
            else:
                if current_image in self.selected_images:
                    self.selected_images.remove(current_image)
            self.status_bar.showMessage(f"Immagini selezionate: {len(self.selected_images)}") # Aggiorna lo status bar
    # AGGIORNAMENTO INTERFACCIA QUANDO SI CAMBIA IMMAGINE ----------------------------------------------------------
    def update_ui(self):
        if self.image_paths:
            self.image_label.setPixmap(QPixmap(self.image_paths[self.current_index]))
            # Controlla se l'immagine è nei preferiti e aggiorna la checkbox
            self.favorite_check.blockSignals(True)  # Evita attivazione del segnale mentre aggiorniamo lo stato
            self.favorite_check.setChecked(self.favorites.get(self.current_index, False))
            self.favorite_check.blockSignals(False)  # Riattiva i segnali dopo l'aggiornamento
    # DOWNLOAD IMMAGINE ---------------------------------------------------------------------------------------------
    def download_images(self):
        # Se nessun'immagine è stata selezionata, scarica quella visualizzata
        if not self.selected_images:
            if not self.image_paths:
                QMessageBox.warning(self, "Attenzione", "Nessuna immagine da scaricare.")
                return
            images_to_download = [self.image_paths[self.current_index]] # Usa l'immagine corrente come quella da scaricare
        else:
            images_to_download = self.selected_images
        # Se l'immagine è una sola, salvala senza zippare
        if len(images_to_download) == 1:
            image_path = images_to_download[0]
            save_path, _ = QFileDialog.getSaveFileName(
                self,
                "Salva Immagine",
                os.path.basename(image_path),  # Default filename
                "Images (*.png *.jpg *.jpeg);;All Files (*)")            
            if save_path:
                try:
                    shutil.copy(image_path, save_path)
                    QMessageBox.information(self, "Download completato", f"Immagine salvata in:\n{save_path}")
                except Exception as e:
                    QMessageBox.critical(self, "Errore", f"Impossibile salvare l'immagine: {str(e)}")        
        else:  # Se le immagini sono molteplici, zippale
            save_path, _ = QFileDialog.getSaveFileName(
                self,
                "Salva Immagini come ZIP",
                "",
                "ZIP Files (*.zip);;All Files (*)")            
            if save_path:
                # Crea una dir temporanea per immagazzinare le foto prima di zipparle
                temp_dir = tempfile.mkdtemp()                
                try:
                    # Copia le immagini selezionate alla dir temporanea                
                    for i, image_path in enumerate(images_to_download):
                        shutil.copy(image_path, os.path.join(temp_dir, f"image_{i+1}{os.path.splitext(image_path)[1]}"))                    
                    # Crea un file zip
                    with zipfile.ZipFile(save_path, 'w') as zipf:
                        for root, dirs, files in os.walk(temp_dir):
                            for file in files:
                                zipf.write(os.path.join(root, file), os.path.basename(file))                    
                    QMessageBox.information(self, "Download completato", f"Immagini salvate in:\n{save_path}")                
                except Exception as e:
                    QMessageBox.critical(self, "Errore", f"Impossibile creare il file ZIP: {str(e)}")                
                finally:
                    # Ripulisci dir temporanea               
                    shutil.rmtree(temp_dir)
    # DELETE IMMAGINE ---------------------------------------------------------------------------------------------
    def delete_images(self):
        # Se non ci sono molteplici immagini selezionate, elimina la visualizzata
        if not self.selected_images:
            if not self.image_paths:
                QMessageBox.warning(self, "Attenzione", "Nessuna immagine da eliminare.")
                return
            images_to_delete = [self.image_paths[self.current_index]]
        else:
            images_to_delete = self.selected_images.copy()
        # Conferma eliminazione
        if len(images_to_delete) == 1:
            msg = f"Sei sicuro di voler eliminare l'immagine selezionata?\n\n{os.path.basename(images_to_delete[0])}"
        else:
            msg = f"Sei sicuro di voler eliminare {len(images_to_delete)} immagini selezionate?"
        reply = QMessageBox.question(
            self,
            "Conferma eliminazione",
            msg,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No)
        if reply != QMessageBox.StandardButton.Yes:
            return
        # Elimina
        deleted_count = 0
        failed_deletions = []
        for image_path in images_to_delete:
            try:
                # Rimuovi da liste interne se esistono
                if image_path in self.image_paths:
                    index = self.image_paths.index(image_path)
                    # Rimuovi da tutte le liste in modo sicuro
                    if index < len(self.image_paths):
                        del self.image_paths[index]
                    if image_path in self.likes:
                        del self.likes[image_path]
                    if index in self.favorites:
                        del self.favorites[index]
                    if image_path in self.comments:
                        del self.comments[image_path]                    
                    # Aggiorna l'indice se neccessario
                    if self.current_index >= len(self.image_paths):
                        self.current_index = max(0, len(self.image_paths) - 1)                
                deleted_count += 1
            except Exception as e:
                failed_deletions.append((os.path.basename(image_path), str(e)))
        # Mostra risultati
        if failed_deletions:
            error_msg = "\n".join([f"{name}: {error}" for name, error in failed_deletions])
            QMessageBox.warning(
                self,
                "Eliminazione parziale",
                f"{deleted_count} immagini eliminate con successo.\n\nErrori:\n{error_msg}")
        else:
            QMessageBox.information(
                self,
                "Operazione completata",
                f"{deleted_count} immagini eliminate con successo.")
        # Ripulisci selezione
        self.selected_images.clear()
        self.status_bar.showMessage(f"Immagini selezionate: 0")        
        # Aggiorna la vista
        if self.image_paths:
            self.update_display()
        else:
            self.image_label.clear()
            self.comment_box.clear()
            self.setWindowTitle("Photo")
    # STAMPA IMMAGINE -------------------------------------------------------------------------------------------------
    def print_image(self):
        if not self.image_paths:
            QMessageBox.warning(self, "Attenzione", "Nessuna immagine da stampare.")
            return
        printer = QPrinter(QPrinter.PrinterMode.HighResolution) # Crea stampa e dialogo di stampa
        print_dialog = QPrintDialog(printer, self)
        printer.setPageOrientation(QPageLayout.Orientation.Portrait) # Imposta valori di default della stampa
        printer.setFullPage(True)        
        if print_dialog.exec() == QPrintDialog.DialogCode.Accepted:
            try:
                pixmap = QPixmap(self.image_paths[self.current_index]) # Carica immagine corrente
                painter = QPainter() # Crea painter per gestire la stampa
                painter.begin(printer)                
                page_rect = printer.pageRect(QPrinter.Unit.DevicePixel) # Calcola dimensioni per mantenere il rapporto d'immagine
                pixmap_rect = pixmap.rect()
                # Scala la pixmap per addattarsi alla pagina mentre si mantiene il rapporto
                scale = min(page_rect.width() / pixmap_rect.width(),
                        page_rect.height() / pixmap_rect.height())
                painter.scale(scale, scale)
                painter.drawPixmap(0, 0, pixmap) # Imposta immagine centrata
                painter.end()                
                QMessageBox.information(self, "Stampa", "Immagine inviata alla stampante con successo!")
            except Exception as e:
                QMessageBox.critical(self, "Errore", f"Errore durante la stampa:\n{str(e)}")
    # AGGIORNAMENTO DETTAGLI DELL'IMMAGINE -------------------------------------------------------------------------------
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
            # Combina tutte le informazioni in un unico messaggio
            message = f"Zoom: {int(self.zoom_factor * 100)}% | Dimensioni originali: {width}x{height} px | Peso: {file_size_str}"
            self.status_bar.showMessage(message)
    # MESSAGGIO D'AVVISO -------------------------------------------------------------------------------------------------
    def show_alert(self, message):
        alert = QMessageBox()
        alert.setIcon(QMessageBox.Icon.Warning)
        alert.setWindowTitle("Errore")
        alert.setText(message)
        alert.setStandardButtons(QMessageBox.StandardButton.Ok)
        alert.exec()  # Mostra la finestra di dialogo
    # TEMI - CHIARO/SCURO ------------------------------------------------------------------------------------------------
    def set_light_theme(self):
        self.setStyleSheet("")        
        self.update_icons()
        self.update_display()
    def set_dark_theme(self):
        dark_stylesheet = """
            QMainWindow, QWidget {
                background-color: #2D2D2D;
                color: #FFFFFF;}
            QPushButton {
                background-color: #3A3A3A;
                border: 1px solid #555;
                color: #FFFFFF;
                padding: 5px;}
            QPushButton:hover {
                background-color: #4A4A4A;}
            QLineEdit, QTextEdit {
                background-color: #3A3A3A;
                color: #FFFFFF;
                border: 1px solid #555;}
            QCheckBox {
                color: #FFFFFF;
                spacing: 5px;}
            QCheckBox::indicator {
                border: 1px solid #555;
                background-color: #3A3A3A;}
            QCheckBox::indicator:checked {
                width: 12px;
                height: 12px;
                image: url(icons/checked_white.png);
                background-color: #4A4A4A;
                color: #FFFFFF;
                border: 1px solid #555;}
            QCheckBox::indicator:hover {
                border: 1px solid #CCCCCC;}
            QMenuBar {
                background-color: #2D2D2D;
                color: #FFFFFF;}
            QMenuBar::item:selected {
                background-color: #4A4A4A;}
            QMenu {
                background-color: #3A3A3A;
                color: #FFFFFF;}
            QMenu::item:selected {
                background-color: #4A4A4A;}
            QStatusBar {
                background-color: #2D2D2D;
                color: #FFFFFF;}
        """
        self.setStyleSheet(dark_stylesheet)
        self.update_icons()
        self.update_display()
    # AGGIORNAMENTO ICONE IN BASE AL TEMA SCELTO ---------------------------------------------------------------------------
    def update_icons(self):
        is_dark = self.is_dark_theme()
        if self.image_paths:
            current_path = self.image_paths[self.current_index]
            is_liked = self.likes.get(current_path, False)
            like_state = "_filled" if is_liked else "_empty"
            self.like_btn.setIcon(QIcon(f"icons/heart{like_state}_white.png" if is_dark else f"icons/heart{like_state}.png"))
        else:
            self.like_btn.setIcon(QIcon("icons/heart_empty_white.png" if is_dark else "icons/heart_empty.png"))  
        btn_icons = {
            self.rotate_btn: "rotate",
            self.dwn_btn: "download",
            self.del_btn: "delete",
            self.print_btn: "print",
            self.fullscreen_img_btn: "fullscreen",
            self.zoom_in_btn: "zoomin",
            self.zoom_out_btn: "zoomout",
            self.search_btn: "search"
        }    
        for btn, icon_name in btn_icons.items():
            btn.setIcon(QIcon(f"icons/{icon_name}_white.png" if is_dark else f"icons/{icon_name}.png"))
    def is_dark_theme(self):
        return self.palette().window().color().lightness() < 128



if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Photo()
    window.show()
    sys.exit(app.exec())
