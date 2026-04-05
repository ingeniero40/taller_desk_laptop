from Gestion_Taller_Computo.infrastructure.database.psycopg_db import Psycopg2Database
db = Psycopg2Database()
print("Actual Columns: name, sku, stock, min_stock, category")
res = db.executeRawQuery("SELECT name, sku, stock, min_stock, category FROM products LIMIT 5", fetch=True)
for row in res:
    print(row)
