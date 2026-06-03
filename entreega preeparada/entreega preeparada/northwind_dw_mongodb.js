// ============================================================
// DATA WAREHOUSE NORTHWIND - MongoDB
// Proyecto BI - Base de Datos Avanzadas
// Autor: Aimer Rivera Centeno
// Herramienta: MongoDB Shell (mongosh)
// Uso: mongosh < northwind_dw_mongodb.js
// ============================================================

// ──────────────────────────────────────────────
// 0. SELECCIÓN / CREACIÓN DE LA BASE DE DATOS
// ──────────────────────────────────────────────
use("northwind_dw");

print("=== Iniciando creación del DW Northwind en MongoDB ===");

// ──────────────────────────────────────────────
// 1. LIMPIAR COLECCIONES PREVIAS (si existen)
// ──────────────────────────────────────────────
const colecciones = [
  "dim_fecha", "dim_cliente", "dim_empleado",
  "dim_producto", "dim_shipper", "dim_territorio",
  "fact_ventas"
];

colecciones.forEach(col => {
  try { db[col].drop(); print(`  Colección ${col} eliminada.`); }
  catch(e) {}
});

// ============================================================
// 2. DIMENSIONES
// ============================================================

// ──────────────────────────────────────────────
// 2.1  dim_fecha
// ──────────────────────────────────────────────
db.createCollection("dim_fecha", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["fecha_id", "fecha_completa", "anio", "mes", "dia"],
      properties: {
        fecha_id:       { bsonType: "string",  description: "YYYYMMDD – clave surrogate" },
        fecha_completa: { bsonType: "date",    description: "Fecha completa ISO" },
        anio:           { bsonType: "int" },
        trimestre:      { bsonType: "int",     minimum: 1, maximum: 4 },
        mes:            { bsonType: "int",     minimum: 1, maximum: 12 },
        nombre_mes:     { bsonType: "string" },
        semana_anio:    { bsonType: "int" },
        dia:            { bsonType: "int",     minimum: 1, maximum: 31 },
        nombre_dia:     { bsonType: "string" },
        es_fin_semana:  { bsonType: "bool" }
      }
    }
  }
});

db.dim_fecha.createIndex({ fecha_id: 1 },        { unique: true, name: "idx_fecha_id" });
db.dim_fecha.createIndex({ anio: 1, mes: 1 },    { name: "idx_anio_mes" });
db.dim_fecha.createIndex({ trimestre: 1 },       { name: "idx_trimestre" });

// Datos de ejemplo – abarca el rango temporal de Northwind (1996-1998)
db.dim_fecha.insertMany([
  { fecha_id: "19960704", fecha_completa: new Date("1996-07-04"), anio: 1996, trimestre: 3, mes: 7,  nombre_mes: "Julio",      semana_anio: 27, dia: 4,  nombre_dia: "Jueves",   es_fin_semana: false },
  { fecha_id: "19961001", fecha_completa: new Date("1996-10-01"), anio: 1996, trimestre: 4, mes: 10, nombre_mes: "Octubre",    semana_anio: 40, dia: 1,  nombre_dia: "Martes",   es_fin_semana: false },
  { fecha_id: "19970115", fecha_completa: new Date("1997-01-15"), anio: 1997, trimestre: 1, mes: 1,  nombre_mes: "Enero",      semana_anio: 3,  dia: 15, nombre_dia: "Miércoles",es_fin_semana: false },
  { fecha_id: "19970601", fecha_completa: new Date("1997-06-01"), anio: 1997, trimestre: 2, mes: 6,  nombre_mes: "Junio",      semana_anio: 22, dia: 1,  nombre_dia: "Domingo",  es_fin_semana: true  },
  { fecha_id: "19971225", fecha_completa: new Date("1997-12-25"), anio: 1997, trimestre: 4, mes: 12, nombre_mes: "Diciembre",  semana_anio: 52, dia: 25, nombre_dia: "Jueves",   es_fin_semana: false },
  { fecha_id: "19980301", fecha_completa: new Date("1998-03-01"), anio: 1998, trimestre: 1, mes: 3,  nombre_mes: "Marzo",      semana_anio: 9,  dia: 1,  nombre_dia: "Domingo",  es_fin_semana: true  },
  { fecha_id: "19980715", fecha_completa: new Date("1998-07-15"), anio: 1998, trimestre: 3, mes: 7,  nombre_mes: "Julio",      semana_anio: 29, dia: 15, nombre_dia: "Miércoles",es_fin_semana: false },
]);
print("  dim_fecha: OK");

