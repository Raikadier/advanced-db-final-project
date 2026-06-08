-- =============================================================================
-- northwind_staging_supabase.sql
-- Staging Area Northwind BI — PostgreSQL / Supabase
-- Un solo archivo: tablas STG_* + índices + etl_runs
-- Columnas PascalCase entre comillas — compatible con northwind_etl/load.py
-- Ejecutar en SQL Editor del proyecto northwind-staging (Supabase)
-- =============================================================================

SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;

-- -----------------------------------------------------------------------------
-- STG_CATEGORIES
-- -----------------------------------------------------------------------------
DROP TABLE IF EXISTS stg_categories CASCADE;
CREATE TABLE stg_categories (
    "CategoryID"        INT            NOT NULL,
    "CategoryName"      VARCHAR(15)    NOT NULL,
    "Description"       TEXT,
    "STG_LOAD_DATE"     DATE,
    "STG_SOURCE_NAME"   VARCHAR(50),
    "STG_BATCH_ID"      VARCHAR(20),
    CONSTRAINT pk_stg_categories PRIMARY KEY ("CategoryID")
);

-- -----------------------------------------------------------------------------
-- STG_SUPPLIERS
-- -----------------------------------------------------------------------------
DROP TABLE IF EXISTS stg_suppliers CASCADE;
CREATE TABLE stg_suppliers (
    "SupplierID"        INT            NOT NULL,
    "CompanyName"       VARCHAR(40)    NOT NULL,
    "ContactName"       VARCHAR(30),
    "ContactTitle"      VARCHAR(30),
    "Address"           VARCHAR(60),
    "City"              VARCHAR(15),
    "Region"            VARCHAR(15),
    "PostalCode"        VARCHAR(10),
    "Country"           VARCHAR(15),
    "Phone"             VARCHAR(24),
    "Fax"               VARCHAR(24),
    "STG_LOAD_DATE"     DATE,
    "STG_SOURCE_NAME"   VARCHAR(50),
    "STG_BATCH_ID"      VARCHAR(20),
    CONSTRAINT pk_stg_suppliers PRIMARY KEY ("SupplierID")
);

-- -----------------------------------------------------------------------------
-- STG_SHIPPERS
-- -----------------------------------------------------------------------------
DROP TABLE IF EXISTS stg_shippers CASCADE;
CREATE TABLE stg_shippers (
    "ShipperID"         INT            NOT NULL,
    "CompanyName"       VARCHAR(40)    NOT NULL,
    "Phone"             VARCHAR(24),
    "STG_LOAD_DATE"     DATE,
    "STG_SOURCE_NAME"   VARCHAR(50),
    "STG_BATCH_ID"      VARCHAR(20),
    CONSTRAINT pk_stg_shippers PRIMARY KEY ("ShipperID")
);

-- -----------------------------------------------------------------------------
-- STG_CUSTOMERS
-- -----------------------------------------------------------------------------
DROP TABLE IF EXISTS stg_customers CASCADE;
CREATE TABLE stg_customers (
    "CustomerID"        CHAR(5)        NOT NULL,
    "CompanyName"       VARCHAR(40)    NOT NULL,
    "ContactName"       VARCHAR(30),
    "ContactTitle"      VARCHAR(30),
    "Address"           VARCHAR(60),
    "City"              VARCHAR(15),
    "Region"            VARCHAR(15),
    "PostalCode"        VARCHAR(10),
    "Country"           VARCHAR(15),
    "Phone"             VARCHAR(24),
    "Fax"               VARCHAR(24),
    "STG_LOAD_DATE"     DATE,
    "STG_SOURCE_NAME"   VARCHAR(50),
    "STG_BATCH_ID"      VARCHAR(20),
    CONSTRAINT pk_stg_customers PRIMARY KEY ("CustomerID")
);

-- -----------------------------------------------------------------------------
-- STG_EMPLOYEES
-- -----------------------------------------------------------------------------
DROP TABLE IF EXISTS stg_employees CASCADE;
CREATE TABLE stg_employees (
    "EmployeeID"        INT            NOT NULL,
    "LastName"          VARCHAR(20)    NOT NULL,
    "FirstName"         VARCHAR(10)    NOT NULL,
    "Title"             VARCHAR(30),
    "TitleOfCourtesy"   VARCHAR(25),
    "BirthDate"         DATE,
    "HireDate"          DATE,
    "City"              VARCHAR(15),
    "Region"            VARCHAR(15),
    "Country"           VARCHAR(15),
    "ReportsTo"         INT,
    "FullName"          VARCHAR(35),
    "STG_LOAD_DATE"     DATE,
    "STG_SOURCE_NAME"   VARCHAR(50),
    "STG_BATCH_ID"      VARCHAR(20),
    CONSTRAINT pk_stg_employees PRIMARY KEY ("EmployeeID")
);

