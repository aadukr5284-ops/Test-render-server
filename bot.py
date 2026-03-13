#!/usr/bin/env python3
"""
🔥 PRO INFO BOT - PSUTIL-FREE VERSION 🔥
Render Pro Edition - Bina psutil ke chalega!
"""

import os
import sys
import platform
import subprocess
import socket
import datetime
import requests
import time
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes

# ============================================================================
# CONFIGURATION
# ============================================================================

BOT_TOKEN = "8772560384:AAEGRgYpRPPaKKKO87sGTg0vC6Plm3qWNpc"

# ============================================================================
# SYSTEM INFO WITHOUT PSUTIL
# ============================================================================

class SystemCollector:
    """Bina psutil ke system info collect karega"""
    
    @staticmethod
    def get_basic_info():
        """Basic system info"""
        uname = platform.uname()
        
        # Get public IP
        try:
            public_ip = requests.get('https://api.ipify.org', timeout=5).text
        except:
            public_ip = "Not available"
        
        return {
            "🖥️ HOSTNAME": socket.gethostname(),
            "🌐 LOCAL IP": socket.gethostbyname(socket.gethostname()),
            "🌍 PUBLIC IP": public_ip,
            "💻 OS": f"{uname.system} {uname.release}",
            "🏭 ARCH": uname.machine,
            "🐍 PYTHON": sys.version.split()[0],
            "⏰ TIME": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    
    @staticmethod
    def get_cpu_info():
        """CPU info from /proc/cpuinfo"""
        try:
            with open('/proc/cpuinfo', 'r') as f:
                data = f.read()
            
            # Count cores
            cores = data.count('processor')
            
            # Get model
            model = "Unknown"
            for line in data.split('\n'):
                if 'model name' in line:
                    model = line.split(':')[1].strip()
                    break
            
            # Get load average
            try:
                load = os.getloadavg()
                load_str = f"{load[0]:.2f}, {load[1]:.2f}, {load[2]:.2f}"
            except:
                load_str = "N/A"
            
            return {
                "🔤 MODEL": model,
                "💪 CORES": cores,
                "📊 LOAD": load_str
            }
        except:
            return {
                "🔤 MODEL": platform.processor() or "Unknown",
                "💪 CORES": os.cpu_count() or "Unknown",
                "ℹ️": "Limited CPU info"
            }
    
    @staticmethod
    def get_memory_info():
        """Memory from /proc/meminfo"""
        try:
            with open('/proc/meminfo', 'r') as f:
                data = f.read()
            
            mem = {}
            for line in data.split('\n'):
                if ':' in line:
                    k, v = line.split(':')
                    mem[k] = v.strip().split()[0]
            
            total = int(mem.get('MemTotal', 0)) // 1024
            free = int(mem.get('MemFree', 0)) // 1024
            available = int(mem.get('MemAvailable', total)) // 1024
            used = total - free
            
            return {
                "💾 TOTAL": f"{total} MB",
                "📤 USED": f"{used} MB",
                "📥 FREE": f"{free} MB",
                "📊 USAGE": f"{(used/total)*100:.1f}%" if total > 0 else "N/A"
            }
        except:
            return {"ℹ️": "Memory info unavailable"}
    
    @staticmethod
    def get_disk_info():
        """Disk from df command"""
        try:
            result = subprocess.run(['df', '-h'], capture_output=True, text=True)
            lines = result.stdout.split('\n')[1:4]  # First few partitions
            
            disks = []
            for line in lines:
                if line:
                    parts = line.split()
                    if len(parts) >= 6:
                        disks.append(f"📂 {parts[5]}: {parts[1]} ({parts[4]} used)")
            
            return "\n".join(disks) if disks else "No disk info"
        except:
            return "Disk info unavailable"
    
    @staticmethod
    def get_network_info():
        """Network interfaces"""
        try:
            result = subprocess.run(['ip', '-br', 'addr'], capture_output=True, text=True)
            return result.stdout[:500] if result.stdout else "No network info"
        except:
            return "Network info unavailable"
    
    @staticmethod
    def get_uptime():
        """Uptime from /proc/uptime"""
        try:
            with open('/proc/uptime', 'r') as f:
                uptime = float(f.read().split()[0])
            
            days = int(uptime // 86400)
            hours = int((uptime % 86400) // 3600)
            minutes = int((uptime % 3600) // 60)
            
            return f"{days}d {hours}h {minutes}m"
        except:
            return "Unknown"
    
    @staticmethod
    def speed_test():
        """Internet speed test"""
        try:
            import speedtest
            st = speedtest.Speedtest()
            st.get_best_server()
            
            download = st.download() / 1_000_000
            upload = st.upload() / 1_000_000
            ping = st.results.ping
            
            return {
                "📥 DOWNLOAD": f"{download:.2f} Mbps",
                "📤 UPLOAD": f"{upload:.2f} Mbps",
                "🏓 PING": f"{ping:.2f} ms"
            }
        except Exception as e:
            return {"error": f"Speed test failed: {str(e)}"}


# ============================================================================
# BOT HANDLERS
# ============================================================================

class InfoBot:
    def __init__(self):
        self.collector = SystemCollector()
        self.start_time = time.time()
    
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Start command"""
        user = update.effective_user
        
        welcome = f"""
╔══════════════════════════════════════════════╗
║   🔥 PRO INFO BOT - RENDER PRO EDITION 🔥   ║
╚══════════════════════════════════════════════╝

👋 Welcome {user.first_name}!

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📌 <b>COMMANDS:</b>

🔹 /start  - Home menu
🔹 /status - Quick status
🔹 /system - Full system info
🔹 /cpu    - CPU details
🔹 /memory - RAM details
🔹 /disk   - Storage info
🔹 /speed  - Internet speed
🔹 /uptime - Bot uptime

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

👇 <b>Select option:</b> 👇
        """
        
        keyboard = [
            [InlineKeyboardButton("📊 STATUS", callback_data="status"),
             InlineKeyboardButton("💻 SYSTEM", callback_data="system")],
            [InlineKeyboardButton("🧠 CPU", callback_data="cpu"),
             InlineKeyboardButton("💾 MEMORY", callback_data="memory")],
            [InlineKeyboardButton("💿 DISK", callback_data="disk"),
             InlineKeyboardButton("⚡ SPEED", callback_data="speed")],
            [InlineKeyboardButton("⏰ UPTIME", callback_data="uptime")]
        ]
        
        await update.message.reply_text(
            welcome,
            parse_mode='HTML',
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    
    async def status(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Quick status"""
        basic = self.collector.get_basic_info()
        cpu = self.collector.get_cpu_info()
        mem = self.collector.get_memory_info()
        
        msg = f"""
╔══════════════════════════════════════════════╗
║              📊 QUICK STATUS                 ║
╚══════════════════════════════════════════════╝

🌍 <b>Public IP:</b> {basic['🌍 PUBLIC IP']}
💻 <b>Hostname:</b> {basic['🖥️ HOSTNAME']}
🏭 <b>OS:</b> {basic['💻 OS']}

🧠 <b>CPU:</b> {cpu['💪 CORES']} cores
📊 <b>Load:</b> {cpu.get('📊 LOAD', 'N/A')}

💾 <b>RAM:</b> {mem.get('📊 USAGE', 'N/A')}
⏰ <b>Time:</b> {basic['⏰ TIME']}
        """
        
        if update.callback_query:
            await update.callback_query.edit_message_text(
                msg, parse_mode='HTML',
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("🔙 BACK", callback_data="back_to_menu")
                ]])
            )
        else:
            await update.message.reply_text(msg, parse_mode='HTML')
    
    async def system_info(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Full system info"""
        basic = self.collector.get_basic_info()
        uptime = self.collector.get_uptime()
        
        msg = f"""
╔══════════════════════════════════════════════╗
║            💻 SYSTEM INFORMATION             ║
╚══════════════════════════════════════════════╝

🖥️ <b>Hostname:</b> {basic['🖥️ HOSTNAME']}
🌐 <b>Local IP:</b> {basic['🌐 LOCAL IP']}
🌍 <b>Public IP:</b> {basic['🌍 PUBLIC IP']}
💻 <b>Operating System:</b> {basic['💻 OS']}
🏭 <b>Architecture:</b> {basic['🏭 ARCH']}
🐍 <b>Python Version:</b> {basic['🐍 PYTHON']}
⏰ <b>Current Time:</b> {basic['⏰ TIME']}
⏱️ <b>System Uptime:</b> {uptime}
        """
        
        if update.callback_query:
            await update.callback_query.edit_message_text(
                msg, parse_mode='HTML',
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("🔙 BACK", callback_data="back_to_menu")
                ]])
            )
        else:
            await update.message.reply_text(msg, parse_mode='HTML')
    
    async def cpu_info(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """CPU details"""
        cpu = self.collector.get_cpu_info()
        
        msg = f"""
╔══════════════════════════════════════════════╗
║                🧠 CPU DETAILS                 ║
╚══════════════════════════════════════════════╝

🔤 <b>Model:</b> {cpu['🔤 MODEL']}
💪 <b>Physical Cores:</b> {cpu['💪 CORES']}
📊 <b>Load Average:</b> {cpu.get('📊 LOAD', 'N/A')}
        """
        
        if update.callback_query:
            await update.callback_query.edit_message_text(
                msg, parse_mode='HTML',
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("🔙 BACK", callback_data="back_to_menu")
                ]])
            )
        else:
            await update.message.reply_text(msg, parse_mode='HTML')
    
    async def memory_info(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Memory details"""
        mem = self.collector.get_memory_info()
        
        msg = f"""
╔══════════════════════════════════════════════╗
║              💾 MEMORY DETAILS                ║
╚══════════════════════════════════════════════╝

{chr(10).join([f"<b>{k}:</b> {v}" for k, v in mem.items()])}
        """
        
        if update.callback_query:
            await update.callback_query.edit_message_text(
                msg, parse_mode='HTML',
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("🔙 BACK", callback_data="back_to_menu")
                ]])
            )
        else:
            await update.message.reply_text(msg, parse_mode='HTML')
    
    async def disk_info(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Disk details"""
        disk = self.collector.get_disk_info()
        
        msg = f"""
╔══════════════════════════════════════════════╗
║              💿 DISK INFORMATION              ║
╚══════════════════════════════════════════════╝

{disk}
        """
        
        if update.callback_query:
            await update.callback_query.edit_message_text(
                msg, parse_mode='HTML',
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("🔙 BACK", callback_data="back_to_menu")
                ]])
            )
        else:
            await update.message.reply_text(msg, parse_mode='HTML')
    
    async def speed_test(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Speed test"""
        msg = "⚡ Running speed test... Please wait (10-15 seconds) ⏳"
        
        if update.callback_query:
            await update.callback_query.edit_message_text(msg)
            speed = self.collector.speed_test()
        else:
            sent = await update.message.reply_text(msg)
            speed = self.collector.speed_test()
        
        if "error" in speed:
            result = f"❌ {speed['error']}"
        else:
            result = f"""
╔══════════════════════════════════════════════╗
║            ⚡ SPEED TEST RESULTS              ║
╚══════════════════════════════════════════════╝

📥 <b>Download:</b> {speed['📥 DOWNLOAD']}
📤 <b>Upload:</b> {speed['📤 UPLOAD']}
🏓 <b>Ping:</b> {speed['🏓 PING']}
            """
        
        if update.callback_query:
            await update.callback_query.edit_message_text(
                result, parse_mode='HTML',
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("🔙 BACK", callback_data="back_to_menu")
                ]])
            )
        else:
            await sent.edit_text(result, parse_mode='HTML')
    
    async def uptime_info(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Bot uptime"""
        uptime_seconds = time.time() - self.start_time
        days = int(uptime_seconds // 86400)
        hours = int((uptime_seconds % 86400) // 3600)
        minutes = int((uptime_seconds % 3600) // 60)
        seconds = int(uptime_seconds % 60)
        
        system_uptime = self.collector.get_uptime()
        
        msg = f"""
╔══════════════════════════════════════════════╗
║                ⏰ UPTIME                      ║
╚══════════════════════════════════════════════╝

🤖 <b>Bot Uptime:</b> {days}d {hours}h {minutes}m {seconds}s
💻 <b>System Uptime:</b> {system_uptime}
        """
        
        if update.callback_query:
            await update.callback_query.edit_message_text(
                msg, parse_mode='HTML',
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("🔙 BACK", callback_data="back_to_menu")
                ]])
            )
        else:
            await update.message.reply_text(msg, parse_mode='HTML')
    
    async def back_to_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Back to main menu"""
        await self.start(update, context)
    
    async def button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle button clicks"""
        query = update.callback_query
        await query.answer()
        
        handlers = {
            "status": self.status,
            "system": self.system_info,
            "cpu": self.cpu_info,
            "memory": self.memory_info,
            "disk": self.disk_info,
            "speed": self.speed_test,
            "uptime": self.uptime_info,
            "back_to_menu": self.back_to_menu
        }
        
        handler = handlers.get(query.data)
        if handler:
            await handler(update, context)


# ============================================================================
# MAIN
# ============================================================================

def main():
    print("""
╔══════════════════════════════════════════════╗
║   🔥 PRO INFO BOT - PSUTIL-FREE VERSION 🔥  ║
║                                              ║
║           ⚡ BOT STARTING... ⚡               ║
╚══════════════════════════════════════════════╝
    """)
    
    bot = InfoBot()
    app = Application.builder().token(BOT_TOKEN).build()
    
    # Add handlers
    app.add_handler(CommandHandler("start", bot.start))
    app.add_handler(CommandHandler("status", bot.status))
    app.add_handler(CommandHandler("system", bot.system_info))
    app.add_handler(CommandHandler("cpu", bot.cpu_info))
    app.add_handler(CommandHandler("memory", bot.memory_info))
    app.add_handler(CommandHandler("disk", bot.disk_info))
    app.add_handler(CommandHandler("speed", bot.speed_test))
    app.add_handler(CommandHandler("uptime", bot.uptime_info))
    app.add_handler(CallbackQueryHandler(bot.button_callback))
    
    print("✅ Bot is running! Press Ctrl+C to stop.")
    app.run_polling()


if __name__ == "__main__":
    main()