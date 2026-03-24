# ETL - Machine Learning (Schema Matching)

Sistema ETL (Extract, Transform, Load) que utiliza Machine Learning para realizar matching inteligente de esquemas entre diferentes plataformas empresariales, como **NetSuite** y **Oracle Primavera Unifier**. El objetivo principal es identificar y emparejar automáticamente campos equivalentes entre sistemas heterogéneos mediante análisis semántico y redes neuronales.

---

## Tabla de Contenidos

- [Descripción General](#descripción-general)
- [Arquitectura General](#arquitectura-general)
- [Pipeline ETL](#pipeline-etl)
- [Tecnologías](#tecnologías)
- [Requisitos Previos](#requisitos-previos)
- [Instalación](#instalación)
- [Estructura de la Base de Datos MongoDB](#estructura-de-la-base-de-datos-mongodb)
- [Modelo de Entrenamiento](#modelo-de-entrenamiento)
- [Contribuir](#contribuir)
- [Licencia](#licencia)

---

## Descripción General

En integraciones empresariales es habitual necesitar mapear campos entre dos sistemas que usan nombres, estructuras y convenciones diferentes. Este proyecto automatiza ese proceso mediante:

1. **Configuración semántica** — Gestiona tokens diferenciadores, tokens de identidad, stopwords y grupos semánticos en MongoDB para preprocesar los nombres de campos.
2. **Entrenamiento de modelos ML** — Almacena pares de campos etiquetados (match / no match) para entrenar modelos de matching.
3. **Core Neuronal** *(en desarrollo)* — Módulo de redes neuronales para realizar la predicción de equivalencia entre campos.

---

## Arquitectura General

```mermaid
graph TB
    subgraph Fuentes["Fuentes de Datos"]
        NS[NetSuite API]
        UNI[Oracle Primavera Unifier]
        OTHER[Otros Sistemas]
    end

    subgraph ETL["Pipeline ETL"]
        EXT[Extracción]
        TRANS[Transformación y Normalización]
        LOAD[Carga]
    end

    subgraph ML["Motor de Machine Learning"]
        SEM[Configuración Semántica]
        TRAIN[Datos de Entrenamiento]
        MODEL[Modelo Neuronal]
    end

    subgraph Destino["Destino"]
        MAP[Mapeo de Campos Identificado]
        DB[(MongoDB)]
    end

    NS --> EXT
    UNI --> EXT
    OTHER --> EXT
    EXT --> TRANS
    TRANS --> LOAD

    SEM --> TRANS
    TRAIN --> MODEL
    MODEL --> MAP
    LOAD --> DB
    MAP --> LOAD
```

---

## Pipeline ETL

El flujo completo del proceso ETL se representa a continuación:

```mermaid
flowchart LR
    A[API Origen] -->|JSON| B(Extracción de Esquema)
    B --> C{Preprocesamiento}
    C -->|Tokens| D[Normalización Semántica]
    D --> E[Generación de Pares]
    E --> F{Modelo ML}
    F -->|Match| G[Mapeo Confirmado]
    F -->|No Match| H[Descartado]
    G --> I[Carga al Destino ETL]

    style A fill:#4a9eff,color:#fff
    style F fill:#ff6b6b,color:#fff
    style G fill:#51cf66,color:#fff
    style I fill:#845ef7,color:#fff
```

### Detalle del Preprocesamiento

```mermaid
flowchart TD
    INPUT[Campo de Entrada] --> STOP{Eliminar Stopwords}
    STOP --> IDENT{Detectar Tokens de Identidad}
    IDENT --> DIFF{Aplicar Tokens Diferenciadores}
    DIFF --> GROUP{Resolver Grupos Semánticos}
    GROUP --> OUTPUT[Campo Normalizado]

    subgraph MongoDB
        SW[(stopwords)]
        TI[(tokens_identidad)]
        TD2[(tokens_diferenciadores)]
        GS[(grupos_semanticos)]
    end

    SW -.-> STOP
    TI -.-> IDENT
    TD2 -.-> DIFF
    GS -.-> GROUP
```

---

## Tecnologías

```mermaid
graph LR
    subgraph Backend
        PY[Python 3.10+]
        FA[FastAPI]
        UV[Uvicorn]
    end

    subgraph Datos
        MG[(MongoDB)]
    end

    subgraph ML["Machine Learning"]
        NC[NeuronalCore - En Desarrollo]
    end

    PY --> FA
    FA --> UV
    PY --> MG
    PY --> NC
```

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

## Estructura de la Base de Datos MongoDB

La clase `SemanticConfigMongoDb` define la arquitectura de base de datos para almacenar configuraciones semánticas y datos de entrenamiento.

### Modelo Entidad-Relación

```mermaid
erDiagram
    TOKENS_DIFERENCIADORES {
        string token UK
        string categoria
        boolean activo
        string notas
        datetime fecha_alta
        datetime fecha_modificacion
    }

    TOKENS_IDENTIDAD {
        string token UK
        string tipo
        boolean activo
        datetime fecha_alta
    }

    STOPWORDS {
        string token UK
        string contexto
        boolean activo
        datetime fecha_alta
    }

    GRUPOS_SEMANTICOS {
        string grupo
        string token
        string idioma
        boolean activo
        datetime fecha_alta
    }

    CAMBIOS_LOG {
        string coleccion
        string accion
        string token
        object detalles
        datetime fecha
        string usuario
    }

    TRAINING_DATASETS {
        ObjectId _id PK
        string dataset_hash UK
        string nombre
        string version
        object metadata
        datetime fecha_creacion
        datetime fecha_modificacion
        boolean activo
    }

    TRAINING_PAIRS {
        ObjectId dataset_id FK
        int indice
        string field_a
        string field_b
        int match
        array tokens_a
        array tokens_b
        datetime fecha_creacion
    }

    TRAINING_DATASETS ||--o{ TRAINING_PAIRS : "contiene"
    TOKENS_DIFERENCIADORES ||--o{ CAMBIOS_LOG : "registra"
    TOKENS_IDENTIDAD ||--o{ CAMBIOS_LOG : "registra"
    STOPWORDS ||--o{ CAMBIOS_LOG : "registra"
    GRUPOS_SEMANTICOS ||--o{ CAMBIOS_LOG : "registra"
```

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

---

## Modelo de Entrenamiento

El flujo de entrenamiento del modelo de matching sigue el siguiente proceso:

```mermaid
flowchart TD
    A[Recopilar Pares de Campos] --> B[Etiquetar: Match / No Match]
    B --> C[Almacenar en training_pairs]
    C --> D[Generar Dataset con Hash SHA256]
    D --> E[Preprocesar con Configuración Semántica]
    E --> F[Entrenar Modelo Neuronal]
    F --> G{Evaluar Precisión}
    G -->|Aceptable| H[Modelo Listo para Producción]
    G -->|Insuficiente| I[Ajustar Hiperparámetros]
    I --> F

    style H fill:#51cf66,color:#fff
    style G fill:#ffd43b,color:#333
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
