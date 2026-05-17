"""
Seed de datos de prueba para Mercado Plug.
Cubre: usuarios, tiendas, productos, pedidos, ventas,
       comisiones, interacciones, productos guardados.

Ejecutar: python seed.py
"""
import sys
import os
from decimal import Decimal

sys.path.append(os.path.dirname(__file__))

from app.database import SessionLocal, engine, Base
from app.models.commission import Commission, CommissionPayment, CommissionStatus
from app.models.interaction import InteractionAction, ProductInteraction
from app.models.location import Location
from app.models.order import Order, OrderStatus
from app.models.product import Product, ProductStatus, ProductType, StockStatus
from app.models.sale import Sale
from app.models.saved_product import SavedProduct
from app.models.store import Store, StoreStatus
from app.models.user import User, UserRole, UserStatus
from app.core.security import hash_password

Base.metadata.create_all(bind=engine)
db = SessionLocal()

# ─────────────────────────────────────────────────────────────────
# LIMPIAR (orden inverso por FK)
# ─────────────────────────────────────────────────────────────────
print(">> Limpiando datos previos...")
db.query(SavedProduct).delete()
db.query(ProductInteraction).delete()
db.query(CommissionPayment).delete()
db.query(Commission).delete()
db.query(Sale).delete()
db.query(Order).delete()
db.query(Product).delete()
db.query(Store).delete()
db.query(User).delete()
db.query(Location).delete()
db.commit()

# ─────────────────────────────────────────────────────────────────
# UBICACIONES
# ─────────────────────────────────────────────────────────────────
print(">> Creando ubicaciones...")

loc_admin   = Location(province="Distrito Nacional",     municipality="Santo Domingo de Guzmán", sector="Gazcue",           address_line="Av. Independencia #45")
loc_operador= Location(province="Distrito Nacional",     municipality="Santo Domingo de Guzmán", sector="Piantini",         address_line="Calle Rafael Augusto Sánchez #22")
loc_ana     = Location(province="Santiago",              municipality="Santiago de los Caballeros", sector="Los Jardines",  address_line="Calle del Sol #12",  reference_point="Frente al Parque Duarte")
loc_maria   = Location(province="La Romana",             municipality="La Romana",               sector="Centro",           address_line="Av. Libertad #200",  reference_point="Al lado del supermercado Nacional")
loc_carlos  = Location(province="Santo Domingo",         municipality="Santo Domingo Este",       sector="Los Mameyes",      address_line="Calle 5 #88")
loc_pedro   = Location(province="San Pedro de Macorís",  municipality="San Pedro de Macorís",     sector="Miramar",          address_line="Calle Duarte #56")
loc_lucia   = Location(province="Santiago",              municipality="Santiago de los Caballeros", sector="Villa del Rey",  address_line="Av. 27 de Febrero #310")

loc_t_elec  = Location(province="Santiago",              municipality="Santiago de los Caballeros", sector="Centro Comercial", address_line="Av. Juan Pablo Duarte #340", reference_point="Planta baja Plaza Central")
loc_t_moda  = Location(province="La Romana",             municipality="La Romana",               sector="Centro",           address_line="Calle Castillo Márquez #18")
loc_t_hogar = Location(province="Distrito Nacional",     municipality="Santo Domingo de Guzmán", sector="Naco",             address_line="Av. Abraham Lincoln #405, Local 3")

for loc in [loc_admin, loc_operador, loc_ana, loc_maria, loc_carlos, loc_pedro, loc_lucia,
            loc_t_elec, loc_t_moda, loc_t_hogar]:
    db.add(loc)
db.flush()

# ─────────────────────────────────────────────────────────────────
# USUARIOS
# ─────────────────────────────────────────────────────────────────
print(">> Creando usuarios...")