// ──────────────────────────────────────────────
// 2.2  dim_cliente
// ──────────────────────────────────────────────
db.createCollection("dim_cliente", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["cliente_id", "company_name", "country"],
      properties: {
        cliente_id:       { bsonType: "string" },
        company_name:     { bsonType: "string" },
        contact_name:     { bsonType: "string" },
        contact_title:    { bsonType: "string" },
        address:          { bsonType: "string" },
        city:             { bsonType: "string" },
        region:           { bsonType: ["string","null"] },
        postal_code:      { bsonType: ["string","null"] },
        country:          { bsonType: "string" },
        phone:            { bsonType: "string" },
        fax:              { bsonType: ["string","null"] },
        segmento_cliente: { bsonType: "string",
                            enum: ["Premium","Regular","Inactivo","Nuevo"] }
      }
    }
  }
});

db.dim_cliente.createIndex({ cliente_id: 1 },    { unique: true, name: "idx_cliente_id" });
db.dim_cliente.createIndex({ country: 1 },       { name: "idx_country" });
db.dim_cliente.createIndex({ company_name: "text" }, { name: "idx_text_company" });

db.dim_cliente.insertMany([
  { cliente_id: "ALFKI", company_name: "Alfreds Futterkiste",      contact_name: "Maria Anders",    contact_title: "Sales Representative", address: "Obere Str. 57",  city: "Berlin",    region: null,   postal_code: "12209", country: "Germany", phone: "030-0074321",  fax: "030-0076545",  segmento_cliente: "Premium"  },
  { cliente_id: "ANATR", company_name: "Ana Trujillo Emparedados",  contact_name: "Ana Trujillo",    contact_title: "Owner",                address: "Avda. de la C.", city: "México D.F.",region: null,   postal_code: "05021", country: "Mexico",  phone: "(5) 555-4729", fax: "(5) 555-3745", segmento_cliente: "Regular"  },
  { cliente_id: "BOLID", company_name: "Bólido Comidas preparadas", contact_name: "Martín Sommer",   contact_title: "Owner",                address: "C/ Araquil 67",  city: "Madrid",    region: null,   postal_code: "28023", country: "Spain",   phone: "(91) 555 22 82",fax: null,          segmento_cliente: "Inactivo" },
  { cliente_id: "BONAP", company_name: "Bon app",                   contact_name: "Laurence Lebihan",contact_title: "Owner",                address: "12 rue St. Gil.",city: "Marseille", region: null,   postal_code: "13008", country: "France",  phone: "91.24.45.40",  fax: "91.24.45.41",  segmento_cliente: "Premium"  },
  { cliente_id: "CHOPS", company_name: "Chop-suey Chinese",         contact_name: "Yang Wang",       contact_title: "Owner",                address: "Hauptstr. 29",   city: "Bern",      region: null,   postal_code: "3012",  country: "Switzerland",phone: "0452-076545",fax: null,           segmento_cliente: "Regular"  },
]);
print("  dim_cliente: OK");

// ──────────────────────────────────────────────
// 2.3  dim_empleado
// ──────────────────────────────────────────────
db.createCollection("dim_empleado", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["empleado_id", "full_name"],
      properties: {
        empleado_id:  { bsonType: "int" },
        last_name:    { bsonType: "string" },
        first_name:   { bsonType: "string" },
        full_name:    { bsonType: "string" },
        title:        { bsonType: "string" },
        hire_date:    { bsonType: "date" },
        city:         { bsonType: "string" },
        country:      { bsonType: "string" },
        region:       { bsonType: ["string","null"] },
        reports_to:   { bsonType: ["int","null"] }
      }
    }
  }
});

db.dim_empleado.createIndex({ empleado_id: 1 }, { unique: true, name: "idx_empleado_id" });
db.dim_empleado.createIndex({ country: 1 },     { name: "idx_emp_country" });

