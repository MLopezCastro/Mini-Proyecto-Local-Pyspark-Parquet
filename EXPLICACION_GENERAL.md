# 🧠 Mini-Proyecto PySpark – Explicación Conceptual

## 1️⃣ ¿Qué es Apache Spark?

**Apache Spark** es un motor de procesamiento de datos distribuido.
Permite leer, transformar y analizar grandes volúmenes de datos en paralelo, incluso si están repartidos en varias máquinas.

En este proyecto, se utilizó Spark **localmente**, simulando un mini-cluster dentro de una sola PC.

---

## 2️⃣ ¿Qué hace Spark en la práctica?

Spark trabaja con módulos:

* **Spark SQL:** trabaja con tablas (DataFrames) y permite usar SQL.
* **Spark Core:** maneja la ejecución distribuida (los hilos y particiones).
* **Spark Streaming, MLlib y GraphX:** módulos adicionales que no usamos aquí.

Nosotros trabajamos con **Spark SQL**, manipulando DataFrames como si fueran tablas o planillas.

---

## 3️⃣ La analogía simple

Imaginá que tenés un Excel gigante con millones de filas.
Si lo abrís con pandas, se carga todo en memoria y puede colgarse.

Spark, en cambio:

* Divide el archivo en **particiones**.
* Procesa cada parte **en paralelo**.
* Une los resultados al final.

Esto lo hace ideal para trabajar con **big data**, aunque también puede usarse localmente como hicimos acá.

---

## 4️⃣ Qué hace este proyecto paso a paso

1. **Crea un CSV sintético** con 300.000 registros (clientes, regiones, fechas, montos).
2. **Lee el CSV con Spark**, infiriendo los tipos de datos.
3. **Transforma los datos** agregando columnas de `anio` y `mes`.
4. **Filtra** registros con `monto > 500`.
5. **Agrupa** por `region`, `anio` y `mes`, sumando los montos.
6. **Escribe el resultado en formato Parquet**, comprimido y **particionado** por año y mes.
7. **Compara rendimiento** entre CSV y Parquet.
8. **Muestra el plan de ejecución (EXPLAIN)** para ver cómo Spark procesa las tareas internamente.

---

## 5️⃣ ¿Qué es el formato Parquet?

**Parquet** es un formato binario columnar (guarda los datos por columnas, no por filas).

Ventajas:

* Mucho más rápido que CSV.
* Mucho más liviano.
* Permite leer solo columnas o carpetas relevantes (partition pruning).

Ejemplo de estructura generada:

```
output/
ventas_agg/
anio=2023/
mes=1/
mes=2/
...
```

---

## 6️⃣ ¿Por qué tanto problema con `winutils.exe`?

Spark usa internamente funciones de **Hadoop** para manejar archivos.
En Linux, esas utilidades vienen integradas.
En Windows, no.

Por eso Spark necesita que exista el archivo `winutils.exe` dentro de `C:\hadoop\bin`.

Las variables necesarias son:

```powershell
$env:HADOOP_HOME = "C:\hadoop"
$env:PATH = "C:\hadoop\bin;" + $env:PATH
```

---

## 7️⃣ Qué lograste

✅ Crear y activar un entorno virtual con PySpark.
✅ Ejecutar un pipeline local de Spark.
✅ Leer, transformar y guardar datos.
✅ Generar resultados en formato Parquet.
✅ Medir rendimiento.
✅ Comprender cómo Spark maneja datos en paralelo.

---

## 8️⃣ Cómo podrías explicarlo a otra persona

> "Construí un pipeline local con PySpark para procesar datos de ventas.
> Generé un dataset sintético, lo transformé y lo exporté a formato Parquet particionado por año y mes.
> Aprendí cómo Spark maneja la paralelización, el formato Parquet y la configuración local de Hadoop en Windows."

