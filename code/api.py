from datetime import datetime

from requests import post

from configure import CLIENT_ID, API_KEY, WAREHOUSE


def get_orders_list(day_from: datetime, day_to: datetime, orders_status='', check_status=[]):
    headers = {
        'Client-Id': CLIENT_ID,
        'Api-Key': API_KEY
    }

    status = True
    order_list = []
    index = 0

    while status is True:
        body = {
            "dir": "ASC",
            "filter": {
                "since": f"{day_from.strftime('%Y-%m-%d')}T00:00:00.000Z",
                "status": orders_status,
                "to": f"{day_to.strftime('%Y-%m-%d')}T23:59:59.000Z"
            },
            "limit": 1000,
            "offset": index,
            "translit": True,
        }

        index += 1000
        req = post('https://api-seller.ozon.ru/v3/posting/fbs/list', headers=headers, json=body)
        if req.status_code != 200:
            break

        orders = req.json()['result']
        status = orders['has_next']
        last_order = {}

        postings = orders['postings']
        for posting in postings:
            if posting['delivery_method']['warehouse_id'] == WAREHOUSE:
                order_id = posting['posting_number']
                order_status = posting['status']
                shipment_date = posting['shipment_date'][:-10]
                create_date = posting['in_process_at'][:-10]
                
                products = posting['products']
                for product in products:
                    sku = str(product['sku'])
                    offer_id = product['offer_id']
                    name = product['name']
                    quantity = product['quantity']
                    price = int(product['price'].split('.')[0])

                    order_id_to_check = order_id.split('-')[0] + '-' + order_id.split('-')[1]
                    if order_list == []:
                        last_order = {
                            'order_id': order_id, 
                            'offer_id': offer_id, 
                            'sku': sku,
                            'name': name, 
                            'quantity': quantity, 
                            'price': price,
                            'create_date': create_date,
                            'shipment_date': shipment_date
                        }

                        order_list.append(last_order)
                        
                    elif check_status != [] and not order_status in check_status:
                        break

                    elif order_id_to_check in last_order.get('order_id') and sku == last_order.get('sku'):
                        last_order['quantity'] += quantity
                     
                    else:
                        last_order = {
                            'order_id': order_id, 
                            'offer_id': offer_id, 
                            'sku': sku,
                            'name': name, 
                            'quantity': quantity,
                            'price': price, 
                            'create_date': create_date,
                            'shipment_date': shipment_date
                        }

                        order_list.append(last_order)

    return order_list


def get_transaction_list(day_from: datetime, day_to: datetime):
    headers = {
        'Client-Id': CLIENT_ID,
        'Api-Key': API_KEY
    }

    status = True
    transaction_list = []
    index = 1
    
    while status is True:
        body = {
            "filter": {
                "date": {
                    "from": f"{day_from.strftime('%Y-%m-%d')}T00:00:00.000Z",
                    "to": f"{day_to.strftime('%Y-%m-%d')}T23:59:59.000Z"
                },
                "operation_type": [],
                "posting_number": "",
                "transaction_type": "all"
            },
            "page": index,
            "page_size": 1000
        }   
    
        index += 1
        req = post('https://api-seller.ozon.ru/v3/finance/transaction/list', headers=headers, json=body)

        if req.status_code != 200 or req.json() == []:
            break

        transactions = req.json()['result']['operations']
        for transaction in transactions:
            transaction_type = transaction['type']
            posting_number = transaction['posting']['posting_number']
            sku = str(transaction['items'][0]['sku'])

            # Доставка покупателю
            if transaction_type == 'orders':
                delivery_charge = transaction['delivery_charge']
                commission = transaction['sale_commission']
                operation_date = transaction['operation_date'][:10]
                all_delivery_spending = delivery_charge

                for delivery_spending in transaction['services']:
                    all_delivery_spending += delivery_spending['price'] 

                transaction_list.append({
                    'order_id': posting_number, 
                    'delivery_spending': all_delivery_spending, 
                    'commission': commission, 
                    'operation_date': operation_date, 
                    'transaction_type': transaction_type,
                    'sku': sku
                })

            # Эквайринг    
            elif transaction_type == 'other':
                acquiring = int(transaction['services'][0]['price'])

                transaction_list.append({
                    'order_id': posting_number, 
                    'acquiring': acquiring, 
                    'transaction_type': transaction_type,
                    'sku': sku
                })

            # Возврат товара
            elif transaction_type == 'returns':
                return_delivery_charge = transaction['return_delivery_charge']
                all_delivery_return_spending = return_delivery_charge 
                
                for delivery_return_spending in transaction['services']:
                    all_delivery_return_spending += delivery_return_spending['price']

                transaction_list.append({
                    'order_id': posting_number, 
                    'delivery_return_spending': all_delivery_return_spending,
                    'transaction_type': transaction_type,
                    'sku': sku
                })

            # Хранение возврата
            elif transaction_type == 'services':
                return_spending = transaction['services'][0]['price']
            
                transaction_list.append({
                    'order_id': posting_number, 
                    'return_spending': return_spending,
                    'transaction_type': transaction_type,
                    'sku': sku
                })
            

        body = {
            "filter": {
                "date": {
                    "from": f"{day_from.strftime('%Y-%m-%d')}T00:00:00.000Z",
                    "to": f"{day_to.strftime('%Y-%m-%d')}T23:59:59.000Z"
                },
                "operation_type": [],
                "posting_number": "",
                "transaction_type": "all"
            },
            "page": index,
            "page_size": 1000
        }   

        req = post('https://api-seller.ozon.ru/v3/finance/transaction/list', headers=headers, json=body)
        if req.json()['result']['operations'] == []:
            status = False

    return transaction_list