db.dim_empleado.insertMany([
  { empleado_id: 1, last_name: "Davolio",   first_name: "Nancy",   full_name: "Nancy Davolio",   title: "Sales Representative",  hire_date: new Date("1992-05-01"), city: "Seattle",   country: "USA",  region: "WA", reports_to: 2  },
  { empleado_id: 2, last_name: "Fuller",    first_name: "Andrew",  full_name: "Andrew Fuller",   title: "Vice President, Sales", hire_date: new Date("1992-08-14"), city: "Tacoma",    country: "USA",  region: "WA", reports_to: null },
  { empleado_id: 3, last_name: "Leverling", first_name: "Janet",   full_name: "Janet Leverling", title: "Sales Representative",  hire_date: new Date("1992-04-01"), city: "Kirkland",  country: "USA",  region: "WA", reports_to: 2  },
  { empleado_id: 4, last_name: "Peacock",   first_name: "Margaret",full_name: "Margaret Peacock",title: "Sales Representative",  hire_date: new Date("1993-05-03"), city: "Redmond",   country: "USA",  region: "WA", reports_to: 2  },
  { empleado_id: 5, last_name: "Buchanan",  first_name: "Steven",  full_name: "Steven Buchanan", title: "Sales Manager",         hire_date: new Date("1993-10-17"), city: "London",    country: "UK",   region: null, reports_to: 2  },
]);
print("  dim_empleado: OK");

// ──────────────────────────────────────────────
// 2.4  dim_producto
// ──────────────────────────────────────────────
db.createCollection("dim_producto", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["producto_id", "product_name", "categoria"],
      properties: {
        producto_id:    { bsonType: "int" },
        product_name:   { bsonType: "string" },
        categoria_id:   { bsonType: "int" },
        categoria:      { bsonType: "string" },
        proveedor_id:   { bsonType: "int" },
        proveedor:      { bsonType: "string" },
        unit_price:     { bsonType: "double" },
        units_in_stock: { bsonType: "int" },
        units_on_order: { bsonType: "int" },
        reorder_level:  { bsonType: "int" },
        discontinued:   { bsonType: "bool" },
        costo_adquisicion: { bsonType: "double",
                             description: "Precio de costo estimado para calcular margen" }
      }
    }
  }
});

db.dim_producto.createIndex({ producto_id: 1 },   { unique: true, name: "idx_producto_id" });
db.dim_producto.createIndex({ categoria_id: 1 },  { name: "idx_cat_id" });
db.dim_producto.createIndex({ product_name: "text" }, { name: "idx_text_producto" });

db.dim_producto.insertMany([
  { producto_id: 1,  product_name: "Chai",                 categoria_id: 1, categoria: "Beverages",   proveedor_id: 1, proveedor: "Exotic Liquids",          unit_price: 18.00, units_in_stock: 39, units_on_order: 0,  reorder_level: 10, discontinued: false, costo_adquisicion: 10.00 },
  { producto_id: 2,  product_name: "Chang",                categoria_id: 1, categoria: "Beverages",   proveedor_id: 1, proveedor: "Exotic Liquids",          unit_price: 19.00, units_in_stock: 17, units_on_order: 40, reorder_level: 25, discontinued: false, costo_adquisicion: 11.00 },
  { producto_id: 11, product_name: "Queso Cabrales",       categoria_id: 4, categoria: "Dairy Products",proveedor_id:5, proveedor: "Cooperativa de Quesos",  unit_price: 21.00, units_in_stock: 22, units_on_order: 30, reorder_level: 30, discontinued: false, costo_adquisicion: 12.00 },
  { producto_id: 17, product_name: "Alice Mutton",         categoria_id: 6, categoria: "Meat/Poultry",proveedor_id: 7, proveedor: "Pavlova Ltd.",             unit_price: 39.00, units_in_stock: 0,  units_on_order: 0,  reorder_level: 0,  discontinued: true,  costo_adquisicion: 22.00 },
  { producto_id: 72, product_name: "Mozzarella di Giovanni",categoria_id:4, categoria: "Dairy Products",proveedor_id:14,proveedor: "Formaggi Fortini s.r.l.",unit_price: 34.80, units_in_stock: 14, units_on_order: 0,  reorder_level: 0,  discontinued: false, costo_adquisicion: 19.00 },
]);
print("  dim_producto: OK");

// ──────────────────────────────────────────────
// 2.5  dim_shipper
// ──────────────────────────────────────────────
db.createCollection("dim_shipper", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["shipper_id", "company_name"],
      properties: {
        shipper_id:        { bsonType: "int" },
        company_name:      { bsonType: "string" },
        phone:             { bsonType: "string" },
        avg_delivery_days: { bsonType: "double" }
      }
    }
  }
});

