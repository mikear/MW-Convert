"""
Improved GUI application for MW Convert.

This module provides a modern, well-structured GUI for converting Markdown files
to DOCX format with proper error handling, logging, and separation of concerns.
"""

import logging
import os
import sys
import urllib.parse
from pathlib import Path
from typing import Optional

from PySide6.QtCore import QObject, QSize, Qt, QThread, QUrl, Signal
from PySide6.QtGui import QAction, QDesktopServices, QIcon
from PySide6.QtWidgets import (
    QApplication,
    QDialog,
    QFileDialog,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QTextBrowser,
    QVBoxLayout,
    QWidget,
)

from main import ConversionError, ValidationError, convert_md_to_docx, setup_logging

# Configure logging for GUI
logger = logging.getLogger(__name__)


def resource_path(relative_path: str) -> str:
    """
    Get absolute path to resource, works for dev and for PyInstaller.

    Args:
        relative_path: Relative path to the resource

    Returns:
        Absolute path to the resource
    """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS  # type: ignore
    except AttributeError:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


class ConversionWorker(QObject):
    """
    Worker class for handling file conversion in a separate thread.

    This prevents the GUI from freezing during conversion operations.
    """

    finished = Signal(str)
    error = Signal(str)
    started = Signal()

    def __init__(self, input_md_path: str, template_path: Optional[str] = None) -> None:
        """
        Initialize the conversion worker.

        Args:
            input_md_path: Path to the input Markdown file
            template_path: Optional path to DOCX template
        """
        super().__init__()
        self.input_md_path = input_md_path
        self.template_path = template_path

    def run(self) -> None:
        """Execute the conversion process in the worker thread."""
        self.started.emit()
        logger.info(f"Starting conversion: {self.input_md_path}")

        try:
            output_path = convert_md_to_docx(
                self.input_md_path, reference_docx_path=self.template_path
            )
            if output_path:
                logger.info(f"Conversion successful: {output_path}")
                self.finished.emit(str(output_path))
            else:
                error_msg = "La conversión falló. Revise la consola para más detalles."
                logger.error(error_msg)
                self.error.emit(error_msg)
        except (ValidationError, ConversionError) as e:
            error_msg = f"Error durante la conversión: {str(e)}"
            logger.error(error_msg)
            self.error.emit(error_msg)
        except Exception as e:
            error_msg = f"Error inesperado durante la conversión: {str(e)}"
            logger.error(error_msg, exc_info=True)
            self.error.emit(error_msg)


class StyleManager:
    """Manages application styling and themes."""

    @staticmethod
    def get_dark_theme_stylesheet() -> str:
        """
        Get the dark theme stylesheet for the application.

        Returns:
            CSS stylesheet string for dark theme
        """
        return """
            QMainWindow {
                background-color: #2b2b2b;
                color: #f0f0f0;
            }
            QLabel {
                color: #f0f0f0;
            }
            QGroupBox {
                background-color: #3c3c3c;
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
                background-color: transparent;
            }
            QMenuBar::item:selected {
                background-color: #6495ED;
            }
            QMenu {
                background-color: #3c3c3c;
                color: #f0f0f0;
                border: 1px solid #555;
            }
            QMenu::item:selected {
                background-color: #6495ED;
            }
            QProgressBar {
                border: 2px solid #6495ED;
                border-radius: 5px;
                text-align: center;
                background-color: #444;
            }
            QProgressBar::chunk {
                background-color: #6495ED;
                border-radius: 3px;
            }
        """


