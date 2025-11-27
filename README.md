## This project is focused on detecting snoring sounds from audio recordings using machine learning techniques. The dataset includes labeled audio samples of snoring and non-snoring sounds, and the project involves preprocessing the audio data, extracting features, training a machine learning model, evaluating its performance, and real-time detection with vibration alerts.

## Project Structure

The project is structured as follows:
===========================================================================================================
```
├── data/
│   ├── 0/  # Folder containing non-snoring audio files
│   ├── 1/  # Folder containing snoring audio files
│   ├── train/  # Training data (created by the script)
│   │   ├── snoring/
│   │   └── non-snoring/
│   └── test/  # Testing data (created by the script)
│       ├── snoring/
│       └── non-snoring/
├── models/  # Saved models
├── inference_audios # For storing test audios
├── src/
│   ├── logs/  # Training logs
│   ├── preprocess.py  # Data preprocessing script
│   ├── feature_extraction.py  # Feature extraction script
│   ├── train.py  # Model training script
│   ├── evaluate.py  # Model evaluation script
│   ├── inference.py  # Single audio inference script
│   ├── utils.py  # Utility functions
│   ├── config.py  # Configuration settings
│   ├── model.py  # Model architecture
│   ├── split_dataset.py  # Script to split dataset into training and testing
│   └── realtime/  # Real-time detection module
│       ├── realtime_detection.py  # Core real-time detection class
│       ├── realtime_main.py  # Full-featured real-time detection program
│       ├── start_monitoring.py  # Quick start script for real-time monitoring
│       └── vibration_control.py  # Vibration control module (supports Raspberry Pi, Arduino, etc.)
├── README.md  # Project documentation
└── requirements.txt
===========================================================================================================
```

### Dataset
The dataset consists of two folders:

data/1/: Contains 500 snoring audio files, each 1 second long.
data/0/: Contains 500 non-snoring audio files, each 1 second long. These include background sounds like baby crying, clock ticking, door opening, etc.

Dataset Sources
The snoring sounds were collected from the following online sources:

- Soundsnap - Snoring
- Zapsplat - Snoring
- Fesliyan Studios - Snoring
- YouTube - Snoring

### Project Workflow

1. Data Preprocessing
The first step is to split the dataset into training and testing sets. The script split_dataset.py handles this task:
==> python src/split_dataset.py

2. Feature Extraction
The MFCC (Mel-Frequency Cepstral Coefficients) features are extracted from the audio files. This is done using the preprocess.py and feature_extraction.py scripts.
==> python src/preprocess.py
This script will:

- Load the audio files.
- Extract MFCC features.
- Split the data into training and validation sets.
- Save the processed data in .npz files for training and validation.

3. Model Training
The train.py script is used to train a neural network on the preprocessed data.
==> python src/train.py
During training, the model weights that achieve the best validation loss are saved to the models/ directory. The training process is monitored using callbacks like ModelCheckpoint and EarlyStopping.

4. Model Evaluation
Once the model is trained, it can be evaluated on the test data using the evaluate.py script.
==> python src/evaluate.py
This script loads the saved model and evaluates its performance using metrics like accuracy, precision, recall, and F1-score.

5. Single Audio Inference
After training, individual audio files can be tested to infer whether the audio contains snoring or not.
==> python src/inference.py

6. Real-Time Detection
The project now includes a real-time detection system that can monitor audio input from a microphone and trigger vibration alerts when snoring is detected.

Method 1: Quick Start (Recommended for first-time users)
==> python src/realtime/start_monitoring.py
This script uses default parameters and is the easiest way to start real-time monitoring.

Method 2: Full-Featured Program
==> python src/realtime/realtime_main.py --vibration-controller simulated
This program supports all configuration options via command-line arguments.

### Real-Time Detection Features:
- Real-time audio capture from microphone
- Continuous snoring detection using the trained model
- Vibration alerts when snoring is detected (supports Raspberry Pi GPIO, Arduino, or simulated mode)
- Configurable detection threshold and sensitivity
- Sliding window processing with overlap for smooth detection
- Continuous detection counting to reduce false positives

### Real-Time Detection Parameters:
- --threshold: Prediction threshold (0-1, default 0.5)
- --chunk-duration: Audio window duration in seconds (default 1.0)
- --overlap: Window overlap ratio (0-1, default 0.5)
- --min-snore-count: Number of consecutive detections required to trigger alert (default 3)
- --vibration-controller: Controller type ('raspberrypi', 'arduino', 'simulated', 'auto')
- --vibration-duration: Vibration duration in seconds (default 0.5)
- --vibration-intensity: Vibration intensity (0-1, default 0.8)

____________________________________________________________________

A pipeline main.py can also be used to run all the programs at once. But, currently, its not functional so, try to run every program manually.
____________________________________________________________________

### Configuration
All configuration settings (e.g., paths, audio processing parameters, training parameters) are stored in config.py. You can modify this file to change the sample rate, number of MFCCs, batch size, number of epochs, learning rate, and other settings.

How to Use

1. Clone the Repository: Clone the project repository to your local machine.
   git clone <Not yet specified>

2. Install Dependencies: Install the necessary Python packages.
   pip install -r requirements.txt

3. Organize Your Dataset: Place your audio files in the data/1 and data/0 directories.

4. Split the Dataset: Run the split_dataset.py script to organize the data into training and testing sets.
   ==> python src/split_dataset.py

5. Preprocess the Data: Extract MFCC features and prepare the data for training.
   ==> python src/preprocess.py

6. Train the Model: Train the model using the processed data.
   ==> python src/train.py

7. Evaluate the Model: Evaluate the trained model on the test set.
   ==> python src/evaluate.py

8. Real-Time Detection: Start real-time monitoring (requires trained model).
   ==> python src/realtime/start_monitoring.py
   
   Or with custom parameters:
   ==> python src/realtime/realtime_main.py --threshold 0.6 --chunk-duration 0.5 --vibration-controller simulated

### Real-Time Detection Setup:

For Raspberry Pi:
- Install RPi.GPIO library: pip install RPi.GPIO
- Connect vibration motor to GPIO pin 18 (or specify custom pin)
- Run: python src/realtime/realtime_main.py --vibration-controller raspberrypi

For Arduino:
- Upload vibration control sketch to Arduino
- Connect Arduino via USB
- Install pyserial: pip install pyserial
- Run: python src/realtime/realtime_main.py --vibration-controller arduino --port COM3

For Testing (Simulated Mode):
- No hardware required
- Run: python src/realtime/start_monitoring.py
- Or: python src/realtime/realtime_main.py --vibration-controller simulated

### Results
The final model performance will be printed after running the evaluate.py script. This includes metrics like accuracy, precision, recall, and F1-score.

For real-time detection, the system displays:
- Real-time status indicators (🟢 normal, 🔴 snoring detected)
- Snoring probability values
- Continuous detection count
- Vibration trigger notifications





