import os
import logging
import preprocess, train, evaluate
from config import DATA_DIR, MODEL_DIR, LOG_DIR

def setup_logging():
    """
    设置日志配置。
    如果日志目录不存在，则创建它。
    配置日志记录器，将日志信息写入到 'process.log' 文件中。
    """
    # 检查日志目录是否存在，如果不存在则创建
    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR)
    
    # 配置基本的日志设置
    logging.basicConfig(filename=os.path.join(LOG_DIR, 'process.log'), # 日志文件路径
                        level=logging.INFO, # 记录INFO级别及以上的信息
                        format='%(asctime)s - %(levelname)s - %(message)s') # 日志格式

def main():
    """
    主函数， orchestrates the entire snore detection pipeline:
    1. 设置日志。
    2. 执行数据预处理。
    3. 执行模型训练。
    4. 执行模型评估。
    每个步骤都包含错误处理和日志记录。
    """
    # 调用 setup_logging 函数初始化日志系统
    setup_logging()
    
    # 记录预处理步骤开始的信息
    logging.info("Starting the preprocessing step.")
    try:
        # 调用 preprocess 模块中的 preprocess_data 函数进行数据预处理
        preprocess.preprocess_data()
        # 记录预处理成功完成的信息
        logging.info("Preprocessing completed successfully.")
    except Exception as e:
        # 如果预处理过程中发生错误，记录错误信息并退出
        logging.error(f"Error during preprocessing: {e}")
        return
    
    # 记录训练步骤开始的信息
    logging.info("Starting the training step.")
    try:
        train.train_model()
        logging.info("Training completed successfully.")
    except Exception as e:
        logging.error(f"Error during training: {e}")
        return
    
    # 记录评估步骤开始的信息
    logging.info("Starting the evaluation step.")
    try:
        evaluate.evaluate_model()
        logging.info("Evaluation completed successfully.")
    except Exception as e:
        logging.error(f"Error during evaluation: {e}")
        return

if __name__ == "__main__":
    main()
