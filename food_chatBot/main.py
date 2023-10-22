from fastapi import FastAPI
from fastapi import Request
from fastapi.responses import JSONResponse
import db_helper
import generic

app = FastAPI()
inprogress_orders={}


@app.post("/")
async def handle_request(request : Request):
    body = await request.body()
    print("Request Body:", body.decode())
    # payload = await request.json()

    # Attempt to parse JSON
    try:
        payload = await request.json()
        # Your code to handle the JSON payload goes here
        # return {"message": "JSON received successfully"}
    except Exception as e:
        print("JSON Parsing Error:", e)
        return {"error": "Invalid JSON format"}
    #Extract the necessary information from the payload 
    # based on the structure of the webhook request coming from dialogueflow
    intent = payload['queryResult']['intent']['displayName']
    parameters = payload['queryResult']['parameters']
    output_context = payload['queryResult']['outputContexts']
    session_id = generic.match_session_id(output_context[0]["name"])
    intent_handler_dict ={
        'order.add - context: ongoing-order': add_order,
        'order.remove - context: ongoing-order':remove_order,
        'order.complete - context: ongoing-order':place_order,
        'track.order - context: ongoing-tracking':track_order,

    }
    return intent_handler_dict[intent](parameters,session_id)
def add_order(parameters: dict,session_id:str):
    food_items = parameters['food-items']
    quantities = parameters['number']
    if (len(food_items)!=len(quantities)):
        fulfillment_text =f'Sorry i can not understand . Can you specify food item and quanitity please!'
    else:
        new_food_dict = dict(zip(food_items,quantities))
        if session_id in inprogress_orders:
            curr_food_dict = inprogress_orders[session_id]
            curr_food_dict.update(new_food_dict)
            inprogress_orders[session_id]=curr_food_dict
        else:
            inprogress_orders[session_id]=new_food_dict
        fulfillment_text=f'So far you have {generic.food_dict_to_str(inprogress_orders[session_id])}. Do you need anything else?'
    return JSONResponse(content={
        'fulfillmentText':fulfillment_text
    })
    
def remove_order(parameters: dict,session_id:str):
    if session_id not in inprogress_orders:
        return JSONResponse(content=
                            {
                                'fulfillmentText':'Sorry i cannot find your order. Please place your order again!'
                            })
    else:
        fulfillmentText=''
        food_items = parameters['food-items']
        current_orders = inprogress_orders[session_id]
        removed_items = []
        items_not_found=[]
        for item in food_items:
            if item not in current_orders:
                items_not_found.append(item)
                pass
            else:
                removed_items.append(item)
                del current_orders[item]
        if (len(removed_items)>0):
            fulfillmentText=f' Removed {" , ".join(removed_items)} from your order'
        if (len(items_not_found)>0):
            fulfillmentText+=f' Your current order does not have {" , ".join(items_not_found)}'
        if (len(current_orders.keys())==0):
            fulfillmentText+=" Your order is empty!"
        else:
            order_str = generic.food_dict_to_str(current_orders)
            fulfillmentText+=f' Here is what is left in your order {order_str}'
        return JSONResponse(content={
            'fulfillmentText':fulfillmentText
        })
def place_order(parameters :dict,session_id:str):
    if session_id not in inprogress_orders:
        fulfillmentText ='I am sorry i am having trouble placing your order.Can you please order again!'
    else:
        order=inprogress_orders[session_id]
        order_id=db_helper.save_to_db(order)
        if order_id ==-1:
            fulfillmentText=f'Sorry i could not place your order due to server error. Please place your order again'
        else:
            order_total=db_helper.get_total(order_id)
            fulfillmentText =f'Awesome ! your order is placed.' \
                f'Your order id is {order_id} '\
                f'and order total is Rs {order_total} which you can pay at the time of delivery'
            del inprogress_orders[session_id]
    return JSONResponse(content={
        'fulfillmentText':fulfillmentText
        })
def track_order(parameters: dict,session_id:str):
    order_id = parameters['number']
    status= db_helper.get_order_status(order_id)
    if status:
        fulfillment_text = f' Your order with order_id {order_id} is {status}'
    else :
        fulfillment_text=f'No order found with order_id {order_id}'
    return JSONResponse(content={
        'fulfillmentText': fulfillment_text
        })

