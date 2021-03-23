#! /usr/bin/env python
# -*- coding: utf-8 -*-

from appium import webdriver
import os
import time


class OneStrokeTest:

    def __init__(self, device_name, platform_version, port):
        app_path = os.path.join(os.getcwd(), 'yibijizhang.apk')
        self.device_name = device_name
        self.deseried_caps = {
            'automationName': 'uiAutomator1',
            'platformName': 'Android',
            'platformVersion': platform_version,
            'deviceName': self.device_name,
            'appPackage': 'com.mobivans.onestrokecharge',
            'appActivity': 'com.stub.stub01.Stub01',
            'app': app_path,
            'unicodeKeyboard': 'true'
        }
        self.url = f'http://127.0.0.1:{port}/wd/hub'

    def start_test(self):
        driver = webdriver.Remote(self.url, self.deseried_caps)
        driver.implicitly_wait(60)
        try:
            # 注意text属性本来应该用find_element_by_name，但是现在版本的appium这个方法支持有问题，不可用
            # 所以我们使用find_element_by_android_uiautomator方法，其中写的是android内置测试框架uiAutomator
            # 的java代码，所以这里必须注意引号的用法外单内双，不能反过来。
            driver.find_element_by_android_uiautomator('text("记一笔")').click()
            driver.scroll(driver.find_element_by_android_uiautomator('text("医疗")'),
                          driver.find_element_by_android_uiautomator('text("餐饮")'),
                          1000)
            driver.find_element_by_android_uiautomator('text("书籍")').click()
            editor = driver.find_element_by_id('add_et_remark')
            editor.clear()
            editor.send_keys('购买学习书籍。')
            driver.find_element_by_id('keyb_btn_2').click()
            driver.find_element_by_id('keyb_btn_3').click()
            driver.find_element_by_id('keyb_btn_9').click()
            driver.find_element_by_id('keyb_btn_finish').click()
            driver.find_element_by_android_uiautomator('text("长按记录可删除")').click()
            remarks = driver.find_elements_by_id('account_item_txt_remark')
            money = driver.find_elements_by_id('account_item_txt_money')
            if remarks[0].text == '购买学习书籍。' and money[0].text == '-239':
                print('test success.')
            else:
                print('test fail.')
        except Exception as e:
            with open(f'./report/{self.device_name}_error.log', 'w') as f:
                f.write(str(e))
            # now = time.strftime('%Y%m%d%H%M%S')
            now = int(time.time())
            driver.get_screenshot_as_file(f'./report/{self.device_name}_{now}.png')
        finally:
            driver.quit()
        print('script over.')


if __name__ == '__main__':
    OneStrokeTest('emulator-5554', '5.0.2', 4723).start_test()
