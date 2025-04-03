import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
import re
import matplotlib
# macOS 환경에서 스레드 문제 해결을 위한 백엔드 변경
matplotlib.use('Agg')  # GUI 불필요한 백엔드로 설정
import matplotlib.font_manager as fm
import matplotlib.pyplot as plt
import seaborn as sns
import os
import pickle
import platform
import matplotlib.font_manager as fm
from datetime import datetime

# 한글 폰트 설정 함수 개선
def set_korean_font():
    """matplotlib에서 한글 폰트를 사용할 수 있도록 설정합니다."""
    # 시스템 확인
    system = platform.system()
    
    # 가능한 폰트 경로들
    font_paths = []
    
    # 시스템별 폰트 경로 추가
    if system == 'Darwin':  # macOS
        font_paths.extend([
            '/Library/Fonts/AppleGothic.ttf',
            '/Library/Fonts/NanumGothic.ttf',
            '/Library/Fonts/AppleSDGothicNeo.ttc',
            '/System/Library/Fonts/AppleSDGothicNeo.ttc'
        ])
    elif system == 'Windows':  # Windows
        font_paths.extend([
            'c:/Windows/Fonts/malgun.ttf',
            'c:/Windows/Fonts/NanumGothic.ttf',
            'c:/Windows/Fonts/gulim.ttc'
        ])
    else:  # Linux 또는 기타 시스템 (서버 환경 포함)
        font_paths.extend([
            '/usr/share/fonts/truetype/nanum/NanumGothic.ttf',
            '/usr/share/fonts/truetype/nanum/NanumBarunGothic.ttf',
            '/usr/share/fonts/nanum/NanumGothic.ttf',
            '/usr/share/fonts/truetype/unfonts-core/UnDotum.ttf',
            '/usr/local/share/fonts/NanumGothic.ttf'
        ])
    
    # 사용자 정의 폰트 디렉토리 확인 (현재 스크립트 경로 기준)
    current_dir = os.path.dirname(os.path.abspath(__file__))
    font_dir = os.path.join(os.path.dirname(current_dir), 'fonts')
    
    if os.path.exists(font_dir):
        for font_file in os.listdir(font_dir):
            if font_file.endswith(('.ttf', '.ttc')):
                font_paths.append(os.path.join(font_dir, font_file))
    
    # matplotlib 버전에 따라 다른 방법 사용
    try:
        fm._rebuild()
    except AttributeError:
        fm.fontManager.ttflist = []
        for f in fm.findSystemFonts():
            fm.fontManager.ttflist.append(fm.FontProperties(fname=f))
    
    # 사용 가능한 폰트 찾기
    font_found = False
    for font_path in font_paths:
        if os.path.exists(font_path):
            try:
                # 폰트 속성 가져오기
                font_prop = fm.FontProperties(fname=font_path)
                try:
                    font_name = font_prop.get_name()
                except AttributeError:
                    try:
                        font_name = font_prop.get_family()
                    except AttributeError:
                        font_name = "sans-serif"
                
                # matplotlib 설정
                plt.rcParams['font.family'] = font_name
                plt.rcParams['axes.unicode_minus'] = False  # 마이너스 기호 깨짐 방지
                
                print(f"한글 폰트를 설정했습니다: {font_path}")
                font_found = True
                break
            except Exception as e:
                print(f"폰트 설정 중 오류 발생: {font_path} - {e}")
    
    # 폰트 파일을 찾지 못한 경우 시스템에 설치된 폰트 중 한글 폰트 찾기
    if not font_found:
        # 시스템에 설치된 폰트 탐색
        system_fonts = [f.name for f in fm.fontManager.ttflist]
        for font_name in ['NanumGothic', 'Malgun Gothic', 'AppleGothic', '맑은 고딕', '나눔고딕']:
            if font_name in system_fonts:
                plt.rcParams['font.family'] = font_name
                plt.rcParams['axes.unicode_minus'] = False
                print(f"시스템 폰트를 사용합니다: {font_name}")
                font_found = True
                break
    
    # 마지막 대안: sans-serif 폰트 사용
    if not font_found:
        plt.rcParams['font.family'] = 'sans-serif'
        plt.rcParams['font.sans-serif'] = ['NanumGothic', 'Malgun Gothic', 'AppleGothic', 'Arial', 'DejaVu Sans']
        plt.rcParams['axes.unicode_minus'] = False
        print("기본 sans-serif 폰트를 사용합니다.")
    
    return font_found

