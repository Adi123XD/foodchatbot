import mysql.connector
cnn = mysql.connector.connect(
    host='localhost',
    user='root',
    password='MYSQL',
    database='pandeyji_eatery'
)

def get_order_status (order_id :int):
    print("in here")
    cursor= cnn.cursor()
    query=("select status from order_tracking where order_id = %s")
    cursor.execute(query,(order_id,));
    status = cursor.fetchone()
    cursor.close()
    if status:
        return status[0]
    else :
        return "Not found"
def get_order_id():
    cursor = cnn.cursor()
    query=("select max(order_id) from orders")
    cursor.execute(query)
    order_id = cursor.fetchone()[0]
    if order_id:
        return order_id+1
    else:
        return 1
def insert_order(food_item,quantity,order_id):
    try:
        cursor = cnn.cursor()
        cursor.callproc('insert_order_item',(food_item,quantity,order_id))
        cnn.commit()
        cursor.close()
        print("Order placed succcessfully")
        return 1
    except mysql.connector.Error as err:
        print(f'Error inserting order item {err}')
        #Rollback the changes
        cnn.rollback()
        return -1
    except Exception as e:
        print(f'An error occurred {e}')
        return -1
    
def insert_order_tracking(order_id:int , status):
    cursor = cnn.cursor()
    query = "insert into order_tracking (order_id ,status) values (%s,%s)"
    cursor.execute(query , (order_id,status,))
    cnn.commit()
    cursor.close()
def save_to_db(orders :dict):
    order_id = get_order_id()
    for food_item , quantity in orders.items():
        rcode=insert_order(food_item,quantity,order_id)
        if rcode ==-1:
            return -1
    insert_order_tracking(order_id,"in_progress")
    return order_id
def get_total(order_id):
    cursor=cnn.cursor()
    query=f'Select get_total_order_price ({order_id})'
    cursor.execute(query)
    result = cursor.fetchone()[0]
    return result
    pass


if __name__ =='__main__':
    print(get_order_status(42))

