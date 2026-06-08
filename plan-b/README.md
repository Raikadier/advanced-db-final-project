# Plan B — CSV sin infraestructura

Genera o valida CSV del DW para Power BI cuando no hay Supabase/Atlas disponibles.

```bash
cd plan-b/
python verify_csvs.py          # valida csvs/ existentes
python generate_csvs.py        # requiere northwind.sql (T-SQL) en esta carpeta
```

Los CSV ya generados están en `plan-b/csvs/`.