# 폰트 설치 함수
def install_korean_font():
    """
    서버 환경에 한글 폰트를 자동으로 설치합니다.
    """
    try:
        import requests
    except ImportError:
        print("requests 라이브러리가 설치되어 있지 않습니다.")
        print("pip install requests로 설치하세요.")
        return False
    
    # 현재 스크립트 경로 기준 폰트 디렉토리 생성
    current_dir = os.path.dirname(os.path.abspath(__file__))
    font_dir = os.path.join(os.path.dirname(current_dir), 'fonts')
    
    if not os.path.exists(font_dir):
        os.makedirs(font_dir)
        print(f"폰트 디렉토리를 생성했습니다: {font_dir}")
    
    # 나눔고딕 폰트 파일 경로
    nanum_font_path = os.path.join(font_dir, 'NanumGothic.ttf')
    
    # 이미 설치되어 있는지 확인
    if os.path.exists(nanum_font_path):
        print(f"이미 폰트가 설치되어 있습니다: {nanum_font_path}")
        return True
    
    # 나눔고딕 폰트 다운로드 URL
    font_url = "https://github.com/naver/nanumfont/raw/master/downloads/NanumGothic.ttf"
    
    try:
        # 폰트 파일 다운로드
        print(f"나눔고딕 폰트를 다운로드 중입니다: {font_url}")
        response = requests.get(font_url)
        response.raise_for_status()
        
        # 폰트 파일 저장
        with open(nanum_font_path, 'wb') as f:
            f.write(response.content)
        
        print(f"폰트를 설치했습니다: {nanum_font_path}")
        
        # matplotlib 폰트 캐시 재구성
        fm._rebuild()
        
        return True
    except Exception as e:
        print(f"폰트 설치 중 오류가 발생했습니다: {e}")
        return False