-- -----------------------------------------------------------------------------
-- STG_REGION
-- -----------------------------------------------------------------------------
DROP TABLE IF EXISTS stg_region CASCADE;
CREATE TABLE stg_region (
    "RegionID"              INT            NOT NULL,
    "RegionDescription"     VARCHAR(50)    NOT NULL,
    "STG_LOAD_DATE"         DATE,
    "STG_SOURCE_NAME"       VARCHAR(50),
    "STG_BATCH_ID"          VARCHAR(20),
    CONSTRAINT pk_stg_region PRIMARY KEY ("RegionID")
);

-- -----------------------------------------------------------------------------
-- STG_TERRITORIES
-- -----------------------------------------------------------------------------
DROP TABLE IF EXISTS stg_territories CASCADE;
CREATE TABLE stg_territories (
    "TerritoryID"           VARCHAR(20)    NOT NULL,
    "TerritoryDescription"  VARCHAR(50)    NOT NULL,
    "RegionID"              INT            NOT NULL,
    "STG_LOAD_DATE"         DATE,
    "STG_SOURCE_NAME"       VARCHAR(50),
    "STG_BATCH_ID"          VARCHAR(20),
    CONSTRAINT pk_stg_territories PRIMARY KEY ("TerritoryID")
);

-- -----------------------------------------------------------------------------
-- STG_EMPLOYEE_TERRITORIES
-- -----------------------------------------------------------------------------
DROP TABLE IF EXISTS stg_employee_territories CASCADE;
CREATE TABLE stg_employee_territories (
    "EmployeeID"        INT            NOT NULL,
    "TerritoryID"       VARCHAR(20)    NOT NULL,
    "STG_LOAD_DATE"     DATE,
    "STG_SOURCE_NAME"   VARCHAR(50),
    "STG_BATCH_ID"      VARCHAR(20),
    CONSTRAINT pk_stg_emp_terr PRIMARY KEY ("EmployeeID", "TerritoryID")
);

-- -----------------------------------------------------------------------------
-- STG_PRODUCTS
-- -----------------------------------------------------------------------------
DROP TABLE IF EXISTS stg_products CASCADE;
CREATE TABLE stg_products (
    "ProductID"             INT              NOT NULL,
    "ProductName"           VARCHAR(40)      NOT NULL,
    "SupplierID"            INT,
    "CategoryID"            INT,
    "QuantityPerUnit"       VARCHAR(20),
    "UnitPrice"             NUMERIC(18,2)    DEFAULT 0.00,
    "UnitsInStock"          SMALLINT         DEFAULT 0,
    "UnitsOnOrder"          SMALLINT         DEFAULT 0,
    "ReorderLevel"          SMALLINT         DEFAULT 0,
    "Discontinued"          SMALLINT         NOT NULL DEFAULT 0,
    "STG_AlertaBajoReorden" VARCHAR(6),
    "STG_StockProyectado"   INT,
    "STG_LOAD_DATE"         DATE,
    "STG_SOURCE_NAME"       VARCHAR(50),
    "STG_BATCH_ID"          VARCHAR(20),
    CONSTRAINT pk_stg_products PRIMARY KEY ("ProductID")
);

-- -----------------------------------------------------------------------------
-- STG_ORDERS
-- -----------------------------------------------------------------------------
DROP TABLE IF EXISTS stg_orders CASCADE;
CREATE TABLE stg_orders (
    "OrderID"           INT              NOT NULL,
    "CustomerID"        CHAR(5),
    "EmployeeID"        INT,
    "OrderDate"         DATE,
    "RequiredDate"      DATE,
    "ShippedDate"       DATE,
    "ShipVia"           INT,
    "Freight"           NUMERIC(18,2)    DEFAULT 0.00,
    "ShipName"          VARCHAR(40),
    "ShipAddress"       VARCHAR(60),
    "ShipCity"          VARCHAR(15),
    "ShipRegion"        VARCHAR(15),
    "ShipPostalCode"    VARCHAR(10),
    "ShipCountry"       VARCHAR(15),
    "STG_DiasEntrega"   INT,
    "STG_EntregaPuntual" SMALLINT,
    "STG_LOAD_DATE"     DATE,
    "STG_SOURCE_NAME"   VARCHAR(50),
    "STG_BATCH_ID"      VARCHAR(20),
    CONSTRAINT pk_stg_orders PRIMARY KEY ("OrderID")
);

