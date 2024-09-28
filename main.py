import asyncio
import json
import logging
import os
import random

import discord
from discord.ext import commands

# Set up logging
logging.basicConfig(level=logging.INFO)

# Initialize the bot with intents
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# Vocabulary and flashcard files
vocab_file = 'vocab.json'
flashcard_file = 'flashcards.json'

# Initialize vocabularies and flashcards
vocab_categories = {
    'chinese': {},
    'greek': {},
    'latin': {},
    'sanskrit': {},
    'norse': {}  # Added Norse category
}

flashcards = {}

# Leaderboard storage
leaderboard = {}


# Load vocabularies and flashcards from JSON files
def load_data():
    global vocab_categories, flashcards
    if os.path.exists(vocab_file):
        with open(vocab_file, 'r', encoding='utf-8') as f:
            vocab_data = json.load(f)
            vocab_categories = {
                lang: vocab_data.get(lang, {})
                for lang in vocab_categories
            }
        logging.info("Vocabularies loaded successfully.")
    else:
        logging.warning(
            "Vocabulary file not found. Starting with empty vocabularies.")

    if os.path.exists(flashcard_file):
        with open(flashcard_file, 'r', encoding='utf-8') as f:
            flashcards = json.load(f)
        logging.info("Flashcards loaded successfully.")
    else:
        logging.warning(
            "Flashcard file not found. Starting with empty flashcards.")


# Save vocabularies and flashcards to JSON files
def save_data():
    with open(vocab_file, 'w', encoding='utf-8') as f:
        json.dump(vocab_categories, f, ensure_ascii=False, indent=4)
    logging.info("Vocabularies saved successfully.")

    with open(flashcard_file, 'w', encoding='utf-8') as f:
        json.dump(flashcards, f, ensure_ascii=False, indent=4)
    logging.info("Flashcards saved successfully.")


# Event when the bot is ready
@bot.event
async def on_ready():
    logging.info(f'{bot.user} has connected to Discord!')
    load_data()


# Define available colors
available_colors = {
    "silver": discord.Color.from_rgb(192, 192, 192),  # Silver
    "gold": discord.Color.from_rgb(255, 215, 0),  # Gold
    "purple": discord.Color.purple(),  # Purple
    "yellow": discord.Color.from_rgb(255, 255, 0),  # Yellow
    "green": discord.Color.green(),  # Green
    "red": discord.Color.red(),  # Red
    "azure": discord.Color.from_rgb(0, 127, 255),  # Azure Blue
    "orange": discord.Color.from_rgb(255, 165, 0)  # Orange
}


# Command to greet users
@bot.command(name='hi')  # Shortened command
async def hello(ctx):
    await ctx.send(
        "Hello! 👋 I'm here to help you learn! Type `!cmds` to see what I can do!"
    )


# Command to list available commands
@bot.command(name='cmds')  # Shortened command
async def commands_list(ctx):
    help_message = """
**Available Commands:**

**General Commands:**
- `!hi`: Greet the bot.
- `!cmds`: Lists all available commands.
- `!langs`: Lists supported languages.

**Interactive Learning:**
- `!grammar [lang]`: Explains grammar elements for a specified language.
- `!flash [difficulty]`: Starts a flashcard game.
- `!guess [lang]`: Starts a word guess game.
- `!write [lang]`: Write a word that starts with a specified letter.
- `!addch [char] [translation]`: Adds a word to Chinese vocabulary.
- `!addgr [word] [translation]`: Adds a word to Greek vocabulary.
- `!addla [word] [translation]`: Adds a word to Latin vocabulary.
- `!addsans [word] [translation]`: Adds a word to Sanskrit vocabulary.
- `!addnorse [word] [translation]`: Adds a word to Norse vocabulary.
- `!rand [lang]`: Provides a random word in the specified language.

**Color Management:**
- `!setcolor [color]`: Set your color.
- `!resetcolor`: Reset your color.
- `!colors`: List available colors.

**Learning Tools:**
- `!written`: Show how alphabets and characters look in all languages.
- `!challenge`: Start a challenge for a fun competition!
- `!lead`: View the leaderboard.

**Calculator:**
- `!calc [expression]`: Perform a calculation.

**Flashcard Management:**
- `!flashcardcreate [word] [translation]`: Create a flashcard.
- `!flashcardgenerate`: Generate a random flashcard.
- `!flashcardlist`: List all your flashcards.

**Hangman Game:**
- `!hangman [lang]`: Start a Hangman game with a word from the specified language.
    """
    await ctx.send(help_message)


# Command to list supported languages
@bot.command(name='langs')
async def list_languages(ctx):
    languages = ", ".join(
        [lang.capitalize() for lang in vocab_categories])
    await ctx.send(f"**Supported Languages:** {languages}")