db.dim_shipper.createIndex({ shipper_id: 1 }, { unique: true, name: "idx_shipper_id" });

db.dim_shipper.insertMany([
  { shipper_id: 1, company_name: "Speedy Express", phone: "(503) 555-9831", avg_delivery_days: 3.2 },
  { shipper_id: 2, company_name: "United Package",  phone: "(503) 555-3199", avg_delivery_days: 4.8 },
  { shipper_id: 3, company_name: "Federal Shipping", phone: "(503) 555-9931", avg_delivery_days: 5.1 },
]);
print("  dim_shipper: OK");

// ──────────────────────────────────────────────
// 2.6  dim_territorio
// ──────────────────────────────────────────────
db.createCollection("dim_territorio", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["territorio_id", "country"],
      properties: {
        territorio_id: { bsonType: "string" },
        city:          { bsonType: ["string","null"] },
        region:        { bsonType: ["string","null"] },
        country:       { bsonType: "string" },
        continente:    { bsonType: "string" },
        zona:          { bsonType: "string",
                         description: "Agrupación geográfica para análisis" }
      }
    }
  }
});

db.dim_territorio.createIndex({ territorio_id: 1 }, { unique: true, name: "idx_terr_id" });
db.dim_territorio.createIndex({ country: 1 },       { name: "idx_terr_country" });
db.dim_territorio.createIndex({ zona: 1 },          { name: "idx_terr_zona" });

db.dim_territorio.insertMany([
  { territorio_id: "USA-WA",  city: "Seattle",     region: "WA",      country: "USA",         continente: "América",  zona: "Norteamérica" },
  { territorio_id: "DEU-BE",  city: "Berlin",      region: null,      country: "Germany",     continente: "Europa",   zona: "Europa Occidental" },
  { territorio_id: "MEX-MX",  city: "México D.F.", region: null,      country: "Mexico",      continente: "América",  zona: "Latinoamérica" },
  { territorio_id: "GBR-LN",  city: "London",      region: null,      country: "UK",          continente: "Europa",   zona: "Europa Occidental" },
  { territorio_id: "FRA-PA",  city: "Paris",       region: "Île-de-F",country: "France",      continente: "Europa",   zona: "Europa Occidental" },
  { territorio_id: "BRA-SP",  city: "São Paulo",   region: "SP",      country: "Brazil",      continente: "América",  zona: "Latinoamérica" },
  { territorio_id: "ESP-MD",  city: "Madrid",      region: null,      country: "Spain",       continente: "Europa",   zona: "Europa Occidental" },
  { territorio_id: "ARG-BA",  city: "Buenos Aires",region: null,      country: "Argentina",   continente: "América",  zona: "Latinoamérica" },
]);
print("  dim_territorio: OK");

// ============================================================
// 3. TABLA DE HECHOS – fact_ventas
// ============================================================
db.createCollection("fact_ventas", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: [
        "order_id", "fecha_id", "cliente_id", "empleado_id",
        "producto_id", "shipper_id", "territorio_id",
        "cantidad", "unit_price", "descuento",
        "total_venta", "margen", "dias_entrega"
      ],
      properties: {
        // ── Claves ───────────────────────────────
        order_id:        { bsonType: "int",    description: "Número de orden Northwind" },
        order_detail_id: { bsonType: "string", description: "order_id + producto_id" },
        fecha_id:        { bsonType: "string", description: "FK → dim_fecha.fecha_id (YYYYMMDD)" },
        fecha_entrega_id:{ bsonType: "string", description: "FK → dim_fecha.fecha_id – fecha real de entrega" },
        cliente_id:      { bsonType: "string", description: "FK → dim_cliente.cliente_id" },
        empleado_id:     { bsonType: "int",    description: "FK → dim_empleado.empleado_id" },
        producto_id:     { bsonType: "int",    description: "FK → dim_producto.producto_id" },
        shipper_id:      { bsonType: "int",    description: "FK → dim_shipper.shipper_id" },
        territorio_id:   { bsonType: "string", description: "FK → dim_territorio.territorio_id" },

        // ── Métricas aditivas ────────────────────
        cantidad:        { bsonType: "int",    minimum: 1 },
        unit_price:      { bsonType: "double", minimum: 0 },
        descuento:       { bsonType: "double", minimum: 0, maximum: 1 },
        freight:         { bsonType: "double", minimum: 0 },

        // ── Métricas calculadas ──────────────────
        subtotal:        { bsonType: "double", description: "cantidad * unit_price" },
        total_venta:     { bsonType: "double", description: "subtotal * (1 - descuento)" },
        costo_total:     { bsonType: "double", description: "cantidad * costo_adquisicion" },
        margen:          { bsonType: "double", description: "total_venta - costo_total" },
        margen_pct:      { bsonType: "double", description: "margen / total_venta * 100" },

        // ── Tiempo ──────────────────────────────
        order_date:      { bsonType: "date" },
        required_date:   { bsonType: "date" },
        shipped_date:    { bsonType: ["date","null"] },
        dias_entrega:    { bsonType: ["int","null"],
                           description: "shipped_date - order_date" }
      }
    }
  }
});

