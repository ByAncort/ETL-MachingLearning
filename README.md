# ETL - Machine Learning (Schema Matching)

Sistema ETL (Extract, Transform, Load) que utiliza Machine Learning para realizar matching inteligente de esquemas entre diferentes plataformas empresariales, como **NetSuite** y **Oracle Primavera Unifier**. El objetivo principal es identificar y emparejar automáticamente campos equivalentes entre sistemas heterogéneos mediante análisis semántico y redes neuronales.

---

## Tabla de Contenidos

- [Descripción General](#descripción-general)
- [Arquitectura del Proyecto](#arquitectura-del-proyecto)
- [Tecnologías](#tecnologías)
- [Requisitos Previos](#requisitos-previos)
- [Instalación](#instalación)
- [Uso](#uso)
  - [Normalizador de JSON](#normalizador-de-json)
  - [API REST](#api-rest)
- [Estructura de la Base de Datos MongoDB](#estructura-de-la-base-de-datos-mongodb)
- [Contribuir](#contribuir)
- [Licencia](#licencia)

---

## Descripción General

En integraciones empresariales es habitual necesitar mapear campos entre dos sistemas que usan nombres, estructuras y convenciones diferentes. Este proyecto automatiza ese proceso mediante:

1. **Normalización de esquemas JSON** — Analiza estructuras JSON complejas y las aplana en listas de campos con su tipo y valores.
2. **Configuración semántica** — Gestiona tokens diferenciadores, tokens de identidad, stopwords y grupos semánticos en MongoDB para preprocesar los nombres de campos.
3. **Entrenamiento de modelos ML** — Almacena pares de campos etiquetados (match / no match) para entrenar modelos de matching.
4. **Core Neuronal** *(en desarrollo)* — Módulo de redes neuronales para realizar la predicción de equivalencia entre campos.

---

## Arquitectura del Proyecto

```
ETL-MachingLearning/
│
├── SchemeMatcher/              # Módulo principal de matching de esquemas
│   ├── main.py                 # API REST con FastAPI
│   ├── Service/
│   │   └── normalizer.py       # Normalizador y analizador de estructuras JSON
│   ├── jsonExample/
│   │   ├── netsuite.json       # Ejemplo de respuesta de API NetSuite
│   │   └── unifier.json        # Ejemplo de respuesta de Oracle Primavera Unifier
│   └── test_main.http          # Archivo de pruebas HTTP para los endpoints
│
├── NeuronalCore/               # Módulo de redes neuronales (en desarrollo)
│
└── README.md                   # Documentación del proyecto
```

---

## Tecnologías

| Componente         | Tecnología                                        |
|--------------------|---------------------------------------------------|
| Lenguaje           | Python 3.10+                                      |
| Framework API      | [FastAPI](https://fastapi.tiangolo.com/)           |
| Base de Datos      | [MongoDB](https://www.mongodb.com/)                |
| Machine Learning   | En desarrollo (NeuronalCore)                       |
| Servidor ASGI      | [Uvicorn](https://www.uvicorn.org/)                |

---

## Requisitos Previos

- **Python** 3.10 o superior
- **MongoDB** en ejecución (local o remoto)
- **pip** (gestor de paquetes de Python)

---

## Instalación

1. **Clonar el repositorio:**

   ```bash
   git clone https://github.com/ByAncort/ETL-MachingLearning.git
   cd ETL-MachingLearning
   ```

2. **Crear un entorno virtual (recomendado):**

   ```bash
   python -m venv venv
   source venv/bin/activate        # Linux / macOS
   # venv\Scripts\activate         # Windows
   ```

3. **Instalar dependencias:**

   ```bash
   pip install fastapi uvicorn pymongo
   ```

4. **Configurar MongoDB:**

   Asegúrate de tener una instancia de MongoDB corriendo. Por defecto, la configuración espera una conexión en `localhost:27017`.

---

## Uso

### Normalizador de JSON

El módulo `normalizer.py` analiza estructuras JSON anidadas y genera una lista plana de campos con su tipo y valores. Es útil para comparar esquemas de diferentes sistemas.

```bash
cd SchemeMatcher
python Service/normalizer.py
```

**Salida de ejemplo:**

```
=== ESTRUCTURA NETSUITE ===
{'campo': 'links', 'tipo': 'array'}
{'campo': 'links.rel', 'tipo': 'str', 'value': 'self'}
{'campo': 'links.href', 'tipo': 'str', 'value': 'https://...'}
{'campo': 'count', 'tipo': 'int', 'value': '2'}
{'campo': 'items', 'tipo': 'array'}
{'campo': 'items.custbody_bea_bp_primavera', 'tipo': 'str', 'value': 'Prefactura de Arrendamiento'}
...

=== ESTRUCTURA UNIFIER ===
{'campo': 'options.bpname', 'tipo': 'str', 'value': 'Prefactura de Arrendamiento'}
{'campo': 'data', 'tipo': 'array'}
{'campo': 'data.uuu_record_last_update_date', 'tipo': 'str', 'value': '02-19-2026 15:19:46'}
...
```

### API REST

Inicia el servidor FastAPI con Uvicorn:

```bash
cd SchemeMatcher
uvicorn main:app --reload
```

El servidor estará disponible en `http://127.0.0.1:8000`.

**Endpoints disponibles:**

| Método | Ruta            | Descripción                  |
|--------|-----------------|------------------------------|
| GET    | `/`             | Mensaje de bienvenida        |
| GET    | `/hello/{name}` | Saludo personalizado         |

**Documentación interactiva:**

- Swagger UI: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- ReDoc: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

---

## Estructura de la Base de Datos MongoDB

La clase `SemanticConfigMongoDb` define la arquitectura de base de datos para almacenar configuraciones semánticas y datos de entrenamiento.

### Colecciones de Configuración Semántica

Almacenan tokens clasificados para análisis semántico y preprocesamiento de texto.

| Colección                | Propósito                                   | Índice Principal                        |
|--------------------------|---------------------------------------------|-----------------------------------------|
| `tokens_diferenciadores` | Tokens que discriminan entre conceptos      | `token` (único)                         |
| `tokens_identidad`       | Tokens de identificadores únicos (RFC, CURP) | `token` (único)                         |
| `stopwords`              | Palabras eliminadas en preprocesamiento     | `token` (único)                         |
| `grupos_semanticos`      | Agrupación semántica de tokens              | `(grupo, token, idioma)` único, `token` |
| `cambios_log`            | Auditoría de cambios                        | (ninguno)                               |

### Colecciones de Datos de Entrenamiento

| Colección           | Propósito                                      | Índices Principales                                               |
|---------------------|-------------------------------------------------|-------------------------------------------------------------------|
| `training_datasets` | Metadatos de datasets (hash SHA256, versión)   | `dataset_hash` único, `fecha_creacion`, `version`                 |
| `training_pairs`    | Pares de campos con etiqueta match (1) o no (0) | `(dataset_id, field_a, field_b)` único, `(dataset_id, match)`     |

### Flujo de Datos

```
tokens_diferenciadores ─┐
tokens_identidad ───────┤
stopwords ──────────────┼──> Preprocesamiento de campos
grupos_semanticos ──────┘
                                    │
                                    v
                          training_datasets (1:N) ──> training_pairs
                                    │
                                    v
                            Modelo ML (NeuronalCore)
```

**Características clave:**

- **Caché en memoria** para acceso rápido a tokens activos sin consultas repetidas a MongoDB.
- **Índices únicos** que previenen duplicados en tokens y grupos semánticos.
- **Inserciones en lotes** de 1000 registros para `training_pairs`.
- **Hash SHA256** para identificar datasets y evitar duplicados automáticamente.
- **Log de auditoría** en `cambios_log` para rastrear modificaciones.

---

## Contribuir

1. Haz un fork del repositorio.
2. Crea una rama para tu feature: `git checkout -b feature/nueva-funcionalidad`
3. Realiza tus cambios y haz commit: `git commit -m "Agregar nueva funcionalidad"`
4. Sube tu rama: `git push origin feature/nueva-funcionalidad`
5. Abre un Pull Request.

---

## Licencia

Este proyecto no tiene una licencia definida actualmente. Contacta al autor para más información.