# Command to explain grammar elements
@bot.command(name='grammar')
async def explain_grammar(ctx, lang: str):
    grammar_info = {
        'greek':
        "Greek grammar includes cases, genders, and conjugations. For example, nouns have nominative, accusative, genitive, and vocative cases.",
        'latin':
        "Latin grammar is known for its extensive use of cases, verb conjugations, and agreement between subjects and verbs.",
        'chinese':
        "Chinese grammar is analytic, relying on word order and particles rather than inflections to convey meaning.",
        'sanskrit':
        "Sanskrit grammar is highly inflected, with eight cases, three genders, and extensive verb conjugations.",
        'norse':
        "Norse grammar features strong and weak declensions, three genders, and a system of verb conjugations."
    }

    lang = lang.lower()
    info = grammar_info.get(lang)
    if info:
        await ctx.send(f"**{lang.capitalize()} Grammar:**\n{info}")
    else:
        await ctx.send(
            f"No grammar information available for '{lang}'. Please choose from Chinese, Greek, Latin, Sanskrit, or Norse."
        )


# Command to start a flashcard game
@bot.command(name='flash')
async def flashcard_game(ctx, difficulty: str = "easy"):
    difficulties = ['easy', 'medium', 'hard']
    difficulty = difficulty.lower()

    if difficulty not in difficulties:
        await ctx.send(
            "Invalid difficulty level. Choose from easy, medium, or hard.")
        return

    # Select a language based on difficulty or randomly
    language = random.choice(list(vocab_categories.keys()))
    vocab = vocab_categories[language]

    if not vocab:
        await ctx.send(f"No vocabulary available for {language}.")
        return

    word, translation = random.choice(list(vocab.items()))
    await ctx.send(
        f"Flashcard ({language.capitalize()}, {difficulty.capitalize()}): **{word}** - What is the meaning?"
    )

    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel

    try:
        response = await bot.wait_for('message', check=check, timeout=30.0)
        if response.content.lower() == translation.lower():
            await ctx.send("Correct! 🎉")
            # Update leaderboard
            if ctx.author.id not in leaderboard:
                leaderboard[ctx.author.id] = 0
            leaderboard[ctx.author.id] += 1
        else:
            await ctx.send(f"Wrong! The correct answer was: **{translation}**")
    except asyncio.TimeoutError:
        await ctx.send(f"Time's up! The correct answer was: **{translation}**")


# Command to guess a word
@bot.command(name='guess')
async def guess_word(ctx, lang: str):
    lang = lang.lower()
    if lang not in vocab_categories:
        await ctx.send(
            "Language not supported. Choose from Chinese, Greek, Latin, Sanskrit, or Norse."
        )
        return

    vocab = vocab_categories[lang]
    if not vocab:
        await ctx.send(f"No vocabulary available for {lang}.")
        return

    word, translation = random.choice(list(vocab.items()))
    await ctx.send(
        f"Guess the word in **{lang.capitalize()}**: **{translation}**")

    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel

    try:
        response = await bot.wait_for('message', check=check, timeout=30.0)
        if response.content.lower() == word.lower():
            await ctx.send("Correct! 🎉")
            # Update leaderboard
            if ctx.author.id not in leaderboard:
                leaderboard[ctx.author.id] = 0
            leaderboard[ctx.author.id] += 1
        else:
            await ctx.send(f"Wrong! The correct word was: **{word}**")
    except asyncio.TimeoutError:
        await ctx.send(f"Time's up! The correct word was: **{word}**")


# Command to write a word starting with a specified letter
@bot.command(name='write')
async def write_word(ctx, lang: str, letter: str):
    lang = lang.lower()
    letter = letter.lower()
    if lang not in vocab_categories:
        await ctx.send(
            "Language not supported. Choose from Chinese, Greek, Latin, Sanskrit, or Norse."
        )
        return

    vocab = vocab_categories[lang]
    words_starting_with = [
        word for word in vocab.keys() if word.lower().startswith(letter)
    ]

    if not words_starting_with:
        await ctx.send(
            f"No words found in {lang.capitalize()} starting with '{letter}'.")
        return

    word = random.choice(words_starting_with)
    await ctx.send(f"Write the meaning of the word: **{word}**")

    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel

    try:
        response = await bot.wait_for('message', check=check, timeout=30.0)
        if response.content.lower() == vocab[word].lower():
            await ctx.send("Correct! 🎉")
            # Update leaderboard
            if ctx.author.id not in leaderboard:
                leaderboard[ctx.author.id] = 0
            leaderboard[ctx.author.id] += 1
        else:
            await ctx.send(f"Wrong! The correct meaning was: **{vocab[word]}**"
                           )
    except asyncio.TimeoutError:
        await ctx.send(f"Time's up! The correct meaning was: **{vocab[word]}**"
                       )


