from flask import Flask, render_template, request, redirect, url_for, flash, send_file, jsonify
from werkzeug.utils import secure_filename
import os
import pandas as pd
import sys
import logging
import pickle
from datetime import datetime

# 로깅 설정
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    handlers=[logging.StreamHandler()])
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = 'bootcamp_evaluator_secret_key'

# min 함수를 Jinja2 템플릿에서 사용할 수 있도록 설정
app.jinja_env.globals.update(min=min)

# 디렉토리 설정
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')
RESULTS_FOLDER = os.path.join(os.path.dirname(__file__), 'results')
ALLOWED_EXTENSIONS = {'csv'}

# 필요한 디렉토리가 없으면 생성
for folder in [UPLOAD_FOLDER, RESULTS_FOLDER]:
    if not os.path.exists(folder):
        os.makedirs(folder)
        logger.info(f"디렉토리 생성됨: {folder}")

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['RESULTS_FOLDER'] = RESULTS_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB 제한

# 평가 모델 인스턴스 생성
try:
    # evaluator.py 파일이 같은 경로에 있으므로, 직접 임포트
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    from models.evaluator import BootcampApplicationEvaluator
    
    # 인스턴스 생성
    evaluator = BootcampApplicationEvaluator()
    
    # 모델 로드 확인
    model_loaded = evaluator.model is not None
    if model_loaded:
        logger.info("사전 훈련된 모델을 성공적으로 로드했습니다.")
    else:
        logger.warning("사전 훈련된 모델을 찾을 수 없습니다. models 디렉토리에 모델 파일이 있는지 확인하세요.")
except Exception as e:
    logger.error(f"평가 모델 인스턴스 생성 중 오류: {e}")
    evaluator = None

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    # 모델 상태 확인
    model_status = "준비됨" if evaluator and evaluator.model is not None else "사용할 수 없음"
    return render_template('index.html', model_status=model_status)

@app.route('/evaluate-file', methods=['GET', 'POST'])
def evaluate_file():
    if request.method == 'POST':
        # 파일이 없는 경우
        if 'file' not in request.files:
            flash('파일이 없습니다', 'danger')
            return redirect(request.url)
            
        file = request.files['file']
        
        # 파일명이 없는 경우
        if file.filename == '':
            flash('선택된 파일이 없습니다', 'danger')
            return redirect(request.url)
            
        # 파일 확장자 확인
        if not file.filename.endswith('.csv'):
            flash('CSV 파일만 업로드 가능합니다', 'danger')
            return redirect(request.url)
        
        # 평가 대상 선택 옵션 가져오기
        status_filter_mode = request.form.get('status_filter_mode', '검토전만')
            
        # 파일 저장
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{timestamp}_{filename}")
        file.save(file_path)
        
        # 파일 평가
        try:
            # evaluator가 없는 경우 다시 생성
            if evaluator is None:
                try:
                    from models.evaluator import BootcampApplicationEvaluator
                    evaluator_instance = BootcampApplicationEvaluator()
                    logger.info("평가 모델을 다시 생성했습니다.")
                except Exception as e:
                    logger.error(f"평가 모델 재생성 중 오류: {e}")
                    flash("평가 모델이 준비되지 않았습니다. 관리자에게 문의하세요.", "danger")
                    return redirect(url_for('index'))
            else:
                evaluator_instance = evaluator
                
            evaluation_results = evaluator_instance.evaluate_applications_from_csv(
                file_path, 
                status_column='합불상태',
                status_filter_mode=status_filter_mode  # 평가 대상 선택 옵션 전달
            )
            
            # 결과를 저장하고 고유 ID 생성
            result_id = f"result_{timestamp}"
            result_path = os.path.join(app.config['RESULTS_FOLDER'], f"{result_id}.pkl")
            
            # 딕셔너리로 결과 처리 (evaluation_results가 딕셔너리인 경우)
            if isinstance(evaluation_results, dict):
                evaluation_results['result_id'] = result_id
                evaluation_results['timestamp'] = timestamp
            else:
                # 객체인 경우 (클래스 인스턴스인 경우)
                try:
                    evaluation_results.result_id = result_id
                    evaluation_results.timestamp = timestamp
                except AttributeError:
                    # 딕셔너리도 아니고 속성을 설정할 수 없는 경우, 래퍼 생성
                    results_wrapper = {
                        'original_results': evaluation_results,
                        'result_id': result_id,
                        'timestamp': timestamp
                    }
                    evaluation_results = results_wrapper
            
            # 결과 저장
            with open(result_path, 'wb') as f:
                pickle.dump(evaluation_results, f)
            
            # 결과 페이지로 리다이렉트 (페이지네이션 적용)
            return redirect(url_for('evaluation_results', result_id=result_id, page=1))
        except Exception as e:
            logger.error(f"파일 평가 중 오류: {e}")
            flash(f"파일 평가 중 오류가 발생했습니다: {e}", "danger")
            return redirect(request.url)
    
    return render_template('evaluate_file.html')

