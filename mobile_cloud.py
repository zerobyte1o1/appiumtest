#! /usr/bin/env python
# -*- coding: utf-8 -*-

import os
import time
import socket
import threading

from training.class43.CBT.CloudTest.onestroketest import OneStrokeTest


class MobileCloud:

    # 获取当前系统的设备信息
    def get_device_info(self):
        port = 5000
        bp_port = 8000
        # 利用adb devices命令获取当前系统的设备列表
        devices = os.popen('adb devices').read().strip().splitlines()
        # 剔除首行的无用信息
        devices.pop(0)
        infors = []
        for device in devices:
            device_name = device.split('\t')[0].strip()
            # 利用adb -s 设备名 shell getprop ro.build.version.release命令获取指定设备的版本号
            platform_version = os.popen(f'adb -s {device_name} shell getprop'
                                        f' ro.build.version.release').read().strip()
            # 分别查找当前系统可用的端口号
            port = self.find_port(port)
            bp_port = self.find_port(bp_port)
            # 把已经准备好的设备信息以元组的形式添加到设备列表中
            infors.append((device_name, platform_version, port, bp_port))
            # 这里切记不可漏掉下面的加1动作
            port += 1
            bp_port += 1
        return infors

    # 定义一个查找当前系统可用端口的方法。
    def find_port(self, port):
        while self.check_port(port):
            port += 1
        return port

    # 定义一个检查指定端口是否占用的方法，占用返回True，否则返回Flase。
    def check_port(self, port):
        # 构造一个socket连接对象，注意使用的是tcp连接方式
        con = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            # connectex和connect方法一样都是去连接指定ip端口，但是前者是有返回值的，而后者没有返回值
            # connectex返回值是0，代表连接成功，如果不是0，代表连接错误
            # connect方法没有返回值，如果连接不成功就会抛出socket.error的错误，否则就不会有错误抛出。
            con.connect(('127.0.0.1', port))
            con.shutdown(socket.SHUT_RDWR)
            return True
        except socket.error:
            return False

    # 构造appium server启动的命令
    # appium -p port -bp bp_port --device-name device_name --platform-version platform_version
    #  --log log_file --log-level info --log-timestamp
    def start_appium(self, device_name, platform_version, port, bp_port):
        log_file = os.path.join(os.getcwd(), f'report/{device_name}_appium.log')
        cmd = f'appium -p {port} -bp {bp_port} --device-name {device_name}' \
              f' --platform-version {platform_version} --log {log_file} --log-level info' \
              f' --log-timestamp'
        os.system(cmd)

    def start_test(self):
        devices = self.get_device_info()
        threads = []
        for index, device in enumerate(devices):
            ost = OneStrokeTest(*device[:3])
            # 注意这里一定不要掉错了方法，client线程要调用测试脚本的测试方法
            # server线程要调用appium server启动的方法
            client_thread = threading.Thread(target=ost.start_test, name=f'client-{index}')
            server_thread = threading.Thread(target=self.start_appium, args=(*device,),
                                             name=f'server-{index}')
            threads.append(server_thread)
            threads.append(client_thread)
        # 当前的线程顺序是
        # server-0, client-0, server-1, client-1, ……, server-n, client-n
        # 想要把线程顺序调整为
        # server-0, server-1, ……, server-n, client-0, client-1, ……, client-n
        threads.sort(key=lambda t: t.getName()[:1], reverse=True)
        # 优先启动appium server的线程，确保测试脚本线程后启动
        # 设置appium server线程为守护线程的目的是在主线程执行结束的时候，能跟随主线程一起结束
        for t in threads:
            if t.getName() == 'client-0':
                time.sleep(30)
            # 设置守护线程，只要主线程运行结束，这个线程就可以结束了。
            t.setDaemon(True)
            t.start()
        # 设置测试脚本线程阻塞的目的是要保证所有的测试脚本线程执行完毕，主线程才可以结束。
        for t in threads:
            if t.getName().startswith('client'):
                # 设置线程阻塞，目的是确保主线程必须等待所有的测试脚本线程执行完毕方可结束
                t.join()
        # 杀掉可能存在的node.exe进程，避免下次运行appium server不能正常启动。
        os.system('taskkill /f /im node.exe')
        print('************ 全部测试完成 *************')


if __name__ == '__main__':
    MobileCloud().start_test()
