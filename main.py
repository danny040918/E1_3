import json
import time

# --- [도구 1: 라벨 정규화] ---
# 다양한 입력을 'Cross' 또는 'X'로 통일해요.
def normalize_label(label):
    label = str(label).lower().strip()
    if label in ['t', 'cross', '+']:
        return "Cross"
    if label in ['x']:
        return "X"
    return label

# --- [도구 2: MAC 연산] ---
# 외부 라이브러리 없이 반복문으로만 곱하고 더해요.
def calculate_mac(matrix1, matrix2):
    score = 0.0
    size = len(matrix1)
    for i in range(size):
        for j in range(size):
            score += matrix1[i][j] * matrix2[i][j]
    return score

# --- [도구 3: 점수 비교 및 판정] ---
# epsilon(아주 작은 수)을 사용해 동점인지 판정해요.
def judge(score_a, score_b):
    epsilon = 1e-9
    if abs(score_a - score_b) < epsilon:
        return "UNDECIDED"
    return "Cross" if score_a > score_b else "X"

# --- [도구 4: 성능 측정] ---
# 순수 연산만 10번 반복해서 평균 시간을 구해요.
def measure_performance(filter_a, filter_b, pattern):
    iterations = 10
    start = time.perf_counter()
    for _ in range(iterations):
        calculate_mac(filter_a, pattern)
        calculate_mac(filter_b, pattern)
    end = time.perf_counter()
    return ((end - start) / iterations) * 1000 # ms 단위

# --- [기능 1: 3x3 수동 입력 모드] ---
def run_manual_mode():
    print("\n--- [모드 1] 3x3 수동 입력 시작 ---")
    
    def get_input(name):
        while True:
            try:
                print(f"{name} 입력 (각 줄에 숫자 3개를 공백으로 구분, 총 3줄):")
                mat = []
                for _ in range(3):
                    row = list(map(float, input().split()))
                    if len(row) != 3: raise ValueError
                    mat.append(row)
                return mat
            except:
                print("입력 형식 오류: 숫자 3개를 정확히 입력하세요.")

    filter_a = get_input("필터 A (Cross용)")
    filter_b = get_input("필터 B (X용)")
    pattern = get_input("판정할 패턴")

    s_a = calculate_mac(filter_a, pattern)
    s_b = calculate_mac(filter_b, pattern)
    res = judge(s_a, s_b)
    
    print(f"\n결과: Cross점수({s_a:.2f}), X점수({s_b:.2f}) -> 판정: {res}")
    perf = measure_performance(filter_a, filter_b, pattern)
    print(f"성능: 3x3 평균 연산 시간 {perf:.6f} ms")

# --- [기능 2: JSON 일괄 처리 모드] ---
def run_json_mode():
    print("\n--- [모드 2] JSON 데이터 분석 시작 ---")
    try:
        with open('data.json', 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        print("에러: data.json 파일이 없습니다.")
        return

    filters = data['filters']
    patterns = data['patterns']
    
    results = []
    performance_data = []
    total, pass_count, fail_count = 0, 0, 0

    for p_id, p_info in patterns.items():
        total += 1
        try:
            # 1. 크기 추출 (size_5_1 -> 5)
            size = int(p_id.split('_')[1])
            f_key = f"size_{size}"
            
            # 2. 데이터 가져오기
            p_mat = p_info['input']
            expected = normalize_label(p_info['expected'])
            f_cross = filters[f_key]['cross']
            f_x = filters[f_key]['x']

            # 3. 검증 (크기가 맞는지)
            if len(p_mat) != size or len(f_cross) != size:
                raise ValueError(f"크기 불일치 (기대:{size})")

            # 4. 연산 및 판정
            s_cross = calculate_mac(f_cross, p_mat)
            s_x = calculate_mac(f_x, p_mat)
            final_res = judge(s_cross, s_x)

            # 5. PASS/FAIL 체크
            status = "PASS" if final_res == expected else "FAIL"
            if status == "PASS": pass_count += 1
            else: fail_count += 1

            print(f"[{p_id}] Cross:{s_cross:>6.2f}, X:{s_x:>6.2f} | 판정:{final_res:<6} | 정답:{expected:<6} -> {status}")

            # 6. 성능 측정 저장
            avg_t = measure_performance(f_cross, f_x, p_mat)
            performance_data.append([f"{size}x{size}", avg_t, size])

        except Exception as e:
            print(f"[{p_id}] 처리 실패: {e}")
            fail_count += 1

    # 결과 요약 출력
    print(f"\n--- 최종 리포트 ---")
    print(f"전체 테스트: {total} | 통과: {pass_count} | 실패: {fail_count}")
    
    print("\n--- 성능 분석 표 ---")
    print("크기(NxN) | 평균 시간(ms) | 연산 횟수(N)")
    for p in performance_data:
        print(f"{p[0]:<10} | {p[1]:<14.6f} | {p[2]}")

# --- [메인 실행부] ---
def main():
    while True:
        print("\n[MAC 패턴 판정 시스템]")
        print("1. 3x3 수동 입력 모드")
        print("2. JSON 일괄 처리 모드")
        print("3. 종료")
        choice = input("선택: ")

        if choice == '1': run_manual_mode()
        elif choice == '2': run_json_mode()
        elif choice == '3': break
        else: print("잘못된 선택입니다.")

if __name__ == "__main__":
    main()