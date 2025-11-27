"""
实时呼噜声检测系统主程序
整合音频采集、实时推理和振动控制
"""

import os
import sys
# 添加src目录到路径，以便导入config模块和realtime模块
realtime_dir = os.path.dirname(os.path.abspath(__file__))  # .../src/realtime
src_dir = os.path.dirname(realtime_dir)                    # .../src
project_root = os.path.dirname(src_dir)  # Snore_Detection
sys.path.insert(0, src_dir)

if src_dir not in sys.path:    # 防止重复添加
    sys.path.insert(0, src_dir)

import argparse
# 导入realtime模块（从src/realtime目录导入）
from realtime_detection import RealtimeSnoreDetector
from vibration_control import create_vibration_controller

# 导入config常量（不需要路径变量）
from config import SR, N_MFCC, N_MELS, TIME_STEPS


def main():
    """主函数"""
    # 计算模型路径（基于项目根目录）
    models_dir = os.path.join(project_root, 'models')
    default_model_path = os.path.join(models_dir, 'final_snore_detection_model.h5')
    
    parser = argparse.ArgumentParser(description='实时呼噜声检测与振动提醒系统')
    parser.add_argument('--model', type=str, 
                       default=default_model_path,
                       help='模型文件路径')
    parser.add_argument('--threshold', type=float, default=0.5,
                       help='预测阈值（0-1，默认0.5）')
    parser.add_argument('--chunk-duration', type=float, default=1.0,
                       help='音频窗口时长（秒，默认1.0）')
    parser.add_argument('--overlap', type=float, default=0.5,
                       help='窗口重叠比例（0-1，默认0.5）')
    parser.add_argument('--vibration-controller', type=str, default='auto',
                       choices=['auto', 'raspberrypi', 'arduino', 'simulated'],
                       help='振动控制器类型')
    parser.add_argument('--vibration-duration', type=float, default=0.5,
                       help='振动持续时间（秒，默认0.5）')
    parser.add_argument('--vibration-intensity', type=float, default=0.8,
                       help='振动强度（0-1，默认0.8）')
    parser.add_argument('--min-snore-count', type=int, default=3,
                       help='连续检测到呼噜声的次数阈值（默认3次）')
    
    args = parser.parse_args()
    
    # 处理模型路径（如果是相对路径，转换为绝对路径）
    if not os.path.isabs(args.model):
        args.model = os.path.abspath(os.path.join(os.path.dirname(__file__), args.model))
    
    # 检查模型文件
    if not os.path.exists(args.model):
        print(f"❌ 错误: 模型文件不存在: {args.model}")
        print("请先训练模型或指定正确的模型路径")
        return
    
    # 创建振动控制器
    print(f"正在初始化振动控制器 ({args.vibration_controller})...")
    vibration_controller = create_vibration_controller(args.vibration_controller)
    
    # 定义振动回调函数
    def trigger_vibration():
        """触发振动的回调函数"""
        vibration_controller.vibrate(
            duration=args.vibration_duration,
            intensity=args.vibration_intensity
        )
    
    # 创建实时检测器
    print(f"正在加载模型: {args.model}")
    detector = RealtimeSnoreDetector(
        model_path=args.model,
        chunk_duration=args.chunk_duration,
        overlap=args.overlap,
        vibration_callback=trigger_vibration,
        threshold=args.threshold
    )
    detector.snore_threshold_count = args.min_snore_count
    
    print("\n" + "="*50)
    print("🚀 实时呼噜声检测系统已启动")
    print("="*50)
    print(f"模型路径: {args.model}")
    print(f"预测阈值: {args.threshold}")
    print(f"音频窗口: {args.chunk_duration}秒 (重叠{args.overlap*100}%)")
    print(f"振动设置: {args.vibration_duration}秒, 强度{args.vibration_intensity}")
    print(f"触发条件: 连续{args.min_snore_count}次检测到呼噜声")
    print("="*50)
    print("按 Ctrl+C 停止检测\n")
    
    try:
        # 开始实时检测
        detector.start_detection()
    except KeyboardInterrupt:
        print("\n\n正在关闭系统...")
    finally:
        detector.stop_detection()
        if hasattr(vibration_controller, 'stop'):
            vibration_controller.stop()
        print("系统已关闭")


if __name__ == "__main__":
    main()