-- -----------------------------------------------------------------------------
-- STG_ORDER_DETAILS
-- -----------------------------------------------------------------------------
DROP TABLE IF EXISTS stg_order_details CASCADE;
CREATE TABLE stg_order_details (
    "OrderID"           INT              NOT NULL,
    "ProductID"         INT              NOT NULL,
    "UnitPrice"         NUMERIC(18,2)    NOT NULL DEFAULT 0.00,
    "Quantity"          SMALLINT         NOT NULL DEFAULT 1,
    "Discount"          NUMERIC(5,2)     NOT NULL DEFAULT 0.00,
    "STG_ValorNeto"     NUMERIC(18,2),
    "STG_LOAD_DATE"     DATE,
    "STG_SOURCE_NAME"   VARCHAR(50),
    "STG_BATCH_ID"      VARCHAR(20),
    CONSTRAINT pk_stg_order_details PRIMARY KEY ("OrderID", "ProductID")
);

-- -----------------------------------------------------------------------------
-- etl_runs — control de ejecuciones del pipeline
-- -----------------------------------------------------------------------------
DROP TABLE IF EXISTS etl_runs CASCADE;
CREATE TABLE etl_runs (
    run_id          BIGSERIAL PRIMARY KEY,
    started_at      TIMESTAMPTZ      NOT NULL DEFAULT now(),
    finished_at     TIMESTAMPTZ,
    status          VARCHAR(20)      NOT NULL DEFAULT 'running',
    batch_id        VARCHAR(20),
    phase           VARCHAR(30)      NOT NULL DEFAULT 'staging',
    rows_loaded     JSONB,
    tables_ok       TEXT[],
    tables_failed   TEXT[],
    error_message   TEXT,
    source_name     VARCHAR(50)      DEFAULT 'Northwind',
    duration_sec    NUMERIC(10,2)
);

CREATE INDEX idx_etl_runs_started ON etl_runs (started_at DESC);
CREATE INDEX idx_etl_runs_status  ON etl_runs (status);

-- =============================================================================
-- Índices de performance (consultas BI / Fase B → MongoDB)
-- =============================================================================
CREATE INDEX idx_stg_orders_customer    ON stg_orders ("CustomerID");
CREATE INDEX idx_stg_orders_employee    ON stg_orders ("EmployeeID");
CREATE INDEX idx_stg_orders_shipvia     ON stg_orders ("ShipVia");
CREATE INDEX idx_stg_orders_orderdate   ON stg_orders ("OrderDate");
CREATE INDEX idx_stg_orders_shipcountry ON stg_orders ("ShipCountry");
CREATE INDEX idx_stg_od_orderid         ON stg_order_details ("OrderID");
CREATE INDEX idx_stg_od_productid       ON stg_order_details ("ProductID");
CREATE INDEX idx_stg_products_category  ON stg_products ("CategoryID");
CREATE INDEX idx_stg_products_supplier  ON stg_products ("SupplierID");
CREATE INDEX idx_stg_territories_region ON stg_territories ("RegionID");
CREATE INDEX idx_stg_empterr_employee   ON stg_employee_territories ("EmployeeID");

-- =============================================================================
-- Verificación post-creación
-- =============================================================================
SELECT
    table_name AS tabla_staging,
    (SELECT COUNT(*) FROM information_schema.columns c
     WHERE c.table_schema = 'public' AND c.table_name = t.table_name) AS columnas
FROM information_schema.tables t
WHERE table_schema = 'public'
  AND table_name IN (
    'stg_categories', 'stg_suppliers', 'stg_shippers', 'stg_customers',
    'stg_employees', 'stg_region', 'stg_territories', 'stg_employee_territories',
    'stg_products', 'stg_orders', 'stg_order_details', 'etl_runs'
  )
ORDER BY table_name;
