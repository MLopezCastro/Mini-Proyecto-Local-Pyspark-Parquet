
---

### ✅ Versión corregida de `EXPLICACION_TECNICA.md`

```markdown
# ⚙️ Mini-Proyecto Local PySpark – Explicación Técnica

## 🧩 Estructura del proyecto

```

Mini-Proyecto-Local-Pyspark-Parquet/
├─ .venv/                     ← entorno virtual
├─ data/
│  └─ ventas.csv              ← datos sintéticos
├─ logs/
│  └─ final.txt               ← logs o tiempos de ejecución
├─ output/
│  └─ ventas_agg/             ← salida Parquet particionada
├─ nyc_simple.py              ← script principal
└─ README.md

````

---

## ⚙️ Preparación del entorno

### 1️⃣ Crear y activar entorno virtual

```powershell
py -3.11 -m venv .venv
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
````

### 2️⃣ Instalar dependencias

```powershell
python -m pip install --upgrade pip
python -m pip install pyspark==3.5.1 pandas pyarrow faker
```

### 3️⃣ Configurar Hadoop en Windows

Spark requiere el binario `winutils.exe` para manejar archivos locales.
Descargalo y colocalo en `C:\hadoop\bin\winutils.exe`.

Luego, en PowerShell:

```powershell
$env:HADOOP_HOME = "C:\hadoop"
$env:PATH = "C:\hadoop\bin;" + $env:PATH
```

Comprobá que funciona:

```powershell
C:\hadoop\bin\winutils.exe
```

Debe mostrar la ayuda, no un error.

---

## 🧱 Script principal (`nyc_simple.py`)

### 🔹 1. Configuración inicial

Define rutas relativas (`BASE`, `CSV`, `OUT`), crea carpetas y usa `Faker` para generar datos si no existen.

### 🔹 2. Crear SparkSession

```python
spark = (
    SparkSession.builder
        .master("local[*]")
        .appName("MiniProyectoLocal")
        .config("spark.sql.shuffle.partitions", "12")
        .config("spark.hadoop.io.native.lib.available", "false")
        .getOrCreate()
)
```

* `local[*]`: usa todos los cores del equipo.
* `spark.sql.shuffle.partitions`: reduce particiones por defecto (200 → 12).
* `native.lib.available=false`: evita intentar librerías nativas ausentes en Windows.

### 🔹 3. Lectura CSV

```python
df = spark.read.csv(CSV, header=True, inferSchema=True)
df.printSchema()
```

### 🔹 4. Transformaciones

```python
df2 = df.withColumn("fecha", to_date("fecha")) \
        .withColumn("anio", year("fecha")) \
        .withColumn("mes", month("fecha"))
df_filtrado = df2.filter(col("monto") > 500)
```

### 🔹 5. Agregación

```python
agg = df_filtrado.groupBy("region", "anio", "mes") \
                 .agg(_sum("monto").alias("monto_total"))
```

### 🔹 6. Escritura Parquet

```python
agg.write.mode("overwrite") \
         .partitionBy("anio","mes") \
         .option("compression","snappy") \
         .parquet(OUT)
```

Crea una carpeta por año y mes:

```
output/ventas_agg/anio=2023/mes=1/
```

### 🔹 7. Benchmark

Lee el Parquet y mide el tiempo comparado con CSV:

```python
parq = spark.read.parquet(OUT)
parq.count()
```

### 🔹 8. Plan de ejecución

```python
agg.explain(True)
```

Muestra el plan lógico y físico (`Exchange`, `HashAggregate`, etc.).

---

## 🧪 Validaciones

* Archivos `.snappy.parquet` creados correctamente.
* Archivo `_SUCCESS` presente.
* Plan físico con `Exchange hashpartitioning`.
* Parquet mucho más rápido de leer que CSV.

---

## 🧰 Reejecución limpia

```powershell
Remove-Item -Recurse -Force .\output\ventas_agg -ErrorAction SilentlyContinue
python .\nyc_simple.py
```

---

## 🚫 Errores comunes

| Error                  | Causa                          | Solución                                |
| ---------------------- | ------------------------------ | --------------------------------------- |
| `HADOOP_HOME unset`    | No está configurado `winutils` | Setear `$env:HADOOP_HOME` y `$env:PATH` |
| `UnsatisfiedLinkError` | Binario winutils incorrecto    | Descargar versión Hadoop 3.3.x          |
| `Parquet no aparece`   | OUT apuntaba a `C:\spark_out`  | Corregir a `.\\output\\ventas_agg`      |
| `Java not found`       | Java ausente o PATH roto       | Instalar JDK 11 o superior              |

---

## 🧩 .gitignore recomendado

```
.venv/
data/*.csv
output/**
logs/**
*.log
```

---

## ✅ Conclusión

Este proyecto demuestra cómo correr **PySpark localmente en Windows**,
desde la configuración de entorno hasta la escritura optimizada en **Parquet particionado**.

El resultado es un pipeline reproducible, portable y que muestra los fundamentos del procesamiento distribuido de datos con Spark SQL.

```

---


```
