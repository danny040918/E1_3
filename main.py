import json
import time

# --- [도구 1: 시각화 - 뚫린 네모(□) 적용] ---
def visualize_matrix(matrix, title="패턴 시각화"):
    size = len(matrix)
    print(f"\n{'='*30}")
    print(f" [ {title} ({size}x{size}) ]")
    print(f"{'='*30}")
    
    for row in matrix:
        # 0.5보다 크면 ■ (색칠된 네모), 작으면 □ (뚫린 네모)
        # 가독성을 위해 기호 뒤에 공백을 하나씩 추가했습니다.
        line = "".join(["■ " if val > 0.5 else "□ " for val in row])
        print(line)
    print(f"{'='*30}\n")

# --- [도구 2: 신뢰도 계산] ---
def calculate_confidence(s_a, s_b):
    total = s_a + s_b
    if total == 0: return 0
    return (abs(s_a - s_b) / max(s_a, s_b)) * 100

def normalize_label(label):
    label = str(label).lower().strip()
    if label in ['t', 'cross', '+', '십자가']: return "십자가(Cross)"
    if label in ['x', '엑스']: return "X자(X)"
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
        return "판정 불가"
    return "십자가(Cross)" if score_a > score_b else "X자(X)"

# --- [기능 1: 수동 입력 모드] ---
def run_manual_mode():
    print("\n[모드 1] 3x3 수동 입력 분석")
    
    def get_safe_input(size):
        mat = []
        print(f"{size}x{size} 행렬 데이터를 입력하세요 (한 줄에 {size}개씩 숫자 입력):")
        while len(mat) < size:
            try:
                row = list(map(float, input(f"{len(mat)+1}행 입력: ").split()))
                if len(row) != size:
                    print(f"오류: 정확히 {size}개의 숫자를 입력해야 합니다.")
                    continue
                mat.append(row)
            except ValueError:
                print("오류: 숫자만 입력 가능합니다.")
        return mat

    print("\n--- 필터 A (십자가) 설정 ---")
    filter_a = get_safe_input(3)
    print("\n--- 필터 B (X자) 설정 ---")
    filter_b = get_safe_input(3)
    print("\n--- 분석할 패턴 입력 ---")
    pattern = get_safe_input(3)

    visualize_matrix(pattern, "입력된 패턴 모양")
    
    s_a = calculate_mac(filter_a, pattern)
    s_b = calculate_mac(filter_b, pattern)
    res = judge(s_a, s_b)
    conf = calculate_confidence(s_a, s_b)
    
    print(f"▶ 최종 판정: {res}")
    print(f"▶ 판정 신뢰도: {conf:.1f}%")

# --- [기능 2: JSON 모드 (대형 데이터 시각화)] ---
def run_json_mode():
    print("\n[모드 2] JSON 데이터 일괄 분석")
    try:
        # 한글 깨짐 방지를 위해 encoding='utf-8' 추가
        with open('data.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print("오류: data.json 파일을 찾을 수 없습니다.")
        return
    except Exception as e:
        print(f"파일 로드 중 오류 발생: {e}")
        return

    filters = data['filters']
    patterns = data['patterns']
    
    for p_id, p_info in patterns.items():
        try:
            size = int(p_id.split('_')[1])
            f_key = f"size_{size}"
            p_mat = p_info['input']
            expected = normalize_label(p_info['expected'])
            
            start_time = time.perf_counter()
            s_cross = calculate_mac(filters[f_key]['cross'], p_mat)
            s_x = calculate_mac(filters[f_key]['x'], p_mat)
            end_time = time.perf_counter()
            
            elapsed = (end_time - start_time) * 1000 
            
            final_res = judge(s_cross, s_x)
            conf = calculate_confidence(s_cross, s_x)
            status = "✅ 일치" if final_res == expected else "❌ 불일치"
            
            # 시각화 출력 (■와 □ 사용)
            visualize_matrix(p_mat, f"분석 패턴: {p_id}")
            
            print(f"▶ 분석 결과: {final_res} (정답: {expected}) -> {status}")
            print(f"▶ 판정 신뢰도: {conf:.1f}%")
            print(f"▶ 연산 소요 시간: {elapsed:.4f} ms")
            print("-" * 50)

        except KeyError:
            print(f"주의: {size}x{size} 크기에 대한 필터 데이터가 없습니다.")

def main():
    while True:
        print("\n" + "="*45)
        print("   MAC 패턴 인식 시스템 v2.1 (시각화 개선)")
        print("="*45)
        print("1. 수동 입력 모드 (3x3 전용)")
        print("2. JSON 일괄 처리 모드 (대형 패턴 포함)")
        print("3. 프로그램 종료")
        print("="*45)
        choice = input("원하는 메뉴 번호를 선택하세요: ")
        
        if choice == '1':
            run_manual_mode()
        elif choice == '2':
            run_json_mode()
        elif choice == '3':
            print("프로그램을 종료합니다. 수고하셨습니다!")
            break
        else:
            print("잘못된 선택입니다. 다시 입력해주세요.")

if __name__ == "__main__":
    main()