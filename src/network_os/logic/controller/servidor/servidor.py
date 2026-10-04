from __future__ import annotations

from collections.abc import Callable
from hmac import compare_digest
from pathlib import Path
from typing import TypeVar

from ....persistencia.persistencias_servidorCSV.persistencias_servidorCSV import (
    PersistenciaServidorCSV,
)
from ...model.archivo.archivo import Archivo
from ...model.paquete_datos.paquete_datos import PaqueteDatos
from ...model.registro_auditoria.registro_auditoria import RegistroAuditoria
from ...structure.carpeta.carpeta import Carpeta
from ...structure.hash_table.hash_map import HashMap
from ..AuditoriaServidor.auditoria_servidor import AuditoriaServidor
from ..gestor_archivos.gestor_archivos import GestorArchivos


T = TypeVar("T")


class Servidor:
    """Fachada para las operaciones locales de un servidor."""

    def __init__(
        self,
        nombre: str,
        id_servidor: int,
        direccion_base: str | Path,
    ) -> None:
        self.__validar_nombre(nombre)
        self.__validar_id(id_servidor)

        self.__nombre = nombre.strip()
        self.__id = id_servidor
        self.__servidor_csv = PersistenciaServidorCSV(
            direccion_base,
            self.__nombre,
            self.__id,
        )
        self.__auditoria = AuditoriaServidor(
            self.__nombre,
            self.__servidor_csv.auditoria,
        )
        self.__credenciales_usuarios: HashMap = (
            self.__servidor_csv.usuarios.cargar()
        )
        self.__repositorio = GestorArchivos(
            self.__nombre,
            self.__servidor_csv.archivos,
        )
        self.__repositorio.cargar_servidor()

    @property
    def nombre(self) -> str:
        return self.__nombre

    @property
    def id(self) -> int:
        return self.__id

    @property
    def auditoria(self) -> AuditoriaServidor:
        return self.__auditoria

    @property
    def persistencia(self) -> PersistenciaServidorCSV:
        return self.__servidor_csv

    @property
    def gestor_archivos(self) -> GestorArchivos:
        return self.__repositorio

    @staticmethod
    def __validar_nombre(nombre: str) -> None:
        if not isinstance(nombre, str) or not nombre.strip():
            raise ValueError("El nombre del servidor debe ser una cadena no vacia.")

    @staticmethod
    def __validar_id(id_servidor: int) -> None:
        if (
            not isinstance(id_servidor, int)
            or isinstance(id_servidor, bool)
            or id_servidor < 0
        ):
            raise ValueError("El ID del servidor debe ser un entero no negativo.")

    @staticmethod
    def __validar_nombre_usuario(nombre: str) -> str:
        if not isinstance(nombre, str):
            raise TypeError("El nombre de usuario debe ser una cadena.")

        nombre_limpio = nombre.strip()
        if not 3 <= len(nombre_limpio) <= 30:
            raise ValueError(
                "El nombre de usuario debe tener entre 3 y 30 caracteres."
            )
        if any(caracter.isspace() for caracter in nombre_limpio):
            raise ValueError("El nombre de usuario no puede contener espacios.")
        if not all(
            caracter.isalnum() or caracter in "._-"
            for caracter in nombre_limpio
        ):
            raise ValueError(
                "El nombre de usuario solo puede contener letras, numeros, "
                "puntos, guiones y guiones bajos."
            )
        return nombre_limpio

    @staticmethod
    def __validar_contrasena(contrasena: str) -> None:
        if not isinstance(contrasena, str):
            raise TypeError("La contrasena debe ser una cadena.")
        if not 8 <= len(contrasena) <= 128:
            raise ValueError("La contrasena debe tener entre 8 y 128 caracteres.")
        if not any(caracter.isalpha() for caracter in contrasena):
            raise ValueError("La contrasena debe contener al menos una letra.")
        if not any(caracter.isdigit() for caracter in contrasena):
            raise ValueError("La contrasena debe contener al menos un numero.")

    def agregar_usuario(self, nombre: str, contrasena: str) -> None:
        nombre_limpio = self.__validar_nombre_usuario(nombre)
        self.__validar_contrasena(contrasena)

        def operacion() -> None:
            if self.__credenciales_usuarios.contiene(nombre_limpio):
                raise ValueError("El usuario ya esta registrado.")
            self.__credenciales_usuarios.insertar(nombre_limpio, contrasena)
            self.__servidor_csv.usuarios.guardar(self.__credenciales_usuarios)

        self.ejecutar_accion(
            "USUARIOS",
            "AGREGAR_USUARIO",
            f"Usuario '{nombre_limpio}'.",
            operacion,
        )

    def eliminar_usuario(self, nombre: str) -> bool:
        nombre_limpio = self.__validar_nombre_usuario(nombre)
        if not self.__credenciales_usuarios.contiene(nombre_limpio):
            self.registrar_evento(
                "USUARIOS",
                "ELIMINAR_USUARIO",
                "FALLIDO",
                f"El usuario '{nombre_limpio}' no existe.",
            )
            return False

        def operacion() -> bool:
            eliminado = self.__credenciales_usuarios.eliminar(nombre_limpio)
            self.__servidor_csv.usuarios.guardar(self.__credenciales_usuarios)
            return eliminado

        return self.ejecutar_accion(
            "USUARIOS",
            "ELIMINAR_USUARIO",
            f"Usuario '{nombre_limpio}'.",
            operacion,
        )

    def autenticar_usuario(self, nombre: str, contrasena: str) -> bool:
        try:
            nombre_limpio = self.__validar_nombre_usuario(nombre)
            self.__validar_contrasena(contrasena)
        except (TypeError, ValueError) as error:
            self.registrar_evento(
                "USUARIOS",
                "AUTENTICAR_USUARIO",
                "FALLIDO",
                str(error),
            )
            return False

        almacenada = self.__credenciales_usuarios.obtener(nombre_limpio)
        autenticado = isinstance(almacenada, str) and compare_digest(
            almacenada.encode("utf-8"),
            contrasena.encode("utf-8"),
        )
        self.registrar_evento(
            "USUARIOS",
            "AUTENTICAR_USUARIO",
            "EXITOSO" if autenticado else "FALLIDO",
            f"Intento de acceso para '{nombre_limpio}'.",
        )
        return autenticado

    def listar_contenido(self) -> list[Carpeta | Archivo]:
        return self.__repositorio.listar_elementos()

    def obtener_carpeta_actual(self) -> Carpeta:
        return self.__repositorio.carpeta_actual

    def crear_subcarpeta(self, nombre: str) -> Carpeta:
        return self.ejecutar_accion(
            "ARCHIVOS",
            "CREAR_SUBCARPETA",
            f"Subcarpeta '{nombre}'.",
            lambda: self.__repositorio.crear_nueva_subcarpeta(nombre),
        )

    def renombrar_carpeta(self, nombre: str) -> None:
        self.ejecutar_accion(
            "ARCHIVOS",
            "RENOMBRAR_CARPETA",
            f"Nuevo nombre '{nombre}'.",
            lambda: self.__repositorio.renombrar_subcarpeta(nombre),
        )

    def eliminar_subcarpeta(self, id: int) -> None:
        self.ejecutar_accion(
            "ARCHIVOS",
            "ELIMINAR_SUBCARPETA",
            f"Subcarpeta con ID {id}.",
            lambda: self.__repositorio.eliminar_subcarpeta(id),
        )

    def entrar_subcarpeta(self, nombre: str) -> None:
        self.__repositorio.bajar_a_subcarpeta(nombre)

    def subir_nivel(self) -> None:
        self.__repositorio.subir_nivel()

    def volver_a_raiz(self) -> None:
        self.__repositorio.volver_a_raiz()

    def cortar_subcarpeta(self, id: int) -> None:
        self.ejecutar_accion(
            "ARCHIVOS",
            "CORTAR_SUBCARPETA",
            f"Subcarpeta con ID {id}.",
            lambda: self.__repositorio.extraer_subcarpeta(id),
        )

    def copiar_subcarpeta(self, id: int) -> None:
        self.ejecutar_accion(
            "ARCHIVOS",
            "COPIAR_SUBCARPETA",
            f"Subcarpeta con ID {id}.",
            lambda: self.__repositorio.copiar_subcarpeta(id),
        )

    def pegar_subcarpeta(self) -> None:
        self.ejecutar_accion(
            "ARCHIVOS",
            "PEGAR_SUBCARPETA",
            "Contenido del portapapeles.",
            self.__repositorio.pegar_subcarpeta,
        )

    def crear_paquete(self, destino: str, contenido: object) -> PaqueteDatos:
        if isinstance(contenido, Carpeta):
            tipo = "SUBCARPETA"
        elif isinstance(contenido, Archivo):
            tipo = "ARCHIVO"
        else:
            tipo = type(contenido).__name__.upper()

        return PaqueteDatos(
            origen=self.__nombre,
            destino=destino,
            tipo=tipo,
            contenido=contenido,
        )

    def compartir_subcarpeta(self, id: int, destino: str) -> PaqueteDatos:
        def operacion() -> PaqueteDatos:
            copia = self.__repositorio.exportar_subcarpeta(id)
            return self.crear_paquete(destino, copia)

        return self.ejecutar_accion(
            "RED",
            "COMPARTIR_SUBCARPETA",
            f"Subcarpeta con ID {id} enviada a '{destino}'.",
            operacion,
        )

    def recibir_paquete(self, paquete: PaqueteDatos) -> None:
        if not isinstance(paquete, PaqueteDatos):
            raise TypeError("El paquete debe ser una instancia de PaqueteDatos.")
        if paquete.destino != self.__nombre:
            raise ValueError("El paquete no esta dirigido a este servidor.")
        if paquete.tipo != "SUBCARPETA" or not isinstance(
            paquete.contenido, Carpeta
        ):
            raise ValueError("El servidor solo puede recibir subcarpetas por ahora.")

        self.ejecutar_accion(
            "RED",
            "RECIBIR_PAQUETE",
            f"Paquete recibido desde '{paquete.origen}'.",
            lambda: self.__repositorio.importar_subcarpeta(paquete.contenido),
        )

    def registrar_evento(
        self,
        categoria: str,
        accion: str,
        resultado: str,
        detalle: str,
    ) -> None:
        self.__auditoria.registrar(categoria, accion, resultado, detalle)

    def consultar_auditoria(self) -> list[RegistroAuditoria]:
        return self.__auditoria.consultar_todo()

    def guardar_estado(self) -> None:
        def operacion() -> None:
            self.__servidor_csv.usuarios.guardar(self.__credenciales_usuarios)
            self.__repositorio.guardar()

        self.ejecutar_accion(
            "PERSISTENCIA",
            "GUARDAR_ESTADO",
            "Estado local del servidor.",
            operacion,
        )

    def cargar_estado(self) -> None:
        def operacion() -> None:
            self.__credenciales_usuarios = self.__servidor_csv.usuarios.cargar()
            self.__repositorio.cargar()

        self.ejecutar_accion(
            "PERSISTENCIA",
            "CARGAR_ESTADO",
            "Estado local del servidor.",
            operacion,
        )

    def ejecutar_accion(
        self,
        categoria: str,
        accion: str,
        detalle: str,
        operacion: Callable[[], T],
    ) -> T:
        if not callable(operacion):
            raise TypeError("La operacion debe ser invocable.")

        try:
            resultado = operacion()
        except Exception as error:
            self.registrar_evento(
                categoria,
                accion,
                "ERROR",
                f"{detalle} {type(error).__name__}: {error}",
            )
            raise

        self.registrar_evento(
            categoria,
            accion,
            "EXITOSO",
            detalle,
        )
        return resultado