class MarkdownConverterApp(QMainWindow):
    """
    Main application window for the Markdown Converter.

    This class provides a modern GUI interface for converting Markdown files
    to DOCX format with support for custom templates.
    """

    def __init__(self) -> None:
        """Initialize the main application window."""
        super().__init__()
        self.setup_logging()
        self.init_state()
        self.init_ui()
        self.create_menu_bar()

        logger.info("MW Convert application initialized")

    def setup_logging(self) -> None:
        """Set up logging for the GUI application."""
        setup_logging(logging.INFO)

    def init_state(self) -> None:
        """Initialize application state variables."""
        self.current_md_path: Optional[str] = None
        self.output_docx_path: Optional[str] = None
        self.template_path: Optional[str] = None
        self.thread: Optional[QThread] = None
        self.worker: Optional[ConversionWorker] = None

    def init_ui(self) -> None:
        """Initialize the user interface."""
        self.setWindowTitle("MW Convert")
        self.setGeometry(100, 100, 400, 450)
        self.setWindowIcon(QIcon(resource_path("icons/app_icon.ico")))

        # Apply dark theme
        self.setStyleSheet(StyleManager.get_dark_theme_stylesheet())

        # Central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        self.layout = QVBoxLayout(central_widget)

        self.create_file_selection_group()
        self.create_template_selection_group()
        self.create_convert_button()
        self.create_output_group()
        self.create_footer()

        self.reset_application_state()

    def create_file_selection_group(self) -> None:
        """Create the file selection group."""
        markdown_group = QGroupBox("Paso 1: Selección de Archivo Markdown")
        markdown_layout = QVBoxLayout()

        self.browse_button = QPushButton("Buscar archivo .md")
        self.browse_button.setIcon(QIcon(resource_path("icons/search.png")))
        self.browse_button.clicked.connect(self.browse_file)
        markdown_layout.addWidget(self.browse_button)

        self.drop_area_label = QLabel("Arrastre y suelte su archivo .md aquí")
        self.drop_area_label.setAlignment(Qt.AlignCenter)
        self.drop_area_label.setStyleSheet(
            "QLabel { border: 2px dashed #aaa; border-radius: 5px; "
            "background-color: #333; padding: 20px; }"
        )
        markdown_layout.addWidget(self.drop_area_label)
        markdown_group.setLayout(markdown_layout)
        self.layout.addWidget(markdown_group)

        # Enable drag and drop
        self.setAcceptDrops(True)

    def create_template_selection_group(self) -> None:
        """Create the template selection group."""
        self.template_group = QGroupBox(
            "Paso 2: Selección de Plantilla DOCX (Opcional)"
        )
        template_layout = QVBoxLayout()

        self.template_path_label = QLabel("Plantilla seleccionada: Ninguna")
        template_layout.addWidget(self.template_path_label)

        template_button_layout = QHBoxLayout()
        self.template_button = QPushButton("Seleccionar plantilla")
        self.template_button.setIcon(QIcon(resource_path("icons/docx.ico")))
        self.template_button.clicked.connect(self.select_template_file)
        template_button_layout.addWidget(self.template_button)

        self.clear_template_button = QPushButton("Limpiar")
        self.clear_template_button.setIcon(QIcon(resource_path("icons/clear.png")))
        self.clear_template_button.clicked.connect(self.clear_template_selection)
        self.clear_template_button.hide()
        template_button_layout.addWidget(self.clear_template_button)

        template_layout.addLayout(template_button_layout)
        self.template_group.setLayout(template_layout)
        self.layout.addWidget(self.template_group)

    def create_convert_button(self) -> None:
        """Create the convert button."""
        self.convert_button = QPushButton("Convertir a DOCX")
        self.convert_button.setIcon(QIcon(resource_path("icons/convert_about.png")))
        self.convert_button.clicked.connect(self.convert_selected_file)
        self.convert_button.setEnabled(False)
        self.layout.addWidget(self.convert_button)

    def create_output_group(self) -> None:
        """Create the output actions group."""
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
        self.open_file_button.setIcon(QIcon(resource_path("icons/docx.ico")))
        self.open_file_button.setEnabled(False)
        self.open_file_button.clicked.connect(self.open_output_file)
        output_layout.addWidget(self.open_file_button)

        self.open_folder_button = QPushButton("Ver en carpeta")
        self.open_folder_button.setIcon(QIcon(resource_path("icons/folder_open.png")))
        self.open_folder_button.setEnabled(False)
        self.open_folder_button.clicked.connect(self.open_output_folder)
        output_layout.addWidget(self.open_folder_button)

        self.output_group.setLayout(output_layout)
        self.layout.addWidget(self.output_group)

    def create_footer(self) -> None:
        """Create the application footer."""
        app_info_label = QLabel("MW Convert v1.3 (2025)")
        app_info_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(app_info_label)

        developer_info_layout = QHBoxLayout()
        developer_info_layout.setAlignment(Qt.AlignCenter)

        developed_by_label = QLabel("Desarrollado por Diego A. Rábalo")
        developer_info_layout.addWidget(developed_by_label)

        linkedin_button = QPushButton()
        linkedin_button.setIcon(QIcon(resource_path("icons/linkedin.ico")))
        linkedin_button.setIconSize(QSize(16, 16))
        linkedin_button.setToolTip("Perfil de LinkedIn")
        linkedin_button.clicked.connect(self.open_linkedin_profile)
        developer_info_layout.addWidget(linkedin_button)

        self.new_project_button = QPushButton("Nuevo Proyecto")
        self.new_project_button.setIcon(QIcon(resource_path("icons/new_project.png")))
        self.new_project_button.clicked.connect(self.reset_application_state)
        self.new_project_button.setEnabled(False)
        developer_info_layout.addWidget(self.new_project_button)

        self.layout.addLayout(developer_info_layout)

    def dragEnterEvent(self, event) -> None:
        """Handle drag enter events for file dropping."""
        if (
            event.mimeData().hasUrls()
            and self.childAt(event.pos()) == self.drop_area_label
        ):
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event) -> None:
        """Handle drop events for file dropping."""
        if self.childAt(event.pos()) == self.drop_area_label:
            for url in event.mimeData().urls():
                file_path = url.toLocalFile()
                if file_path.endswith(".md"):
                    self.set_selected_file(file_path)
                    break
            event.acceptProposedAction()
        else:
            event.ignore()

    def set_selected_file(self, file_path: str) -> None:
        """
        Set the selected Markdown file and update UI state.

        Args:
            file_path: Path to the selected Markdown file
        """
        self.current_md_path = file_path
        file_name = os.path.basename(file_path)
        self.drop_area_label.setText(f"Archivo seleccionado: {file_name}")
        self.convert_button.setEnabled(True)
        self.template_group.setEnabled(True)
        self.new_project_button.setEnabled(False)
        self.status_label.setText("")
        self.open_file_button.setEnabled(False)
        self.open_folder_button.setEnabled(False)
        self.output_group.setEnabled(False)

        logger.info(f"File selected: {file_path}")

    def browse_file(self) -> None:
        """Open file dialog to browse for Markdown file."""
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(
            self, "Seleccionar archivo Markdown", "", "Archivos Markdown (*.md)"
        )
        if file_path:
            self.set_selected_file(file_path)

    def select_template_file(self) -> None:
        """Open file dialog to select DOCX template."""
        file_dialog = QFileDialog()
        template_path, _ = file_dialog.getOpenFileName(
            self, "Seleccionar Plantilla DOCX", "", "Archivos DOCX (*.docx)"
        )
        if template_path:
            self.template_path = template_path
            template_name = os.path.basename(template_path)
            self.template_path_label.setText(f"Plantilla seleccionada: {template_name}")
            self.clear_template_button.show()
            logger.info(f"Template selected: {template_path}")
        else:
            self.clear_template_selection()

    def clear_template_selection(self) -> None:
        """Clear the selected template."""
        self.template_path = None
        self.template_path_label.setText("Plantilla seleccionada: Ninguna")
        self.clear_template_button.hide()
        logger.info("Template selection cleared")

    def convert_selected_file(self) -> None:
        """Start the conversion process for the selected file."""
        if not self.current_md_path:
            self.show_error_message("No hay archivo seleccionado para convertir")
            return

        self._perform_conversion(self.current_md_path)

    def _perform_conversion(self, input_md_path: str) -> None:
        """
        Perform the conversion in a separate thread.

        Args:
            input_md_path: Path to the input Markdown file
        """
        file_name = os.path.basename(input_md_path)
        self.status_label.setText(f"Convirtiendo {file_name}...")
        QApplication.processEvents()
        self.progress_bar.show()

        # Create worker thread
        self.thread = QThread()
        self.worker = ConversionWorker(input_md_path, self.template_path)
        self.worker.moveToThread(self.thread)

        # Connect signals
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self._on_conversion_finished)
        self.worker.error.connect(self._on_conversion_error)
        self.worker.finished.connect(self.thread.quit)
        self.worker.error.connect(self.thread.quit)

        # Start the thread
        self.thread.start()

    def _on_conversion_finished(self, output_docx_path: str) -> None:
        """
        Handle successful conversion completion.

        Args:
            output_docx_path: Path to the converted DOCX file
        """
        self.progress_bar.hide()
        self.output_docx_path = output_docx_path
        file_name = os.path.basename(output_docx_path)
        self.status_label.setText(f"¡Conversión exitosa! Salida: {file_name}")

        # Enable output actions
        self.open_file_button.setEnabled(True)
        self.open_folder_button.setEnabled(True)
        self.new_project_button.setEnabled(True)
        self.output_group.setEnabled(True)

        # Disable conversion controls
        self.convert_button.setEnabled(False)
        self.template_group.setEnabled(False)

        logger.info(f"Conversion completed successfully: {output_docx_path}")

    def _on_conversion_error(self, error_message: str) -> None:
        """
        Handle conversion errors.

        Args:
            error_message: Error message describing the failure
        """
        self.progress_bar.hide()
        self.status_label.setText("Error en la conversión")
        self.show_error_message(f"Error durante la conversión:\n{error_message}")
        logger.error(f"Conversion failed: {error_message}")

    def open_output_file(self) -> None:
        """Open the converted DOCX file."""
        if self.output_docx_path and os.path.exists(self.output_docx_path):
            try:
                QDesktopServices.openUrl(QUrl.fromLocalFile(self.output_docx_path))
                logger.info(f"Opened output file: {self.output_docx_path}")
            except Exception as e:
                self.show_error_message(f"Error al abrir el archivo: {e}")
                logger.error(f"Failed to open output file: {e}")

    def open_output_folder(self) -> None:
        """Open the folder containing the converted file."""
        if self.output_docx_path:
            try:
                output_dir = os.path.dirname(self.output_docx_path)
                QDesktopServices.openUrl(QUrl.fromLocalFile(output_dir))
                logger.info(f"Opened output folder: {output_dir}")
            except Exception as e:
                self.show_error_message(f"Error al abrir la carpeta: {e}")
                logger.error(f"Failed to open output folder: {e}")

    def reset_application_state(self) -> None:
        """Reset the application to its initial state."""
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
        self.template_group.setEnabled(False)
        self.output_group.setEnabled(False)
        self.drop_area_label.setText("Arrastre y suelte su archivo .md aquí")
        logger.info("Application state reset")

    def show_error_message(self, message: str) -> None:
        """
        Show an error message dialog.

        Args:
            message: Error message to display
        """
        QMessageBox.critical(self, "Error", message)

    def show_info_message(self, title: str, message: str) -> None:
        """
        Show an information message dialog.

        Args:
            title: Dialog title
            message: Information message to display
        """
        QMessageBox.information(self, title, message)

    def create_menu_bar(self) -> None:
        """Create the application menu bar."""
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu("Archivo")

        new_action = QAction("Nuevo Proyecto", self)
        new_action.triggered.connect(self.reset_application_state)
        file_menu.addAction(new_action)

        file_menu.addSeparator()

        exit_action = QAction("Salir", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Help menu
        help_menu = menubar.addMenu("Ayuda")

        manual_action = QAction("Manual de Ayuda", self)
        manual_action.triggered.connect(self.show_help_manual)
        help_menu.addAction(manual_action)

        about_action = QAction("Acerca de", self)
        about_action.triggered.connect(self.show_about_dialog)
        help_menu.addAction(about_action)

        # Contribute menu
        contribute_menu = menubar.addMenu("Contribuir")

        linkedin_action = QAction("Compartir en LinkedIn", self)
        linkedin_action.triggered.connect(self.share_on_linkedin)
        contribute_menu.addAction(linkedin_action)

        donate_action = QAction("Donar", self)
        donate_action.triggered.connect(self.open_paypal_link)
        contribute_menu.addAction(donate_action)

    def open_linkedin_profile(self) -> None:
        """Open the developer's LinkedIn profile."""
        linkedin_url = "https://www.linkedin.com/in/rabalo"
        QDesktopServices.openUrl(QUrl(linkedin_url))

    def show_about_dialog(self) -> None:
        """Show the about dialog with application information."""
        about_text = """
        <h2>MW Convert</h2>
        <p><b>Versión:</b> 1.3 (2025)</p>
        <p><b>Descripción:</b> Aplicación para convertir archivos Markdown (.md)
        a documentos DOCX (.docx) con soporte para plantillas personalizadas.</p>
        <p><b>Tecnologías utilizadas:</b></p>
        <ul>
            <li><b>Python</b> como lenguaje de programación principal.</li>
            <li><b>PySide6</b> para la interfaz gráfica de usuario (GUI).</li>
            <li><b>Pypandoc</b> como motor de conversión de documentos.</li>
        </ul>
        <p><b>Características principales:</b></p>
        <ul>
            <li>Conversión robusta de Markdown a DOCX usando Pandoc.</li>
            <li>Soporte para plantillas DOCX personalizadas.</li>
            <li>Interfaz moderna con tema oscuro.</li>
            <li>Funcionalidad de arrastrar y soltar.</li>
        </ul>
        """

        QMessageBox.about(self, "Acerca de MW Convert", about_text)

    def show_help_manual(self) -> None:
        """Show the help manual dialog."""
        help_dialog = QDialog(self)
        help_dialog.setWindowTitle("Manual de Ayuda - MW Convert")
        help_dialog.setModal(True)
        help_dialog.resize(600, 400)

        layout = QVBoxLayout()
        text_browser = QTextBrowser()

        # Load manual content
        manual_path = Path(__file__).parent / "manual.html"
        if manual_path.exists():
            try:
                text_browser.setHtml(manual_path.read_text(encoding="utf-8"))
            except Exception as e:
                text_browser.setPlainText(f"Error loading manual: {e}")
                logger.error(f"Failed to load manual: {e}")
        else:
            text_browser.setPlainText("Error: Manual de ayuda no encontrado.")

        layout.addWidget(text_browser)

        close_button = QPushButton("Cerrar")
        close_button.clicked.connect(help_dialog.accept)
        layout.addWidget(close_button)

        help_dialog.setLayout(layout)
        help_dialog.exec()

    def share_on_linkedin(self) -> None:
        """Share application information on LinkedIn."""
        app_details = (
            "🚀 ¡Acabo de usar una increíble app para convertir Markdown a DOCX! "
            "📄✨ Permite estilos personalizados con plantillas DOCX. "
            "¡Súper útil para documentos profesionales y académicos! "
            "#Markdown #DOCX #Productividad #Pandoc"
        )
        creator_info = "Desarrollado por Diego A. Rábalo"
        linkedin_profile = "https://www.linkedin.com/in/rabalo"

        share_text = urllib.parse.quote_plus(
            f"{app_details}\n\n{creator_info}\n\n"
            f"Conoce más sobre el desarrollo y otras herramientas en mi perfil: "
            f"{linkedin_profile}"
        )

        linkedin_share_url = (
            f"https://www.linkedin.com/sharing/share-offsite/"
            f"?url={urllib.parse.quote_plus(linkedin_profile)}&title={share_text}"
        )

        QDesktopServices.openUrl(QUrl(linkedin_share_url))

    def open_paypal_link(self) -> None:
        """Open PayPal donation link."""
        paypal_url = "https://paypal.me/diegorabalo"
        QDesktopServices.openUrl(QUrl(paypal_url))


def main() -> None:
    """Main function to run the application."""
    app = QApplication(sys.argv)

    # Set application properties
    app.setApplicationName("MW Convert")
    app.setApplicationVersion("1.3")
    app.setOrganizationName("Diego A. Rábalo")

    window = MarkdownConverterApp()
    window.show()

    logger.info("Application started")
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