admin    = User(name="Admin Mercado Plug",  email="admin@mercadoplug.com",    password_hash=hash_password("Admin2026$"),         phone="+1 809-000-0001", role=UserRole.admin,    status=UserStatus.active, location_id=loc_admin.id)
operador = User(name="Luis Operador",       email="operador@mercadoplug.com", password_hash=hash_password("Operador2026$"),       phone="+1 809-000-0002", role=UserRole.operator, status=UserStatus.active, location_id=loc_operador.id)
ana      = User(name="Ana García",          email="ana@mercadoplug.com",      password_hash=hash_password("Ana2026$seller"),      phone="+1 809-111-2233", role=UserRole.seller,   status=UserStatus.active, location_id=loc_ana.id)
maria    = User(name="María Rodríguez",     email="maria@mercadoplug.com",    password_hash=hash_password("Maria2026$seller"),    phone="+1 849-333-4455", role=UserRole.seller,   status=UserStatus.active, location_id=loc_maria.id)
carlos   = User(name="Carlos López",        email="carlos@mercadoplug.com",   password_hash=hash_password("Carlos2026$buyer"),    phone="+1 829-555-7788", role=UserRole.buyer,    status=UserStatus.active, location_id=loc_carlos.id)
pedro    = User(name="Pedro Martínez",      email="pedro@mercadoplug.com",    password_hash=hash_password("Pedro2026$buyer"),     phone="+1 809-777-9900", role=UserRole.buyer,    status=UserStatus.active, location_id=loc_pedro.id)
lucia    = User(name="Lucía Fernández",     email="lucia@mercadoplug.com",    password_hash=hash_password("Lucia2026$buyer"),     phone="+1 829-444-6600", role=UserRole.buyer,    status=UserStatus.active, location_id=loc_lucia.id)

for u in [admin, operador, ana, maria, carlos, pedro, lucia]:
    db.add(u)
db.flush()

# ─────────────────────────────────────────────────────────────────
# TIENDAS
# ─────────────────────────────────────────────────────────────────
print(">> Creando tiendas...")

t_elec = Store(
    seller_id=ana.id, store_name="Electrónica Rápida", slug="electronica-rapida",
    description="Los mejores gadgets, accesorios y electrónica al mejor precio en Santiago.",
    logo_url="https://placehold.co/200x200?text=ER", cover_image_url="https://placehold.co/1200x400?text=Electronica+Rapida",
    whatsapp_number="+1 809-111-2233", location_id=loc_t_elec.id, status=StoreStatus.active, commission_rate=Decimal("0.04"),
)
t_moda = Store(
    seller_id=maria.id, store_name="Moda Urban", slug="moda-urban",
    description="Ropa, calzado y accesorios de tendencia. Envíos a todo el país.",
    logo_url="https://placehold.co/200x200?text=MU", cover_image_url="https://placehold.co/1200x400?text=Moda+Urban",
    whatsapp_number="+1 849-333-4455", location_id=loc_t_moda.id, status=StoreStatus.active, commission_rate=Decimal("0.04"),
)
t_hogar = Store(
    seller_id=ana.id, store_name="Hogar & Deco", slug="hogar-deco",
    description="Todo para tu hogar: muebles, decoración y artículos del hogar.",
    logo_url="https://placehold.co/200x200?text=HD", cover_image_url="https://placehold.co/1200x400?text=Hogar+Deco",
    whatsapp_number="+1 809-111-2233", location_id=loc_t_hogar.id, status=StoreStatus.active, commission_rate=Decimal("0.05"),
)

for s in [t_elec, t_moda, t_hogar]:
    db.add(s)
db.flush()

# ─────────────────────────────────────────────────────────────────
# PRODUCTOS Y SERVICIOS
# ─────────────────────────────────────────────────────────────────
print(">> Creando productos y servicios...")

def prod(store, name, desc, price, cat, ptype, images, delivery, stock=StockStatus.available):
    return Product(
        store_id=store.id, name=name, description=desc, price=price,
        currency="DOP", category=cat, type=ptype, images=images,
        stock_status=stock, whatsapp_number=store.whatsapp_number,
        location_id=store.location_id, delivery=delivery, status=ProductStatus.active,
    )

