import os # 导入os模块，用于文件路径操作
import numpy as np # 导入numpy库，用于数值计算和数组操作
import librosa # 导入librosa库，用于音频分析和处理
from sklearn.model_selection import train_test_split # 从sklearn导入train_test_split，用于数据集划分
from utils import extract_mfcc, extract_mel_spectrogram, normalize_features # 从utils模块导入自定义的特征提取和归一化函数
from config import TRAIN_DATA_DIR, TEST_DATA_DIR, SR, N_MFCC, N_MELS, HOP_LENGTH, AUGMENTATION, TIME_STEPS, NOISE_FACTOR # 从config模块导入配置参数

def preprocess_file(file, label):
    """
    预处理单个音频文件，提取MFCC和Mel频谱特征，并进行归一化和形状调整。
    Args:
        file (str): 音频文件的路径。
        label (int): 音频文件对应的标签。
        
    Returns:
        tuple: 包含处理后的特征数组和标签，如果特征提取失败则返回(None, None)。
    """
    # 提取MFCC特征
    mfcc_features = extract_mfcc(file, SR, N_MFCC)
    # 提取Mel频谱特征
    mel_features = extract_mel_spectrogram(file, SR)

    # 检查特征是否成功提取
    if mfcc_features is None or mel_features is None:
        print(f"Failed to extract features from file: {file}")
        return None, None

    # 将MFCC特征和Mel频谱特征沿轴0（行）拼接起来
    combined_features = np.concatenate((mfcc_features, mel_features), axis=0)
    # 对组合后的特征进行归一化
    normalized_features = normalize_features(combined_features)

    # 确保特征的第二维度（时间步）与TIME_STEPS一致，通过填充或截断实现
    if normalized_features.shape[1] != TIME_STEPS:
        if normalized_features.shape[1] < TIME_STEPS:
            # 如果特征的时间步小于TIME_STEPS，则进行零填充
            pad_width = TIME_STEPS - normalized_features.shape[1]
            normalized_features = np.pad(normalized_features, ((0, 0), (0, pad_width)), mode='constant')
        else:
            # 如果特征的时间步大于TIME_STEPS，则进行截断
            normalized_features = normalized_features[:, :TIME_STEPS]

    return normalized_features, label # 返回处理后的特征和标签

def preprocess_data():
    """
    主数据预处理函数，遍历数据集，提取特征，进行数据增强（如果启用），
    然后将数据划分为训练集、验证集和测试集，并保存为npz文件。
    """
    features = [] # 用于存储所有提取的特征
    labels = [] # 用于存储所有对应的标签

    # 遍历'snoring'和'non-snoring'子目录，为它们分配标签0和1
    for label, subdir in enumerate(['snoring', 'non-snoring']):
        subdir_path = os.path.join(TRAIN_DATA_DIR, subdir) # 构建当前子目录的完整路径
        # 遍历子目录中的所有文件
        for file in os.listdir(subdir_path):
            # 只处理.wav音频文件
            if file.endswith('.wav'):
                file_path = os.path.join(subdir_path, file) # 构建音频文件的完整路径
                # 预处理原始音频文件
                feature, current_label = preprocess_file(file_path, label) # 注意这里使用current_label避免与循环变量label混淆
                
                # 如果特征提取成功，则添加到列表中
                if feature is not None:
                    features.append(feature)
                    labels.append(current_label)

                # 如果启用了数据增强
                if AUGMENTATION:
                    y, _ = librosa.load(file_path, sr=SR) # 加载音频数据

                    # 定义数据增强技术：时间拉伸、添加噪声、音高偏移
                    augmentations = [
                        librosa.effects.time_stretch(y, rate=0.8), # 时间拉伸，速率0.8
                        y + NOISE_FACTOR * np.random.randn(len(y)), # 添加高斯噪声
                        librosa.effects.pitch_shift(y, sr=SR, n_steps=2) # 音高偏移，上移2个半音
                    ]
                    
                    # 遍历每种增强后的音频数据
                    for augmented_y in augmentations:
                        # 提取增强后音频的MFCC特征 (直接传入y数据，file_path=None)
                        mfcc_aug = extract_mfcc(file_path=None, sr=SR, n_mfcc=N_MFCC, y=augmented_y)
                        # 提取增强后音频的Mel频谱特征 (直接传入y数据，file_path=None)
                        mel_aug = extract_mel_spectrogram(file_path=None, sr=SR, y=augmented_y)
                        
                        # 检查增强特征是否成功提取
                        if mfcc_aug is None or mel_aug is None:
                            print(f"Failed to extract augmented features for file: {file}")
                            continue

                        # 拼接和归一化增强后的特征
                        combined_aug = np.concatenate((mfcc_aug, mel_aug), axis=0)
                        normalized_aug = normalize_features(combined_aug)
            
                        # 确保增强特征的形状与TIME_STEPS一致
                        if normalized_aug.shape[1] != TIME_STEPS:
                            if normalized_aug.shape[1] < TIME_STEPS:
                                pad_width = TIME_STEPS - normalized_aug.shape[1]
                                normalized_aug = np.pad(normalized_aug, ((0, 0), (0, pad_width)), mode='constant')
                            else:
                                normalized_aug = normalized_aug[:, :TIME_STEPS]
                        
                        # 将增强后的特征和标签添加到列表中
                        features.append(normalized_aug)
                        labels.append(current_label) # 增强数据使用与原始数据相同的标签
                        

    # 将特征和标签列表转换为NumPy数组
    features = np.array(features)
    labels = np.array(labels)

    # 第一次划分：将数据分为训练集和临时集（用于验证和测试）
    X_train, X_temp, y_train, y_temp = train_test_split(features, labels, test_size=0.3, random_state=42)
    # 第二次划分：将临时集进一步分为验证集和测试集
    X_val, X_test, y_val, y_test = train_test_split(X_temp, y_temp, test_size=0.5, random_state=42) # 0.5 * 0.3 = 0.15，所以验证集和测试集各占总数据的15%
    
    # 将训练集、验证集和测试集保存为压缩的.npz文件
    np.savez_compressed(os.path.join(TRAIN_DATA_DIR, 'train_data.npz'), X_train=X_train, y_train=y_train)
    np.savez_compressed(os.path.join(TRAIN_DATA_DIR, 'val_data.npz'), X_val=X_val, y_val=y_val)
    np.savez_compressed(os.path.join(TEST_DATA_DIR, 'test_data.npz'), X_test=X_test, y_test=y_test)
    
    print("Data preprocessing and splitting completed successfully.") # 打印完成消息

if __name__ == "__main__":
    # 当脚本作为主程序运行时，执行数据预处理函数
    preprocess_data()