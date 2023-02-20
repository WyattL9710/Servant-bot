import os
import discord
import constants
import random
import requests
import pytz
from bs4 import BeautifulSoup
from datetime import datetime, date, timedelta
from discord.ext import commands
import json
import asyncio
import time

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
  """Greets the user."""
  await ctx.send('Hello! How can I help you today?')

@bot.command(name='8ball')
async def eightball(ctx):
  """Tells your fortune."""
  await ctx.send(random.choice(constants.EIGHT_BALL))

@bot.command()
async def motivate(ctx):
  """Gives a motivational quote."""
  url = 'https://www.brainyquote.com/topics/motivational-quotes'
  response = requests.get(url)
  soup = BeautifulSoup(response.text, 'html.parser')
  quotes = soup.find_all('a', class_='b-qt')
  quote = random.choice(quotes).text
  await ctx.send(quote)

@bot.command()
async def roastme(ctx):
  """Roasts the user."""
  msg = random.choice(constants.ROAST_MSG)
  await ctx.send(msg)


@bot.command()
async def roll(ctx, message):
  """Rolls a dice."""
  try:
    num_sides = int(message)
  except:
    # Default to 6 sides if no valid number is provided
    num_sides = 6

  # Generate a random number between 1 and the number of sides
  roll = random.randint(1, num_sides)

  # Send a message with the roll result
  await ctx.send(f"You rolled a {roll}!")


@bot.command()
async def facts(ctx):
  """Gives a random fact."""
  msg = random.choice(constants.FACTS_MSG)
  await ctx.send(msg)

@bot.command()
async def sortinghat(ctx):
  """Sorts the user into a Harry Potter House."""
  houses = ['Gryffindor', 'Hufflepuff', 'Ravenclaw', 'Slytherin']
  house = random.choice(houses)
  user = ctx.author.mention
  await ctx.send(f'{user}, you have been sorted into {house}!')

@bot.command()
async def weather(ctx, location):
  """Gives weather details for a specific location."""
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
  """???"""
  emoji = "🍪" # The cookie emoji
  response = "Wow! You found the secret command! Here's a " + emoji
  await ctx.send(response)



with open("birthday_list.json", "r") as f:
    birthdays = json.load(f)

# Command to set a user's birthday
@bot.command()
async def set_birthday(ctx, date_string, username=None):
  """Sets the birthday of a user."""
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
  birthdays[str(user.id)] = date.strftime('%m/%d/%Y')
  
  # Save the updated birthday list to the file
  with open("birthday_list.json", "w") as f:
      json.dump(birthdays, f)
  
  # Send a confirmation message
  await ctx.send(f"{user.name}'s birthday has been set to {date_string}.")

  
# Command to get a user's age
@bot.command()
async def age(ctx, username=None):
  """Provides the age of a user."""
  # If username is None, use the username of the message author
  if username is None:
      user = ctx.author
  else:
      user = discord.utils.find(lambda u: u.name == username, ctx.guild.members)
      if user is None:
          await ctx.send(f"Could not find user with username {username}.")
          return

  user_id = str(user.id)
        
  # Check if the user has set their birthday
  if user_id not in birthdays.keys():
      await ctx.send("You haven't set your birthday yet!")
      return

  birthday = datetime.strptime(birthdays[user_id], '%m/%d/%Y')
  
  # Calculate the user's age
  now = datetime.now()
  age = now.year - birthday.year - ((now.month, now.day) < (birthday.month, birthday.day))
  
  # Send the user's age
  await ctx.send(f"{user.name} is {age} years old.")
  
# Command to get upcoming birthdays
@bot.command()
async def upcoming_birthdays(ctx):
  """Shows upcoming birthdays."""
  # Get the current date
  now = datetime.now()
  
  # Sort the birthdays by date
  sorted_birthdays = sorted(birthdays.items(), key=lambda x: x[1])

  if len(birthdays) == 0:
    await ctx.send("There are no upcoming birthdays.")
    return

  # Find the next upcoming birthday
  for user_id, date in sorted_birthdays:
      print(f'user: {user_id} date: {date}')
      date = datetime.strptime(date, '%m/%d/%Y')
      date = date.replace(year=now.year)
      user = ctx.guild.get_member(int(user_id))
      if user is None:
          continue
      if date.month >= now.month and date.day >= now.day:
          days_until_birthday = (date - now).days
          if days_until_birthday == 0:
              await ctx.send(f"Today is {user.name}'s birthday!")
          else:
              await ctx.send(f"{user.name}'s birthday is coming up on {date.strftime('%B %d')}. Only {days_until_birthday} days left!")

