from flask import Flask, render_template, request, redirect, url_for, flash, send_file, jsonify
from werkzeug.utils import secure_filename
import os
import pandas as pd
import sys
import logging
from models.evaluator import BootcampApplicationEvaluator
import io
import json
from datetime import datetime

# 로깅 설정
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    handlers=[logging.StreamHandler()])
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = 'bootcamp_evaluator_secret_key'

# 디렉토리 설정
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')
ALLOWED_EXTENSIONS = {'csv'}

# 파일 업로드 디렉토리가 없으면 생성
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
    logger.info(f"업로드 디렉토리 생성됨: {UPLOAD_FOLDER}")

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB 제한

# 평가 모델 인스턴스 생성
try:
    evaluator = BootcampApplicationEvaluator()
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
        evaluator = BootcampApplicationEvaluator()
        evaluation_results = evaluator.evaluate_applications_from_csv(
            file_path, 
            status_column='합불상태',
            status_filter_mode=status_filter_mode  # 평가 대상 선택 옵션 전달
        )
        
        # 여기를 수정: 'evaluation_results.html'을 'result.html'로 변경
        return render_template(
            'results.html',  # 실제 템플릿 파일명인 results.html로 변경
            results=evaluation_results,
            threshold=evaluator.threshold
)
    
    return render_template('evaluate_file.html')

@app.route('/evaluate_text', methods=['GET', 'POST'])
def evaluate_text():
    # 모델이 로드되지 않은 경우
    if evaluator is None or evaluator.model is None:
        flash('평가 모델이 준비되지 않았습니다. 관리자에게 문의하세요.')
        return redirect(url_for('index'))
        
    result = None
    
    if request.method == 'POST':
        text = request.form.get('text', '')
        
        if not text:
            flash('텍스트가 입력되지 않았습니다')
            return redirect(request.url)
            
        try:
            result = evaluator.evaluate_application(text)
        except Exception as e:
            logger.error(f'텍스트 평가 중 오류: {str(e)}')
            flash(f'텍스트 평가 중 오류가 발생했습니다: {str(e)}')
            return redirect(request.url)
    
    threshold = evaluator.threshold if evaluator and hasattr(evaluator, 'threshold') else 0.5
    return render_template('evaluate_text.html', result=result, threshold=threshold)

@app.route('/api/evaluate_text', methods=['POST'])
def api_evaluate_text():
    """API 엔드포인트: 텍스트 평가"""
    # 모델이 로드되지 않은 경우
    if evaluator is None or evaluator.model is None:
        return jsonify({"error": "평가 모델이 준비되지 않았습니다"}), 503
        
    if not request.is_json:
        return jsonify({"error": "JSON 요청이 필요합니다"}), 400
        
    data = request.get_json()
    text = data.get('text', '')
    
    if not text:
        return jsonify({"error": "텍스트가 입력되지 않았습니다"}), 400
        
    try:
        result = evaluator.evaluate_application(text)
        return jsonify(result)
    except Exception as e:
        logger.error(f'API 텍스트 평가 중 오류: {str(e)}')
        return jsonify({"error": str(e)}), 500

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
    return jsonify({
        "model_loaded": model_loaded,
        "threshold": threshold
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)