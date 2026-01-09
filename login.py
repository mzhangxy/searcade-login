import os
import time
from seleniumbase import Driver

def auto_login():
    # 获取环境变量（在 GitHub Actions 中配置）
    email = os.environ.get("USER_EMAIL")
    password = os.environ.get("USER_PASSWORD")
    
    # 启动 Undetected Chromedriver
    # uc=True 开启绕过模式，headless2 是专门为绕过设计的增强型无头模式
    driver = Driver(uc=True, headless2=True)
    
    try:
        print("正在访问首页...")
        driver.get("https://searcade.com/en/")
        time.sleep(2)
        
        # 1. 点击登录按钮
        print("点击 Login 按钮...")
        driver.click('a[href*="/login"]') # 根据实际选择器调整
        
        # 2. 第一个页面：输入 Email
        # SeleniumBase 会自动等待 CF 验证完成
        print("正在处理 Email 页面 (等待 CF 验证)...")
        driver.type('input[type="email"]', email)
        time.sleep(1)
        driver.click('button:contains("Continue")') # 匹配包含 Continue 的按钮
        
        # 3. 第二个页面：输入 Password
        print("正在处理 Password 页面...")
        # 等待密码输入框出现
        driver.wait_for_element('input[type="password"]')
        driver.type('input[type="password"]', password)
        time.sleep(1)
        
        # 点击最终登录
        driver.click('button[type="submit"]')
        
        # 验证是否登录成功
        time.sleep(5)
        if "dashboard" in driver.current_url or driver.is_element_visible('a[href*="/logout"]'):
            print("登录成功！")
            # 在这里保存 Cookie 或执行后续操作
            cookies = driver.get_cookies()
            print(f"成功获取 Cookie，数量: {len(cookies)}")
        else:
            print(f"登录可能失败，当前 URL: {driver.current_url}")
            driver.save_screenshot("login_failed.png")

    except Exception as e:
        print(f"发生错误: {e}")
        driver.save_screenshot("error.png")
    finally:
        driver.quit()

if __name__ == "__main__":
    auto_login()
