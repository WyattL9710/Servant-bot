import os
import discord
import constants
import random
import requests
import pytz
from bs4 import BeautifulSoup
from datetime import datetime, date, timedelta
from discord.ext import commands

intents = discord.Intents.all()
client = discord.Client(intents=intents)
bot = commands.Bot(command_prefix='/', intents=intents)
 

@client.event
async def on_ready():
  print('Logged in as {0.user}'.format(client))

def send_webhook(content):
    data = {"content": content}
    headers = {"Content-Type": "application/json"}
    response = requests.post('https://discord.com/api/webhooks/1076382263853465620/oBH7j-eQ17u1utoIuoW7wrg0NPkLwcbQwE2P17pPkMGXR-EiBLhK9mbBGx_CL6BRWQAm', json=data, headers=headers)
    response.raise_for_status()

@client.event
async def on_message(message):
  if message.author == client.user:
    return

@bot.command()
async def hello(ctx):
  await ctx.send('Hello! How can I help you today?')

@bot.command(name='8ball')
async def eightball(ctx):
  await ctx.send(random.choice(constants.EIGHT_BALL))

@bot.command()
async def motivationalquote(ctx):
  url = 'https://www.brainyquote.com/topics/motivational-quotes'
  response = requests.get(url)
  soup = BeautifulSoup(response.text, 'html.parser')
  quotes = soup.find_all('a', class_='b-qt')
  quote = random.choice(quotes).text
  await ctx.send(quote)

@bot.command()
async def roastme(ctx):
  msg = random.choice(constants.ROAST_MSG)
  await ctx.send(msg)


@bot.command()
async def roll(ctx, message):
  try:
    num_sides = int(message.content.split(' ')[1])
  except:
    # Default to 6 sides if no valid number is provided
    num_sides = 6

  # Generate a random number between 1 and the number of sides
  roll = random.randint(1, num_sides)

  # Send a message with the roll result
  await ctx.send(f"You rolled a {roll}!")


@bot.command()
async def facts(ctx):
  msg = random.choice(constants.FACTS_MSG)
  await ctx.send(msg)

@bot.command()
async def sortinghat(ctx):
  houses = ['Gryffindor', 'Hufflepuff', 'Ravenclaw', 'Slytherin']
  house = random.choice(houses)
  user = ctx.author.mention
  await ctx.send(f'{user}, you have been sorted into {house}!')

@bot.command()
async def weather(ctx, message):
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
  await ctx.send(message_text)

@bot.command()
async def secret(ctx):
  emoji = "🍪" # The cookie emoji
  response = "Wow! You found the secret command! Here's a " + emoji
  await ctx.send(response)



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

@bot.command(name='rps')
async def rock_paper_scissors(ctx):
  choices = ['rock', 'paper', 'scissors']
  bot_choice = random.choice(choices)
  await ctx.send(f"I choose {bot_choice}!")


@bot.command(name='timesince')
async def time_since(ctx, date: str):
    try:
        target_date = datetime.strptime(date, '%m/%d/%Y')
        today = datetime.now()

        # calculate the difference in years
        years = today.year - target_date.year
        if (today.month, today.day) < (target_date.month, target_date.day):
            years -= 1

        # calculate the difference in months and remaining days
        total_months = (today.year - target_date.year) * 12 + today.month - target_date.month
        months = total_months % 12

        if today.day < target_date.day:
            days_in_last_month = (today.replace(day=1) - timedelta(days=1)).day
            days = days_in_last_month - target_date.day + today.day
            if months == 0:
                years -= 1
                months = 12
            else:
                months -= 1
        else:
            days = today.day - target_date.day

        # construct the output string
        time_str = f"{years} years, {months} months, and {days} days"
        await ctx.send(f"It has been {time_str} since {target_date.strftime('%B %d, %Y')}")
    except ValueError:
        await ctx.send("Invalid date format. Please enter a valid date in MM/DD/YYYY format.")



@bot.command(name='timeuntil')
async def time_until(ctx, date: str):
    try:
        target_date = datetime.strptime(date, '%m/%d/%Y')
        today = datetime.now()

        # calculate the difference in years
        years = target_date.year - today.year
        if (today.month, today.day) > (target_date.month, target_date.day):
            years -= 1

        # calculate the difference in months and remaining days
        total_months = (target_date.year - today.year) * 12 + target_date.month - today.month
        months = total_months % 12

        if today.day > target_date.day:
            days_in_last_month = (today.replace(day=1) - timedelta(days=1)).day
            days = days_in_last_month - today.day + target_date.day
            if months == 0:
                years -= 1
                months = 12
            else:
                months -= 1
        else:
            days = target_date.day - today.day

        # construct the output string
        time_str = f"{years} years, {months} months, and {days} days"
        await ctx.send(f"There are {time_str} until {target_date.strftime('%B %d, %Y')}")
    except ValueError:
        await ctx.send("Invalid date format. Please enter a valid date in MM/DD/YYYY format.")


bot.run (os.environ['DISCORD_TOKEN'])