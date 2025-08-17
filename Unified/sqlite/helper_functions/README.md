# Zoho Token Setup

## Steps

1. **Create a Self-Client**
   - Go to [Zoho API Console](https://api-console.zoho.com/).
   - Create a **Self-Client**.
   - Copy the **Client ID** and **Client Secret**.
   
     <img width="250" alt="image" src="https://github.com/user-attachments/assets/a77b6de4-d63e-466f-85db-028b7885fa88" />


2. **Generate an Authorization Code**
   - Go back to the same console, under your Self-Client → click Generate Code.
   - Enter Scope → e.g., ZohoCRM.modules.ALL or ZohoInventory.fullaccess.all (depends on product)
     
    <img width="250" alt="image" src="https://github.com/user-attachments/assets/a3641004-0d40-4acd-82a3-36ec7d179e63" />


3. **Run Script**
   - The module `save_zoho_tokens` exchanges the code for `refresh_token` (long-term)
   - This refresh_token is saved to required db (here `Ecom_connector_credentials`) and used by our `fetch_from_zoho` module to get access_token.

## Notes
- Codes expire in ~3 mins.
- Access tokens expire in 1 hr (auto-refreshed with refresh token).
- Don’t lose your refresh token — it’s permanent.
