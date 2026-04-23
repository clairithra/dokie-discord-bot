import discord
import os
import httpx
from discord.ext import commands

# Bot setup
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# DeepSeek API setup
DEEPSEEK_API_KEY = os.environ.get('DEEPSEEK_API_KEY')
DEEPSEEK_URL = "https://api.deepseek.com/v1/chat/completions"

# FAQ responses (保持不变)
FAQ_RESPONSES = {
    "download_app": "You can access Dokie directly at **https://dokie.ai** — no download needed! It's a web-based tool that works in your browser. Just sign up and start creating 🎨",
    "export_project": "To download your presentation:\n1. Click the **Export** button in the top right\n2. Choose your format (PPTX, PDF, etc.)\n3. Wait for it to process\n\n⚠️ Note: Exported files may look slightly different from the preview. For the best experience, use the **Share Link** to preserve all animations and designs!",
    "sign_in": "Having trouble signing in? Try these steps:\n1. Clear your browser cache and cookies\n2. Try a different browser (Chrome/Edge recommended)\n3. Check if you're using the correct email\n4. Use 'Forgot Password' if needed\n\nStill stuck? Email us at **support@dokie.ai** with your account email.",
    "crash": "Sorry to hear you're experiencing issues! To help us fix this ASAP, please email **support@dokie.ai** with:\n1. Your account email\n2. Project share link (if applicable)\n3. What you were doing when it crashed\n4. Any error messages you saw\n\nWe'll investigate and get back to you within 24 hours!",
    "refund": "You can cancel your subscription anytime in your account settings — changes take effect at the next billing cycle.\n\nRefund requests: Per our Terms (Section 6), we can't refund unused time since credits and server resources are allocated immediately upon renewal. Your plan stays active until the end of your current billing period.\n\nFor special circumstances, email **support@dokie.ai** with your account details.",
    "export_issues": "Our export engine is being optimized. If your exported file looks different from the Dokie preview, **don't waste credits trying to fix it** — it's likely a rendering bug.\n\n✨ **Best solution:** Use the **Share Link** instead! It preserves all designs and animations exactly as they appear in Dokie.",
    "generation_error": "Sorry the generation didn't work! This can happen due to network issues or model hiccups.\n\nTo help us fix this, email **support@dokie.ai** with:\n1. Your account email\n2. Project share link\n3. Brief description of what went wrong\n\nWe'll investigate + compensate you with credits!",
    "generation_bad": "Sorry the AI didn't nail it this time! Sometimes the model has a brain fart during complex tasks.\n\nEmail **support@dokie.ai** with your project link and we'll refund the credits used. You can also try regenerating with more specific prompts!",
    "slow": "Performance issues can be caused by:\n- Network connection\n- Browser (try Chrome/Edge)\n- Large projects with many slides\n- Too many browser tabs open\n\nIf it's consistently slow, email **support@dokie.ai** with details!",
    "version_history": "Version history is in the **left sidebar** when you open your project! Every iteration is saved automatically. Just click on any version to restore it. 🕐",
    "mobile": "We don't have a dedicated mobile app yet, but our website is mobile-optimized! You can open **https://dokie.ai** on your phone and use it directly in your browser. 📱",
    "credits": "Check your credit balance in **Account Settings**. Each plan comes with monthly credits that reset at your billing cycle. Need more? You can upgrade your plan or purchase credit top-ups!",
    "feature_request": "Love hearing ideas from users! 🎉\n\nEmail **support@dokie.ai** with your suggestion and we'll pass it to the product team. We might even throw in some bonus credits as a thank-you!"
}

async def should_respond_and_classify(message_content: str):
    """
    Step 1: 判断是否应该回复
    Step 2: 如果应该回复,分类问题类型
    """
    prompt = f"""You are Dokie AI's support bot. Dokie is an AI presentation tool (dokie.ai).

Analyze this message: "{message_content}"

First, determine if this message is asking a question about Dokie or needs Dokie support.

IGNORE messages that are:
- General chat/greetings
- Questions about hiring/jobs/developers
- Completely unrelated to Dokie product

If the message IS about Dokie, classify it into ONE category:
- download_app: Where to download Dokie
- export_project: How to download/export presentations
- sign_in: Login issues
- crash: App crashed/broken/errors
- refund: Refunds/billing/subscriptions
- export_issues: Export formatting problems
- generation_error: AI generation failed
- generation_bad: Poor AI output quality
- slow: Performance/speed issues
- version_history: Finding old versions
- mobile: Mobile app questions
- credits: Credit balance questions
- feature_request: Feature suggestions

Respond with ONLY:
- "ignore" if the message is not about Dokie
- The category name if it is about Dokie"""

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                DEEPSEEK_URL,
                headers={
                    "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "deepseek-chat",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.1,
                    "max_tokens": 50
                },
                timeout=10.0
            )

            if response.status_code == 200:
                result = response.json()
                answer = result['choices'][0]['message']['content'].strip().lower()
                return answer if answer != "ignore" else None
            else:
                return None

    except Exception as e:
        print(f"API error: {e}")
        return None

@bot.event
async def on_ready():
    print(f'✅ {bot.user} is online!')

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    # 让DeepSeek判断是否应该回复 + 分类
    category = await should_respond_and_classify(message.content)

    # 如果DeepSeek说应该回复,就回复
    if category and category in FAQ_RESPONSES:
        await message.reply(FAQ_RESPONSES[category])

    await bot.process_commands(message)

# Run bot
token = os.environ.get('DISCORD_BOT_TOKEN')
if not token:
    print("ERROR: DISCORD_BOT_TOKEN not found!")
    exit(1)
bot.run(token)
