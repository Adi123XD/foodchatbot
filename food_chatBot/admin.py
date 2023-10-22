import mysql.connector
cnn = mysql.connector.connect(
    host='localhost',
    user='root',
    password='MYSQL',
    database='pandeyji_eatery'
)

def change_order_status():
    order_id=int(input("enter the order_id for which you want to change the status\n"))
    status=input("Enter the new status for the order\n")
    cursor= cnn.cursor()
    query=("update order_tracking set status =%s where order_id =%s")
    cursor.execute(query ,(status,order_id,))
    cnn.commit()
    cursor.close()
def see_records():
    table_name = input("enter the table whose content you want to see\n")
    cursor=cnn.cursor()
    query=(f"select * from {table_name}")
    cursor.execute(query)
    record=cursor.fetchall()
    for i in record:
        print(i)
if __name__ =='__main__':
    ch =int(input("Enter 1 to view the contents of your table and 2 to change the order_status\n Enter your choice"))
    case_dict={
        1:see_records,
        2:change_order_status
    }
    if ch in case_dict:
        case_dict[ch]()
    else:
        print("wrong choice\n")
