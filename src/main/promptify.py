import logging
import openai
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes

OPENAI_API_KEY = ''
TELEGRAM_BOT_TOKEN = 'Տոկենը ստեղ չեմ տեղադրում)'
openai.api_key = OPENAI_API_KEY

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    welcome_text = (
        "Hi there! I'm your image assistant bot. 🖼️ "
        "Send /imggen followed by an image description, and I'll first craft a precise prompt using ChatGPT, "
        "then generate a DALL-E image for you based on it."
    )
    await update.message.reply_text(welcome_text)
    logging.info(f"Sent welcome message to user: {update.effective_user.username or update.effective_user.id}")


async def generate_prompt(characteristics: str) -> str:
    logging.info(f"Creating prompt for characteristics: {characteristics}")
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user",
             "content": f"Please generate a detailed prompt for DALL-E using these characteristics: {characteristics}"}
        ]
    )
    prompt = response['choices'][0]['message']['content']
    logging.info(f"Refined prompt: {prompt}")
    return prompt


async def generate_image(prompt: str) -> str:
    logging.info(f"Generating image with prompt: {prompt}")
    response = openai.Image.create(
        prompt=prompt,
        n=1,
        size="1024x1024"
    )
    image_url = response['data'][0]['url']
    logging.info(f"Generated image URL: {image_url}")
    return image_url


async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    characteristics = update.message.text[len('/imggen '):]
    logging.info(
        f"Image generation request from {update.effective_user.username or update.effective_user.id} with description: {characteristics}")
    try:
        refined_prompt = await generate_prompt(characteristics)
        image_url = await generate_image(refined_prompt)
        await context.bot.send_photo(chat_id=update.effective_chat.id, photo=image_url)
        logging.info(f"Image successfully sent to user: {update.effective_user.username or update.effective_user.id}")
    except Exception as e:
        logging.error(f"Error during image processing: {e}")
        await context.bot.send_message(chat_id=update.effective_chat.id,
                                       text="Oops! Something went wrong with the image generation. Try again!")


async def run() -> None:
    application = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    application.add_handler(MessageHandler(filters.COMMAND & filters.Regex(r'^/imggen'), handle_text))
    application.add_handler(MessageHandler(filters.COMMAND & filters.Regex(r'^/start'), start))
    logging.info("Bot is now up and running")
    application.run_polling()
