from shared.herramienta import (
    imprimir_titulo,
    imprimir_error,
    imprimir_info,
    imprimir_color
)

from models import (
    EstudianteController,
    DocenteController,
    MateriaController,
    MatriculaController
)
class MenuCRUD:
    """Menú CRUD reutilizable para cualquier controlador."""

    def __init__(self, controlador, titulo):
        self._controlador = controlador
        self._titulo = titulo
        self._activo = True

    @staticmethod
    def pausa():
        input("\nPresione Enter para continuar...")

    @staticmethod
    def pedir_entero(mensaje):
        try:
            return int(input(mensaje).strip())
        except ValueError:
            imprimir_error("Debe ingresar un número entero.")
            return None

    def mostrar_resultado(self, resultado):
        if isinstance(resultado, tuple) and len(resultado) == 2:
            ok, mensaje = resultado

            if ok:
                imprimir_color(mensaje, "VERDE")
            else:
                imprimir_error(mensaje)
        else:
            print(resultado)

    def ejecutar(self):
        self._activo = True

        while self._activo:
            imprimir_titulo(self._titulo)

            imprimir_color("1. Crear / registrar", "VERDE")
            imprimir_color("2. Ver todos", "AMARILLO")
            imprimir_color("3. Buscar", "CYAN")
            imprimir_color("4. Ver por ID", "AZUL")
            imprimir_color("5. Actualizar", "MORADO")
            imprimir_color("6. Eliminar", "ROJO")
            imprimir_color("0. Volver", "BLANCO")

            opcion = input("\nSeleccione una opción: ").strip()

            if opcion == "1":
                self.crear()
            elif opcion == "2":
                self.listar()
            elif opcion == "3":
                self.buscar()
            elif opcion == "4":
                self.ver_por_id()
            elif opcion == "5":
                self.actualizar()
            elif opcion == "6":
                self.eliminar()
            elif opcion == "0":
                self.volver()
            else:
                imprimir_error("Opción no válida.")
                self.pausa()

    def crear(self):
        imprimir_titulo(f"REGISTRAR {self._titulo}")
        datos = {}

        for campo, etiqueta in self._controlador.MODELO.CAMPOS.items():
            datos[campo] = input(f"{etiqueta}: ").strip()

        resultado = self._controlador.crear(datos)
        self.mostrar_resultado(resultado)
        self.pausa()

    def listar(self):
        imprimir_titulo(f"LISTA DE {self._titulo}")
        registros = self._controlador.listar()

        if not registros:
            imprimir_info("No hay registros.")
        else:
            for registro in registros:
                imprimir_color("-" * 45, "VERDE")

                if isinstance(registro, dict):
                    for campo, valor in registro.items():
                        nombre = f"{campo.capitalize():<15}:"
                        texto = f"{nombre} {valor}"
                        imprimir_color(texto, "CYAN")
                else:
                    imprimir_color(str(registro), "AMARILLO")

                imprimir_color("-" * 45, "VERDE")

        self.pausa()

    def buscar(self):
        imprimir_titulo(f"BUSCAR {self._titulo}")

        termino = input("Texto a buscar: ").strip()
        resultados = self._controlador.buscar(termino)

        if not resultados:
            imprimir_info("No se encontraron coincidencias.")
        else:
            for registro in resultados:
                imprimir_color("-" * 45, "VERDE")

                if isinstance(registro, dict):
                    for campo, valor in registro.items():
                        imprimir_color(
                            f"{campo.capitalize():<15}: {valor}",
                            "CYAN"
                        )
                else:
                    imprimir_color(str(registro), "AMARILLO")

                imprimir_color("-" * 45, "VERDE")

        self.pausa()

    def ver_por_id(self):
        imprimir_titulo(f"VER {self._titulo} POR ID")

        identificador = self.pedir_entero("ID: ")

        if identificador is None:
            self.pausa()
            return

        registro = self._controlador.obtener(identificador)

        if registro is None:
            imprimir_error("No existe un registro con ese ID.")
        else:
            imprimir_color("-" * 45, "VERDE")

            if isinstance(registro, dict):
                for campo, valor in registro.items():
                    imprimir_color(
                        f"{campo.capitalize():<15}: {valor}",
                        "CYAN"
                    )
            else:
                imprimir_color(str(registro), "AMARILLO")

            imprimir_color("-" * 45, "VERDE")

        self.pausa()

    def actualizar(self):
        imprimir_titulo(f"ACTUALIZAR {self._titulo}")

        identificador = self.pedir_entero("ID del registro: ")

        if identificador is None:
            self.pausa()
            return

        registro = self._controlador.obtener(identificador)

        if registro is None:
            imprimir_error("No existe un registro con ese ID.")
            self.pausa()
            return

        imprimir_info(
            "Deje vacío un campo si no desea modificarlo."
        )

        datos = {}

        for campo, etiqueta in self._controlador.MODELO.CAMPOS.items():
            valor = input(f"{etiqueta} nuevo: ").strip()

            if valor:
                datos[campo] = valor

        if datos:
            resultado = self._controlador.actualizar(
                identificador, datos
            )
            self.mostrar_resultado(resultado)
        else:
            imprimir_info("No se realizaron cambios.")

        self.pausa()

    def eliminar(self):
        imprimir_titulo(f"ELIMINAR {self._titulo}")

        identificador = self.pedir_entero("ID del registro: ")

        if identificador is None:
            self.pausa()
            return

        registro = self._controlador.obtener(identificador)

        if registro is None:
            imprimir_error("No existe un registro con ese ID.")
            self.pausa()
            return

        confirmacion = input(
            "¿Está seguro de eliminarlo? (s/n): "
        ).strip().lower()

        if confirmacion in ("s", "si", "sí"):
            resultado = self._controlador.eliminar(identificador)
            self.mostrar_resultado(resultado)
        else:
            imprimir_info("Operación cancelada.")

        self.pausa()

    def volver(self):
        self._activo = False


class MenuPrincipalAcademico:

    def __init__(self):
        self.menus = {
            "1": MenuCRUD(
                EstudianteController(),
                "ESTUDIANTES"
            ),
            "2": MenuCRUD(
                DocenteController(),
                "DOCENTES"
            ),
            "3": MenuCRUD(
                MateriaController(),
                "MATERIAS"
            ),
            "4": MenuCRUD(
                MatriculaController(),
                "MATRÍCULAS"
            ),
        }

    def ejecutar(self):
        while True:
            imprimir_titulo("SISTEMA ACADÉMICO")

            imprimir_color(
                "1. Gestionar estudiantes", "VERDE"
            )
            imprimir_color(
                "2. Gestionar docentes", "AMARILLO"
            )
            imprimir_color(
                "3. Gestionar materias", "CYAN"
            )
            imprimir_color(
                "4. Gestionar matrículas", "MORADO"
            )
            imprimir_color("0. Salir", "ROJO")

            opcion = input(
                "\nSeleccione una opción: "
            ).strip()

            if opcion in self.menus:
                self.menus[opcion].ejecutar()

            elif opcion == "0":
                imprimir_color(
                    "Gracias por utilizar el sistema académico.",
                    "VERDE"
                )
                break

            else:
                imprimir_error("Opción no válida.")
                input("\nPresione Enter para continuar...")

if __name__ == "__main__":
    MenuPrincipalAcademico().ejecutar()