p_audifonos  = prod(t_elec,  "Audífonos Bluetooth Pro Max",     "Audífonos inalámbricos con cancelación activa de ruido, 30h de batería y estuche de carga.",     3500,  "Electrónica",      ProductType.product,  ["https://placehold.co/600x400?text=Audifonos"],  True)
p_cargador   = prod(t_elec,  "Cargador USB-C 65W GaN",          "Cargador rápido compacto compatible con laptops, tablets y smartphones.",                        1200,  "Electrónica",      ProductType.product,  ["https://placehold.co/600x400?text=Cargador"],   True)
p_smartwatch = prod(t_elec,  "Smartwatch Fitness Band X5",      "Reloj inteligente con monitor de frecuencia cardíaca, GPS y resistencia al agua IP68.",           4800,  "Electrónica",      ProductType.product,  ["https://placehold.co/600x400?text=Smartwatch"], True)
p_parlante   = prod(t_elec,  "Parlante Bluetooth Portátil",     "Sonido 360°, resistente al agua IPX7, batería de 12h. Ideal para exteriores.",                   2900,  "Electrónica",      ProductType.product,  ["https://placehold.co/600x400?text=Parlante"],   True)
p_reparacion = prod(t_elec,  "Reparación de Pantallas",         "Servicio de cambio de pantalla para iPhone y Samsung. Garantía de 3 meses.",                     1800,  "Servicios Técnicos", ProductType.service, ["https://placehold.co/600x400?text=Reparacion"], False)
p_cctv       = prod(t_elec,  "Instalación de CCTV (4 cámaras)", "Instalación profesional de sistema de cámaras HD con acceso remoto.",                           12000, "Servicios Técnicos", ProductType.service, ["https://placehold.co/600x400?text=CCTV"],       False)
p_tenis      = prod(t_moda,  "Tenis Nike Air Max 270",          "Zapatillas deportivas originales, tallas 37-44. Varios colores.",                                 6500,  "Calzado",          ProductType.product,  ["https://placehold.co/600x400?text=Tenis+Nike"], True)
p_blusa      = prod(t_moda,  "Blusa Lino Verano",               "Blusa de lino de alta calidad, perfecta para el verano. Tallas S-XL.",                            950,  "Ropa",             ProductType.product,  ["https://placehold.co/600x400?text=Blusa"],      True)
p_cartera    = prod(t_moda,  "Cartera de Cuero Genuine",        "Cartera artesanal 100% cuero genuino. Compartimentos para tarjetas y billete.",                   2200,  "Accesorios",       ProductType.product,  ["https://placehold.co/600x400?text=Cartera"],    True)
p_gafas      = prod(t_moda,  "Gafas de Sol Polarizadas UV400",  "Protección UV400, marco metálico liviano, unisex. Incluye estuche y paño.",                       1400,  "Accesorios",       ProductType.product,  ["https://placehold.co/600x400?text=Gafas"],      True)
p_asesoria   = prod(t_moda,  "Asesoría de Imagen Personal",     "Sesión de 1h con estilista: colorimetría, tipo de cuerpo y armado de outfits.",                   3500,  "Servicios",        ProductType.service,  ["https://placehold.co/600x400?text=Asesoria"],   False)
p_toallas    = prod(t_hogar, "Set de Toallas de Baño Premium",  "Juego de 4 toallas 100% algodón egipcio, ultra absorbentes. 6 colores.",                          1800,  "Hogar",            ProductType.product,  ["https://placehold.co/600x400?text=Toallas"],    True)
p_lampara    = prod(t_hogar, "Lámpara de Pie LED Regulable",    "Lámpara moderna con 3 tonos de luz y regulador de intensidad. Base de mármol sintético.",         3200,  "Decoración",       ProductType.product,  ["https://placehold.co/600x400?text=Lampara"],    True)
p_deco       = prod(t_hogar, "Servicio de Decoración de Interiores", "Diseño y decoración de salas, habitaciones o espacios de trabajo. Presupuesto sin costo.",   8500,  "Servicios",        ProductType.service,  ["https://placehold.co/600x400?text=Decoracion"], False)

all_products = [p_audifonos, p_cargador, p_smartwatch, p_parlante, p_reparacion, p_cctv,
                p_tenis, p_blusa, p_cartera, p_gafas, p_asesoria,
                p_toallas, p_lampara, p_deco]
for p in all_products:
    db.add(p)
db.flush()

# ─────────────────────────────────────────────────────────────────
# PEDIDOS
# ─────────────────────────────────────────────────────────────────
print(">> Creando pedidos...")

def make_order(user, product, qty=1, status=OrderStatus.pending, address=None, notes=None):
    return Order(
        user_id=user.id, product_id=product.id, store_id=product.store_id,
        quantity=qty, unit_price=product.price, currency=product.currency,
        status=status, delivery_address=address, notes=notes,
    )

# Pedidos entregados (generarán ventas y comisiones)
o1 = make_order(carlos, p_audifonos,  status=OrderStatus.delivered, address="Calle 5 #88, Los Mameyes", notes="Dejar con el portero")
o2 = make_order(pedro,  p_tenis,      status=OrderStatus.delivered, address="Calle Duarte #56, Miramar")
o3 = make_order(carlos, p_cargador,   status=OrderStatus.delivered, address="Calle 5 #88, Los Mameyes")
o4 = make_order(lucia,  p_lampara,    status=OrderStatus.delivered, address="Av. 27 de Febrero #310, Santiago")
o5 = make_order(pedro,  p_toallas,    status=OrderStatus.delivered, address="Calle Duarte #56, Miramar")
o6 = make_order(carlos, p_smartwatch, status=OrderStatus.delivered, address="Calle 5 #88, Los Mameyes")

