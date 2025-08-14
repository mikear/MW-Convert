import sys
import os
import subprocess
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton, QLabel, QMessageBox, QFileDialog, QHBoxLayout, QGroupBox, QMenuBar, QMenu, QDialog, QTextBrowser, QProgressBar
)
from PySide6.QtGui import QDesktopServices, QIcon, QAction
from PySide6.QtCore import Qt, QUrl, QThread, Signal, QObject, QSize
import main

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

class Worker(QObject):
    finished = Signal(str)
    error = Signal(str)
    started = Signal()

    def __init__(self, input_md_path, template_path):
        super().__init__()
        self.input_md_path = input_md_path
        self.template_path = template_path

    def run(self):
        self.started.emit()
        try:
            output_docx_path = main.convert_md_to_docx(self.input_md_path, reference_docx_path=self.template_path)
            if output_docx_path:
                self.finished.emit(output_docx_path)
            else:
                self.error.emit("La conversión falló. Revise la consola para más detalles.")
        except Exception as e:
            self.error.emit(f"Error durante la conversión: {str(e)}")

class MarkdownConverterApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MW Convert")
        self.setGeometry(100, 100, 400, 450)
        self.setWindowIcon(QIcon(resource_path('icons/app_icon.ico')))

        

        # Global stylesheet for a modern dark theme
        # Global stylesheet for a modern dark theme
        app.setStyleSheet("""
            QMainWindow {
                background-color: #2b2b2b; /* Slightly lighter dark background for the main window */
                color: #f0f0f0;
            }
            QLabel {
                color: #f0f0f0;
            }
            QGroupBox {
                background-color: #3c3c3c; /* Darker background for group boxes */
                border: 2px solid #6495ED;
                border-radius: 5px;
                margin-top: 1ex;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top center;
                padding: 0 3px;
                background-color: #555;
                color: #f0f0f0;
                border-radius: 3px;
            }
            QPushButton {
                background-color: #336699;
                border: 1px solid #4477AA;
                border-radius: 5px;
                color: #f0f0f0;
                padding: 8px 15px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #6495ED;
                border: 1px solid #ADD8E6;
            }
            QPushButton:pressed {
                background-color: #4169E1;
                border: 1px solid #ADD8E6;
            }
            QPushButton:disabled {
                background-color: #444;
                color: #888;
                border: 1px solid #555;
            }
            QMenuBar {
                background-color: #3c3c3c;
                color: #f0f0f0;
            }
            QMenuBar::item {
                background-color: #3c3c3c;
                color: #f0f0f0;
            }
            QMenuBar::item:selected {
                background-color: #555;
            }
            QMenu {
                background-color: #3c3c3c;
                color: #f0f0f0;
                border: 1px solid #555;
            }
            QMenu::item:selected {
                background-color: #555;
            }
            QTextBrowser {
                background-color: #3c3c3c;
                color: #f0f0f0;
                border: 1px solid #555;
            }
            QTextBrowser a {
                color: #FFFFFF; /* White for all links */
            }
            QTextBrowser a:hover {
                color: #ADD8E6; /* Light blue on hover */
            }
            QProgressBar {
                text-align: center;
                color: #f0f0f0;
                background-color: #3c3c3c;
                border: 1px solid #555;
                border-radius: 5px;
            }
            QProgressBar::chunk {
                background-color: #6495ED;
                border-radius: 5px;
            }
        """)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout()
        self.central_widget.setLayout(self.layout)

        self.create_menu_bar()

        self.new_project_button = QPushButton("Nuevo Proyecto")
        self.new_project_button.setIcon(QIcon(resource_path('icons/document_new_open.png')))
        self.new_project_button.clicked.connect(self.reset_application_state)
        self.new_project_button.setEnabled(False)
        self.layout.addWidget(self.new_project_button)

        # The global stylesheet will handle most button styles,
        # but we can keep specific adjustments if needed.
        # For now, remove the specific new_project_button_style
        # as it will be covered by the global QPushButton style.
        # self.new_project_button.setStyleSheet(new_project_button_style)

        self.setAcceptDrops(True)
        self.current_md_path = None
        self.output_docx_path = None  # Para abrir/carpeta

        # Group 1: Markdown File Selection
        markdown_group = QGroupBox("Paso 1: Selección de Archivo Markdown")
        markdown_layout = QVBoxLayout()

        self.browse_button = QPushButton("Buscar archivo .md")
        self.browse_button.setIcon(QIcon(resource_path('icons/search.png')))
        self.browse_button.clicked.connect(self.browse_file)
        markdown_layout.addWidget(self.browse_button)

        self.drop_area_label = QLabel("Arrastre y suelte su archivo .md aquí")
        self.drop_area_label.setAlignment(Qt.AlignCenter)
        self.drop_area_label.setStyleSheet("QLabel { border: 2px dashed #aaa; border-radius: 5px; background-color: #333; padding: 20px; }")
        markdown_layout.addWidget(self.drop_area_label)
        markdown_group.setLayout(markdown_layout)
        self.layout.addWidget(markdown_group)

        # Group 2: DOCX Template Selection (Opcional)
        self.template_group = QGroupBox("Paso 2: Selección de Plantilla DOCX (Opcional)")
        template_layout = QVBoxLayout()
        self.template_group.setEnabled(False)

        self.template_path = None
        self.template_path_label = QLabel("Plantilla seleccionada: Ninguna")
        self.template_path_label.setAlignment(Qt.AlignCenter)
        template_layout.addWidget(self.template_path_label)

        template_button_layout = QHBoxLayout()
        self.select_template_button = QPushButton("Seleccionar Plantilla DOCX")
        self.select_template_button.setIcon(QIcon(resource_path('icons/file.png')))
        self.select_template_button.clicked.connect(self.select_template_file)
        template_button_layout.addWidget(self.select_template_button)

        self.clear_template_button = QPushButton()
        self.clear_template_button.setIcon(QIcon(resource_path('icons/clear_error.png')))
        self.clear_template_button.setFixedSize(32, 32)
        self.clear_template_button.clicked.connect(self.clear_template_selection)
        self.clear_template_button.hide()
        template_button_layout.addWidget(self.clear_template_button)
        template_layout.addLayout(template_button_layout)
        self.template_group.setLayout(template_layout)
        self.layout.addWidget(self.template_group)

        # Convert Button
        self.convert_button = QPushButton("Convertir a DOCX")
        self.convert_button.setIcon(QIcon(resource_path('icons/convert_about.png')))
        self.convert_button.clicked.connect(self.convert_selected_file)
        self.convert_button.setEnabled(False)
        self.layout.addWidget(self.convert_button)

        # Group 3: Status and Output Actions
        self.output_group = QGroupBox("Paso 3: Estado y Acciones de Salida")
        output_layout = QVBoxLayout()
        self.output_group.setEnabled(False)

        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignCenter)
        output_layout.addWidget(self.status_label)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)
        self.progress_bar.hide()
        output_layout.addWidget(self.progress_bar)

        output_layout.addStretch(1)

        self.open_file_button = QPushButton("Abrir documento")
        self.open_file_button.setIcon(QIcon(resource_path('icons/docx.ico')))
        self.open_file_button.setEnabled(False)
        self.open_file_button.clicked.connect(self.open_output_file)
        output_layout.addWidget(self.open_file_button)

        self.open_folder_button = QPushButton("Ver en carpeta")
        self.open_folder_button.setIcon(QIcon(resource_path('icons/folder_open.png')))
        self.open_folder_button.setEnabled(False)
        self.open_folder_button.clicked.connect(self.open_output_folder)
        output_layout.addWidget(self.open_folder_button)
        self.output_group.setLayout(output_layout)
        self.layout.addWidget(self.output_group)

        # Developed by and LinkedIn link
        app_info_label = QLabel("MW Convert v1.3 (2025)")
        app_info_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(app_info_label)

        developer_info_layout = QHBoxLayout()
        developer_info_layout.setAlignment(Qt.AlignCenter)

        developed_by_label = QLabel("Desarrollado por Diego A. Rábalo")
        developer_info_layout.addWidget(developed_by_label)

        github_url = "https://github.com/mikear"
        github_icon_path = resource_path('icons/github.png')
        github_button = QPushButton(QIcon(github_icon_path), "")
        github_button.setFixedSize(24, 24)
        github_button.setIconSize(QSize(16, 16))
        github_button.setFlat(True)
        github_button.clicked.connect(lambda: QDesktopServices.openUrl(QUrl(github_url)))
        developer_info_layout.addWidget(github_button)

        linkedin_url = "https://www.linkedin.com/in/rabalo?lipi=urn%3Ali%3Apage%3Ad_flagship3_profile_view_base_contact_details%3BYmE7N4DBTRqMk9Vla0BdWQ%3D%3D"
        linkedin_icon_path = resource_path('icons/linkedin.ico')
        linkedin_button = QPushButton(QIcon(linkedin_icon_path), "") # Empty text, only icon
        linkedin_button.setFixedSize(24, 24) # Set a fixed size for the button
        linkedin_button.setIconSize(QSize(16, 16)) # Set icon size
        linkedin_button.setFlat(True) # Make background transparent
        linkedin_button.clicked.connect(lambda: QDesktopServices.openUrl(QUrl(linkedin_url)))
        developer_info_layout.addWidget(linkedin_button)

        self.layout.addLayout(developer_info_layout)

        

    

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls() and self.childAt(event.pos()) == self.drop_area_label:
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event):
        if self.childAt(event.pos()) == self.drop_area_label:
            for url in event.mimeData().urls():
                file_path = url.toLocalFile()
                if file_path.endswith('.md'):
                    self.current_md_path = file_path
                    self.drop_area_label.setText(f"Archivo seleccionado: {os.path.basename(file_path)}")
                    self.convert_button.setEnabled(True)
                    self.template_group.setEnabled(True) # Enable template selection
                    self.new_project_button.setEnabled(False)
                    self.status_label.setText("")
                    self.open_file_button.setEnabled(False)
                    self.open_folder_button.setEnabled(False)
                    self.output_group.setEnabled(False) # Disable output group until conversion
                    break
            event.acceptProposedAction()
        else:
            event.ignore()

    def browse_file(self):
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(self, "Seleccionar archivo Markdown", "", "Archivos Markdown (*.md)")
        if file_path:
            self.current_md_path = file_path
            self.drop_area_label.setText(f"Archivo seleccionado: {os.path.basename(file_path)}")
            self.convert_button.setEnabled(True)
            self.template_group.setEnabled(True) # Enable template selection
            self.new_project_button.setEnabled(False)
            self.status_label.setText("")
            self.open_file_button.setEnabled(False)
            self.open_folder_button.setEnabled(False)
            self.output_group.setEnabled(False) # Disable output group until conversion

    def select_template_file(self):
        file_dialog = QFileDialog()
        template_path, _ = file_dialog.getOpenFileName(self, "Seleccionar Plantilla DOCX", "", "Archivos DOCX (*.docx)")
        if template_path:
            self.template_path = template_path
            self.template_path_label.setText(f"Plantilla seleccionada: {os.path.basename(template_path)}")
            self.clear_template_button.show()
        else:
            self.template_path = None
            self.template_path_label.setText("Plantilla seleccionada: Ninguna")
            self.clear_template_button.hide()

    def clear_template_selection(self):
        self.template_path = None
        self.template_path_label.setText("Plantilla seleccionada: Ninguna")
        self.clear_template_button.hide()

    def _perform_conversion(self, input_md_path):
        self.status_label.setText(f"Convirtiendo {os.path.basename(input_md_path)}...")
        QApplication.processEvents()
        self.progress_bar.show()
        self.status_label.setText("")

        self.thread = QThread()
        self.worker = Worker(input_md_path, self.template_path)
        self.worker.moveToThread(self.thread)

        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self._on_conversion_finished)
        self.worker.error.connect(self._on_conversion_error)

        self.thread.start()

    def _on_conversion_finished(self, output_docx_path):
        self.progress_bar.hide()
        self.status_label.setText(f"¡Conversión exitosa! Salida: {os.path.basename(output_docx_path)}")
        self.output_docx_path = output_docx_path
        self.open_file_button.setEnabled(True)
        self.open_folder_button.setEnabled(True)
        self.output_group.setEnabled(True) # Enable output group after successful conversion
        self.new_project_button.setEnabled(True)
        self.convert_button.setEnabled(False)
        self.thread.quit()
        self.thread.wait()
        self.worker.deleteLater()
        self.thread.deleteLater()

    def _on_conversion_error(self, error_message):
        self.progress_bar.hide()
        self.status_label.setText(error_message)
        self.open_file_button.setEnabled(False)
        self.open_folder_button.setEnabled(False)
        self.new_project_button.setEnabled(False)
        self.convert_button.setEnabled(True)
        self.thread.quit()
        self.thread.wait()
        self.worker.deleteLater()
        self.thread.deleteLater()

    def open_output_file(self):
        if self.output_docx_path and os.path.exists(self.output_docx_path):
            QDesktopServices.openUrl(QUrl.fromLocalFile(self.output_docx_path))

    def open_output_folder(self):
        if self.output_docx_path and os.path.exists(self.output_docx_path):
            QDesktopServices.openUrl(QUrl.fromLocalFile(os.path.dirname(self.output_docx_path)))

    def convert_selected_file(self):
        if self.current_md_path:
            self._perform_conversion(self.current_md_path)
        else:
            QMessageBox.warning(self, "Advertencia", "Por favor, seleccione un archivo Markdown primero.")

    def reset_application_state(self):
        self.current_md_path = None
        self.output_docx_path = None
        self.template_path = None
        self.template_path_label.setText("Plantilla seleccionada: Ninguna")
        self.clear_template_button.hide()
        self.status_label.setText("")
        self.open_file_button.setEnabled(False)
        self.open_folder_button.setEnabled(False)
        self.new_project_button.setEnabled(False)
        self.convert_button.setEnabled(False)
        self.template_group.setEnabled(False) # Disable template group
        self.output_group.setEnabled(False) # Disable output group
        self.drop_area_label.setText("Arrastre y suelte su archivo .md aquí")

    def create_menu_bar(self):
        menu_bar = self.menuBar()

        file_menu = menu_bar.addMenu("Archivo")
        new_project_action = QAction(QIcon(resource_path('icons/document_new_open.png')), "Nuevo Proyecto", self)
        new_project_action.triggered.connect(self.reset_application_state)
        file_menu.addAction(new_project_action)

        exit_action = QAction("Salir", self)
        exit_action.triggered.connect(QApplication.quit)
        file_menu.addAction(exit_action)

        help_menu = menu_bar.addMenu("Ayuda")
        help_manual_action = QAction(QIcon(resource_path('icons/help_info.png')), "Manual de Ayuda", self)
        help_manual_action.triggered.connect(self.show_help_manual)
        help_menu.addAction(help_manual_action)

        about_action = QAction(QIcon(resource_path('icons/about.png')), "Acerca de", self)
        about_action.triggered.connect(self.show_about_dialog)
        help_menu.addAction(about_action)

        contribute_menu = menu_bar.addMenu("Contribuir")
        share_action = QAction(QIcon(resource_path('icons/linkedin.ico')), "Compartir en LinkedIn", self)
        share_action.triggered.connect(self.share_on_linkedin)
        contribute_menu.addAction(share_action)

        donate_action = QAction(QIcon(os.path.join(os.path.dirname(__file__), 'icons/paypal.png')), "Donar", self)
        donate_action.triggered.connect(self.open_paypal_link)
        contribute_menu.addAction(donate_action)

    def convert_from_menu(self):
        QMessageBox.information(self, "Convertir", "La función de convertir desde el menú se implementará aquí.")

    def show_about_dialog(self):
        about_dialog = QDialog(self)
        about_dialog.setWindowTitle("Acerca de")
        about_dialog.setGeometry(250, 250, 450, 350)

        layout = QVBoxLayout()
        text_browser = QTextBrowser()
        text_browser.setOpenExternalLinks(True)
        text_browser.setStyleSheet("""
            QTextBrowser {
                background-color: #FFFFFF; /* White background */
                color: #000000; /* Black text */
            }
            a {
                color: #0000FF; /* Blue for links */
            }
            a:hover {
                color: #0000AA; /* Darker blue on hover */
            }
        """)
        text_browser.setHtml("""
            <p><b>MW Convert v1.3</b></p>
            <p>Desarrollado por Diego A. Rábalo</p>
            <p><b>Contacto:</b></p>
            <ul>
                <li><img src="icons/github.png" width="16" height="16" style="vertical-align: middle;"/> <a href="https://github.com/mikear">GitHub</a></li>
                <li><img src="icons/linkedin.ico" width=\"16\" height=\"16\" style=\"vertical-align: middle;"/> <a href=\"https://www.linkedin.com/in/rabalo\">LinkedIn</a></li>
                <li><a href=\"mailto:diego_rabalo@hotmail.com\">diego_rabalo@hotmail.com</a></li>
            </ul>
            <p><b>Notas de la Versión 1.3:</b></p>
            <ul>
                <li>Se optimizó la interfaz de usuario (GUI) para una mejor experiencia de usuario (UX).</li>
                <li>Se optimizó y minimizó el tamaño de la aplicación.</li>
            </ul>
            <p><b>Notas de la Versión 1.2:</b></p>
            <ul>
                <li>Corrección de errores críticos en el formateo de listas, código y otros elementos de Markdown.</li>
                <li>Se migró el motor de conversión a la librería `pypandoc` para mayor estabilidad y precisión.</li>
                <li>Actualización de la información de contacto y créditos.</li>
            </ul>
            <p><b>Créditos y Agradecimientos:</b></p>
            <ul>
                <li>A <b>The Qt Company</b> por el framework <a href=\"https://www.qt.io/product/qt6/pyside6\">PySide6</a>.</li>
                <li>A <b>Juho Vepsäläinen</b> (creador) y <b>Jessica Tegner</b> (mantenedora) por la librería <a href=\"https://github.com/JessicaTegner/pypandoc\">pypandoc</a>.</li>
            </ul>
        """)
        layout.addWidget(text_browser)

        close_button = QPushButton("Cerrar")
        close_button.clicked.connect(about_dialog.accept)
        layout.addWidget(close_button)

        about_dialog.setLayout(layout)
        about_dialog.exec()

    def show_help_manual(self):
        help_dialog = QDialog(self)
        help_dialog.setWindowTitle("Manual de Ayuda")
        help_dialog.setGeometry(200, 200, 700, 600)

        layout = QVBoxLayout()
        text_browser = QTextBrowser()
        text_browser.setStyleSheet("""
            QTextBrowser {
                background-color: #FFFFFF; /* White background */
                color: #000000; /* Black text */
            }
            a {
                color: #0000FF; /* Blue for links */
            }
            a:hover {
                color: #0000AA; /* Darker blue on hover */
            }
        """)

        manual_path = os.path.join(os.path.dirname(__file__), 'manual.html')
        if os.path.exists(manual_path):
            with open(manual_path, 'r', encoding='utf-8') as f:
                text_browser.setHtml(f.read())
        else:
            text_browser.setPlainText("Error: Manual de ayuda no encontrado.")

        layout.addWidget(text_browser)

        close_button = QPushButton("Cerrar")
        close_button.clicked.connect(help_dialog.accept)
        layout.addWidget(close_button)

        help_dialog.setLayout(layout)
        help_dialog.exec()

    def share_on_linkedin(self):
        app_details = "🚀 ¡Acabo de usar una increíble app para convertir Markdown a DOCX! 📄✨ Permite estilos personalizados con plantillas DOCX. ¡Súper útil para documentos profesionales y académicos! #Markdown #DOCX #Productividad #Pandoc"
        creator_info = "Desarrollado por Diego A. Rábalo"
        linkedin_profile = "https://www.linkedin.com/in/rabalo"

        import urllib.parse
        share_text = urllib.parse.quote_plus(f"{app_details}\n\n{creator_info}\n\nConoce más sobre el desarrollo y otras herramientas en mi perfil: {linkedin_profile}")

        linkedin_share_url = f"https://www.linkedin.com/sharing/share-offsite/?url={urllib.parse.quote_plus(linkedin_profile)}&title={share_text}"

        QDesktopServices.openUrl(QUrl(linkedin_share_url))

    def open_paypal_link(self):
        paypal_url = "https://paypal.me/diegorabalo"
        QDesktopServices.openUrl(QUrl(paypal_url))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MarkdownConverterApp()
    window.show()
    sys.exit(app.exec())