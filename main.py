import os
import subprocess

def convert_md_to_docx(input_md_path, output_dir="output", reference_docx_path=None):
    """
    Convierte un archivo Markdown a DOCX usando Pandoc.
    Permite especificar un directorio de salida y una plantilla DOCX.
    Devuelve la ruta del archivo DOCX generado o None si falla.
    """
    os.makedirs(output_dir, exist_ok=True)

    file_name = os.path.splitext(os.path.basename(input_md_path))[0] + ".docx"
    output_docx_path = os.path.join(output_dir, file_name)

    command = ["pandoc", input_md_path, "-o", output_docx_path]

    if reference_docx_path:
        command.extend(["--reference-doc", reference_docx_path])

    try:
        result = subprocess.run(command, check=True, capture_output=True, text=True)
        print(f"Pandoc Stdout: {result.stdout}")
        print(f"Pandoc Stderr: {result.stderr}")
        return output_docx_path
    except subprocess.CalledProcessError as e:
        print(f"Error durante la conversión con Pandoc: {e}")
        print(f"Pandoc Stdout: {e.stdout}")
        print(f"Pandoc Stderr: {e.stderr}")
        return None
    except FileNotFoundError:
        print("Error: Pandoc no se encontró. Asegúrese de que esté instalado y en su PATH.")
        return None
    except Exception as e:
        print(f"Error inesperado durante la conversión: {str(e)}")
        return None

if __name__ == "__main__":
    # Ejemplo de uso para pruebas
    dummy_md_content = "# Documento de Prueba\n\nEste es un archivo markdown de prueba."
    test_md_path = "test_input.md"
    with open(test_md_path, "w", encoding="utf-8") as f:
        f.write(dummy_md_content)

    converted_file = convert_md_to_docx(test_md_path)
    if converted_file:
        print(f"Convertido exitosamente a: {converted_file}")
        os.remove(test_md_path)
    else:
        print("La conversión falló.")
