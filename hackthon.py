import random
import time
import threading
from collections import deque

# ------------------ MODELS ------------------

class Product:
    def __init__(self, pid, name, price, stock):
        self.pid = pid
        self.name = name
        self.price = price
        self.stock = stock
        self.lock = threading.Lock()

class Order:
    def __init__(self, oid, user, items, total):
        self.oid = oid
        self.user = user
        self.items = items
        self.total = total
        self.status = "CREATED"

# ------------------ GLOBAL STORAGE ------------------

products = {}
carts = {}
orders = {}
logs = []
event_queue = deque()
processed_requests = set()
user_order_times = {}

order_counter = 1

# ------------------ LOGGING ------------------

def log(msg):
    timestamp = time.strftime("%H:%M:%S")
    entry = f"[{timestamp}] {msg}"
    logs.append(entry)

# ------------------ PRODUCT ------------------

def add_product():
    pid = input("Product ID: ")
    if pid in products:
        print("Duplicate ID")
        return

    name = input("Name: ")
    price = float(input("Price: "))
    stock = int(input("Stock: "))

    if stock < 0:
        print("Invalid stock")
        return

    products[pid] = Product(pid, name, price, stock)
    log(f"Product {pid} added")

def view_products():
    if not products:
        print("No products available")
    for p in products.values():
        print(p.pid, p.name, p.price, p.stock)

# ------------------ CART ------------------

def add_to_cart():
    user = input("User: ")
    pid = input("Product ID: ")
    qty = int(input("Qty: "))

    if pid not in products:
        print("Invalid product")
        return

    product = products[pid]

    with product.lock:   # REAL LOCK
        if product.stock < qty:
            print("Not enough stock")
            return

        product.stock -= qty

    carts.setdefault(user, {})
    carts[user][pid] = carts[user].get(pid, 0) + qty

    log(f"{user} added {pid} x{qty}")

    # reservation expiry
    #4threading.Timer(70, release_stock, args=(user, pid, qty)).start()

def release_stock(user, pid, qty):
    if user in carts and pid in carts[user]:
        products[pid].stock += qty
        carts[user][pid] -= qty
        if carts[user][pid] <= 0:
            del carts[user][pid]
        log(f"Stock released for {pid}")

def view_cart():
    user = input("User: ")
    if user not in carts or not carts[user]:
        print("❌ Cart is empty")
        return

    total = 0
    for pid, qty in carts[user].items():
        p = products[pid]
        print(p.name, qty)
        total += p.price * qty
    print("Total:", total)

# ------------------ DISCOUNT & COUPON ------------------

def apply_discount(total, cart, coupon=None):
    if total > 1000:
        total *= 0.9

    for pid, qty in cart.items():
        if qty > 3:
            total *= 0.95

    if coupon == "SAVE10":
        total *= 0.9
    elif coupon == "FLAT200":
        total -= 200

    return max(total, 0)

# ------------------ STATE MACHINE ------------------

valid_transitions = {
    "CREATED": ["PAID", "FAILED", "CANCELLED"],
    "PAID": ["SHIPPED", "CANCELLED"],
    "SHIPPED": ["DELIVERED"],
    "DELIVERED": [],
    "FAILED": [],
    "CANCELLED": []
}

def update_status(order, new_status):
    if new_status in valid_transitions[order.status]:
        order.status = new_status
        return True
    return False

# ------------------ EVENT SYSTEM ------------------

def process_events():
    while event_queue:
        event = event_queue.popleft()
        if event == "FAIL":
            print("Event failed, stopping chain")
            break
        print("Processed:", event)

# ------------------ ORDER ------------------