// Índices de la fact table
db.fact_ventas.createIndex({ order_detail_id: 1 },           { unique: true, name: "idx_pk_fact" });
db.fact_ventas.createIndex({ fecha_id: 1 },                  { name: "idx_fv_fecha" });
db.fact_ventas.createIndex({ cliente_id: 1 },                { name: "idx_fv_cliente" });
db.fact_ventas.createIndex({ empleado_id: 1 },               { name: "idx_fv_empleado" });
db.fact_ventas.createIndex({ producto_id: 1 },               { name: "idx_fv_producto" });
db.fact_ventas.createIndex({ shipper_id: 1 },                { name: "idx_fv_shipper" });
db.fact_ventas.createIndex({ territorio_id: 1 },             { name: "idx_fv_territorio" });
db.fact_ventas.createIndex({ fecha_id: 1, cliente_id: 1 },   { name: "idx_fv_fecha_cliente" });
db.fact_ventas.createIndex({ fecha_id: 1, producto_id: 1 },  { name: "idx_fv_fecha_producto" });
db.fact_ventas.createIndex({ total_venta: -1 },              { name: "idx_fv_total_desc" });
db.fact_ventas.createIndex({ margen: -1 },                   { name: "idx_fv_margen_desc" });

// Datos de ejemplo (representativos del dataset Northwind)
db.fact_ventas.insertMany([
  {
    order_id: 10248, order_detail_id: "10248-11",
    fecha_id: "19960704", fecha_entrega_id: "19960716",
    cliente_id: "ALFKI", empleado_id: 5, producto_id: 11,
    shipper_id: 3, territorio_id: "DEU-BE",
    cantidad: 12, unit_price: 14.00, descuento: 0.00, freight: 32.38,
    subtotal: 168.00, total_venta: 168.00,
    costo_total: 144.00, margen: 24.00, margen_pct: 14.29,
    order_date: new Date("1996-07-04"),
    required_date: new Date("1996-08-01"),
    shipped_date: new Date("1996-07-16"),
    dias_entrega: 12
  },
  {
    order_id: 10248, order_detail_id: "10248-72",
    fecha_id: "19960704", fecha_entrega_id: "19960716",
    cliente_id: "ALFKI", empleado_id: 5, producto_id: 72,
    shipper_id: 3, territorio_id: "DEU-BE",
    cantidad: 10, unit_price: 34.80, descuento: 0.00, freight: 32.38,
    subtotal: 348.00, total_venta: 348.00,
    costo_total: 190.00, margen: 158.00, margen_pct: 45.40,
    order_date: new Date("1996-07-04"),
    required_date: new Date("1996-08-01"),
    shipped_date: new Date("1996-07-16"),
    dias_entrega: 12
  },
  {
    order_id: 10249, order_detail_id: "10249-14",
    fecha_id: "19960705", fecha_entrega_id: "19960710",
    cliente_id: "ANATR", empleado_id: 6, producto_id: 1,
    shipper_id: 1, territorio_id: "MEX-MX",
    cantidad: 9, unit_price: 18.60, descuento: 0.00, freight: 11.61,
    subtotal: 167.40, total_venta: 167.40,
    costo_total: 90.00, margen: 77.40, margen_pct: 46.23,
    order_date: new Date("1996-07-05"),
    required_date: new Date("1996-08-16"),
    shipped_date: new Date("1996-07-10"),
    dias_entrega: 5
  },
  {
    order_id: 10390, order_detail_id: "10390-2",
    fecha_id: "19970102", fecha_entrega_id: "19970107",
    cliente_id: "BONAP", empleado_id: 3, producto_id: 2,
    shipper_id: 2, territorio_id: "FRA-PA",
    cantidad: 20, unit_price: 19.00, descuento: 0.10, freight: 93.27,
    subtotal: 380.00, total_venta: 342.00,
    costo_total: 220.00, margen: 122.00, margen_pct: 35.67,
    order_date: new Date("1997-01-02"),
    required_date: new Date("1997-01-30"),
    shipped_date: new Date("1997-01-07"),
    dias_entrega: 5
  },
  {
    order_id: 10620, order_detail_id: "10620-1",
    fecha_id: "19971005", fecha_entrega_id: "19971010",
    cliente_id: "BOLID", empleado_id: 2, producto_id: 1,
    shipper_id: 1, territorio_id: "ESP-MD",
    cantidad: 5, unit_price: 18.00, descuento: 0.05, freight: 0.94,
    subtotal: 90.00, total_venta: 85.50,
    costo_total: 50.00, margen: 35.50, margen_pct: 41.52,
    order_date: new Date("1997-10-05"),
    required_date: new Date("1997-11-02"),
    shipped_date: new Date("1997-10-10"),
    dias_entrega: 5
  },
  {
    order_id: 10700, order_detail_id: "10700-72",
    fecha_id: "19971010", fecha_entrega_id: null,
    cliente_id: "CHOPS", empleado_id: 3, producto_id: 72,
    shipper_id: 1, territorio_id: "DEU-BE",
    cantidad: 16, unit_price: 34.80, descuento: 0.25, freight: 65.10,
    subtotal: 556.80, total_venta: 417.60,
    costo_total: 304.00, margen: 113.60, margen_pct: 27.21,
    order_date: new Date("1997-10-10"),
    required_date: new Date("1997-11-07"),
    shipped_date: null,
    dias_entrega: null
  },
]);
print("  fact_ventas: OK");

