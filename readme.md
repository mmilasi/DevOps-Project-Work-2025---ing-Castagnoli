# Project Work
ITS Adriano Olivetti - DevOps 2024/2026 - Tutor: Ing. Stefano Castagnoli

# Italiano

### Obbiettivo e Workflow
#### Obbiettivo
L'obbiettivo del Project Work è la creazione di una GUI per la visualizzazione di immagini in linguaggio Python.
I requisiti minimi richiesti dal professore sono i seguenti:
- Area di testo
- Barra di stato
- Bottoni
- Casella di testo
- Caselle di selezione
- Finestre di dialogo (apri/salva file)
- Menù

La finestra e la posizione dei controlli dovranno adattarsi automaticamente in seguito alla modifica della dimensione della finestra stessa​.

#### Workflow
**1. Definizione schematica dell'UI richiesta con utilizzo di Canva**
<img src="https://i.imgur.com/dIOPddf.png" style="width: 80%; padding: 10px; display: block; margin: auto;">

**2. Valutazione e scelta di Framework**

Dopo aver valutato **Tkinter, Kivy e PyQt,** ho scelto di utilizzare **PyQt** per lo sviluppo della mia app.

Tkinter, pur essendo incluso in Python e semplice da usare, ha un'interfaccia grafica datata e limitata, con pochi widget avanzati. La sua estetica poco moderna non si adattava alla qualità visiva che volevo ottenere.

Kivy, invece, è più orientato al mobile e a interfacce touch. Nonostante sia flessibile e moderno, non offre un look & feel nativo su desktop e può risultare meno intuitivo per applicazioni tradizionali.

PyQt, al contrario, offre un'interfaccia grafica moderna, un set completo di widget professionali e un'ottima documentazione. La presenza di numerosi esempi pratici e una community attiva lo rendono ideale per progetti desktop complessi. Inoltre, la possibilità di personalizzare facilmente lo stile ha contribuito a soddisfare le mie esigenze estetiche, nettamente superiori rispetto a quanto offerto da Tkinter.
In sintesi, ritengo che PyQt rappresenta la scelta più completa ed equilibrata tra funzionalità, estetica e supporto.

### Applicazione
Photo Gallery è un'applicazione desktop per visualizzare e gestire collezioni di immagini. Offre funzionalità come zoom, rotazione, like, descrizioni, selezione multipla, ricerca visiva e molto altro.

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
13. **Ricerca visiva**: Ricerca l'immagine corrente su Google Lens  

### Tasti rapidi
 - `Esc`: Esci dalla modalità fullscreen  
 - `Ctrl+Rotellina mouse`: Zoom in/out  

### Requisiti di sistema
 - Python 3.x  
 - Librerie richieste: PyQt6  
 - Connessione internet attiva per la funzione di ricerca visiva  

### Installazione
 1. Installa Python 3.x  
 2. Installa le dipendenze: `pip install -r requirements.txt`   
 3. Esegui l'applicazione: `python photo_gallery.py`  

### Utilizzo
 1. Carica immagini tramite il menu "File" > "Carica Immagini"  
 2. Naviga tra le immagini con i pulsanti di navigazione  
 3. Usa i vari pulsanti per modificare, commentare o gestire le immagini  
 4. Seleziona più immagini con la checkbox per operazioni multiple  
 5. Clicca "Ricerca Visiva" per cercare l'immagine su Google Lens  

### Note Aggiuntive
 - L'applicazione include una barra di stato che mostra i dettagli dell'immagine  
 - Le icone si adattano automaticamente al tema selezionato  
 - L'interfaccia è reattiva e si adatta alle dimensioni della finestra  
 - La ricerca visiva richiede una connessione internet funzionante  

# English

### Objective and Workflow
#### Objective
The goal of the Project Work is the creation of a GUI for image visualization using the Python programming language.  
The minimum requirements set by the professor are as follows:  
- Text area  
- Status bar  
- Buttons  
- Text box  
- Check boxes  
- Dialog windows (open/save file)  
- Menu  

The window and the position of the controls must adjust automatically when the window is resized.

#### Workflow
**1. Required UI graphical definition using Canva**  
<img src="https://i.imgur.com/83KMrWe.png" style="width: 80%; padding: 10px; display: block; margin: auto;">

**2. Evaluation and choice of Framework**

After evaluating **Tkinter, Kivy, and PyQt**, I chose to use **PyQt** for the development of my app.

Tkinter, although included in Python and easy to use, has an outdated and limited graphical interface, with few advanced widgets. Its outdated aesthetics did not match the visual quality I wanted to achieve.

Kivy, on the other hand, is more mobile and touch interfaces oriented. Although it is flexible and modern, it does not offer a native desktop look & feel and may be less intuitive for traditional applications.

PyQt, on the other hand, offers a modern graphical interface, a full set of professional widgets, and excellent documentation. The presence of numerous practical examples and an active community makes it ideal for complex desktop projects. Moreover, the possibility to easily customize the style helped meet my aesthetic needs, which are far superior compared to what Tkinter offers.

Long story short, I believe PyQt is the most complete and balanced choice in terms of functionality, aesthetics, and support!

### Description
Photo Gallery is a desktop application for viewing and managing image collections. It offers features like zoom, rotation, likes, descriptions, multi-selection, visual search and more.

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
 13. **Visual Search**: Search current image using Google Lens  

### Keyboard Shortcuts
 - `Esc`: Exit fullscreen mode  
 - `Ctrl+Mouse Wheel`: Zoom in/out  

### System Requirements
 - Python 3.x  
 - Required libraries: PyQt6  
 - Active internet connection for visual search feature  

### Installation
 1. Install Python 3.x  
 2. Install dependencies: `pip install -r requirements.txt`  
 3. Run the application: `python photo_gallery.py`  

### Usage
 1. Load images via "File" > "Load Images" menu  
 2. Browse images with navigation buttons  
 3. Use various buttons to modify, comment or manage images  
 4. Select multiple images with checkbox for batch operations  
 5. Click "Visual Search" to search image on Google Lens  

### Additional Notes
 - The application includes a status bar showing image details  
 - Icons automatically adapt to the selected theme  
 - The interface is responsive and adjusts to window size changes  
 - Visual search requires working internet connection  