import boto3


def get_stocks_for_user(user: str) -> list:
    client = boto3.client('sdb')
    response = client.get_attributes(
        DomainName='wiggles',
        ItemName=user,
    )
    
    return response.get('Items', [])

def get_stocks_for_user(user: str) -> list:
    client = boto3.client('sdb')
    response = client.get_attributes(
        DomainName='wiggles',
        ItemName=user,
    )
    print(response)


def put_stocks_for_user(user: str, stocks: str) -> list:
    client = boto3.client('sdb')
    # gets = client.get_attributes(
    #     DomainName='wiggles',
    #     ItemName=user,
    # )
    # current_stocks = gets.get('Attributes', [])
    # if current_stocks is not []:


    response = client.put_attributes(
        DomainName='wiggles',
        ItemName=user,
        Attributes=[
            {
                'Name': 'stocks',
                'Value': stocks,
                'Replace': True
            },
        ]
    )
    print(response)
put_stocks_for_user('remotephone2', 'test,test,test')

get_stocks_for_user('remotephone2')