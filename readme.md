ITS Adriano Olivetti
DevOps 2024/2026
Tutor: Ing. Stefano Castagnoli
**Project Work**

## Italiano

### Descrizione
Photo Gallery è un'applicazione desktop per visualizzare e gestire collezioni di immagini. Offre funzionalità come zoom, rotazione, like, descrizioni, selezione multipla e molto altro.

### Funzionalità principali
1. **Caricamento immagini**: Supporta PNG, JPG, JPEG
2. **Navigazione**: Scorri tra le immagini con pulsanti "←" e "→"
3. **Zoom**: 
   - Zoom in/out con pulsanti o rotellina mouse (Ctrl+Rotellina)
   - Reset zoom con pulsante "1:1"
4. **Rotazione**: Ruota immagini di 90° alla volta
5. **Like**: Aggiungi/rimuovi cuore alle immagini preferite
6. **Commenti**: Aggiungi descrizioni testuali alle immagini
7. **Selezione multipla**: Seleziona più immagini per azioni batch
8. **Download**:
   - Salva singola immagine
   - Crea ZIP per più immagini
9. **Eliminazione**: Rimuovi immagini singole o multiple
10. **Stampa**: Stampa direttamente le immagini
11. **Temi**: Interfaccia chiara/scura personalizzabile
12. **Fullscreen**: Modalità a schermo intero per la visualizzazione

### Tasti rapidi
- `Esc`: Esci dalla modalità fullscreen
- `Ctrl+Rotellina mouse`: Zoom in/out

### Requisiti di sistema
- Python 3.x
- Librerie richieste: PyQt6

### Installazione
1. Installa Python 3.x
2. Installa le dipendenze: `pip install PyQt6`
3. Esegui l'applicazione: `python photo_gallery.py`

### Utilizzo
1. Carica immagini tramite il menu "File" > "Carica Immagini"
2. Naviga tra le immagini con i pulsanti di navigazione
3. Usa i vari pulsanti per modificare, commentare o gestire le immagini
4. Seleziona più immagini con la checkbox per operazioni multiple

### Note Aggiuntive
- L'applicazione include una barra di stato che mostra i dettagli dell'immagine
- Tutte le azioni sono reversibili (eccetto l'eliminazione permanente)
- Le icone si adattano automaticamente al tema selezionato
- L'interfaccia è reattiva e si adatta alle dimensioni della finestra

## English

### Description
Photo Gallery is a desktop application for viewing and managing image collections. It offers features like zoom, rotation, likes, descriptions, multi-selection and more.

### Main Features
1. **Image loading**: Supports PNG, JPG, JPEG
2. **Navigation**: Browse images with "←" and "→" buttons
3. **Zoom**:
   - Zoom in/out with buttons or mouse wheel (Ctrl+Wheel)
   - Reset zoom with "1:1" button
4. **Rotation**: Rotate images 90° at a time
5. **Likes**: Add/remove heart to favorite images
6. **Comments**: Add text descriptions to images
7. **Multi-selection**: Select multiple images for batch actions
8. **Download**:
   - Save single image
   - Create ZIP for multiple images
9. **Deletion**: Remove single or multiple images
10. **Printing**: Directly print images
11. **Themes**: Customizable light/dark interface
12. **Fullscreen**: Fullscreen viewing mode

### Keyboard Shortcuts
- `Esc`: Exit fullscreen mode
- `Ctrl+Mouse Wheel`: Zoom in/out

### System Requirements
- Python 3.x
- Required libraries: PyQt6

### Installation
1. Install Python 3.x
2. Install dependencies: `pip install PyQt6`
3. Run the application: `python photo_gallery.py`

### Usage
1. Load images via "File" > "Load Images" menu
2. Browse images with navigation buttons
3. Use various buttons to modify, comment or manage images
4. Select multiple images with checkbox for batch operations

### Additional Notes
- The application includes a status bar showing image details
- All actions are reversible (except permanent deletion)
- Icons automatically adapt to the selected theme
- The interface is responsive and adjusts to window size changes
