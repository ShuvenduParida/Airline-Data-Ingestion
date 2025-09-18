# ✈️ Airline Data Ingestion Pipeline (AWS Serverless)

This project implements a **serverless data ingestion and transformation pipeline** using AWS services. It demonstrates how to build an **event-driven ETL workflow** where new files uploaded to **Amazon S3** trigger a pipeline that processes, transforms, and loads data into **Amazon Redshift** for analytics.

---

## 📌 Architecture Overview

1. A **CSV file** (`flights.csv`) is uploaded to the S3 bucket `daily-airline-data`.
2. **AWS CloudTrail** captures the `PutObject` event.
3. **Amazon EventBridge Rule** listens for the event and triggers the **Step Function**.
4. The **Step Function** orchestrates the pipeline:
   - Starts the **Glue Crawler** to update table schemas.
   - Waits until the crawler finishes.
   - Triggers the **Glue ETL job**.
   - Monitors job execution status.
   - Sends **SNS notifications** for success/failure.
5. The **Glue ETL job**:
   - Reads raw flight data from S3 (`rawfile_daily_raw`).
   - Joins with airport dimension data from Redshift (`airports_dim`).
   - Applies schema transformations.
   - Loads the cleaned fact data into Redshift (`daily_flights_fact`).
6. **Amazon Redshift** stores the transformed data for querying and analytics.

---

## 📊 Workflow Diagrams

### Step Function Workflow
This state machine manages orchestration of crawler, Glue job, and notifications:

![Step Function Workflow](diagrams/step_function_graph.png)

### Glue ETL Job Flow
This Glue job transforms airline flight data and loads it into Redshift:

![Glue ETL Flow](diagrams/glue_etl_flow.png)

### High-Level Architecture
End-to-end data pipeline from **S3 → Step Functions → Glue → Redshift**:

![Architecture](diagrams/architecture.png)

---

## ⚙️ Components

### 1. **Amazon S3**
- Raw flight data (`flights.csv`) is stored in the S3 bucket `daily-airline-data`.

### 2. **AWS CloudTrail**
- Captures S3 API calls (`PutObject`, `CompleteMultipartUpload`) when new files are uploaded.

### 3. **Amazon EventBridge**
- EventBridge rule listens for CloudTrail events from the S3 bucket.
- Triggers Step Function automatically when a new file is uploaded.

### 4. **AWS Step Functions**
- Defined in **Amazon States Language (ASL)** → [`state_machine.asl.json`](step-functions/state_machine.asl.json).
- Key states:
  - `StartCrawler` → starts Glue Crawler.
  - `GetCrawler` → checks crawler state.
  - `Glue StartJobRun` → triggers ETL job.
  - `GetJobRun` → checks job status.
  - `success notification` / `failed notification` → sends SNS messages.

### 5. **AWS Glue**
- **Glue Crawlers**: Create/update schemas for raw S3 and Redshift tables.
- **Glue Job** (`airline_data_ingestion.py`):
  - Reads raw data from S3.
  - Joins with airport dimension table.
  - Applies transformations.
  - Loads processed data into Redshift fact table.

### 6. **Amazon Redshift**
- Tables created manually (DDL in `sql/`):
  - `airports_dim` → Airport dimension.
  - `daily_flights_fact` → Fact table with flight-level data.

### 7. **Amazon SNS**
- Sends notifications on job success or failure.

---

## 🛠️ Deployment Guide

### Step 1: Redshift Setup
Run the following SQL to create target tables:

```sql
CREATE TABLE airlines.airports_dim (
    airport_id VARCHAR(50),
    name VARCHAR(200),
    city VARCHAR(100),
    state VARCHAR(100)
);

CREATE TABLE airlines.daily_flights_fact (
    carrier VARCHAR(10),
    dep_airport VARCHAR(200),
    arr_airport VARCHAR(200),
    dep_city VARCHAR(100),
    arr_city VARCHAR(100),
    dep_state VARCHAR(100),
    arr_state VARCHAR(100),
    dep_delay BIGINT,
    arr_delay BIGINT
);

```

Step 2: Glue Setup

Create Glue Crawlers:

daily_raw_data_crawler → Crawls raw S3 files.

dim_airline_data_crawler → Crawls airport dimension.

Create Glue Job (airline_data_ingestion) using script:

glue-job/airline_data_ingestion.py

Step 3: Step Functions Setup

Deploy the Step Function using definition file:

step-functions/state_machine.asl.json

Ensure IAM role has access to:

Glue

SNS

S3

CloudWatch Logs

Step 4: EventBridge Setup

Create EventBridge rule to capture CloudTrail events for:

PutObject

CompleteMultipartUpload

Target → Step Function state machine.

Step 5: Testing

Upload flights.csv to s3://daily-airline-data.

Verify Step Function execution in AWS Console.

Check Glue job logs.

Query Redshift:

SELECT COUNT(*) FROM airlines.daily_flights_fact;


Confirm SNS notification (success/failure).

🔔 Notifications

On Success → SNS publishes:
"Glue job execution successful"

On Failure → SNS publishes:
"Glue job execution failed"

📌 Tech Stack

Amazon S3 → Data lake for raw files

AWS CloudTrail → Event tracking

Amazon EventBridge → Event routing

AWS Step Functions → Workflow orchestration

AWS Glue → ETL processing

Amazon Redshift → Data warehouse

Amazon SNS → Notifications
