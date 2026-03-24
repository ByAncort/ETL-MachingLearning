## Arquitectura de la Base de Datos MongoDB

La clase `SemanticConfigMongoDb` define una estructura de base de datos diseñada para almacenar configuraciones semánticas y datos de entrenamiento para un modelo de aprendizaje automático (probablemente para matching de campos/entidades). A continuación se describe cada colección, su propósito, esquema e índices.

---

### 1. **Colecciones de Configuración Semántica**

Estas colecciones almacenan tokens clasificados que se usan para análisis semántico y preprocesamiento de texto.

#### `tokens_diferenciadores`
- **Propósito:** Tokens que ayudan a discriminar entre conceptos (ej. *customer*, *vendor*, *sale*).
- **Esquema:**
  - `token` (string, único)
  - `categoria` (string, opcional)
  - `activo` (boolean)
  - `notas` (string, opcional)
  - `fecha_alta` (datetime)
  - `fecha_modificacion` (datetime)
- **Índice:** `token` único.

#### `tokens_identidad`
- **Propósito:** Tokens que representan identificadores únicos (ej. *rfc*, *curp*, *uuid*).
- **Esquema:**
  - `token` (string, único)
  - `tipo` (string, fijo "identidad")
  - `activo` (boolean)
  - `fecha_alta` (datetime)
- **Índice:** `token` único.

#### `stopwords`
- **Propósito:** Palabras o términos que se eliminan en el preprocesamiento (ej. *cust*, *field*).
- **Esquema:**
  - `token` (string, único)
  - `contexto` (string, ej. "sistema")
  - `activo` (boolean)
  - `fecha_alta` (datetime)
- **Índice:** `token` único.

#### `grupos_semanticos`
- **Propósito:** Agrupar tokens bajo un mismo concepto semántico (ej. grupo "email" con tokens *correo*, *mail*, *email*).
- **Esquema:**
  - `grupo` (string)
  - `token` (string)
  - `idioma` (string, ej. "es")
  - `activo` (boolean)
  - `fecha_alta` (datetime)
- **Índices:**
  - Compuesto único: `(grupo, token, idioma)`
  - Simple en `token` (para búsquedas inversas)

#### `cambios_log`
- **Propósito:** Auditoría de cambios en las colecciones anteriores.
- **Esquema:**
  - `coleccion` (string)
  - `accion` (string, ej. "INSERT", "UPDATE")
  - `token` (string, opcional)
  - `detalles` (objeto, opcional)
  - `fecha` (datetime)
  - `usuario` (string, por defecto "system")
- **Sin índices explícitos** (pueden añadirse según necesidad).

---

### 2. **Colecciones de Datos de Entrenamiento**

Estas colecciones almacenan datasets utilizados para entrenar el modelo.

#### `training_datasets`
- **Propósito:** Metadatos de cada dataset de entrenamiento.
- **Esquema:**
  - `_id` (ObjectId, automático)
  - `dataset_hash` (string, único) – hash SHA256 del contenido para detectar duplicados.
  - `nombre` (string) – nombre descriptivo.
  - `version` (string) – versión del dataset.
  - `metadata` (objeto) – contiene:
    - `total_pares` (int)
    - `positivos` (int)
    - `negativos` (int)
    - `balance_ratio` (float)
    - `fecha_generacion` (datetime)
    - `config` (objeto, opcional) – parámetros de generación.
  - `fecha_creacion` (datetime)
  - `fecha_modificacion` (datetime)
  - `activo` (boolean) – indica si el dataset está vigente.
- **Índices:**
  - Único en `dataset_hash`
  - Descendente en `fecha_creacion`
  - Simple en `version`

#### `training_pairs`
- **Propósito:** Pares individuales de campos con su etiqueta de matching.
- **Esquema:**
  - `dataset_id` (ObjectId) – referencia al dataset padre.
  - `indice` (int) – posición dentro del dataset.
  - `field_a` (string) – primer campo.
  - `field_b` (string) – segundo campo.
  - `match` (int) – 1 si son equivalentes, 0 si no.
  - `tokens_a` (array de strings, opcional) – tokens precomputados para optimización.
  - `tokens_b` (array de strings, opcional)
  - `fecha_creacion` (datetime)
- **Índices:**
  - Compuesto único: `(dataset_id, field_a, field_b)`
  - Compuesto: `(dataset_id, match)` para búsquedas rápidas.

---

### 3. **Relaciones y Flujo de Datos**

- **Relación 1:N** entre `training_datasets` y `training_pairs` mediante `dataset_id`.
- **Cache en memoria:** La clase mantiene cachés (`_cache_diferenciadores`, `_cache_identidad`, etc.) para acceder rápidamente a los tokens activos sin consultar MongoDB cada vez. Estos cachés se invalidan cuando se agregan o actualizan tokens.
- **Métodos principales:**
  - `guardar_dataset`: inserta metadatos en `training_datasets` y los pares en `training_pairs` en lotes.
  - `cargar_dataset`: recupera pares, con opción de balanceo y formato de salida.
  - `exportar_dataset_json`: exporta un dataset a archivo JSON.
  - Métodos para gestionar tokens y grupos semánticos (`add_token_diferenciador`, `add_to_grupo_semantico`, etc.).
  - Propiedades (`TOKENS_DIFERENCIADORES`, `GRUPOS_SEMANTICOS`, etc.) que exponen los cachés.
  - `migrar_datos_iniciales`: carga datos por defecto en las colecciones.

---

### 4. **Consideraciones de Diseño**

- **Optimización de lectura:** Se utilizan cachés en memoria para los tokens activos, reduciendo latencia.
- **Integridad:** Índices únicos previenen duplicados en tokens y grupos semánticos.
- **Auditoría:** `cambios_log` registra todas las modificaciones (aunque no se usa en todos los métodos, pero está disponible).
- **Flexibilidad:** Los datasets se identifican por hash, permitiendo evitar duplicados automáticamente.
- **Escalabilidad:** Las inserciones en `training_pairs` se realizan en lotes de 1000 para mejorar rendimiento.

---

### 5. **Resumen de Colecciones**

| Colección            | Propósito                                        | Índices Principales                              |
|----------------------|--------------------------------------------------|--------------------------------------------------|
| `tokens_diferenciadores` | Tokens discriminadores                          | `token` único                                    |
| `tokens_identidad`       | Tokens de identidad                             | `token` único                                    |
| `stopwords`              | Palabras a eliminar en preprocesamiento         | `token` único                                    |
| `grupos_semanticos`      | Agrupación semántica de tokens                  | `(grupo, token, idioma)` único, `token`          |
| `cambios_log`            | Auditoría de cambios                            | (ninguno)                                        |
| `training_datasets`      | Metadatos de datasets de entrenamiento          | `dataset_hash` único, `fecha_creacion`, `version`|
| `training_pairs`         | Pares de campos con etiquetas                   | `(dataset_id, field_a, field_b)` único, `(dataset_id, match)` |

Esta arquitectura proporciona una base sólida para gestionar configuraciones semánticas y datos de entrenamiento, con mecanismos de caché para un acceso eficiente y persistencia confiable.
