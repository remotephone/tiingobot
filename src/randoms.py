import random

def get_tax_refund(ssn):
    try:
        minimum = -int(ssn) * 100
        maximum = int(ssn) * 100
        random.seed()
        refund = random.randint(minimum, maximum)
        print(refund)
        if refund > 0:
            return f'Your refund is ${str(abs(refund))}'
        else:
            return f'You owe ${str(abs(refund))}'
    except ValueError as e:
        return 'You owe one million dollars'