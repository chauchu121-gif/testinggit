def one_hot_encode(num, num_classes):
    # Kiểm tra xem số num có hợp lệ không
    if num >= num_classes:
        print(f"Lỗi: Vị trí {num} vượt quá số lớp {num_classes}!")
        return None # Hoặc trả về vector toàn số 0
    
    vector = [0] * num_classes
    vector[num] = 1
    return vector

# Thử nghiệm:
print(one_hot_encode(3, 4)) 
# Kết quả: Lỗi: Vị trí 5 vượt quá số lớp 4! None