def place_order():
    global order_counter

    user = input("User: ")
    request_id = input("Request ID: ")

    if request_id in processed_requests:
        print("Duplicate request")
        return

    processed_requests.add(request_id)

    if user not in carts or not carts[user]:
        print("Empty cart")
        return

    cart = carts[user]
    print("DEBUG CART:", carts)
    coupon = input("Coupon (optional): ")

    total = sum(products[pid].price * qty for pid, qty in cart.items())
    total = apply_discount(total, cart, coupon)

    oid = order_counter
    order_counter += 1

    order = Order(oid, user, cart.copy(), total)
    orders[oid] = order

    carts[user] = {}

    log(f"Order {oid} created")

    event_queue.append("ORDER_CREATED")

    # simulate failure injection
    if random.choice([True, False]):
        event_queue.append("FAIL")
    else:
        event_queue.append("PAYMENT_SUCCESS")

    process_payment(order)

# ------------------ PAYMENT ------------------

def process_payment(order):
    if random.choice([True, False]):
        update_status(order, "PAID")
        print("Payment success")
        event_queue.append("INVENTORY_UPDATED")
        check_fraud(order.user)
    else:
        print("Payment failed")
        rollback(order)

    process_events()

# ------------------ ROLLBACK ------------------

def rollback(order):
    for pid, qty in order.items.items():
        products[pid].stock += qty
    update_status(order, "FAILED")
    log(f"Order {order.oid} failed")

# ------------------ CANCEL ------------------

def cancel_order():
    oid = int(input("Order ID: "))

    if oid not in orders:
        print("❌ Order not found")
        return

    order = orders[oid]   # ✅ define order here

    if order.status in ["FAILED", "CANCELLED"]:
        print("❌ Cannot cancel this order")
        return

    # restore stock
    for pid, qty in order.items.items():
        products[pid].stock += qty

    order.status = "CANCELLED"   # ✅ now valid

    print("✅ Order cancelled successfully")

# ------------------ RETURN ------------------

def return_product():
    oid = int(input("Order ID: "))
    pid = input("Product ID: ")
    qty = int(input("Qty: "))

    order = orders[oid]
    products[pid].stock += qty
    order.total -= products[pid].price * qty

# ------------------ FRAUD ------------------

def check_fraud(user):
    now = time.time()
    user_order_times.setdefault(user, [])
    user_order_times[user] = [t for t in user_order_times[user] if now - t < 60]
    user_order_times[user].append(now)

    if len(user_order_times[user]) >= 3:
        print("Fraud detected!")

# ------------------ LOW STOCK ------------------

def low_stock():
    found = False

    for p in products.values():
        if p.stock <= 0:
            print(p.name, "OUT OF STOCK")
            found = True
        elif p.stock < 5:
            print(p.name, "LOW STOCK")
            found = True

    if not found:
        print("✅ All products have sufficient stock")

# ------------------ VIEW ------------------

def view_orders():
    if not orders:
        print("❌ No orders available")
        return

    for o in orders.values():
        print(o.oid, o.user, o.total, o.status)

def view_logs():
    for l in logs:
        print(l)

# ------------------ CONCURRENCY ------------------

def simulate_concurrency():
    def user_action(name):
        add_to_cart()

    t1 = threading.Thread(target=user_action, args=("A",))
    t2 = threading.Thread(target=user_action, args=("B",))

    t1.start()
    t2.start()

    t1.join()
    t2.join()

# ------------------ MENU ------------------

def menu():
    while True:
        print("\n1.Add Product 2.View Products 3.Add Cart 4.View Cart")
        print("5.Place Order 6.Cancel 7.View Orders 8.Low Stock")
        print("9.Return 10.Concurrent 11.Logs 0.Exit")

        c = input("👉 Enter your choice: ")

        if c == "1": add_product()
        elif c == "2": view_products()
        elif c == "3": add_to_cart()
        elif c == "4": view_cart()
        elif c == "5": place_order()
        elif c == "6": cancel_order()
        elif c == "7": view_orders()
        elif c == "8": low_stock()
        elif c == "9": return_product()
        elif c == "10": simulate_concurrency()
        elif c == "11": view_logs()
        elif c == "0": break

if __name__ == "__main__":
    menu()