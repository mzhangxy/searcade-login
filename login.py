import os
import time
from seleniumbase import Driver

def auto_login():
    email = os.environ.get("USER_EMAIL")
    password = os.environ.get("USER_PASSWORD")
    
    # 使用 uc=True 绕过检测
    driver = Driver(uc=True, headless2=True)
    
    try:
        print("正在访问首页...")
        driver.get("https://searcade.com/en/")
        
        # 优化点 1: 使用更宽泛的 CSS 选择器定位 Login 按钮
        # 尝试匹配包含 "Login" 文本的 a 标签，或 class 中包含 login 的元素
        print("尝试寻找 Login 按钮...")
        login_selector = 'a:contains("Login")' 
        
        # 等待元素加载，增加容错
        driver.wait_for_element(login_selector, timeout=15)
        driver.click(login_selector)
        
        # 优化点 2: 处理 Cloudflare 5秒盾
        # 页面跳转到登录页时，Cloudflare 可能会拦截
        print("已进入登录流程，等待 CF 验证或页面加载...")
        time.sleep(5) # 强制等待 5 秒是过盾的基础要求
        
        # 第一步：输入 Email
        driver.wait_for_element('input[type="email"]', timeout=20)
        driver.type('input[type="email"]', email)
        print("已输入 Email")
        
        # 点击 Continue (通常是一个 type="submit" 的 button)
        driver.click('button[type="submit"]')
        
        # 第二步：输入 Password
        # 此时可能会再次触发 CF 挑战，driver.wait_for_element 会自动重试
        print("等待密码输入框...")
        driver.wait_for_element('input[type="password"]', timeout=20)
        driver.type('input[type="password"]', password)
        print("已输入密码")
        
        driver.click('button[type="submit"]')
        
        # 登录成功检查
        print("点击登录，等待页面跳转...")
        time.sleep(8) # 给页面足够的渲染时间
        
        current_url = driver.current_url
        print(f"当前页面 URL: {current_url}")

        # 只要 URL 包含 admin 或页面出现了"Successfully signed in as mzhangxy"文本，就视为成功
        if driver.is_text_visible("Successfully signed in as mzhangxy"):
            print("✅ 登录成功！已成功进入管理后台。")
        else:
            print(f"未能确认登录状态，当前路径: {driver.current_url}")
            driver.save_screenshot("debug_login.png")
            return  # 登录失败则终止后续巡检

        # 第三步：服务器状态巡检 
        print("开始巡检服务器状态...")
        driver.wait_for_element('div[class*="row"]', timeout=15)
        
        # 定义服务器 名字 -> ID 的映射
        # michael -> 4193, color -> 4159
        server_config = {
            "michael": "4193",
            "color": "4159" 
        }
        
        for name, s_id in server_config.items():
            print(f"正在检查服务器: {name} (ID: {s_id})...")
            
            # 使用精准的 CSS 选择器定位：寻找 href 包含特定 ID 的 a 标签
            # 这种方法不依赖任何文本，只看 HTML 结构里的 ID
            id_selector = f'a[href*="/servers/{s_id}"]'
            
            if driver.is_element_visible(id_selector):
                # 提取状态文字
                status_text = driver.get_text(f"{id_selector} span").strip().lower()
                
                if "online" in status_text:
                    print(f"🟢 服务器 {name} (ID: {s_id}) 正常在线。")
                else:
                    print(f"🔴 服务器 {name} (ID: {s_id}) 不在线，准备进入控制台...")
                    
                    # 直接跳转到控制台 URL，比点击卡片更高效、更不容易出错
                    console_url = f"https://searcade.com/en/admin/servers/{s_id}"
                    driver.get(console_url)
                    
                    # 第四步：自愈操作
                    print(f"已进入控制台，寻找 Start 按钮...")
                    driver.wait_for_element('button:contains("Start")', timeout=15)
                    driver.click('button:contains("Start")')
                    
                    try:
                        # 监测状态变为 Online
                        driver.wait_for_text("Online", 'span[class*="badge"]', timeout=90)
                        print(f"🎊 服务器 {name} 重启成功！")
                    except:
                        print(f"❌ 等待超时，请手动检查服务器 {name}。")
                    
                    # 返回列表页继续检查下一个
                    driver.get("https://searcade.com/en/admin")
                    time.sleep(5)
            else:
                print(f"❓ 未能在页面上找到 ID 为 {s_id} 的服务器。")

    except Exception as e:
        print(f"❌ 运行过程中发生错误: {e}")
        driver.save_screenshot("error_report.png")
    finally:
        driver.quit()

if __name__ == "__main__":
    auto_login()
