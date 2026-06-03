-- =============================================================================
-- create_staging.sql
-- Script DDL — Creación de la Staging Area Northwind BI
-- Motor: MySQL 8+ / MariaDB 10.6+
-- Para SQL Server: cambiar ENGINE=InnoDB por GO, TINYINT por BIT, etc.
-- =============================================================================

CREATE DATABASE IF NOT EXISTS northwind_staging
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE northwind_staging;

-- -----------------------------------------------------------------------------
-- STG_CATEGORIES
-- -----------------------------------------------------------------------------
DROP TABLE IF EXISTS stg_categories;
CREATE TABLE stg_categories (
    CategoryID          INT            NOT NULL,
    CategoryName        VARCHAR(15)    NOT NULL,
    Description         TEXT,
    -- Metadatos de carga
    STG_LOAD_DATE       DATE,
    STG_SOURCE_NAME     VARCHAR(50),
    STG_BATCH_ID        VARCHAR(20),
    CONSTRAINT pk_stg_categories PRIMARY KEY (CategoryID)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- -----------------------------------------------------------------------------
-- STG_SUPPLIERS
-- -----------------------------------------------------------------------------
DROP TABLE IF EXISTS stg_suppliers;
CREATE TABLE stg_suppliers (
    SupplierID          INT            NOT NULL,
    CompanyName         VARCHAR(40)    NOT NULL,
    ContactName         VARCHAR(30),
    ContactTitle        VARCHAR(30),
    Address             VARCHAR(60),
    City                VARCHAR(15),
    Region              VARCHAR(15),
    PostalCode          VARCHAR(10),
    Country             VARCHAR(15),
    Phone               VARCHAR(24),
    Fax                 VARCHAR(24),
    -- Metadatos de carga
    STG_LOAD_DATE       DATE,
    STG_SOURCE_NAME     VARCHAR(50),
    STG_BATCH_ID        VARCHAR(20),
    CONSTRAINT pk_stg_suppliers PRIMARY KEY (SupplierID)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- -----------------------------------------------------------------------------
-- STG_SHIPPERS
-- -----------------------------------------------------------------------------
DROP TABLE IF EXISTS stg_shippers;
CREATE TABLE stg_shippers (
    ShipperID           INT            NOT NULL,
    CompanyName         VARCHAR(40)    NOT NULL,
    Phone               VARCHAR(24),
    -- Metadatos de carga
    STG_LOAD_DATE       DATE,
    STG_SOURCE_NAME     VARCHAR(50),
    STG_BATCH_ID        VARCHAR(20),
    CONSTRAINT pk_stg_shippers PRIMARY KEY (ShipperID)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- -----------------------------------------------------------------------------
-- STG_CUSTOMERS
-- -----------------------------------------------------------------------------
DROP TABLE IF EXISTS stg_customers;
CREATE TABLE stg_customers (
    CustomerID          CHAR(5)        NOT NULL,
    CompanyName         VARCHAR(40)    NOT NULL,
    ContactName         VARCHAR(30),
    ContactTitle        VARCHAR(30),
    Address             VARCHAR(60),
    City                VARCHAR(15),
    Region              VARCHAR(15),
    PostalCode          VARCHAR(10),
    Country             VARCHAR(15),
    Phone               VARCHAR(24),
    Fax                 VARCHAR(24),
    -- Metadatos de carga
    STG_LOAD_DATE       DATE,
    STG_SOURCE_NAME     VARCHAR(50),
    STG_BATCH_ID        VARCHAR(20),
    CONSTRAINT pk_stg_customers PRIMARY KEY (CustomerID)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- -----------------------------------------------------------------------------
-- STG_EMPLOYEES
-- -----------------------------------------------------------------------------
DROP TABLE IF EXISTS stg_employees;
CREATE TABLE stg_employees (
    EmployeeID          INT            NOT NULL,
    LastName            VARCHAR(20)    NOT NULL,
    FirstName           VARCHAR(10)    NOT NULL,
    Title               VARCHAR(30),
    TitleOfCourtesy     VARCHAR(25),
    BirthDate           DATE,
    HireDate            DATE,
    City                VARCHAR(15),
    Region              VARCHAR(15),
    Country             VARCHAR(15),
    ReportsTo           INT,
    FullName            VARCHAR(35),   -- TR-013: campo derivado
    -- Metadatos de carga
    STG_LOAD_DATE       DATE,
    STG_SOURCE_NAME     VARCHAR(50),
    STG_BATCH_ID        VARCHAR(20),
    CONSTRAINT pk_stg_employees PRIMARY KEY (EmployeeID)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- -----------------------------------------------------------------------------
-- STG_PRODUCTS
-- -----------------------------------------------------------------------------
DROP TABLE IF EXISTS stg_products;
CREATE TABLE stg_products (
    ProductID               INT              NOT NULL,
    ProductName             VARCHAR(40)      NOT NULL,
    SupplierID              INT,
    CategoryID              INT,
    QuantityPerUnit         VARCHAR(20),
    UnitPrice               DECIMAL(18,2)    DEFAULT 0.00,
    UnitsInStock            SMALLINT         DEFAULT 0,
    UnitsOnOrder            SMALLINT         DEFAULT 0,
    ReorderLevel            SMALLINT         DEFAULT 0,
    Discontinued            TINYINT          NOT NULL DEFAULT 0,
    STG_AlertaBajoReorden   VARCHAR(6),      -- TR-009: ALERTA / OK
    STG_StockProyectado     INT,             -- TR-010: InStock + OnOrder
    -- Metadatos de carga
    STG_LOAD_DATE           DATE,
    STG_SOURCE_NAME         VARCHAR(50),
    STG_BATCH_ID            VARCHAR(20),
    CONSTRAINT pk_stg_products PRIMARY KEY (ProductID)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- -----------------------------------------------------------------------------
-- STG_ORDERS
-- -----------------------------------------------------------------------------
DROP TABLE IF EXISTS stg_orders;
CREATE TABLE stg_orders (
    OrderID             INT              NOT NULL,
    CustomerID          CHAR(5),
    EmployeeID          INT,
    OrderDate           DATE,
    RequiredDate        DATE,
    ShippedDate         DATE,
    ShipVia             INT,
    Freight             DECIMAL(18,2)    DEFAULT 0.00,
    ShipName            VARCHAR(40),
    ShipAddress         VARCHAR(60),
    ShipCity            VARCHAR(15),
    ShipRegion          VARCHAR(15),
    ShipPostalCode      VARCHAR(10),
    ShipCountry         VARCHAR(15),
    STG_DiasEntrega     INT,             -- TR-007: ShippedDate - OrderDate (días)
    STG_EntregaPuntual  TINYINT,         -- TR-008: 1=puntual, 0=tarde, NULL=no despachado
    -- Metadatos de carga
    STG_LOAD_DATE       DATE,
    STG_SOURCE_NAME     VARCHAR(50),
    STG_BATCH_ID        VARCHAR(20),
    CONSTRAINT pk_stg_orders PRIMARY KEY (OrderID)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- -----------------------------------------------------------------------------
-- STG_ORDER_DETAILS
-- -----------------------------------------------------------------------------
DROP TABLE IF EXISTS stg_order_details;
CREATE TABLE stg_order_details (
    OrderID             INT              NOT NULL,
    ProductID           INT              NOT NULL,
    UnitPrice           DECIMAL(18,2)    NOT NULL DEFAULT 0.00,
    Quantity            SMALLINT         NOT NULL DEFAULT 1,
    Discount            DECIMAL(5,2)     NOT NULL DEFAULT 0.00,
    STG_ValorNeto       DECIMAL(18,2),   -- TR-006: UnitPrice * Qty * (1 - Discount)
    -- Metadatos de carga
    STG_LOAD_DATE       DATE,
    STG_SOURCE_NAME     VARCHAR(50),
    STG_BATCH_ID        VARCHAR(20),
    CONSTRAINT pk_stg_order_details PRIMARY KEY (OrderID, ProductID)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- -----------------------------------------------------------------------------
-- STG_REGION  (4 registros — necesaria para P6)
-- -----------------------------------------------------------------------------
DROP TABLE IF EXISTS stg_region;
CREATE TABLE stg_region (
    RegionID            INT            NOT NULL,
    RegionDescription   VARCHAR(50)    NOT NULL,
    STG_LOAD_DATE       DATE,
    STG_SOURCE_NAME     VARCHAR(50),
    STG_BATCH_ID        VARCHAR(20),
    CONSTRAINT pk_stg_region PRIMARY KEY (RegionID)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- -----------------------------------------------------------------------------
-- STG_TERRITORIES  (53 registros — necesaria para P6)
-- -----------------------------------------------------------------------------
DROP TABLE IF EXISTS stg_territories;
CREATE TABLE stg_territories (
    TerritoryID          VARCHAR(20)    NOT NULL,
    TerritoryDescription VARCHAR(50)    NOT NULL,
    RegionID             INT            NOT NULL,
    STG_LOAD_DATE        DATE,
    STG_SOURCE_NAME      VARCHAR(50),
    STG_BATCH_ID         VARCHAR(20),
    CONSTRAINT pk_stg_territories PRIMARY KEY (TerritoryID)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- -----------------------------------------------------------------------------
-- STG_EMPLOYEE_TERRITORIES  (49 registros — necesaria para P5, P6)
-- -----------------------------------------------------------------------------
DROP TABLE IF EXISTS stg_employee_territories;
CREATE TABLE stg_employee_territories (
    EmployeeID          INT            NOT NULL,
    TerritoryID         VARCHAR(20)    NOT NULL,
    STG_LOAD_DATE       DATE,
    STG_SOURCE_NAME     VARCHAR(50),
    STG_BATCH_ID        VARCHAR(20),
    CONSTRAINT pk_stg_emp_terr PRIMARY KEY (EmployeeID, TerritoryID)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- =============================================================================
-- Índices de performance para consultas BI frecuentes
-- =============================================================================
CREATE INDEX idx_stg_orders_customer   ON stg_orders (CustomerID);
CREATE INDEX idx_stg_orders_employee   ON stg_orders (EmployeeID);
CREATE INDEX idx_stg_orders_shipvia    ON stg_orders (ShipVia);
CREATE INDEX idx_stg_orders_orderdate  ON stg_orders (OrderDate);
CREATE INDEX idx_stg_orders_shipcountry ON stg_orders (ShipCountry);
CREATE INDEX idx_stg_od_orderid        ON stg_order_details (OrderID);
CREATE INDEX idx_stg_od_productid      ON stg_order_details (ProductID);
CREATE INDEX idx_stg_products_category ON stg_products (CategoryID);
CREATE INDEX idx_stg_products_supplier ON stg_products (SupplierID);

-- =============================================================================
-- Verificación post-creación
-- =============================================================================
SELECT
    TABLE_NAME        AS `Tabla Staging`,
    TABLE_ROWS        AS `Filas estimadas`,
    CREATE_TIME       AS `Creada`
FROM information_schema.TABLES
WHERE TABLE_SCHEMA = 'northwind_staging'
ORDER BY TABLE_NAME;
