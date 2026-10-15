from datetime import date
from pathlib import Path
from shared.json_manager import GestorJSON


BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"


class Modelo:
    CAMPOS = {}
    ARCHIVO = ""

    def __init__(self, **datos):
        self.datos = datos

    def a_dict(self):
        return dict(self.datos)


class Estudiante(Modelo):
    CAMPOS = {
        "nombre": "Nombre",
        "apellido": "Apellido",
        "email": "Correo electrónico",
        "carnet": "Carnet",
    }
    ARCHIVO = "estudiantes.json"


class Docente(Modelo):
    CAMPOS = {
        "nombre": "Nombre",
        "apellido": "Apellido",
        "email": "Correo electrónico",
        "especialidad": "Especialidad",
    }
    ARCHIVO = "docentes.json"


class Materia(Modelo):
    CAMPOS = {
        "nombre": "Nombre de la materia",
        "codigo": "Código",
        "docente_id": "ID del docente",
    }
    ARCHIVO = "materias.json"


class Matricula(Modelo):
    CAMPOS = {
        "estudiante_id": "ID del estudiante",
        "materia_id": "ID de la materia",
        "periodo": "Período (ej. 2026-2027)",
    }
    ARCHIVO = "matriculas.json"


class CRUDController:
    MODELO = Modelo
    ARCHIVO = ""

    def __init__(self):
        ruta = DATA_DIR / (self.ARCHIVO or self.MODELO.ARCHIVO)
        ruta.parent.mkdir(parents=True, exist_ok=True)
        self._gestor = GestorJSON(str(ruta))

    def _leer(self):
        datos = self._gestor.leer()
        return datos if isinstance(datos, list) else []

    def _guardar(self, datos):
        self._gestor.guardar(datos)

    def _siguiente_id(self, registros):
        return max(
            (int(r.get("id", 0)) for r in registros),
            default=0
        ) + 1

    def listar(self):
        return self._leer()

    def obtener(self, identificador):
        if identificador is None:
            return None

        try:
            identificador = int(identificador)
        except (ValueError, TypeError):
            return None

        return next(
            (r for r in self._leer()
             if int(r.get("id", 0)) == identificador),
            None
        )

    def buscar(self, termino):
        termino = str(termino).strip().lower()

        if not termino:
            return []

        campos = list(self.MODELO.CAMPOS.keys())

        return [
            registro
            for registro in self._leer()
            if any(
                termino in str(registro.get(campo, "")).lower()
                for campo in campos
            )
        ]

    def crear(self, datos):
        if not isinstance(datos, dict):
            return False, "Los datos proporcionados no son válidos."

        limpios = {}

        for campo in self.MODELO.CAMPOS:
            valor = datos.get(campo, "")

            if campo.endswith("_id"):
                try:
                    valor = int(valor)
                except (ValueError, TypeError):
                    return False, f"{campo} debe ser un número entero."

            if isinstance(valor, str):
                valor = valor.strip()

            limpios[campo] = valor

        for campo, etiqueta in self.MODELO.CAMPOS.items():
            if not str(limpios.get(campo, "")).strip():
                return False, f"El campo '{etiqueta}' es obligatorio."

        registros = self._leer()

        error = self._validar_relaciones(limpios)
        if error:
            return False, error

        if self.MODELO is Estudiante:
            carnet = str(limpios["carnet"]).lower()

            if any(
                str(r.get("carnet", "")).lower() == carnet
                for r in registros
            ):
                return False, "Ya existe un estudiante con ese carnet."

        if self.MODELO is Materia:
            codigo = str(limpios["codigo"]).lower()

            if any(
                str(r.get("codigo", "")).lower() == codigo
                for r in registros
            ):
                return False, "Ya existe una materia con ese código."

        nuevo = {
            "id": self._siguiente_id(registros),
            **limpios
        }

        if self.MODELO is Matricula:
            nuevo["notas"] = []

        registros.append(nuevo)
        self._guardar(registros)

        return True, f"Registro creado correctamente. ID: {nuevo['id']}"

    def _validar_relaciones(self, datos):
        return None

    def actualizar(self, identificador, datos):
        registros = self._leer()

        try:
            identificador = int(identificador)
        except (ValueError, TypeError):
            return False, "El ID debe ser un número entero."

        for registro in registros:
            if int(registro.get("id", 0)) == identificador:
                cambios = {}

                for campo in self.MODELO.CAMPOS:
                    valor = datos.get(campo, registro.get(campo, ""))

                    if isinstance(valor, str):
                        valor = valor.strip()

                    if campo.endswith("_id"):
                        try:
                            valor = int(valor)
                        except (ValueError, TypeError):
                            return False, f"{campo} debe ser un número entero."

                    cambios[campo] = valor

                combinado = {**registro, **cambios}

                for campo, etiqueta in self.MODELO.CAMPOS.items():
                    if not str(combinado.get(campo, "")).strip():
                        return False, f"El campo '{etiqueta}' es obligatorio."

                error = self._validar_relaciones(combinado)
                if error:
                    return False, error

                if self.MODELO is Estudiante:
                    carnet = str(combinado["carnet"]).lower()

                    if any(
                        int(r.get("id", 0)) != identificador
                        and str(r.get("carnet", "")).lower() == carnet
                        for r in registros
                    ):
                        return False, "Ya existe un estudiante con ese carnet."

                if self.MODELO is Materia:
                    codigo = str(combinado["codigo"]).lower()

                    if any(
                        int(r.get("id", 0)) != identificador
                        and str(r.get("codigo", "")).lower() == codigo
                        for r in registros
                    ):
                        return False, "Ya existe una materia con ese código."

                registro.update(cambios)
                self._guardar(registros)

                return True, "Registro actualizado correctamente."

        return False, "No se encontró el registro."

    def eliminar(self, identificador):
        try:
            identificador = int(identificador)
        except (ValueError, TypeError):
            return False, "El ID debe ser un número entero."

        registros = self._leer()

        registro = next(
            (r for r in registros
             if int(r.get("id", 0)) == identificador),
            None
        )

        if registro is None:
            return False, "No se encontró el registro."

        if self.MODELO is Estudiante:
            matriculas = MatriculaController().listar()

            if any(
                int(m.get("estudiante_id", 0)) == identificador
                for m in matriculas
            ):
                return False, "No se puede eliminar: el estudiante tiene matrículas."

        if self.MODELO is Materia:
            matriculas = MatriculaController().listar()

            if any(
                int(m.get("materia_id", 0)) == identificador
                for m in matriculas
            ):
                return False, "No se puede eliminar: la materia tiene matrículas."

        if self.MODELO is Docente:
            materias = MateriaController().listar()

            if any(
                int(m.get("docente_id", 0)) == identificador
                for m in materias
            ):
                return False, "No se puede eliminar: el docente tiene materias asignadas."

        registros = [
            r for r in registros
            if int(r.get("id", 0)) != identificador
        ]

        self._guardar(registros)

        return True, "Registro eliminado correctamente."


