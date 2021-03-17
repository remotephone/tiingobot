# Tiingobot

This uses Tiingo's free API to to query stock prices using discord commands. You will need to set up a discord bot to get an authentication token. The guide [here](https://realpython.com/how-to-make-a-discord-bot-python/) had most of what I needed to figure this out. 

`!stonks gme` will return prices for the Gamestop ticker, for example. There is some validation of the tickers submitted for queries, but it's probably not infallible.  If someone sends a ticker that doesn't match the regex, it will return GME by default. If someone returns a ticker that doesn't exist or there is some other kind of error, a Result not found value will return.


## Permissions

You'll need to create a discord bot user with permissions to send messages and use slash commands. 


## Limits

The free Tiingo API limits you to 500 calls per hour. The bot by default limits to 1 request per user every 10 seconds. Edit the limits if you need to. 


## Usage

Edit the `docker-compose_example.yml` file to include your tokens, pin a version if you want, and then deploy. I use a docker swarm. 

`docker stack deploy --with-registry-auth -c docker-compose.yml tiingobot`

To deploy something from the github container registry, you may have to authenticate. I followed the instructions [here](https://docs.github.com/en/packages/guides/migrating-to-github-container-registry-for-docker-images#authenticating-with-the-container-registry).

