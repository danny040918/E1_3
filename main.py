import json
import time

# --- [보완 #5, #6, #17: 라벨 매핑 및 모드별 정책 정의] ---
LABEL_MAP = {
    "cross": "십자가(Cross)",
    "x": "X자(X)",
    "tie": "UNDECIDED"  # [보완 #6] 자동 분석 시 동점 표준 라벨
}

def normalize_label(label):
    """[보완 #5] 입력된 라벨을 표준 라벨로 변환"""
    label = str(label).lower().strip()
    if label in ['t', 'cross', '+', '십자가']: return LABEL_MAP["cross"]
    if label in ['x', '엑스']: return LABEL_MAP["x"]
    return label

# --- [도구 1: 시각화] ---
def visualize_matrix(matrix, title="패턴 시각화"):
    size = len(matrix)
    print(f"\n{'='*30}\n [ {title} ({size}x{size}) ]\n{'='*30}")
    for row in matrix:
        line = "".join(["■ " if val > 0.5 else "□ " for val in row])
        print(line)
    print(f"{'='*30}")

# --- [도구 2: 연산 및 판정 로직] ---
def calculate_mac(matrix1, matrix2):
    """
    [보완 #14: 해석 기준 명시]
    - MAC 점수는 두 행렬의 유사도를 측정하는 지표입니다.
    - 두 행렬의 패턴이 일치할수록 곱의 합산인 MAC 점수가 커집니다.
    - 즉, 'MAC 점수 증가 = 패턴 유사성 증가'를 의미합니다.
    """
    score = 0.0
    for i in range(len(matrix1)):
        for j in range(len(matrix1)):
            score += matrix1[i][j] * matrix2[i][j]
    return score

def calculate_confidence(s_a, s_b):
    total = s_a + s_b
    if total == 0: return 0
    return (abs(s_a - s_b) / max(s_a, s_b)) * 100

def judge(score_a, score_b, mode="auto"):
    """[보완 #17] 모드별 동점 정책 분리"""
    epsilon = 1e-9
    if abs(score_a - score_b) < epsilon:
        return "판정 불가(동점)" if mode == "manual" else LABEL_MAP["tie"]
    return LABEL_MAP["cross"] if score_a > score_b else LABEL_MAP["x"]

# --- [기능 1: 수동 입력 모드 (보완 #1 반영)] ---
def run_manual_mode():
    print("\n[모드 1] 3x3 수동 입력 분석")
    def get_safe_input(size):
        mat = []
        print(f"{size}x{size} 데이터를 입력하세요 (한 줄에 {size}개씩):")
        while len(mat) < size:
            try:
                row = list(map(float, input(f"{len(mat)+1}행: ").split()))
                if len(row) == size: mat.append(row)
                else: print(f"오류: {size}개를 입력해야 합니다.")
            except ValueError: print("오류: 숫자만 입력 가능합니다.")
        return mat

    f_a = get_safe_input(3)
    f_b = get_safe_input(3)
    pattern = get_safe_input(3)

    start_time = time.perf_counter()
    s_a = calculate_mac(f_a, pattern)
    s_b = calculate_mac(f_b, pattern)
    elapsed_ms = (time.perf_counter() - start_time) * 1000
    
    res = judge(s_a, s_b, mode="manual")
    conf = calculate_confidence(s_a, s_b)
    
    visualize_matrix(pattern, "입력된 패턴")
    print("-" * 45)
    print(f"▶ 필터 A 점수: {s_a:.4f} | 필터 B 점수: {s_b:.4f}")
    print(f"▶ 연산 소요 시간: {elapsed_ms:.4f} ms")
    print(f"▶ 최종 판정: {res} (신뢰도: {conf:.1f}%)")
    print("-" * 45)

# --- [기능 2: JSON 모드 (보완 #6, #8, #18 반영)] ---
def run_json_mode():
    print("\n[모드 2] JSON 데이터 일괄 분석")
    try:
        with open('data.json', 'r', encoding='utf-8') as f: data = json.load(f)
    except FileNotFoundError: return print("오류: data.json 파일이 없습니다.")

    total, pass_c = 0, 0
    failed_cases = []

    for p_id, p_info in data['patterns'].items():
        size = len(p_info['input'])
        f_key = f"size_{size}"
        if f_key not in data['filters']: continue

        total += 1
        
        # [Step 1: 정규화 (Normalization)] - 보완 #18
        expected = normalize_label(p_info['expected'])
        
        # [Step 2: 판정 (Judgment)]
        s_c = calculate_mac(data['filters'][f_key]['cross'], p_info['input'])
        s_x = calculate_mac(data['filters'][f_key]['x'], p_info['input'])
        res = judge(s_c, s_x, mode="auto")
        
        # [Step 3: 출력 (Output)]
        if res == LABEL_MAP["tie"]:
            status = "❌ FAIL (UNDECIDED)"
        elif res == expected:
            status = "✅ PASS"
        else:
            status = "❌ FAIL (MISMATCH)"
        print(f"[{p_id}] 예상: {expected:12} | 판정: {res:12} | 상태: {status}")

        # [Step 4: 테스트 및 집계 (Test/Validation)]
        if status == "✅ PASS":
            pass_c += 1
        else:
            failed_cases.append(f"{p_id} (결과: {res}, 정답: {expected})")

    # [보완 #8] 전체 요약 출력
    print("\n" + "="*50)
    print(f" [ 분석 요약 ] 총: {total} | 통과: {pass_c} | 실패: {len(failed_cases)}")
    if failed_cases:
        print("-" * 50)
        print(" [ 실패 케이스 상세 ]")
        for case in failed_cases: print(f" - {case}")
    print("="*50)

# --- [기능 3: 성능 분석 (보완 #7 반영)] ---
def run_performance_analysis():
    print("\n[모드 3] 크기별 성능 분석 (10회 평균)")
    sizes = [3, 5, 13, 25]
    print("-" * 60)
    print(f"{'행렬 크기':^10} | {'N^2 (연산 수)':^15} | {'평균 시간 (ms)':^15}")
    print("-" * 60)
    for n in sizes:
        f, p = [[0.5]*n for _ in range(n)], [[0.8]*n for _ in range(n)]
        start = time.perf_counter()
        for _ in range(10): calculate_mac(f, p)
        avg_ms = ((time.perf_counter() - start) / 10) * 1000
        print(f"{n:2} x {n:<2}      | {n*n:15,d} | {avg_ms:15.6f}")
    print("-" * 60)

def main():
    while True:
        print("\n" + "="*45)
        print("   MAC 패턴 인식 시스템 v2.7 (최종 통합본)")
        print("="*45)
        print("1. 수동 입력 모드 (3x3)")
        print("2. JSON 일괄 처리 모드")
        print("3. 크기별 성능 분석")
        print("4. 프로그램 종료")
        print("="*45)
        choice = input("선택: ")
        if choice == '1': run_manual_mode()
        elif choice == '2': run_json_mode()
        elif choice == '3': run_performance_analysis()
        elif choice == '4': break

if __name__ == "__main__":
    main()