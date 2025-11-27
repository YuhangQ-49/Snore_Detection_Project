"""
快速启动实时监控脚本
简化版启动程序，方便快速开始监控
"""

import os
import sys

# 添加路径
realtime_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.dirname(realtime_dir)
project_root = os.path.dirname(src_dir)
sys.path.insert(0, src_dir)

from realtime_detection import RealtimeSnoreDetector
from vibration_control import create_vibration_controller

def main():
    """快速启动实时监控"""
    print("="*60)
    print("实时呼噜声监控系统 - 快速启动")
    print("="*60)
    
    # 检查模型文件
    models_dir = os.path.join(project_root, 'models')
    model_path = os.path.join(models_dir, 'final_snore_detection_model.h5')
    
    if not os.path.exists(model_path):
        print(f"\n❌ 错误: 模型文件不存在")
        print(f"路径: {model_path}")
        print("\n请先训练模型:")
        print("  python src/main.py")
        return
    
    print(f"\n✓ 找到模型: {model_path}")
    
    # 创建振动控制器（模拟模式）
    print("✓ 初始化振动控制器（模拟模式）...")
    vibration_controller = create_vibration_controller('simulated')
    
    # 定义振动回调
    def trigger_vibration():
        vibration_controller.vibrate(duration=0.5, intensity=0.8)
    
    # 创建检测器
    print("✓ 加载模型并初始化检测器...\n")
    detector = RealtimeSnoreDetector(
        model_path=model_path,
        chunk_duration=1.0,      # 1秒窗口
        overlap=0.5,             # 50%重叠
        vibration_callback=trigger_vibration,
        threshold=0.5            # 预测阈值
    )
    detector.snore_threshold_count = 3  # 连续3次检测到才触发
    
    print("="*60)
    print("系统配置:")
    print(f"  - 音频窗口: {detector.chunk_duration}秒")
    print(f"  - 窗口重叠: {detector.overlap*100}%")
    print(f"  - 预测阈值: {detector.threshold}")
    print(f"  - 触发条件: 连续{detector.snore_threshold_count}次检测到呼噜声")
    print("="*60)
    print("\n开始监控... (按 Ctrl+C 停止)\n")
    
    try:
        detector.start_detection()
    except KeyboardInterrupt:
        print("\n\n正在关闭...")
    finally:
        detector.stop_detection()
        print("监控已停止")

if __name__ == "__main__":
    main()

