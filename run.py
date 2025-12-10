# ===========================================
# run.py - Main entry point
# ===========================================
import asyncio
import logging
from multiprocessing import Process
from utils.scheduler import start_scheduler, stop_scheduler

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def run_admin_bot():
    """Run Admin Bot"""
    from admin_bot.main import main
    asyncio.run(main())

def run_user_bot():
    """Run User Bot"""
    from user_bot.main import main
    asyncio.run(main())

def run_bypass_server():
    """Run Bypass Detection Server"""
    from bypass_server.app import app
    from config.settings import Config
    app.run(host=Config.SERVER_HOST, port=Config.SERVER_PORT)

if __name__ == "__main__":
    print("🚀 Starting Telegram Resource Distribution System...")
    print("=" * 50)
    
    # Start scheduler
    start_scheduler()
    
    # Create processes for each component
    admin_process = Process(target=run_admin_bot, name="AdminBot")
    user_process = Process(target=run_user_bot, name="UserBot")
    server_process = Process(target=run_bypass_server, name="BypassServer")
    
    try:
        # Start all processes
        admin_process.start()
        user_process.start()
        server_process.start()
        
        print("✅ Admin Bot started")
        print("✅ User Bot started")
        print("✅ Bypass Server started")
        print("=" * 50)
        print("System is running. Press Ctrl+C to stop.")
        
        # Wait for processes
        admin_process.join()
        user_process.join()
        server_process.join()
        
    except KeyboardInterrupt:
        print("\n\n🛑 Shutting down...")
        
        admin_process.terminate()
        user_process.terminate()
        server_process.terminate()
        
        admin_process.join()
        user_process.join()
        server_process.join()
        
        stop_scheduler()
        
        print("✅ All services stopped")