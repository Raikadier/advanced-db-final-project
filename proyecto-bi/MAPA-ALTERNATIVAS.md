# Alternativas al mapa Azure Maps (choropleth)

Azure Maps filled map en PBIR no aplicaba color de forma fiable (geocodificación + formato condicional
fuera de Desktop). Se reemplazó por visuales nativos que **sí responden** a los segmentadores País/Zona.

## Implementado en el reporte

| Visual | Tipo | Ubicación en página | Qué muestra |
|--------|------|---------------------|-------------|
| `ebfc2b4fd2f76f7f2d0a` | Azure Maps (burbujas) | Arriba derecha | Lat/lon por país, tamaño = ventas, color por zona |
| `5132533975daf04dec8d` | Treemap | Abajo derecha | Jerarquía Zona → País por tamaño de venta |

Columnas `dim_pais[latitud]` y `dim_pais[longitud]`: centroides por país (21 filas).

Ambos usan `[Ventas por País]` y `dim_pais`. Los segmentadores `dim_territorio.country` / `zona` filtran vía relación `territorio_pais`.

## Otras opciones (manual en Power BI Desktop)

1. **Mapa de burbujas Azure Maps** — Añadir columnas `latitud` / `longitud` en `dim_pais` (centroide por país), Location = lat/lon, Size = ventas, capa burbujas ON, filled map OFF. Suele ser más estable que choropleth.

2. **Filled Map legacy (Bing)** — Visual antiguo `filledMap` con `dim_pais[pais_mapa]` + Values; Microsoft pide migrar a Azure. Útil solo si Azure falla y aceptas el aviso de migración.

3. **Shape map** — Requiere TopoJSON personalizado por país; máximo control visual, más mantenimiento.

4. **Matriz + mapa en servicio** — Publicar en Power BI Service y configurar el choropleth en Desktop una vez (el CF a veces no se serializa bien en PBIR).

## Recuperar mapa choropleth en Desktop (opcional)

1. Insertar **Azure Maps** → Location: `dim_pais[pais_mapa]`, Tooltips: `[Ventas por País]`.
2. Formato → Mapa relleno ON → Colores → fx → gradiente `#D4EDDA` → `#155724`, base `[Ventas por País]`.
3. Estilo del mapa: `grayscale_light`.
4. Guardar como PBIP y comparar `visual.json` generado por Desktop.
