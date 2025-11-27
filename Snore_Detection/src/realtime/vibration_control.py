"""
振动控制模块
提供不同平台的振动控制接口（PC、树莓派、Arduino等）
"""

import platform
import time


class VibrationController:
    """振动控制器基类"""
    
    def __init__(self):
        self.is_vibrating = False
    
    def vibrate(self, duration=0.5, intensity=1.0):
        """
        触发振动
        
        Args:
            duration: 振动时长（秒）
            intensity: 振动强度（0-1）
        """
        raise NotImplementedError("子类必须实现 vibrate 方法")
    
    def stop(self):
        """停止振动"""
        raise NotImplementedError("子类必须实现 stop 方法")


class RaspberryPiVibrationController(VibrationController):
    """树莓派GPIO控制振动器"""
    
    def __init__(self, pin=18):
        """
        初始化树莓派振动控制器
        
        Args:
            pin: GPIO引脚号（默认18）
        """
        super().__init__()
        self.pin = pin
        try:
            import RPi.GPIO as GPIO
            self.GPIO = GPIO
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(pin, GPIO.OUT)
            self.pwm = GPIO.PWM(pin, 1000)  # 1000Hz PWM频率
            self.pwm.start(0)
            print(f"树莓派振动控制器已初始化 (GPIO {pin})")
        except ImportError:
            print("警告: 未安装RPi.GPIO库，将使用模拟模式")
            self.GPIO = None
            self.pwm = None
    
    def vibrate(self, duration=0.5, intensity=1.0):
        """触发振动"""
        if self.GPIO is None:
            print(f"[模拟] 振动 {duration} 秒，强度: {intensity}")
            time.sleep(duration)
            return
        
        try:
            self.is_vibrating = True
            duty_cycle = int(intensity * 100)  # 转换为PWM占空比（0-100）
            self.pwm.ChangeDutyCycle(duty_cycle)
            time.sleep(duration)
            self.stop()
        except Exception as e:
            print(f"振动控制错误: {e}")
    
    def stop(self):
        """停止振动"""
        self.is_vibrating = False
        if self.pwm:
            self.pwm.ChangeDutyCycle(0)


class ArduinoVibrationController(VibrationController):
    """Arduino串口控制振动器"""
    
    def __init__(self, port='COM3', baudrate=9600):
        """
        初始化Arduino振动控制器
        
        Args:
            port: 串口名称（Windows: 'COM3', Linux: '/dev/ttyUSB0'）
            baudrate: 波特率
        """
        super().__init__()
        self.port = port
        self.baudrate = baudrate
        self.serial = None
        
        try:
            import serial
            self.serial = serial.Serial(port, baudrate, timeout=1)
            time.sleep(2)  # 等待Arduino初始化
            print(f"Arduino振动控制器已初始化 (端口: {port})")
        except ImportError:
            print("警告: 未安装pyserial库，将使用模拟模式")
        except Exception as e:
            print(f"警告: 无法连接到Arduino: {e}，将使用模拟模式")
    
    def vibrate(self, duration=0.5, intensity=1.0):
        """触发振动"""
        if self.serial is None:
            print(f"[模拟] 振动 {duration} 秒，强度: {intensity}")
            time.sleep(duration)
            return
        
        try:
            self.is_vibrating = True
            # 发送命令到Arduino (格式: "V,duration*1000,intensity*255\n")
            command = f"V,{int(duration*1000)},{int(intensity*255)}\n"
            self.serial.write(command.encode())
            time.sleep(duration)
            self.stop()
        except Exception as e:
            print(f"振动控制错误: {e}")
    
    def stop(self):
        """停止振动"""
        self.is_vibrating = False
        if self.serial:
            self.serial.write(b"S\n")  # 发送停止命令


class SimulatedVibrationController(VibrationController):
    """模拟振动控制器（用于测试）"""
    
    def vibrate(self, duration=0.5, intensity=1.0):
        """模拟振动"""
        print(f"[模拟] 🔔 振动提醒: 持续时间 {duration} 秒，强度 {intensity:.2f}")
        time.sleep(duration)
    
    def stop(self):
        """停止振动"""
        pass


def create_vibration_controller(controller_type='auto'):
    """
    创建振动控制器实例
    
    Args:
        controller_type: 控制器类型 ('raspberrypi', 'arduino', 'simulated', 'auto')
                        'auto'会根据系统自动选择
    
    Returns:
        VibrationController实例
    """
    if controller_type == 'auto':
        system = platform.system().lower()
        if 'linux' in system:
            # 尝试树莓派
            try:
                with open('/proc/cpuinfo') as f:
                    if 'Raspberry Pi' in f.read():
                        controller_type = 'raspberrypi'
                    else:
                        controller_type = 'simulated'
            except:
                controller_type = 'simulated'
        else:
            controller_type = 'simulated'
    
    if controller_type == 'raspberrypi':
        return RaspberryPiVibrationController()
    elif controller_type == 'arduino':
        return ArduinoVibrationController()
    else:
        return SimulatedVibrationController()


if __name__ == "__main__":
    # 测试振动控制器
    print("测试振动控制器...")
    
    controller = create_vibration_controller('simulated')
    
    print("触发3次振动测试:")
    for i in range(3):
        controller.vibrate(duration=0.5, intensity=0.8)
        time.sleep(1)

