import time
from io import BytesIO
from PIL import Image
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class CrackBilibili(object):
    """破解Biblibili极验验证码    
    """

    def __init__(self, username, password):
        self.url = 'https://passport.bilibili.com/login'
        self.browser = webdriver.Chrome()
        self.wait = WebDriverWait(self.browser, 20)
        self.username = username
        self.password = password

    def __del__(self):
        time.sleep(15)
        self.browser.close()

    def open(self):
        """打开网页,输入用户名和密码
        """
        self.browser.get(self.url)
        username = self.wait.until(EC.presence_of_element_located((By.ID, "login-username")))
        password = self.wait.until(EC.presence_of_element_located((By.ID, "login-passwd")))
        username.send_keys(self.username)
        password.send_keys(self.password)

    def show_img(self):
        """鼠标悬停,显示极验图片
        """
        div_element = self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, "gt_slider")))
        ActionChains(self.browser).move_to_element(div_element).perform()

    def get_screenshot(self):
        """
        获取网页截图
        :return: 截图对象
        """
        screenshot = self.browser.get_screenshot_as_png()
        screenshot = Image.open(BytesIO(screenshot))
        return screenshot

    def get_position(self):
        """获取图片所在标签的位置信息        
        Returns:返回截图区域信息, 类似于CSS中的位置描述
        """
        img = self.wait.until(EC.presence_of_element_located((By.XPATH, "//div[@class='gt_cut_fullbg gt_show']")))
        time.sleep(2)
        location = img.location
        size = img.size
        top, bottom, left, right = location['y'], location['y'] + size['height'], location['x'], location['x'] + size[
            'width']
        return (top, bottom, left, right)

    def get_image(self, name='captcha.png'):
        """根据位置信息,通过截图获取验证码图片
        :return: 图片对象
        """
        top, bottom, left, right = self.get_position()
        print('验证码位置', top, bottom, left, right)  # 验证码图片位置 224 340 535 795 长=260，宽=116
        screenshot = self.get_screenshot()
        captcha = screenshot.crop((left, top, right, bottom))
        captcha.save(name)
        return captcha

    def get_slider(self):
        """获取滑块
        :return: 滑块对象
        """
        slider = self.wait.until(EC.element_to_be_clickable((By.XPATH, "//div[@class='gt_slider_knob gt_show']")))
        return slider

    def get_gap(self, image1, image2):
        """通过对比像素点,获取缺口偏移量, 起始位置left设为58~70均可, 是为了正好跳过前面拖动的缺口位置, 从而找到后面的拼图缺口,计算大致偏移量,如果移动偏移量过于准确,会提示图片被怪兽吃掉了!
        :param image1: 不带缺口图片
        :param image2: 带缺口图片
        :return: 偏移量的大小
        """
        print("Image Size:", image1.size)  # Image Size: (260, 116)
        left = 65
        for i in range(left, image1.size[0]):  # range(65, 260)
            for j in range(image1.size[1]):  # range(116)
                if not self.is_pixel_equal(image1, image2, i, j):
                    left = i
                    return left
        print(left)
        return left

    def is_pixel_equal(self, image1, image2, x, y):
        """
        判断两个像素是否相同
        :param image1: 图片1
        :param image2: 图片2
        :param x: 位置x0
        :param y: 位置y
        :return: 像素是否相同(每个像素点的RGB值之差小于60,则认为它们相同)
        """
        # 取两个图片的像素点
        pixel1 = image1.load()[x, y]
        pixel2 = image2.load()[x, y]
        # threshold = 58
        threshold = 40
        if abs(pixel1[0] - pixel2[0]) < threshold and abs(pixel1[1] - pixel2[1]) < threshold and abs(
                pixel1[2] - pixel2[2]) < threshold:
            return True
        else:
            return False

    def get_track(self, distance):
        """根据偏移量获取移动的轨迹列表,主要是模拟人的操作行为,先加速后减速,将每个次move的值用列表存起来,move的总和与偏移量相等
        :param distance: 偏移量
        :return: 移动轨迹
        """
        # 移动轨迹, 即每次移动的距离,为一个列表,总和等于偏移量
        track = []
        # 当前位移, 也即记录当前移动了多少距离
        current = 0
        # 减速阈值, 也即开始减速的位置,这里设置为偏移量的4/5处开始减速,可以更改
        mid = distance * 4 / 5
        # 计算用的时间间隔
        t = 0.3
        # 初始速度
        v = 0

        while current < distance:
            if current < mid:
                # 当前位移小于4/5的偏移量时,加速度为2
                a = 2
            else:
                # 当前位移大于4/5的偏移量时,加速度为-3
                a = -3
            # 初始速度v0
            v0 = v
            # 本次移动完成之后的速度v = v0 + at
            v = v0 + a * t
            # 本次移动距离x = v0t + 1/2 * a * t^2
            move = v0 * t + 1 / 2 * a * t * t
            # 当前位移, 这里都将move四舍五入取整
            current += round(move)
            # 将move的距离放入轨迹列表
            track.append(round(move))

        print("轨迹列表:", track)
        return track

    def move_slider(self, slider, track):
        """根据轨迹列表,拖动滑块到缺口处
        :param slider: 滑块
        :param track: 轨迹
        """
        ActionChains(self.browser).click_and_hold(slider).perform()
        for x in track:
            ActionChains(self.browser).move_by_offset(xoffset=x, yoffset=0).perform()
        time.sleep(0.5)
        ActionChains(self.browser).release().perform()

    def login(self):
        """点击登录按钮
        """
        time.sleep(0.5)
        login = self.wait.until(EC.element_to_be_clickable((By.XPATH, "//a[@class='btn btn-login']")))
        login.click()
        # time.sleep(3)
        print('登录成功')

    def run_spider(self):
        # 打开网页,传入用户名和密码
        self.open()
        # 鼠标悬停,显示图片
        self.show_img()
        # 获取无缺口验证码截图,保存
        img_1 = self.get_image(name='img1.png')
        # 获取滑块对象
        slider = self.get_slider()
        # 点击滑块对象,显示有缺口的验证码图片
        slider.click()
        # 等待6秒, 让点击之后出现提示消失, 方便截图
        time.sleep(3)
        # 获取有缺口的验证码截图,保存
        img_2 = self.get_image(name='img2.png')
        # 获取偏移量大小
        gap = self.get_gap(img_1, img_2)
        print('偏移量:', gap)

        # 根据偏移量的值, 计算移动轨迹, 得到轨迹列表, 传入的偏移量可以适当修正, 比如gap-6
        track = self.get_track(gap-5)
        # print("轨迹列表:", track)

        # 根据轨迹列表, 移动滑块
        self.move_slider(slider, track)
        # 点击登录按钮
        self.login()


def main():
    username = '826956010@qq.com'
    password = 'hu200901959'
    crack_bilibili = CrackBilibili(username, password)
    crack_bilibili.run_spider()


if __name__ == '__main__':
    main()
