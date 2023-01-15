from datetime import datetime

from numpy import quantile
from pandas import DataFrame, read_excel, concat

from api import get_orders_list, get_transaction_list


def create_info_table():
    order_list = []
    transaction_list = []

    end_year = datetime.now().year
    for year in range(2022, end_year+1):
        if year == 2022:
            day_from = datetime(year, 7, 31)
        else:
            day_from = datetime(year, 1, 1)

        day_to = datetime(year, 12, 31)

        order_list += get_orders_list(day_from=day_from, day_to=day_to)
        transaction_list += get_transaction_list(day_from=day_from, day_to=day_to)

    order_dict_list = []
    for order in order_list:
        order_id = order.get('order_id')
        offer_id = order.get('offer_id')
        sku = order.get('sku')
        name = order.get('name')
        quantity = order.get('quantity')
        price = order.get('price') * quantity
        create_date = order.get('create_date')
        shipment_date = order.get('shipment_date')

        order_dict_list.append({
            'Id заказа': order_id, 
            'Артикуль': offer_id, 
            'SKU': sku,
            'Название': name, 
            'Количество': quantity,
            'Затраты на товар': 0, 
            'Затраты на упоковку': 0, 
            'Затраты на доставку': 0, 
            'Затраты на возврат': 0,
            'Коммисия': 0, 
            'Эквайринг': 0,
            'Налог': 0, 
            'Все затраты': 0, 
            'Доход': price, 
            'На счет ИП': 0, 
            'Прибль': 0, 
            'Дата создания заказа': create_date, 
            'Дата отгрузки': shipment_date, 
            'Дата когда забрали заказ': ''
        })

    info_df = DataFrame(order_dict_list)

    for transaction in transaction_list:
        line_index = []

        indexs = info_df.index[info_df['SKU'] == transaction.get('sku')].to_list()
        for index in indexs:
            line_index = [index]
            order_id_to_check = transaction.get('order_id').split('-')[0] + '-' + transaction.get('order_id').split('-')[1]
            if order_id_to_check in info_df.iloc[line_index]['Id заказа'].to_list()[0]:
                break

        if line_index != []:

            all_delivery_spending = round(transaction.get('delivery_spending', 0))
            all_delivery_spending += info_df.iloc[line_index]['Затраты на доставку'].to_list()[0]
            delivery_return_spending = round(transaction.get('delivery_return_spending', 0))
            delivery_return_spending += info_df.iloc[line_index]['Затраты на возврат'].to_list()[0]
            delivery_return_spending += round(transaction.get('return_spending', 0))
            quantity = info_df.iloc[line_index]['Количество'].to_list()[0]
            
            if info_df.iloc[line_index]['Дата когда забрали заказ'].to_list()[0] != info_df.iloc[line_index]['Дата отгрузки'].to_list()[0]:
                operation_date = transaction.get('operation_date', info_df.iloc[line_index]['Дата когда забрали заказ'].to_list()[0])

            if transaction.get('acquiring', 0) > 0 or delivery_return_spending != 0:  
                acquiring = 0   
                commission = 0
                operation_date = info_df.iloc[line_index]['Дата отгрузки'].to_list()[0]
            else:
                commission = round(transaction.get('commission', info_df.iloc[line_index]['Коммисия'].to_list()[0])) * quantity
                acquiring = transaction.get('acquiring', info_df.iloc[line_index]['Эквайринг'].to_list()[0])
            all_spending = all_delivery_spending + commission + acquiring + delivery_return_spending + info_df.iloc[line_index]['Затраты на возврат'].to_list()[0]
            price = info_df.iloc[line_index]['Доход'].to_list()[0]
            amount = price + all_spending
            if amount < 0:
                amount = 0
            profit = price + all_spending

            info_df.loc[line_index, 'Затраты на доставку'] = all_delivery_spending
            info_df.loc[line_index, 'Затраты на возврат'] = delivery_return_spending
            info_df.loc[line_index, 'Коммисия'] = commission
            info_df.loc[line_index, 'Эквайринг'] = acquiring
            info_df.loc[line_index, 'Все затраты'] = all_spending
            info_df.loc[line_index, 'На счет ИП'] = amount
            info_df.loc[line_index, 'Прибль'] = profit
            info_df.loc[line_index, 'Дата когда забрали заказ'] = operation_date

    return info_df


