import yaml
import os
from pathlib import Path

# Danh sách các file cần sửa
FILES_TO_FIX = [
    'cfg/training/yolov7_cbam.yaml',
    'cfg/training/yolov7_eca.yaml',
    'cfg/training/yolov7_ca.yaml'
]

# Vị trí bạn đã chèn module Attention (Sau layer 50)
# Nghĩa là module mới nằm ở index 51.
# Tất cả các layer từ 51 trở đi trong file gốc giờ sẽ bị đẩy lên +1.
INSERT_POSITION = 50 

def fix_yolo_yaml(file_path):
    path = Path(file_path)
    if not path.exists():
        print(f"❌ Không tìm thấy file: {file_path}")
        return

    print(f"\n🔧 Đang xử lý file: {file_path}...")
    
    with open(path, 'r') as f:
        data = yaml.safe_load(f)

    # Kiểm tra xem cấu trúc có đúng chuẩn YOLO không
    if 'head' not in data:
        print("⚠️ File không có mục 'head'. Bỏ qua.")
        return

    new_head = []
    changed_count = 0

    # Duyệt qua từng layer trong phần HEAD
    for i, layer in enumerate(data['head']):
        # Cấu trúc layer: [from, number, module, args]
        # layer[0] chính là "from" (địa chỉ nguồn)
        source = layer[0]
        new_source = source

        # Trường hợp 1: source là một list các số (Ví dụ: [75, 88, 101] hoặc [-1, 63])
        if isinstance(source, list):
            temp_source = []
            for item in source:
                # Chỉ sửa những số dương (absolute index) lớn hơn vị trí chèn
                if isinstance(item, int) and item > INSERT_POSITION:
                    temp_source.append(item + 1)
                    changed_count += 1
                else:
                    temp_source.append(item)
            new_source = temp_source

        # Trường hợp 2: source là một số nguyên dương duy nhất (ít gặp nhưng vẫn check)
        elif isinstance(source, int) and source > INSERT_POSITION:
            new_source = source + 1
            changed_count += 1

        # Cập nhật lại layer
        layer[0] = new_source
        new_head.append(layer)

    # Gán lại head mới
    data['head'] = new_head

    # Lưu đè lại file
    with open(path, 'w') as f:
        # Dùng sort_keys=False để giữ thứ tự dòng
        yaml.dump(data, f, sort_keys=False, default_flow_style=None)
    
    if changed_count > 0:
        print(f"✅ Đã sửa thành công! (Cập nhật {changed_count} chỉ số index)")
    else:
        print("ℹ️ Không tìm thấy chỉ số nào cần sửa (Có thể file đã đúng sẵn).")

# --- CHẠY CHƯƠNG TRÌNH ---
if __name__ == "__main__":
    print(f"🚀 Bắt đầu sửa lỗi Index Shift (Vị trí chèn: sau layer {INSERT_POSITION})")
    for file_name in FILES_TO_FIX:
        fix_yolo_yaml(file_name)
    print("\n🏁 Hoàn tất! Bạn hãy kiểm tra lại file và push lên GitHub.")