// ============================================================
// 4. QUERIES DE VERIFICACIÓN (responden las 10 preguntas BI)
// ============================================================
print("\n=== Consultas de validación ===\n");

// P1. Ventas por mes y año
print("P1 – Ventas por periodo:");
db.fact_ventas.aggregate([
  { $lookup: { from: "dim_fecha", localField: "fecha_id",
               foreignField: "fecha_id", as: "fecha" }},
  { $unwind: "$fecha" },
  { $group: { _id: { anio: "$fecha.anio", mes: "$fecha.mes" },
              total_ventas: { $sum: "$total_venta" },
              num_ordenes:  { $sum: 1 } }},
  { $sort: { "_id.anio": 1, "_id.mes": 1 } }
]).forEach(r => print("  ", JSON.stringify(r)));

// P2. Top 5 clientes por ingresos
print("\nP2 – Top clientes:");
db.fact_ventas.aggregate([
  { $group: { _id: "$cliente_id",
              total: { $sum: "$total_venta" },
              ordenes: { $sum: 1 } }},
  { $sort: { total: -1 }}, { $limit: 5 },
  { $lookup: { from: "dim_cliente", localField: "_id",
               foreignField: "cliente_id", as: "cli" }},
  { $unwind: "$cli" },
  { $project: { cliente: "$cli.company_name",
                total: { $round: ["$total",2] },
                ordenes: 1 }}
]).forEach(r => print("  ", JSON.stringify(r)));

// P3. Productos más vendidos (volumen)
print("\nP3 – Productos más vendidos:");
db.fact_ventas.aggregate([
  { $group: { _id: "$producto_id",
              unidades: { $sum: "$cantidad" },
              ingresos: { $sum: "$total_venta" } }},
  { $sort: { unidades: -1 }}, { $limit: 5 },
  { $lookup: { from: "dim_producto", localField: "_id",
               foreignField: "producto_id", as: "prod" }},
  { $unwind: "$prod" },
  { $project: { producto: "$prod.product_name",
                categoria: "$prod.categoria",
                unidades: 1,
                ingresos: { $round: ["$ingresos",2] } }}
]).forEach(r => print("  ", JSON.stringify(r)));

// P4. Ingresos por categoría
print("\nP4 – Ingresos por categoría:");
db.fact_ventas.aggregate([
  { $lookup: { from: "dim_producto", localField: "producto_id",
               foreignField: "producto_id", as: "prod" }},
  { $unwind: "$prod" },
  { $group: { _id: "$prod.categoria",
              total: { $sum: "$total_venta" } }},
  { $sort: { total: -1 } }
]).forEach(r => print("  ", JSON.stringify(r)));