class EstudianteController(CRUDController):
    MODELO = Estudiante


class DocenteController(CRUDController):
    MODELO = Docente


class MateriaController(CRUDController):
    MODELO = Materia

    def _validar_relaciones(self, datos):
        try:
            docente_id = int(datos.get("docente_id"))
        except (ValueError, TypeError):
            return "El ID del docente debe ser un número entero."

        if DocenteController().obtener(docente_id) is None:
            return "No existe un docente con ese ID."

        return None


class MatriculaController(CRUDController):
    MODELO = Matricula

    def _validar_relaciones(self, datos):
        try:
            estudiante_id = int(datos.get("estudiante_id"))
            materia_id = int(datos.get("materia_id"))
        except (ValueError, TypeError):
            return "Los ID del estudiante y de la materia deben ser números enteros."

        if EstudianteController().obtener(estudiante_id) is None:
            return "No existe un estudiante con ese ID."

        if MateriaController().obtener(materia_id) is None:
            return "No existe una materia con ese ID."

        return None

    def crear(self, datos):
        datos = dict(datos)

        if not str(datos.get("periodo", "")).strip():
            datos["periodo"] = date.today().strftime("%Y")

        return super().crear(datos)

    def agregar_nota(self, matricula_id, tipo, valor, peso=1):
        try:
            matricula_id = int(matricula_id)
            valor = float(valor)
            peso = float(peso)
        except (ValueError, TypeError):
            return False, "El ID, la nota y el peso deben ser válidos."

        if not 0 <= valor <= 20:
            return False, "La nota debe estar entre 0 y 20."

        if peso <= 0:
            return False, "El peso debe ser mayor que cero."

        if not str(tipo).strip():
            return False, "Debe indicar el tipo de evaluación."

        registros = self._leer()

        for matricula in registros:
            if int(matricula.get("id", 0)) == matricula_id:
                matricula.setdefault("notas", []).append({
                    "tipo": str(tipo).strip(),
                    "valor": valor,
                    "peso": peso,
                })

                self._guardar(registros)
                return True, "Nota agregada correctamente."

        return False, "No se encontró la matrícula."

    def boletin(self, estudiante_id):
        try:
            estudiante_id = int(estudiante_id)
        except (ValueError, TypeError):
            return None

        estudiante = EstudianteController().obtener(estudiante_id)

        if estudiante is None:
            return None

        materias = {
            int(m["id"]): m
            for m in MateriaController().listar()
        }

        matriculas = [
            m for m in self._leer()
            if int(m.get("estudiante_id", 0)) == estudiante_id
        ]

        lineas = [
            f"BOLETÍN DE {estudiante.get('nombre', '')} "
            f"{estudiante.get('apellido', '')}",
            f"Carnet: {estudiante.get('carnet', '')}",
            "-" * 55,
        ]

        if not matriculas:
            lineas.append("El estudiante no tiene matrículas registradas.")

        for matricula in matriculas:
            materia = materias.get(matricula.get("materia_id"), {})
            notas = matricula.get("notas", [])

            peso_total = sum(
                float(n.get("peso", 1)) for n in notas
            )

            promedio = (
                sum(
                    float(n.get("valor", 0)) * float(n.get("peso", 1))
                    for n in notas
                ) / peso_total
                if peso_total else None
            )

            lineas.append(
                f"Materia: {materia.get('nombre', 'Materia no encontrada')}"
            )
            lineas.append(f"Período: {matricula.get('periodo', '')}")

            if notas:
                for nota in notas:
                    lineas.append(
                        f"  {nota.get('tipo', 'Evaluación')}: "
                        f"{float(nota.get('valor', 0)):.2f}/20 "
                        f"(peso {float(nota.get('peso', 1)):g})"
                    )

                lineas.append(f"  Promedio: {promedio:.2f}/20")
            else:
                lineas.append("  Todavía no hay notas.")

            lineas.append("-" * 55)

        return "\n".join(lineas)