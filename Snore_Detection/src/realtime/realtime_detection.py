"""
实时呼噜声检测模块
用于实时采集音频、进行推理并触发振动提醒
"""

import os
import sys
# 添加src目录到路径，以便导入config模块
# 当前文件在 src/realtime/realtime_detection.py，需要导入 src/config.py
realtime_dir = os.path.dirname(os.path.abspath(__file__))  # src/realtime
src_dir = os.path.dirname(realtime_dir)  # src
sys.path.insert(0, src_dir)

import numpy as np
import pyaudio
import librosa
from collections import deque
from tensorflow.keras.models import load_model
from config import SR, N_MFCC, N_MELS, TIME_STEPS  # 只导入常量，不导入路径
import threading
import time


class RealtimeSnoreDetector:
    """实时呼噜声检测器类"""
    
    def __init__(self, model_path, chunk_duration=1.0, overlap=0.5, 
                 vibration_callback=None, threshold=0.5):
        """
        初始化实时检测器
        
        Args:
            model_path: 模型文件路径
            chunk_duration: 每次处理的音频时长（秒）
            overlap: 窗口重叠比例（0-1）
            vibration_callback: 检测到呼噜声时的回调函数（用于触发振动）
            threshold: 预测阈值，超过此值认为是呼噜声
        """
        self.model = load_model(model_path)
        self.chunk_duration = chunk_duration
        self.overlap = overlap
        self.vibration_callback = vibration_callback
        self.threshold = threshold
        
        # 音频参数
        self.chunk_size = int(SR * chunk_duration)
        self.hop_size = int(SR * chunk_duration * (1 - overlap))
        self.format = pyaudio.paFloat32
        self.channels = 1
        
        # 音频缓冲区
        self.audio_buffer = deque(maxlen=int(SR * 3))  # 保存3秒音频
        
        # 状态控制
        self.is_running = False
        self.audio_stream = None
        self.pyaudio_instance = None
        
        # 连续检测计数（避免误触发）
        self.snore_count = 0
        self.snore_threshold_count = 3  # 连续3次检测到才触发
        
    def extract_features(self, audio_data):
        """
        从音频数据中提取特征
        
        Args:
            audio_data: 音频数组
            
        Returns:
            预处理后的特征数组
        """
        # 提取MFCC特征
        mfcc_features = librosa.feature.mfcc(y=audio_data, sr=SR, n_mfcc=N_MFCC)
        
        # 提取Mel频谱特征
        mel_features = librosa.feature.melspectrogram(y=audio_data, sr=SR, n_mels=N_MELS)
        
        # 合并特征
        combined_features = np.concatenate((mfcc_features, mel_features), axis=0)
        
        # 归一化
        mean = np.mean(combined_features)
        std = np.std(combined_features)
        if std > 0:
            normalized_features = (combined_features - mean) / std
        else:
            normalized_features = combined_features
        
        # 调整时间步长度
        if normalized_features.shape[1] != TIME_STEPS:
            if normalized_features.shape[1] < TIME_STEPS:
                pad_width = TIME_STEPS - normalized_features.shape[1]
                normalized_features = np.pad(
                    normalized_features, 
                    ((0, 0), (0, pad_width)), 
                    mode='constant'
                )
            else:
                normalized_features = normalized_features[:, :TIME_STEPS]
        
        return np.expand_dims(normalized_features, axis=0)
    
    def predict(self, audio_data):
        """
        对音频数据进行预测
        
        Args:
            audio_data: 音频数组
            
        Returns:
            预测概率（0-1之间，接近0表示是呼噜声，接近1表示非呼噜声）
            注意：模型训练时 label 0=呼噜声，label 1=非呼噜声
        """
        features = self.extract_features(audio_data)
        prediction = self.model.predict(features, verbose=0)
        return prediction[0][0]
    
    def process_audio_chunk(self, audio_chunk):
        """
        处理音频块
        
        Args:
            audio_chunk: 音频数据块
        """
        if len(audio_chunk) < self.chunk_size:
            # 如果音频太短，进行填充
            audio_chunk = np.pad(
                audio_chunk, 
                (0, self.chunk_size - len(audio_chunk)), 
                mode='constant'
            )
        
        # 进行预测
        prediction = self.predict(audio_chunk)
        # 注意：模型训练时 label 0=呼噜声，label 1=非呼噜声
        # 模型输出：接近0 = 呼噜声，接近1 = 非呼噜声
        # 所以判断呼噜声的逻辑应该是：预测值 < (1 - threshold)
        # 例如：threshold=0.5，则 prediction < 0.5 时认为是呼噜声
        is_snore = prediction < (1 - self.threshold)
        
        # 更新计数
        if is_snore:
            self.snore_count += 1
        else:
            self.snore_count = 0
        
        # 触发振动（连续检测到多次才触发，避免误报）
        if self.snore_count >= self.snore_threshold_count:
            if self.vibration_callback:
                self.vibration_callback()
            self.snore_count = 0  # 重置计数
        
        return prediction, is_snore
    
    def audio_callback(self, in_data, frame_count, time_info, status):
        """
        音频流回调函数
        
        Args:
            in_data: 输入的音频数据
            frame_count: 帧数
            time_info: 时间信息
            status: 状态信息
            
        Returns:
            (None, pyaudio.paContinue) 表示继续录音
        """
        if status:
            print(f"音频流状态: {status}")
        
        # 将字节数据转换为numpy数组
        audio_data = np.frombuffer(in_data, dtype=np.float32)
        
        # 添加到缓冲区
        self.audio_buffer.extend(audio_data)
        
        return (None, pyaudio.paContinue)
    
    def start_detection(self):
        """开始实时检测"""
        if self.is_running:
            print("检测器已经在运行中")
            return
        
        self.is_running = True
        self.pyaudio_instance = pyaudio.PyAudio()
        
        # 列出可用的音频设备（用于调试）
        print("\n可用音频输入设备:")
        try:
            for i in range(self.pyaudio_instance.get_device_count()):
                info = self.pyaudio_instance.get_device_info_by_index(i)
                if info['maxInputChannels'] > 0:
                    print(f"  设备 {i}: {info['name']} (默认: {info['defaultSampleRate']} Hz)")
        except:
            pass
        
        # 打开音频流（使用阻塞模式以提高实时性）
        print(f"\n正在打开音频流 (采样率: {SR} Hz)...")
        try:
            self.audio_stream = self.pyaudio_instance.open(
                format=self.format,
                channels=self.channels,
                rate=SR,
                input=True,
                frames_per_buffer=self.hop_size,
                start=False  # 手动启动
            )
        except Exception as e:
            print(f"❌ 无法打开音频流: {e}")
            print("请检查麦克风是否已连接并允许访问")
            self.is_running = False
            return
        
        # 启动音频流
        self.audio_stream.start_stream()
        print("✓ 音频流已启动\n")
        
        # 实时处理循环
        print("="*60)
        print("开始实时呼噜声监控...")
        print("="*60)
        print("提示: 按 Ctrl+C 停止监控\n")
        
        last_process_time = time.time()
        frame_count = 0
        
        try:
            while self.is_running:
                # 从音频流读取数据
                try:
                    audio_data_bytes = self.audio_stream.read(self.hop_size, exception_on_overflow=False)
                    audio_data = np.frombuffer(audio_data_bytes, dtype=np.float32)
                    
                    # 添加到缓冲区
                    self.audio_buffer.extend(audio_data)
                    
                    # 当缓冲区有足够数据时进行处理
                    if len(self.audio_buffer) >= self.chunk_size:
                        # 获取最近1秒的音频数据
                        audio_chunk = np.array(list(self.audio_buffer)[-self.chunk_size:])
                        prediction, is_snore = self.process_audio_chunk(audio_chunk)
                        
                        # 显示实时状态
                        frame_count += 1
                        current_time = time.time()
                        elapsed = current_time - last_process_time
                        
                        # 构建状态显示
                        # 将预测值转换为呼噜声概率（更直观）
                        # prediction接近0表示呼噜声，接近1表示非呼噜声
                        snore_probability = 1 - prediction  # 转换为呼噜声概率
                        status_icon = "🔴" if is_snore else "🟢"
                        status_text = "检测到呼噜声！" if is_snore else "正常"
                        snore_indicator = f"[连续: {self.snore_count}/{self.snore_threshold_count}]" if is_snore else ""
                        
                        print(f"\r{status_icon} 时间: {frame_count * self.chunk_duration * (1-self.overlap):.1f}s | "
                              f"呼噜声概率: {snore_probability:.3f} | {status_text} {snore_indicator}", 
                              end='', flush=True)
                        
                        # 如果检测到呼噜声且达到阈值，显示提醒
                        if self.snore_count == self.snore_threshold_count:
                            print(f"\n🔔 触发振动提醒！预测值: {prediction:.3f}")
                        
                        last_process_time = current_time
                
                except Exception as e:
                    print(f"\n⚠️ 音频处理错误: {e}")
                    time.sleep(0.1)
                    continue
                
                # 小延迟，避免CPU占用过高
                time.sleep(0.01)
                
        except KeyboardInterrupt:
            print("\n\n⚠️ 检测被用户中断")
        except Exception as e:
            print(f"\n❌ 运行时错误: {e}")
        finally:
            self.stop_detection()
    
    def stop_detection(self):
        """停止检测"""
        self.is_running = False
        
        if self.audio_stream:
            self.audio_stream.stop_stream()
            self.audio_stream.close()
        
        if self.pyaudio_instance:
            self.pyaudio_instance.terminate()
        
        print("\n实时检测已停止")


def vibration_alert():
    """振动提醒函数（需要根据实际硬件实现）"""
    print("\n🔔 检测到呼噜声！触发振动提醒...")
    # 这里可以添加实际的硬件控制代码
    # 例如：控制GPIO引脚、发送命令到串口等


if __name__ == "__main__":
    # 计算项目根目录和模型路径
    project_root = os.path.dirname(os.path.dirname(src_dir))  # Snore_Detection
    models_dir = os.path.join(project_root, 'models')
    model_path = os.path.join(models_dir, 'final_snore_detection_model.h5')
    
    if not os.path.exists(model_path):
        print(f"错误: 模型文件不存在: {model_path}")
        print("请先训练模型或检查模型路径")
        exit(1)
    
    # 创建检测器
    detector = RealtimeSnoreDetector(
        model_path=model_path,
        chunk_duration=1.0,  # 1秒窗口
        overlap=0.5,  # 50%重叠
        vibration_callback=vibration_alert,
        threshold=0.5  # 预测阈值
    )
    
    # 开始检测
    detector.start_detection()

