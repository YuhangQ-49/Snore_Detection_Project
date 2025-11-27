# 实时监控使用指南

## 🚀 快速开始

### 方法一：使用快速启动脚本（推荐）

```bash
# 从项目根目录运行
cd Snore_Detection_Project/Snore_Detection
python src/realtime/start_monitoring.py
```

### 方法二：使用完整参数的主程序

```bash
# 从项目根目录运行
cd Snore_Detection_Project/Snore_Detection
python src/realtime/realtime_main.py --vibration-controller simulated
```

## 📋 使用说明

### 基本运行

实时监控系统会自动：
1. **检测麦克风** - 自动查找可用的音频输入设备
2. **实时采集音频** - 每秒采集和分析音频数据
3. **检测呼噜声** - 使用深度学习模型实时判断
4. **触发提醒** - 检测到呼噜声时触发振动（或模拟）

### 实时监控界面说明

运行时会显示实时状态：
```
🟢 时间: 1.5s | 预测: 0.123 | 正常
🔴 时间: 2.0s | 预测: 0.856 | 检测到呼噜声！ [连续: 2/3]
🔔 触发振动提醒！预测值: 0.923
```

- 🟢 **绿色圆点**: 正常状态（未检测到呼噜声）
- 🔴 **红色圆点**: 检测到呼噜声
- **预测值**: 0-1之间的概率，越高越可能是呼噜声
- **连续计数**: 连续检测到呼噜声的次数/触发阈值

### 参数调整

如果需要调整参数，使用主程序：

```bash
python src/realtime/realtime_main.py \
    --threshold 0.6 \                    # 提高阈值（更严格）
    --chunk-duration 0.5 \               # 减小窗口（更快响应）
    --overlap 0.7 \                      # 增加重叠（更平滑）
    --min-snore-count 5 \                # 增加触发次数（减少误报）
    --vibration-controller simulated
```

## ⚙️ 参数说明

| 参数 | 默认值 | 说明 | 建议值 |
|------|--------|------|--------|
| `--threshold` | 0.5 | 预测阈值（0-1），越高越严格 | 0.4-0.7 |
| `--chunk-duration` | 1.0 | 每次处理的音频时长（秒） | 0.5-2.0 |
| `--overlap` | 0.5 | 窗口重叠比例（0-1） | 0.3-0.7 |
| `--min-snore-count` | 3 | 连续检测次数阈值 | 3-5 |
| `--vibration-duration` | 0.5 | 振动持续时间（秒） | 0.3-1.0 |
| `--vibration-intensity` | 0.8 | 振动强度（0-1） | 0.5-1.0 |

## 🔧 故障排除

### 问题1：找不到麦克风

**症状**: 
```
❌ 无法打开音频流: NoDefaultInputDevice
```

**解决方案**:
1. 检查麦克风是否连接
2. 检查系统音频设置
3. 在Windows上，检查隐私设置中的麦克风权限

### 问题2：音频延迟太高

**解决方案**:
```bash
# 减小窗口大小和增加重叠
python src/realtime/realtime_main.py \
    --chunk-duration 0.5 \
    --overlap 0.7
```

### 问题3：误报太多

**解决方案**:
```bash
# 提高阈值和增加触发次数
python src/realtime/realtime_main.py \
    --threshold 0.7 \
    --min-snore-count 5
```

### 问题4：检测不灵敏

**解决方案**:
```bash
# 降低阈值和减少触发次数
python src/realtime/realtime_main.py \
    --threshold 0.4 \
    --min-snore-count 2
```

## 📊 性能优化建议

### 1. 降低延迟

- 使用更快的硬件（更好的CPU）
- 减小 `chunk-duration`（如0.5秒）
- 增加 `overlap`（如0.7）
- 优化模型（量化、剪枝）

### 2. 提高准确性

- 在真实环境中收集数据重新训练
- 调整阈值和连续计数参数
- 使用更好的麦克风
- 减少环境噪音

### 3. 降低CPU使用

- 增大 `chunk-duration`（如2.0秒）
- 减少 `overlap`（如0.3）
- 使用模型量化

## 💡 使用技巧

1. **首次运行**: 建议使用默认参数，观察检测效果
2. **调整参数**: 根据实际环境逐步调整阈值和触发条件
3. **长时间运行**: 建议测试至少1小时，观察稳定性和准确性
4. **真实环境**: 在实际睡眠环境中测试，收集反馈并优化

## 🔗 相关文档

- **硬件配置**: 查看 `HARDWARE_SETUP.md`
- **实施路线图**: 查看 `IMPLEMENTATION_ROADMAP.md`
- **快速启动**: 查看 `QUICKSTART.md`

## ❓ 常见问题

**Q: 监控会一直运行吗？**
A: 是的，会持续运行直到你按 Ctrl+C 停止。

**Q: 可以后台运行吗？**
A: 可以，使用 `nohup` (Linux) 或 `start` (Windows) 命令。

**Q: 如何查看日志？**
A: 实时状态会直接显示在终端。详细日志可以重定向到文件。

**Q: 需要网络连接吗？**
A: 不需要，所有处理都在本地完成。


