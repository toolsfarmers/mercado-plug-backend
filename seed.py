"""
Script de datos de prueba para Mercado Plug.
Ejecutar: python seed.py
"""
import sys
import os

sys.path.append(os.path.dirname(__file__))

from app.database import SessionLocal, engine
from app.models import *  # noqa: F401 — importa todos los modelos para que Base los registre
from app.database import Base
from app.models.location import Location
from app.models.user import User, UserRole, UserStatus
from app.models.store import Store, StoreStatus
from app.models.product import Product, ProductType, StockStatus, ProductStatus
from app.core.security import hash_password

Base.metadata.create_all(bind=engine)

db = SessionLocal()

# ─────────────────────────────────────────────────────────────────
# LIMPIAR datos previos del seed (orden inverso por FK)
# ─────────────────────────────────────────────────────────────────
print(">> Limpiando datos previos...")
db.query(Product).delete()
db.query(Store).delete()
db.query(User).delete()
db.query(Location).delete()
db.commit()

# ─────────────────────────────────────────────────────────────────
# LOCATIONS
# ─────────────────────────────────────────────────────────────────
print(">> Creando ubicaciones...")

loc_admin = Location(
    province="Distrito Nacional",
    municipality="Santo Domingo de Guzmán",
    sector="Gazcue",
    address_line="Av. Independencia #45",
)
loc_ana = Location(
    province="Santiago",
    municipality="Santiago de los Caballeros",
    sector="Los Jardines",
    address_line="Calle del Sol #12",
    reference_point="Frente al Parque Duarte",
)
loc_carlos = Location(
    province="Santo Domingo",
    municipality="Santo Domingo Este",
    sector="Los Mameyes",
    address_line="Calle 5 #88",
)
loc_maria = Location(
    province="La Romana",
    municipality="La Romana",
    sector="Centro",
    address_line="Av. Libertad #200",
    reference_point="Al lado del supermercado Nacional",
)
loc_pedro = Location(
    province="San Pedro de Macorís",
    municipality="San Pedro de Macorís",
    sector="Miramar",
    address_line="Calle Duarte #56",
)
loc_tienda_electronica = Location(
    province="Santiago",
    municipality="Santiago de los Caballeros",
    sector="Centro Comercial",
    address_line="Av. Juan Pablo Duarte #340",
    reference_point="Planta baja del Plaza Central",
)
loc_tienda_moda = Location(
    province="La Romana",
    municipality="La Romana",
    sector="Centro",
    address_line="Calle Castillo Márquez #18",
)
loc_tienda_hogar = Location(
    province="Distrito Nacional",
    municipality="Santo Domingo de Guzmán",
    sector="Naco",
    address_line="Av. Abraham Lincoln #405, Local 3",
)

for loc in [loc_admin, loc_ana, loc_carlos, loc_maria, loc_pedro,
            loc_tienda_electronica, loc_tienda_moda, loc_tienda_hogar]:
    db.add(loc)
db.flush()

# ─────────────────────────────────────────────────────────────────
# USUARIOS
# ─────────────────────────────────────────────────────────────────
print(">> Creando usuarios...")

admin = User(
    name="Admin Mercado Plug",
    email="admin@mercadoplug.com",
    password_hash=hash_password("Admin2026$"),
    phone="+1 809-000-0001",
    role=UserRole.admin,
    status=UserStatus.active,
    location_id=loc_admin.id,
)
ana = User(
    name="Ana García",
    email="ana@mercadoplug.com",
    password_hash=hash_password("Ana2026$seller"),
    phone="+1 809-111-2233",
    role=UserRole.seller,
    status=UserStatus.active,
    location_id=loc_ana.id,
)
carlos = User(
    name="Carlos López",
    email="carlos@mercadoplug.com",
    password_hash=hash_password("Carlos2026$buyer"),
    phone="+1 829-555-7788",
    role=UserRole.buyer,
    status=UserStatus.active,
    location_id=loc_carlos.id,
)
maria = User(
    name="María Rodríguez",
    email="maria@mercadoplug.com",
    password_hash=hash_password("Maria2026$seller"),
    phone="+1 849-333-4455",
    role=UserRole.seller,
    status=UserStatus.active,
    location_id=loc_maria.id,
)
pedro = User(
    name="Pedro Martínez",
    email="pedro@mercadoplug.com",
    password_hash=hash_password("Pedro2026$buyer"),
    phone="+1 809-777-9900",
    role=UserRole.buyer,
    status=UserStatus.active,
    location_id=loc_pedro.id,
)

