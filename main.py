import json
import time

# --- [도구 1: 시각화] ---
def visualize_matrix(matrix, title="패턴 모양"):
    print(f"\n<{title}>")
    for row in matrix:
        # 0.5보다 크면 색칠된 칸(■), 작으면 빈 칸(□)
        line = "".join(["■ " if val > 0.5 else "□ " for val in row])
        print(line)

# --- [도구 2: 신뢰도 계산] ---
def calculate_confidence(s_a, s_b):
    total = s_a + s_b
    if total == 0: return 0
    # 두 점수의 차이가 전체에서 차지하는 비중을 계산
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

def measure_performance(filter_a, filter_b, pattern):
    iterations = 10
    start = time.perf_counter()
    for _ in range(iterations):
        calculate_mac(filter_a, pattern)
        calculate_mac(filter_b, pattern)
    end = time.perf_counter()
    return ((end - start) / iterations) * 1000

# --- [기능 1: 수동 입력 (예외 처리 강화)] ---
def run_manual_mode():
    print("\n--- [모드 1] 3x3 수동 입력 ---")
    
    def get_safe_input(size):
        mat = []
        print(f"{size}x{size} 행렬을 입력하세요 (한 줄에 {size}개씩 숫자 입력):")
        while len(mat) < size:
            try:
                row = list(map(float, input(f"{len(mat)+1}행: ").split()))
                if len(row) != size:
                    print(f"오류: {size}개의 숫자를 입력해야 합니다.")
                    continue
                mat.append(row)
            except ValueError:
                print("오류: 숫자만 입력 가능합니다.")
        return mat

    filter_a = get_safe_input(3)
    filter_b = get_safe_input(3)
    pattern = get_safe_input(3)

    visualize_matrix(pattern, "입력된 패턴 시각화")
    
    s_a = calculate_mac(filter_a, pattern)
    s_b = calculate_mac(filter_b, pattern)
    res = judge(s_a, s_b)
    conf = calculate_confidence(s_a, s_b)
    
    print(f"\n결과: {res} (신뢰도: {conf:.1f}%)")

# --- [기능 2: JSON 모드 (시각화 추가)] ---
def run_json_mode():
    print("\n--- [모드 2] JSON 데이터 분석 ---")
    try:
        with open('data.json', 'r') as f:
            data = json.load(f)
    except Exception as e:
        print(f"파일 로드 실패: {e}")
        return

    filters = data['filters']
    patterns = data['patterns']
    
    for p_id, p_info in patterns.items():
        try:
            size = int(p_id.split('_')[1])
            f_key = f"size_{size}"
            p_mat = p_info['input']
            expected = normalize_label(p_info['expected'])
            
            s_cross = calculate_mac(filters[f_key]['cross'], p_mat)
            s_x = calculate_mac(filters[f_key]['x'], p_mat)
            final_res = judge(s_cross, s_x)
            conf = calculate_confidence(s_cross, s_x)
            
            status = "✅ PASS" if final_res == expected else "❌ FAIL"
            
            print(f"\n[{p_id}] 판정: {final_res} | 정답: {expected} -> {status}")
            print(f"   (점수차: {abs(s_cross-s_x):.2f}, 신뢰도: {conf:.1f}%)")
            
            # 5x5 이하만 시각화 (너무 크면 터미널이 지저분해짐)
            if size <= 5:
                visualize_matrix(p_mat, f"{p_id} 시각화")

        except KeyError:
            print(f"[{p_id}] 필터 데이터가 없습니다 (size_{size})")

def main():
    while True:
        print("\n[MAC 패턴 판정 시스템 고도화 버전]")
        print("1. 수동 입력 모드")
        print("2. JSON 일괄 처리 모드")
        print("3. 종료")
        choice = input("선택: ")
        if choice == '1': run_manual_mode()
        elif choice == '2': run_json_mode()
        elif choice == '3': break

if __name__ == "__main__":
    main()