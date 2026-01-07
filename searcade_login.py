from playwright.sync_api import sync_playwright
from playwright_stealth import stealth  # Install with: pip install playwright-stealth
import os
import time

def login_searcade(username, password):
    with sync_playwright() as p:
        # Launch with anti-detection args
        browser = p.chromium.launch(
            headless=True,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--no-sandbox',
                '--disable-setuid-sandbox'
            ]
        )
        
        # Create context with user-agent
        context = browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            viewport={'width': 1920, 'height': 1080}
        )
        
        page = context.new_page()
        
        # Apply stealth to hide automation
        stealth(page)
        
        # Hide webdriver property
        page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

        try:
            print("正在访问主页: https://searcade.com/en/")
            page.goto("https://searcade.com/en/", wait_until="networkidle")

            login_link_selector = 'a:has-text("Login")'
            print(f"正在点击登录链接: {login_link_selector}")
            page.wait_for_selector(login_link_selector, timeout=30000)
            page.click(login_link_selector)

            # 等待 Userveria 页面加载
            print("正在等待 Userveria 登录流程页面加载...")
            page.wait_for_url("**userveria.com**", timeout=30000)
            
            # 额外等待 Cloudflare 挑战完成（通常几秒）
            time.sleep(5)  # 给 Cloudflare JS 检查时间
            page.wait_for_load_state('networkidle', timeout=60000)

            # 第一步：邮箱输入页面
            email_input_selector = 'input[type="email"], input[placeholder="mail@example.com"], input[name="email"]'
            continue_button_selector = 'button:has-text("Continue with email"), button:has-text("Continue")'

            print("正在填写 Email...")
            page.wait_for_selector(email_input_selector, timeout=60000)
            page.fill(email_input_selector, username)  # username 就是 email
            page.click(continue_button_selector)
            
            # 等待进入密码页面
            time.sleep(2)
            password_input_selector = 'input[type="password"], input[name="password"]'
            login_button_selector = 'button:has-text("Login"), button:has-text("Sign in")'

            print("正在填写 Password...")
            page.wait_for_selector(password_input_selector, timeout=60000)
            page.fill(password_input_selector, password)
            print("正在点击登录按钮...")
            page.click(login_button_selector)

            # 处理可能的授权确认页面
            print("检查是否出现授权确认页面...")
            authorize_button_selector = 'button:has-text("Allow"), button:has-text("Authorize"), button:has-text("Continue"), button:has-text("Yes")'

            try:
                page.wait_for_selector(authorize_button_selector, timeout=10000)
                print("检测到授权确认页面，正在点击允许...")
                page.click(authorize_button_selector)
            except:
                print("无授权确认页面（可能已授权过），继续...")

            # 等待重定向回 Searcade 并登录成功
            print("正在等待重定向回 Searcade 主页...")
            page.wait_for_url("https://searcade.com/**", timeout=30000)
            time.sleep(2)  # 额外等待页面稳定

            # 登录成功指示器（调整为更可靠的，如注销按钮或用户相关文本）
            success_indicator_selector = 'text="Your servers", a:has-text("Logout"), text="Welcome back"'

            print(f"正在等待登录成功指示器: {success_indicator_selector}")
            try:
                page.wait_for_selector(success_indicator_selector, timeout=20000)
                print(f"账号 {username} 登录成功!")
            except:
                error_message_selector = '.alert.alert-danger, .error-message, .form-error, .alert, text="Invalid", text="incorrect"'
                print("未找到登录成功指示器，尝试查找错误消息...")
                try:
                    error_element = page.wait_for_selector(error_message_selector, timeout=5000)
                    if error_element:
                        error_text = error_element.inner_text().strip()
                        print(f"账号 {username} 登录失败: {error_text}")
                        page.screenshot(path=f"login_fail_{username.replace('@', '_').replace('.', '_')}.png")
                        raise RuntimeError(f"登录失败: {error_text}")
                    else:
                        print(f"账号 {username} 登录失败: 未找到成功指示器且未检测到特定错误消息。")
                        page.screenshot(path=f"login_mystery_fail_{username.replace('@', '_').replace('.', '_')}.png")
                        raise RuntimeError("登录失败: 状态不明确，未找到成功指示器。")
                except Exception as e_inner:
                    print(f"账号 {username} 登录失败: 未找到成功指示器，且查找错误消息失败。可能的原因: {e_inner}")
                    page.screenshot(path=f"login_error_lookup_fail_{username.replace('@', '_').replace('.', '_')}.png")
                    raise RuntimeError(f"登录失败: 无法确认成功或错误。")
        except Exception as e:
            print(f"处理账号 {username} 时发生错误: {e}")
            page.screenshot(path=f"process_error_{username.replace('@', '_').replace('.', '_')}.png")
            raise RuntimeError(f"登录操作中断: {e}")
        finally:
            browser.close()

if __name__ == "__main__":
    accounts_str = os.environ.get('SEARCADE_ACCOUNTS', '')
    if not accounts_str:
        print("环境变量 'SEARCADE_ACCOUNTS' 未设置或为空。请设置账号信息。")
        exit(1)

    accounts = accounts_str.split()
    any_account_failed = False

    for account in accounts:
        try:
            username, password = account.split(':', 1)
            login_searcade(username, password)
            print(f"账号 {username} 处理完成。")
        except ValueError:
            print(f"账号信息格式错误: {account}。应为 'username:password'")
            any_account_failed = True
        except RuntimeError as e:
            print(f"账号 {username} 处理失败: {e}")
            any_account_failed = True

    if any_account_failed:
        print("部分或所有账号处理失败，退出码为 1。")
        exit(1)
    else:
        print("所有账号均已成功处理。")
        exit(0)

def login_searcade(username, password):
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=False,  # 关键：必须关闭 headless
            args=['--disable-blink-features=AutomationControlled']
        )
        
        context = browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )
        page = context.new_page()

        try:
            print("正在访问主页: https://searcade.com/en/")
            page.goto("https://searcade.com/en/", wait_until="domcontentloaded")
            
            # 等待 Cloudflare 验证完成（最多30秒）
            print("等待 Cloudflare 验证...")
            page.wait_for_timeout(10000)  # 先等10秒
            
            # 后续代码保持不变...
