import os
import pypandoc

def convert_md_to_docx(input_md_path, output_dir="output", reference_docx_path=None):
    """
    Convierte un archivo Markdown a DOCX usando pypandoc.
    Permite especificar un directorio de salida y una plantilla DOCX.
    Devuelve la ruta del archivo DOCX generado o None si falla.
    """
    os.makedirs(output_dir, exist_ok=True)

    file_name = os.path.splitext(os.path.basename(input_md_path))[0] + ".docx"
    output_docx_path = os.path.join(output_dir, file_name)

    extra_args = []
    if reference_docx_path:
        extra_args.extend(['--reference-doc', reference_docx_path])

    try:
        # Especificar el formato de entrada como 'gfm+smart' 
        # (GitHub-Flavored Markdown con tipografía inteligente)
        pypandoc.convert_file(
            input_md_path,
            'docx',
            format='gfm+smart',
            outputfile=output_docx_path,
            extra_args=extra_args
        )
        print(f"Conversión exitosa. Salida: {output_docx_path}")
        return output_docx_path
    except Exception as e:
        print(f"Error durante la conversión con pypandoc: {str(e)}")
        return None

if __name__ == "__main__":
    # Ejemplo de uso para pruebas
    dummy_md_content = """
# Documento de Prueba

Este es un archivo markdown de prueba.

**Listas:**

**Lista Ordenada:**
1. Primer elemento
2. Segundo elemento
   1. Sub-elemento 2.1
   2. Sub-elemento 2.2
3. Tercer elemento

**Lista Desordenada:**
* Elemento A
* Elemento B
  * Sub-elemento B.1
  * Sub-elemento B.2
* Elemento C
"""
    test_md_path = "test_input.md"
    with open(test_md_path, "w", encoding="utf-8") as f:
        f.write(dummy_md_content)

    converted_file = convert_md_to_docx(test_md_path)
    if converted_file:
        print(f"Convertido exitosamente a: {converted_file}")
    else:
        print("La conversión falló.")