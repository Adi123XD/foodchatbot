import re
def match_session_id(session_str : str):
    match = re.search(r"sessions/(.*?)/contexts/",session_str)
    if match:
        extracted_string = match.group(1)
        return extracted_string
    else:
        return ""
def food_dict_to_str(food_dict :dict):
    return " and ".join([f'{int(value)} {key}' for key , value in food_dict.items()])
    
if __name__=="__main__":
    print(match_session_id("projects/adi-plmr/agent/sessions/7b411484-bdbb-c0dc-c720-f2ff561ad195/contexts/ongoing_order"))