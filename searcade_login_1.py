import os
import time
import requests
from seleniumbase import Driver

def send_telegram_msg(message):
    """发送通知到 Telegram"""
    token = os.environ.get("TG_BOT_TOKEN")
    chat_id = os.environ.get("TG_CHAT_ID")
    if not token or not chat_id:
        print("⚠️ 未配置 Telegram Token 或 Chat ID，跳过通知。")
        return

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": f"🤖 **Searcade 运维助手报告**\n\n{message}",
        "parse_mode": "Markdown"
    }
    try:
        requests.post(url, json=payload, timeout=10)
    except Exception as e:
        print(f"发送 TG 通知失败: {e}")

def run_auto_maintenance():
    email = os.environ.get("USER_EMAIL")
    password = os.environ.get("USER_PASSWORD")
    
    server_config = {
        "michael": "4193",
        "color": "4159"
    }

    driver = Driver(uc=True, headless2=True)
    
    try:
        # --- 1. 登录流程 ---
        print("正在登录...")
        driver.get("https://searcade.com/en/login")
        driver.type('input[type="email"]', email)
        driver.click('button[type="submit"]')
        
        driver.wait_for_element('input[type="password"]', timeout=25)
        driver.type('input[type="password"]', password)
        driver.click('button[type="submit"]')
        
        # --- 2. 状态验证 ---
        time.sleep(10)
        if "/admin" not in driver.current_url and not driver.is_text_visible("Logout"):
            send_telegram_msg("❌ 登录失败：未能进入管理后台，请检查 GitHub Actions 截图。")
            return

        # --- 3. 巡检与自愈 ---
        driver.get("https://searcade.com/en/admin")
        driver.wait_for_element('div[class*="row"]', timeout=20)
        
        for name, s_id in server_config.items():
            id_selector = f'a[href*="/servers/{s_id}"]'
            
            if driver.is_element_visible(id_selector):
                status_text = driver.get_text(f"{id_selector} span").strip().lower()
                
                if "online" in status_text:
                    print(f"🟢 {name} 在线")
                else:
                    msg = f"🔴 服务器 `{name}` (ID: {s_id}) 掉线了！状态: {status_text}。正在尝试重启..."
                    print(msg)
                    send_telegram_msg(msg)
                    
                    # 尝试启动
                    driver.get(f"https://searcade.com/en/admin/servers/{s_id}")
                    driver.wait_for_element('button:contains("Start")', timeout=20)
                    driver.click('button:contains("Start")')
                    
                    try:
                        driver.wait_for_text("Online", 'span[class*="badge"]', timeout=90)
                        success_msg = f"🎊 服务器 `{name}` 重启成功，现已恢复在线！"
                        print(success_msg)
                        send_telegram_msg(success_msg)
                    except:
                        fail_msg = f"⚠️ 服务器 `{name}` 重启指令已发送，但 90 秒内未检测到在线状态，请检查控制台。"
                        print(fail_msg)
                        send_telegram_msg(fail_msg)
                    
                    driver.get("https://searcade.com/en/admin")
                    time.sleep(5)
            else:
                print(f"❓ 未找到服务器 {name}")

    except Exception as e:
        error_msg = f"🚨 脚本运行异常: {str(e)}"
        print(error_msg)
        send_telegram_msg(error_msg)
    finally:
        driver.quit()

if __name__ == "__main__":
    run_auto_maintenance()


#下面是需加入工作流yaml的内容:
env:
        USER_EMAIL: ${{ secrets.USER_EMAIL }}
        USER_PASSWORD: ${{ secrets.USER_PASSWORD }}
        TG_BOT_TOKEN: ${{ secrets.TG_BOT_TOKEN }}   # 新增
        TG_CHAT_ID: ${{ secrets.TG_CHAT_ID }}       # 新增
