import json
import time

# --- [도구 1: 시각화 - 모든 사이즈 대응] ---
def visualize_matrix(matrix, title="Pattern Visualization"):
    size = len(matrix)
    print(f"\n{'='*20}")
    print(f" {title} ({size}x{size})")
    print(f"{'='*20}")
    
    for row in matrix:
        # 대형 행렬일수록 간격을 좁게 해서 한눈에 들어오게 함
        # 0.5보다 크면 ■, 작으면 □
        line = "".join(["■" if val > 0.5 else "  " for val in row])
        print(line)
    print(f"{'='*20}\n")

# --- [도구 2: 신뢰도 계산] ---
def calculate_confidence(s_a, s_b):
    total = s_a + s_b
    if total == 0: return 0
    # 두 점수의 차이 비중을 백분율로 계산
    return (abs(s_a - s_b) / max(s_a, s_b)) * 100

def normalize_label(label):
    label = str(label).lower().strip()
    if label in ['t', 'cross', '+']: return "Cross"
    if label in ['x']: return "X"
    return label

def calculate_mac(matrix1, matrix2):
    score = 0.0
    for i in range(len(matrix1)):
        for j in range(len(matrix1)):
            score += matrix1[i][j] * matrix2[i][j]
    return score

def judge(score_a, score_b):
    epsilon = 1e-9
    if abs(score_a - score_b) < epsilon:
        return "UNDECIDED"
    return "Cross" if score_a > score_b else "X"

# --- [기능 1: 수동 입력] ---
def run_manual_mode():
    print("\n[Mode 1] Manual Input (3x3)")
    
    def get_safe_input(size):
        mat = []
        print(f"Enter {size}x{size} matrix (row by row):")
        while len(mat) < size:
            try:
                row = list(map(float, input(f"Row {len(mat)+1}: ").split()))
                if len(row) != size:
                    print(f"Error: Please enter exactly {size} numbers.")
                    continue
                mat.append(row)
            except ValueError:
                print("Error: Numbers only.")
        return mat

    filter_a = get_safe_input(3)
    filter_b = get_safe_input(3)
    pattern = get_safe_input(3)

    visualize_matrix(pattern, "Manual Input Pattern")
    
    s_a = calculate_mac(filter_a, pattern)
    s_b = calculate_mac(filter_b, pattern)
    res = judge(s_a, s_b)
    conf = calculate_confidence(s_a, s_b)
    
    print(f"Result: {res} (Confidence: {conf:.1f}%)")

# --- [기능 2: JSON 모드 (대형 데이터 시각화 포함)] ---
def run_json_mode():
    print("\n[Mode 2] JSON Batch Processing")
    try:
        with open('data.json', 'r') as f:
            data = json.load(f)
    except Exception as e:
        print(f"File Load Error: {e}")
        return

    filters = data['filters']
    patterns = data['patterns']
    
    for p_id, p_info in patterns.items():
        try:
            # ID에서 사이즈 추출 (예: test_13_1 -> 13)
            size = int(p_id.split('_')[1])
            f_key = f"size_{size}"
            p_mat = p_info['input']
            expected = normalize_label(p_info['expected'])
            
            # MAC 연산 및 성능 측정
            start_time = time.perf_counter()
            s_cross = calculate_mac(filters[f_key]['cross'], p_mat)
            s_x = calculate_mac(filters[f_key]['x'], p_mat)
            end_time = time.perf_counter()
            
            elapsed = (end_time - start_time) * 1000 # ms 단위
            
            final_res = judge(s_cross, s_x)
            conf = calculate_confidence(s_cross, s_x)
            status = "PASS" if final_res == expected else "FAIL"
            
            # 시각화 출력 (모든 사이즈 출력)
            visualize_matrix(p_mat, f"Pattern: {p_id}")
            
            print(f"▶ Analysis Result: {final_res} (Expected: {expected}) -> {status}")
            print(f"▶ Confidence: {conf:.1f}%")
            print(f"▶ Processing Time: {elapsed:.4f} ms")
            print("-" * 40)

        except KeyError:
            print(f"Skip: Filter for size_{size} not found.")

def main():
    while True:
        print("\n========================================")
        print("   MAC Pattern Recognition System v2.0")
        print("========================================")
        print("1. Manual Input Mode (3x3)")
        print("2. JSON Batch Mode (All Sizes)")
        print("3. Exit")
        choice = input("Select: ")
        if choice == '1': run_manual_mode()
        elif choice == '2': run_json_mode()
        elif choice == '3': break

if __name__ == "__main__":
    main()