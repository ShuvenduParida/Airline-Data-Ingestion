import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job

args = getResolvedOptions(sys.argv, ['JOB_NAME'])
sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args['JOB_NAME'], args)

# Script generated for node Daily raw file data
Dailyrawfiledata_node1757838987070 = glueContext.create_dynamic_frame.from_catalog(
    database="airline_data_ingestion_table",
    table_name="rawfile_daily_raw",
    transformation_ctx="Dailyrawfiledata_node1757838987070"
)

# Script generated for node AWS Glue Data Catalog (airport dimension)
AWSGlueDataCatalog_node1757841312822 = glueContext.create_dynamic_frame.from_catalog(
    database="airline_data_ingestion_table",
    table_name="dev_airlines_airports_dim",
    redshift_tmp_dir="s3://stroing-intermediate-data/intermediate_values/",
    transformation_ctx="AWSGlueDataCatalog_node1757841312822"
)

# Script generated for node Join (origin airport)
Join_node1757841564946 = Join.apply(
    frame1=Dailyrawfiledata_node1757838987070,
    frame2=AWSGlueDataCatalog_node1757841312822,
    keys1=["originairportid"],
    keys2=["airport_id"],
    transformation_ctx="Join_node1757841564946"
)

# Script generated for node dept_airport_schema_change
dept_airport_schema_chenge_node1757843320262 = ApplyMapping.apply(
    frame=Join_node1757841564946,
    mappings=[
        ("carrier", "string", "carrier", "string"),
        ("destairportid", "long", "destairportid", "long"),
        ("depdelay", "long", "dep_delay", "bigint"),
        ("arrdelay", "long", "arr_delay", "bigint"),
        ("city", "string", "dept_city", "string"),
        ("name", "string", "dep_airport", "string"),
        ("state", "string", "dep_state", "string")
    ],
    transformation_ctx="dept_airport_schema_chenge_node1757843320262"
)

# Script generated for node Join2 (destination airport)
Join2_node1757843658545 = Join.apply(
    frame1=dept_airport_schema_chenge_node1757843320262,
    frame2=AWSGlueDataCatalog_node1757841312822,
    keys1=["destairportid"],
    keys2=["airport_id"],
    transformation_ctx="Join2_node1757843658545"
)

# Script generated for node redshift_fact_table_write
redshift_fact_table_write_node1757843717086 = ApplyMapping.apply(
    frame=Join2_node1757843658545,
    mappings=[
        ("carrier", "string", "carrier", "string"),
        ("dep_state", "string", "dep_state", "string"),
        ("state", "string", "arr_state", "string"),
        ("arr_delay", "bigint", "arr_delay", "long"),
        ("city", "string", "arr_city", "string"),
        ("name", "string", "arr_airport", "string"),
        ("dep_delay", "bigint", "dep_delay", "long"),
        ("dep_airport", "string", "dep_airport", "string")
    ],
    transformation_ctx="redshift_fact_table_write_node1757843717086"
)

# ✅ Correct Redshift sink
glueContext.write_dynamic_frame.from_jdbc_conf(
    frame=redshift_fact_table_write_node1757843717086,
    catalog_connection="Jdbc quicksight connection",  # 👈 must match the name of your Glue connection
    connection_options={
        "dbtable": "dev_airlines_daily_flights_fact",
        "database": "dev"
    },
    redshift_tmp_dir="s3://stroing-intermediate-data/intermediate_values/",
    transformation_ctx="redshift_fact_table_write"
)

job.commit()
