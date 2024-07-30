GADGETS = [1953, 2539, 2541, 3533, 2543, 2525, 3543, 3539, 3551, 2529, 2535, 3529, 3532, 3517, 2533, 2537, 3519, 
	3468, 4680, 3532, 2506, 3512, 4879, 4881, 4886]
INSCRIPTIONS_ANIMATIONS = [
	5164, # 1er août
	4643, # anciens
	4315, # célibataires
	4311, # Miss
	4307, # Mister
	4306, # Burgers
	4298, # Match aux cartes
	4293, # Bûcheronnage
]
INSCRIPTIONS_SPORTS = [
	4462, # Ultimate
	4443, # Jeux de la Canto
	4423, # Pétanque
	4322, # Raid
	4094, # Quidditch
	3994, # Fun Cross
	3991, # Lacrosse (RIP)
	3990, # Volley mixte
	3988, # Hockey sur gazon
	3987, # Tir à la corde féminin
	3986, # Lutte féminine
	3985, # Beach foot
	3984, # Bad beach
	3983, # Dodgeball
	3982, # Spike Ball
	3992, # Beer pong
	3981, # Beach hand
]
INSCRIPTIONS = INSCRIPTIONS_ANIMATIONS + INSCRIPTIONS_SPORTS

def gadget_or_inscr(id):
    if id in GADGETS:
        return "Gadget"
    elif id in INSCRIPTIONS_ANIMATIONS:
        return "Animation"
    elif id in INSCRIPTIONS_SPORTS:
        return "Sport"
    else:
        raise ValueError(f"Erreur : un produit est inconnu (ni gadget ni sport) : {id}.")

def find_quantity(x):
    if x['item_type'] == 'Gadget':
        return int(x['item_quantity'])
    else:
        meta = x['item_meta_data']
        if meta[0]['id'] == 10:
            quantity_key = '22'
        elif x['item_product_id'] in [4307]:
            return 1
        elif x['item_product_id'] in [4322,4311]:
            return x['item_quantity']
            # if meta[-1]['key'] == '_reduced_stock':
            #     found = int(meta[-1]['value'])
            #     if found > 100:
            #         return 1
            #     else:
            #         return found
            # else:
            #     return 1
        elif x['item_product_id'] == 5164:
            quantity_key = meta[0]['value']['_gravity_form_data']['cart_quantity_field']
            return int(meta[0]['value']['_gravity_form_lead'][quantity_key]) * x['item_quantity']
        else:
            quantity_key = meta[0]['value']['_gravity_form_data']['cart_quantity_field']
            
        if quantity_key:
            value = int(meta[0]['value']['_gravity_form_lead'][quantity_key])
            if value > 100:
                return 1
            else: 
                return value
        else:
            return 1

def find_unit_price(x):
    meta = x['item_meta_data']
    if x['item_type'] == 'Gadget':
        found = x['item_price']
    elif x['item_product_id'] in [4307]:
        found = 0
    elif x['item_product_id'] in [4311]:
        found = 1
    else:
        form = meta[0]['value']['_gravity_form_lead']
            
        if '21.2' in form:
            found = form['21.2']
        elif '23' in form:
            found = str(form['23'])
    
    if isinstance(found, str):
        found = float(found.replace('CHF',''))

    return int(found)

def check_twint_payment(x):
    return "; ".join(f"{k['value']['status']} (ref. {k['value']['reference']})" for k in x if k['key'] == '_mame_twint_order')

def get_details(row):
    if row['item_type']=='Gadget':
        return "; ".join(f"{k['display_key']}: {k['display_value']}" for k in row['item_meta_data'] if k['display_key'][0]!='_')
    else:
        return ""