class BootcampApplicationEvaluator:
    def __init__(self):
        # 모델 및 벡터라이저를 저장할 변수들
        self.tfidf_vectorizer = None
        self.model = None
        self.threshold = 0.5  # 기본 임계값
        # 특성 추출에 사용할 단어 목록들
        self.positive_words = ['성공', '열정', '관심', '노력', '경험', '프로젝트', '학습', '개발', '참여', '완료', '성장', '동료']
        self.negative_words = ['어려움', '실패', '부족', '문제', '못', '안', '불가능', '포기']
        self.tech_keywords = ['프로그래밍', '개발', '코딩', '알고리즘', '데이터', '분석', '프로젝트', '연구', '개선', '백엔드', '프론트엔드', '인공지능', 'nlp', 'llm', 'cv',
                              '자바', 'java', 'JavaScript', 'JS', '자바스크립트', '리액트', 'React', 'Spring', '스프링', 'Node.js', 'Next.js', 'Kotlin', '코틀린', '논문']
        
        # 모델 저장 경로
        self.model_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'models')
        self.uploads_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'uploads')
        self.static_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static')
        
        # 디렉토리가 없으면 생성
        for directory in [self.model_dir, self.uploads_dir, self.static_dir]:
            if not os.path.exists(directory):
                os.makedirs(directory)
                
        # 저장된 모델이 있으면 로드
        self.load_model()

    def extract_text_features(self, text):
        """텍스트에서 유용한 특성들을 추출합니다."""
        if not isinstance(text, str):
            return {
                'length': 0,
                'sentence_count': 0,
                'avg_sentence_length': 0,
                'positive_word_count': 0,
                'negative_word_count': 0,
                'tech_keyword_count': 0,
                'positive_ratio': 0,
                'negative_ratio': 0,
                'tech_ratio': 0
            }

        # 텍스트 길이
        length = len(text)

        # 문장 수 (마침표, 느낌표, 물음표로 구분)
        sentences = re.split(r'[.!?]', text)
        sentences = [s for s in sentences if s.strip()]
        sentence_count = len(sentences)

        # 평균 문장 길이
        avg_sentence_length = length / max(sentence_count, 1)

        # 긍정적인 단어 포함 여부
        positive_word_count = sum(1 for word in self.positive_words if word in text)

        # 부정적인 단어 포함 여부
        negative_word_count = sum(1 for word in self.negative_words if word in text)

        # 기술 관련 키워드
        tech_keyword_count = sum(1 for word in self.tech_keywords if word in text)

        return {
            'length': length,
            'sentence_count': sentence_count,
            'avg_sentence_length': avg_sentence_length,
            'positive_word_count': positive_word_count,
            'negative_word_count': negative_word_count,
            'tech_keyword_count': tech_keyword_count,
            'positive_ratio': positive_word_count / len(self.positive_words),
            'negative_ratio': negative_word_count / len(self.negative_words),
            'tech_ratio': tech_keyword_count / len(self.tech_keywords)
        }

    def calculate_score(self, features):
        """특성 값들을 기반으로 점수를 계산합니다."""
        # 가중치 설정
        weights = {
            'length': 0.0001,
            'sentence_count': 0.002,
            'avg_sentence_length': 0.01,
            'positive_word_count': 0.2,
            'negative_word_count': -0.1,
            'tech_keyword_count': 0.3,
            'positive_ratio': 0.3,
            'negative_ratio': -0.2,
            'tech_ratio': 0.4
        }

        # 점수 계산
        score = 0
        for key, value in features.items():
            if key in weights:
                score += value * weights[key]

        return score

    def evaluate_application(self, application_text):
        """지원서 텍스트를 평가하고 점수와 설명을 반환합니다."""
        if not isinstance(application_text, str) or not application_text.strip():
            return {
                'score': 0,
                'rf_probability': 0,
                'evaluation': '텍스트가 비어있습니다.',
                'recommendation': '평가할 내용이 없습니다.',
                'details': []
            }

        # 텍스트 특성 추출
        features = self.extract_text_features(application_text)

        # 점수 계산
        score = self.calculate_score(features)

        # TF-IDF 특성 추출 및 모델 예측 (모델이 준비된 경우)
        rf_probability = 0.5  # 기본값
        
        if self.tfidf_vectorizer is not None and self.model is not None:
            try:
                tfidf_vector = self.tfidf_vectorizer.transform([application_text])
                tfidf_df = pd.DataFrame(
                    tfidf_vector.toarray(),
                    columns=self.tfidf_vectorizer.get_feature_names_out()
                )

                # 모든 특성 결합
                features_df = pd.DataFrame([features])
                X = pd.concat([features_df, tfidf_df], axis=1)

                # 랜덤 포레스트 모델로 확률 예측
                rf_probability = self.model.predict_proba(X)[0][1]
            except Exception as e:
                print(f"모델 예측 중 오류: {e}")
                rf_probability = 0.5
        
        # 점수 및 확률에 따른 평가
        if score >= self.threshold and rf_probability >= 0.5:
            evaluation = '긍정적 평가: 합격 가능성이 높은 지원자'
            recommendation = '추가 검토 권장'
        elif score >= self.threshold and rf_probability < 0.5:
            evaluation = '중립적 평가: 점수는 높지만 모델 분석에서는 낮은 점수'
            recommendation = '면접을 통한 추가 평가 권장'
        elif score < self.threshold and rf_probability >= 0.5:
            evaluation = '중립적 평가: 점수는 낮지만 모델 분석에서는 높은 점수'
            recommendation = '면접을 통한 추가 평가 권장'
        else:
            evaluation = '부정적 평가: 합격 가능성이 낮은 지원자'
            recommendation = '상세 검토 필요'

        # 상세 분석
        details = []
        if features['positive_word_count'] >= 3:
            details.append('✓ 긍정적인 단어 사용이 많음')
        if features['tech_keyword_count'] >= 3:
            details.append('✓ 기술 관련 키워드가 풍부함')
        if features['avg_sentence_length'] <= 50:
            details.append('✓ 문장 구조가 간결함')
        if features['negative_word_count'] >= 3:
            details.append('✗ 부정적인 단어 사용이 많음')
        if features['length'] < 200:
            details.append('✗ 지원서 내용이 짧음')

        return {
            'score': score,
            'rf_probability': rf_probability,
            'evaluation': evaluation,
            'recommendation': recommendation,
            'details': details,
            'features': features
        }

    def evaluate_applications_from_csv(self, file_path, status_column='합불상태', text_columns=None, status_filter_mode='검토전만'):
        """
        CSV 파일에서 지원서를 읽어서 평가합니다.
        
        Args:
            file_path: CSV 파일 경로
            status_column: 상태 정보가 있는 열 이름 (기본값: '합불상태')
            text_columns: 텍스트 정보가 있는 열 이름 목록 (None이면 자동 감지)
            status_filter_mode: 평가 대상 선택 옵션 
                            - '검토전만': '검토전' 상태인 인원만 평가
                            - '검토전과합격': '검토전'과 '합격' 상태 모두 평가
                            - '모든인원': 모든 인원 평가
        
        Returns:
            평가 결과를 포함한 딕셔너리
        """
        # 먼저 한글 폰트 설치 시도 (선택 사항)
        try:
            install_korean_font()
        except Exception as font_e:
            print(f"폰트 설치 중 오류 (무시합니다): {font_e}")
        
        # CSV 파일 읽기 - 더 유연한 방식으로
        try:
            # 먼저 기본 방식으로 시도
            df = pd.read_csv(file_path)
        except pd.errors.ParserError as e:
            print(f"기본 파싱 오류: {e}")
            try:
                # 오류 발생 시 더 유연한 방식으로 시도
                df = pd.read_csv(file_path, on_bad_lines='skip')
                print("일부 행을 건너뛰고 파일을 읽었습니다.")
            except Exception as e2:
                print(f"유연한 파싱 시도 중 오류: {e2}")
                try:
                    # 다른 인코딩 시도
                    df = pd.read_csv(file_path, encoding='utf-8-sig', on_bad_lines='skip')
                    print("다른 인코딩으로 파일을 읽었습니다.")
                except Exception as e3:
                    print(f"모든 파싱 시도 실패: {e3}")
                    # CSV 모듈을 사용한 수동 파싱
                    try:
                        import csv
                        rows = []
                        with open(file_path, 'r', encoding='utf-8') as f:
                            reader = csv.reader(f)
                            header = next(reader)
                            for row in reader:
                                # 행의 길이가 헤더와 다른 경우 조정
                                if len(row) > len(header):
                                    row = row[:len(header)]  # 초과 필드 제거
                                elif len(row) < len(header):
                                    row = row + [''] * (len(header) - len(row))  # 부족 필드 추가
                                rows.append(row)
                        df = pd.DataFrame(rows, columns=header)
                        print("수동 파싱을 통해 파일을 읽었습니다.")
                    except Exception as e4:
                        raise Exception(f"CSV 파일을 읽을 수 없습니다: {e4}")

        # 평가 대상 필터링 (상태에 따라)
        if status_column in df.columns:
            if status_filter_mode == '검토전만':
                # '검토전' 상태인 인원만 필터링
                filtered_df = df[df[status_column] == '검토전']
                print(f"'검토전' 상태인 인원만 필터링: {len(filtered_df)}명")
            elif status_filter_mode == '검토전과합격':
                # '검토전'과 '합격' 상태 모두 필터링
                filtered_df = df[df[status_column].isin(['검토전', '합격'])]
                print(f"'검토전'과 '합격' 상태 인원 필터링: {len(filtered_df)}명")
            else:  # '모든인원'
                # 모든 인원 평가
                filtered_df = df
                print(f"모든 인원 평가: {len(filtered_df)}명")
                
            # 필터링 결과가 없으면 전체 데이터 사용
            if filtered_df.empty:
                filtered_df = df
                print(f"필터링 결과가 없어 전체 인원 평가: {len(filtered_df)}명")
        else:
            # 상태 컬럼이 없으면 전체 데이터 사용
            filtered_df = df
            print(f"상태 컬럼이 없어 전체 인원 평가: {len(filtered_df)}명")

        # 텍스트 컬럼이 지정되지 않은 경우, V열 이후의 모든 컬럼을 고려
        if text_columns is None or not text_columns:
            # 데이터프레임의 컬럼명 살펴보기
            columns = df.columns.tolist()
            # V열 이후 컬럼 찾기 (인덱스 21 이후, 0부터 시작)
            if len(columns) > 21:
                text_columns = columns[21:]
            else:
                # 텍스트 컬럼을 찾을 수 없는 경우, 모든 컬럼 사용
                text_columns = columns

        # 결과를 저장할 리스트
        results = []

        # 각 지원자 평가
        for idx, row in filtered_df.iterrows():
            applicant_info = {
                'index': idx
            }
            
            # 상태 컬럼이 있으면 추가
            if status_column in df.columns:
                applicant_info['status'] = row[status_column]

            # 지원자 식별 정보 추가
            if '가입 이름' in df.columns:
                applicant_info['name'] = row['가입 이름']
            elif '이름' in df.columns:
                applicant_info['name'] = row['이름']
            else:
                applicant_info['name'] = f"지원자 {idx}"
                
            if '가입 이메일' in df.columns:
                applicant_info['email'] = row['가입 이메일']
            elif '이메일' in df.columns:
                applicant_info['email'] = row['이메일']

            # 텍스트 컬럼의 내용을 합쳐서 평가
            combined_text = ""
            for col in text_columns:
                if col in row.index and pd.notna(row[col]) and isinstance(row[col], str):
                    combined_text += row[col] + " "

            # 평가 결과
            evaluation = self.evaluate_application(combined_text)
            applicant_info.update(evaluation)

            results.append(applicant_info)

        # 결과를 데이터프레임으로 변환
        results_df = pd.DataFrame(results)

        # 점수로 정렬
        if 'score' in results_df.columns:
            results_df = results_df.sort_values('score', ascending=False)

        # 시각화 (GUI 필요 없이 이미지 생성)
        plt.figure(figsize=(10, 6))
        if 'score' in results_df.columns and len(results_df) > 0:
            try:
                # 한글 폰트 설정
                set_korean_font()
                
                sns.histplot(data=results_df, x='score', kde=True)
                plt.axvline(self.threshold, color='red', linestyle='--', label='임계값')
                plt.title('지원자 점수 분포')
                plt.xlabel('점수')
                plt.ylabel('빈도')
                plt.legend(['임계값', '지원자 분포'])
                
                # 이미지를 파일로 저장
                img_path = os.path.join(self.static_dir, 'applicant_score_distribution.png')
                plt.savefig(img_path, dpi=100, bbox_inches='tight')
                print(f"그래프를 저장했습니다: {img_path}")
            except Exception as plot_e:
                print(f"시각화 중 오류 발생: {plot_e}")
                
                # 폰트 문제일 가능성이 있으므로 폰트 없이 재시도
                try:
                    plt.clf()  # 현재 그림 초기화
                    plt.rcParams['font.family'] = 'sans-serif'  # 기본 폰트로 설정
                    
                    sns.histplot(data=results_df, x='score', kde=True)
                    plt.axvline(self.threshold, color='red', linestyle='--')
                    plt.title('Score Distribution')  # 영어로 제목 설정
                    plt.xlabel('Score')
                    plt.ylabel('Frequency')
                    
                    # 이미지를 파일로 저장
                    img_path = os.path.join(self.static_dir, 'applicant_score_distribution.png')
                    plt.savefig(img_path, dpi=100, bbox_inches='tight')
                    print(f"폰트 없이 그래프를 저장했습니다: {img_path}")
                except Exception as e2:
                    print(f"폰트 없이 시각화 시도 중 오류 발생: {e2}")
            finally:
                plt.close()

        # 결과 저장
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        result_path = os.path.join(self.uploads_dir, f'evaluation_results_{timestamp}.csv')
        results_df.to_csv(result_path, index=False)
        
        # 필터 모드 정보 추가
        filter_info = {
            '검토전만': '검토전 상태인 인원만 평가했습니다.',
            '검토전과합격': '검토전과 합격 상태인 인원을 평가했습니다.',
            '모든인원': '모든 인원을 평가했습니다.'
        }

        return {
            'results_df': results_df,
            'result_path': result_path,
            'total_count': len(results_df),
            'pass_count': len(results_df[results_df['score'] >= self.threshold]) if 'score' in results_df.columns else 0,
            'fail_count': len(results_df[results_df['score'] < self.threshold]) if 'score' in results_df.columns else 0,
            'avg_score': results_df['score'].mean() if 'score' in results_df.columns and len(results_df) > 0 else 0,
            'top5': results_df.head(5) if not results_df.empty else pd.DataFrame(),
            'plot_path': 'applicant_score_distribution.png',
            'filter_mode': status_filter_mode,
            'filter_description': filter_info.get(status_filter_mode, '인원을 평가했습니다.')
        }
    
    def load_model(self):
        """저장된 모델을 로드합니다."""
        model_path = os.path.join(self.model_dir, 'model.pkl')
        vectorizer_path = os.path.join(self.model_dir, 'vectorizer.pkl')
        threshold_path = os.path.join(self.model_dir, 'threshold.txt')
        
        if os.path.exists(model_path) and os.path.exists(vectorizer_path) and os.path.exists(threshold_path):
            try:
                with open(model_path, 'rb') as f:
                    self.model = pickle.load(f)
                    
                with open(vectorizer_path, 'rb') as f:
                    self.tfidf_vectorizer = pickle.load(f)
                    
                with open(threshold_path, 'r') as f:
                    self.threshold = float(f.read())
                    
                print(f"모델을 성공적으로 로드했습니다. 임계값: {self.threshold:.4f}")
                return True
            except Exception as e:
                print(f"모델 로드 중 오류: {e}")
        else:
            print("모델 파일을 찾을 수 없습니다. 모델 파일을 'models' 디렉토리에 복사해주세요.")
        return False