@bot.command()
async def users(ctx):
  """Lists all users that are a member of the server."""
  users = [member.name for member in ctx.guild.members]
  await ctx.send("Usernames: " + ", ".join(users))

@bot.command(name='rps')
async def rock_paper_scissors(ctx):
  """Servant bot will play rock, paper, and scissors with you."""
  choices = ['rock', 'paper', 'scissors']
  bot_choice = random.choice(choices)
  await ctx.send(f"I choose {bot_choice}!")


@bot.command(name='timesince')
async def time_since(ctx, date: str):
  """Shows the amount of time it has been since a specific date."""
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
  """Shows how much time there is until a specfic date."""
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


@bot.command()
async def joke(ctx):
    """Tells a random joke."""
    url = "https://official-joke-api.appspot.com/random_joke"
    response = requests.get(url)
    if response.status_code == 200:
        data = json.loads(response.text)
        await ctx.send(f"{data['setup']} {data['punchline']}")
    else:
        await ctx.send("Oops, something went wrong. Please try again later.")


@bot.command(name='i_want_it_that_way')
async def want_it_that_way(ctx):
    """Bot answers: Tell me whyyyy"""
    await ctx.send("Tell me whyyyy")

@bot.command(name='aint_nothin_but_a_heartache')
async def nothin_but_a_heartache(ctx):
    """Bot answers: Tell me whyyyy"""
    await ctx.send("Tell me whyyyy")

@bot.command(name='nothin_but_a_mistake')
async def nothin_but_a_mistake(ctx):
    """Bot answers: 'Cause I want it that wayyyyy"""
    await ctx.send("'Cause I want it that wayyyyy")


REMINDERS_FILE = 'reminders.json'
reminders = {}

def save_reminders():
    with open(REMINDERS_FILE, 'w') as f:
        json.dump(reminders, f)

def load_reminders():
    global reminders
    try:
        with open(REMINDERS_FILE, 'r') as f:
            reminders = json.load(f)
    except FileNotFoundError:
        pass

@bot.event
async def on_ready():
    load_reminders()

@bot.command()
async def remindme(ctx, time, *, message):
    """Set a reminder in the format of `!remindme <time> <message>`.

    Example: !remindme 1h30m Do laundry
    """
    author = ctx.message.author
    channel = ctx.message.channel

    seconds = 0
    time_list = time.split()
    for t in time_list:
        if t.endswith('s'):
            seconds += int(t[:-1])
        elif t.endswith('m'):
            seconds += int(t[:-1]) * 60
        elif t.endswith('h'):
            seconds += int(t[:-1]) * 60 * 60
        elif t.endswith('d'):
            seconds += int(t[:-1]) * 60 * 60 * 24

    await channel.send(f"{author.mention}, I will remind you in {time} to '{message}'")
    expiration_time = time.time() + seconds
    reminders[str(author.id)] = {'message': message, 'expiration_time': expiration_time}
    save_reminders()

    while time.time() < expiration_time:
        remaining_time = int(expiration_time - time.time())
        await asyncio.sleep(10) # update every 10 seconds
        await channel.send(f"{author.mention}, {remaining_time} seconds left until the reminder expires")

    await channel.send(f"{author.mention}, you asked me to remind you to '{message}' {time} ago")
    del reminders[str(author.id)]
    save_reminders()

@bot.command()
async def timeleft(ctx):
    """Check how much time is left until your next reminder."""
    author = ctx.message.author
    channel = ctx.message.channel

    if str(author.id) in reminders:
        reminder = reminders[str(author.id)]
        expiration_time = reminder['expiration_time']
        remaining_time = int(expiration_time - time.time())
        await channel.send(f"{author.mention}, you have {remaining_time} seconds left until your reminder expires: '{reminder['message']}'")
    else:
        await channel.send(f"{author.mention}, you do not have any active reminders.")






bot.run (os.environ['DISCORD_TOKEN'])