for u in [admin, ana, carlos, maria, pedro]:
    db.add(u)
db.flush()

# ─────────────────────────────────────────────────────────────────
# TIENDAS
# ─────────────────────────────────────────────────────────────────
print(">> Creando tiendas...")

tienda_electronica = Store(
    seller_id=ana.id,
    store_name="Electrónica Rápida",
    slug="electronica-rapida",
    description="Los mejores gadgets, accesorios y electrónica al mejor precio en Santiago.",
    logo_url="https://placehold.co/200x200?text=ER",
    cover_image_url="https://placehold.co/1200x400?text=Electronica+Rapida",
    whatsapp_number="+1 809-111-2233",
    location_id=loc_tienda_electronica.id,
    status=StoreStatus.active,
)
tienda_moda = Store(
    seller_id=maria.id,
    store_name="Moda Urban",
    slug="moda-urban",
    description="Ropa, calzado y accesorios de tendencia. Envíos a todo el país.",
    logo_url="https://placehold.co/200x200?text=MU",
    cover_image_url="https://placehold.co/1200x400?text=Moda+Urban",
    whatsapp_number="+1 849-333-4455",
    location_id=loc_tienda_moda.id,
    status=StoreStatus.active,
)
tienda_hogar = Store(
    seller_id=ana.id,
    store_name="Hogar & Deco",
    slug="hogar-deco",
    description="Todo para tu hogar: muebles, decoración y artículos del hogar.",
    logo_url="https://placehold.co/200x200?text=HD",
    cover_image_url="https://placehold.co/1200x400?text=Hogar+Deco",
    whatsapp_number="+1 809-111-2233",
    location_id=loc_tienda_hogar.id,
    status=StoreStatus.active,
)

for s in [tienda_electronica, tienda_moda, tienda_hogar]:
    db.add(s)
db.flush()

# ─────────────────────────────────────────────────────────────────
# PRODUCTOS Y SERVICIOS
# ─────────────────────────────────────────────────────────────────
print(">> Creando productos y servicios...")

