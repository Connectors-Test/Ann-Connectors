from odoo_rpc_client import create, search_read
from pprint import pprint

def main():
    print("\n== Odoo Demo Interface ==")
    while True:
        print("\nSelect action:")
        print("1. Show all customers (res.partner)")
        print("2. Create new customer")
        print("3. Show all quotations (sale.order)")
        print("4. Create new quotation for a customer")
        print("0. Exit")
        choice = input("Enter choice: ").strip()

        if choice == "1":
            customers = search_read("res.partner", fields=["id", "name", "email"])
            pprint(customers)

        elif choice == "2":
            name = input("Customer name: ").strip()
            email = input("Email (optional): ").strip()
            partner_id = create("res.partner", {"name": name, "email": email})
            print(f"Created customer with ID: {partner_id}")

        elif choice == "3":
            quotes = search_read("sale.order", fields=["id", "name", "partner_id", "amount_total"])
            pprint(quotes)

        elif choice == "4":
            partner_id = int(input("Enter customer ID to create quotation for: "))
            quote_id = create("sale.order", {
                "partner_id": partner_id,
                "date_order": "2024-08-02",
                "validity_date": "2024-09-04",
            })
            print(f"Created quotation with ID: {quote_id}")

        elif choice == "0":
            print("Exiting.")
            break
        else:
            print("Invalid choice. Try again.")

if __name__ == "__main__":
    main()