def update_info_table(buy_df: DataFrame=None):
    info_df = read_excel('./data/info_table.xlsx')
    index = [info_df.index[info_df.count()[0] - 1]]
    date = info_df.iloc[index]['Дата создания заказа'].to_list()[0]
    index_to_drop = info_df.index[info_df['Дата создания заказа'] == date].to_list()

    info_df.drop(labels=index_to_drop, axis=0, inplace=True)
    
    day_from = datetime(int(date.split('-')[0]), int(date.split('-')[1]), int(date.split('-')[2]))
    day_to = datetime.now()

    order_list = get_orders_list(day_from=day_from, day_to=day_to)
    transaction_list = get_transaction_list(day_from=day_from, day_to=day_to)

    order_dict_list = []
    for order in order_list:
        order_id = order.get('order_id')
        offer_id = order.get('offer_id')
        sku = order.get('sku')
        name = order.get('name')
        quantity = order.get('quantity')
        price = order.get('price') * quantity
        create_date = order.get('create_date')
        shipment_date = order.get('shipment_date')

        order_dict_list.append({
            'Id заказа': order_id, 
            'Артикуль': offer_id, 
            'SKU': sku,
            'Название': name, 
            'Количество': quantity,
            'Затраты на товар': 0, 
            'Затраты на упоковку': 0, 
            'Затраты на доставку': 0, 
            'Затраты на возврат': 0,
            'Коммисия': 0, 
            'Эквайринг': 0, 
            'Налог': 0, 
            'Все затраты': 0, 
            'Доход': price, 
            'На счет ИП': 0, 
            'Прибль': 0, 
            'Дата создания заказа': create_date, 
            'Дата отгрузки': shipment_date, 
            'Дата когда забрали заказ': ''
        })

    update_df = DataFrame(order_dict_list)

    info_df = concat([info_df, update_df], ignore_index=True)

    if buy_df:
        for buy_index in range(buy_df.count()[0]):
            line_index = info_df.index[info_df['Id заказа'] == buy_df.iloc[buy_index]['Id заказа']].to_list()

            for index in line_index:
                operation_date = info_df.iloc[line_index]['Дата когда забрали заказ'].to_list()[0]
                if type(index) != list:
                    index = [index]

                if str(info_df.iloc[index]['SKU'].to_list()[0]) == str(buy_df.iloc[buy_index]['SKU']):
                    product_spending = buy_df.iloc[buy_index]['Затраты на товар']
                    pack_spending = buy_df.iloc[buy_index]['Затраты на упоковку']

                    if type(product_spending) is str: 
                        info_df.loc[index, 'Дата когда забрали заказ'] = info_df.iloc[line_index]['Дата отгрузки'].to_list()[0]
                        info_df.loc[index, 'Затраты на товар'] = product_spending
                        info_df.loc[index, 'Затраты на упоковку'] = pack_spending
                        info_df.loc[line_index, 'Прибль'] = 0
                        info_df.loc[line_index, 'На счет ИП'] = 0
                        info_df.loc[line_index, 'Налог'] = 0
                        info_df.loc[line_index, 'Доход'] = 0
                    else:
                        if product_spending > 0:
                            product_spending *= -1
                            pack_spending *= -1

                        info_df.loc[index, 'Затраты на товар'] = product_spending
                        info_df.loc[index, 'Затраты на упоковку'] = pack_spending
                        
                        all_spending = info_df.iloc[index]['Все затраты'].to_list()[0]
                        price = round(info_df.iloc[index]['Доход']).to_list()[0]
                        if info_df.iloc[index]['Затраты на возврат'].to_list()[0] != 0:
                            price = 0
                        
                        commission = info_df.iloc[index]['Коммисия'].to_list()[0]
                        acquiring = info_df.iloc[index]['Эквайринг'].to_list()[0]
                        all_delivery_spending = info_df.iloc[index]['Затраты на доставку'].to_list()[0]
                        delivery_return_spending = info_df.iloc[index]['Затраты на возврат'].to_list()[0]
                        ozon_spending = commission + acquiring + all_delivery_spending + delivery_return_spending 
                        tax = round((price + ozon_spending) * 0.07) * -1

                        if all_spending == ozon_spending:
                            all_spending = all_spending + product_spending + pack_spending
                        if info_df.iloc[index]['Налог'].to_list()[0] == 0:
                            all_spending += tax
                        if delivery_return_spending != 0:
                            all_spending = delivery_return_spending + product_spending + pack_spending 
                        amount = price + ozon_spending
                        if info_df.iloc[index]['Затраты на возврат'].to_list()[0] != 0:
                            tax = 0
                        
                        profit = price + all_spending

                        if amount < 0:
                            amount = 0

                        info_df.loc[index, 'Все затраты'] = all_spending
                        info_df.loc[index, 'Прибль'] = profit
                        info_df.loc[index, 'На счет ИП'] = amount
                        info_df.loc[index, 'Налог'] = tax
                        info_df.loc[index, 'Дата когда забрали заказ'] = operation_date

                        break

    for transaction in transaction_list:
        line_index = []

        indexs = info_df.index[info_df['SKU'] == transaction.get('sku')].to_list()
        for index in indexs:
            line_index = [index]
            order_id_to_check = transaction.get('order_id').split('-')[0] + '-' + transaction.get('order_id').split('-')[1]
            if order_id_to_check in info_df.iloc[line_index]['Id заказа'].to_list()[0]:
                break

        if line_index != []:
            all_delivery_spending = round(transaction.get('delivery_spending', 0))
            all_delivery_spending += info_df.iloc[line_index]['Затраты на доставку'].to_list()[0]
            delivery_return_spending = round(transaction.get('delivery_return_spending', 0))
            delivery_return_spending += info_df.iloc[line_index]['Затраты на возврат'].to_list()[0]
            delivery_return_spending += round(transaction.get('return_spending', 0))
            
            quantity = info_df.iloc[line_index]['Количество'].to_list()[0]
            product_spending = info_df.iloc[line_index]['Затраты на товар'].to_list()[0]
            pack_spending = info_df.iloc[line_index]['Затраты на упоковку'].to_list()[0]
            tax = info_df.iloc[line_index]['Налог'].to_list()[0]

            if info_df.iloc[line_index]['Дата когда забрали заказ'].to_list()[0] != info_df.iloc[line_index]['Дата отгрузки'].to_list()[0]:
                operation_date = transaction.get('operation_date', info_df.iloc[line_index]['Дата когда забрали заказ'].to_list()[0])

            if transaction.get('acquiring', 0) > 0 or delivery_return_spending != 0:  
                acquiring = 0   
                commission = 0
                operation_date = info_df.iloc[line_index]['Дата отгрузки'].to_list()[0]
            else:
                commission = round(transaction.get('commission', info_df.iloc[line_index]['Коммисия'].to_list()[0])) * quantity
                acquiring = transaction.get('acquiring', info_df.iloc[line_index]['Эквайринг'].to_list()[0])
            all_spending = info_df.iloc[line_index]['Все затраты'].to_list()[0] 
            if all_spending < all_delivery_spending + commission + acquiring + delivery_return_spending:
                all_spending = all_delivery_spending + commission + acquiring + delivery_return_spending
            if delivery_return_spending != 0:
                all_spending = all_spending + delivery_return_spending + product_spending + pack_spending + tax
            price = info_df.iloc[line_index]['Доход'].to_list()[0]
            ozon_spending = commission + acquiring + all_delivery_spending + delivery_return_spending 
            amount = price + ozon_spending
            if amount < 0:
                amount = 0
            profit = price + all_spending

            info_df.loc[line_index, 'Затраты на доставку'] = all_delivery_spending
            info_df.loc[line_index, 'Затраты на возврат'] = delivery_return_spending
            info_df.loc[line_index, 'Коммисия'] = commission
            info_df.loc[line_index, 'Эквайринг'] = acquiring
            info_df.loc[line_index, 'Все затраты'] = all_spending
            info_df.loc[line_index, 'На счет ИП'] = amount
            info_df.loc[line_index, 'Прибль'] = profit
            info_df.loc[line_index, 'Дата когда забрали заказ'] = operation_date


    return info_df


