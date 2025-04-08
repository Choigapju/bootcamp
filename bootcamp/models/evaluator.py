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
        self.additional_features = None  # 추가 특성 데이터 저장
        
        # 특성 추출에 사용할 단어 목록들
        self.positive_words = ['성공', '열정', '관심', '노력', '경험', '프로젝트', '학습', '개발', '참여', '완료', '성장', '동료']
        self.negative_words = ['어려움', '실패', '부족', '문제', '못', '안', '불가능', '포기']
        self.tech_keywords = ['프로그래밍', '개발', '코딩', '알고리즘', '데이터', '분석', '프로젝트', '연구', '개선', '백엔드', '프론트엔드', '인공지능', 'nlp', 'llm', 'cv',
                              '자바', 'java', 'JavaScript', 'JS', '자바스크립트', '리액트', 'React', 'Spring', '스프링', 'Node.js', 'Next.js', 'Kotlin', '코틀린', '논문']
        
        # 기술 관련 전공 키워드 정의
        self.tech_majors = ['개발', '프로그래밍', '컴퓨터', '소프트웨어', '데이터', 
                           '인공지능', 'ai', '머신러닝', '클라우드', '디자인',
                           '정보', 'it', '전산', '공학', '통계']
        
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

    def load_model(self):
        """저장된 모델을 로드합니다."""
        model_path = os.path.join(self.model_dir, 'model.pkl')
        vectorizer_path = os.path.join(self.model_dir, 'vectorizer.pkl')
        threshold_path = os.path.join(self.model_dir, 'threshold.txt')
        additional_features_path = os.path.join(self.model_dir, 'additional_features.pkl')
        
        if os.path.exists(model_path) and os.path.exists(vectorizer_path) and os.path.exists(threshold_path):
            try:
                with open(model_path, 'rb') as f:
                    self.model = pickle.load(f)
                    
                with open(vectorizer_path, 'rb') as f:
                    self.tfidf_vectorizer = pickle.load(f)
                    
                with open(threshold_path, 'r') as f:
                    self.threshold = float(f.read())
                
                # 추가 특성 정보 로드 (있는 경우)
                if os.path.exists(additional_features_path):
                    try:
                        with open(additional_features_path, 'rb') as f:
                            self.additional_features = pickle.load(f)
                        print("추가 특성 정보를 성공적으로 로드했습니다.")
                    except Exception as e:
                        print(f"추가 특성 정보 로드 중 오류: {e}")
                        self.additional_features = None
                    
                print(f"모델을 성공적으로 로드했습니다. 임계값: {self.threshold:.2f}")
                return True
            except Exception as e:
                print(f"모델 로드 중 오류: {e}")
        else:
            print("모델 파일을 찾을 수 없습니다. 모델 파일을 'models' 디렉토리에 복사해주세요.")
        return False

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

    # 생년월일 기반 점수 계산 함수 추가
    def calculate_birth_year_score(self, birth_date):
        """생년월일에서 연도를 추출하여 점수 계산 (90년도 이전 출생자에게 감점)"""
        try:
            if pd.isna(birth_date):
                return 0
            
            # 문자열에서 연도 추출 (YYYY-MM-DD 형식 가정)
            birth_year = int(str(birth_date).split('-')[0])
            
            # 90년도 이전 출생자는 감점
            if birth_year < 1990:
                # 1990년에서 멀어질수록 감점 증가 (최대 -0.1점)
                return max(-0.1, (birth_year - 1990) * 0.01)
            else:
                return 0
        except Exception as e:
            print(f"생년월일 점수 계산 오류: {e}")
            return 0

    # 상태1 (직업 상태) 기반 점수 계산 함수 추가
    def calculate_status1_score(self, status1):
        """상태1 (취업준비생 > 대학(원)생 > 직장인/프리랜서) 점수 계산"""
        if pd.isna(status1):
            return 0
        
        status = str(status1).strip().lower()
        
        if '취업준비생' in status:
            return 0.15  # 가장 높은 가산점
        elif '대학' in status or '원생' in status:
            return 0.1   # 중간 가산점
        elif '직장인' in status or '프리랜서' in status:
            return 0.01  # 낮은 가산점
        else:
            return 0

    # 상태2 (전공) 기반 점수 계산 함수 추가
    def calculate_status2_score(self, status2):
        """상태2 (개발/데이터/AI/클라우드 + 디자인 전공) 점수 계산"""
        if pd.isna(status2):
            return 0
        
        major = str(status2).strip().lower()
        
        # 기술 관련 전공 키워드가 포함되어 있으면 가산점
        for keyword in self.tech_majors:
            if keyword in major:
                return 0.1
        
        return 0

    def calculate_score(self, features, birth_date=None, status1=None, status2=None):
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

        # 추가 특성 점수 계산
        birth_year_score = self.calculate_birth_year_score(birth_date) if birth_date else 0
        status1_score = self.calculate_status1_score(status1) if status1 else 0
        status2_score = self.calculate_status2_score(status2) if status2 else 0
        
        # 최종 점수에 추가 특성 점수 반영
        score += birth_year_score + status1_score + status2_score
        
        return score

    def evaluate_application(self, application_text, birth_date=None, status1=None, status2=None, status3=None):
        """지원서 텍스트를 평가하고 점수와 설명을 반환합니다."""
        if not isinstance(application_text, str) or not application_text.strip():
            return {
                'score': 0,
                'rf_probability': 0,
                'final_score': 0,  # 최종 점수 추가
                'evaluation': '텍스트가 비어있습니다.',
                'recommendation': '평가할 내용이 없습니다.',
                'details': [],
                'birth_date': birth_date,
                'status1': status1,
                'status2': status2,
                'status3': status3
            }

        # 텍스트 특성 추출
        features = self.extract_text_features(application_text)

        # 추가 특성 점수 반영하여 점수 계산
        score = self.calculate_score(features, birth_date, status1, status2)

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
                
                # 추가 특성 점수를 DataFrame에 추가
                features_df['birth_year_score'] = self.calculate_birth_year_score(birth_date)
                features_df['status1_score'] = self.calculate_status1_score(status1)
                features_df['status2_score'] = self.calculate_status2_score(status2)
                
                X = pd.concat([features_df, tfidf_df], axis=1)

                # 필요한 컬럼만 선택 (모델이 학습할 때 사용한 특성 순서대로)
                if hasattr(self.model, 'feature_names_in_'):
                    missing_columns = set(self.model.feature_names_in_) - set(X.columns)
                    # 누락된 특성 추가
                    for col in missing_columns:
                        X[col] = 0
                    # 필요한 컬럼만 선택하고 순서 맞추기
                    X = X.reindex(columns=self.model.feature_names_in_, fill_value=0)

                # 랜덤 포레스트 모델로 확률 예측
                rf_probability = self.model.predict_proba(X)[0][1]
                
                # 디버깅 정보 출력
                print(f"텍스트 특성 점수: {score:.4f}, 모델 예측 확률: {rf_probability:.4f}")
                
            except Exception as e:
                print(f"모델 예측 중 오류: {e}")
                rf_probability = 0.5
        
        # 최종 점수 계산 (텍스트 분석 점수와 모델 예측 확률을 조합)
        # 두 값의 가중 평균으로 최종 점수 계산 (예: 50%+50% 또는 30%+70% 등)
        final_score = 0.3 * score + 0.7 * rf_probability
        
        # 최종 점수를 0~10 범위로 스케일링
        final_score_scaled = final_score * 10
        
        # 점수 및 확률에 따른 평가
        if final_score >= self.threshold and rf_probability >= 0.5:
            evaluation = '긍정적 평가: 합격 가능성이 높은 지원자'
            recommendation = '합격 권장'
        elif final_score >= self.threshold and rf_probability < 0.5:
            evaluation = '텍스트 분석 좋음, AI 모델 예측 낮음'
            recommendation = '면접을 통한 추가 평가 권장'
        elif final_score < self.threshold and rf_probability >= 0.5:
            evaluation = 'AI 모델 예측 좋음, 텍스트 분석 낮음'
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
            
        # 추가 특성 관련 분석 추가
        birth_year_score = self.calculate_birth_year_score(birth_date)
        if birth_year_score < 0:
            details.append(f'✗ 1990년 이전 출생으로 인한 소폭 감점 ({birth_year_score:.2f})')
        
        status1_score = self.calculate_status1_score(status1)
        if status1_score > 0:
            status_msg = ''
            if '취업준비생' in str(status1).lower():
                status_msg = '취업준비생'
            elif '대학' in str(status1).lower() or '원생' in str(status1).lower():
                status_msg = '대학(원)생'
            elif '직장인' in str(status1).lower() or '프리랜서' in str(status1).lower():
                status_msg = '직장인/프리랜서'
            
            details.append(f'✓ {status_msg} 상태로 인한 가산점 (+{status1_score:.2f})')
        
        status2_score = self.calculate_status2_score(status2)
        if status2_score > 0:
            details.append(f'✓ 기술 관련 전공으로 인한 가산점 (+{status2_score:.2f})')

        return {
            'score': score,                # 텍스트 특성 기반 점수
            'rf_probability': rf_probability,  # 모델 예측 확률
            'final_score': final_score_scaled,  # 최종 점수 (0-10 범위)
            'evaluation': evaluation,
            'recommendation': recommendation,
            'details': details,
            'features': features,
            'birth_date': birth_date,
            'status1': status1,
            'status2': status2,
            'status3': status3
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

        # 추가 특성 컬럼 확인
        has_additional_features = all(col in df.columns for col in ['생년월일', '상태1', '상태2'])
        if has_additional_features:
            print("추가 특성 (생년월일, 상태1, 상태2)을 발견했습니다.")
        else:
            print("추가 특성 (생년월일, 상태1, 상태2) 중 일부 또는 전체를 찾을 수 없습니다.")

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
            else:
                applicant_info['email'] = ""
            
            # 추가 특성 정보 수집
            birth_date = None
            status1 = None
            status2 = None
            status3 = None
            
            if '생년월일' in df.columns:
                birth_date = row['생년월일']
                applicant_info['birth_date'] = birth_date
            
            if '상태1' in df.columns:
                status1 = row['상태1']
                applicant_info['status1'] = status1
            
            if '상태2' in df.columns:
                status2 = row['상태2']
                applicant_info['status2'] = status2
                
            if '상태3' in df.columns:
                status3 = row['상태3']
                applicant_info['status3'] = status3
                
            # 텍스트 컬럼의 내용을 합쳐서 평가
            combined_text = ""
            for col in text_columns:
                if col in row.index and pd.notna(row[col]) and isinstance(row[col], str):
                    combined_text += row[col] + " "

            # 추가 특성을 포함한 평가 결과
            evaluation = self.evaluate_application(combined_text, birth_date, status1, status2, status3)
            applicant_info.update(evaluation)
            
            results.append(applicant_info)

        # 결과를 데이터프레임으로 변환
        results_df = pd.DataFrame(results)

        # 최종 점수(final_score)를 기준으로 정렬
        if 'final_score' in results_df.columns and not results_df.empty:
            results_df = results_df.sort_values('final_score', ascending=False)
        # 없으면 score 기준으로 정렬    
        elif 'score' in results_df.columns and not results_df.empty:
            results_df = results_df.sort_values('score', ascending=False)

        # 결과 파일에 생년월일, 상태1, 상태2, 상태3 정보 포함 확인
        required_columns = ['birth_date', 'status1', 'status2', 'status3']
        for col in required_columns:
            if col not in results_df.columns:
                results_df[col] = None
        
        # 결과 테이블에 표시될 점수 컬럼 추가 - 최종 점수를 표시
        # 비율 데이터를 보기 좋은 소수점 2자리로 반올림
        if 'final_score' in results_df.columns:
            results_df['display_score'] = results_df['final_score'].round(2)
        else:
            # 최종 점수가 없으면 원래 점수나 RF 확률을 사용
            if 'score' in results_df.columns:
                results_df['display_score'] = (results_df['score'] * 10).round(2)
            elif 'rf_probability' in results_df.columns:
                results_df['display_score'] = (results_df['rf_probability'] * 10).round(2)
            else:
                results_df['display_score'] = 0.0
        
        # 시각화
        plot_path = None
        if 'final_score' in results_df.columns and len(results_df) > 0:
            try:
                # matplotlib 기본 설정
                plt.figure(figsize=(10, 6))
                plt.rcParams['font.family'] = 'sans-serif'
                plt.rcParams['font.sans-serif'] = ['AppleGothic', 'Malgun Gothic', 'NanumGothic', 'Arial']
                plt.rcParams['axes.unicode_minus'] = False
                
                # 최종 점수로 데이터 시각화
                sns.histplot(data=results_df, x='final_score', kde=True)
                plt.axvline(self.threshold * 10, color='red', linestyle='--')  # 임계값 스케일링
                
                # 영어로 레이블 설정 (안전한 옵션)
                plt.title('Application Score Distribution')
                plt.xlabel('Final Score')
                plt.ylabel('Frequency')
                plt.legend(['Threshold', 'Distribution'])
                
                # 타임스탬프를 사용하여 고유 파일 이름 생성
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                plot_filename = f'applicant_score_distribution_{timestamp}.png'
                plot_path = os.path.join(self.static_dir, plot_filename)
                
                # 이미지 저장
                plt.tight_layout()
                plt.savefig(plot_path, dpi=100)
                print(f"그래프를 저장했습니다: {plot_path}")
                
                # 상대 경로로 변환 (템플릿에서 사용하기 위해)
                plot_path = plot_filename
                
            except Exception as e:
                print(f"시각화 중 오류 발생: {e}")
                # 오류 발생 시 더 단순한 방법으로 재시도
                try:
                    plt.clf()  # 현재 그림 초기화
                    plt.figure(figsize=(10, 6))
                    
                    # 가장 기본적인 설정만 사용
                    plt.rcParams.update({'font.family': 'sans-serif'})
                    
                    # 간단한 히스토그램
                    plt.hist(results_df['final_score'].values, bins=20)
                    plt.axvline(self.threshold * 10, color='red', linestyle='--')
                    plt.title('Score Distribution')
                    plt.xlabel('Final Score')
                    plt.ylabel('Count')
                    
                    # 타임스탬프를 사용하여 고유 파일 이름 생성
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    plot_filename = f'score_distribution_simple_{timestamp}.png'
                    plot_path = os.path.join(self.static_dir, plot_filename)
                    
                    # 이미지 저장
                    plt.savefig(plot_path, dpi=100)
                    print(f"단순화된 그래프를 저장했습니다: {plot_path}")
                    
                    # 상대 경로로 변환
                    plot_path = plot_filename
                    
                except Exception as e2:
                    print(f"단순 시각화 시도 중에도 오류 발생: {e2}")
                    plot_path = None
            finally:
                plt.close()  # 항상 플롯 닫기

        # 결과 저장
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        result_path = os.path.join(self.uploads_dir, f'evaluation_results_{timestamp}.csv')
        results_df.to_csv(result_path, index=False, encoding='utf-8-sig')
        
        # 필터 모드 정보 추가
        filter_info = {
            '검토전만': '검토전 상태인 인원만 평가했습니다.',
            '검토전과합격': '검토전과 합격 상태인 인원을 평가했습니다.',
            '모든인원': '모든 인원을 평가했습니다.'
        }
        
        # 최종 점수 기준으로 합격/불합격 카운트
        pass_count = 0
        fail_count = 0
        avg_score = 0
        
        if 'final_score' in results_df.columns and not results_df.empty:
            pass_count = len(results_df[results_df['final_score'] >= self.threshold * 10])
            fail_count = len(results_df[results_df['final_score'] < self.threshold * 10])
            avg_score = results_df['final_score'].mean()
        elif 'score' in results_df.columns and not results_df.empty:
            pass_count = len(results_df[results_df['score'] >= self.threshold])
            fail_count = len(results_df[results_df['score'] < self.threshold])
            avg_score = results_df['score'].mean() * 10  # 스케일링

        return {
            'results_df': results_df,
            'result_path': result_path,
            'total_count': len(results_df),
            'pass_count': pass_count,
            'fail_count': fail_count,
            'avg_score': avg_score,
            'top5': results_df.head(5) if not results_df.empty else pd.DataFrame(),
            'plot_path': plot_path,
            'threshold': self.threshold * 10,  # 임계값 스케일링 (0-10 범위로)
            'filter_mode': status_filter_mode,
            'filter_description': filter_info.get(status_filter_mode, '인원을 평가했습니다.')
        }