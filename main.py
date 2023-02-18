import os
import discord
import constants
import random
import requests
import pytz
from googletrans import Translator
from bs4 import BeautifulSoup
from datetime import datetime, date, timedelta
from discord.ext import commands
from datetime import datetime

intents = discord.Intents.all()
client = discord.Client(intents=intents)
bot = commands.Bot(command_prefix='/', intents=intents)


@client.event
async def on_ready():
  print('Logged in as {0.user}'.format(client))


@client.event
async def on_message(message):
  if message.author == client.user:
    return

  if message.content.startswith('/hello'):
    await message.channel.send('Hello! How can I help you today?')
    return

  if message.content.startswith('/8ball'):
    responses = [
      'It is certain.', 'I predict it is so.', 'Without a doubt.',
      'Yes, definitely.', 'You may rely on it.', 'As I see it, yes.',
      'Most likely.', 'Outlook good.', 'Yes.', 'Signs point to yes.',
      'Reply hazy, try again.', 'Ask again later.', 'Better not tell you now.',
      'Cannot predict now.', 'Concentrate and ask again.',
      "Don't count on it.", 'Outlook not so good.', 'My sources say no.',
      'Very doubtful.'
    ]
    await message.channel.send(random.choice(responses))
    return

  if message.content.startswith('/motivationalquote'):
    url = 'https://www.brainyquote.com/topics/motivational-quotes'
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    quotes = soup.find_all('a', class_='b-qt')
    quote = random.choice(quotes).text
    await message.channel.send(quote)
    return

  if message.content.startswith('/roastme'):
    msg = random.choice(constants.ROAST_MSG)
    await message.channel.send(msg)
    return

  if message.content.startswith('/roll'):
    # Parse the number of dice sides from the command message
    try:
      num_sides = int(message.content.split(' ')[1])
    except:
      # Default to 6 sides if no valid number is provided
      num_sides = 6

    # Generate a random number between 1 and the number of sides
    roll = random.randint(1, num_sides)

    # Send a message with the roll result
    await message.channel.send(f"You rolled a {roll}!")
    return

  if message.content.startswith('/facts'):
    msg = random.choice(constants.FACTS_MSG)
    await message.channel.send(msg)
    return

  if message.content.startswith('/sortinghat'):
    houses = ['Gryffindor', 'Hufflepuff', 'Ravenclaw', 'Slytherin']
    house = random.choice(houses)
    user = message.author.mention
    await message.channel.send(f'{user}, you have been sorted into {house}!')
    return

  if message.content.startswith('/weather'):
    location = message.content[9:]  # Extract location from message
    api_key = os.environ[
      'OPEN_WEATHER_MAP_API_KEY']  # Replace with your OpenWeatherMap API key

    # Construct the API URL with the specified location and API key
    url = f'http://api.openweathermap.org/data/2.5/weather?q={location}&appid={api_key}&units=imperial'

    # Make the API request and parse the response
    response = requests.get(url).json()

    if 'main' in response:
      # Extract the temperature and weather description from the response
      print(f'Response: {response}')
      temperature = response['main']['temp']
      feels_like = response['main']['feels_like']
      temp_min = response['main']['temp_min']
      temp_max = response['main']['temp_max']
      humidity = response['main']['humidity']
      wind_speed = response['wind']['speed']
      description = response['weather'][0]['description']

      # Format and send the weather information as a message
      message_text = f'The current temperature in {location} is {temperature:.1f}°F with {description}s. However, it currently feels like {feels_like}°F. The high today will be {temp_max}°F, and the low will be {temp_min}°F. The current humidity is {humidity}%. The wind speed right now is {wind_speed} mph.'
    else:
      # Handle the case where the API response is empty or does not have the expected keys
      message_text = 'Sorry, I could not find the weather for that location.'

    # Send the message to the Discord channel
    await message.channel.send(message_text)
    return

  if message.content == "/secret":
        emoji = "🍪" # The cookie emoji
        response = "Wow! You found the secret command! Here's a " + emoji
        await message.channel.send(response)
        return
    
  if message.content.startswith('/'):
    await message.channel.send("Sorry, I dont understand. Try again.")






# A dictionary to store users' birthdays
birthdays = {}

# Command to set a user's birthday
@bot.command()
async def set_birthday(ctx, date_string, username=None):
    # Parse the date string
    date = datetime.strptime(date_string, '%m/%d/%Y')
    
    # If username is None, use the username of the message author
    if username is None:
        user = ctx.author
    else:
        user = discord.utils.find(lambda u: u.name == username, ctx.guild.members)
        if user is None:
            await ctx.send(f"Could not find user with username {username}.")
            return
    
    # Store the user's birthday
    birthdays[user.id] = date
    
    # Send a confirmation message
    await ctx.send(f"{user.name}'s birthday has been set to {date_string}.")

# Command to get a user's age
@bot.command()
async def age(ctx, username=None):
    # If username is None, use the username of the message author
    if username is None:
        user = ctx.author
    else:
        user = discord.utils.find(lambda u: u.name == username, ctx.guild.members)
        if user is None:
            await ctx.send(f"Could not find user with username {username}.")
            return
    
    # Check if the user has set their birthday
    if user.id not in birthdays:
        await ctx.send("You haven't set your birthday yet!")
        return
    
    # Calculate the user's age
    now = datetime.now()
    age = now.year - birthdays[user.id].year - ((now.month, now.day) < (birthdays[user.id].month, birthdays[user.id].day))
    
    # Send the user's age
    await ctx.send(f"{user.name} is {age} years old.")
    
# Command to get upcoming birthdays
@bot.command()
async def upcoming(ctx):
    # Get the current date
    now = datetime.now()
    
    # Sort the birthdays by date
    sorted_birthdays = sorted(birthdays.items(), key=lambda x: x[1])
    
    # Find the next upcoming birthday
    for user_id, date in sorted_birthdays:
        user = ctx.guild.get_member(user_id)
        if user is None:
            continue
        if date.month >= now.month and date.day >= now.day:
            days_until_birthday = (date - now).days
            if days_until_birthday == 0:
                await ctx.send(f"Today is {user.name}'s birthday!")
            else:
                await ctx.send(f"{user.name}'s birthday is coming up on {date.strftime('%B %d')}. Only {days_until_birthday} days left!")
            return
    
    # If there are no upcoming birthdays, send a message saying so
    await ctx.send("There are no upcoming birthdays.")

@bot.command()
async def list_users(ctx):
    users = [member.name for member in ctx.guild.members]
    await ctx.send("Usernames: " + ", ".join(users))



bot.run (os.environ['DISCORD_TOKEN'])