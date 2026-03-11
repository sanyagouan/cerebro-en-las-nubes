"""
Servicio de gestión de Clientes en Airtable.

Este servicio maneja todas las operaciones CRUD para:
- Clientes (información principal)
- Preferencias de clientes (mesa, comida, alergias, etc.)
- Notas de clientes (observaciones del staff)

Base Airtable: appQ2ZXAR68cqDmJt
Tablas:
- Clientes: tblPcVRnFTKDu7Z9t
- ClientePreferencias: tbl6xjlRuyJZMmzOV
- ClienteNotas: tbl5RZ31kxSOkGe0U

⚠️ IMPORTANTE: Campo Es_Importante en Airtable es singleSelect ("Sí"/"No"),
   NO es checkbox. Requiere conversión Boolean <-> String.
"""

from typing import List, Optional
from datetime import datetime
from pyairtable import Api
from src.core.entities.cliente import Cliente, ClientePreferencia, ClienteNota
import os


class ClienteService:
    """Servicio para gestión de clientes en Airtable.
    
    Maneja CRUD completo de clientes y sus relaciones (preferencias y notas).
    Incluye conversión automática entre boolean (Python) y strings (Airtable).
    
    Attributes:
        api: Instancia de pyairtable Api
        base_id: ID de la base Airtable
        table_clientes: Tabla principal de Clientes
        table_preferencias: Tabla de ClientePreferencias
        table_notas: Tabla de ClienteNotas
    """
    
    def __init__(self):
        """Inicializa el servicio con conexión a Airtable."""
        self.api = Api(os.getenv("AIRTABLE_API_KEY"))
        self.base_id = "appQ2ZXAR68cqDmJt"
        
        # IDs de tablas
        self.table_clientes = self.api.table(self.base_id, "tblPcVRnFTKDu7Z9t")
        self.table_preferencias = self.api.table(self.base_id, "tbl6xjlRuyJZMmzOV")
        self.table_notas = self.api.table(self.base_id, "tbl5RZ31kxSOkGe0U")
    
    # ========== CONVERSIÓN BOOLEAN <-> STRING ==========
    
    @staticmethod
    def bool_to_airtable(value: bool) -> str:
        """Convierte boolean a string Airtable.
        
        ⚠️ IMPORTANTE: Airtable solo acepta "Sí" o "No" (con acento).
        Usar "Si" (sin acento) causa HTTP 422 error.
        
        Args:
            value: True o False
        
        Returns:
            "Sí" si True, "No" si False
        
        Examples:
            >>> ClienteService.bool_to_airtable(True)
            "Sí"
            >>> ClienteService.bool_to_airtable(False)
            "No"
        """
        return "Sí" if value else "No"
    
    @staticmethod
    def airtable_to_bool(value: str) -> bool:
        """Convierte string Airtable a boolean.
        
        Maneja múltiples variaciones de input para robustez.
        
        Args:
            value: "Sí", "No", "Si" (sin acento), "YES", "NO", etc.
        
        Returns:
            True si "Sí"/"Si"/"YES"/etc., False en caso contrario
        
        Examples:
            >>> ClienteService.airtable_to_bool("Sí")
            True
            >>> ClienteService.airtable_to_bool("Si")  # Sin acento
            True
            >>> ClienteService.airtable_to_bool("YES")
            True
            >>> ClienteService.airtable_to_bool("No")
            False
            >>> ClienteService.airtable_to_bool("")
            False
        """
        if not value:
            return False
        
        value_normalized = value.strip().lower()
        return value_normalized in ["sí", "si", "yes", "true", "1"]
    
    # ========== CLIENTES ==========
    
    async def list_all(self, include_relations: bool = False) -> List[Cliente]:
        """Lista todos los clientes.
        
        Args:
            include_relations: Si True, incluye preferencias y notas
                             (más lento debido a queries adicionales)
        
        Returns:
            Lista de clientes ordenados por nombre
        
        Example:
            >>> clientes = await service.list_all(include_relations=True)
            >>> for c in clientes:
            ...     print(f"{c.nombre}: {len(c.preferencias)} preferencias")
        """
        records = self.table_clientes.all()
        
        clientes = []
        for record in records:
            cliente = self._record_to_cliente(record)
            
            if include_relations:
                cliente.preferencias = await self.get_preferencias(cliente.id)
                cliente.notas = await self.get_notas(cliente.id)
            
            clientes.append(cliente)
        
        # Ordenar por nombre
        clientes.sort(key=lambda c: c.nombre)
        
        return clientes
    
    async def get_by_phone(self, telefono: str, include_relations: bool = True) -> Optional[Cliente]:
        """Busca cliente por teléfono.
        
        Args:
            telefono: Teléfono en formato E.164 (+34XXXXXXXXX)
            include_relations: Si True, incluye preferencias y notas
        
        Returns:
            Cliente si existe, None si no se encuentra
        
        Example:
            >>> cliente = await service.get_by_phone("+34600123456")
            >>> if cliente:
            ...     print(f"Encontrado: {cliente.nombre}")
            ... else:
            ...     print("No existe")
        """
        formula = f"{{Teléfono}} = '{telefono}'"
        records = self.table_clientes.all(formula=formula)
        
        if not records:
            return None
        
        cliente = self._record_to_cliente(records[0])
        
        if include_relations:
            cliente.preferencias = await self.get_preferencias(cliente.id)
            cliente.notas = await self.get_notas(cliente.id)
        
        return cliente
    
    async def create(self, cliente_data: dict) -> Cliente:
        """Crea nuevo cliente.
        
        Args:
            cliente_data: Diccionario con datos del cliente
                Required: nombre, telefono
                Optional: email, notas_generales
        
        Returns:
            Cliente creado con ID asignado
        
        Raises:
            ValueError: Si el cliente ya existe (por teléfono)
        
        Example:
            >>> cliente = await service.create({
            ...     "nombre": "Juan Pérez",
            ...     "telefono": "+34600123456",
            ...     "email": "juan@example.com"
            ... })
            >>> print(cliente.id)  # "recXXXXXXXXXXXXXX"
        """
        # Validar que no exista
        existing = await self.get_by_phone(cliente_data["telefono"])
        if existing:
            raise ValueError(f"Cliente con teléfono {cliente_data['telefono']} ya existe")
        
        # Preparar datos para Airtable
        # ⚠️ Primera_Reserva es tipo DATE, no datetime - solo acepta YYYY-MM-DD
        primera_reserva = cliente_data.get("primera_reserva")
        if primera_reserva:
            # Si viene como datetime, extraer solo la fecha
            if isinstance(primera_reserva, str) and "T" in primera_reserva:
                primera_reserva = primera_reserva.split("T")[0]
        else:
            primera_reserva = datetime.now().strftime("%Y-%m-%d")
        
        airtable_data = {
            "Nombre": cliente_data["nombre"],
            "Teléfono": cliente_data["telefono"],
            "Email": cliente_data.get("email"),
            "Primera_Reserva": primera_reserva,  # Solo fecha YYYY-MM-DD
            "Total_Reservas": cliente_data.get("total_visitas", 0),
            "Notas_Staff": cliente_data.get("notas_generales")
        }
        
        # Crear en Airtable
        record = self.table_clientes.create(airtable_data)
        
        return self._record_to_cliente(record)
    
    async def update(self, cliente_id: str, updates: dict) -> Cliente:
        """Actualiza cliente existente.
        
        Args:
            cliente_id: ID del cliente en Airtable
            updates: Diccionario con campos a actualizar
                Campos válidos: nombre, email, total_visitas, 
                              ultima_visita, notas_generales
        
        Returns:
            Cliente actualizado
        
        Note:
            No se puede cambiar el teléfono (campo clave).
        
        Example:
            >>> cliente = await service.update("recXXX", {
            ...     "total_visitas": 5,
            ...     "ultima_visita": datetime.now().isoformat()
            ... })
        """
        # Mapear campos Python -> Airtable
        airtable_updates = {}
        field_map = {
            "nombre": "Nombre",
            "email": "Email",
            "total_visitas": "Total_Visitas",
            "ultima_reserva": "Ultima_Reserva",
            "notas_generales": "Notas_Generales"
        }
        
        for py_field, air_field in field_map.items():
            if py_field in updates:
                airtable_updates[air_field] = updates[py_field]
        
        # Actualizar
        record = self.table_clientes.update(cliente_id, airtable_updates)
        
        return self._record_to_cliente(record)
    
    # ========== PREFERENCIAS ==========
    
    async def get_preferencias(self, cliente_id: str) -> List[ClientePreferencia]:
        """Obtiene preferencias de un cliente.
        
        Args:
            cliente_id: ID del cliente en Airtable
        
        Returns:
            Lista de preferencias ordenadas por fecha de creación (más reciente primero)
        
        Example:
            >>> preferencias = await service.get_preferencias("recXXX")
            >>> for p in preferencias:
            ...     print(f"{p.tipo}: {p.descripcion}")
        
        Note:
            La tabla ClientePreferencias NO tiene campo Es_Importante.
            Ese campo solo existe en ClienteNotas.
        """
        # Filtrar por linked record
        # FIND busca el cliente_id en el array de linked records
        formula = f"FIND('{cliente_id}', ARRAYJOIN({{Cliente}}))"
        records = self.table_preferencias.all(formula=formula)
        
        preferencias = []
        for record in records:
            fields = record["fields"]
            
            # ⚠️ NOTA: ClientePreferencias NO tiene campo Es_Importante
            pref = ClientePreferencia(
                id=record["id"],
                cliente_id=cliente_id,
                tipo=fields.get("Tipo", "Otros"),
                descripcion=fields.get("Descripcion", ""),
                creado=fields.get("Fecha_Creacion")  # Campo correcto en Airtable
            )
            preferencias.append(pref)
        
        # Ordenar por fecha de creación (más reciente primero)
        preferencias.sort(key=lambda p: p.creado or datetime.min, reverse=True)
        
        return preferencias
    
    async def add_preferencia(self, cliente_id: str, preferencia_data: dict) -> ClientePreferencia:
        """Añade preferencia a un cliente.
        
        Args:
            cliente_id: ID del cliente
            preferencia_data: Diccionario con datos de la preferencia
                Required: tipo, descripcion
        
        Returns:
            Preferencia creada con ID asignado
        
        Example:
            >>> pref = await service.add_preferencia("recXXX", {
            ...     "tipo": "Alergias",
            ...     "descripcion": "Alérgico a mariscos"
            ... })
        
        Note:
            ⚠️ La tabla ClientePreferencias NO tiene campo Es_Importante.
            Ese campo solo existe en la tabla ClienteNotas.
        """
        airtable_data = {
            "Cliente": [cliente_id],  # Linked record (array de IDs)
            "Tipo": preferencia_data["tipo"],
            "Descripcion": preferencia_data["descripcion"],
            "Fecha_Creacion": datetime.now().isoformat()  # Timestamp actual
        }
        
        record = self.table_preferencias.create(airtable_data)
        
        return ClientePreferencia(
            id=record["id"],
            cliente_id=cliente_id,
            tipo=record["fields"]["Tipo"],
            descripcion=record["fields"]["Descripcion"],
            creado=record["fields"].get("Fecha_Creacion")
        )
    
    # ========== NOTAS ==========
    
    async def get_notas(self, cliente_id: str) -> List[ClienteNota]:
        """Obtiene notas de un cliente.
        
        Args:
            cliente_id: ID del cliente
        
        Returns:
            Lista de notas ordenadas por fecha (más reciente primero)
        
        Example:
            >>> notas = await service.get_notas("recXXX")
            >>> if notas:
            ...     print(f"Última nota: {notas[0].nota}")
        """
        # Filtrar por linked record
        formula = f"FIND('{cliente_id}', ARRAYJOIN({{Cliente}}))"
        records = self.table_notas.all(formula=formula, sort=["-Fecha_Creacion"])
        
        notas = []
        for record in records:
            fields = record["fields"]
            
            nota = ClienteNota(
                id=record["id"],
                cliente_id=cliente_id,
                contenido=fields.get("Contenido", ""),
                fecha_creacion=fields.get("Fecha_Creacion", datetime.now().isoformat()),
                staff_nombre=fields.get("Staff_Nombre", "Sistema")
            )
            notas.append(nota)
        
        return notas
    
    async def add_nota(self, cliente_id: str, nota_data: dict) -> ClienteNota:
        """Añade nota a un cliente.
        
        Args:
            cliente_id: ID del cliente
            nota_data: Diccionario con datos de la nota
                Required: nota
                Optional: autor (default: "Sistema"), fecha (default: now)
        
        Returns:
            Nota creada con ID asignado
        
        Example:
            >>> nota = await service.add_nota("recXXX", {
            ...     "nota": "Cliente VIP - siempre mesa en terraza",
            ...     "autor": "Alba"
            ... })
        """
        airtable_data = {
            "Cliente": [cliente_id],  # Linked record
            "Contenido": nota_data["contenido"],
            "Fecha_Creacion": nota_data.get("fecha_creacion", datetime.now().isoformat()),
            "Staff_Nombre": nota_data.get("staff_nombre", "Sistema")
        }
        
        record = self.table_notas.create(airtable_data)
        
        return ClienteNota(
            id=record["id"],
            cliente_id=cliente_id,
            contenido=record["fields"]["Contenido"],
            fecha_creacion=record["fields"]["Fecha_Creacion"],
            staff_nombre=record["fields"]["Staff_Nombre"]
        )
    
    # ========== UTILIDADES ==========
    
    def _record_to_cliente(self, record: dict) -> Cliente:
        """Convierte record de Airtable a modelo Cliente.
        
        Args:
            record: Record de Airtable con estructura:
                {"id": "recXXX", "fields": {...}, "createdTime": "..."}
        
        Returns:
            Instancia de Cliente Pydantic
        """
        fields = record["fields"]
        
        return Cliente(
            id=record["id"],
            nombre=fields.get("Nombre", ""),
            telefono=fields.get("Teléfono", ""),
            email=fields.get("Email"),
            primera_reserva=fields.get("Primera_Reserva"),
            total_visitas=fields.get("Total_Visitas", 0),
            ultima_reserva=fields.get("Ultima_Reserva"),
            notas_generales=fields.get("Notas_Generales")
        )
