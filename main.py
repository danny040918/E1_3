import json
import time

# --- [보완 #5, #6, #17: 라벨 매핑 및 모드별 정책] ---
LABEL_MAP = {
    "cross": "십자가(Cross)",
    "x": "X자(X)",
    "tie": "UNDECIDED"  # [보완 #6] 동점 시 표준 출력값
}

def normalize_label(label):
    label = str(label).lower().strip()
    if label in ['t', 'cross', '+', '십자가']: 
        return LABEL_MAP["cross"]
    if label in ['x', '엑스']: 
        return LABEL_MAP["x"]
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
    score = 0.0
    for i in range(len(matrix1)):
        for j in range(len(matrix1)):
            score += matrix1[i][j] * matrix2[i][j]
    return score

def judge(score_a, score_b, mode="auto"):
    """
    [보완 #17] 모드별 동점 정책 분리
    - mode="manual": 사용자에게 직관적인 '판정 불가' 메시지 제공
    - mode="auto": 시스템 일관성을 위한 'UNDECIDED' 상수 제공
    """
    epsilon = 1e-9
    if abs(score_a - score_b) < epsilon:
        return "판정 불가(동점)" if mode == "manual" else LABEL_MAP["tie"]
    return LABEL_MAP["cross"] if score_a > score_b else LABEL_MAP["x"]

# --- [보완 #7: 성능 분석 기능] ---
def run_performance_analysis():
    print("\n[모드 3] 크기별 성능 분석 (10회 반복 평균)")
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

# --- [기능 1: 수동 모드] ---
def run_manual_mode():
    print("\n[모드 1] 3x3 수동 입력 분석")
    def get_input(s):
        m = []
        while len(m) < s:
            try:
                r = list(map(float, input(f"{len(m)+1}행: ").split()))
                if len(r) == s: m.append(r)
            except: pass
        return m
    f_a = get_input(3); f_b = get_input(3); p = get_input(3)
    start = time.perf_counter()
    s_a, s_b = calculate_mac(f_a, p), calculate_mac(f_b, p)
    elapsed = (time.perf_counter() - start) * 1000
    res = judge(s_a, s_b, mode="manual")
    print(f"\n▶ 결과: {res} | 점수: A={s_a:.2f}, B={s_b:.2f} | 시간: {elapsed:.4f}ms")

# --- [기능 2: JSON 모드 (보완 #6, #8 반영)] ---
def run_json_mode():
    print("\n[모드 2] JSON 데이터 일괄 분석")
    try:
        with open('data.json', 'r', encoding='utf-8') as f: data = json.load(f)
    except: return print("파일 없음")

    total, pass_c = 0, 0
    failed_cases = [] # [보완 #8] 실패 케이스 목록 저장

    for p_id, p_info in data['patterns'].items():
        size = len(p_info['input'])
        f_key = f"size_{size}"
        if f_key not in data['filters']: continue

        total += 1
        s_c = calculate_mac(data['filters'][f_key]['cross'], p_info['input'])
        s_x = calculate_mac(data['filters'][f_key]['x'], p_info['input'])
        
        res = judge(s_c, s_x, mode="auto")
        expected = normalize_label(p_info['expected'])
        
        # [보완 #6] 동점(UNDECIDED)은 실패로 집계
        if res == LABEL_MAP["tie"]:
            status = "❌ FAIL (UNDECIDED)"
            failed_cases.append(f"{p_id} (사유: 동점/판정불가)")
        elif res == expected:
            status = "✅ PASS"
            pass_c += 1
        else:
            status = "❌ FAIL (MISMATCH)"
            failed_cases.append(f"{p_id} (사유: 결과 불일치)")
        
        print(f"[{p_id}] 판정: {res:12} | 상태: {status}")

    # [보완 #8] 최종 요약 출력
    print("\n" + "="*50)
    print(f" [ 분석 요약 ] 총: {total} | 통과: {pass_c} | 실패: {len(failed_cases)}")
    if failed_cases:
        print("-" * 50)
        print(" [ 실패 케이스 목록 ]")
        for case in failed_cases: print(f" - {case}")
    print("="*50)

def main():
    while True:
        print("\nMAC 시스템 v2.6")
        print("1.수동 | 2.JSON | 3.성능분석 | 4.종료")
        c = input("선택: ")
        if c == '1': run_manual_mode()
        elif c == '2': run_json_mode()
        elif c == '3': run_performance_analysis()
        elif c == '4': break

if __name__ == "__main__":
    main()