# Command to add a word to Chinese vocabulary
@bot.command(name='addch')  # Shortened command
async def add_word_chinese(ctx, word: str, translation: str):
    vocab_categories['chinese'][word] = translation
    save_data()
    await ctx.send(
        f"Added to Chinese vocabulary: **{word}** - **{translation}**")


# Command to add a word to Greek vocabulary
@bot.command(name='addgr')  # Shortened command
async def add_word_greek(ctx, word: str, translation: str):
    vocab_categories['greek'][word] = translation
    save_data()
    await ctx.send(f"Added to Greek vocabulary: **{word}** - **{translation}**"
                   )


# Command to add a word to Latin vocabulary
@bot.command(name='addla')  # Shortened command
async def add_word_latin(ctx, word: str, translation: str):
    vocab_categories['latin'][word] = translation
    save_data()
    await ctx.send(f"Added to Latin vocabulary: **{word}** - **{translation}**"
                   )


# Command to add a word to Sanskrit vocabulary
@bot.command(name='addsans')  # Shortened command
async def add_word_sanskrit(ctx, word: str, translation: str):
    vocab_categories['sanskrit'][word] = translation
    save_data()
    await ctx.send(
        f"Added to Sanskrit vocabulary: **{word}** - **{translation}**")


# Command to add a word to Norse vocabulary
@bot.command(name='addnorse')  # New command for Norse
async def add_word_norse(ctx, word: str, translation: str):
    vocab_categories['norse'][word] = translation
    save_data()
    await ctx.send(f"Added to Norse vocabulary: **{word}** - **{translation}**"
                   )


# Command to provide a random word in the specified language
@bot.command(name='rand')  # Shortened command
async def random_word(ctx, lang: str, category: str = None):
    lang = lang.lower()
    if lang not in vocab_categories:
        await ctx.send(
            "Language not supported. Choose from Chinese, Greek, Latin, Sanskrit, or Norse."
        )
        return

    vocab = vocab_categories[lang]
    if category:
        # If categories are implemented within vocab, filter by category
        # For simplicity, assuming vocab is a flat dictionary
        pass  # Placeholder for category filtering
    if not vocab:
        await ctx.send(f"No vocabulary available for {lang.capitalize()}.")
        return

    word, translation = random.choice(list(vocab.items()))
    await ctx.send(
        f"Random word in **{lang.capitalize()}**: **{word}** - **{translation}**"
    )


# Command to set a user's color
@bot.command(name='setcolor')
async def set_color(ctx, color_name: str):
    color_name = color_name.lower()
    if color_name in available_colors:
        role = discord.utils.get(ctx.guild.roles, name=color_name.capitalize())
        if not role:
            # Create a new role if it doesn't exist
            try:
                role = await ctx.guild.create_role(
                    name=color_name.capitalize(),
                    color=available_colors[color_name])
            except discord.Forbidden:
                await ctx.send("I don't have permission to create roles.")
                return
        # Remove existing color roles
        color_roles = [
            discord.utils.get(ctx.guild.roles, name=clr.capitalize())
            for clr in available_colors
        ]
        await ctx.author.remove_roles(*filter(None, color_roles))
        # Assign the new role
        await ctx.author.add_roles(role)
        await ctx.send(
            f"Your color has been set to **{color_name.capitalize()}**!")
    else:
        await ctx.send(
            "That color is not available. Please choose from: " +
            ", ".join([clr.capitalize() for clr in available_colors]))


# Command to reset a user's color
@bot.command(name='resetcolor')
async def reset_color(ctx):
    # Remove all color roles
    color_roles = [
        discord.utils.get(ctx.guild.roles, name=clr.capitalize())
        for clr in available_colors
    ]
    await ctx.author.remove_roles(*filter(None, color_roles))
    await ctx.send("Your color has been reset to default.")


# Command to list available colors
@bot.command(name='colors')
async def list_colors(ctx):
    colors_list = ", ".join(
        [clr.capitalize() for clr in available_colors])
    await ctx.send(f"**Available Colors:** {colors_list}")


# Command to perform calculations
@bot.command(name='calc')
async def calculator(ctx, *, expression: str):
    try:
        # Safe evaluation of mathematical expressions
        allowed_chars = "0123456789+-*/(). "
        if any(char not in allowed_chars for char in expression):
            raise ValueError("Invalid characters in expression.")
        result = eval(expression)
        await ctx.send(f"The result of **{expression}** is: **{result}**")
    except Exception as e:
        await ctx.send(f"Error calculating the expression: {e}")