products = [
    # ── Electrónica Rápida ──
    Product(
        store_id=tienda_electronica.id,
        name="Audífonos Bluetooth Pro Max",
        description="Audífonos inalámbricos con cancelación activa de ruido, 30h de batería y estuche de carga.",
        price=3500.00, currency="DOP", category="Electrónica",
        type=ProductType.product,
        images=["https://placehold.co/600x400?text=Audifonos"],
        stock_status=StockStatus.available,
        whatsapp_number=tienda_electronica.whatsapp_number,
        location_id=tienda_electronica.location_id,
        delivery=True, status=ProductStatus.active,
    ),
    Product(
        store_id=tienda_electronica.id,
        name="Cargador USB-C 65W GaN",
        description="Cargador rápido compacto compatible con laptops, tablets y smartphones.",
        price=1200.00, currency="DOP", category="Electrónica",
        type=ProductType.product,
        images=["https://placehold.co/600x400?text=Cargador"],
        stock_status=StockStatus.available,
        whatsapp_number=tienda_electronica.whatsapp_number,
        location_id=tienda_electronica.location_id,
        delivery=True, status=ProductStatus.active,
    ),
    Product(
        store_id=tienda_electronica.id,
        name="Smartwatch Fitness Band X5",
        description="Reloj inteligente con monitor de frecuencia cardíaca, GPS y resistencia al agua IP68.",
        price=4800.00, currency="DOP", category="Electrónica",
        type=ProductType.product,
        images=["https://placehold.co/600x400?text=Smartwatch"],
        stock_status=StockStatus.available,
        whatsapp_number=tienda_electronica.whatsapp_number,
        location_id=tienda_electronica.location_id,
        delivery=True, status=ProductStatus.active,
    ),
    Product(
        store_id=tienda_electronica.id,
        name="Parlante Bluetooth Portátil",
        description="Sonido 360°, resistente al agua IPX7, batería de 12h. Ideal para exteriores.",
        price=2900.00, currency="DOP", category="Electrónica",
        type=ProductType.product,
        images=["https://placehold.co/600x400?text=Parlante"],
        stock_status=StockStatus.available,
        whatsapp_number=tienda_electronica.whatsapp_number,
        location_id=tienda_electronica.location_id,
        delivery=True, status=ProductStatus.active,
    ),
    Product(
        store_id=tienda_electronica.id,
        name="Reparación de Pantallas de Celular",
        description="Servicio de cambio de pantalla para iPhone y Samsung. Garantía de 3 meses. Entrega en 24h.",
        price=1800.00, currency="DOP", category="Servicios Técnicos",
        type=ProductType.service,
        images=["https://placehold.co/600x400?text=Reparacion"],
        stock_status=StockStatus.available,
        whatsapp_number=tienda_electronica.whatsapp_number,
        location_id=tienda_electronica.location_id,
        delivery=False, status=ProductStatus.active,
    ),
    Product(
        store_id=tienda_electronica.id,
        name="Instalación de CCTV (4 cámaras)",
        description="Instalación profesional de sistema de cámaras de seguridad HD con acceso remoto.",
        price=12000.00, currency="DOP", category="Servicios Técnicos",
        type=ProductType.service,
        images=["https://placehold.co/600x400?text=CCTV"],
        stock_status=StockStatus.available,
        whatsapp_number=tienda_electronica.whatsapp_number,
        location_id=tienda_electronica.location_id,
        delivery=False, status=ProductStatus.active,
    ),

    # ── Moda Urban ──
    Product(
        store_id=tienda_moda.id,
        name="Tenis Nike Air Max 270",
        description="Zapatillas deportivas originales, disponibles en tallas del 37 al 44. Varios colores.",
        price=6500.00, currency="DOP", category="Calzado",
        type=ProductType.product,
        images=["https://placehold.co/600x400?text=Tenis+Nike"],
        stock_status=StockStatus.available,
        whatsapp_number=tienda_moda.whatsapp_number,
        location_id=tienda_moda.location_id,
        delivery=True, status=ProductStatus.active,
    ),
    Product(
        store_id=tienda_moda.id,
        name="Blusa Lino Verano",
        description="Blusa de lino de alta calidad, perfecta para el verano. Tallas S, M, L, XL.",
        price=950.00, currency="DOP", category="Ropa",
        type=ProductType.product,
        images=["https://placehold.co/600x400?text=Blusa"],
        stock_status=StockStatus.available,
        whatsapp_number=tienda_moda.whatsapp_number,
        location_id=tienda_moda.location_id,
        delivery=True, status=ProductStatus.active,
    ),
    Product(
        store_id=tienda_moda.id,
        name="Cartera de Cuero Genuine",
        description="Cartera artesanal 100% cuero genuino. Compartimentos para tarjetas y billete.",
        price=2200.00, currency="DOP", category="Accesorios",
        type=ProductType.product,
        images=["https://placehold.co/600x400?text=Cartera"],
        stock_status=StockStatus.available,
        whatsapp_number=tienda_moda.whatsapp_number,
        location_id=tienda_moda.location_id,
        delivery=True, status=ProductStatus.active,
    ),
    Product(
        store_id=tienda_moda.id,
        name="Gafas de Sol Polarizadas UV400",
        description="Protección UV400, marco metálico liviano, unisex. Incluye estuche y paño.",
        price=1400.00, currency="DOP", category="Accesorios",
        type=ProductType.product,
        images=["https://placehold.co/600x400?text=Gafas"],
        stock_status=StockStatus.available,
        whatsapp_number=tienda_moda.whatsapp_number,
        location_id=tienda_moda.location_id,
        delivery=True, status=ProductStatus.active,
    ),
    Product(
        store_id=tienda_moda.id,
        name="Asesoría de Imagen Personal",
        description="Sesión de 1h con estilista profesional: análisis de colorimetría, tipo de cuerpo y armado de outfits.",
        price=3500.00, currency="DOP", category="Servicios",
        type=ProductType.service,
        images=["https://placehold.co/600x400?text=Asesoria"],
        stock_status=StockStatus.available,
        whatsapp_number=tienda_moda.whatsapp_number,
        location_id=tienda_moda.location_id,
        delivery=False, status=ProductStatus.active,
    ),

    # ── Hogar & Deco ──
    Product(
        store_id=tienda_hogar.id,
        name="Set de Toallas de Baño Premium",
        description="Juego de 4 toallas 100% algodón egipcio, ultra absorbentes. Disponible en 6 colores.",
        price=1800.00, currency="DOP", category="Hogar",
        type=ProductType.product,
        images=["https://placehold.co/600x400?text=Toallas"],
        stock_status=StockStatus.available,
        whatsapp_number=tienda_hogar.whatsapp_number,
        location_id=tienda_hogar.location_id,
        delivery=True, status=ProductStatus.active,
    ),
    Product(
        store_id=tienda_hogar.id,
        name="Lámpara de Pie LED Regulable",
        description="Lámpara moderna con 3 tonos de luz y regulador de intensidad. Base de mármol sintético.",
        price=3200.00, currency="DOP", category="Decoración",
        type=ProductType.product,
        images=["https://placehold.co/600x400?text=Lampara"],
        stock_status=StockStatus.available,
        whatsapp_number=tienda_hogar.whatsapp_number,
        location_id=tienda_hogar.location_id,
        delivery=True, status=ProductStatus.active,
    ),
    Product(
        store_id=tienda_hogar.id,
        name="Servicio de Decoración de Interiores",
        description="Diseño y decoración de salas, habitaciones o espacios de trabajo. Presupuesto sin costo.",
        price=8500.00, currency="DOP", category="Servicios",
        type=ProductType.service,
        images=["https://placehold.co/600x400?text=Decoracion"],
        stock_status=StockStatus.available,
        whatsapp_number=tienda_hogar.whatsapp_number,
        location_id=tienda_hogar.location_id,
        delivery=False, status=ProductStatus.active,
    ),
]

