# Ecommerce_Order_Engine_Hackathon
# 1. Project Overview
# 🛒 Distributed E-Commerce Order Engine
This project is a CLI-based backend simulation of a real-world e-commerce system like Amazon or Flipkart.
The system handles product management, multi-user carts, order processing, payment simulation, and inventory consistency.
It is designed to mimic real backend challenges such as concurrency, stock reservation, payment failures, rollback mechanisms, and event-driven processing.

# 2. Features Implemented
## 🚀Features
- Product Management (Add, View, Update Stock)
- Multi-User Cart System
- Real-Time Stock Reservation
- Concurrency Handling using Locks
- Order Placement Engine
- Payment Simulation (Success/Failure)
- Transaction Rollback System
- Order State Machine (CREATED → PAID → SHIPPED → DELIVERED)
- Discount & Coupon Engine
- Inventory Alert System (Low Stock / Out of Stock)
- Order Management (View, Cancel)
- Return & Refund System
- Event-Driven Processing System
- Inventory Reservation Expiry
- Audit Logging System
- Fraud Detection System
- Failure Injection (Random Failures)
- Idempotency Handling (Duplicate Request Prevention)
- Modular Design (Simulating Microservices)

# 3. Design Approach
## 🏗️ Design Approach
The system is designed using a modular and scalable approach:

- Separate components for Products, Cart, Orders, and Payment
- Used Python dictionaries for fast in-memory storage
- Implemented locking mechanism to avoid race conditions
- Used event queue to simulate event-driven architecture
- Applied state machine logic to manage order lifecycle
- Implemented rollback mechanism to ensure data consistency
- Used threading to simulate concurrency and reservation expiry

# 4. Assumptions
## ⚠️Assumptions
- Data is stored in-memory (no database used)
- Single machine simulation (not distributed physically)
- Users are identified by simple string IDs
- Payment success/failure is simulated randomly
- Reservation expiry is time-based using threads
- CLI-based interaction (no UI)

  # 5.How to Run the Project
  ## ▶️ How to Run

1. Install Python (version 3.x)

2. Download or clone the repository:
   git clone <your-repo-link>

3. Navigate to project folder:
   cd ecommerce_engine

4. Run the program:
   python hackthon.py

5. Use the menu options to interact with the system
