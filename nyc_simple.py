import os, time, random, shutil
from datetime import date, timedelta
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, year, month, to_date, sum as _sum

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, "data");   os.makedirs(DATA, exist_ok=True)
LOGS = os.path.join(BASE, "logs");   os.makedirs(LOGS, exist_ok=True)

# 👉 trabajo real (Spark escribe acá, fuera de OneDrive)
OUT_WORK = r"C:\spark_out\ventas_agg"

# 👉 carpeta final dentro del repo (para que la veas/commitees)
OUT_REPO = os.path.join(BASE, "output", "ventas_agg")
os.makedirs(os.path.join(BASE, "output"), exist_ok=True)

CSV = os.path.join(DATA, "ventas.csv")
print("[DEBUG] CSV :", CSV)
print("[DEBUG] OUT_WORK:", OUT_WORK)
print("[DEBUG] OUT_REPO:", OUT_REPO)

# ----- generar CSV si no existe -----
if not os.path.exists(CSV):
    from faker import Faker
    import pandas as pd
    fake = Faker(); Faker.seed(42)
    rows = int(os.environ.get("VENTAS_ROWS", "300000"))
    print(f"[GEN] creando {rows:,} filas -> {CSV}")
    states = [fake.state() for _ in range(60)]
    start = date(2023,1,1)
    CHUNK = 100_000
    written, first = 0, True
    while written < rows:
        n = min(CHUNK, rows - written)
        recs = []
        for _ in range(n):
            d = start + timedelta(days=random.randint(0, 364))
            recs.append({
                "cliente_id": fake.uuid4(),
                "region": random.choice(states),
                "fecha": d.isoformat(),
                "monto": round(random.uniform(10, 9999), 2)
            })
        pd = __import__("pandas")
        pd.DataFrame(recs).to_csv(CSV, mode="w" if first else "a", header=first, index=False)
        first, written = False, written + n
        print(f"  - {written:,}/{rows:,}")
    print("[GEN] listo.\n")
        
import os
os.environ["HADOOP_HOME"] = r"C:\hadoop"
os.environ["PATH"] = r"C:\hadoop\bin;" + os.environ["PATH"]

# ----- Spark -----
builder = (SparkSession.builder
           .appName("ProyectoSemana5")
           .master("local[*]")
           .config("spark.sql.shuffle.partitions","12")
           .config("spark.local.dir", os.path.join(LOGS, "tmp"))
           .config("spark.hadoop.io.native.lib.available", "false")
           .config("mapreduce.fileoutputcommitter.algorithm.version", "2"))

spark = builder.getOrCreate()

# ----- leer CSV + bench -----
t0 = time.perf_counter()
df = spark.read.csv(CSV, header=True, inferSchema=True)
df.printSchema()
print(f"[CSV] filas={df.count():,} tiempo_lectura={time.perf_counter()-t0:.2f}s")

# ----- transform + agg -----
df2 = (df.withColumn("fecha", to_date("fecha"))
         .withColumn("anio", year("fecha"))
         .withColumn("mes",  month("fecha")))
agg = (df2.filter(col("monto") > 500)
          .groupBy("region","anio","mes")
          .agg(_sum("monto").alias("monto_total")))

# ----- escribir a OUT_WORK -----
# limpiar OUT_WORK
try:
    shutil.rmtree(OUT_WORK)
except FileNotFoundError:
    pass
(agg.write
   .mode("overwrite")
   .partitionBy("anio","mes")
   .option("compression","snappy")
   .parquet(OUT_WORK))
print(f"[WRITE] (work) -> {OUT_WORK}")

# ----- copiar al repo -----
try:
    shutil.rmtree(OUT_REPO)
except FileNotFoundError:
    pass
shutil.copytree(OUT_WORK, OUT_REPO)
print(f"[COPY] -> {OUT_REPO}")

# ----- leer parquet (del repo) + bench -----
t1 = time.perf_counter()
parq = spark.read.parquet(OUT_REPO)
print(f"[PARQUET] filas={parq.count():,} tiempo_lectura={time.perf_counter()-t1:.2f}s")

print("[EXPLAIN] agregación:")
agg.explain(True)

spark.stop()
