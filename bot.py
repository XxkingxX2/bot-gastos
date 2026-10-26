import os
import telebot
from dotenv import load_dotenv
from database import init_db, registrar_gasto, obtener_resumen_mes

load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

if not TOKEN:
    raise ValueError("❌ No se encontró el TELEGRAM_BOT_TOKEN en el archivo .env")

bot = telebot.TeleBot(TOKEN)
init_db()

@bot.message_handler(commands=['start', 'help'])
def enviar_bienvenida(message):
    ayuda_texto = (
        "🤖 *¡Hola! Soy tu bot personal de control de gastos.*\n\n"
        "📝 *Para registrar un gasto*, escribe:\n"
        "`[monto] [categoría] [descripción opcional]`\n"
        "_Ejemplo:_ `12.50 comida almuerzo`\n\n"
        "📊 *Para ver tus cuentas*, escribe:\n"
        "`resumen` (o `total`)\n\n"
        "🔒 _Tus datos son totalmente privados e independientes._"
    )
    bot.reply_to(message, ayuda_texto, parse_mode="Markdown")

@bot.message_handler(func=lambda message: True)
def procesar_mensaje_libre(message):
    user_id = message.from_user.id  # <-- Capturamos el ID único de Telegram del usuario
    texto = message.text.strip()
    
    # 1. Resumen del usuario
    if texto.lower() in ["resumen", "total", "saldo"]:
        total_mes, desglose = obtener_resumen_mes(user_id)
        if total_mes == 0:
            bot.reply_to(message, "📊 No tienes gastos registrados en este mes.")
            return

        respuesta = f"📊 *Tus Gastos del Mes*\n💰 *Total acumulado:* ${total_mes:.2f}\n\n*Desglose por categoría:*\n"
        for cat, monto in desglose:
            respuesta += f"• {cat.capitalize()}: ${monto:.2f}\n"
        
        bot.reply_to(message, respuesta, parse_mode="Markdown")
        return

    # 2. Registrar gasto del usuario
    partes = texto.split(maxsplit=2)
    
    if len(partes) < 2:
        bot.reply_to(
            message, 
            "⚠️ No entendí el mensaje.\nEscribe el gasto así: `10.50 comida almuerzo`\nO escribe `resumen` para ver tus cuentas.", 
            parse_mode="Markdown"
        )
        return

    try:
        monto = float(partes[0].replace(',', '.'))
        categoria = partes[1]
        descripcion = partes[2] if len(partes) > 2 else ""

        registrar_gasto(user_id, monto, categoria, descripcion)

        respuesta = f"✅ *Gasto guardado*\n• Monto: ${monto:.2f}\n• Categoría: {categoria.capitalize()}"
        if descripcion:
            respuesta += f"\n• Nota: {descripcion}"
            
        bot.reply_to(message, respuesta, parse_mode="Markdown")
        
    except ValueError:
        bot.reply_to(message, "❌ El primer valor debe ser el monto en números. Ejemplo: `15 transporte taxi`", parse_mode="Markdown")

if __name__ == "__main__":
    print("🤖 Bot multiusuario de Telegram iniciado...")
    bot.infinity_polling()