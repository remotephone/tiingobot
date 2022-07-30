import requests
import re
import json

def megamillions():
    r = requests.get(' https://www.megamillions.com/cmspages/utilservice.asmx/GetLatestDrawData')

    results = re.findall(r'{.*}', r.text)

    for result in results:
        winning_numbers = ""
        drawing = json.loads(result)
        results = drawing['Drawing']
        for k,v in results.items():
            if k == "PlayDate":
                winning_numbers = f"Winning Numbers for {v.split('T')[0]}:\n".format(v)
            if 'N' in k:
                winning_numbers += str(v) + " - "
            if k == "MBall":
                winning_numbers += f"Megaball - {v}".format(v)
        print(winning_numbers)