# Pedidos en progreso
o7  = make_order(pedro,  p_blusa,     status=OrderStatus.shipped,   address="Calle Duarte #56, Miramar")
o8  = make_order(lucia,  p_cartera,   status=OrderStatus.confirmed, address="Av. 27 de Febrero #310, Santiago")
o9  = make_order(carlos, p_parlante,  status=OrderStatus.confirmed, address="Calle 5 #88, Los Mameyes")
o10 = make_order(pedro,  p_gafas,     status=OrderStatus.pending,   address="Calle Duarte #56, Miramar")
o11 = make_order(lucia,  p_audifonos, status=OrderStatus.pending,   notes="Quiero el color negro")

# Cancelados
o12 = make_order(carlos, p_asesoria,  status=OrderStatus.cancelled)
o13 = make_order(pedro,  p_deco,      status=OrderStatus.cancelled)

all_orders = [o1, o2, o3, o4, o5, o6, o7, o8, o9, o10, o11, o12, o13]
for o in all_orders:
    db.add(o)
db.flush()

# ─────────────────────────────────────────────────────────────────
# VENTAS (por pedidos entregados)
# ─────────────────────────────────────────────────────────────────
print(">> Creando ventas...")

delivered_orders = [o1, o2, o3, o4, o5, o6]
sales_list = []
for order in delivered_orders:
    store = next(s for s in [t_elec, t_moda, t_hogar] if s.id == order.store_id)
    sale = Sale(
        order_id=order.id, store_id=order.store_id, product_id=order.product_id,
        seller_id=store.seller_id, amount=order.unit_price * order.quantity, currency=order.currency,
    )
    db.add(sale)
    sales_list.append((sale, store))
db.flush()

# ─────────────────────────────────────────────────────────────────
# COMISIONES (generadas por cada venta)
# ─────────────────────────────────────────────────────────────────
print(">> Creando comisiones...")

commissions_list = []
for sale, store in sales_list:
    commission = Commission(
        sale_id=sale.id, store_id=store.id,
        amount=sale.amount * store.commission_rate,
        rate=store.commission_rate,
        status=CommissionStatus.pending,
    )
    db.add(commission)
    commissions_list.append(commission)
db.flush()

# Simular que Electrónica Rápida ya pagó sus primeras 2 comisiones
elec_comms = [c for c in commissions_list if c.store_id == t_elec.id][:2]
settled_amount = sum(c.amount for c in elec_comms)
for c in elec_comms:
    c.status = CommissionStatus.paid

payment = CommissionPayment(
    store_id=t_elec.id, amount_paid=settled_amount,
    commissions_count=len(elec_comms),
    notes="Transferencia Banco Popular — ref. MP-2026-001",
    settled_by=operador.id,
)
db.add(payment)
db.flush()

# ─────────────────────────────────────────────────────────────────
# INTERACCIONES
# ─────────────────────────────────────────────────────────────────
print(">> Creando interacciones...")

interactions = [
    # Carlos — interesado en Electrónica
    ProductInteraction(user_id=carlos.id, product_id=p_audifonos.id,  store_id=t_elec.id, action=InteractionAction.click_buy_product),
    ProductInteraction(user_id=carlos.id, product_id=p_smartwatch.id, store_id=t_elec.id, action=InteractionAction.click_buy_product),
    ProductInteraction(user_id=carlos.id, product_id=p_cargador.id,   store_id=t_elec.id, action=InteractionAction.click_buy_product),
    ProductInteraction(user_id=carlos.id, product_id=p_parlante.id,   store_id=t_elec.id, action=InteractionAction.view_product),
    ProductInteraction(user_id=carlos.id, product_id=p_audifonos.id,  store_id=t_elec.id, action=InteractionAction.click_buy_product),
    # Pedro — interesado en Moda y Hogar
    ProductInteraction(user_id=pedro.id,  product_id=p_tenis.id,     store_id=t_moda.id,  action=InteractionAction.click_buy_product),
    ProductInteraction(user_id=pedro.id,  product_id=p_blusa.id,     store_id=t_moda.id,  action=InteractionAction.click_buy_product),
    ProductInteraction(user_id=pedro.id,  product_id=p_toallas.id,   store_id=t_hogar.id, action=InteractionAction.click_buy_product),
    ProductInteraction(user_id=pedro.id,  product_id=p_gafas.id,     store_id=t_moda.id,  action=InteractionAction.view_product),
    # Lucía — interesada en Decoración y Accesorios
    ProductInteraction(user_id=lucia.id,  product_id=p_lampara.id,   store_id=t_hogar.id, action=InteractionAction.click_buy_product),
    ProductInteraction(user_id=lucia.id,  product_id=p_cartera.id,   store_id=t_moda.id,  action=InteractionAction.click_buy_product),
    ProductInteraction(user_id=lucia.id,  product_id=p_gafas.id,     store_id=t_moda.id,  action=InteractionAction.click_buy_product),
    ProductInteraction(user_id=lucia.id,  product_id=p_audifonos.id, store_id=t_elec.id,  action=InteractionAction.view_product),
    # Anónimos
    ProductInteraction(user_id=None, product_id=p_audifonos.id,  store_id=t_elec.id,  action=InteractionAction.view_product),
    ProductInteraction(user_id=None, product_id=p_tenis.id,      store_id=t_moda.id,  action=InteractionAction.click_buy_product),
]
for i in interactions:
    db.add(i)