def create_orders_table(orders_status='', check_status=[]):
    orders_list = []
    end_year = datetime.now().year
    for year in range(2022, end_year+1):
        if year == 2022:
            day_from = datetime(year, 7, 31)
        else:
            day_from = datetime(year, 1, 1)

        day_to = datetime(year, 12, 31)

        orders_list += get_orders_list(day_from=day_from, day_to=day_to, orders_status=orders_status, check_status=check_status)

    order_dict_list = []
    for order in orders_list:
        order_id = order.get('order_id')
        offer_id = order.get('offer_id')
        sku = order.get('sku')
        name = order.get('name')
        quantity = order.get('quantity')
        shipment_date = order.get('shipment_date')

        order_dict_list.append({
            'Id заказа': order_id,
            'Артикуль': offer_id, 
            'SKU': sku,
            'Название': name,
            'Количество': quantity,
            'Дата отгрузки': shipment_date,
            'Затраты на товар': 0,
            'Затраты на упоковку': 0
        })

    orders_df = DataFrame(order_dict_list)

    return orders_df


def create_all_orders_table():
    orders_df = create_orders_table()
    return orders_df


def create_next_orders_table():
    orders_df = create_orders_table(orders_status='awaiting_packaging')
    date = orders_df.iloc[0]['Дата отгрузки']
    orders_df = orders_df[orders_df['Дата отгрузки'] == date]

    return orders_df