# URL 경로와 함수 이름을 일치시키기 위해 두 가지를 모두 수정
@app.route('/evaluation_results/<result_id>')
@app.route('/evaluation_results/<result_id>/<int:page>')
def evaluation_results(result_id, page=1):
    """평가 결과를 표시하는 라우트 (페이지네이션 적용)"""
    try:
        # 결과 파일 로드
        results_path = os.path.join(app.config['RESULTS_FOLDER'], f'{result_id}.pkl')
        with open(results_path, 'rb') as f:
            results = pickle.load(f)
        
        # 페이지네이션 설정
        per_page = 20  # 페이지당 표시할 지원자 수
        
        # 결과 구조에 따라 데이터프레임 접근 방법 결정
        results_df = None
        
        # 딕셔너리인 경우
        if isinstance(results, dict):
            if 'results_df' in results:
                results_df = results['results_df']
            elif 'original_results' in results and isinstance(results['original_results'], dict) and 'results_df' in results['original_results']:
                results_df = results['original_results']['results_df']
        # 객체인 경우
        elif hasattr(results, 'results_df'):
            results_df = results.results_df
        # original_results 래퍼가 있는 경우
        elif hasattr(results, 'original_results'):
            if isinstance(results.original_results, dict) and 'results_df' in results.original_results:
                results_df = results.original_results['results_df']
            elif hasattr(results.original_results, 'results_df'):
                results_df = results.original_results.results_df
        
        # 데이터프레임이 있고 비어있지 않은 경우
        if results_df is not None and not results_df.empty:
            # 전체 페이지 수 계산
            total_pages = (len(results_df) + per_page - 1) // per_page
            
            # 페이지 번호 유효성 검사
            if page < 1:
                page = 1
            elif page > total_pages and total_pages > 0:
                page = total_pages
            
            # 현재 페이지에 표시할 결과만 가져오기
            start = (page - 1) * per_page
            end = min(start + per_page, len(results_df))
            paginated_results = results_df.iloc[start:end]
        else:
            # 결과가 없는 경우 빈 데이터프레임 생성
            paginated_results = pd.DataFrame()
            total_pages = 0
        
        # 임계값 설정 - 다양한 객체 구조 고려
        threshold = 0.5  # 기본값
        
        # 임계값 찾기 시도
        if isinstance(results, dict):
            threshold = results.get('threshold', 0.5)
        elif hasattr(results, 'threshold'):
            threshold = results.threshold
            
        # 필요한 모든 데이터 준비
        template_data = {
            'results': {
                'total_count': len(results_df) if results_df is not None else 0,
                'results_df': results_df,
                'paginated_results': paginated_results,
            },
            'paginated_results': paginated_results,
            'threshold': threshold,
            'page': page,
            'per_page': per_page,
            'total_pages': total_pages,
            'result_id': result_id
        }
        
        # 원본 결과 객체에서 추가 데이터 추출
        if isinstance(results, dict):
            # 딕셔너리에서 추가 필드 복사
            for key in ['pass_count', 'fail_count', 'avg_score', 'filter_mode', 'filter_description', 'top5', 'plot_path', 'result_path']:
                if key in results:
                    template_data['results'][key] = results[key]
        else:
            # 객체에서 속성 복사 시도
            for key in ['pass_count', 'fail_count', 'avg_score', 'filter_mode', 'filter_description', 'top5', 'plot_path', 'result_path']:
                if hasattr(results, key):
                    template_data['results'][key] = getattr(results, key)
        
        # results.html 템플릿 사용
        return render_template(
            'results.html',
            **template_data
        )
    except Exception as e:
        logger.error(f"결과 표시 중 오류 발생: {e}")
        flash(f"결과를 표시할 수 없습니다: {e}", "danger")
        return redirect(url_for('index'))

# 기존 /results 라우트도 유지하여 두 URL이 모두 작동하도록 설정
@app.route('/results/<result_id>')
@app.route('/results/<result_id>/<int:page>')
def results(result_id, page=1):
    """결과 라우트 - evaluation_results 함수로 리다이렉트"""
    return evaluation_results(result_id, page)

@app.route('/evaluate_text', methods=['GET', 'POST'])
def evaluate_text():
    # 단순 리다이렉트
    return redirect(url_for('index'))

@app.route('/download/<filename>')
def download_file(filename):
    """파일 다운로드"""
    try:
        return send_file(os.path.join(app.config['UPLOAD_FOLDER'], filename),
                        as_attachment=True)
    except Exception as e:
        logger.error(f'파일 다운로드 중 오류: {str(e)}')
        flash(f'파일 다운로드 중 오류가 발생했습니다: {str(e)}')
        return redirect(url_for('index'))

@app.route('/model_info')
def model_info():
    """모델 정보 조회"""
    if evaluator is None:
        return jsonify({
            "model_loaded": False,
            "error": "평가 모델 인스턴스가 생성되지 않았습니다."
        })
        
    model_loaded = evaluator.model is not None and evaluator.tfidf_vectorizer is not None
    threshold = evaluator.threshold if hasattr(evaluator, 'threshold') else None
    
    # 추가 특성 정보 확인
    has_additional_features = hasattr(evaluator, 'additional_features') and evaluator.additional_features is not None
    
    return jsonify({
        "model_loaded": model_loaded,
        "threshold": threshold,
        "has_additional_features": has_additional_features
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port, debug=True)