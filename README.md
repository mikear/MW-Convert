¡Entendido! Tomaré tu README.md original y lo modificaré para integrar las imágenes de manera profesional.

La idea es mantener todo tu texto original pero enriquecerlo con una sección visual que muestre la aplicación en acción. Esto se hace añadiendo una galería de imágenes justo después de la introducción.

Aquí tienes el código de tu README.md original, modificado para incluir las imágenes. Simplemente copia y pega este código completo en tu archivo README.md.

(COPIA Y PEGA ESTE CÓDIGO EN TU README.MD)

code
Markdown
download
content_copy
expand_less

![Banner de MW Converter](assets/banner.png)

# MW Convert

MW Convert es una aplicación de escritorio intuitiva y fácil de usar diseñada para convertir archivos Markdown (`.md`) a documentos DOCX (`.docx`) con soporte para plantillas personalizadas.

---

## ✨ Galería de la Aplicación

| Interfaz Principal | Conversión de Alta Fidelidad |
| :---: | :---: |
| ![Captura de la aplicación MW Convert](assets/app-screenshot.png) | ![Ejemplo de documento de salida](assets/output-example.png) |

---

## Características

-   **Conversión Robusta:** Convierte tus archivos Markdown a DOCX utilizando el potente motor de Pandoc, asegurando una fidelidad de estilo y formato excepcional.
-   **Plantillas DOCX Personalizadas:** Aplica tus propias plantillas DOCX para dar a tus documentos convertidos un estilo y diseño profesional y consistente.
-   **Flujo de Trabajo de 3 Pasos:** Una interfaz clara y guiada que te lleva a través de la selección del archivo, la elección de la plantilla (opcional) y la conversión.
-   **Entrada Flexible:** Selecciona archivos Markdown mediante un explorador de archivos o simplemente arrástralos y suéltalos en la aplicación.
-   **Acceso Rápido a Salida:** Abre directamente el documento DOCX convertido o la carpeta que lo contiene con un solo clic.
-   **Interfaz de Usuario Moderna:** Disfruta de una experiencia visual agradable con un tema oscuro moderno y una disposición limpia.

## Requisitos

Para ejecutar MW Convert, necesitas tener instalado lo siguiente:

-   **Python 3.7 o superior:** Puedes descargarlo desde [python.org](https://www.python.org/).
-   **PySide6:** La biblioteca de Python para la interfaz gráfica de usuario.
-   **Pandoc:** Una herramienta universal de conversión de documentos. Asegúrate de que esté instalado y accesible desde la línea de comandos (añadido a tu PATH).
    -   Descarga Pandoc desde [pandoc.org/installing.html](https://pandoc.org/installing.html).

## Instalación

Sigue estos pasos para configurar y ejecutar MW Convert en tu máquina local:

1.  **Clona el repositorio:**
    ```bash
    git clone https://github.com/mikeear/MW-Convert.git
    cd MW-Convert
    ```

2.  **Instala las dependencias de Python:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Asegúrate de que Pandoc esté instalado** y configurado en tu sistema como se menciona en la sección de Requisitos.

## Uso

Para iniciar la aplicación, ejecuta el siguiente comando desde el directorio raíz del proyecto:

```bash
python gui_app.py

Una vez que la aplicación esté abierta, sigue el flujo de trabajo de 3 pasos:

Selecciona o arrastra tu archivo Markdown.

Selecciona una plantilla DOCX (opcional).

Haz clic en "Convertir a DOCX" y luego abre tu documento o la carpeta de salida.

Créditos

Desarrollado por Diego A. Rábalo

LinkedIn: Perfil de Diego A. Rábalo

Correo Electrónico: diego_rabalo@hotmail.com

Licencia

Este proyecto está bajo la licencia MIT. Consulta el archivo LICENSE para más detalles.

code
Code
download
content_copy
expand_less
IGNORE_WHEN_COPYING_START
IGNORE_WHEN_COPYING_END
### ¿Qué cambios he hecho?

1.  **Banner Superior:** Agregué tu banner profesional justo al principio para una excelente primera impresión.
2.  **Nueva Sección "Galería de la Aplicación":** Creé una sección justo después de la descripción principal.
3.  **Tabla de Imágenes:** Usé una tabla de Markdown para mostrar la captura principal de la aplicación junto al resultado de la conversión. Esto le da un aspecto muy ordenado y profesional.
4.  **Rutas Correctas:** Me aseguré de que todas las rutas de las imágenes apunten a la carpeta `assets/`, que es la mejor práctica.

El resto de tu contenido (Características, Requisitos, etc.) se ha mantenido intacto, tal y como lo tenías.