db.flush()

# ─────────────────────────────────────────────────────────────────
# PRODUCTOS GUARDADOS
# ─────────────────────────────────────────────────────────────────
print(">> Creando productos guardados...")

saved = [
    SavedProduct(user_id=carlos.id, product_id=p_smartwatch.id),
    SavedProduct(user_id=carlos.id, product_id=p_parlante.id),
    SavedProduct(user_id=carlos.id, product_id=p_tenis.id),
    SavedProduct(user_id=pedro.id,  product_id=p_audifonos.id),
    SavedProduct(user_id=pedro.id,  product_id=p_cartera.id),
    SavedProduct(user_id=lucia.id,  product_id=p_lampara.id),
    SavedProduct(user_id=lucia.id,  product_id=p_audifonos.id),
    SavedProduct(user_id=lucia.id,  product_id=p_tenis.id),
]
for sv in saved:
    db.add(sv)

db.commit()

# ─────────────────────────────────────────────────────────────────
# RESUMEN
# ─────────────────────────────────────────────────────────────────
total_revenue = sum(Decimal(str(o.unit_price)) * o.quantity for o in delivered_orders)
pending_commissions = sum(
    c.amount for c in commissions_list if c.status == CommissionStatus.pending
)

print("\n" + "=" * 60)
print("  SEED COMPLETADO — MERCADO PLUG")
print("=" * 60)

print(f"\n{'ROL':<10} {'EMAIL':<36} PASSWORD")
print("-" * 60)
print(f"{'admin':<10} {'admin@mercadoplug.com':<36} Admin2026$")
print(f"{'operator':<10} {'operador@mercadoplug.com':<36} Operador2026$")
print(f"{'seller':<10} {'ana@mercadoplug.com':<36} Ana2026$seller")
print(f"{'seller':<10} {'maria@mercadoplug.com':<36} Maria2026$seller")
print(f"{'buyer':<10} {'carlos@mercadoplug.com':<36} Carlos2026$buyer")
print(f"{'buyer':<10} {'pedro@mercadoplug.com':<36} Pedro2026$buyer")
print(f"{'buyer':<10} {'lucia@mercadoplug.com':<36} Lucia2026$buyer")

print(f"\n  Usuarios creados:     7")
print(f"  Tiendas creadas:      3")
print(f"  Productos creados:    {len(all_products)}")
print(f"  Pedidos creados:      {len(all_orders)}  (6 entregados, 3 en progreso, 2 pendientes, 2 cancelados)")
print(f"  Ventas generadas:     {len(sales_list)}")
print(f"  Comisiones:           {len(commissions_list)}  ({len(elec_comms)} pagadas, {len(commissions_list)-len(elec_comms)} pendientes)")
print(f"  Ingresos totales:     DOP {total_revenue:,.2f}")
print(f"  Comisiones pendientes: DOP {pending_commissions:,.2f}")
print(f"  Interacciones:        {len(interactions)}")
print(f"  Productos guardados:  {len(saved)}")

print(f"\n  IDs de referencia:")
print(f"  Admin:     id={admin.id}   | Operador: id={operador.id}")
print(f"  Ana:       id={ana.id}    | Maria:    id={maria.id}")
print(f"  Carlos:    id={carlos.id}    | Pedro:    id={pedro.id}    | Lucia: id={lucia.id}")
print(f"  T.Elec:    id={t_elec.id}    | T.Moda:   id={t_moda.id}    | T.Hogar: id={t_hogar.id}")
print("=" * 60)

db.close()
