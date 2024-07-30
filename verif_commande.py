from io import BytesIO

import streamlit as st

import pandas as pd
from woocommerce import API

from utils import gadget_or_inscr, find_quantity

st.set_page_config(layout="wide")

# from my_secrets import WooCommerce_client, WooCommerce_secret
WooCommerce_client = st.secrets['WooCommerce_client']
WooCommerce_secret = st.secrets['WooCommerce_secret']

wcapi = API(
	url="https://givrins2024.ch",
	consumer_key=WooCommerce_client,
	consumer_secret=WooCommerce_secret,
	wp_api=True,
	version="wc/v3"
)

email = st.text_input("E-mail de la réservation :","").lower()
st.write("Entez ci-dessus l'adresse mail que vous avez donnée pour la réservation et appuyez sur la toutche Enter.")

if email:
    try:
        r = wcapi.get("orders", params={'search': email})
        found_json = r.json()
        correct_json = [k for k in found_json if k['billing']['email'] == email and k['status'] != 'cancelled']

        if len(correct_json) > 0 :
            orders_df = pd.json_normalize(
                correct_json,
                meta=['id','status','date_created','shipping_total','total','billing','shipping','payment_method_title','date_paid','meta_data'],
                record_path=['line_items'],
                record_prefix='item_')

            orders_df['item_type'] = orders_df['item_product_id'].apply(gadget_or_inscr)

            orders_df = orders_df[orders_df['item_type'] != 'Gadget']
            orders_df['item_quantity_comp'] = orders_df.apply(find_quantity, axis=1)

            inscr_df = orders_df.loc[::-1]

            specific_fields = set()

            for index, row in inscr_df.iterrows():
                form_fields = [item['key'] for item in row['item_meta_data'] if item['key'][0] != '_']
                specific_fields = specific_fields | set(form_fields)
                for field in form_fields:
                    inscr_df.loc[index,field] = '/'.join(k['value'] for k in row['item_meta_data'] if k['key'] == field)
            
            specific_fields = specific_fields - {'Total'}

            final_df = inscr_df[['item_type','item_name','item_quantity_comp']+list(specific_fields)].rename(columns={'item_type':'Type','item_name':'Inscription','item_quantity_comp':'Nombre'})
            st.dataframe(final_df)
            buffer = BytesIO()
            with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                final_df.to_excel(writer,sheet_name='Réservations',index=False)
            st.download_button('Télécharger la liste',buffer.getvalue(),'Givrins2024_reservations.xlsx',mime='application/vnd.ms-excel')
        else:
            st.write(f"Aucune commande trouvée pour l'adresse mail {email}.")
    except:
        st.write(
"""Problème dans le système! Désolés pour le désagrément. 

Pouvez-vous contacter l'adresse `secretariat@grivrins2024.ch` pour leur demander de vérifier vos inscriptions manuellement ?
""")