for p in products:
    db.add(p)

db.commit()
print("\n[OK] Seed completado exitosamente!\n")

# ─────────────────────────────────────────────────────────────────
# RESUMEN
# ─────────────────────────────────────────────────────────────────
print("=" * 55)
print("  CREDENCIALES DE ACCESO PARA PRUEBAS")
print("=" * 55)
print(f"\n{'ROL':<10} {'EMAIL':<35} {'PASSWORD'}")
print("-" * 55)
print(f"{'ADMIN':<10} {'admin@mercadoplug.com':<35} Admin2026$")
print(f"{'SELLER':<10} {'ana@mercadoplug.com':<35} Ana2026$seller")
print(f"{'SELLER':<10} {'maria@mercadoplug.com':<35} Maria2026$seller")
print(f"{'BUYER':<10} {'carlos@mercadoplug.com':<35} Carlos2026$buyer")
print(f"{'BUYER':<10} {'pedro@mercadoplug.com':<35} Pedro2026$buyer")
print("\n" + "=" * 55)
print(f"\n  IDs creados:")
print(f"  Admin ID:   {admin.id}")
print(f"  Ana ID:     {ana.id}   | Tiendas: Electrónica Rápida (#{tienda_electronica.id}), Hogar & Deco (#{tienda_hogar.id})")
print(f"  María ID:   {maria.id}   | Tienda:  Moda Urban (#{tienda_moda.id})")
print(f"  Carlos ID:  {carlos.id}")
print(f"  Pedro ID:   {pedro.id}")
print(f"\n  Productos creados: {len(products)}")
print("=" * 55)

db.close()