// P5. Facturación por empleado
print("\nP5 – Facturación por empleado:");
db.fact_ventas.aggregate([
  { $group: { _id: "$empleado_id",
              total: { $sum: "$total_venta" } }},
  { $sort: { total: -1 } },
  { $lookup: { from: "dim_empleado", localField: "_id",
               foreignField: "empleado_id", as: "emp" }},
  { $unwind: "$emp" },
  { $project: { empleado: "$emp.full_name",
                total: { $round: ["$total",2] } }}
]).forEach(r => print("  ", JSON.stringify(r)));

// P6. Ingresos por territorio/país
print("\nP6 – Ingresos por territorio:");
db.fact_ventas.aggregate([
  { $lookup: { from: "dim_territorio", localField: "territorio_id",
               foreignField: "territorio_id", as: "terr" }},
  { $unwind: "$terr" },
  { $group: { _id: { pais: "$terr.country", zona: "$terr.zona" },
              total: { $sum: "$total_venta" } }},
  { $sort: { total: -1 } }
]).forEach(r => print("  ", JSON.stringify(r)));

// P7. Tiempo promedio de entrega
print("\nP7 – Promedio días de entrega:");
db.fact_ventas.aggregate([
  { $match: { dias_entrega: { $ne: null } }},
  { $group: { _id: null,
              avg_dias: { $avg: "$dias_entrega" },
              min_dias: { $min: "$dias_entrega" },
              max_dias: { $max: "$dias_entrega" } }},
  { $project: { _id: 0,
                avg_dias: { $round: ["$avg_dias", 1] },
                min_dias: 1, max_dias: 1 }}
]).forEach(r => print("  ", JSON.stringify(r)));

// P8. Margen de rentabilidad por producto
print("\nP8 – Margen por producto:");
db.fact_ventas.aggregate([
  { $group: { _id: "$producto_id",
              total_venta:  { $sum: "$total_venta" },
              total_costo:  { $sum: "$costo_total" },
              total_margen: { $sum: "$margen" } }},
  { $sort: { total_margen: -1 } },
  { $lookup: { from: "dim_producto", localField: "_id",
               foreignField: "producto_id", as: "prod" }},
  { $unwind: "$prod" },
  { $project: { producto: "$prod.product_name",
                total_venta:  { $round: ["$total_venta",2] },
                total_margen: { $round: ["$total_margen",2] },
                pct_margen: { $round: [
                  { $multiply: [
                    { $divide: ["$total_margen","$total_venta"] }, 100
                  ]}, 1
                ]}}}
]).forEach(r => print("  ", JSON.stringify(r)));

// P9. Clientes inactivos (sin compras recientes – simulado)
print("\nP9 – Clientes con < 1 orden (posible inactividad):");
db.fact_ventas.aggregate([
  { $group: { _id: "$cliente_id", ordenes: { $sum: 1 } }},
  { $match: { ordenes: { $lt: 2 } }},
  { $lookup: { from: "dim_cliente", localField: "_id",
               foreignField: "cliente_id", as: "cli" }},
  { $unwind: "$cli" },
  { $project: { cliente: "$cli.company_name",
                segmento: "$cli.segmento_cliente",
                ordenes: 1 }}
]).forEach(r => print("  ", JSON.stringify(r)));

// P10. Estacionalidad de ventas por trimestre
print("\nP10 – Ventas por trimestre:");
db.fact_ventas.aggregate([
  { $lookup: { from: "dim_fecha", localField: "fecha_id",
               foreignField: "fecha_id", as: "fecha" }},
  { $unwind: "$fecha" },
  { $group: { _id: { anio: "$fecha.anio", trimestre: "$fecha.trimestre" },
              total: { $sum: "$total_venta" },
              ordenes: { $sum: 1 } }},
  { $sort: { "_id.anio": 1, "_id.trimestre": 1 } }
]).forEach(r => print("  ", JSON.stringify(r)));

// ============================================================
// 5. RESUMEN FINAL
// ============================================================
print("\n=== Resumen de colecciones creadas ===");
colecciones.forEach(col => {
  const count = db[col].countDocuments();
  const idxs  = db[col].getIndexes().length;
  print(`  ${col.padEnd(20)} docs: ${String(count).padStart(3)}  índices: ${idxs}`);
});
print("\n=== DW Northwind MongoDB listo ===");
