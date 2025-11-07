
---

# 🚀 Mini-Proyecto Local PySpark – Procesamiento y Escritura Parquet

## 🧠 Descripción general

Este proyecto demuestra cómo ejecutar **Apache Spark localmente en Windows** utilizando **PySpark**, sin necesidad de un clúster real.
El objetivo fue crear un **pipeline completo de procesamiento de datos**: leer un CSV sintético, transformarlo, filtrar y escribir los resultados en formato **Parquet particionado y comprimido**.

Además, se resolvió el clásico error de entorno en Windows relacionado con **Hadoop (`winutils.exe`)**, lo que permitió que Spark escribiera correctamente los archivos de salida en disco.

---

## 🧩 Estructura del proyecto

```
Mini-Proyecto-Local-Pyspark-Parquet/
├─ .venv/                     ← entorno virtual
├─ data/
│  └─ ventas.csv              ← dataset sintético generado automáticamente
├─ logs/
│  └─ final.txt               ← logs y tiempos de ejecución
├─ output/
│  └─ ventas_agg/             ← salida Parquet particionada
├─ nyc_simple.py              ← script principal
├─ EXPLICACION_TECNICA.md     ← documentación técnica
├─ EXPLICACION_GENERAL.md     ← documentación conceptual
└─ README.md
```

---

## ⚙️ Preparación del entorno

### 1️⃣ Crear y activar entorno virtual

```powershell
py -3.11 -m venv .venv
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

### 2️⃣ Instalar dependencias

```powershell
python -m pip install --upgrade pip
python -m pip install pyspark==3.5.1 pandas pyarrow faker
```

---

## 🧱 Configuración de Hadoop en Windows

Spark requiere `winutils.exe` para crear y manejar archivos locales en sistemas Windows.
Sin este archivo, aparece el error:

```
java.io.FileNotFoundException: HADOOP_HOME and hadoop.home.dir are unset
```

### 🔹 Solución aplicada

1. Se creó la carpeta:

   ```
   C:\hadoop\bin\
   ```
2. Se descargó el ejecutable `winutils.exe` compatible con Hadoop 3.3.x
   (por ejemplo, desde el repositorio oficial de Steve Loughran o conda-forge).
3. Se configuraron las variables de entorno en PowerShell:

```powershell
$env:HADOOP_HOME = "C:\hadoop"
$env:PATH = "C:\hadoop\bin;" + $env:PATH
```

4. Se verificó la instalación ejecutando:

```powershell
C:\hadoop\bin\winutils.exe
```

Debe devolver la lista de comandos disponibles (no un error).

---

## 🧩 Ejecución del script principal

### 🧾 Archivo: `nyc_simple.py`

```python
import os, time
from faker import Faker
import pandas as pd
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, year, month, sum as _sum, to_date

# ---- Configuración de rutas ----
BASE = os.getcwd()
CSV = os.path.join(BASE, "data", "ventas.csv")
OUT = os.path.join(BASE, "output", "ventas_agg")

os.makedirs(os.path.dirname(CSV), exist_ok=True)
os.makedirs(OUT, exist_ok=True)

print(f"[DEBUG] CSV : {CSV}")
print(f"[DEBUG] OUT : {OUT}")

# ---- Generar CSV sintético si no existe ----
if not os.path.exists(CSV):
    print("[INFO] Generando datos sintéticos...")
    fake = Faker()
    data = [
        (fake.uuid4(), fake.random_element(["Norte","Sur","Este","Oeste"]),
         fake.date_between(start_date="-1y", end_date="today"),
         round(fake.pyfloat(left_digits=3, right_digits=2, positive=True) * 100, 2))
        for _ in range(300_000)
    ]
    df_fake = pd.DataFrame(data, columns=["cliente_id","region","fecha","monto"])
    df_fake.to_csv(CSV, index=False)
    print("[INFO] CSV generado.")

# ---- Crear SparkSession ----
spark = (
    SparkSession.builder
        .master("local[*]")
        .appName("MiniProyectoLocal")
        .config("spark.sql.shuffle.partitions", "12")
        .config("spark.hadoop.io.native.lib.available", "false")
        .getOrCreate()
)

# ---- Leer CSV + tiempo ----
t0 = time.perf_counter()
df = spark.read.csv(CSV, header=True, inferSchema=True)
print(f"[CSV] filas={df.count():,} tiempo_lectura={time.perf_counter()-t0:.2f}s")

df = df.withColumn("fecha", to_date("fecha")) \
       .withColumn("anio", year("fecha")) \
       .withColumn("mes", month("fecha"))

# ---- Filtro ----
df_filtrado = df.filter(col("monto") > 500)

# ---- Agregación ----
agg = df_filtrado.groupBy("region", "anio", "mes").agg(_sum("monto").alias("monto_total"))

# ---- Escritura Parquet particionada ----
agg.write.mode("overwrite") \
         .partitionBy("anio", "mes") \
         .option("compression", "snappy") \
         .parquet(OUT)
print(f"[WRITE] → {OUT}")

# ---- Leer Parquet + benchmark ----
t1 = time.perf_counter()
parq = spark.read.parquet(OUT)
print(f"[PARQUET] filas={parq.count():,} tiempo_lectura={time.perf_counter()-t1:.2f}s")

# ---- Plan de ejecución ----
agg.explain(True)

spark.stop()
```

---

## 🧪 Ejecución y verificación

Ejecutar desde PowerShell dentro del entorno virtual:

```powershell
python .\nyc_simple.py
```

Salida esperada (aproximada):

```
[DEBUG] CSV : C:\...\data\ventas.csv
[DEBUG] OUT : C:\...\output\ventas_agg
[CSV] filas=300,000 tiempo_lectura=6.04s
[WRITE] → C:\...\output\ventas_agg
[PARQUET] filas=300,000 tiempo_lectura=1.52s
```

Y en el explorador de VS Code se verá:

```
output/
└─ ventas_agg/
   ├─ anio=2023/
   │  ├─ mes=1/
   │  ├─ mes=2/
   │  └─ ...
   ├─ _SUCCESS
```

---

## 🧰 Reejecución limpia

Para borrar resultados previos y correr el pipeline desde cero:

```powershell
Remove-Item -Recurse -Force .\output\ventas_agg -ErrorAction SilentlyContinue
python .\nyc_simple.py
```

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

## 🧠 Conclusión

Este proyecto muestra paso a paso cómo ejecutar **PySpark localmente en Windows**, desde la configuración del entorno hasta la escritura optimizada en **Parquet**.
Se resolvió el error `HADOOP_HOME unset` configurando `winutils.exe`, logrando que Spark pueda manejar archivos sin depender de Linux o un clúster remoto.

El resultado final es un pipeline reproducible, portable y técnicamente sólido, que demuestra dominio práctico de:

* **PySpark SQL**
* **Particionamiento Parquet**
* **Configuración Hadoop local**
* **Comparativa de rendimiento entre CSV y Parquet**

---


