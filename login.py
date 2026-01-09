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
        
        # 点击 Continue (根据图片，这通常是一个 type="submit" 的 button)
        driver.click('button[type="submit"]')
        
        # 第二步：输入 Password
        # 此时可能会再次触发 CF 挑战，driver.wait_for_element 会自动重试
        print("等待密码输入框...")
        driver.wait_for_element('input[type="password"]', timeout=20)
        driver.type('input[type="password"]', password)
        print("已输入密码")
        
        driver.click('button[type="submit"]')
        
        # 登录成功检查
        time.sleep(5)
        if "dashboard" in driver.current_url or driver.is_element_visible('a:contains("Logout")'):
            print("🎉 登录成功！")
        else:
            print(f"未能确认登录状态，当前路径: {driver.current_url}")
            driver.save_screenshot("debug_login.png")

    except Exception as e:
        print(f"❌ 运行出错: {e}")
        driver.save_screenshot("error_screenshot.png")
    finally:
        driver.quit()

if __name__ == "__main__":
    auto_login()
