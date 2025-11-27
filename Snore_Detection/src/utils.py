import os
import librosa
import numpy as np

def load_audio_files(directory, file_extension='.wav'):
    """
    从指定目录加载音频文件。

    参数:
    - directory (str): 包含音频文件的目录路径。
    - file_extension (str): 用于过滤的文件扩展名（默认为'.wav'）。

    返回:
    - list: 音频文件的完整路径列表。
    """
    audio_files = [] # 初始化一个空列表来存储找到的音频文件路径
    # 遍历指定目录及其所有子目录
    for root, _, files in os.walk(directory):
        for file in files:
            # 检查文件是否以指定的扩展名结尾
            if file.endswith(file_extension):
                audio_files.append(os.path.join(root, file))
    return audio_files # 返回所有找到的音频文件路径列表

def extract_mfcc(file_path=None, sr=16000, n_mfcc=13, y=None):
    """
    从音频文件或音频数据中提取梅尔频率倒谱系数（MFCC）。
    MFCC 是一种把“声音波形”变成一小串数字的特征表示，这串数字更接近人耳听觉感知方式；
    
    参数:
    - file_path (str, optional): 音频文件的路径。如果提供了y，则可以为None。
    - sr (int, optional): 音频的采样率（默认为16000 Hz）。
    - n_mfcc (int, optional): 要提取的MFCC数量（默认为13）。
    - y (np.ndarray, optional): 预加载的音频时间序列。如果提供了file_path，则可以为None。

    返回:
    - np.ndarray: 提取的MFCC特征。

    抛出:
    - ValueError: 如果既未提供file_path也未提供y。
    """
    if y is not None:
        # 如果直接提供了音频数据y，则直接从y中提取MFCC
        mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=n_mfcc)
    elif file_path is not None:
        # 如果提供了文件路径，则加载音频文件并提取MFCC
        y, sr = librosa.load(file_path, sr=sr) # 加载音频文件
        mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=n_mfcc) # 提取MFCC
    else:
        raise ValueError("Either file_path or y must be provided")
    return mfcc


# Example update to extract_mel_spectrogram
def extract_mel_spectrogram(file_path=None, sr=16000, y=None):
    """
    从音频文件或音频数据中提取梅尔频谱图。

    参数:
    - file_path (str, optional): 音频文件的路径。如果提供了y，则可以为None。
    - sr (int, optional): 音频的采样率（默认为16000 Hz）。
    - y (np.ndarray, optional): 预加载的音频时间序列。如果提供了file_path，则可以为None。

    返回:
    - np.ndarray: 提取的梅尔频谱图特征。

    抛出:
    - ValueError: 如果既未提供file_path也未提供y。
    """
    if y is not None:
        # 如果直接提供了音频数据y，则直接从y中提取梅尔频谱图
        mel_spectrogram = librosa.feature.melspectrogram(y=y, sr=sr)
    elif file_path is not None:
        # 如果提供了文件路径，则加载音频文件并提取梅尔频谱图
        y, sr = librosa.load(file_path, sr=sr) # 加载音频文件
        mel_spectrogram = librosa.feature.melspectrogram(y=y, sr=sr) # 提取梅尔频谱图
    else:
        raise ValueError("Either file_path or y must be provided")
    return mel_spectrogram


def normalize_features(features):
    """
    对特征进行归一化，使其具有零均值和单位方差（Z-score归一化）。

    参数:
    - features (numpy array): 需要归一化的特征数组。

    返回:
    - numpy array: 归一化后的特征数组。
    """
    # 计算特征的均值和标准差，然后应用Z-score归一化公式
    return (features - np.mean(features)) / np.std(features)