# Command to show written alphabets and characters
@bot.command(name='written')
async def written_script(ctx):
    scripts = {
        'Chinese':
        "汉字 (Hànzì)\n你好 (Nǐ hǎo) - Hello\n再见 (Zàijiàn) - Goodbye",
        'Greek':
        ("Γράμματα (Grámata)\n"
         "Χαίρετε (Chairete) - Hello\n"
         "Αντίο (Antío) - Goodbye\n"
         "Α α, Β β, Γ γ, Δ δ, Ε ε, Ζ ζ, Η η, Θ θ, Ι ι, Κ κ, Λ λ, Μ μ, Ν ν, Ξ ξ, Ο ο, Π π, Ρ ρ, Σ σ/ς, Τ τ, Υ υ, Φ φ, Χ χ, Ψ ψ, Ω ω"
         ),
        'Latin':
        ("Scriptura (Scripture)\n"
         "Salve - Hello\n"
         "Vale - Goodbye\n"
         "A a, B b, C c, D d, E e, F f, G g, H h, I i, J j, K k, L l, M m, N n, O o, P p, Q q, R r, S s, T t, U u, V v"
         ),
        'Sanskrit':
        ("लिपि (Lipī)\n"
         "नमस्ते (Namaste) - Hello\n"
         "अलविदा (Alvida) - Goodbye\n"
         "अ आ इ ई उ ऊ ऋ ए ओ क ख ग घ च छ ज झ ट ठ ड ढ त थ द ध न प फ ब भ म य र ल व श ष स ह"
         ),
        'Norse': ("Runes (Norse):\n"
                  "ᚠ (Fehu) - Wealth\n"
                  "ᚢ (Uruz) - Strength\n"
                  "ᚦ (Thurisaz) - Thorn\n"
                  "ᚨ (Ansuz) - God\n"
                  "ᚱ (Raido) - Journey\n"
                  "ᚲ (Kaunan) - Torch\n"
                  "ᚷ (Gebo) - Gift\n"
                  "ᚹ (Wunjo) - Joy\n"
                  "ᚺ (Hagalaz) - Hail\n"
                  "ᚾ (Naudiz) - Need\n"
                  "ᛁ (Isaz) - Ice\n"
                  "ᛃ (Jera) - Year\n"
                  "ᛇ (Eihwaz) - Yew\n"
                  "ᛈ (Perthro) - Mystery\n"
                  "ᛉ (Algiz) - Protection\n"
                  "ᛊ (Sowilo) - Sun\n"
                  "ᛏ (Tiwaz) - Honor\n"
                  "ᛒ (Berkano) - Growth\n"
                  "ᛖ (Ehwaz) - Horse\n"
                  "ᛗ (Madr) - Man")
    }
    response = "\n\n".join(
        [f"**{lang}**:\n{script}" for lang, script in scripts.items()])
    await ctx.send(response)


# Command to start a Hangman game
@bot.command(name='hangman')
async def hangman(ctx, lang: str):
    lang = lang.lower()
    if lang not in vocab_categories:
        await ctx.send(
            "Language not supported. Choose from Chinese, Greek, Latin, Sanskrit, or Norse."
        )
        return

    vocab = vocab_categories[lang]
    if not vocab:
        await ctx.send(f"No vocabulary available for {lang}.")
        return

    word, translation = random.choice(list(vocab.items()))
    guessed_letters = set()
    attempts = 6

    await ctx.send(
        "Starting Hangman! You have 6 incorrect guesses before you lose.")
    while attempts > 0:
        await ctx.send(
            f"Word: {' '.join([letter if letter in guessed_letters else '_' for letter in word])}"
        )
        await ctx.send(f"Guessed letters: {', '.join(sorted(guessed_letters))}"
                       )
        await ctx.send(f"Attempts left: {attempts}")

        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel

        try:
            guess = await bot.wait_for('message', check=check, timeout=30.0)
            letter = guess.content.lower()

            if letter in guessed_letters:
                await ctx.send("You've already guessed that letter!")
            elif letter in word:
                guessed_letters.add(letter)
                await ctx.send("Good guess!")
                if all(letter in guessed_letters for letter in word):
                    await ctx.send(
                        f"Congratulations! You've guessed the word: **{word}**"
                    )
                    return
            else:
                guessed_letters.add(letter)
                attempts -= 1
                await ctx.send("Wrong guess!")

        except asyncio.TimeoutError:
            await ctx.send(f"Time's up! The correct word was: **{word}**")
            return

    await ctx.send(f"You've run out of attempts! The word was: **{word}**")


# Command to start a word challenge
@bot.command(name='challenge')
async def challenge(ctx):
    await ctx.send(
        "Challenge accepted! Let's make learning fun and competitive!")


# Command to show the leaderboard
@bot.command(name='lead')
async def leaderboard_command(ctx):
    if not leaderboard:
        await ctx.send("No scores recorded yet.")
        return

    leaderboard_message = "\n".join([
        f"<@{user_id}>: {score} points"
        for user_id, score in leaderboard.items()
    ])
    await ctx.send(f"**Leaderboard:**\n{leaderboard_message}")


# Access the Discord bot token
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
